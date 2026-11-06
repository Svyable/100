"""Exact same-hub cross-edge two-hub metric TSP/SEP restricted certificate.

Run python -m scripts.m097_cross_same --max-vertices 11 --json.
All fractions exact; exhaustive cuts and Held-Karp are separate from proof formulas.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, product


def instance(lengths):
    L = tuple(lengths)
    if len(L) < 3 or any(type(z) is not int or z < 2 for z in L):
        raise ValueError("k>=3 and every length>=2 required")
    paths = []
    edges = {(0, 1)}
    nxt = 2
    for length in L:
        p = (0, *range(nxt, nxt + length - 1), 1)
        nxt += length - 1
        paths.append(p)
        edges.update(tuple(sorted((a, b))) for a, b in zip(p, p[1:]))
    edges.add(tuple(sorted((paths[0][1], paths[1][1]))))
    return nxt, tuple(paths), frozenset(edges)


def distances(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
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
            raise AssertionError("graph disconnected")
        out.append(tuple(d))
    return tuple(out)


def pair(a, b):
    if a == b:
        raise ValueError("loop")
    return (a, b) if a < b else (b, a)


def add(x, a, b, value):
    key = pair(a, b)
    x[key] = x.get(key, Fraction(0)) + Fraction(value)
    if not x[key]:
        del x[key]


def candidate_lp(lengths):
    """Exact constructive feasible point, not an optimizer."""
    n, paths, edges = instance(lengths)
    k = len(paths)
    x = {}
    if k == 3 and len(paths[0]) > 3 and len(paths[1]) > 3:
        for p in paths[:2]:
            for a, b in zip(p[1:-2], p[2:-1]):
                add(x, a, b, 1)
        for a, b in zip(paths[2], paths[2][1:]):
            add(x, a, b, 1)
        p1, p2 = paths[0][1], paths[1][1]
        q1, q2 = paths[0][-2], paths[1][-2]
        for a, b in [(0, p1), (0, p2), (1, q1), (1, q2), (p1, p2), (q1, q2)]:
            add(x, a, b, Fraction(1, 2))
    elif k == 3:
        # A Hamiltonian cycle in the graph: the crossed component forms a
        # u-v path when either crossed constituent has length two.
        e = eulerian_witness(lengths)
        tour = shortcut_euler(n, e)
        for a, b in zip(tour, tour[1:] + tour[:1]):
            add(x, a, b, 1)
    else:
        h = k - 2
        alpha = Fraction(2, h)
        gamma = Fraction(h - 2, h * (h - 1))
        old_paths = paths[2:]
        for p in old_paths:
            for a, b in zip(p, p[1:]):
                add(x, a, b, alpha if a in (0, 1) or b in (0, 1) else 1)
        for i, j in combinations(range(h), 2):
            add(x, old_paths[i][1], old_paths[j][1], gamma)
            add(x, old_paths[i][-2], old_paths[j][-2], gamma)
        # Subtour ear insertion: replace one unit of v-incidence by a path
        # through the crossed component, from q2 to q1 then back to v.
        remaining = Fraction(1)
        for a in sorted(v for e in x for v in e if 1 in e and v != 1):
            if remaining == 0:
                break
            t = min(remaining, x.get(pair(1, a), Fraction(0)))
            if t:
                add(x, 1, a, -t)
                add(x, a, paths[1][-2], t)
                remaining -= t
        if remaining:
            raise AssertionError("v-incidence below one")
        chain = list(reversed(paths[1][1:-1])) + list(paths[0][1:-1])
        for a, b in zip(chain, chain[1:]):
            add(x, a, b, 1)
        add(x, chain[-1], 1, 1)
    return x


def predicted(lengths):
    L = tuple(lengths)
    k = len(L)
    m = sum(L)
    lp = Fraction(m - 1)
    if k == 3 and min(L[:2]) >= 3:
        lp += Fraction(1, 2)
    if k % 2 == 0 or min(L[:2]) == 2 or (k >= 5 and 2 in L[2:]):
        tsp = m - 1
    else:
        tsp = m
    return lp, tsp


def eulerian_witness(lengths):
    """Explicit connected Eulerian multigraph of the claimed tour cost."""
    n, paths, _ = instance(lengths)
    L = tuple(lengths)
    k = len(L)
    mult = defaultdict(int)
    def edge(a, b, times=1):
        mult[pair(a, b)] += times
    if min(L[:2]) == 2 and k % 2:
        # Internal crossed chain from the short path's sole vertex to
        # the far end of the other crossed path, joining u to v.
        short, long = (0, 1) if L[0] == 2 else (1, 0)
        edge(0, paths[short][1])
        edge(paths[short][1], paths[long][1])
        for a, b in zip(paths[long][1:], paths[long][2:]):
            edge(a, b)
    else:
        # Cycle at v along both crossed paths and their cross-edge.
        for p in paths[:2]:
            for a, b in zip(p[1:], p[2:]):
                edge(a, b)
        edge(paths[0][1], paths[1][1])
    for p in paths[2:]:
        for a, b in zip(p, p[1:]):
            edge(a, b)
    if k % 2 and min(L[:2]) >= 3:
        if k >= 5 and 2 in L[2:]:
            p = paths[2 + L[2:].index(2)]
            edge(0, p[1], 1)  # now 2 copies of u-w
            edge(p[1], 1, -1)
        else:
            edge(0, 1)
    return {key: value for key, value in mult.items() if value}


def shortcut_euler(n, mult):
    adj = [[] for _ in range(n)]
    eid = 0
    for (a, b), count in mult.items():
        if count < 0:
            raise AssertionError("negative edge multiplicity")
        for _ in range(count):
            adj[a].append((b, eid))
            adj[b].append((a, eid))
            eid += 1
    if any(len(v) % 2 for v in adj):
        raise AssertionError("not Eulerian")
    used = set()
    stack = [0]
    walk = []
    while stack:
        v = stack[-1]
        while adj[v] and adj[v][-1][1] in used:
            adj[v].pop()
        if not adj[v]:
            walk.append(stack.pop())
        else:
            w, e = adj[v].pop()
            used.add(e)
            stack.append(w)
    if len(used) != eid:
        raise AssertionError("not connected")
    seen = set()
    tour = []
    for v in walk:
        if v not in seen:
            seen.add(v)
            tour.append(v)
    if len(tour) != n:
        raise AssertionError("missing vertices")
    return tour


def exact_check(lengths, verify_tour=True):
    n, paths, edges = instance(lengths)
    d = distances(n, edges)
    x = candidate_lp(lengths)
    lp_expected, tsp_expected = predicted(lengths)
    assert all(value > 0 for value in x.values())
    for v in range(n):
        assert sum((w for (a, b), w in x.items() if v in (a, b)), Fraction(0)) == 2, (lengths, v)
    min_cut = None
    for mask in range(1, 1 << (n - 1)):
        value = sum((w for (a, b), w in x.items() if bool(mask & (1 << a)) != bool(mask & (1 << b))), Fraction(0))
        if min_cut is None or value < min_cut:
            min_cut = value
        assert value >= 2, (lengths, mask, value)
    obj = sum((w * d[a][b] for (a, b), w in x.items()), Fraction(0))
    assert obj == lp_expected, (lengths, obj, lp_expected)
    e = eulerian_witness(lengths)
    assert set(e).issubset(edges)
    assert sum(e.values()) == tsp_expected, (lengths, sum(e.values()), tsp_expected)
    tour = shortcut_euler(n, e)
    tour_cost = sum(d[a][b] for a, b in zip(tour, tour[1:] + tour[:1]))
    assert tour_cost == tsp_expected, (lengths, tour_cost, tsp_expected)
    if verify_tour:
        @lru_cache(None)
        def dp(mask, last):
            if mask == 1 << (last - 1):
                return d[0][last]
            return min(dp(mask ^ (1 << (last - 1)), v) + d[v][last] for v in range(1, n) if v != last and mask & (1 << (v - 1)))
        best = min(dp((1 << (n - 1)) - 1, last) + d[last][0] for last in range(1, n))
        assert best == tsp_expected, (lengths, best, tsp_expected)
    return {"lengths": list(lengths), "n": n, "lp": str(obj), "tsp": tour_cost, "min_cut": str(min_cut), "support": len(x)}


def run(max_vertices=11, max_length=6, max_k=6):
    records = []
    for k in range(3, max_k + 1):
        for ab in product(range(2, max_length + 1), repeat=2):
            for rest in combinations_with_replacement(range(2, max_length + 1), k - 2):
                L = (*ab, *rest)
                if sum(L) - k + 2 > max_vertices:
                    continue
                records.append(exact_check(L))
    return {"instances": len(records), "max_vertices": max_vertices, "lp_half_cases": sum('.5' in r['lp'] or '/2' in r['lp'] for r in records), "sample": records[:5]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--max-vertices', type=int, default=11)
    p.add_argument('--max-length', type=int, default=6)
    p.add_argument('--max-k', type=int, default=6)
    p.add_argument('--json', action='store_true')
    args = p.parse_args()
    result = run(args.max_vertices, args.max_length, args.max_k)
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(result)

if __name__ == '__main__':
    main()
