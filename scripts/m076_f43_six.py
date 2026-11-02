#!/usr/bin/env python3
"""M076: exact six-deletion stability of one classical 54-set sunflower family.

This is a restricted finite theorem candidate, not a global sunflower bound.
Standard library only. Two cover enumerators and two intersection representations.
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations, product

from scripts import m076_f43_stability as base

FAMILY = base.base_family()
INSIDE = (0, (2, 1, 1), (0, 0, 0))
OUTSIDE = (1, (2, 1, 0), (0, 0, 0))
EXCEPTIONAL_DROP = frozenset((0, 1, 2, 24, 25, 26))
EXCEPTIONAL_TRIPLE = (0, 1, 3)


def forbidden_edges(candidate):
    """An edge ij means old sets i,j and candidate form a sunflower."""
    return tuple(
        (i, j)
        for i in range(54)
        for j in range(i)
        if base.sunflower(FAMILY[i], FAMILY[j], candidate)
    )


def disjoint_matching(edges):
    """A deterministic (not necessarily maximum) disjoint-edge certificate."""
    used, result = set(), []
    for i, j in edges:
        if i not in used and j not in used:
            used.update((i, j))
            result.append((i, j))
    return tuple(result)


def valid_cover(edges, dropped):
    return all(i in dropped or j in dropped for i, j in edges)


def matching_six_covers(edges):
    """Independent product enumeration using a 5/6-edge matching.

    Seven disjoint edges exclude every six-vertex cover. For a 5-edge
    matching, choose one endpoint of each, then an arbitrary sixth vertex.
    """
    matching = disjoint_matching(edges)
    if len(matching) >= 7:
        return set()
    if len(matching) not in (5, 6):
        raise AssertionError("unexpected matching size")
    covers = set()
    for endpoints in product(*matching):
        seed = frozenset(endpoints)
        options = (seed,) if len(matching) == 6 else (
            seed | {v} for v in range(54) if v not in seed
        )
        for dropped in options:
            if valid_cover(edges, dropped):
                covers.add(dropped)
    return covers


def branch_six_covers(edges):
    """Independent edge-branching enumeration, with a safe matching prune."""
    found = set()

    def visit(remaining, chosen):
        if len(chosen) > 6:
            return
        if not remaining:
            found.add(chosen)
            return
        if len(chosen) + len(disjoint_matching(remaining)) > 6:
            return
        i, j = remaining[0]
        visit(tuple(e for e in remaining if i not in e), chosen | {i})
        visit(tuple(e for e in remaining if j not in e), chosen | {j})

    visit(edges, frozenset())
    six = set()
    for cover in found:
        for extra in combinations((i for i in range(54) if i not in cover),
                                  6 - len(cover)):
            six.add(cover | frozenset(extra))
    return six


def candidate_catalog():
    """Only the two types surviving the 7-edge exclusion can be added."""
    old = set(FAMILY)
    inside = [
        base.mask(p) for p in combinations(range(18), 4)
        if base.mask(p) not in old and base.orbit_key(p) == INSIDE
    ]
    outside = [
        base.mask(p + (18,)) for p in combinations(range(18), 3)
        if base.orbit_key(p + (18,)) == OUTSIDE
    ]
    assert len(inside) == 162 and len(outside) == 108
    return tuple(inside), tuple(outside)


def literal_edges(candidate):
    """Separate frozenset-intersection implementation of the forbidden graph."""
    old = [
        frozenset(v for v in range(18) if member & (1 << v))
        for member in FAMILY
    ]
    c = frozenset(v for v in range(22) if candidate & (1 << v))
    return tuple(
        (i, j)
        for i in range(54)
        for j in range(i)
        if old[i] & old[j] == old[i] & c == old[j] & c
    )



def direct_22_sweep():
    """No orbit keys or forbidden-edge table: literal 22-point negative sweep.

    The 22-point universe realizes all 0..4 outsider patterns. Normalize the
    one-outside survivors to label 18 only after the direct scan.
    """
    old = [
        frozenset(v for v in range(18) if member & (1 << v))
        for member in FAMILY
    ]
    old_masks = set(FAMILY)
    survivors = []
    for points in combinations(range(22), 4):
        if base.mask(points) in old_masks:
            continue
        c = frozenset(points)
        used, count = set(), 0
        for i in range(54):
            if i in used:
                continue
            for j in range(i):
                if j in used:
                    continue
                if old[i] & old[j] == old[i] & c == old[j] & c:
                    used.update((i, j))
                    count += 1
                    break
            if count >= 7:
                break
        if count < 7:
            survivors.append(points)
    normalized = {base.mask(tuple(18 if v >= 18 else v for v in points))
                  for points in survivors}
    return len(survivors), normalized


def check(include_literal=True):
    reps, orbit_counts = base.orbit_representatives()
    assert len(reps) == 18 and sum(orbit_counts.values()) == 7261
    assert base.verify_family(FAMILY)
    inside, outside = candidate_catalog()
    catalog = inside + outside
    if include_literal:
        total, normalized = direct_22_sweep()
        assert total == 594 and normalized == set(catalog)
    forbidden = {c: forbidden_edges(c) for c in catalog}
    if include_literal:
        for key, points in reps.items():
            c = base.mask(points)
            assert forbidden_edges(c) == literal_edges(c), key
        for c in catalog:
            assert forbidden[c] == literal_edges(c), c

    cover_counts = {}
    survivor_counts = {}
    exceptional = []
    total_six = 0
    for key, points in reps.items():
        edges = forbidden_edges(base.mask(points))
        matching = disjoint_matching(edges)
        assert len({v for e in matching for v in e}) == 2 * len(matching)
        assert all(e in edges for e in matching)
        if key not in (INSIDE, OUTSIDE):
            assert len(matching) >= 7, key
        else:
            assert len(matching) == (6 if key == INSIDE else 5), key
        covers_a = matching_six_covers(edges)
        covers_b = branch_six_covers(edges)
        assert covers_a == covers_b, (key, len(covers_a), len(covers_b))
        expected = 32 if key == INSIDE else 97 if key == OUTSIDE else 0
        assert len(covers_a) == expected, (key, len(covers_a))
        cover_counts[str(key)] = len(covers_a)
        total_six += len(covers_a)

        for dropped in covers_a:
            # A candidate is addable iff all old-old forbidden edges are hit.
            addable = [c for c in catalog if valid_cover(forbidden[c], dropped)]
            assert len(addable) == 1, (key, dropped, addable)
            c = addable[0]
            assert (c in inside) == (key == INSIDE)
            if include_literal:
                assert all(valid_cover(literal_edges(c), dropped)
                           for c in addable)
            kept = [a for i, a in enumerate(FAMILY) if i not in dropped]
            assert base.verify_family(kept + [c])
            if key == OUTSIDE:
                triple = c & ((1 << 18) - 1)
                survivors = sum((a & triple) == triple for a in kept)
                survivor_counts[survivors] = survivor_counts.get(survivors, 0) + 1
                assert survivors in (0, 1)
                if survivors == 0:
                    exceptional.append((dropped, triple))

    assert total_six == 129
    assert survivor_counts == {0: 1, 1: 96}, survivor_counts
    assert exceptional == [(EXCEPTIONAL_DROP, base.mask(EXCEPTIONAL_TRIPLE))]
    kept = [a for i, a in enumerate(FAMILY) if i not in EXCEPTIONAL_DROP]
    two = [base.mask(EXCEPTIONAL_TRIPLE + (18,)),
           base.mask(EXCEPTIONAL_TRIPLE + (19,))]
    assert base.verify_family(kept + two)
    assert not base.verify_family(kept + two +
                                  [base.mask(EXCEPTIONAL_TRIPLE + (20,))])
    # For any other outside cover, a surviving old set containing the
    # triple forms a sunflower with two distinct outsider completions.
    return {
        "orbit_types": 18,
        "seven_edge_excluded_types": 16,
        "inside_six_covers": 32,
        "outside_six_covers": 97,
        "catalog_inside": len(inside),
        "catalog_outside_triples": len(outside),
        "outside_survivor_counts": survivor_counts,
        "max_insertions_after_six_deletions": 2,
        "sharp_witness_final_size": len(kept + two),
        "independent_literal_intersections": include_literal,
        "literal_22_point_survivors": 594 if include_literal else None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="also cross-check every forbidden edge using frozensets")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = check(include_literal=args.check)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("M076 six-deletion local stability: exact bound 2, attained")
        print("18 orbit types; 16 excluded by seven disjoint forbidden pairs")
        print("32 inside and 97 outside six-covers; one addable support pattern each")
        print("Two independent cover enumerators: PASS")
        if args.check:
            print("Independent frozenset-intersection edge replay: PASS")


if __name__ == "__main__":
    main()
