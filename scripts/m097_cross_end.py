"""Exact checks for a two-hub graph with one cross-end edge.

Claim X-M097-CROSS-END (#232). The checker is author-produced, not
independent mathematical review. All arithmetic in LP witnesses is rational.
"""
from collections import deque
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
import argparse
import json


def graph(lengths, cross="end"):
    if len(lengths) < 3 or min(lengths) < 2:
        raise ValueError("need k>=3 and every length>=2")
    n, paths, edges = 2, [], {(0, 1)}
    for length in lengths:
        p = [0] + list(range(n, n + length - 1)) + [1]
        n += length - 1
        paths.append(p)
        edges.update(tuple(sorted(pair)) for pair in zip(p, p[1:]))
    b = paths[1][-2] if cross == "end" else paths[1][1]
    edges.add(tuple(sorted((paths[0][1], b))))
    return n, frozenset(edges), paths


def recombined_paths(paths):
    # P2 from u to its last internal vertex; cross to P1's first
    # internal vertex; P1 from that vertex to v.
    return [paths[1][:-1] + paths[0][1:]] + paths[2:]


def distances(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    result = []
    for root in range(n):
        d = [-1] * n
        d[root] = 0
        q = deque([root])
        while q:
            a = q.popleft()
            for b in adj[a]:
                if d[b] < 0:
                    d[b] = d[a] + 1
                    q.append(b)
        assert all(v >= 0 for v in d)
        result.append(d)
    return result


def fractional_witness(paths):
    qs = recombined_paths(paths)
    r = len(qs)
    alpha = Fraction(2, r)
    gamma = Fraction(r - 2, r * (r - 1))
    x = {}
    def add(a, b, value):
        key = tuple(sorted((a, b)))
        x[key] = x.get(key, Fraction(0)) + value
    for q in qs:
        for i, (a, b) in enumerate(zip(q, q[1:])):
            add(a, b, alpha if i in (0, len(q) - 2) else Fraction(1))
    for i, j in combinations(range(r), 2):
        add(qs[i][1], qs[j][1], gamma)
        add(qs[i][-2], qs[j][-2], gamma)
    return {e: w for e, w in x.items() if w}


def expected(lengths):
    m = sum(lengths)
    return (m - 1, m - 1 + int(len(lengths) % 2 == 0 and min(lengths) >= 3))


def check_witness(lengths, full_cuts=True):
    n, edges, paths = graph(lengths)
    x = fractional_witness(paths)
    d = distances(n, edges)
    assert all(w >= 0 for w in x.values())
    for v in range(n):
        assert sum(w for (a, b), w in x.items() if v in (a, b)) == 2
    cost = sum(w * d[a][b] for (a, b), w in x.items())
    assert cost == sum(lengths) - 1, (lengths, cost)
    if full_cuts:
        for mask in range(1, (1 << n) - 1):
            crossing = sum(w for (a, b), w in x.items()
                           if bool(mask & (1 << a)) != bool(mask & (1 << b)))
            assert crossing >= 2, (lengths, mask, crossing)
    return cost


def eulerian_witness(lengths):
    n, edges, paths = graph(lengths)
    qs = recombined_paths(paths)
    y = {}
    def add(a, b, weight):
        key = tuple(sorted((a, b)))
        y[key] = y.get(key, 0) + weight
        if y[key] == 0:
            del y[key]
    for q in qs:
        for a, b in zip(q, q[1:]):
            add(a, b, 1)
    if len(lengths) % 2 == 0:
        if min(lengths) >= 3:
            add(0, 1, 1)
        else:
            # Convert one u-v component into a same-hub excursion,
            # at no cost when it contains a length-two path.
            i = lengths.index(2)
            if i >= 2:
                z = paths[i][1]
                add(0, z, 1)
                add(z, 1, -1)
            elif i == 0:
                x = paths[0][1]
                add(x, 1, -1)
                add(0, x, 1)
            else:
                z = paths[1][1]
                add(0, z, -1)
                add(z, 1, 1)
    assert set(y).issubset(edges)
    assert all(w > 0 for w in y.values())
    deg = [0] * n
    adj = [[] for _ in range(n)]
    for (a, b), w in y.items():
        deg[a] += w
        deg[b] += w
        adj[a].append(b)
        adj[b].append(a)
    assert all(v >= 2 and v % 2 == 0 for v in deg), (lengths, deg)
    seen = {0}
    q = deque([0])
    while q:
        for v in adj[q.popleft()]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    assert len(seen) == n
    assert sum(y.values()) == expected(lengths)[1]
    return y


def tour_dp(lengths, cross="end"):
    n, edges, _ = graph(lengths, cross=cross)
    d = distances(n, edges)
    @lru_cache(None)
    def visit(mask, last):
        if mask == 1 << (last - 1):
            return d[0][last]
        rest = mask ^ (1 << (last - 1))
        return min(visit(rest, prev) + d[prev][last]
                   for prev in range(1, n) if rest & (1 << (prev - 1)))
    mask = (1 << (n - 1)) - 1
    return min(visit(mask, last) + d[last][0] for last in range(1, n))


def run(max_vertices=11, max_k=5):
    count = 0
    types = {"odd": 0, "even_short": 0, "even_long": 0}
    for k in range(3, max_k + 1):
        for lengths in product(range(2, 6), repeat=k):
            n = 2 + sum(L - 1 for L in lengths)
            if n > max_vertices:
                continue
            assert check_witness(lengths) == expected(lengths)[0]
            assert tour_dp(lengths) == expected(lengths)[1]
            eulerian_witness(lengths)
            kind = "odd" if k % 2 else ("even_short" if min(lengths) == 2 else "even_long")
            types[kind] += 1
            count += 1
    return {"instances": count, "types": types}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--max-vertices", type=int, default=11)
    p.add_argument("--max-k", type=int, default=5)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    result = run(a.max_vertices, a.max_k)
    print(json.dumps(result, sort_keys=True) if a.json else result)
