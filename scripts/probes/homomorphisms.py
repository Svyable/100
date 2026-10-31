"""Exact homomorphism counts hom(H, G) for bipartite pattern graphs H.

For H with parts A, B: hom(H, G) = sum over maps f: A -> V(G) of
prod over b in B of |common neighbourhood of f(N(b))| (n if b is isolated).
``count_from_side`` lets a checker recount from the other side, and
``brute_count`` enumerates every map V(H) -> V(G) for tiny cases.
"""
from itertools import product


def bipartite(a_size, b_size, edges):
    """edges: (i, j) with i in A = range(a_size), j in B = range(b_size)."""
    nb = [[i for i, j in edges if j == b] for b in range(b_size)]
    na = [[j for i, j in edges if i == a] for a in range(a_size)]
    return {"A": a_size, "B": b_size, "edges": sorted(edges), "NB": nb, "NA": na}


def count_from_side(H, n, adj, side="A"):
    """hom(H, G) for G given by adjacency bitmasks; enumerate maps of one side."""
    size, nbrs = (H["A"], H["NB"]) if side == "A" else (H["B"], H["NA"])
    full = (1 << n) - 1
    total = 0
    for f in product(range(n), repeat=size):
        prod_ = 1
        for nb in nbrs:
            common = full
            for v in nb:
                common &= adj[f[v]]
            k = bin(common).count("1")
            if k == 0:
                prod_ = 0
                break
            prod_ *= k
        total += prod_
    return total


def brute_count(H, n, adj):
    """Enumerate all maps V(H) -> V(G) (only for very small cases)."""
    total = 0
    for f in product(range(n), repeat=H["A"] + H["B"]):
        if all(adj[f[i]] >> f[H["A"] + j] & 1 for i, j in H["edges"]):
            total += 1
    return total


def sidorenko_holds(hom, n, edges_g, edges_h, vertices_h):
    """t(H,G) >= t(K2,G)^e(H), i.e. hom * n^(2e(H) - v(H)) >= (2 e(G))^e(H)."""
    return hom * n ** (2 * edges_h - vertices_h) >= (2 * edges_g) ** edges_h
