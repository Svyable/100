"""Which deck-readable invariants already separate the graph census.

Degree sequence is read from card edge counts (Kelly). Triangle counts for n >= 4
are read from the cards and divided by n-3. Induced P4 counts for n >= 5 are read
from the cards and divided by n-4. The search path uses adjacency degrees and
direct subgraph counts. A separating table is not a reconstruction theorem.
"""
from itertools import combinations

from probes.core import require
from probes.graphs import KNOWN_GRAPH_COUNTS, census, certify_census, to_adjacency

MINE = {
    "id": "deck_invariants",
    "problem_id": "M078",
    "title": "Deck invariants that separate the census",
    "engines": ["graph_census"],
    "frontier": (
        "Reconstruction is already verified by computer through at least 11 vertices "
        "(McKay 1997). Degree + triangles + induced P4 separates the census through 6 "
        "vertices here; that finite separation is not a general reconstruction proof."
    ),
    "levels": {"smoke": {"max_n": 6}},
}


def scope(params):
    return (
        f"On the complete graph census for 3 <= n <= {params['max_n']}, the excess of "
        "graphs over classes of the deck-certified degree sequence, over degree sequence "
        "plus triangle count, and over those two plus the induced P4 count."
    )


def _adjacency_degrees(n, code):
    adj = to_adjacency(n, code)
    return tuple(sorted(bin(row).count("1") for row in adj))


def _direct_triangles(n, code):
    adj = to_adjacency(n, code)
    return sum(1 for a, b, c in combinations(range(n), 3)
               if (adj[a] >> b) & (adj[b] >> c) & (adj[a] >> c) & 1)


def _induced_p4_on_adj(adj):
    """Number of distinct 4-vertex sets that induce a path P4."""
    m = len(adj)
    seen = set()
    for a in range(m):
        for b in range(m):
            if a == b or not ((adj[a] >> b) & 1):
                continue
            for c in range(m):
                if c in (a, b) or not ((adj[b] >> c) & 1) or ((adj[a] >> c) & 1):
                    continue
                for d in range(m):
                    if d in (a, b, c) or not ((adj[c] >> d) & 1):
                        continue
                    if ((adj[a] >> d) & 1) or ((adj[b] >> d) & 1):
                        continue
                    seen.add(frozenset((a, b, c, d)))
    return len(seen)


def _direct_induced_p4(n, code):
    return _induced_p4_on_adj(to_adjacency(n, code))


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


def _card_induced_p4(n, code):
    """Induced P4 count from cards: each P4 of G appears in exactly n-4 cards."""
    if n < 5:
        return _direct_induced_p4(n, code)
    total = sum(_induced_p4_on_adj(card) for card in _cards(n, code))
    require(total % (n - 4) == 0, "card induced-P4 counts are not divisible by n-4")
    return total // (n - 4)


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


def _table(params, degree_fn, triangle_fn, p4_fn):
    excess_degree, excess_both, excess_triple = {}, {}, {}
    for n in range(3, params["max_n"] + 1):
        codes = census(n)
        excess_degree[n] = _excess(codes, lambda code, n=n: degree_fn(n, code))
        excess_both[n] = _excess(
            codes, lambda code, n=n: (degree_fn(n, code), triangle_fn(n, code))
        )
        excess_triple[n] = _excess(
            codes,
            lambda code, n=n: (degree_fn(n, code), triangle_fn(n, code), p4_fn(n, code)),
        )
    return {
        "max_n": params["max_n"],
        "degree_excess": {str(n): excess_degree[n] for n in excess_degree},
        "degree_and_triangles_excess": {str(n): excess_both[n] for n in excess_both},
        "degree_triangles_p4_excess": {str(n): excess_triple[n] for n in excess_triple},
        "degree_separates_through": _separates_through(excess_degree),
        "degree_and_triangles_separate_through": _separates_through(excess_both),
        "degree_triangles_p4_separate_through": _separates_through(excess_triple),
    }


def search(params):
    summary = _table(params, _adjacency_degrees, _direct_triangles, _direct_induced_p4)
    return {"holds": True, "summary": summary, "certificate": summary}


def check(params, result):
    for n in range(3, params["max_n"] + 1):
        codes = census(n)
        require(len(codes) == KNOWN_GRAPH_COUNTS[n], f"n={n}: census size is not OEIS A000088")
        certify_census(n, codes)
        for code in codes:
            require(_adjacency_degrees(n, code) == _kelly_degrees(n, code),
                    f"n={n}: Kelly degrees differ from the adjacency degrees")
            require(_direct_triangles(n, code) == _card_triangles(n, code),
                    f"n={n}: card triangle count differs from the direct count")
            require(_direct_induced_p4(n, code) == _card_induced_p4(n, code),
                    f"n={n}: card induced-P4 count differs from the direct count")
    summary = _table(params, _kelly_degrees, _card_triangles, _card_induced_p4)
    require(result["summary"] == summary, "deck-invariant table does not match the card recomputation")
    require(result["certificate"] == summary, "certificate is not the checked table")
    require(summary["degree_triangles_p4_separate_through"] >= params["max_n"],
            "induced P4 was expected to finish separation through the smoke range")
