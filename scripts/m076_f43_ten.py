#!/usr/bin/env python3
"""Sharp ten-deletion stability of the classical 54-set sunflower family.

A bounded exact certificate, not a global sunflower bound or an independently
reviewed result. C++ enumerates ten-covers; Python independently checks the
high-capacity masks using literal sets and all outsider equality partitions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import tempfile
from collections import Counter
from itertools import combinations
from pathlib import Path

from scripts import m076_f43_eight as eight
from scripts import m076_f43_nine as nine
from scripts import m076_f43_stability as base

WORK_ID = "X-M076-F43-TEN-FIVE"
SCOPE_SHA256 = "ab92a6f1f2243e7be174b8eadd16105947d0542f92a71ffc1d8587cf750ad295"
DROP = frozenset((0, 2, 3, 5, 6, 8, 18, 24, 25, 26))
INSERT = ((0, 1, 3, 18), (0, 2, 3, 18), (1, 2, 3, 18),
          (3, 6, 7, 18), (5, 6, 7, 18))


def minimal_covers(edges, budget=10):
    """All inclusion-minimal vertex covers of size <= budget.

    Branching on an uncovered edge is complete. A disjoint-edge matching is
    a safe lower bound; terminal supersets are removed by inclusion.
    """
    terminals = set()

    def rec(remaining, chosen):
        if chosen.bit_count() > budget:
            return
        if not remaining:
            terminals.add(chosen)
            return
        if chosen.bit_count() + len(eight.greedy_matching(remaining)) > budget:
            return
        edge = remaining[0]
        lo = edge & -edge
        for vertex in (lo, edge ^ lo):
            rec(tuple(e for e in remaining if not e & vertex),
                chosen | vertex)

    rec(tuple(edges), 0)
    minimal = {s for s in terminals if not any(
        t != s and (t & s) == t for t in terminals)}
    assert all(eight.is_cover(edges, s) for s in minimal)
    assert all(not eight.is_cover(edges, s ^ (1 << i))
               for s in minimal for i in range(54) if s & (1 << i))
    return minimal


def inputs():
    assert base.verify_family(eight.FAMILY)
    reps, counts = base.orbit_representatives()
    assert len(reps) == 18 and sum(counts.values()) == 7261
    graphs = nine.representative_graphs()
    assert set(graphs) == set(reps)
    old = [frozenset(i for i in range(18) if a & (1 << i))
           for a in eight.FAMILY]
    for key, edges in graphs.items():
        representative = frozenset(reps[key])
        literal_edges = {((1 << i) | (1 << j))
                         for i in range(54) for j in range(i)
                         if old[i] & old[j] == old[i] & representative
                         == old[j] & representative}
        assert literal_edges == set(edges)
        if key not in nine.SURVIVORS:
            matching = eight.greedy_matching(edges)[:11]
            assert len(matching) == 11
            assert (sum(e.bit_count() for e in matching),
                    (sum(matching)).bit_count()) == (22, 22)

    mins = set()
    by_type = {}
    for key, expected, sizes in (
        (eight.INSIDE, 32, {6: 32}),
        (eight.OUTSIDE, 4, {5: 2, 7: 2}),
        (nine.THIRD, 8, {9: 8}),
    ):
        covers = minimal_covers(graphs[key])
        assert len(covers) == expected
        assert dict(Counter(s.bit_count() for s in covers)) == sizes
        mins.update(covers)
        by_type[str(key)] = {"minimal_covers": len(covers),
                             "sizes": sizes}
    assert len(mins) == 44
    catalog = sum(nine.candidates(), ())
    assert len(catalog) == 306
    edge_map = tuple(eight.forbidden_edges(c) for c in catalog)
    # A spurious forbidden edge could incorrectly exclude a genuine
    # insertion. Replay *all* 306 graphs with a distinct set representation,
    # not merely the individually allowed candidates in the final census.
    for c, edges in zip(catalog, edge_map):
        candidate = frozenset(i for i in range(19) if c & (1 << i))
        literal_edges = {((1 << i) | (1 << j))
                         for i in range(54) for j in range(i)
                         if old[i] & old[j] == old[i] & candidate
                         == old[j] & candidate}
        assert literal_edges == set(edges)
    supers = tuple(
        sum(1 << j for j, a in enumerate(eight.FAMILY)
            if (a & c & eight.SUPPORT) == (c & eight.SUPPORT))
        if 162 <= i < 270 else 0
        for i, c in enumerate(catalog))
    for i, c in enumerate(catalog):
        if 162 <= i < 270:
            triple = frozenset(j for j in range(18) if c & (1 << j))
            literal_supers = sum(1 << j for j, a in enumerate(old)
                                 if triple <= a)
            assert literal_supers == supers[i]
    raw = [str(len(mins)), *(str(d) for d in sorted(mins)),
           str(len(catalog))]
    for i, edges in enumerate(edge_map):
        raw.append(" ".join(map(str, (len(edges), supers[i], *edges))))
    return "\n".join(raw) + "\n", catalog, edge_map, supers, by_type


def scan_cpp(data):
    """Enumerate all ten-supersets of all 44 minimal cover masks."""
    source = Path(__file__).with_name("m076_f43_ten_scan.cpp")
    assert source.is_file()
    with tempfile.TemporaryDirectory(prefix="m076-ten-") as tmp:
        binary = str(Path(tmp) / "scan")
        subprocess.run([os.environ.get("CXX", "c++"), "-O3", "-std=c++17",
                        str(source), "-o", binary], check=True,
                       capture_output=True, text=True, timeout=60)
        result = subprocess.run([binary], input=data, text=True,
                                capture_output=True, check=True, timeout=90)
    lines = result.stdout.splitlines()
    assert lines and lines[-1].startswith("SUMMARY ")
    summary = list(map(int, lines[-1].split()[1:]))
    assert len(summary) == 22
    visited, high_raw, *distribution = summary
    expected_visited = (32 * math.comb(48, 4)
                        + 2 * math.comb(49, 5)
                        + 2 * math.comb(47, 3)
                        + 8 * math.comb(45, 1))
    assert visited == expected_visited == 10073118
    assert high_raw == len(lines) - 1 == 18730
    assert {i: count for i, count in enumerate(distribution) if count} == {
        1: 7610670, 2: 2027990, 3: 329902, 4: 85826,
        5: 12490, 6: 5192, 7: 936, 8: 112}
    masks = {}
    for line in lines[:-1]:
        d, cap = map(int, line.split())
        assert d.bit_count() == 10 and cap >= 5
        if d in masks:
            assert masks[d] == cap
        masks[d] = cap
    assert len(masks) == 9841
    digest = hashlib.sha256(("\n".join(map(str, sorted(masks)))
                             + "\n").encode("ascii")).hexdigest()
    assert digest == "531d31cdc363cd14d072d1871065e5f10fbb99e02b133a41d785cf17f0c08d01"
    return masks, visited, high_raw, digest


def literal_sunflower(a, b, c):
    return a & b == a & c == b & c


def verify_witness():
    old = [frozenset(i for i in range(18) if a & (1 << i))
           for a in eight.FAMILY]
    new = [frozenset(p) for p in INSERT]
    assert len(DROP) == 10 and len(set(new)) == 5
    assert not set(new) & set(old)
    family = [a for i, a in enumerate(old) if i not in DROP] + new
    assert len(family) == len(set(family)) == 49
    assert all(not literal_sunflower(a, b, c)
               for a, b, c in combinations(family, 3))
    # The ten deleted sets are all essential to this particular witness.
    for j in DROP:
        restored = family + [old[j]]
        assert any(literal_sunflower(a, b, c)
                   for a, b, c in combinations(restored, 3))
    assert base.verify_family([base.mask(tuple(sorted(s))) for s in family])
    return len(family), math.comb(len(family), 3)


def verify_no_six(masks, catalog, edge_map, supers):
    """Literal replay of every potentially six-capable ten-cover.

    Old-old-new constraints are checked independently of the bitset scanner.
    All partitions of outside labels (not just all-distinct labels) are tested.
    """
    old = [frozenset(i for i in range(18) if a & (1 << i))
           for a in eight.FAMILY]
    support = [frozenset(i for i in range(18) if c & (1 << i))
               for c in catalog]
    caps = Counter()
    six_subsets = outsider_partitions = 0
    for d, claimed_cap in sorted(masks.items()):
        allowed = [i for i, edges in enumerate(edge_map)
                   if all(d & edge for edge in edges)]
        kept = [a for j, a in enumerate(old) if not d & (1 << j)]
        slots = []
        for i in allowed:
            probe = support[i] | (frozenset((18,))
                                  if 162 <= i < 270 else frozenset())
            assert all(not literal_sunflower(a, b, probe)
                       for a, b in combinations(kept, 2))
            copies = (2 if 162 <= i < 270 and not (supers[i] & ~d)
                      else 1)
            slots.extend([i] * copies)
        assert len(slots) == claimed_cap
        caps[len(slots)] += 1
        if len(slots) < 6:
            continue
        for choice in combinations(range(len(slots)), 6):
            six_subsets += 1
            ids = [slots[j] for j in choice]
            fixed = [support[i] for i in ids if not 162 <= i < 270]
            outside = [i for i in ids if 162 <= i < 270]
            for labels in nine.set_partitions(len(outside)):
                if any(outside[a] == outside[b] and labels[a] == labels[b]
                       for a, b in combinations(range(len(outside)), 2)):
                    continue
                inserted = fixed + [
                    support[i] | frozenset((18 + labels[j],))
                    for j, i in enumerate(outside)]
                outsider_partitions += 1
                if any(literal_sunflower(a, b, c)
                       for a, b in combinations(inserted, 2) for c in kept):
                    continue
                if any(literal_sunflower(a, b, c)
                       for a, b, c in combinations(inserted, 3)):
                    continue
                raise AssertionError(("six-insertion falsifier",
                                      [j for j in range(54) if d & (1 << j)],
                                      [sorted(x) for x in inserted]))
    assert dict(caps) == {5: 6836, 6: 2597, 7: 372, 8: 36}
    assert (six_subsets, outsider_partitions) == (6209, 35971)
    return dict(sorted(caps.items())), six_subsets, outsider_partitions


def check():
    data, catalog, edges, supers, cover_types = inputs()
    masks, visited, raw_high, digest = scan_cpp(data)
    caps, selections, partitions = verify_no_six(masks, catalog, edges, supers)
    size, triples = verify_witness()
    return {
        "work_id": WORK_ID,
        "orbit_types": 18,
        "excluded_by_eleven_disjoint_pairs": 15,
        "minimal_cover_templates": 44,
        "minimal_covers_by_type": cover_types,
        "candidate_support_patterns": len(catalog),
        "ten_cover_superset_visits_with_multiplicity": visited,
        "high_capacity_visits_with_multiplicity": raw_high,
        "distinct_high_capacity_ten_covers": len(masks),
        "high_capacity_mask_sha256": digest,
        "high_capacity_distribution": caps,
        "six_slot_subsets_checked": selections,
        "outsider_equality_patterns_checked": partitions,
        "sharp_max_insertions": 5,
        "sharp_family_size": size,
        "sharp_family_triples_checked": triples,
        "independent_mathematical_review": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = check()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("M076 ten-deletion: sharp five-insertion restricted candidate")
        print("9,841 high-capacity ten-covers; no six-insertion extension")


if __name__ == "__main__":
    main()
