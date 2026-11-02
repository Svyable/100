#!/usr/bin/env python3
"""M097: exact metric TSP and subtour-LP certificates on block trees.

Author-side executable checks for claim #189; not independent mathematical review.
Only standard library; all LP witnesses and dual cut covers use Fractions.
"""
import argparse
from collections import deque
from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import combinations, permutations
from functools import lru_cache
import json


def edge(a, b):
    if a == b:
        raise ValueError("loops forbidden")
    return (min(a, b), max(a, b))


@dataclass
class Graph:
    n: int
    edges: set
    x: dict
    blocks: list


def block(kind, lengths):
    """An isolated block: bridge, cycle, or subdivided k-path dipole."""
    if kind == "bridge":
        n, edges, paths = 2, {edge(0, 1)}, []
        x = {edge(0, 1): Q(2)}
        expected_lp, expected_tsp = 2, 2
    elif kind == "cycle":
        L = lengths[0]
        if len(lengths) != 1 or L < 3:
            raise ValueError("cycle length >=3")
        n = L
        edges = {edge(i, (i + 1) % L) for i in range(L)}
        paths = []
        x = {e: Q(1) for e in edges}
        expected_lp = expected_tsp = L
    elif kind == "theta":
        k = len(lengths)
        if k < 2 or any(type(L) is not int or L < 2 for L in lengths):
            raise ValueError("k>=2 and all lengths>=2")
        n, edges, paths, x = 2, set(), [], {}
        near0, near1 = [], []
        for L in lengths:
            p = [0] + list(range(n, n + L - 1)) + [1]
            n += L - 1
            paths.append(p)
            near0.append(p[1])
            near1.append(p[-2])
            for a, b in zip(p, p[1:]):
                e = edge(a, b)
                edges.add(e)
                x[e] = Q(2, k) if a in (0, 1) or b in (0, 1) else Q(1)
        gamma = Q(k - 2, k * (k - 1))
        for near in (near0, near1):
            for a, b in combinations(near, 2):
                e = edge(a, b)
                x[e] = x.get(e, Q(0)) + gamma
        expected_lp = sum(lengths)
        expected_tsp = expected_lp + (k % 2) * (min(lengths) - 2)
    else:
        raise ValueError("unknown block")
    record = {"kind": kind, "lengths": tuple(lengths), "edges": set(edges),
              "paths": paths, "vertices": tuple(range(n)),
              "lp": expected_lp, "tsp": expected_tsp}
    return Graph(n, edges, x, [record])


def glue(g, h, v, w):
    """Glue at exactly one vertex, splitting one unit of incident LP mass."""
    if not 0 <= v < g.n or not 0 <= w < h.n:
        raise ValueError("bad articulation vertex")
    # The vertex sets are disjoint before the prescribed identification.
    mapping = {w: v}
    next_id = g.n
    for a in range(h.n):
        if a != w:
            mapping[a] = next_id
            next_id += 1
    he = {edge(mapping[a], mapping[b]) for a, b in h.edges}
    hx = {edge(mapping[a], mapping[b]): z for (a, b), z in h.x.items()}
    if g.edges & he:
        raise ValueError("overlapping blocks")
    gx = dict(g.x)
    # Existing and new blocks each have exactly degree 2 at the shared vertex.
    old = {b if a == v else a: z for (a, b), z in gx.items() if v in (a, b)}
    new = {b if a == v else a: z for (a, b), z in hx.items() if v in (a, b)}
    if sum(old.values(), Q(0)) != 2 or sum(new.values(), Q(0)) != 2:
        raise AssertionError("invalid block degree at articulation")
    for a, z in old.items():
        gx[edge(v, a)] -= z / 2
    for b, z in new.items():
        hx[edge(v, b)] -= z / 2
    for e, z in hx.items():
        gx[e] = gx.get(e, Q(0)) + z
    for a, za in old.items():
        for b, zb in new.items():
            e = edge(a, b)
            gx[e] = gx.get(e, Q(0)) + za * zb / 4
    gx = {e: z for e, z in gx.items() if z}
    mapped_blocks = []
    for B in h.blocks:
        mapped_blocks.append({
            **B,
            "edges": {edge(mapping[a], mapping[b]) for a, b in B["edges"]},
            "paths": [[mapping[a] for a in p] for p in B["paths"]],
            "vertices": tuple(mapping[a] for a in B["vertices"]),
        })
    return Graph(next_id, g.edges | he, gx, g.blocks + mapped_blocks)


def metric(g):
    adj = [[] for _ in range(g.n)]
    for a, b in g.edges:
        adj[a].append(b)
        adj[b].append(a)
    out = []
    for s in range(g.n):
        dist = [-1] * g.n
        dist[s] = 0
        q = deque([s])
        while q:
            a = q.popleft()
            for b in adj[a]:
                if dist[b] < 0:
                    dist[b] = dist[a] + 1
                    q.append(b)
        if -1 in dist:
            raise AssertionError("disconnected")
        out.append(dist)
    return out


def component_after_removal(g, removed, root):
    adj = [[] for _ in range(g.n)]
    for a, b in g.edges - removed:
        adj[a].append(b)
        adj[b].append(a)
    seen = {root}
    todo = [root]
    for a in todo:
        for b in adj[a]:
            if b not in seen:
                seen.add(b)
                todo.append(b)
    return frozenset(seen)


def cut_edges(g, side):
    return {e for e in g.edges if (e[0] in side) != (e[1] in side)}


def dual_cut_cover(g):
    """Explicit nonnegative graph-cut dual: coefficient exactly one per edge."""
    cuts = []
    for B in g.blocks:
        if B["kind"] == "bridge":
            e = next(iter(B["edges"]))
            side = component_after_removal(g, {e}, e[0])
            cuts.append((side, Q(1), {e}))
        elif B["kind"] == "cycle":
            for v in B["vertices"]:
                adjacent = {e for e in B["edges"] if v in e}
                side = component_after_removal(g, adjacent, v)
                cuts.append((side, Q(1, 2), adjacent))
        else:
            for path in B["paths"]:
                L = len(path) - 1
                for i, j in combinations(range(L), 2):
                    pair = {edge(path[i], path[i + 1]),
                            edge(path[j], path[j + 1])}
                    side = component_after_removal(g, pair, path[i + 1])
                    cuts.append((side, Q(1, L - 1), pair))
    coefficients = {e: Q(0) for e in g.edges}
    for side, weight, expected in cuts:
        if not side or len(side) == g.n or cut_edges(g, side) != expected:
            raise AssertionError(("invalid cut boundary", side, expected))
        for e in expected:
            coefficients[e] += weight
    if any(z != 1 for z in coefficients.values()):
        raise AssertionError(("dual edge coverage", coefficients))
    return 2 * sum((z for _, z, _ in cuts), Q(0)), len(cuts)


def check_primal(g):
    if any(z < 0 or e[0] >= e[1] or e[0] < 0 or e[1] >= g.n
           for e, z in g.x.items()):
        raise AssertionError("invalid primal edge or coefficient")
    for v in range(g.n):
        if sum((z for e, z in g.x.items() if v in e), Q(0)) != 2:
            raise AssertionError(("degree", v))
    for mask in range(1, 1 << (g.n - 1)):
        side = {v for v in range(g.n) if mask & (1 << v)}
        crossing = sum((z for e, z in g.x.items()
                        if (e[0] in side) != (e[1] in side)), Q(0))
        if crossing < 2:
            raise AssertionError(("subtour", mask, crossing))
    d = metric(g)
    return sum((z * d[a][b] for (a, b), z in g.x.items()), Q(0))


def tsp_independent(d):
    """Iterative Held-Karp DP; does not inspect block structure or LP point."""
    n = len(d)
    if n == 2:
        return 2 * d[0][1]
    current = {(1 << j, j): d[0][j] for j in range(1, n)}
    for _ in range(2, n):
        following = {}
        for (mask, last), value in current.items():
            for j in range(1, n):
                if not mask & (1 << j):
                    key = (mask | (1 << j), j)
                    cost = value + d[last][j]
                    following[key] = min(following.get(key, cost), cost)
        current = following
    return min(v + d[last][0] for (mask, last), v in current.items())


def check_instance(g, tour=True):
    lower, cuts = dual_cut_cover(g)
    upper = check_primal(g)
    expected_lp = sum(B["lp"] for B in g.blocks)
    expected_tsp = sum(B["tsp"] for B in g.blocks)
    if lower != expected_lp or upper != expected_lp:
        raise AssertionError(("LP formula", lower, upper, expected_lp))
    if tour and tsp_independent(metric(g)) != expected_tsp:
        raise AssertionError(("TSP formula", g.n, expected_tsp))
    return {"n": g.n, "blocks": len(g.blocks), "cuts": cuts,
            "lp": str(upper), "tsp": expected_tsp,
            "ratio": str(Q(expected_tsp, expected_lp))}


def fixtures():
    # Trees of distinct blocks, glued at hub and at internal vertices.
    theta = block("theta", (3, 3, 3))
    yield "theta", theta
    yield "theta_leaf", glue(theta, block("bridge", ()), 0, 0)
    yield "theta_internal_leaf", glue(theta, block("bridge", ()), 2, 0)
    yield "theta_triangle", glue(theta, block("cycle", (3,)), 2, 0)
    yield "theta_square", glue(theta, block("cycle", (4,)), 1, 0)
    yield "cycle_tree", glue(glue(block("cycle", (3,)),
                                   block("cycle", (4,)), 1, 0),
                              block("bridge", ()), 4, 0)
    yield "even_theta_leaf", glue(block("theta", (2, 3, 2, 3)),
                                   block("bridge", ()), 0, 0)
    yield "theta_two", glue(block("theta", (2, 3, 3)),
                             block("theta", (2, 2, 3)), 2, 0)
    yield "two_odd_thetas", glue(block("theta", (3, 3, 3)),
                                  block("theta", (3, 3, 3)), 2, 0)


def check():
    results = {}
    for name, g in fixtures():
        results[name] = check_instance(g, tour=True)
    # Negative controls: corruption of primal and dual must be rejected.
    g = glue(block("theta", (3, 3, 3)), block("bridge", ()), 0, 0)
    bad = Graph(g.n, g.edges, dict(g.x), g.blocks)
    e = next(iter(bad.x))
    bad.x[e] += Q(1, 7)
    try:
        check_primal(bad)
        raise AssertionError("tampered primal accepted")
    except AssertionError as exc:
        if str(exc) == "tampered primal accepted":
            raise
    # A graph with a bridge has LP bridge cost 2, not 1.
    assert dual_cut_cover(g)[0] == 11
    assert tsp_independent(metric(g)) == 12
    assert check_instance(block("cycle", (3,)))["lp"] == "3"
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("pass --check")
    result = check()
    print(json.dumps(result if args.json else {
        "cases": len(result), "max_vertices": max(x["n"] for x in result.values()),
        "fractional": sum(Q(x["ratio"]) > 1 for x in result.values()),
        "largest_ratio": str(max(Q(x["ratio"]) for x in result.values())),
    }, sort_keys=True))
