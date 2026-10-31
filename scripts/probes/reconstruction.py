"""M078 - Graph reconstruction: every graph on 3 <= n <= N vertices is determined by its deck."""
from .core import digest, require
from .graphs import (KNOWN_GRAPH_COUNTS, canonical, census, certify_census, degree_canonical,
                     delete_vertex, edge_set, to_adjacency)

PROBE = {
    "id": "reconstruction",
    "problem_id": "M078",
    "title": "Vertex-deck reconstruction for every graph up to N vertices",
    "engines": ["graph_census"],
    "frontier": ("Known: verified by computer for all graphs on at most 11 vertices (McKay 1997) "
                 "and beyond; proved for trees, regular and disconnected graphs (Kelly 1957)."),
    "levels": {"smoke": {"max_n": 6}, "deep": {"max_n": 7}},
}


def scope(params):
    return (f"For every n with 3 <= n <= {params['max_n']}, the {params['max_n']}-vertex census is complete "
            "(Burnside-certified) and no two non-isomorphic graphs share a vertex-deleted deck.")


def deck(n, code):
    adj = to_adjacency(n, code)
    return sorted(canonical(n - 1, delete_vertex(n, adj, v)) for v in range(n))


def search(params):
    out, holds = {}, True
    for n in range(3, params["max_n"] + 1):
        codes = census(n)
        seen = {}
        clash = None
        for c in codes:
            key = tuple(deck(n, c))
            if key in seen:
                clash = [seen[key], c]
                holds = False
                break
            seen[key] = c
        out[str(n)] = {"graphs": codes, "distinct_decks": len(seen)}
        if clash:
            out[str(n)]["counterexample"] = clash
            break
    return {
        "holds": holds,
        "summary": {n: {"graphs": len(v["graphs"]), "distinct_decks": v["distinct_decks"]}
                    for n, v in out.items()} | {"census_sha256": digest(out)},
        "certificate": out,
    }


def check(params, result):
    cert = result["certificate"]
    for n in range(3, params["max_n"] + 1):
        codes = cert[str(n)]["graphs"]
        require(len(codes) == KNOWN_GRAPH_COUNTS[n], f"n={n}: count differs from OEIS A000088")
        certify_census(n, codes)
        memo, decks = {}, set()
        for c in codes:
            edges = edge_set(n, c)
            cards = []
            for v in range(n):
                relabel = {u: u - (u > v) for u in range(n) if u != v}
                card = frozenset((relabel[a], relabel[b]) for a, b in edges if v not in (a, b))
                if card not in memo:
                    memo[card] = degree_canonical(n - 1, card)
                cards.append(memo[card])
            decks.add(tuple(sorted(cards)))
        require(len(decks) == len(codes), f"n={n}: two non-isomorphic graphs share a deck")
        require(cert[str(n)]["distinct_decks"] == len(codes), "summary mismatch")
    require(result["summary"]["census_sha256"] == digest(cert), "census hash mismatch")
