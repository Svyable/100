#!/usr/bin/env python3
"""Seven-deletion neighborhood of the 54-set Abbott--Hanson--Sauer family.

A finite restricted candidate only: neither a global sunflower bound nor
an independently reviewed theorem. Standard library; no external solver.
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
SHARP_DROP = frozenset((0, 1, 2, 3, 24, 25, 26))
SHARP_TRIPLE = (0, 1, 3)
SUPPORT = (1 << 18) - 1


def forbidden_edges(candidate):
    """Edges of the old-old-candidate sunflower obstruction graph."""
    return tuple(
        (1 << i) | (1 << j)
        for i in range(54) for j in range(i)
        if base.sunflower(FAMILY[i], FAMILY[j], candidate)
    )


def greedy_matching(edges):
    used, selected = 0, []
    for edge in edges:
        if not used & edge:
            used |= edge
            selected.append(edge)
    return tuple(selected)


def cover_valid(edges, deleted):
    return all(edge & deleted for edge in edges)


def product_seven_covers(edges):
    """Every seven-cover chooses an endpoint of each disjoint matched edge."""
    matching = greedy_matching(edges)
    if len(matching) >= 8:
        return set()
    if len(matching) not in (5, 6):
        raise AssertionError("unexpected candidate matching size")
    result = set()
    for choices in product(*(
        tuple(1 << i for i in range(54) if edge & (1 << i))
        for edge in matching
    )):
        chosen = sum(choices)  # matching endpoints are disjoint
        free = [1 << i for i in range(54) if not chosen & (1 << i)]
        for extras in combinations(free, 7 - len(matching)):
            deletion = chosen + sum(extras)
            if cover_valid(edges, deletion):
                result.add(deletion)
    return result


def branch_seven_covers(edges):
    """Separate edge-branching enumeration; matching is a safe lower bound."""
    minimal = set()

    def visit(remaining, chosen):
        if chosen.bit_count() > 7:
            return
        if not remaining:
            minimal.add(chosen)
            return
        if chosen.bit_count() + len(greedy_matching(remaining)) > 7:
            return
        edge = remaining[0]
        low = edge & -edge
        for endpoint in (low, edge ^ low):
            visit(tuple(e for e in remaining if not e & endpoint),
                  chosen | endpoint)

    visit(edges, 0)
    result = set()
    for chosen in minimal:
        free = [1 << i for i in range(54) if not chosen & (1 << i)]
        for extras in combinations(free, 7 - chosen.bit_count()):
            result.add(chosen + sum(extras))
    return result


def candidate_catalog():
    """All inside sets and outside support triples not excluded by 8-matching."""
    old = set(FAMILY)
    inside = tuple(
        base.mask(p) for p in combinations(range(18), 4)
        if base.mask(p) not in old and base.orbit_key(p) == INSIDE
    )
    outside = tuple(
        base.mask(p + (18,)) for p in combinations(range(18), 3)
        if base.orbit_key(p + (18,)) == OUTSIDE
    )
    assert (len(inside), len(outside)) == (162, 108)
    return inside, outside


def literal_edges(candidate):
    """Independent frozenset intersection representation of the same graph."""
    old = [
        frozenset(i for i in range(18) if a & (1 << i))
        for a in FAMILY
    ]
    new = frozenset(i for i in range(22) if candidate & (1 << i))
    return {
        (1 << i) | (1 << j)
        for i in range(54) for j in range(i)
        if old[i] & old[j] == old[i] & new == old[j] & new
    }


def direct_22_sweep():
    """Orbit-key-free exhaustive scan of all nonmembers on 22 points."""
    old = [
        frozenset(i for i in range(18) if a & (1 << i))
        for a in FAMILY
    ]
    old_masks = set(FAMILY)
    survivors = []
    for points in combinations(range(22), 4):
        if base.mask(points) in old_masks:
            continue
        candidate = frozenset(points)
        used, count = set(), 0
        for i in range(54):
            if i in used:
                continue
            for j in range(i):
                if j in used:
                    continue
                if old[i] & old[j] == old[i] & candidate == old[j] & candidate:
                    used.update((i, j))
                    count += 1
                    break
            if count >= 8:
                break
        if count < 8:
            survivors.append(points)
    normalized = {
        base.mask(tuple(18 if x >= 18 else x for x in p))
        for p in survivors
    }
    return len(survivors), normalized


def check(literal=True):
    assert base.verify_family(FAMILY)
    representatives, counts = base.orbit_representatives()
    assert len(representatives) == 18 and sum(counts.values()) == 7261
    inside, outside = candidate_catalog()
    catalog = inside + outside
    edge_map = {c: forbidden_edges(c) for c in catalog}
    if literal:
        n, normalized = direct_22_sweep()
        assert n == 594 and normalized == set(catalog)
        for c, edges in edge_map.items():
            assert set(edges) == literal_edges(c)
        for key, points in representatives.items():
            c = base.mask(points)
            assert set(forbidden_edges(c)) == literal_edges(c), key

    distribution = Counter()
    seven_counts = {}
    patterns = Counter()
    total = 0
    for key, points in representatives.items():
        edges = forbidden_edges(base.mask(points))
        matching = greedy_matching(edges)
        assert all(edge in edges and edge.bit_count() == 2 for edge in matching)
        assert (sum(matching)).bit_count() == 2 * len(matching)
        if key not in (INSIDE, OUTSIDE):
            assert len(matching) >= 8, (key, len(matching))
            continue
        assert len(matching) == (6 if key == INSIDE else 5)
        covers_a = product_seven_covers(edges)
        covers_b = branch_seven_covers(edges)
        assert covers_a == covers_b, (key, len(covers_a), len(covers_b))
        assert len(covers_a) == (1456 if key == INSIDE else 2306)
        seven_counts["inside" if key == INSIDE else "outside"] = len(covers_a)
        total += len(covers_a)
        for deletion in covers_a:
            assert deletion.bit_count() == 7 and cover_valid(edges, deletion)
            allowed = [c for c in catalog if cover_valid(edge_map[c], deletion)]
            assert 1 <= len(allowed) <= 2, (key, deletion, allowed)
            kept = [a for i, a in enumerate(FAMILY) if not deletion & (1 << i)]
            upper = 0
            survivors = []
            for c in allowed:
                if c in inside:
                    upper += 1
                else:
                    triple = c & SUPPORT
                    n = sum((a & triple) == triple for a in kept)
                    survivors.append(n)
                    # Three distinct completions share core triple; if an old
                    # superset survives, two completions plus it are a sunflower.
                    upper += 2 if n == 0 else 1
            assert upper <= 2, (key, deletion, allowed, survivors)
            shape = (len(allowed), tuple(sorted(survivors)), upper)
            distribution[shape] += 1
            patterns[(len(allowed), upper)] += 1

    assert total == 3762
    expected = {
        (1, (), 1): 1384,
        (2, (), 2): 64,
        (1, (0,), 2): 48,
        (1, (1,), 1): 2238,
        (2, (1,), 2): 20,
        (2, (1, 1), 2): 8,
    }
    assert dict(distribution) == expected, distribution
    dropped = sum(1 << i for i in SHARP_DROP)
    assert dropped in product_seven_covers(
        forbidden_edges(base.mask(SHARP_TRIPLE + (18,)))
    )
    kept = [a for i, a in enumerate(FAMILY) if not dropped & (1 << i)]
    new = [base.mask(SHARP_TRIPLE + (18,)),
           base.mask(SHARP_TRIPLE + (19,))]
    assert base.verify_family(kept + new)
    assert not base.verify_family(kept + new + [
        base.mask(SHARP_TRIPLE + (20,))
    ])
    return {
        "orbit_types": 18,
        "excluded_by_eight_disjoint_edges": 16,
        "inside_seven_covers": seven_counts["inside"],
        "outside_seven_covers": seven_counts["outside"],
        "seven_cover_patterns_checked": total,
        "candidate_inside_sets": len(inside),
        "candidate_outside_triples": len(outside),
        "cover_shapes": [
            {"allowed_patterns": k[0], "surviving_old_supersets": list(k[1]),
             "upper_bound_insertions": k[2], "count": v}
            for k, v in sorted(distribution.items())
        ],
        "max_insertions": 2,
        "sharp_example_final_size": len(kept + new),
        "literal_intersection_replay": literal,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="replay literal frozenset graphs and 22-point sweep")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = check(literal=args.check)
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print("M076 seven-deletion candidate: at most two insertions (sharp)")
        print("3762 seven-cover patterns, two exact enumerators; "
              "literal replay: " + ("yes" if args.check else "no"))


if __name__ == "__main__":
    main()
