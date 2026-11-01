#!/usr/bin/env python3
"""Audit the seven-vertex dense-cut lemma used in the CH (27,9) irregular branch.

The mathematical proof is proofs/M074_SEVEN_VERTEX_CAP.md. This exhaustive
check covers the sole 18-edge underlying graph that survives the K5 argument;
it does not search 27-vertex digraphs.
"""
import argparse
import json
from itertools import combinations

N = 7
MISSING = frozenset({(0, 1), (2, 3), (4, 5)})
PAIRS = tuple(p for p in combinations(range(N), 2) if p not in MISSING)
POSITIVE = ((0, 1), (0, 2), (0, 5), (0, 6), (1, 2), (1, 3),
            (2, 5), (4, 0), (4, 1), (4, 2), (4, 5), (4, 6),
            (5, 3), (5, 6), (6, 1), (6, 3))


def inspect_edges(edges):
    """Independent strict loop/digon/triangle and indegree test."""
    out = [0] * N
    incoming = [0] * N
    seen = set()
    for u, v in edges:
        if not (type(u) is int and type(v) is int and
                0 <= u < N and 0 <= v < N and u != v):
            raise ValueError("invalid arc")
        if (u, v) in seen or (v, u) in seen:
            raise ValueError("duplicate arc or digon")
        seen.add((u, v))
        out[u] |= 1 << v
        incoming[v] |= 1 << u
    triangle = any(out[v] & incoming[u]
                   for u in range(N)
                   for v in range(N) if out[u] & (1 << v))
    return {"arcs": len(seen),
            "maximum_indegree": max(x.bit_count() for x in incoming),
            "triangle_free": not triangle}


def enumerate_unique_dense_graph():
    """Enumerate all orientations of K7 minus a matching of three pairs."""
    assert len(PAIRS) == 18
    admissible_degree = 0
    c3_free = 0
    for mask in range(1 << 18):
        out = [0] * N
        incoming = [0] * N
        for bit, (u, v) in enumerate(PAIRS):
            if mask & (1 << bit):
                u, v = v, u
            out[u] |= 1 << v
            incoming[v] |= 1 << u
        if max(bits.bit_count() for bits in incoming) > 3:
            continue
        admissible_degree += 1
        if not any(out[v] & incoming[u]
                   for u in range(N)
                   for v in range(N) if out[u] & (1 << v)):
            c3_free += 1
    return {"orientations": 1 << 18,
            "indegree_cap_survivors": admissible_degree,
            "triangle_free_and_cap": c3_free}


def boundary_profile():
    """Show that the former z=4 relaxed control violates the new C-cap."""
    alpha = (2,)*7 + (7, 8)
    incoming_c_to_b = (0,)*4 + (5,)*4 + (7,)*2
    m = sum(alpha)
    k = sum(incoming_c_to_b)
    return {"alpha2_vertices": alpha.count(2),
            "maximum_indegree_inside_C": 10-alpha.count(2),
            "minimum_arcs_inside_C": 63-k-(m-18),
            "seven_vertex_arc_cap": 17,
            "excluded": 63-k-(m-18) > 17}


def report():
    r = enumerate_unique_dense_graph()
    witness = inspect_edges(POSITIVE)
    return {"dense_class": r, "positive_control": witness,
            "former_relaxed_profile": boundary_profile(),
            "scope": "Seven-vertex lemma and one irregular integer profile only"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = report()
    print(json.dumps(result, sort_keys=True, indent=2))
    if args.check:
        assert result["dense_class"] == {
            "orientations": 262144,
            "indegree_cap_survivors": 19592,
            "triangle_free_and_cap": 0,
        }
        assert result["positive_control"] == {
            "arcs": 16, "maximum_indegree": 3, "triangle_free": True
        }
        assert result["former_relaxed_profile"] == {
            "alpha2_vertices": 7,
            "maximum_indegree_inside_C": 3,
            "minimum_arcs_inside_C": 18,
            "seven_vertex_arc_cap": 17,
            "excluded": True,
        }


if __name__ == "__main__":
    main()
