"""Optional, separately represented full subtour LP audit for claim #232.

Requires SciPy and NumPy. No imports from m097_cross_end.py. This
numerical optimization is a falsifier, not a proof or independent review.
"""
import argparse
from collections import deque
from functools import lru_cache
from itertools import combinations, product
import json


def instance(lengths):
    n = 2
    adj = {0: {1}, 1: {0}}
    paths = []
    def edge(a, b):
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    for length in lengths:
        path = [0] + list(range(n, n + length - 1)) + [1]
        n += length - 1
        paths.append(path)
        for a, b in zip(path, path[1:]):
            edge(a, b)
    edge(paths[0][1], paths[1][-2])
    metric = []
    for s in range(n):
        d = {s: 0}
        q = deque([s])
        while q:
            a = q.popleft()
            for b in adj[a]:
                if b not in d:
                    d[b] = d[a] + 1
                    q.append(b)
        metric.append([d[v] for v in range(n)])
    return metric


def optimum_lp(metric):
    import numpy as np
    from scipy.optimize import linprog
    n = len(metric)
    pairs = list(combinations(range(n), 2))
    objective = np.array([metric[a][b] for a, b in pairs], dtype=float)
    degrees = np.zeros((n, len(pairs)))
    for j, (a, b) in enumerate(pairs):
        degrees[a, j] = degrees[b, j] = 1
    cuts = np.array([
        [-int(bool(mask & (1 << a)) != bool(mask & (1 << b)))
         for a, b in pairs]
        for mask in range(1, 1 << (n - 1))
    ], dtype=float)
    result = linprog(
        objective, A_eq=degrees, b_eq=np.full(n, 2),
        A_ub=cuts, b_ub=np.full(len(cuts), -2),
        bounds=(0, None), method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)
    return result.fun


def optimum_tour(metric):
    n = len(metric)
    @lru_cache(None)
    def dp(mask, last):
        if mask == (1 << (last - 1)):
            return metric[0][last]
        prev_mask = mask ^ (1 << (last - 1))
        return min(dp(prev_mask, prev) + metric[prev][last]
                   for prev in range(1, n)
                   if prev_mask & (1 << (prev - 1)))
    mask = (1 << (n - 1)) - 1
    return min(dp(mask, end) + metric[end][0] for end in range(1, n))


def run(max_vertices=10):
    checked = 0
    for k in range(3, 6):
        for lengths in product(range(2, 6), repeat=k):
            n = 2 + sum(L - 1 for L in lengths)
            if n > max_vertices:
                continue
            metric = instance(lengths)
            m = sum(lengths)
            target_lp = m - 1
            target_tsp = target_lp + int(k % 2 == 0 and min(lengths) >= 3)
            lp = optimum_lp(metric)
            tsp = optimum_tour(metric)
            if abs(lp - target_lp) > 1e-7 or tsp != target_tsp:
                raise AssertionError((lengths, lp, tsp, target_lp, target_tsp))
            checked += 1
    return {"checked": checked, "max_vertices": max_vertices,
            "method": "independent full-cut SciPy HiGHS and subset DP"}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--max-vertices", type=int, default=10)
    args = p.parse_args()
    print(json.dumps(run(args.max_vertices), sort_keys=True))
