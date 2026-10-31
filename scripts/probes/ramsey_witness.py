"""M095 - Ramsey lower-bound witnesses from Paley and circulant colourings.

A graph G on m vertices with no K_s and no independent set of size t
certifies R(s,t) > m. Search uses greedy-pivot clique search; the check
re-enumerates every s- and t-subset directly.
"""
from itertools import combinations

from .core import digest, require
from .fields import field

PROBE = {
    "id": "ramsey_witnesses",
    "problem_id": "M095",
    "title": "Exact Ramsey lower-bound colourings (Paley and circulant graphs)",
    "engines": ["finite_fields", "clique_search"],
    "frontier": ("Known: R(3,3)=6, R(3,4)=9, R(3,5)=14, R(4,4)=18; 43 <= R(5,5) <= 46 "
                 "(lower bound Exoo 1989). Witnesses here reproduce classical lower bounds."),
    "levels": {
        "smoke": {"witnesses": ["paley5", "circ8_1_4", "circ13_1_5", "paley17"]},
        "deep": {"witnesses": ["paley5", "circ8_1_4", "circ13_1_5", "paley17", "paley37"]},
    },
}

CLAIMS = {  # name -> (s, t): certifies R(s, t) > vertex count
    "paley5": (3, 3), "circ8_1_4": (3, 4), "circ13_1_5": (3, 5),
    "paley17": (4, 4), "paley37": (5, 5),
}


def scope(params):
    parts = []
    for w in params["witnesses"]:
        s, t = CLAIMS[w]
        parts.append(f"R({s},{t}) > {graph(w)[0]}")
    return "Explicit colourings certify " + ", ".join(parts) + "."


def graph(name):
    if name.startswith("paley"):
        q = int(name[5:])
        F = field(q)
        adj = [[i != j and F.chi[F.sub(i, j)] == 1 for j in range(q)] for i in range(q)]
        return q, adj
    m = int(name.split("_")[0][4:])
    dist = {int(d) for d in name.split("_")[1:]}
    dist |= {m - d for d in dist}
    return m, [[i != j and (j - i) % m in dist for j in range(m)] for i in range(m)]


def clique_number(m, adj):
    nbr = [sum(1 << j for j in range(m) if adj[i][j]) for i in range(m)]
    best = 0
    def expand(size, cand):
        nonlocal best
        if not cand:
            best = max(best, size)
            return
        if size + bin(cand).count("1") <= best:
            return
        while cand:
            v = cand.bit_length() - 1
            expand(size + 1, cand & nbr[v])
            cand &= ~(1 << v)
            if size + bin(cand).count("1") <= best:
                return
    expand(0, (1 << m) - 1)
    return best


def search(params):
    found = {}
    holds = True
    for name in params["witnesses"]:
        m, adj = graph(name)
        comp = [[i != j and not adj[i][j] for j in range(m)] for i in range(m)]
        s, t = CLAIMS[name]
        omega, alpha = clique_number(m, adj), clique_number(m, comp)
        ok = omega < s and alpha < t
        holds &= ok
        edges = [[i, j] for i in range(m) for j in range(i + 1, m) if adj[i][j]]
        found[name] = {"vertices": m, "s": s, "t": t, "clique_number": omega,
                       "independence_number": alpha, "edges": edges, "certifies": ok}
    return {
        "holds": holds,
        "summary": {n: f"R({w['s']},{w['t']}) > {w['vertices']}" if w["certifies"] else "fails"
                    for n, w in found.items()} | {"witnesses_sha256": digest(found)},
        "certificate": found,
    }


def check(params, result):
    for name, w in result["certificate"].items():
        m, s, t = w["vertices"], w["s"], w["t"]
        E = {(a, b) for a, b in w["edges"]}
        require(all(0 <= a < b < m for a, b in E), f"{name}: malformed edges")
        def edge(a, b):
            return (min(a, b), max(a, b)) in E
        mono_red = any(all(edge(a, b) for a, b in combinations(S, 2)) for S in combinations(range(m), s))
        mono_blue = any(not any(edge(a, b) for a, b in combinations(S, 2)) for S in combinations(range(m), t))
        require(w["certifies"] == (not mono_red and not mono_blue),
                f"{name}: certification flag disagrees with exhaustive subset check")
        require(w["certifies"], f"{name}: colouring has a monochromatic clique")
