#!/usr/bin/env python3
"""Exact 54-set sunflower stability certificate for M076.

A negative local-search boundary, NOT a new bound on f(4,3).
Only the Python standard library is required.
"""
from __future__ import annotations
import argparse
from itertools import combinations

# Each 9-point component has three 3-point blocks; take two points
# from each of two different blocks. Two disjoint components: 54 sets.
def mask(points):
    return sum(1 << x for x in points)


def base_family():
    family = []
    for offset in (0, 9):
        blocks = [range(offset + 3 * i, offset + 3 * i + 3)
                  for i in range(3)]
        for i, j in combinations(range(3), 2):
            for left in combinations(blocks[i], 2):
                for right in combinations(blocks[j], 2):
                    family.append(mask(left + right))
    assert len(family) == 54 and len(set(family)) == 54
    return tuple(family)


def sunflower(a, b, c):
    return (a & b) == (a & c) == (b & c)


def verify_family(family):
    if len(set(family)) != len(family) or any(x.bit_count() != 4 for x in family):
        return False
    return all(not sunflower(a, b, c) for a, b, c in combinations(family, 3))


def orbit_key(points):
    # Independent permutations of the 3 elements in each block,
    # of the 3 blocks in each component, and of the 2 components.
    counts = []
    for copy in range(2):
        groups = [sum(copy * 9 + 3 * g <= x < copy * 9 + 3 * g + 3
                      for x in points) for g in range(3)]
        counts.append(tuple(sorted(groups, reverse=True)))
    return (sum(x >= 18 for x in points),) + tuple(sorted(counts, reverse=True))


def orbit_representatives():
    family = set(base_family())
    reps, counts = {}, {}
    for points in combinations(range(22), 4):
        if mask(points) in family:
            continue
        key = orbit_key(points)
        reps.setdefault(key, points)
        counts[key] = counts.get(key, 0) + 1
    if len(reps) != 18 or sum(counts.values()) != 7261:
        raise AssertionError("orbit enumeration changed")
    return reps, counts


# SIX disjoint forbidden-pair witnesses except for one orbit, which
# has five. This isolates the only type admissible after five deletions. The indices refer to base_family().
# For each pair (i,j), the two old sets and the candidate form a sunflower.
MATCHING_WITNESSES = {
    (0, (1, 1, 0), (1, 1, 0)): ((1, 3), (0, 4), (5, 9), (2, 12), (7, 18), (6, 21)),
    (0, (1, 1, 1), (1, 0, 0)): ((1, 3), (0, 4), (5, 11), (10, 12), (9, 13), (2, 14)),
    (0, (2, 0, 0), (1, 1, 0)): ((0, 9), (1, 10), (2, 11), (28, 30), (27, 31), (18, 35)),
    (0, (2, 0, 0), (2, 0, 0)): ((0, 9), (1, 10), (2, 11), (27, 36), (28, 37), (29, 38)),
    (0, (2, 1, 0), (1, 0, 0)): ((0, 1), (2, 9), (24, 33), (25, 34), (26, 35), (30, 36)),
    (0, (2, 1, 1), (0, 0, 0)): ((0, 1), (9, 10), (2, 11), (19, 21), (18, 22), (26, 27)),
    (0, (3, 0, 0), (1, 0, 0)): ((0, 9), (1, 10), (2, 11), (3, 12), (4, 13), (5, 14)),
    (0, (3, 1, 0), (0, 0, 0)): ((0, 1), (3, 4), (6, 7), (2, 9), (5, 12), (8, 15)),
    (1, (1, 1, 0), (1, 0, 0)): ((1, 3), (0, 4), (5, 9), (2, 12), (7, 18), (6, 21)),
    (1, (1, 1, 1), (0, 0, 0)): ((1, 3), (0, 4), (5, 11), (10, 12), (9, 13), (2, 14)),
    (1, (2, 0, 0), (1, 0, 0)): ((0, 9), (1, 10), (2, 11), (18, 33), (19, 34), (20, 35)),
    (1, (2, 1, 0), (0, 0, 0)): ((0, 1), (2, 9), (24, 27), (25, 28), (26, 29)),
    (1, (3, 0, 0), (0, 0, 0)): ((0, 9), (1, 10), (2, 11), (3, 12), (4, 13), (5, 14)),
    (2, (1, 0, 0), (1, 0, 0)): ((3, 9), (4, 10), (5, 11), (0, 12), (1, 13), (2, 14)),
    (2, (1, 1, 0), (0, 0, 0)): ((1, 3), (0, 4), (5, 9), (2, 12), (7, 18), (6, 21)),
    (2, (2, 0, 0), (0, 0, 0)): ((0, 9), (1, 10), (2, 11), (18, 27), (19, 28), (20, 29)),
    (3, (1, 0, 0), (0, 0, 0)): ((3, 9), (4, 10), (5, 11), (0, 12), (1, 13), (2, 14)),
    (4, (0, 0, 0), (0, 0, 0)): ((0, 27), (1, 28), (2, 29), (3, 30), (4, 31), (5, 32)),
}

# Exact sharpness: deleting five old sets allows this new-vertex set.
SPECIAL_KEY = (1, (2, 1, 0), (0, 0, 0))
SHARP_OUTSIDE = (0, 1, 3, 18)
DROP_OUTSIDE = frozenset((1, 2, 24, 25, 26))
# Deleting six old sets allows this original-support set.
SHARP_INSIDE = (0, 1, 3, 6)
DROP_INSIDE = frozenset((1, 10, 11, 21, 22, 26))


def check_matching(key, candidate, pairs, family=None):
    family = base_family() if family is None else family
    threshold = 5 if key == SPECIAL_KEY else 6
    if len(pairs) != threshold:
        return False
    used = [i for pair in pairs for i in pair]
    if len(set(used)) != 2 * threshold or any(i < 0 or i >= 54 for i in used):
        return False
    c = mask(candidate)
    return all(sunflower(family[i], family[j], c) for i, j in pairs)


def check_certificates():
    family = base_family()
    if not verify_family(family):
        raise AssertionError("base family is not sunflower-free")
    reps, counts = orbit_representatives()
    if set(reps) != set(MATCHING_WITNESSES):
        raise AssertionError("missing or extraneous orbit certificate")
    for key, rep in reps.items():
        if not check_matching(key, rep, MATCHING_WITNESSES[key], family):
            raise AssertionError(f"invalid matching certificate for {key}")
    for candidate, dropped in ((SHARP_OUTSIDE, DROP_OUTSIDE),
                               (SHARP_INSIDE, DROP_INSIDE)):
        if not verify_family([x for i, x in enumerate(family)
                              if i not in dropped] + [mask(candidate)]):
            raise AssertionError("sharpness control failed")
    return counts


def is_special_without_orbits(points):
    """Literal support-pattern check, independent of orbit_key()."""
    if sum(x >= 18 for x in points) != 1:
        return False
    old = [x for x in points if x < 18]
    for start in (0, 9):
        if all(start <= x < start + 9 for x in old):
            counts = sorted(sum(start + 3*g <= x < start + 3*g + 3
                                for x in old) for g in range(3))
            return counts == [0, 1, 2]
    return False


def independent_full_sweep():
    """Separate frozenset representation; no orbit reduction or certificate table.

    Checks every 4-subset of 22 points (all patterns of up to four outsiders).
    Greedily constructs five/six disjoint forbidden old pairs.
    """
    family = [frozenset(i for i in range(18) if x & (1 << i))
              for x in base_family()]
    old = set(family)
    for points in combinations(range(22), 4):
        candidate = frozenset(points)
        if candidate in old:
            continue
        required = 5 if is_special_without_orbits(points) else 6
        used, found = set(), 0
        for i in range(54):
            if i in used:
                continue
            for j in range(i):
                if j in used:
                    continue
                if (family[i] & family[j] ==
                        family[i] & candidate ==
                        family[j] & candidate):
                    used.update((i, j))
                    found += 1
                    break
            if found >= required:
                break
        if found < required:
            raise AssertionError(f"independent sweep failed at {points}")
    return True


def enumerate_five_covers():
    """Complete branch-on-an-uncovered-edge search for all size-five covers."""
    family = base_family()
    c = mask(SHARP_OUTSIDE)
    edges = tuple((i, j) for i, a in enumerate(family)
                  for j, b in enumerate(family[:i]) if sunflower(a, b, c))

    def recurse(remaining, chosen):
        if not remaining:
            return {chosen} if len(chosen) == 5 else set()
        if len(chosen) == 5:
            return set()
        a, b = remaining[0]
        result = set()
        for vertex in (a, b):
            rest = tuple(pair for pair in remaining if vertex not in pair)
            result.update(recurse(rest, chosen | {vertex}))
        return result

    return recurse(edges, frozenset())


def check_five_deletion_rigidity():
    """Any five-deletion neighborhood admits at most one new four-set."""
    family = base_family()
    covers = enumerate_five_covers()
    expected = {frozenset((0, 2, 24, 25, 26)),
                frozenset((1, 2, 24, 25, 26))}
    if covers != expected:
        raise AssertionError(f"unexpected five-covers: {covers}")
    for cover in covers:
        kept = [a for i, a in enumerate(family) if i not in cover]
        admissible_triples = []
        for triple in combinations(range(18), 3):
            candidate = mask(triple + (18,))
            if all(not sunflower(a, b, candidate)
                   for a, b in combinations(kept, 2)):
                admissible_triples.append(triple)
        if admissible_triples != [(0, 1, 3)]:
            raise AssertionError(f"unexpected addable triples: {admissible_triples}")
        c1, c2 = mask((0, 1, 3, 18)), mask((0, 1, 3, 19))
        if not any(sunflower(a, c1, c2) for a in kept):
            raise AssertionError("two outside candidates should conflict with a survivor")
    return True


def independent_cover_sweep():
    """Exhaust all C(54,5)=3,162,510 deletion sets without branching."""
    family = base_family()
    candidate = mask(SHARP_OUTSIDE)
    edges = tuple((1 << i) | (1 << j)
                  for i, a in enumerate(family)
                  for j, b in enumerate(family[:i])
                  if sunflower(a, b, candidate))
    covers = set()
    for indices in combinations(range(54), 5):
        cover_mask = sum(1 << i for i in indices)
        if all(cover_mask & edge for edge in edges):
            covers.add(frozenset(indices))
    if covers != enumerate_five_covers():
        raise AssertionError("independent full cover sweep disagrees")
    return len(covers)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="check all 18 orbit certificates and 7261 candidates")
    args = parser.parse_args()
    counts = check_certificates()
    check_five_deletion_rigidity()
    if args.check:
        independent_full_sweep()
        independent_cover_sweep()
    print("M076 54-set baseline: 24804 triples, no sunflower")
    print(f"18 orbit certificates; {sum(counts.values())} alternative 4-sets on 22 points")
    print("17 orbit types require >=6 deletions; one requires >=5")
    print("All five-deletion covers force one original triple; at most one insertion")
    print("Both bounds attained by explicit deletion-and-addition controls")
    if args.check:
        print("Independent 7261-candidate frozenset sweep: PASS")
        print("Independent 3162510 five-deletion brute-force sweep: PASS")


if __name__ == "__main__":
    main()
