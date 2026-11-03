#!/usr/bin/env python3
"""M097: connected eight-vertex graph-metric Held--Karp census.

No third-party modules needed for exact winner verification.
--full needs networkx 3.6.1, numpy 2.3.5, scipy 1.17.0.
The exhaustive computation uses HiGHS to propose rational primal and dual
certificates, and checks their exact feasibility/equality independently.
It is NOT external mathematical review.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
import hashlib
import itertools
import json
import time

N = 8
EDGES = tuple(itertools.combinations(range(N), 2))
INDEX = {e: i for i, e in enumerate(EDGES)}
DEGREES = tuple(tuple(k for k, (u, v) in enumerate(EDGES)
                       if u == i or v == i) for i in range(N))
# One representative of every non-singleton cut and its complement.
CUTS = tuple(tuple(k for k, (u, v) in enumerate(EDGES)
                   if bool(mask & (1 << u)) != bool(mask & (1 << v)))
             for mask in range(1, 1 << N)
             if mask & 1 and mask.bit_count() not in (1, N-1, N))
EXPECTED = {
    "graphs": 11117,
    "max_ratio": "10/9",
    "ratio_histogram": {"1": 11055, "18/17": 44, "20/19": 16, "10/9": 2},
    "sha256": "0c45fd5d90681c36e45502c571b3d96daed62adaaa0826132aac3a88966d0d6f",
    "max_graph6": ["Gk_G" + chr(96) + "K", "Gk_GdK"],
}
WINNER_PRIMAL = {0:"1", 2:"1/2", 3:"1/2", 7:"1", 16:"1/2",
                 17:"1/2", 18:"1/2", 20:"1", 22:"1", 26:"1", 27:"1/2"}
WINNER_DEGREE_DUAL = {1:"1/2", 2:"1/2", 3:"1/2", 4:"1/2",
                      5:"1/2", 6:"1/2"}
WINNER_CUT_DUAL = {89:"1/2", 100:"1/2", 118:"1/2"}
WINNER_TOUR = [0, 7, 13, 20, 27, 26, 22, 3]


def dense(sparse, length):
    return [Fraction(sparse.get(i, 0)) for i in range(length)]


def check_lp(cost, primal, degree_dual, cut_dual):
    """Exact LP optimality via feasible primal, dual and equal objectives."""
    if (len(cost), len(primal), len(degree_dual), len(cut_dual)) != (
            len(EDGES), len(EDGES), N, len(CUTS)):
        raise ValueError("certificate dimensions")
    x = [Fraction(v) for v in primal]
    y = [Fraction(v) for v in degree_dual]
    z = [Fraction(v) for v in cut_dual]
    if any(v < 0 for v in x + z):
        raise ValueError("negative primal or dual cut variable")
    if any(sum(x[j] for j in row) != 2 for row in DEGREES):
        raise ValueError("degree equality")
    if any(sum(x[j] for j in row) < 2 for row in CUTS):
        raise ValueError("subtour inequality")
    reduced = [Fraction(c) - y[u] - y[v]
               for (u, v), c in zip(EDGES, cost)]
    for multiplier, cut in zip(z, CUTS):
        if multiplier:
            for j in cut:
                reduced[j] -= multiplier
    if any(r < 0 for r in reduced):
        raise ValueError("dual reduced cost")
    primal_value = sum(c * v for c, v in zip(cost, x))
    dual_value = 2 * (sum(y) + sum(z))
    if primal_value != dual_value:
        raise ValueError("primal-dual gap")
    return primal_value


def graph6_edges(g6):
    """Pure-Python graph6 decoder for eight vertices, independent of networkx."""
    if len(g6) != 6 or ord(g6[0]) - 63 != N:
        raise ValueError("graph6 length or order")
    bits = []
    for ch in g6[1:]:
        v = ord(ch) - 63
        if not 0 <= v < 64:
            raise ValueError("graph6 character")
        bits.extend((v >> shift) & 1 for shift in range(5, -1, -1))
    order = [(i, j) for j in range(1, N) for i in range(j)]
    if any(bits[len(order):]):
        raise ValueError("graph6 nonzero padding")
    return tuple(edge for bit, edge in zip(bits, order) if bit)


def graph_distances(g6):
    neighbors = [set() for _ in range(N)]
    for u, v in graph6_edges(g6):
        neighbors[u].add(v)
        neighbors[v].add(u)
    dist = [[N + 1] * N for _ in range(N)]
    for s in range(N):
        dist[s][s] = 0
        queue = [s]
        for u in queue:
            for v in neighbors[u]:
                if dist[s][v] > dist[s][u] + 1:
                    dist[s][v] = dist[s][u] + 1
                    queue.append(v)
        if any(d > N for d in dist[s]):
            raise ValueError("disconnected graph")
    return tuple(dist[u][v] for u, v in EDGES)


def independent_tsp(cost):
    """Held--Karp integer DP, not the tour matrix used in --full."""
    d = [[0] * N for _ in range(N)]
    for (u, v), c in zip(EDGES, cost):
        d[u][v] = d[v][u] = c
    @lru_cache(None)
    def dp(mask, last):
        if mask == (1 << N) - 1:
            return d[last][0]
        return min(d[last][j] + dp(mask | (1 << j), j)
                   for j in range(1, N) if not mask & (1 << j))
    return dp(1, 0)


def check_winners():
    assert len(CUTS) == 119
    for g6 in EXPECTED["max_graph6"]:
        cost = graph_distances(g6)
        hk = check_lp(cost, dense(WINNER_PRIMAL, len(EDGES)),
                      dense(WINNER_DEGREE_DUAL, N),
                      dense(WINNER_CUT_DUAL, len(CUTS)))
        tour = sum(cost[i] for i in WINNER_TOUR)
        assert tour == independent_tsp(cost) == 10
        assert hk == 9
        assert Fraction(tour, 1) / hk == Fraction(10, 9)
    return True


def all_tours():
    for tail in itertools.permutations(range(1, N)):
        if tail[0] < tail[-1]:
            vertices = (0,) + tail
            yield [INDEX[tuple(sorted((vertices[i], vertices[(i+1) % N])))]
                   for i in range(N)]


def full_census():
    """Rebuild all isomorphism classes, exact LP certificates and tour optima."""
    import networkx as nx
    import numpy as np
    from scipy.optimize import linprog
    parents = [g for g in nx.graph_atlas_g() if len(g) == 7]
    seen = defaultdict(list)
    tours = np.asarray(list(all_tours()), dtype=np.int16)
    tour_matrix = np.zeros((len(tours), len(EDGES)), dtype=np.int16)
    for i, tour in enumerate(tours):
        tour_matrix[i, tour] = 1
    degree_matrix = np.zeros((N, len(EDGES)))
    for i, row in enumerate(DEGREES):
        degree_matrix[i, list(row)] = 1
    cut_matrix = np.zeros((len(CUTS), len(EDGES)))
    for i, row in enumerate(CUTS):
        cut_matrix[i, list(row)] = -1
    digest = hashlib.sha256()
    hist = Counter()
    winners = []
    total = 0
    start = time.monotonic()
    for parent in parents:
        for neighborhood in range(128):
            graph = parent.copy()
            graph.add_node(7)
            for i in range(7):
                if neighborhood & (1 << i):
                    graph.add_edge(i, 7)
            if not nx.is_connected(graph):
                continue
            key = (graph.number_of_edges(),
                   nx.weisfeiler_lehman_graph_hash(graph, iterations=3))
            if any(nx.is_isomorphic(graph, old) for old in seen[key]):
                continue
            seen[key].append(graph)
            g6 = nx.to_graph6_bytes(graph, header=False).decode().strip()
            cost = graph_distances(g6)
            assert cost == tuple(dict(nx.all_pairs_shortest_path_length(graph))[u][v]
                                 for u, v in EDGES)
            result = linprog(np.array(cost, dtype=float),
                             A_ub=cut_matrix, b_ub=np.full(len(CUTS), -2.),
                             A_eq=degree_matrix, b_eq=np.full(N, 2.),
                             bounds=(0, None), method="highs")
            if not result.success:
                raise RuntimeError((total, result.message))
            rational = lambda seq: [Fraction(float(x)).limit_denominator(100000)
                                    for x in seq]
            hk = check_lp(cost, rational(result.x),
                          rational(result.eqlin.marginals),
                          rational(-result.ineqlin.marginals))
            costs = tour_matrix @ np.array(cost, dtype=np.int16)
            tsp = int(costs.min())
            assert tsp == sum(cost[j] for j in tours[int(costs.argmin())])
            ratio = str(Fraction(tsp) / hk)
            if ratio != "1":
                # Separate interior-point LP path and integer DP on every
                # fractional-gap case (62 in the pinned eight-vertex census).
                alt = linprog(np.array(cost, dtype=float),
                              A_ub=cut_matrix, b_ub=np.full(len(CUTS), -2.),
                              A_eq=degree_matrix, b_eq=np.full(N, 2.),
                              bounds=(0, None), method="highs-ipm")
                if not alt.success:
                    raise RuntimeError((total, alt.message, "IPM"))
                assert check_lp(cost, rational(alt.x),
                                rational(alt.eqlin.marginals),
                                rational(-alt.ineqlin.marginals)) == hk
                assert independent_tsp(cost) == tsp
            hist[ratio] += 1
            digest.update((g6 + "\t" + str(tsp) + "\t" + str(hk) + "\n").encode())
            if ratio == EXPECTED["max_ratio"]:
                winners.append(g6)
            total += 1
    outcome = {"graphs": total, "max_ratio": str(max(map(Fraction, hist))),
               "ratio_histogram": dict(hist), "sha256": digest.hexdigest(),
               "max_graph6": winners}
    if outcome != EXPECTED:
        raise AssertionError("full census differs: " + json.dumps(outcome))
    return {"result": outcome, "seconds": round(time.monotonic() - start, 2)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="stdlib-only exact verification of both maximizers")
    parser.add_argument("--full", action="store_true",
                        help="optional dependencies: rerun all 11,117 cases")
    args = parser.parse_args()
    if not args.check and not args.full:
        parser.error("specify --check or --full")
    check_winners()
    if args.full:
        print(json.dumps(full_census(), sort_keys=True))
    else:
        print("two graph6 witnesses: HK=9, optimal TSP=10, ratio=10/9")
