"""Which deck-readable invariants already separate the graph census.

Degree sequence is read from card edge counts (Kelly). Triangle counts for n >= 4
are read from the cards and divided by n-3. The search path uses adjacency degrees
and a direct triangle count. Neither number is a reconstruction theorem.
"""
from itertools import combinations

from probes.core import require
from probes.graphs import (
    KNOWN_GRAPH_COUNTS, census, certify_census, delete_vertex, to_adjacency,
)

MINE = {
    "id": "deck_invariants",
    "problem_id": "M078",
    "title": "Deck invariants that separate the census",
    "engines": ["graph_census"],
    "frontier": ("Reconstruction is already verified by computer through at least 11 vertices (McKay 1997). "
                 "The new column is the multiset of card degree sequences, read from the deck. "
                 "With the triangle count it separates the census through 7 vertices. "
                 "That is a finite certificate, not a reconstruction theorem."),
    "levels": {"smoke": {"max_n": 7}},
}


def scope(params):
    return (f"On the complete graph census for 3 <= n <= {params['max_n']}, excess over the degree sequence, "
            "over degree sequence plus triangles, and over the deck of card degree sequences plus triangles.")


def _adjacency_degrees(n, code):
    adj = to_adjacency(n, code)
    return tuple(sorted(bin(row).count("1") for row in adj))


def _direct_triangles(n, code):
    adj = to_adjacency(n, code)
    return sum(1 for a, b, c in combinations(range(n), 3)
               if (adj[a] >> b) & (adj[b] >> c) & (adj[a] >> c) & 1)


def _cards(n, code):
    adj = to_adjacency(n, code)
    cards = []
    for dropped in range(n):
        keep = [u for u in range(n) if u != dropped]
        card = [0] * (n - 1)
        for i, a in enumerate(keep):
            for j in range(i + 1, n - 1):
                if adj[a] >> keep[j] & 1:
                    card[i] |= 1 << j
                    card[j] |= 1 << i
        cards.append(card)
    return cards


def _kelly_degrees(n, code):
    """Degree sequence from card edge counts: e(G) = sum e(G-v) / (n-2), deg(v) = e(G) - e(G-v)."""
    cards = _cards(n, code)
    card_edges = [sum(bin(row).count("1") for row in card) // 2 for card in cards]
    total = sum(card_edges)
    require(total % (n - 2) == 0, "card edge counts are not a Kelly instance")
    edges = total // (n - 2)
    return tuple(sorted(edges - e for e in card_edges))


def _card_triangles(n, code):
    if n == 3:
        return 1 if _kelly_degrees(n, code) == (2, 2, 2) else 0
    cards = _cards(n, code)

    def triangles(adj):
        m = len(adj)
        return sum(bin(adj[a] & adj[b]).count("1")
                   for a in range(m) for b in range(a + 1, m) if adj[a] >> b & 1) // 3

    total = sum(triangles(card) for card in cards)
    require(total % (n - 3) == 0, "card triangle counts are not divisible by n-3")
    return total // (n - 3)


def _degree_tuple(adj):
    return tuple(sorted(bin(row).count("1") for row in adj))


def _card_degree_deck(n, code):
    """Multiset of degree sequences of the vertex-deleted cards, from the packed cards."""
    return tuple(sorted(_degree_tuple(card) for card in _cards(n, code)))


def _deleted_degree_deck(n, code):
    """Same multiset, recomputed by deleting each vertex from the adjacency list."""
    adj = to_adjacency(n, code)
    return tuple(sorted(_degree_tuple(delete_vertex(n, adj, v)) for v in range(n)))


def _excess(codes, key):
    classes = len({key(code) for code in codes})
    return len(codes) - classes


def _separates_through(excess):
    reached = 2
    for n in range(3, max(excess) + 1):
        if excess[n] == 0 and n == reached + 1:
            reached = n
        else:
            break
    return reached if reached >= 3 else 0


def search(params):
    excess_degree, excess_both, excess_deck = {}, {}, {}
    for n in range(3, params["max_n"] + 1):
        codes = census(n)
        excess_degree[n] = _excess(codes, lambda code, n=n: _adjacency_degrees(n, code))
        excess_both[n] = _excess(codes, lambda code, n=n: (
            _adjacency_degrees(n, code), _direct_triangles(n, code)))
        excess_deck[n] = _excess(codes, lambda code, n=n: (
            _card_degree_deck(n, code), _direct_triangles(n, code)))
    summary = {
        "max_n": params["max_n"],
        "degree_excess": {str(n): excess_degree[n] for n in excess_degree},
        "degree_and_triangles_excess": {str(n): excess_both[n] for n in excess_both},
        "degree_deck_and_triangles_excess": {str(n): excess_deck[n] for n in excess_deck},
        "degree_separates_through": _separates_through(excess_degree),
        "degree_and_triangles_separate_through": _separates_through(excess_both),
        "degree_deck_and_triangles_separate_through": _separates_through(excess_deck),
    }
    return {"holds": True, "summary": summary, "certificate": summary}


def check(params, result):
    excess_degree, excess_both, excess_deck = {}, {}, {}
    for n in range(3, params["max_n"] + 1):
        codes = census(n)
        require(len(codes) == KNOWN_GRAPH_COUNTS[n], f"n={n}: census size is not OEIS A000088")
        certify_census(n, codes)
        for code in codes:
            require(_adjacency_degrees(n, code) == _kelly_degrees(n, code),
                    f"n={n}: Kelly degrees differ from the adjacency degrees")
            require(_direct_triangles(n, code) == _card_triangles(n, code),
                    f"n={n}: card triangle count differs from the direct count")
            require(_card_degree_deck(n, code) == _deleted_degree_deck(n, code),
                    f"n={n}: card degree deck differs from vertex deletion")
        excess_degree[n] = _excess(codes, lambda code, n=n: _kelly_degrees(n, code))
        excess_both[n] = _excess(codes, lambda code, n=n: (_kelly_degrees(n, code), _card_triangles(n, code)))
        excess_deck[n] = _excess(codes, lambda code, n=n: (
            _deleted_degree_deck(n, code), _card_triangles(n, code)))
    summary = {
        "max_n": params["max_n"],
        "degree_excess": {str(n): excess_degree[n] for n in excess_degree},
        "degree_and_triangles_excess": {str(n): excess_both[n] for n in excess_both},
        "degree_deck_and_triangles_excess": {str(n): excess_deck[n] for n in excess_deck},
        "degree_separates_through": _separates_through(excess_degree),
        "degree_and_triangles_separate_through": _separates_through(excess_both),
        "degree_deck_and_triangles_separate_through": _separates_through(excess_deck),
    }
    require(result["summary"] == summary, "deck-invariant table does not match the card recomputation")
    require(result["certificate"] == summary, "certificate is not the checked table")
