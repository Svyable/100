#!/usr/bin/env python3
"""Eight-deletion neighborhood of the Abbott--Hanson--Sauer 54-family.

Exact finite restricted candidate; not a global sunflower theorem or
independently reviewed mathematical/priority claim. Standard library only.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations, product

from scripts import m076_f43_stability as base

FAMILY = base.base_family()
INSIDE = (0, (2, 1, 1), (0, 0, 0))
OUTSIDE = (1, (2, 1, 0), (0, 0, 0))
SUPPORT = (1 << 18) - 1
SHARP_DROP = frozenset((0, 1, 10, 11, 18, 21, 25, 26))
SHARP_INSERT = ((0, 1, 3, 6), (0, 1, 3, 7),
                (0, 1, 4, 8), (0, 1, 5, 8))

# Nine vertex-disjoint old-old-candidate sunflower pairs for each of the
# sixteen excluded orbit types. Computed as graph matchings, but the checker
# validates every pair from literal set intersections; no solver is trusted.
NINE_PAIR_WITNESSES = {
 (0,(1,1,0),(1,1,0)): ((0,4),(1,3),(2,14),(5,11),(6,23),(7,20),(8,53),(15,52),(16,51)),
 (0,(1,1,1),(1,0,0)): ((0,4),(1,3),(2,14),(5,11),(6,23),(7,20),(8,53),(9,13),(10,12)),
 (0,(2,0,0),(1,1,0)): ((0,11),(1,10),(2,9),(18,53),(19,52),(20,51),(21,44),(22,43),(23,42)),
 (0,(2,0,0),(2,0,0)): ((0,11),(1,10),(2,9),(18,53),(19,52),(20,51),(21,50),(22,49),(23,48)),
 (0,(2,1,0),(1,0,0)): ((0,1),(2,11),(24,53),(25,52),(26,51),(27,41),(28,40),(29,39),(30,38)),
 (0,(3,0,0),(1,0,0)): ((0,11),(1,10),(2,9),(3,14),(4,13),(5,12),(6,17),(7,16),(8,15)),
 (0,(3,1,0),(0,0,0)): ((0,1),(2,11),(3,4),(5,14),(6,7),(8,17),(24,53),(25,52),(26,51)),
 (1,(1,1,0),(1,0,0)): ((0,4),(1,3),(2,14),(5,11),(6,23),(7,20),(8,53),(15,52),(16,51)),
 (1,(1,1,1),(0,0,0)): ((0,4),(1,3),(2,14),(5,11),(6,23),(7,20),(8,53),(9,13),(10,12)),
 (1,(2,0,0),(1,0,0)): ((0,11),(1,10),(2,9),(18,53),(19,52),(20,51),(21,50),(22,49),(23,48)),
 (1,(3,0,0),(0,0,0)): ((0,11),(1,10),(2,9),(3,14),(4,13),(5,12),(6,17),(7,16),(8,15)),
 (2,(1,0,0),(1,0,0)): ((0,14),(1,13),(2,12),(3,11),(4,10),(5,9),(6,53),(7,52),(8,51)),
 (2,(1,1,0),(0,0,0)): ((0,4),(1,3),(2,14),(5,11),(6,23),(7,20),(8,53),(15,52),(16,51)),
 (2,(2,0,0),(0,0,0)): ((0,11),(1,10),(2,9),(18,53),(19,52),(20,51),(21,50),(22,49),(23,48)),
 (3,(1,0,0),(0,0,0)): ((0,14),(1,13),(2,12),(3,11),(4,10),(5,9),(6,53),(7,52),(8,51)),
 (4,(0,0,0),(0,0,0)): ((0,53),(1,52),(2,51),(3,50),(4,49),(5,48),(6,47),(7,46),(8,45)),
}


def forbidden_edges(candidate):
    return tuple((1 << i) | (1 << j)
                 for i in range(54) for j in range(i)
                 if base.sunflower(FAMILY[i], FAMILY[j], candidate))


def greedy_matching(edges):
    used, result = 0, []
    for edge in edges:
        if not used & edge:
            result.append(edge)
            used |= edge
    return tuple(result)


def is_cover(edges, deleted):
    return all(deleted & edge for edge in edges)


def product_eight_covers(edges):
    """Exhaust covers by endpoint choices of a fixed disjoint matching."""
    matching = greedy_matching(edges)
    assert len(matching) in (5, 6)
    result = set()
    for choices in product(*((edge & -edge, edge ^ (edge & -edge))
                             for edge in matching)):
        chosen = sum(choices)
        free = [1 << i for i in range(54) if not chosen & (1 << i)]
        for extra in combinations(free, 8 - len(matching)):
            deleted = chosen + sum(extra)
            if is_cover(edges, deleted):
                result.add(deleted)
    return result


def branch_eight_covers(edges):
    """Independent branch-on-uncovered-edge search, then size-eight expansion."""
    minimal = set()

    def recurse(remaining, chosen):
        if chosen.bit_count() > 8:
            return
        if not remaining:
            minimal.add(chosen)
            return
        if chosen.bit_count() + len(greedy_matching(remaining)) > 8:
            return
        edge = remaining[0]
        low = edge & -edge
        for vertex in (low, edge ^ low):
            recurse(tuple(e for e in remaining if not e & vertex),
                    chosen | vertex)

    recurse(edges, 0)
    result = set()
    for chosen in minimal:
        free = [1 << i for i in range(54) if not chosen & (1 << i)]
        for extra in combinations(free, 8 - chosen.bit_count()):
            result.add(chosen + sum(extra))
    return result


def candidate_catalog():
    old = set(FAMILY)
    inside = tuple(base.mask(p) for p in combinations(range(18), 4)
                   if base.mask(p) not in old and base.orbit_key(p) == INSIDE)
    outside = tuple(base.mask(p + (18,)) for p in combinations(range(18), 3)
                    if base.orbit_key(p + (18,)) == OUTSIDE)
    assert len(inside) == 162 and len(outside) == 108
    return inside, outside


def literal_sunflower(a, b, c):
    return a & b == a & c == b & c


def literal_direct_sweep():
    """Orbit-free second representation and independent cover-existence search."""
    old = [frozenset(i for i in range(18) if a & (1 << i))
           for a in FAMILY]
    old_set = set(old)
    surviving = []

    def greedy_pairs(edges):
        used, count = set(), 0
        for i, j in edges:
            if i not in used and j not in used:
                used.update((i, j))
                count += 1
        return count

    def has_eight_cover(edges, budget=8):
        if not edges:
            return True
        if budget == 0 or greedy_pairs(edges) > budget:
            return False
        i, j = edges[0]
        return (has_eight_cover(tuple(e for e in edges if i not in e), budget - 1)
                or has_eight_cover(tuple(e for e in edges if j not in e), budget - 1))

    for p in combinations(range(22), 4):
        c = frozenset(p)
        if c in old_set:
            continue
        edges = tuple((i, j) for i in range(54) for j in range(i)
                      if literal_sunflower(old[i], old[j], c))
        if has_eight_cover(edges):
            surviving.append(p)
    normalized = {base.mask(tuple(18 if i >= 18 else i for i in p))
                  for p in surviving}
    return len(surviving), normalized


def sharp_family():
    deleted = [a for i, a in enumerate(FAMILY) if i not in SHARP_DROP]
    inserted = [base.mask(p) for p in SHARP_INSERT]
    return deleted + inserted


def literal_sharp_check():
    family = [frozenset(i for i in range(18) if a & (1 << i))
              for a in FAMILY if a not in
              {FAMILY[i] for i in SHARP_DROP}]
    family += [frozenset(p) for p in SHARP_INSERT]
    return (len(family) == len(set(family)) == 50
            and all(not literal_sunflower(a, b, c)
                    for a, b, c in combinations(family, 3)))


def check(literal=True):
    assert base.verify_family(FAMILY)
    reps, counts = base.orbit_representatives()
    assert len(reps) == 18 and sum(counts.values()) == 7261
    assert set(NINE_PAIR_WITNESSES) == set(reps) - {INSIDE, OUTSIDE}
    for key, pairs in NINE_PAIR_WITNESSES.items():
        c = base.mask(reps[key])
        vertices = [v for pair in pairs for v in pair]
        assert len(pairs) == 9 and len(set(vertices)) == 18
        assert all(0 <= v < 54 for v in vertices)
        assert all(base.sunflower(FAMILY[i], FAMILY[j], c)
                   for i, j in pairs)

    inside, outside = candidate_catalog()
    catalog = inside + outside
    edge_map = {c: forbidden_edges(c) for c in catalog}
    covers = {}
    for key, expected in ((INSIDE, 32416), (OUTSIDE, 35811)):
        edges = forbidden_edges(base.mask(reps[key]))
        a = product_eight_covers(edges)
        b = branch_eight_covers(edges)
        assert a == b and len(a) == expected, (key, len(a), len(b))
        covers[key] = a
    assert len(covers[INSIDE] & covers[OUTSIDE]) == 16
    union = covers[INSIDE] | covers[OUTSIDE]
    assert len(union) == 68211

    distribution = Counter()
    maximum = 0
    for deleted in union:
        allowed = [c for c in catalog if is_cover(edge_map[c], deleted)]
        assert allowed
        upper = 0
        for c in allowed:
            if c in inside:
                upper += 1
            else:
                triple = c & SUPPORT
                retained_supersets = sum((a & triple) == triple
                                         for i, a in enumerate(FAMILY)
                                         if not deleted & (1 << i))
                upper += 2 if retained_supersets == 0 else 1
        distribution[(len(allowed), upper)] += 1
        maximum = max(maximum, upper)
    expected_distribution = {
        (1, 1): 62552, (1, 2): 1107, (2, 2): 4372,
        (2, 3): 40, (3, 3): 120, (4, 4): 20,
    }
    assert dict(distribution) == expected_distribution
    assert maximum == 4
    assert base.verify_family(sharp_family()) and literal_sharp_check()

    if literal:
        n, normalized = literal_direct_sweep()
        assert n == 594 and normalized == set(catalog)
    return {
        "orbit_types": 18, "excluded_by_nine_disjoint_pairs": 16,
        "inside_eight_covers": len(covers[INSIDE]),
        "outside_eight_covers": len(covers[OUTSIDE]),
        "overlapping_covers": 16, "distinct_covers": len(union),
        "candidate_inside_sets": len(inside),
        "candidate_outside_triples": len(outside),
        "distribution": [
            {"patterns": p, "upper_insertions": u, "covers": count}
            for (p, u), count in sorted(distribution.items())
        ],
        "sharp_max_insertions": maximum, "sharp_final_size": 50,
        "literal_22_point_replay": literal,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = check(literal=args.check)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("M076 eight-deletion: at most four insertions, sharp")
        print("68,211 distinct eight-covers; 2 exact enumerators")


if __name__ == "__main__":
    main()
