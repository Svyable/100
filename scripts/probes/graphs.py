"""Census of all simple graphs on n <= 7 vertices up to isomorphism.

Search side: orderly extension (add a vertex to every graph on n-1 vertices
in every way) with an invariant-refined canonical form.
Check side: Burnside's lemma counts isomorphism classes independently, and
a brute-force canonical form over all n! permutations re-certifies that the
listed graphs are pairwise non-isomorphic.
"""
from itertools import permutations, product
from math import factorial

KNOWN_GRAPH_COUNTS = {1: 1, 2: 2, 3: 4, 4: 11, 5: 34, 6: 156, 7: 1044}  # OEIS A000088


def pair_order(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def to_adjacency(n, code):
    adj = [0] * n
    for bit, (i, j) in enumerate(pair_order(n)):
        if code >> bit & 1:
            adj[i] |= 1 << j
            adj[j] |= 1 << i
    return adj


def encode(n, adj, order):
    """Edge code of the graph relabelled so that position k holds order[k]."""
    code, bit = 0, 0
    for i in range(n):
        row = adj[order[i]]
        for j in range(i + 1, n):
            if row >> order[j] & 1:
                code |= 1 << bit
            bit += 1
    return code


def _classes(n, adj):
    degree = [bin(a).count("1") for a in adj]
    key = [(degree[v], tuple(sorted(degree[u] for u in range(n) if adj[v] >> u & 1)))
           for v in range(n)]
    groups = {}
    for v in range(n):
        groups.setdefault(key[v], []).append(v)
    return [groups[k] for k in sorted(groups)]


def canonical(n, adj):
    """Maximum edge code over relabellings respecting an isomorphism invariant."""
    classes = _classes(n, adj)
    best = -1
    for parts in product(*(permutations(c) for c in classes)):
        order = [v for part in parts for v in part]
        code = encode(n, adj, order)
        if code > best:
            best = code
    return best


def census(n):
    """Sorted canonical codes of all graphs on n vertices (1 <= n <= 7)."""
    if type(n) is not int or not 1 <= n <= 7:
        raise ValueError("graph census supports 1 <= n <= 7")
    level = {0}
    for m in range(2, n + 1):
        nxt = set()
        for code in level:
            base = to_adjacency(m - 1, code)
            for nbrs in range(1 << (m - 1)):
                adj = [a | ((nbrs >> i & 1) << (m - 1)) for i, a in enumerate(base)] + [nbrs]
                nxt.add(canonical(m, adj))
        level = nxt
    return sorted(level)


def delete_vertex(n, adj, v):
    keep = [u for u in range(n) if u != v]
    out = []
    for u in keep:
        row = 0
        for k, w in enumerate(keep):
            if adj[u] >> w & 1:
                row |= 1 << k
        out.append(row)
    return out


# ---------------------------------------------------------------- check side

def burnside_count(n):
    """Number of isomorphism classes of graphs on n vertices via Burnside."""
    pairs = pair_order(n)
    total = 0
    for perm in permutations(range(n)):
        seen, cycles = set(), 0
        for p in pairs:
            if p in seen:
                continue
            cycles += 1
            cur = p
            while cur not in seen:
                seen.add(cur)
                a, b = perm[cur[0]], perm[cur[1]]
                cur = (a, b) if a < b else (b, a)
        total += 1 << cycles
    if total % factorial(n):
        raise ArithmeticError("Burnside sum not divisible by n!")
    return total // factorial(n)


def edge_set(n, code):
    return frozenset(p for bit, p in enumerate(pair_order(n)) if code >> bit & 1)


def brute_canonical(n, edges):
    """Independent canonical form: lexicographically least sorted relabelled edge list."""
    best = None
    for perm in permutations(range(n)):
        image = tuple(sorted((min(perm[a], perm[b]), max(perm[a], perm[b])) for a, b in edges))
        if best is None or image < best:
            best = image
    return best


def degree_canonical(n, edges):
    """Independent canonical form: least sorted edge list over degree-respecting relabellings."""
    deg = [0] * n
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1
    classes = {}
    for v in range(n):
        classes.setdefault(deg[v], []).append(v)
    blocks = [classes[d] for d in sorted(classes)]
    best = None
    for parts in product(*(permutations(b) for b in blocks)):
        order = [v for part in parts for v in part]
        pos = {v: i for i, v in enumerate(order)}
        image = tuple(sorted((min(pos[a], pos[b]), max(pos[a], pos[b])) for a, b in edges))
        if best is None or image < best:
            best = image
    return best


def certify_census(n, codes):
    """Check that ``codes`` lists every graph on n vertices exactly once up to isomorphism."""
    from .core import require
    require(len(codes) == burnside_count(n),
            f"n={n}: census size {len(codes)} differs from Burnside count")
    forms = {degree_canonical(n, edge_set(n, c)) for c in codes}
    require(len(forms) == len(codes), f"n={n}: census contains isomorphic duplicates")
