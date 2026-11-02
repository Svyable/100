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
    """Replay every requested witness, then bind the public claim to the replay.

    In particular, an empty/partial certificate is never evidence of a bound.
    The checker intentionally verifies the colouring, not that it was generated
    by the named Paley/circulant constructor: a distinct valid graph on the
    same number of vertices would prove the same lower bound.
    """
    names = params.get("witnesses")
    require(isinstance(names, list) and bool(names) and
            all(isinstance(name, str) and name in CLAIMS for name in names) and
            len(names) == len(set(names)), "invalid or duplicate witness requests")
    require(isinstance(result, dict), "result must be an object")
    found = result.get("certificate")
    require(isinstance(found, dict) and set(found) == set(names),
            "certificate must contain exactly the requested witnesses")
    require(result.get("holds") is True, "all registered witnesses must certify")

    summary = {}
    for name in names:
        w = found[name]
        require(isinstance(w, dict) and set(w) == {
            "vertices", "s", "t", "clique_number", "independence_number",
            "edges", "certifies",
        }, f"{name}: incomplete or extra witness fields")
        m = graph(name)[0]
        s, t = CLAIMS[name]
        require(type(w["vertices"]) is int and w["vertices"] == m and
                type(w["s"]) is int and w["s"] == s and
                type(w["t"]) is int and w["t"] == t,
                f"{name}: graph order or Ramsey thresholds differ from claim")

        edges = w["edges"]
        require(isinstance(edges, list) and all(
            isinstance(pair, list) and len(pair) == 2 and
            all(type(x) is int for x in pair) and
            0 <= pair[0] < pair[1] < m for pair in edges
        ), f"{name}: malformed edge list")
        E = {tuple(pair) for pair in edges}
        require(len(E) == len(edges), f"{name}: duplicate edges")

        def is_red(a, b):
            return (min(a, b), max(a, b)) in E

        def has_clique(k, red):
            return any(all(is_red(a, b) is red for a, b in combinations(S, 2))
                       for S in combinations(range(m), k))

        require(not has_clique(s, True) and not has_clique(t, False),
                f"{name}: monochromatic forbidden clique")
        # No s/t clique exists, so the maximum lies below s/t respectively.
        # Compute the reported maxima by a separate exhaustive subset scan.
        omega = next((k for k in range(s - 1, 0, -1)
                      if has_clique(k, True)), 0)
        alpha = next((k for k in range(t - 1, 0, -1)
                      if has_clique(k, False)), 0)
        require(type(w["clique_number"]) is int and
                w["clique_number"] == omega and
                type(w["independence_number"]) is int and
                w["independence_number"] == alpha and
                w["certifies"] is True,
                f"{name}: incorrect witness statistics or certification flag")
        summary[name] = f"R({s},{t}) > {m}"

    summary["witnesses_sha256"] = digest(found)
    require(result.get("summary") == summary,
            "published summary or digest does not match verified witnesses")
