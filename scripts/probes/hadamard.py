"""M094 - Hadamard conjecture: exact Hadamard matrices for many orders 4k <= N.

Constructions (search side): Sylvester doubling, Paley I (q = 3 mod 4) and
Paley II (q = 1 mod 4) over GF(q) for prime powers q, Williamson quadruples of
symmetric circulants (meet-in-the-middle on periodic autocorrelations) for
remaining gap orders 4n with odd n <= williamson_max, all closed under
Kronecker products. Check side: every row pair is verified orthogonal, i.e. H H^T = nI,
with popcount arithmetic on +-1 bit rows. Orders the engine cannot reach are
reported as *engine gaps*, which the literature fills by other constructions.
"""
from .core import digest, require
from .fields import field, prime_power

PROBE = {
    "id": "hadamard",
    "problem_id": "M094",
    "title": "Exact Hadamard matrices from Sylvester, Paley I/II and Kronecker products",
    "engines": ["finite_fields"],
    "frontier": ("Known: constructions exist for every order 4k < 668; 668 is the smallest "
                 "order with no known Hadamard matrix (after order 428, Kharaghani & "
                 "Tayfeh-Rezaie 2005). Orders 116, 156 and 172 are published propus "
                 "quadruples (arXiv:1503.04226, arXiv:1708.05098), not new matrices. "
                 "Engine gaps below are NOT open cases."),
    "levels": {"smoke": {"limit": 128, "williamson_max": 23},
               "deep": {"limit": 400, "williamson_max": 23}},
}


def scope(params):
    limit = params["limit"]
    built = sum(1 for n in recipes(limit, params.get("williamson_max", 0)) if n % 4 == 0)
    return (f"Explicit (+1/-1) matrices with H H^T = nI for {built} of the {limit // 4} orders "
            f"4k <= {limit} (the rest are engine gaps, not open cases).")


# Rows are ints: bit j set means entry -1 in column j.

def sylvester(k):
    rows = [0]
    for size in (1 << i for i in range(k)):
        full = (1 << size) - 1
        rows = [r | (r << size) for r in rows] + [r | ((r ^ full) << size) for r in rows]
    return rows


def _jacobsthal(q):
    F = field(q)
    return [[F.chi[F.sub(a, b)] for b in range(q)] for a in range(q)]


def paley1(q):
    """Order q + 1 for q = 3 mod 4: H = I + [[0, j^T], [-j, Q]]."""
    Q = _jacobsthal(q)
    n = q + 1
    M = [[0] * n for _ in range(n)]
    for j in range(1, n):
        M[0][j], M[j][0] = 1, -1
    for a in range(q):
        for b in range(q):
            M[a + 1][b + 1] = Q[a][b]
    for i in range(n):
        M[i][i] += 1
    return _pack(M)


def paley2(q):
    """Order 2(q + 1) for q = 1 mod 4 from the symmetric conference matrix."""
    Q = _jacobsthal(q)
    n = q + 1
    C = [[0] * n for _ in range(n)]
    for j in range(1, n):
        C[0][j] = C[j][0] = 1
    for a in range(q):
        for b in range(q):
            C[a + 1][b + 1] = Q[a][b]
    zero, one = ((1, -1), (-1, -1)), ((1, 1), (1, -1))
    M = [[0] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            block = zero if C[i][j] == 0 else tuple(tuple(C[i][j] * x for x in r) for r in one)
            for di in range(2):
                for dj in range(2):
                    M[2 * i + di][2 * j + dj] = block[di][dj]
    return _pack(M)


def _pack(M):
    return [sum(1 << j for j, x in enumerate(row) if x == -1) for row in M]


def symmetric_circulants(n):
    """All symmetric circulant +-1 first rows of odd order n with leading entry 1, by row sum."""
    half = (n - 1) // 2
    by_sum = {}
    for bits in range(1 << half):
        row = [1] * n
        for j in range(1, half + 1):
            if bits >> (j - 1) & 1:
                row[j] = row[n - j] = -1
        paf = tuple(sum(row[i] * row[(i + t) % n] for i in range(n)) for t in range(1, half + 1))
        by_sum.setdefault(sum(row), []).append((row, paf))
    return by_sum


def williamson_quadruple(n):
    """First rows of symmetric circulants A, B, C, D with A^2 + B^2 + C^2 + D^2 = 4n I, or None."""
    by_sum = symmetric_circulants(n)
    sums = sorted(by_sum, key=lambda r: (abs(r), r))
    for ra in sums:
        for rb in sums:
            for rc in sums:
                rest = 4 * n - ra * ra - rb * rb - rc * rc
                rd = next((r for r in sums if r * r == rest), None)
                if rd is None or not (abs(ra), abs(rb)) <= (abs(rc), abs(rd)):
                    continue
                table = {}
                for A, pa in by_sum[ra]:
                    for B, pb in by_sum[rb]:
                        table.setdefault(tuple(x + y for x, y in zip(pa, pb)), (A, B))
                for C, pc in by_sum[rc]:
                    for D, pd in by_sum[rd]:
                        hit = table.get(tuple(-(x + y) for x, y in zip(pc, pd)))
                        if hit:
                            return hit[0], hit[1], C, D
    return None


def _circulant(seq):
    v = len(seq)
    return [[seq[(j - i) % v] for j in range(v)] for i in range(v)]


def _transpose(M):
    return [list(col) for col in zip(*M)]


def _reverse_rows(M):
    return [row[::-1] for row in M]


def _neg(M):
    return [[-x for x in row] for row in M]


def propus_matrix(A, B, C, D):
    """Symmetric Hadamard matrix from the Balonin–Seberry GP array.

    A, B, C, D are circulant ±1 blocks with A symmetric, B = C, and
    AA^T + BB^T + CC^T + DD^T = 4v I. R is the exchange matrix.
    """
    def R(M):
        return _reverse_rows(M)
    def TR(M):
        return R(_transpose(M))
    blocks = [
        [A, R(B), R(C), R(D)],
        [R(C), TR(D), _neg(A), _neg(TR(B))],
        [R(B), _neg(A), _neg(TR(D)), TR(C)],
        [R(D), _neg(TR(C)), TR(B), _neg(A)],
    ]
    v = len(A)
    rows = []
    for bi in range(4):
        for i in range(v):
            row = []
            for bj in range(4):
                row.extend(blocks[bi][bj][i])
            rows.append(row)
    return rows


def sequence_from_support(v, support):
    """±1 sequence of length v with −1 exactly on the support. Positions are in Z_v."""
    seq = [1] * v
    for i in support:
        if not 0 <= i < v or seq[i] == -1:
            raise ValueError(f"bad support index {i} for length {v}")
        seq[i] = -1
    return seq


def circulant_from_support(v, support):
    return _circulant(sequence_from_support(v, support))


# Propus supplementary difference sets. A position list is the set of −1 entries.
# Sources: Di Matteo–Đoković–Kotsireas, arXiv:1503.04226 (v = 29, 43) and
# Đoković–Kotsireas, arXiv:1708.05098 (v = 39). Each quadruple is one published
# example, not a search. Plugged in as [A, B, C, D] with C = B.
PROPUS = {
    29: (
        (0, 4, 5, 6, 7, 9, 13, 16, 20, 22, 23, 24, 25),
        (0, 1, 2, 5, 6, 8, 11, 12, 14, 16, 22),
        (0, 1, 2, 5, 6, 8, 11, 12, 14, 16, 22),
        (0, 1, 2, 3, 5, 8, 10, 13, 14, 15, 18, 22, 25),
    ),
    39: (
        (0, 2, 4, 7, 8, 12, 13, 18, 19, 20, 21, 26, 27, 31, 32, 35, 37),
        (0, 1, 2, 3, 10, 14, 17, 18, 19, 21, 24, 26, 27, 30, 32, 36, 37),
        (0, 1, 2, 3, 10, 14, 17, 18, 19, 21, 24, 26, 27, 30, 32, 36, 37),
        (0, 1, 2, 3, 4, 5, 9, 11, 12, 15, 26, 29, 31, 33, 36),
    ),
    43: None,  # filled below: B = C = Paley residues, A and D from the paper
}


def paley_residues(p):
    return tuple(sorted({(x * x) % p for x in range(1, p)}))


def propus_blocks(v):
    if v == 43:
        D = (0, 1, 3, 4, 5, 8, 12, 13, 14, 18, 19, 20, 21, 23, 26, 27, 29, 30, 32, 34, 36)
        A = (0, 1, 2, 4, 8, 11, 16, 21, 22, 27, 32, 35, 39, 41, 42)
        B = paley_residues(43)
        supports = (A, B, B, D)
    else:
        supports = PROPUS[v]
    return [circulant_from_support(v, s) for s in supports]


def propus(v):
    """Hadamard matrix of order 4v from a published propus quadruple, packed as bit rows."""
    return _pack(propus_matrix(*propus_blocks(v)))


def williamson(n):
    """Hadamard matrix of order 4n from the Williamson array, or None."""
    quad = williamson_quadruple(n)
    if quad is None:
        return None
    circ = [[[row[(j - i) % n] for j in range(n)] for i in range(n)] for row in quad]
    A, B, C, D = circ
    neg = lambda X: [[-v for v in r] for r in X]
    blocks = [[A, B, C, D], [neg(B), A, neg(D), C], [neg(C), D, A, neg(B)], [neg(D), neg(C), B, A]]
    M = [sum((blk[i] for blk in brow), []) for brow in blocks for i in range(n)]
    return _pack(M)


def kron(A, B):
    nb, full = len(B), (1 << len(B)) - 1
    rows = []
    for ra in A:
        for rb in B:
            r = 0
            for j in range(len(A)):
                r |= (rb ^ full if ra >> j & 1 else rb) << (j * nb)
            rows.append(r)
    return rows


def recipes(limit, williamson_max=0):
    """Map order -> recipe tuple, preferring the simplest construction."""
    base = {1: ("sylvester", 0), 2: ("sylvester", 1)}
    for q in range(3, limit):
        pk = prime_power(q)
        if not pk or pk[0] == 2:
            continue
        if q % 4 == 3 and q + 1 <= limit:
            base.setdefault(q + 1, ("paley1", q))
        if q % 4 == 1 and 2 * (q + 1) <= limit:
            base.setdefault(2 * (q + 1), ("paley2", q))
    k = 2
    while 1 << k <= limit:
        base.setdefault(1 << k, ("sylvester", k))
        k += 1
    def close(found):
        changed = True
        while changed:
            changed = False
            for a in sorted(found):
                for b in sorted(found):
                    if 1 < a <= b and a * b <= limit and a * b not in found:
                        found[a * b] = ("kron", a, b)
                        changed = True
        return found
    found = close(dict(base))
    for n in range(3, williamson_max + 1, 2):  # Williamson only where the cheaper methods leave a gap
        if 4 * n <= limit and 4 * n not in found and _williamson_cached(n) is not None:
            found[4 * n] = ("williamson", n)
            found = close(found)
    for v in (29, 39, 43):  # published propus quadruples: orders 116, 156, 172
        if 4 * v <= limit and 4 * v not in found:
            found[4 * v] = ("propus", v)
            found = close(found)
    return found


_WILLIAMSON = {}


def _williamson_cached(n):
    if n not in _WILLIAMSON:
        _WILLIAMSON[n] = williamson(n)
    return _WILLIAMSON[n]


def build(order, plan, cache):
    if order in cache:
        return cache[order]
    kind = plan[order]
    if kind[0] == "sylvester":
        rows = sylvester(kind[1])
    elif kind[0] == "paley1":
        rows = paley1(kind[1])
    elif kind[0] == "paley2":
        rows = paley2(kind[1])
    elif kind[0] == "williamson":
        rows = _williamson_cached(kind[1])
    elif kind[0] == "propus":
        rows = propus(kind[1])
    else:
        rows = kron(build(kind[1], plan, cache), build(kind[2], plan, cache))
    cache[order] = rows
    return rows


def search(params):
    limit = params["limit"]
    plan = recipes(limit, params.get("williamson_max", 0))
    cache, matrices = {}, {}
    for order in sorted(plan):
        if order % 4 == 0:
            matrices[str(order)] = build(order, plan, cache)
    targets = list(range(4, limit + 1, 4))
    gaps = [n for n in targets if str(n) not in matrices]
    return {
        "holds": True,
        "summary": {
            "limit": limit,
            "constructed_orders": len(matrices),
            "orders_divisible_by_4": len(targets),
            "engine_gaps": gaps,
            "recipes": {str(n): "/".join(map(str, plan[n])) for n in sorted(plan) if n % 4 == 0},
            "matrices_sha256": digest(matrices),
        },
        "certificate": {"matrices": matrices},
    }


def check(params, result):
    matrices = result["certificate"]["matrices"]
    for key, rows in matrices.items():
        n = int(key)
        require(n % 4 == 0 and n <= params["limit"] and len(rows) == n,
                f"order {n}: wrong size or not a multiple of four")
        require(all(0 <= r < (1 << n) for r in rows), f"order {n}: row out of range")
        half = n // 2
        for i in range(n):
            ri = rows[i]
            for j in range(i + 1, n):
                require(bin(ri ^ rows[j]).count("1") == half,
                        f"order {n}: rows {i} and {j} are not orthogonal")
    targets = set(range(4, params["limit"] + 1, 4))
    require(sorted(targets - {int(k) for k in matrices}) == result["summary"]["engine_gaps"],
            "engine gap list inconsistent with certificate")
    require(result["summary"]["matrices_sha256"] == digest(matrices), "summary hash mismatch")
