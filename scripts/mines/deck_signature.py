"""A deck signature that separates every graph on at most 7 vertices.

The signature of G is the sorted list, over vertices v, of
(degree sequence of G-v, number of triangles in G-v). Both numbers are read
off the card G-v. Degree sequence plus one global triangle count left excess
graphs at 6 vertices; this per-card signature leaves none through 7, which is
the whole census this repository can enumerate. McKay's verification already
goes past 11 vertices, so this is not a reconstruction theorem.
"""
from itertools import combinations

from probes.core import require
from probes.graphs import (KNOWN_GRAPH_COUNTS, census, certify_census, delete_vertex,
                           edge_set, to_adjacency)

MINE = {
    "id": "deck_signature",
    "problem_id": "M078",
    "title": "Per-card degree and triangle signature separates the census",
    "engines": ["graph_census"],
    "frontier": ("Graph reconstruction is verified by computer through at least 11 vertices (McKay 1997). "
                 "The signature below separates only the census this repository enumerates, through 7 vertices."),
    "levels": {"smoke": {"max_n": 7}},
}


def scope(params):
    return (f"For every n with 3 <= n <= {params['max_n']}, the multiset of "
            "(degree sequence of G-v, number of triangles in G-v) is different for every graph G on n vertices.")


def _triangles(adj):
    m = len(adj)
    return sum(1 for a, b, c in combinations(range(m), 3)
               if (adj[a] >> b) & (adj[b] >> c) & (adj[a] >> c) & 1)


def _from_adjacency(n, code):
    adj = to_adjacency(n, code)
    cards = []
    for vertex in range(n):
        card = delete_vertex(n, adj, vertex)
        degrees = tuple(sorted(bin(row).count("1") for row in card))
        cards.append((degrees, _triangles(card)))
    return tuple(sorted(cards))


def _from_edges(n, code):
    edges = edge_set(n, code)
    cards = []
    for vertex in range(n):
        keep = [u for u in range(n) if u != vertex]
        index = {u: i for i, u in enumerate(keep)}
        card_edges = [(index[a], index[b]) for a, b in edges if vertex not in (a, b)]
        degrees = [0] * (n - 1)
        for a, b in card_edges:
            degrees[a] += 1
            degrees[b] += 1
        incident = [set() for _ in range(n - 1)]
        for a, b in card_edges:
            incident[a].add(b)
            incident[b].add(a)
        triangles = sum(1 for a, b, c in combinations(range(n - 1), 3)
                        if b in incident[a] and c in incident[b] and a in incident[c])
        cards.append((tuple(sorted(degrees)), triangles))
    return tuple(sorted(cards))


def _excess(n, reader):
    codes = census(n)
    require(len(codes) == KNOWN_GRAPH_COUNTS[n], f"n={n}: census is not OEIS A000088")
    certify_census(n, codes)
    signatures = [reader(n, code) for code in codes]
    return len(codes) - len(set(signatures)), len(codes)


def search(params):
    excess, graphs = {}, {}
    for n in range(3, params["max_n"] + 1):
        extra, count = _excess(n, _from_adjacency)
        excess[str(n)] = extra
        graphs[str(n)] = count
    separates = 2
    for n in range(3, params["max_n"] + 1):
        if excess[str(n)] == 0 and n == separates + 1:
            separates = n
        else:
            break
    summary = {
        "max_n": params["max_n"],
        "graphs": graphs,
        "excess": excess,
        "separates_through": separates if separates >= 3 else 0,
    }
    return {"holds": separates == params["max_n"], "summary": summary, "certificate": summary}


def check(params, result):
    excess = {}
    for n in range(3, params["max_n"] + 1):
        codes = census(n)
        for code in codes:
            require(_from_adjacency(n, code) == _from_edges(n, code),
                    f"n={n}: adjacency cards and edge-set cards disagree")
        extra, count = _excess(n, _from_edges)
        require(count == KNOWN_GRAPH_COUNTS[n], "count mismatch")
        excess[str(n)] = extra
    require(all(value == 0 for value in excess.values()),
            "the per-card signature does not separate the census")
    require(result["summary"]["excess"] == excess, "recorded excess does not match the edge-set recount")
    require(result["summary"]["separates_through"] == params["max_n"], "separation claim does not reach max_n")
    require(result["certificate"] == result["summary"], "certificate is not the checked summary")
