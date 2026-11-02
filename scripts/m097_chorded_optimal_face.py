"""Exact optimal-face and quantitative stability checks for chorded multitheta TSP.

Author-side arithmetic check, not independent mathematical or novelty acceptance.
Claim X-M097-CHORDED-MULTITHETA (#228).
"""
from collections import deque
from fractions import Fraction
from itertools import combinations, combinations_with_replacement
import argparse
import json


def graph(lengths):
    if len(lengths) < 2 or min(lengths) < 2:
        raise ValueError("at least two paths of length at least two required")
    paths = []
    edges = {(0, 1)}
    nxt = 2
    for length in lengths:
        vertices = [0] + list(range(nxt, nxt + length - 1)) + [1]
        nxt += length - 1
        paths.append(tuple(vertices))
        edges.update(tuple(sorted((a, b))) for a, b in zip(vertices, vertices[1:]))
    return nxt, edges, paths


def shortest(n, edges, start, end):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    for row in adj:
        row.sort()
    parent = {start: None}
    q = deque([start])
    while q:
        v = q.popleft()
        if v == end:
            break
        for w in adj[v]:
            if w not in parent:
                parent[w] = v
                q.append(w)
    if end not in parent:
        raise ValueError("disconnected")
    path = [end]
    while path[-1] != start:
        path.append(parent[path[-1]])
    return tuple(reversed(path))


def forbidden_and_routes(lengths):
    """Return all pairs having at least one geodesic through the direct chord.

    For each pair choose a shortest route through the chord when possible,
    otherwise an ordinary shortest route. Routes are literal vertex lists.
    """
    n, edges, paths = graph(lengths)
    without = edges - {(0, 1)}
    forbidden = set()
    routes = {}
    for a, b in combinations(range(n), 2):
        ordinary = shortest(n, edges, a, b)
        options = []
        for u, v in [(0, 1), (1, 0)]:
            first = shortest(n, without, a, u)
            last = shortest(n, without, v, b)
            candidate = first + (v,) + last[1:]
            if len(candidate) == len(ordinary):
                assert len(set(candidate)) == len(candidate), (lengths, a, b, candidate)
                options.append(candidate)
        if options:
            forbidden.add((a, b))
            routes[(a, b)] = options[0]
        else:
            routes[(a, b)] = ordinary
    return n, edges, paths, forbidden, routes


def optimal_point(lengths, paths):
    k = len(lengths)
    alpha = Fraction(2, k)
    gamma = Fraction(k - 2, k * (k - 1))
    x = {}
    def add(a, b, value):
        e = tuple(sorted((a, b)))
        x[e] = x.get(e, Fraction(0)) + value
    for path in paths:
        for i, (a, b) in enumerate(zip(path, path[1:])):
            add(a, b, alpha if i in (0, len(path) - 2) else Fraction(1))
    for i, j in combinations(range(k), 2):
        add(paths[i][1], paths[j][1], gamma)
        add(paths[i][-2], paths[j][-2], gamma)
    return x


def tour_point(n):
    # Deliberately includes the direct chord (0,1), testing nonoptimal slack.
    vertices = list(range(n))
    edges = [tuple(sorted((a, b))) for a, b in zip(vertices, vertices[1:] + vertices[:1])]
    return {e: Fraction(1) for e in edges}


def mixture(a, b, lam):
    return {e: lam * a.get(e, 0) + (1 - lam) * b.get(e, 0) for e in a.keys() | b.keys()}


def audit(lengths, x, check_feasible=True):
    n, edges, paths, forbidden, routes = forbidden_and_routes(lengths)
    if check_feasible:
        for v in range(n):
            assert sum(w for e, w in x.items() if v in e) == 2
        for mask in range(1, (1 << n) - 1):
            cut = sum(w for (a, b), w in x.items()
                      if bool(mask & (1 << a)) != bool(mask & (1 << b)))
            assert cut >= 2
    assert all(w >= 0 for w in x.values())
    y = {e: Fraction(0) for e in edges}
    for pair, weight in x.items():
        if weight == 0:
            continue
        for a, b in zip(routes[pair], routes[pair][1:]):
            y[tuple(sorted((a, b)))] += weight
    cost = sum(w * (len(routes[e]) - 1) for e, w in x.items())
    m = sum(lengths)
    eps = cost - m
    mass = sum(x.get(e, 0) for e in forbidden)
    assert eps >= 0 and mass <= y[(0, 1)] <= eps, (lengths, mass, y[(0, 1)], eps)
    for length, path in zip(lengths, paths):
        loads = [y[tuple(sorted((a, b)))] for a, b in zip(path, path[1:])]
        delta = sum(loads) - length
        assert delta >= 0
        for a, b in combinations(loads, 2):
            assert a + b >= 2
        if length >= 3:
            assert all(1 - delta / (length - 2) <= w <= 1 + delta for w in loads)
    return dict(cost=cost, slack=eps, forbidden_mass=mass, chord_load=y[(0, 1)],
                forbidden_count=len(forbidden))


def run(max_vertices=9):
    checked = 0
    nonoptimal = 0
    for k in range(2, 5):
        for lengths in combinations_with_replacement(range(2, 6), k):
            n = 2 + sum(v - 1 for v in lengths)
            if n > max_vertices:
                continue
            n, edges, paths = graph(lengths)
            x = optimal_point(lengths, paths)
            base = audit(lengths, x)
            assert base["cost"] == sum(lengths)
            assert base["forbidden_mass"] == base["chord_load"] == 0
            tour = tour_point(n)
            assert audit(lengths, tour)["slack"] >= 0
            assert audit(lengths, mixture(x, tour, Fraction(2, 5)))["slack"] >= 0
            checked += 1
            nonoptimal += 2
    return dict(optimal_instances=checked, perturbed_instances=nonoptimal)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-vertices", type=int, default=9)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run(args.max_vertices)
    print(json.dumps(result, sort_keys=True) if args.json else result)
