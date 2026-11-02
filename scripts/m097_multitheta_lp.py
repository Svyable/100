#!/usr/bin/env python3
"""Independent optional HiGHS LP formulation for X-M097-MULTITHETA.

This intentionally does not import m097_multitheta: independent graph, metric,
edge/cut indexing and rational LP-duality replay. Requires scipy + numpy.
Author-side cross-check only, not independent mathematical review.
"""
import argparse
from fractions import Fraction
from itertools import combinations, combinations_with_replacement
import json
import numpy as np
from scipy.optimize import linprog


def independent_instance(lengths):
    k = len(lengths)
    n = 2 + sum(t - 1 for t in lengths)
    adjacency = [set() for _ in range(n)]
    current = 2
    for t in lengths:
        vertices = [0] + list(range(current, current + t - 1)) + [1]
        current += t - 1
        for a, b in zip(vertices, vertices[1:]):
            adjacency[a].add(b)
            adjacency[b].add(a)
    dist = [[0 if a == b else n + 1 for b in range(n)] for a in range(n)]
    for a in range(n):
        seen = {a}
        frontier = [a]
        while frontier:
            new = []
            for u in frontier:
                for v in adjacency[u]:
                    if v not in seen:
                        seen.add(v)
                        dist[a][v] = dist[a][u] + 1
                        new.append(v)
            frontier = new
        assert len(seen) == n
    edges = list(combinations(range(n), 2))
    cost = [dist[a][b] for a, b in edges]
    Aeq = np.zeros((n, len(edges)))
    for j, (a, b) in enumerate(edges):
        Aeq[a, j] = Aeq[b, j] = 1
    cuts = []
    for mask in range(1, 1 << n):
        if mask & 1 and mask.bit_count() not in (1, n - 1, n):
            cuts.append([j for j, (a, b) in enumerate(edges)
                         if bool(mask & (1 << a)) != bool(mask & (1 << b))])
    Aub = np.zeros((len(cuts), len(edges)))
    for i, cut in enumerate(cuts):
        Aub[i, cut] = -1
    result = linprog(np.asarray(cost, dtype=float),
                     A_eq=Aeq, b_eq=np.full(n, 2.0),
                     A_ub=Aub, b_ub=np.full(len(cuts), -2.0),
                     bounds=(0, None), method="highs")
    if not result.success:
        raise AssertionError(result.message)
    rational = lambda seq: [Fraction(float(v)).limit_denominator(100000)
                            for v in seq]
    x = rational(result.x)
    y = rational(result.eqlin.marginals)
    z = rational(-result.ineqlin.marginals)
    assert all(v >= 0 for v in x + z)
    assert all(sum(x[j] for j, e in enumerate(edges) if a in e) == 2
               for a in range(n))
    assert all(sum(x[j] for j in cut) >= 2 for cut in cuts)
    reduced = [Fraction(cost[j]) - y[a] - y[b]
               for j, (a, b) in enumerate(edges)]
    for cut, multiplier in zip(cuts, z):
        if multiplier:
            for j in cut:
                reduced[j] -= multiplier
    assert all(v >= 0 for v in reduced)
    primal = sum(cost[j] * x[j] for j in range(len(edges)))
    dual = 2 * (sum(y) + sum(z))
    assert primal == dual == sum(lengths)
    return primal


def check_all():
    count = 0
    for k in range(2, 6):
        for lengths in combinations_with_replacement(range(2, 7), k):
            if 2 + sum(t - 1 for t in lengths) <= 11:
                independent_instance(lengths)
                count += 1
    assert count == 63
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("specify --check")
    print(json.dumps({"independent_lp_cases": check_all(),
                      "rational_primal_dual": True}, sort_keys=True))
