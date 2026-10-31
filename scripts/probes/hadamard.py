"""M094 - Hadamard conjecture: exact Hadamard matrices for many orders 4k <= N.

Constructions (search side): Sylvester doubling, Paley I (q = 3 mod 4) and
Paley II (q = 1 mod 4) over GF(q) for prime powers q, closed under Kronecker
products. Check side: every row pair is verified orthogonal, i.e. H H^T = nI,
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
                 "Tayfeh-Rezaie 2005). Engine gaps below are NOT open cases."),
    "levels": {"smoke": {"limit": 128}, "deep": {"limit": 400}},
}


def scope(params):
    limit = params["limit"]
    built = sum(1 for n in recipes(limit) if n % 4 == 0)
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


def recipes(limit):
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
    found = dict(base)
    changed = True
    while changed:
        changed = False
        for a in sorted(found):
            for b in sorted(found):
                if 1 < a <= b and a * b <= limit and a * b not in found:
                    found[a * b] = ("kron", a, b)
                    changed = True
    return found


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
    else:
        rows = kron(build(kind[1], plan, cache), build(kind[2], plan, cache))
    cache[order] = rows
    return rows


def search(params):
    limit = params["limit"]
    plan = recipes(limit)
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
