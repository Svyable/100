"""Optional independent graph-metric full-cut LP and tour DP audit (SciPy)."""
from __future__ import annotations
import argparse
import json
from collections import deque
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, product


def solve(lengths):
    import numpy as np
    from scipy.optimize import linprog
    k = len(lengths)
    graph = {0: {1}, 1: {0}}
    first = []
    nxt = 2
    for length in lengths:
        previous = 0
        for _ in range(length - 1):
            v = nxt
            nxt += 1
            graph.setdefault(previous, set()).add(v)
            graph[v] = {previous}
            previous = v
            if _ == 0:
                first.append(v)
        graph[previous].add(1)
        graph[1].add(previous)
    a, b = first[:2]
    graph[a].add(b)
    graph[b].add(a)
    n = nxt
    distances = []
    for source in range(n):
        ds = [-1] * n
        ds[source] = 0
        q = deque([source])
        while q:
            u = q.popleft()
            for v in graph[u]:
                if ds[v] == -1:
                    ds[v] = ds[u] + 1
                    q.append(v)
        distances.append(ds)
    pairs = list(combinations(range(n), 2))
    c = np.array([distances[a][b] for a, b in pairs], dtype=float)
    degree = np.array([[int(v in ab) for ab in pairs] for v in range(n)], dtype=float)
    cut = np.array([[int(bool(mask & (1 << a)) != bool(mask & (1 << b))) for a, b in pairs]
                    for mask in range(1, 1 << (n - 1))], dtype=float)
    r = linprog(c, A_eq=degree, b_eq=2 * np.ones(n), A_ub=-cut,
                b_ub=-2 * np.ones(len(cut)), bounds=(0, None), method="highs")
    if not r.success:
        raise RuntimeError(r.message)
    @lru_cache(None)
    def dp(mask, end):
        if mask == 1 << (end - 1):
            return distances[0][end]
        return min(dp(mask ^ (1 << (end - 1)), j) + distances[j][end]
                   for j in range(1, n) if j != end and mask & (1 << (j - 1)))
    tsp = min(dp((1 << (n - 1)) - 1, j) + distances[j][0] for j in range(1, n))
    return r.fun, tsp


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--max-vertices', type=int, default=10)
    p.add_argument('--json', action='store_true')
    args = p.parse_args()
    checked = 0
    half = 0
    for k in range(3, 6):
        for a, b in product(range(2, 6), repeat=2):
            for tail in combinations_with_replacement(range(2, 6), k - 2):
                L = (a, b, *tail)
                if sum(L) - k + 2 > args.max_vertices:
                    continue
                m = sum(L)
                lp_expected = m - (0.5 if k == 3 and min(a, b) >= 3 else 1)
                tsp_expected = m - 1 if (k % 2 == 0 or min(a, b) == 2 or
                                         (k >= 5 and 2 in tail)) else m
                lp, tsp = solve(L)
                if abs(lp - lp_expected) > 1e-8 or tsp != tsp_expected:
                    raise AssertionError((L, lp, tsp, lp_expected, tsp_expected))
                checked += 1
                half += lp_expected != int(lp_expected)
    result = {'independent_full_cut_lp_and_dp': checked, 'half_integral_cases': half,
              'max_vertices': args.max_vertices}
    print(json.dumps(result, sort_keys=True) if args.json else result)


if __name__ == '__main__':
    main()
