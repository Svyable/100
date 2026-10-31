"""M097 - Metric TSP 4/3 conjecture on every graphic metric with n <= N vertices.

For each connected graph G (from the graph census) the instance is its
shortest-path metric. Search side: exact Held-Karp (subtour) LP by cutting
planes over the rational simplex, and the optimal tour by Held-Karp DP.
Check side: LP optimality is re-proved from the duality certificate against
*every* subtour constraint, and the tour optimum is recomputed by brute force
over all Hamiltonian cycles. The conjectured bound is OPT <= (4/3) * HK.
"""
from fractions import Fraction
from itertools import combinations, permutations

from . import exact_lp
from .core import digest, fraction_text, require
from .graphs import census, to_adjacency

PROBE = {
    "id": "held_karp",
    "problem_id": "M097",
    "title": "Held-Karp integrality gap on all graphic metrics up to N vertices",
    "engines": ["exact_lp", "graph_census"],
    "frontier": ("Known: the integrality gap is at least 4/3 and at most 3/2 (Wolsey; Shmoys-Williamson); "
                 "exact maximum gaps have been computed for all metrics on small n (Benoit-Boyd 2008)."),
    "levels": {"smoke": {"max_n": 6}, "deep": {"max_n": 7}},
}


def scope(params):
    return (f"For the shortest-path metric of every connected graph on 3..{params['max_n']} vertices, "
            "OPT <= (4/3) * HK with both values certified exactly.")


def metric(n, adj):
    INF = 10 ** 9
    d = [[0 if i == j else (1 if adj[i] >> j & 1 else INF) for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return d


def connected(n, adj):
    seen, stack = 1, [0]
    while stack:
        v = stack.pop()
        new = adj[v] & ~seen
        seen |= new
        stack += [u for u in range(n) if new >> u & 1]
    return seen == (1 << n) - 1


def edges_of(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def cut_row(n, S):
    return [1 if ((i in S) != (j in S)) else 0 for i, j in edges_of(n)]


def held_karp_lp(n, d):
    E = edges_of(n)
    c = [d[i][j] for i, j in E]
    A_eq = [[1 if v in e else 0 for e in E] for v in range(n)]
    b_eq = [2] * n
    cuts = []
    candidates = [frozenset(S) for k in range(2, n - 1) for S in combinations(range(1, n), k)]
    while True:
        value, x, y, z = exact_lp.solve(c, A_eq, b_eq, [cut_row(n, S) for S in cuts], [2] * len(cuts))
        worst, cut = None, None
        for S in candidates:
            load = sum(xe for xe, (i, j) in zip(x, E) if (i in S) != (j in S))
            if load < 2 and (worst is None or load < worst):
                worst, cut = load, S
        if cut is None:
            return value, x, y, z, cuts
        cuts.append(cut)


def tour_dp(n, d):
    """Held-Karp dynamic programme for the optimal tour starting at vertex 0."""
    full = 1 << n
    best = {(1, 0): (0, None)}
    for mask in range(1, full):
        if not mask & 1:
            continue
        for last in range(n):
            if (mask, last) not in best:
                continue
            cost = best[(mask, last)][0]
            for nxt in range(n):
                if not mask >> nxt & 1:
                    key = (mask | 1 << nxt, nxt)
                    if key not in best or cost + d[last][nxt] < best[key][0]:
                        best[key] = (cost + d[last][nxt], last)
    end = min(range(1, n), key=lambda v: (best[(full - 1, v)][0] + d[v][0], v))
    total = best[(full - 1, end)][0] + d[end][0]
    tour, mask, v = [], full - 1, end
    while v is not None:
        tour.append(v)
        prev = best[(mask, v)][1]
        mask &= ~(1 << v)
        v = prev
    return total, tour[::-1]


def search(params):
    rows, worst = [], None
    for n in range(3, params["max_n"] + 1):
        for code in census(n):
            adj = to_adjacency(n, code)
            if not connected(n, adj):
                continue
            d = metric(n, adj)
            hk, x, y, z, cuts = held_karp_lp(n, d)
            opt, tour = tour_dp(n, d)
            ratio = Fraction(opt) / hk
            rows.append({"n": n, "graph": code, "hk": fraction_text(hk), "opt": opt, "tour": tour,
                         "x": [fraction_text(v) for v in x], "y": [fraction_text(v) for v in y],
                         "cuts": [sorted(S) for S in cuts], "z": [fraction_text(v) for v in z]})
            if worst is None or ratio > worst[0]:
                worst = (ratio, n, code)
    return {
        "holds": worst[0] <= Fraction(4, 3),
        "summary": {"instances": len(rows), "max_ratio": fraction_text(worst[0]),
                    "max_ratio_instance": {"n": worst[1], "graph": worst[2]},
                    "certificate_sha256": digest(rows)},
        "certificate": rows,
    }


def check(params, result):
    rows = result["certificate"]
    expected = {(n, code) for n in range(3, params["max_n"] + 1) for code in census(n)
                if connected(n, to_adjacency(n, code))}
    require({(r["n"], r["graph"]) for r in rows} == expected and len(rows) == len(expected),
            "instances must be exactly the connected graphs of the census")
    worst = Fraction(0)
    for r in rows:
        n = r["n"]
        adj = to_adjacency(n, r["graph"])
        # independent metric: breadth-first search from every vertex
        d = []
        for s in range(n):
            dist, frontier, k = {s: 0}, [s], 0
            while frontier:
                k += 1
                nxt = [u for v in frontier for u in range(n) if adj[v] >> u & 1 and u not in dist]
                for u in nxt:
                    dist.setdefault(u, k)
                frontier = [u for u in set(nxt)]
            d.append([dist[t] for t in range(n)])
        E = edges_of(n)
        c = [d[i][j] for i, j in E]
        every_cut = [frozenset(S) for k in range(2, n - 1) for S in combinations(range(1, n), k)]
        A_eq = [[1 if v in e else 0 for e in E] for v in range(n)]
        # primal must satisfy every subtour constraint, dual is supported on the listed cuts
        A_ge = [cut_row(n, S) for S in every_cut]
        zfull = [Fraction(0)] * len(every_cut)
        index = {S: k for k, S in enumerate(every_cut)}
        for S, zs in zip(r["cuts"], r["z"]):
            zfull[index[frozenset(S)]] += Fraction(zs)
        try:
            hk = exact_lp.certify(c, A_eq, [2] * n, A_ge, [2] * len(A_ge),
                                  [Fraction(v) for v in r["x"]], [Fraction(v) for v in r["y"]], zfull)
        except ValueError as exc:
            require(False, f"n={n} graph {r['graph']}: LP certificate invalid ({exc})")
        require(fraction_text(hk) == r["hk"], "recorded HK value differs from certified optimum")
        tour = r["tour"]
        require(sorted(tour) == list(range(n)), "tour must visit every vertex once")
        length = sum(d[tour[i]][tour[(i + 1) % n]] for i in range(n))
        brute = min(d[0][p[0]] + sum(d[p[i]][p[i + 1]] for i in range(n - 2)) + d[p[-1]][0]
                    for p in permutations(range(1, n)))
        require(length == r["opt"] == brute, f"n={n} graph {r['graph']}: tour is not optimal")
        ratio = Fraction(r["opt"]) / hk
        require(ratio <= Fraction(4, 3) or not result["holds"], "4/3 bound violated")
        worst = max(worst, ratio)
    require(fraction_text(worst) == result["summary"]["max_ratio"], "summary ratio mismatch")
    require(result["summary"]["certificate_sha256"] == digest(rows), "certificate hash mismatch")
