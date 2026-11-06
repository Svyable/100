"""Exact independent-style replay of M097 separated-chord-network candidate.

No imports from other M097 checkers. All-cut rational primal and tour subset-DP
are separate algorithms. Historical novelty and specialist review not claimed.
"""
import argparse
import json
import random
from collections import deque
from fractions import Fraction
from itertools import combinations


def make_graph(lengths, chords):
    k = len(lengths)
    if k < 3 or any(L < 2 for L in lengths):
        raise ValueError("Need k>=3 and lengths>=2")
    paths, nxt = [], 2
    for L in lengths:
        paths.append([0] + list(range(nxt, nxt + L - 1)) + [1])
        nxt += L - 1
    marks = [set() for _ in paths]
    edges = {(0, 1)}
    def add(a, b):
        if a == b:
            raise ValueError("loops prohibited")
        edges.add(tuple(sorted((a, b))))
    for p in paths:
        for a, b in zip(p, p[1:]):
            add(a, b)
    for (i, a), (j, b) in chords:
        if (i, a) == (j, b):
            raise ValueError("loop chord")
        if not (0 <= i < k and 0 <= j < k):
            raise ValueError("path index")
        marks[i].add(a)
        marks[j].add(b)
        add(paths[i][a], paths[j][b])
    for i, p in enumerate(paths):
        s = sorted(marks[i])
        if any(a < 2 or a > len(p) - 3 for a in s):
            raise ValueError("mark too near a hub")
        if any(b - a < 2 for a, b in zip(s, s[1:])):
            raise ValueError("marks too close")
    if len(edges) != 1 + sum(lengths) + len(chords):
        raise ValueError("duplicate or pre-existing chord")
    return paths, edges, nxt


def distances(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    rows = []
    for s in range(n):
        d = [n + 1] * n
        d[s] = 0
        q = deque([s])
        while q:
            a = q.popleft()
            for b in adj[a]:
                if d[b] > d[a] + 1:
                    d[b] = d[a] + 1
                    q.append(b)
        if max(d) > n:
            raise AssertionError("disconnected graph")
        rows.append(d)
    return rows


def primal(paths):
    k = len(paths)
    alpha = Fraction(2, k)
    gamma = Fraction(k - 2, k * (k - 1))
    x = {}
    def add(a, b, w):
        key = tuple(sorted((a, b)))
        x[key] = x.get(key, Fraction(0)) + w
    for p in paths:
        add(p[0], p[1], alpha)
        add(p[-2], p[-1], alpha)
        for a, b in zip(p[1:-2], p[2:-1]):
            add(a, b, Fraction(1))
    for i, j in combinations(range(k), 2):
        add(paths[i][1], paths[j][1], gamma)
        add(paths[i][-2], paths[j][-2], gamma)
    return x


def tour_dp(d):
    n = len(d)
    old = {(1 << j, j): d[0][j + 1] for j in range(n - 1)}
    for _ in range(2, n):
        new = {}
        for (mask, j), val in old.items():
            for q in range(n - 1):
                if mask & (1 << q):
                    continue
                key = (mask | (1 << q), q)
                nv = val + d[j + 1][q + 1]
                if nv < new.get(key, 10**9):
                    new[key] = nv
        old = new
    return min(val + d[j + 1][0] for (mask, j), val in old.items())


def special_geodesic_pairs(d, special_edges):
    n = len(d)
    return {(a, b) for a, b in combinations(range(n), 2)
            if any(d[a][p] + 1 + d[q][b] == d[a][b] or
                   d[a][q] + 1 + d[p][b] == d[a][b]
                   for p, q in special_edges)}


def check(lengths, chords, tours=8, seed=1):
    paths, edges, n = make_graph(lengths, chords)
    d = distances(n, edges)
    x = primal(paths)
    m = sum(lengths)
    assert all(sum(w for (a, b), w in x.items() if v in (a, b)) == 2
               for v in range(n))
    assert sum(w * d[a][b] for (a, b), w in x.items()) == m
    mincut = Fraction(10**6)
    for mask in range(1, 1 << (n - 1)):
        cut = sum(w for (a, b), w in x.items()
                  if bool(mask & (1 << a)) != bool(mask & (1 << b)))
        assert cut >= 2, (lengths, chords, mask, cut)
        mincut = min(mincut, cut)
    expected = m + (len(paths) % 2) * min(1, min(lengths) - 2)
    optimum = tour_dp(d)
    assert optimum == expected, (lengths, chords, optimum, expected)
    base = {tuple(sorted((a, b))) for p in paths
            for a, b in zip(p, p[1:])}
    specials = edges - base
    B = special_geodesic_pairs(d, specials)
    assert not any(x.get(ab, 0) for ab in B), (lengths, chords, B)
    rng = random.Random(seed)
    for _ in range(tours):
        perm = [0] + rng.sample(range(1, n), n - 1)
        pairs = [tuple(sorted((perm[i], perm[(i + 1) % n])))
                 for i in range(n)]
        cost = sum(d[a][b] for a, b in pairs)
        mass = sum(ab in B for ab in pairs)
        assert mass <= cost - m, (lengths, chords, mass, cost - m)
    return dict(n=n, m=m, k=len(paths), chords=len(chords),
                sep=m, tsp=optimum, mincut=str(mincut),
                geodesic_pairs=len(B), support=len(x))


def fixed_cases():
    return [
        ((4, 4, 4), [((0, 2), (1, 2)), ((1, 2), (2, 2))]),
        ((4, 4, 4), [((0, 2), (1, 2)), ((1, 2), (2, 2)), ((0, 2), (2, 2))]),
        ((4, 4, 2), [((0, 2), (1, 2))]),
        ((4, 4, 2, 2), [((0, 2), (1, 2))]),
        ((6, 4, 3), [((0, 2), (0, 4)), ((0, 4), (1, 2))]),
        ((6, 4, 4), [((0, 2), (0, 4)), ((0, 4), (1, 2)), ((0, 2), (2, 2))]),
        ((6, 6, 3), [((0, 2), (1, 2)), ((0, 4), (1, 4))]),
        ((6, 6, 2), [((0, 2), (1, 2)), ((0, 4), (1, 4))]),
    ]


def random_cases(seed=20261102, attempts=90):
    rng = random.Random(seed)
    for _ in range(attempts):
        k = rng.choice([3, 4])
        while True:
            lengths = tuple(rng.randrange(2, 7) for _ in range(k))
            if 2 + sum(L - 1 for L in lengths) <= 12:
                break
        positions = []
        for i, L in enumerate(lengths):
            choices = list(range(2, L - 1))
            if len(choices) > 1:
                choices = rng.choice([choices[:1], choices[-1:], choices[::2]])
            positions.extend((i, p) for p in choices)
        possible = list(combinations(positions, 2))
        rng.shuffle(possible)
        marks = [set() for _ in lengths]
        chords = []
        for a, b in possible:
            if len(chords) >= rng.randrange(2, 5):
                break
            if all(abs(p - q) >= 2 for i, p in (a, b)
                   for q in marks[i] if q != p):
                chords.append((a, b))
                marks[a[0]].add(a[1])
                marks[b[0]].add(b[1])
        if chords:
            yield lengths, chords


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    fixed = [check(L, C) for L, C in fixed_cases()]
    random_records = [check(L, C, tours=2) for L, C in random_cases()]
    result = {"fixed": len(fixed), "seeded": len(random_records),
              "multi_chord": sum(r["chords"] >= 2 for r in fixed + random_records),
              "max_vertices": max(r["n"] for r in fixed + random_records),
              "sharp_two_chord_witness": fixed[0],
              "sharp_three_chord_witness": fixed[1]}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result)
    return result


if __name__ == "__main__":
    main()
