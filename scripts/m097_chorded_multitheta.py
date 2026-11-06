"""Exact small-instance checks for chorded multitheta graphic TSP.

Claim X-M097-CHORDED-MULTITHETA (#228). This code does not establish
historical novelty or independent mathematical review.
"""
from collections import deque
from fractions import Fraction
from itertools import combinations, combinations_with_replacement
from functools import lru_cache
import argparse
import json


def build(lengths):
    if len(lengths) < 2 or min(lengths) < 2:
        raise ValueError('need >=2 long paths, each length >=2')
    n = 2
    edges = {(0, 1)}  # direct hub edge
    paths = []
    for length in lengths:
        interior = list(range(n, n + length - 1))
        n += length - 1
        path = [0] + interior + [1]
        paths.append(path)
        for a, b in zip(path, path[1:]):
            edges.add(tuple(sorted((a, b))))
    return n, sorted(edges), paths


def distances(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    ans = []
    for s in range(n):
        d = [-1] * n
        d[s] = 0
        q = deque([s])
        while q:
            a = q.popleft()
            for b in adj[a]:
                if d[b] == -1:
                    d[b] = d[a] + 1
                    q.append(b)
        assert -1 not in d
        ans.append(d)
    return ans


def lp_point(lengths, paths):
    k = len(lengths)
    alpha = Fraction(2, k)
    gamma = Fraction(k - 2, k * (k - 1))
    x = {}
    def add(a, b, w):
        key = tuple(sorted((a, b)))
        x[key] = x.get(key, Fraction(0)) + w
    for path in paths:
        for i, (a, b) in enumerate(zip(path, path[1:])):
            add(a, b, alpha if i == 0 or i == len(path) - 2 else Fraction(1))
    for i, j in combinations(range(k), 2):
        add(paths[i][1], paths[j][1], gamma)
        add(paths[i][-2], paths[j][-2], gamma)
    return x


def check_lp(lengths):
    n, edges, paths = build(lengths)
    d = distances(n, edges)
    x = lp_point(lengths, paths)
    assert all(w >= 0 for w in x.values())
    assert all(sum(w for (a, b), w in x.items() if v in (a, b)) == 2 for v in range(n))
    for mask in range(1, (1 << n) - 1):
        cut = sum(w for (a, b), w in x.items() if bool(mask & (1 << a)) != bool(mask & (1 << b)))
        assert cut >= 2, (lengths, mask, cut)
    value = sum(w * d[a][b] for (a, b), w in x.items())
    assert value == sum(lengths), (lengths, value)
    return value


def tour_dp(d):
    n = len(d)
    # Independent exact Held--Karp Hamiltonian-cycle DP; no path-mode assumptions.
    @lru_cache(None)
    def dp(mask, end):
        if mask == (1 << end):
            return d[0][end]
        prev = mask ^ (1 << end)
        return min(dp(prev, i) + d[i][end] for i in range(1, n) if prev & (1 << i))
    return min(dp(((1 << n) - 1) ^ 1, end) + d[end][0] for end in range(1, n))


def formula(lengths):
    m = sum(lengths)
    return m, m + (len(lengths) % 2) * min(1, min(lengths) - 2)


def run(max_vertices=10):
    checked = 0
    odd2 = odd3 = even = 0
    for k in range(2, 6):
        for lengths in combinations_with_replacement(range(2, 8), k):
            n = 2 + sum(v - 1 for v in lengths)
            if n > max_vertices:
                continue
            expected_lp, expected_tour = formula(lengths)
            assert check_lp(lengths) == expected_lp
            n, edges, paths = build(lengths)
            observed_tour = tour_dp(distances(n, edges))
            assert observed_tour == expected_tour, (lengths, observed_tour, expected_tour)
            checked += 1
            if k % 2 == 0: even += 1
            elif min(lengths) == 2: odd2 += 1
            else: odd3 += 1
    return dict(checked=checked, even=even, odd_with_length_two=odd2, odd_all_lengths_at_least_three=odd3)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--max-vertices', type=int, default=10)
    p.add_argument('--json', action='store_true')
    a = p.parse_args()
    result = run(a.max_vertices)
    print(json.dumps(result, sort_keys=True) if a.json else result)
