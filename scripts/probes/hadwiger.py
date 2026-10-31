"""M071 - Hadwiger: every graph on n <= N vertices with a proper t-colouring
certificate and a K_t-minor model where t is its chromatic number.

The certificate per graph is (proper colouring with t colours, t connected
pairwise-adjacent branch sets). Since chi <= t and K_t contains K_chi as a
minor, the check never needs to trust a chromatic-number computation.
"""
from itertools import combinations

from .core import digest, require
from .graphs import census, certify_census, edge_set, to_adjacency

PROBE = {
    "id": "hadwiger",
    "problem_id": "M071",
    "title": "Hadwiger's conjecture on every graph up to N vertices",
    "engines": ["graph_census"],
    "frontier": ("Known: proved for chromatic number <= 6 (Robertson, Seymour & Thomas 1993), "
                 "so every graph on <= 7 vertices is a known case. Reproduction only."),
    "levels": {"smoke": {"max_n": 6}, "deep": {"max_n": 7}},
}


def scope(params):
    return (f"Every graph on 1..{params['max_n']} vertices has a proper t-colouring and a K_t minor "
            "model for t = its chromatic number.")


def colouring(n, adj, k):
    colour = [-1] * n
    def place(v):
        if v == n:
            return True
        used = {colour[u] for u in range(v) if adj[v] >> u & 1}
        for c in range(min(k, max(colour[:v], default=-1) + 2)):
            if c not in used:
                colour[v] = c
                if place(v + 1):
                    return True
        colour[v] = -1
        return False
    return list(colour) if place(0) else None


def components(n, adj):
    seen, comps = 0, []
    for s in range(n):
        if seen >> s & 1:
            continue
        comp, frontier = 1 << s, 1 << s
        while frontier:
            v = frontier.bit_length() - 1
            frontier &= ~(1 << v)
            new = adj[v] & ~comp
            comp |= new
            frontier |= new
        seen |= comp
        comps.append([v for v in range(n) if comp >> v & 1])
    return comps


def _connected(block, adj):
    block = set(block)
    start = next(iter(block))
    stack, seen = [start], {start}
    while stack:
        v = stack.pop()
        for u in block:
            if u not in seen and adj[v] >> u & 1:
                seen.add(u)
                stack.append(u)
    return seen == block


def minor_model(vertices, adj, t):
    """Partition ``vertices`` (a connected set) into t connected, pairwise adjacent blocks."""
    m = len(vertices)
    labels = [0] * m
    def rec(i, used):
        if i == m:
            if used != t:
                return None
            blocks = [[vertices[j] for j in range(m) if labels[j] == b] for b in range(t)]
            if not all(_connected(b, adj) for b in blocks):
                return None
            for a, b in combinations(blocks, 2):
                if not any(adj[x] >> y & 1 for x in a for y in b):
                    return None
            return blocks
        if m - i < t - used:
            return None
        for b in range(min(used + 1, t)):
            labels[i] = b
            found = rec(i + 1, max(used, b + 1))
            if found:
                return found
        return None
    return rec(0, 0)


def certify(n, code):
    adj = to_adjacency(n, code)
    t = next(k for k in range(1, n + 1) if colouring(n, adj, k))
    col = colouring(n, adj, t)
    for comp in components(n, adj):
        inside = sum(1 << v for v in comp)
        cadj = [adj[v] & inside for v in range(n)]
        if t > 1 and colouring(n, cadj, t - 1):
            continue  # this component is (t-1)-colourable; the K_t model lives elsewhere
        model = minor_model(comp, adj, t)
        if model:
            return {"graph": code, "colouring": col, "branch_sets": model}
    return {"graph": code, "colouring": col, "branch_sets": None}


def search(params):
    out, holds, dist = {}, True, {}
    for n in range(1, params["max_n"] + 1):
        certs = [certify(n, c) for c in census(n)]
        bad = [c for c in certs if c["branch_sets"] is None]
        for c in certs:
            t = len(set(c["colouring"]))
            dist[t] = dist.get(t, 0) + 1
        out[str(n)] = certs
        if bad:
            holds = False
            break
    return {
        "holds": holds,
        "summary": {"graphs_certified": sum(len(v) for v in out.values()),
                    "by_chromatic_number": {str(k): dist[k] for k in sorted(dist)},
                    "certificate_sha256": digest(out)},
        "certificate": out,
    }


def check(params, result):
    cert = result["certificate"]
    for n in range(1, params["max_n"] + 1):
        rows = cert[str(n)]
        certify_census(n, [r["graph"] for r in rows])
        for r in rows:
            edges = edge_set(n, r["graph"])
            col = r["colouring"]
            require(len(col) == n and all(col[a] != col[b] for a, b in edges),
                    f"n={n} graph {r['graph']}: colouring is not proper")
            t = len(set(col))
            blocks = r["branch_sets"]
            require(blocks is not None and len(blocks) == t, f"n={n} graph {r['graph']}: no K_{t} model")
            flat = [v for b in blocks for v in b]
            require(len(flat) == len(set(flat)) and all(0 <= v < n for v in flat) and all(blocks),
                    "branch sets must be disjoint, nonempty vertex sets")
            nbr = {v: set() for v in range(n)}
            for a, b in edges:
                nbr[a].add(b)
                nbr[b].add(a)
            for b in blocks:
                seen, stack = {b[0]}, [b[0]]
                while stack:
                    v = stack.pop()
                    for u in nbr[v] & set(b):
                        if u not in seen:
                            seen.add(u)
                            stack.append(u)
                require(seen == set(b), f"n={n} graph {r['graph']}: branch set {b} disconnected")
            for a, b in combinations(blocks, 2):
                require(any(y in nbr[x] for x in a for y in b),
                        f"n={n} graph {r['graph']}: branch sets {a}, {b} not adjacent")
    require(result["summary"]["certificate_sha256"] == digest(cert), "certificate hash mismatch")
