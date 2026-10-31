"""M084 - Matrix multiplication exponent: exact tensor-decomposition certificates.

A rank-r decomposition of the <n,n,n> matrix multiplication tensor proves
omega <= log_n(r). Search side builds Strassen's rank-7 <2,2,2> scheme and its
Kronecker powers; check side expands every term sparsely over Z and compares
with the matmul tensor coefficient by coefficient. Any external decomposition
(e.g. from a flip-graph or learned search) can be replayed with
``verify_decomposition``.
"""
from math import log

from .core import digest, require

PROBE = {
    "id": "strassen",
    "problem_id": "M084",
    "title": "Exact matrix-multiplication tensor decompositions (Strassen and Kronecker powers)",
    "engines": ["tensor_certificates"],
    "frontier": ("Known: omega <= log2(7) ~ 2.807 (Strassen 1969); the best published bounds are "
                 "below 2.372 via the laser method. rank<2,2,2> = 7 exactly (Winograd 1971)."),
    "levels": {"smoke": {"powers": [1, 2]}, "deep": {"powers": [1, 2, 3]}},
}

# Strassen: each term is (U, V, W) as dicts {(row, col): coeff} over A, B and C.
STRASSEN = [
    ({(0, 0): 1, (1, 1): 1}, {(0, 0): 1, (1, 1): 1}, {(0, 0): 1, (1, 1): 1}),
    ({(1, 0): 1, (1, 1): 1}, {(0, 0): 1}, {(1, 0): 1, (1, 1): -1}),
    ({(0, 0): 1}, {(0, 1): 1, (1, 1): -1}, {(0, 1): 1, (1, 1): 1}),
    ({(1, 1): 1}, {(1, 0): 1, (0, 0): -1}, {(0, 0): 1, (1, 0): 1}),
    ({(0, 0): 1, (0, 1): 1}, {(1, 1): 1}, {(0, 0): -1, (0, 1): 1}),
    ({(1, 0): 1, (0, 0): -1}, {(0, 0): 1, (0, 1): 1}, {(1, 1): 1}),
    ({(0, 1): 1, (1, 1): -1}, {(1, 0): 1, (1, 1): 1}, {(0, 0): 1}),
]


def scope(params):
    return ("Exact integer rank-7^k decompositions of the <2^k,2^k,2^k> matmul tensor for k in {"
            + ", ".join(map(str, params["powers"])) + "}, hence omega <= log2(7).")


def kron_terms(T1, n1, T2, n2):
    def k(a, b):
        return {(i1 * n2 + i2, j1 * n2 + j2): c1 * c2
                for (i1, j1), c1 in a.items() for (i2, j2), c2 in b.items()}
    return [(k(u1, u2), k(v1, v2), k(w1, w2)) for u1, v1, w1 in T1 for u2, v2, w2 in T2]


def power(k):
    terms, n = STRASSEN, 2
    for _ in range(k - 1):
        terms, n = kron_terms(terms, n, STRASSEN, 2), n * 2
    return n, terms


def search(params):
    out = {}
    for k in params["powers"]:
        n, terms = power(k)
        out[str(n)] = [[sorted([list(key), c] for key, c in part.items()) for part in t] for t in terms]
    return {
        "holds": True,
        "summary": {"ranks": {n: len(t) for n, t in out.items()},
                    "omega_upper_bound": round(log(7, 2), 6),
                    "decompositions_sha256": digest(out)},
        "certificate": {"decompositions": out},
    }


def verify_decomposition(n, terms):
    """Raise ProbeFailure unless sum_r U_r (x) V_r (x) W_r equals <n,n,n> exactly.

    Convention: C[i][k] = sum_r W_r[i][k] * (sum U_r[a][b] A[a][b]) * (sum V_r[c][d] B[c][d]).
    """
    acc = {}
    for U, V, W in terms:
        for (a, b), cu in U:
            for (c, d), cv in V:
                for (i, k), cw in W:
                    key = (a, b, c, d, i, k)
                    acc[key] = acc.get(key, 0) + cu * cv * cw
    target = {(i, j, j, k, i, k) for i in range(n) for j in range(n) for k in range(n)}
    for key, value in acc.items():
        require(all(0 <= x < n for x in key), f"<{n},{n},{n}>: index out of range {key}")
        require(value == (1 if key in target else 0), f"<{n},{n},{n}>: wrong coefficient at {key}")
    require(all(acc.get(t) == 1 for t in target), f"<{n},{n},{n}>: missing matmul coefficient")


def check(params, result):
    decs = result["certificate"]["decompositions"]
    require(sorted(map(int, decs)) == sorted(2 ** k for k in params["powers"]), "missing sizes")
    for key, terms in decs.items():
        n = int(key)
        require(len(terms) == 7 ** round(log(n, 2)), f"<{n},{n},{n}>: unexpected rank")
        verify_decomposition(n, [[[(tuple(i), c) for i, c in part] for part in t] for t in terms])
    require(result["summary"]["decompositions_sha256"] == digest(decs), "summary hash mismatch")
