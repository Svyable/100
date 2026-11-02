#!/usr/bin/env python3
"""M097 subdivided parallel-path graphic metric: exact rational SEP witness.

Claim #187. Author-side verification, not independent mathematical review.
"""
import argparse
from collections import deque
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, combinations_with_replacement
import json


def build_graph(lengths):
    lengths = tuple(lengths)
    if len(lengths) < 2 or any(not isinstance(l, int) or isinstance(l, bool)
                                or l < 2 for l in lengths):
        raise ValueError("at least two paths, each of integer length >= 2")
    edges, near0, near1, paths = set(), [], [], []
    next_vertex = 2
    for length in lengths:
        path = [0] + list(range(next_vertex, next_vertex + length - 1)) + [1]
        next_vertex += length - 1
        paths.append(path)
        near0.append(path[1])
        near1.append(path[-2])
        edges.update(tuple(sorted((u, v))) for u, v in zip(path, path[1:]))
    return next_vertex, edges, paths, (near0, near1)


def metric(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    out = []
    for root in range(n):
        d = [-1] * n
        d[root] = 0
        q = deque([root])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if d[v] < 0:
                    d[v] = d[u] + 1
                    q.append(v)
        if -1 in d:
            raise ValueError("disconnected")
        out.append(d)
    return out


def primal(lengths):
    n, edges, paths, neighbors = build_graph(lengths)
    k = len(paths)
    x = {e: Fraction(2, k) if 0 in e or 1 in e else Fraction(1)
         for e in edges}
    gamma = Fraction(k - 2, k * (k - 1))
    for near in neighbors:
        for u, v in combinations(near, 2):
            e = tuple(sorted((u, v)))
            x[e] = x.get(e, Fraction(0)) + gamma
    return n, {e: w for e, w in x.items() if w}


def check_primal(lengths, point=None):
    n, edges, _, _ = build_graph(lengths)
    d = metric(n, edges)
    if point is None:
        n2, point = primal(lengths)
        assert n == n2
    if any(not (0 <= u < v < n) or not isinstance(w, Fraction) or w < 0
           for (u, v), w in point.items()):
        raise AssertionError("invalid edge or weight")
    for v in range(n):
        if sum((w for (a, b), w in point.items() if v in (a, b)),
               Fraction(0)) != 2:
            raise AssertionError("degree")
    for mask in range(1, (1 << n) - 1):
        if not mask & 1:
            continue
        crossing = sum((w for (u, v), w in point.items()
                        if bool(mask & (1 << u)) != bool(mask & (1 << v))),
                       Fraction(0))
        if crossing < 2:
            raise AssertionError(("subtour cut", mask, crossing))
    value = sum((d[u][v] * w for (u, v), w in point.items()), Fraction(0))
    if value != sum(lengths):
        raise AssertionError(("primal cost", value))
    return value


def tsp_dp(dist):
    """Independent integer tour DP, not the graph-path parity proof."""
    n = len(dist)
    @lru_cache(None)
    def visit(mask, last):
        if mask == (1 << n) - 1:
            return dist[last][0]
        return min(dist[last][j] + visit(mask | (1 << j), j)
                   for j in range(1, n) if not mask & (1 << j))
    return visit(1, 0)


def tsp_formula(lengths):
    build_graph(lengths)
    return sum(lengths) + (len(lengths) % 2) * (min(lengths) - 2)


def check_instance(lengths):
    n, edges, _, _ = build_graph(lengths)
    lp = check_primal(lengths)
    integer = tsp_dp(metric(n, edges))
    expected = tsp_formula(lengths)
    if integer != expected:
        raise AssertionError((lengths, integer, expected))
    return {"paths": list(lengths), "vertices": n, "lp": str(lp),
            "tsp": integer, "ratio": str(Fraction(integer, lp))}


def all_small(max_vertices=11, max_paths=5, max_length=6):
    rows = []
    for k in range(2, max_paths + 1):
        for lengths in combinations_with_replacement(range(2, max_length + 1), k):
            if 2 + sum(l - 1 for l in lengths) <= max_vertices:
                rows.append(check_instance(lengths))
    return rows


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--max-vertices", type=int, default=11)
    args = p.parse_args()
    if not args.check:
        p.error("specify --check")
    rows = all_small(max_vertices=args.max_vertices)
    print(json.dumps({"cases": len(rows),
                      "fractional": sum(Fraction(r["ratio"]) > 1 for r in rows),
                      "max_ratio": str(max(Fraction(r["ratio"]) for r in rows)),
                      "max_vertices": args.max_vertices}, sort_keys=True))
