#!/usr/bin/env python3
"""Exact 17-edge obstruction for seven-vertex directed-C3-free digraphs with max indegree 3.

A 17-edge candidate lacks four undirected pairs. If its underlying graph
contains K5, a C3-free orientation gives a sink with indegree >=4. Otherwise
the four missing edges have minimum vertex cover at least three, and are
isomorphic to one of the THREE listed graphs. The 2^17 orientation decisions
for each representative are exhausted using integer bitsets.

This proves the seven-vertex max-16 lemma, NOT a 27-vertex theorem.
"""
import argparse
import json
from itertools import combinations

PAIRS = tuple(combinations(range(7), 2))
MISSING_TYPES = {
    "triangle_plus_edge": ((0, 1), (0, 2), (1, 2), (3, 4)),
    "path4_plus_edge": ((0, 1), (0, 2), (1, 3), (4, 5)),
    "path3_plus_two_edges": ((0, 1), (0, 2), (3, 4), (5, 6)),
}


def enumerate_orientation_class(missing):
    excluded = set(missing)
    edges = tuple(edge for edge in PAIRS if edge not in excluded)
    if len(edges) != 17:
        raise ValueError("Expected exactly four distinct missing unordered pairs")
    admissible = 0
    counterexamples = 0
    for bits in range(1 << len(edges)):
        out = [0] * 7
        incoming = [0] * 7
        for i, (u, v) in enumerate(edges):
            if bits & (1 << i):
                u, v = v, u
            out[u] |= 1 << v
            incoming[v] |= 1 << u
        if any(mask.bit_count() > 3 for mask in incoming):
            continue
        admissible += 1
        if not any(out[v] & incoming[u]
                   for u in range(7) for v in range(7)
                   if out[u] & (1 << v)):
            counterexamples += 1
    return {"orientations": 1 << 17,
            "indegree_cap_survivors": admissible,
            "triangle_free_and_cap": counterexamples}


def report():
    results = {name: enumerate_orientation_class(rep)
               for name, rep in MISSING_TYPES.items()}
    return {
        "missing_graph_types": len(results),
        "exact_checks": results,
        "global_seven_vertex_arc_ceiling": 16,
        "scope": "Exact seven-vertex lemma only; no full CH27 or general claim",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    results = report()
    print(json.dumps(results, sort_keys=True, indent=2))
    if args.check:
        expected = {
            "triangle_plus_edge": 17192,
            "path4_plus_edge": 18460,
            "path3_plus_two_edges": 20004,
        }
        for name, number in expected.items():
            assert results["exact_checks"][name] == {
                "orientations": 131072,
                "indegree_cap_survivors": number,
                "triangle_free_and_cap": 0,
            }


if __name__ == "__main__":
    main()
