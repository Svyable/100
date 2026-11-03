#!/usr/bin/env python3
"""Nine-deletion neighborhood of the classical 54-set four-uniform family.

Exact restricted theorem candidate. Same-author computational checks do not
constitute independent mathematical review or a historical priority audit.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations, product

from scripts import m076_f43_eight as eight
from scripts import m076_f43_stability as base

FAMILY = eight.FAMILY
THIRD = (0, (3, 1, 0), (0, 0, 0))
SURVIVORS = (eight.INSIDE, eight.OUTSIDE, THIRD)
NINE_DROP = eight.SHARP_DROP | {9}
NINE_INSERT = eight.SHARP_INSERT


def candidates():
    inside, outside = eight.candidate_catalog()
    third = tuple(base.mask(p) for p in combinations(range(18), 4)
                  if base.orbit_key(p) == THIRD)
    assert (len(inside), len(outside), len(third)) == (162, 108, 36)
    return inside, outside, third


def representative_graphs():
    reps, counts = base.orbit_representatives()
    assert len(reps) == 18 and sum(counts.values()) == 7261
    graphs = {key: eight.forbidden_edges(base.mask(p))
              for key, p in reps.items()}
    for key, edges in graphs.items():
        matching = eight.greedy_matching(edges)
        if key not in SURVIVORS:
            # Every pair is checked from literal sets in literal_orbit_check.
            assert len(matching) >= 10, (key, len(matching))
    assert tuple(len(eight.greedy_matching(graphs[k]))
                 for k in SURVIVORS) == (6, 5, 9)
    return graphs


def branch_nine_covers(edges):
    """Complete branching on uncovered edges, then exact-size expansion."""
    terminals = set()

    def rec(remaining, chosen):
        if chosen.bit_count() > 9:
            return
        if not remaining:
            terminals.add(chosen)
            return
        if chosen.bit_count() + len(eight.greedy_matching(remaining)) > 9:
            return
        edge = remaining[0]
        lo = edge & -edge
        for vertex in (lo, edge ^ lo):
            rec(tuple(e for e in remaining if not e & vertex),
                chosen | vertex)

    rec(edges, 0)
    covers = set()
    for chosen in terminals:
        free = [1 << i for i in range(54) if not chosen & (1 << i)]
        for extra in combinations(free, 9 - chosen.bit_count()):
            covers.add(chosen | sum(extra))
    return covers, len(terminals)


def product_nine_covers(edges):
    """Independent endpoint-product enumeration for a fixed matching."""
    matching = eight.greedy_matching(edges)
    result = set()
    for endpoints in product(*((edge & -edge, edge ^ (edge & -edge))
                               for edge in matching)):
        chosen = sum(endpoints)
        free = [1 << i for i in range(54) if not chosen & (1 << i)]
        for extra in combinations(free, 9 - len(matching)):
            deleted = chosen | sum(extra)
            if eight.is_cover(edges, deleted):
                result.add(deleted)
    return result


def cover_union(graphs, second_path=False):
    union = set()
    records = {}
    for key, expected, terminals_expected in (
        (eight.INSIDE, 470632, 128),
        (eight.OUTSIDE, 408481, 30),
        (THIRD, 8, 8),
    ):
        covers, terminals = branch_nine_covers(graphs[key])
        assert len(covers) == expected and terminals == terminals_expected
        if second_path:
            assert covers == product_nine_covers(graphs[key]), key
        records[str(key)] = {"covers": len(covers), "branch_terminals": terminals}
        union.update(covers)
    assert len(union) == 878401
    return union, records


def insertion_capacity(deleted, allowed, outside_start=162, outside_end=270):
    """A safe sum of per-support insertion caps; ignores cross-support clashes."""
    total = 0
    for i, c in allowed:
        if outside_start <= i < outside_end:
            triple = c & eight.SUPPORT
            survivors = any((a & triple) == triple
                            for j, a in enumerate(FAMILY)
                            if not deleted & (1 << j))
            total += 1 if survivors else 2
        else:
            total += 1
    return total


def capacity_census(covers, catalog):
    edge_map = tuple(eight.forbidden_edges(c) for c in catalog)
    # Precompute surviving-old-superset masks for outside support triples.
    supermask = tuple(
        sum(1 << j for j, a in enumerate(FAMILY)
            if (a & (c & eight.SUPPORT)) == (c & eight.SUPPORT))
        if 162 <= i < 270 else 0
        for i, c in enumerate(catalog)
    )
    distribution = Counter()
    high = {}
    for deleted in covers:
        allowed = tuple(i for i, edges in enumerate(edge_map)
                        if all(deleted & e for e in edges))
        cap = sum(
            2 if 162 <= i < 270 and not (supermask[i] & ~deleted) else 1
            for i in allowed
        )
        distribution[cap] += 1
        if cap >= 5:
            high[deleted] = allowed
    assert dict(distribution) == {
        1: 752354, 2: 115481, 3: 9104, 4: 1331, 5: 80, 6: 51
    }, dict(distribution)
    assert len(high) == 131
    return distribution, high


def literal_sunflower(a, b, c):
    return a & b == a & c == b & c


def set_partitions(n):
    """All partitions of n outside occurrences, up to relabeling."""
    def rec(i, blocks, labels):
        if i == n:
            yield tuple(labels)
            return
        for label in range(blocks + 1):
            labels.append(label)
            yield from rec(i + 1, max(blocks, label + 1), labels)
            labels.pop()
    yield from rec(0, 0, [])


def literal_five_search(high, catalog):
    """Exhaust five insertions with all equality patterns of outside labels.

    Old-old-new is separately rechecked with literal sets. New-new-old and
    new-new-new are checked for every partition of outside occurrences.
    """
    old = [frozenset(i for i in range(18) if a & (1 << i))
           for a in FAMILY]
    tested_subsets = tested_partitions = 0
    for deleted, allowed in high.items():
        kept = [a for i, a in enumerate(old) if not deleted & (1 << i)]
        slots = []
        for i in allowed:
            c = catalog[i]
            support = frozenset(j for j in range(18) if c & (1 << j))
            if 162 <= i < 270:
                n = 1 if any(support <= a for a in kept) else 2
                slots.extend(("outside", support) for _ in range(n))
            else:
                slots.append(("inside", support))
            # Independent literal check of every old-old-new obstruction.
            probe = support | (frozenset((18,)) if 162 <= i < 270 else frozenset())
            assert all(not literal_sunflower(a, b, probe)
                       for a, b in combinations(kept, 2))
        assert len(slots) in (5, 6)
        for indices in combinations(range(len(slots)), 5):
            tested_subsets += 1
            selected = [slots[i] for i in indices]
            fixed = [s for kind, s in selected if kind == "inside"]
            out = [s for kind, s in selected if kind == "outside"]
            for labels in set_partitions(len(out)):
                if any(labels[i] == labels[j] and out[i] == out[j]
                       for i in range(len(out)) for j in range(i)):
                    continue
                tested_partitions += 1
                inserted = fixed + [
                    s | frozenset((18 + labels[i],))
                    for i, s in enumerate(out)
                ]
                if any(literal_sunflower(a, b, c)
                       for a, b in combinations(inserted, 2) for c in kept):
                    continue
                if any(literal_sunflower(a, b, c)
                       for a, b, c in combinations(inserted, 3)):
                    continue
                return {
                    "falsifier_deleted": [i for i in range(54) if deleted & (1 << i)],
                    "falsifier_inserted": [sorted(s) for s in inserted],
                }
    return {"tested_five_subsets": tested_subsets,
            "tested_outside_partitions": tested_partitions}


def literal_orbit_check(graphs):
    old = [frozenset(i for i in range(18) if a & (1 << i))
           for a in FAMILY]
    reps, _ = base.orbit_representatives()
    for key, edges in graphs.items():
        c = frozenset(reps[key])
        pairs = [(i, j) for i in range(54) for j in range(i)
                 if literal_sunflower(old[i], old[j], c)]
        assert {((1 << i) | (1 << j)) for i, j in pairs} == set(edges)
        if key not in SURVIVORS:
            matching = eight.greedy_matching(edges)[:10]
            assert len(matching) == 10
            assert len({v for e in matching
                        for v in range(54) if e & (1 << v)}) == 20
    return True



def literal_direct_sweep():
    """Orbit-free 22-point replay using frozenset intersections."""
    old = [frozenset(i for i in range(18) if a & (1 << i))
           for a in FAMILY]
    old_set = set(old)

    def greedy_pairs(edges):
        used, count = set(), 0
        for i, j in edges:
            if i not in used and j not in used:
                used.update((i, j))
                count += 1
        return count

    def has_cover(edges, budget):
        if not edges:
            return True
        if budget == 0 or greedy_pairs(edges) > budget:
            return False
        i, j = edges[0]
        return (has_cover(tuple(e for e in edges if i not in e), budget - 1)
                or has_cover(tuple(e for e in edges if j not in e), budget - 1))

    survivors = []
    for p in combinations(range(22), 4):
        candidate = frozenset(p)
        if candidate in old_set:
            continue
        edges = tuple((i, j) for i in range(54) for j in range(i)
                      if literal_sunflower(old[i], old[j], candidate))
        if has_cover(edges, 9):
            survivors.append(p)
    normalized = {base.mask(tuple(18 if i >= 18 else i for i in p))
                  for p in survivors}
    return len(survivors), normalized

def literal_sharp_check():
    old = [frozenset(i for i in range(18) if a & (1 << i))
           for j, a in enumerate(FAMILY) if j not in NINE_DROP]
    new = [frozenset(s) for s in NINE_INSERT]
    family = old + new
    return len(family) == len(set(family)) == 49 and all(
        not literal_sunflower(a, b, c)
        for a, b, c in combinations(family, 3)
    )


def check(second_path=True):
    assert base.verify_family(FAMILY)
    graphs = representative_graphs()
    assert literal_orbit_check(graphs)
    catalog = sum(candidates(), ())
    if second_path:
        n, normalized = literal_direct_sweep()
        assert n == 630 and normalized == set(catalog), (n, len(normalized))
    covers, records = cover_union(graphs, second_path=second_path)
    distribution, high = capacity_census(covers, catalog)
    no_five = literal_five_search(high, catalog)
    assert "falsifier_deleted" not in no_five, no_five
    assert literal_sharp_check()
    return {
        "orbit_types": 18, "excluded_by_ten_disjoint_pairs": 15,
        "surviving_types": 3, "candidate_support_patterns": len(catalog),
        "representative_cover_counts": records,
        "distinct_nine_covers": len(covers),
        "capacity_distribution": dict(sorted(distribution.items())),
        "high_capacity_covers": len(high),
        "no_five_literal_search": no_five,
        "sharp_max_insertions": 4, "sharp_final_size": 49,
        "second_cover_enumerator": second_path,
        "independent_mathematical_review": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="also compare complete endpoint-product cover enumerator")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = check(second_path=args.check)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("M076 nine-deletion: sharp bound of four insertions")
        print("878,401 covers; 131 high-capacity covers, none admits five")


if __name__ == "__main__":
    main()
