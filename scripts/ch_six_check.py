#!/usr/bin/env python3
"""Exhaustive six-vertex check for the finite M074 elementary argument.

All partial orientations of K6 are considered: each unordered pair is
either unused, directed forward, or directed backward. Pruning uses only a
completed directed triangle or the impossibility of reaching outdegree 2.
The paper proof does NOT rely on this computational search.
"""
from itertools import combinations


def has_triangle(out):
    """Independent full check on any adjacency-mask tuple."""
    n = len(out)
    return any(
        (out[u] >> v & 1) and (out[v] >> w & 1) and (out[w] >> u & 1)
        for u in range(n) for v in range(n) for w in range(n)
    )


def search_six():
    n = 6
    pairs = list(combinations(range(n), 2))
    out = [0] * n
    degree = [0] * n
    remaining = [n - 1] * n
    visited = 0
    pruned_triangle = 0
    pruned_degree = 0

    def visit(index):
        nonlocal visited, pruned_triangle, pruned_degree
        visited += 1
        if index == len(pairs):
            if all(x >= 2 for x in degree):
                assert not has_triangle(out)
                return tuple(out)
            return None
        u, v = pairs[index]
        remaining[u] -= 1
        remaining[v] -= 1
        for src, dst in ((u, v), (v, u), (-1, -1)):
            if src >= 0:
                # A newly created directed triangle must use the newest arc.
                if any((out[dst] >> w & 1) and (out[w] >> src & 1)
                       for w in range(n)):
                    pruned_triangle += 1
                    continue
                out[src] |= 1 << dst
                degree[src] += 1
            if all(degree[z] + remaining[z] >= 2 for z in range(n)):
                result = visit(index + 1)
                if result is not None:
                    return result
            else:
                pruned_degree += 1
            if src >= 0:
                out[src] &= ~(1 << dst)
                degree[src] -= 1
        remaining[u] += 1
        remaining[v] += 1
        return None

    witness = visit(0)
    return dict(witness=witness, visited=visited,
                pruned_triangle=pruned_triangle, pruned_degree=pruned_degree)


if __name__ == "__main__":
    import json
    result = search_six()
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(1 if result["witness"] is not None else 0)
