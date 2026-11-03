#!/usr/bin/env python3
"""M097: exact graphic TSP on arbitrarily weighted full subdivisions.

Every core edge is replaced by an internally disjoint path with >=2 strictly
positive rational-weight edges. Independent exact Hamiltonian DP is a falsifier;
the all-orders theorem is proved in research/M097_WEIGHTED_SUBDIVISION.md.
"""
import argparse
import json
from fractions import Fraction
from itertools import combinations, combinations_with_replacement
from random import Random


def validate(n, paths):
    if not isinstance(n, int) or n < 2 or not paths:
        raise ValueError("connected core with at least two vertices required")
    normalized = []
    adj = [[] for _ in range(n)]
    for idx, (u, v, weights) in enumerate(paths):
        if not (isinstance(u, int) and isinstance(v, int)
                and 0 <= u < n and 0 <= v < n and u != v):
            raise ValueError("loops and invalid core endpoints forbidden")
        if len(weights) < 2:
            raise ValueError("each core edge must be subdivided at least once")
        ws = tuple(Fraction(w) for w in weights)
        if any(w <= 0 for w in ws):
            raise ValueError("all path-edge weights must be strictly positive")
        normalized.append((u, v, ws))
        adj[u].append(v)
        adj[v].append(u)
    seen, stack = {0}, [0]
    while stack:
        for v in adj[stack.pop()]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    if len(seen) != n:
        raise ValueError("core must be connected")
    return normalized


def cycle_basis(n, paths):
    """Fundamental even edge subsets; parallel core edges are individually indexed."""
    par = list(range(n))
    tree = [[] for _ in range(n)]
    chords = []

    def find(x):
        while par[x] != x:
            x = par[x]
        return x

    for i, (u, v, _) in enumerate(paths):
        a, b = find(u), find(v)
        if a == b:
            chords.append((i, u, v))
        else:
            par[a] = b
            tree[u].append((v, i))
            tree[v].append((u, i))
    basis = []
    for chord_idx, u, target in chords:
        todo = [u]
        parent = {u: (-1, -1)}
        for v in todo:
            if v == target:
                break
            for w, idx in tree[v]:
                if w not in parent:
                    parent[w] = (v, idx)
                    todo.append(w)
        if target not in parent:
            raise AssertionError("spanning tree lost connectivity")
        mask = 1 << chord_idx
        v = target
        while v != u:
            prev, idx = parent[v]
            mask ^= 1 << idx
            v = prev
        basis.append(mask)
    assert len(basis) == len(paths) - n + 1
    return basis


def _mst_connection(n, paths, fmask, max_weights):
    parent = list(range(n))
    components = n

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    def unite(u, v):
        nonlocal components
        a, b = find(u), find(v)
        if a == b:
            return False
        parent[a] = b
        components -= 1
        return True

    for i, (u, v, _) in enumerate(paths):
        if (fmask >> i) & 1:
            unite(u, v)
    chosen = []
    total = Fraction(0)
    for i in sorted(range(len(paths)), key=lambda j: (max_weights[j], j)):
        if not ((fmask >> i) & 1):
            u, v, _ = paths[i]
            if unite(u, v):
                chosen.append(i)
                total += max_weights[i]
    assert components == 1
    return total, tuple(chosen)


def exact_core_tsp(n, raw_paths):
    """All-orders weighted parity/MST formula; 2^(m-n+1) core states."""
    paths = validate(n, raw_paths)
    W = [sum(ws) for _, _, ws in paths]
    a = [max(ws) for _, _, ws in paths]
    M = sum(W)
    basis = cycle_basis(n, paths)
    best = None
    for state in range(1 << len(basis)):
        fmask = 0
        for j, b in enumerate(basis):
            if (state >> j) & 1:
                fmask ^= b
        mst, through = _mst_connection(n, paths, fmask, a)
        cost = M + sum(W[e] - 2 * a[e] for e in range(len(paths))
                       if not (fmask >> e) & 1) + 2 * mst
        candidate = (cost, fmask, through)
        if best is None or candidate < best:
            best = candidate
    return dict(cost=best[0], even_mask=best[1], through=best[2],
                core_states=1 << len(basis), path_totals=tuple(W),
                maxima=tuple(a))


def expand(n, raw_paths):
    paths = validate(n, raw_paths)
    edges, indices = [], []
    vertices = n
    for i, (u, v, ws) in enumerate(paths):
        prev, ids = u, []
        for j, w in enumerate(ws):
            nxt = v if j == len(ws) - 1 else vertices
            if nxt == vertices:
                vertices += 1
            ids.append(len(edges))
            edges.append((prev, nxt, w))
            prev = nxt
        indices.append(tuple(ids))
    return vertices, tuple(edges), tuple(indices)


def certificate(n, raw_paths, plan):
    """Construct an actual Eulerian spanning walk achieving the parity formula."""
    vertices, edges, indices = expand(n, raw_paths)
    paths = validate(n, raw_paths)
    through = set(plan["through"])
    copies = [0] * len(edges)
    for e, ids in enumerate(indices):
        if (plan["even_mask"] >> e) & 1:
            for idx in ids:
                copies[idx] = 1
        elif e in through:
            for idx in ids:
                copies[idx] = 2
        else:
            ws = paths[e][2]
            omit = ws.index(max(ws))
            for j, idx in enumerate(ids):
                copies[idx] = 0 if j == omit else 2
    incidence = [[] for _ in range(vertices)]
    count = 0
    for (u, v, _), mult in zip(edges, copies):
        for _ in range(mult):
            incidence[u].append((v, count))
            incidence[v].append((u, count))
            count += 1
    if any(len(adj) % 2 for adj in incidence):
        raise AssertionError("Eulerian parity violation")
    if any(not adj for adj in incidence):
        raise AssertionError("spanning violation")
    seen, todo = {0}, [0]
    while todo:
        for v, _ in incidence[todo.pop()]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    if len(seen) != vertices:
        raise AssertionError("disconnected certificate")
    used, walk_stack, walk = set(), [0], []
    positions = [0] * vertices
    while walk_stack:
        u = walk_stack[-1]
        while positions[u] < len(incidence[u]) and incidence[u][positions[u]][1] in used:
            positions[u] += 1
        if positions[u] == len(incidence[u]):
            walk.append(walk_stack.pop())
        else:
            v, i = incidence[u][positions[u]]
            used.add(i)
            walk_stack.append(v)
    walk.reverse()
    if len(used) != count or len(walk) != count + 1 or walk[0] != walk[-1]:
        raise AssertionError("Eulerian walk incomplete")
    weight = sum(mult * w for (_, _, w), mult in zip(edges, copies))
    if weight != plan["cost"]:
        raise AssertionError("wrong certificate cost")
    return dict(weight=weight, walk=tuple(walk), edge_copies=tuple(copies),
                distinct_vertices=len(set(walk)))


def metric_closure(n, edges):
    d = [[Fraction(0) if i == j else None for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        w = Fraction(w)
        if d[u][v] is None or w < d[u][v]:
            d[u][v] = d[v][u] = w
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] is not None and d[k][j] is not None:
                    via = d[i][k] + d[k][j]
                    if d[i][j] is None or via < d[i][j]:
                        d[i][j] = via
    assert all(all(x is not None for x in row) for row in d)
    return d


def hamiltonian_dp(d):
    """Different representation: exact full-metric subset DP, no core formula."""
    n = len(d)
    if n == 2:
        return 2 * d[0][1]
    best = {(1, 0): Fraction(0)}
    for mask in range(1, 1 << n, 2):
        for last in range(n):
            z = best.get((mask, last))
            if z is None:
                continue
            for v in range(1, n):
                if not ((mask >> v) & 1):
                    key = (mask | (1 << v), v)
                    cost = z + d[last][v]
                    if key not in best or cost < best[key]:
                        best[key] = cost
    return min(best[((1 << n) - 1, last)] + d[last][0]
               for last in range(1, n))


def full_metric_tsp(n, raw_paths):
    N, edges, _ = expand(n, raw_paths)
    return hamiltonian_dp(metric_closure(N, edges))


def subtour_lp(d):
    """Exact rational LP for small test instances, not needed by the proof."""
    from probes import exact_lp
    n = len(d)
    if n < 3:
        raise ValueError("subtour LP requires at least three vertices")
    pairs = tuple(combinations(range(n), 2))
    c = [d[u][v] for u, v in pairs]
    eq = [[int(v in edge) for edge in pairs] for v in range(n)]
    subsets = [frozenset(S)
               for k in range(1, n)
               for S in combinations(range(1, n), k)]
    ge = [[int((u in S) != (v in S)) for u, v in pairs] for S in subsets]
    value, x, y, z = exact_lp.solve(c, eq, [2] * n, ge, [2] * len(ge))
    certified = exact_lp.certify(c, eq, [2] * n, ge, [2] * len(ge), x, y, z)
    assert value == certified
    return value


def clone_metric(d, v):
    """Add a zero-cost twin of v in an already closed finite metric."""
    n = len(d)
    return [list(row) + [row[v]] for row in d] + [list(d[v]) + [Fraction(0)]]


def epsilon_for_ratio_tolerance(d, tolerance):
    """Finite rational ε ensuring |gap_ratio(G_ε) − gap_ratio(d)| <= tolerance.

    For a positive n-point metric d, the proof gives
    |R_ε − R| <= N(N-1)D*ε/(n*μ²), N=n+binom(n,2).
    No TSP or LP solver is needed to choose ε.
    """
    n = len(d)
    if n < 3 or any(len(row) != n for row in d):
        raise ValueError("metric with at least three vertices required")
    tolerance = Fraction(tolerance)
    if tolerance <= 0:
        raise ValueError("positive ratio tolerance required")
    distances = [Fraction(d[i][j]) for i in range(n) for j in range(i+1, n)]
    if any(z <= 0 for z in distances):
        raise ValueError("strictly positive off-diagonal distances required")
    mu, D = min(distances), max(distances)
    for i in range(n):
        if d[i][i] != 0:
            raise ValueError("metric diagonal must be zero")
        for j in range(n):
            if d[i][j] != d[j][i] or any(
                    Fraction(d[i][j]) > Fraction(d[i][k]) + Fraction(d[k][j])
                    for k in range(n)):
                raise ValueError("input must be a symmetric triangle metric")
    N = n + n*(n-1)//2
    return tolerance * n * mu * mu / (N * (N - 1) * D)


def weighted_2_subdivision(n, original_edges, epsilon):
    """Each original edge w becomes two edges epsilon,w (twin at first endpoint)."""
    return [(u, v, (epsilon, w)) for u, v, w in original_edges]


def run_check(trials=750, seed=20261102):
    rng = Random(seed)
    cases = 0
    largest = 0
    max_rank = 0
    for n in range(2, 6):
        potential = list(combinations(range(n), 2))
        for _ in range(trials):
            # Connected core created as a random spanning tree plus indexed extras.
            paths = []
            for v in range(1, n):
                u = rng.randrange(v)
                ws = tuple(Fraction(rng.choice([1, 2, 5, 11]), rng.choice([1, 2]))
                           for _ in range(rng.choice((2, 2, 3))))
                paths.append((u, v, ws))
            for _ in range(rng.randrange(0, 4)):
                u, v = rng.choice(potential)
                paths.append((u, v, tuple(Fraction(rng.choice([1, 2, 5, 11]),
                                                   rng.choice([1, 2])) for _ in range(2))))
            N = n + sum(len(x[2]) - 1 for x in paths)
            if N > 11:
                continue
            formula = exact_core_tsp(n, paths)
            cert = certificate(n, paths, formula)
            dp = full_metric_tsp(n, paths)
            assert formula["cost"] == cert["weight"] == dp, (n, paths, formula, dp)
            largest = max(largest, N)
            max_rank = max(max_rank, len(paths) - n + 1)
            if len(paths) <= 9:
                even_brute = set()
                for mask in range(1 << len(paths)):
                    parity = [0] * n
                    for i, (u, v, _) in enumerate(paths):
                        if (mask >> i) & 1:
                            parity[u] ^= 1
                            parity[v] ^= 1
                    if not any(parity):
                        even_brute.add(mask)
                basis = cycle_basis(n, validate(n, paths))
                even_basis = set()
                for state in range(1 << len(basis)):
                    mask = 0
                    for i, b in enumerate(basis):
                        if (state >> i) & 1:
                            mask ^= b
                    even_basis.add(mask)
                assert even_basis == even_brute
            cases += 1
    # Exact tests for graph-metric zero-distance clone invariance (SEP and TSP).
    base = metric_closure(3, [(0, 1, 2), (1, 2, 7), (0, 2, 13)])
    original_sep, original_tsp = subtour_lp(base), hamiltonian_dp(base)
    for v in (0, 1, 2):
        cloned = clone_metric(base, v)
        assert subtour_lp(cloned) == original_sep
        assert hamiltonian_dp(cloned) == original_tsp
    return dict(instances=cases, max_vertices=largest, max_cycle_rank=max_rank,
                zero_clone_checks=3, all_passed=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--trials", type=int, default=750)
    args = p.parse_args()
    print(json.dumps(run_check(trials=args.trials), sort_keys=True))
