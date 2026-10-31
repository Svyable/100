"""M080 - Rota's basis conjecture over small finite fields.

For n bases B_1..B_n of GF(p)^n, find an n x n grid whose row i is B_i (in
some order) and whose columns are all bases. GL(n,p) acts transitively on
ordered bases and preserves the property, so B_1 may be fixed to the standard
basis in standard order. Search enumerates every multiset {B_2..B_n}; the
certificate stores, per instance, one byte-coded choice of row orders. The
check re-derives the basis count from |GL(n,p)|/n!, re-verifies each listed
basis, replays every instance in the same canonical order and recomputes all
column determinants.
"""
from itertools import combinations, combinations_with_replacement, permutations, product
from math import factorial, prod

from .core import digest, require

PROBE = {
    "id": "rota",
    "problem_id": "M080",
    "title": "Rota's basis conjecture: exhaustive grids over GF(p)^n",
    "engines": ["finite_fields", "symmetry_reduction"],
    "frontier": ("Known: true for every matroid of rank <= 3 (Chan 1995) and other special cases; "
                 "open in general. These cases are reproductions only."),
    "levels": {"smoke": {"cases": [[2, 2], [3, 2], [5, 2], [7, 2], [2, 3]]},
               "deep": {"cases": [[2, 2], [3, 2], [5, 2], [7, 2], [2, 3], [3, 3]]}},
}


def scope(params):
    cases = ", ".join(f"GF({p})^{n}" for p, n in params["cases"])
    return f"Every choice of n bases of {cases} admits a Rota grid (B_1 fixed by GL-transitivity)."


def _rank(vectors, p):
    rows = [list(v) for v in vectors]
    r = 0
    for c in range(len(rows[0])):
        piv = next((i for i in range(r, len(rows)) if rows[i][c] % p), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = pow(rows[r][c], p - 2, p)
        rows[r] = [x * inv % p for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] % p:
                f = rows[i][c]
                rows[i] = [(x - f * y) % p for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def bases(p, n):
    vectors = [v for v in product(range(p), repeat=n) if any(v)]
    return [b for b in combinations(vectors, n) if _rank(b, p) == n]


def _standard(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def search(params):
    out, holds = {}, True
    for p, n in params["cases"]:
        B = bases(p, n)
        independent = {frozenset(b) for b in B}
        perms = list(permutations(range(n)))
        codes = list(product(range(len(perms)), repeat=n - 1))
        require(len(codes) <= 256, "row-order code must fit in one byte")
        std = _standard(n)
        found = bytearray()
        counter = None
        for others in combinations_with_replacement(range(len(B)), n - 1):
            rows = [B[i] for i in others]
            for code_index, code in enumerate(codes):
                ordered = [tuple(rows[r][k] for k in perms[c]) for r, c in enumerate(code)]
                if all(frozenset(col) in independent and len(set(col)) == n
                       for col in zip(std, *ordered)):
                    found.append(code_index)
                    break
            else:
                holds, counter = False, [list(std)] + [list(map(list, r)) for r in rows]
                break
        out[f"{p}^{n}"] = {"p": p, "n": n, "bases": [list(map(list, b)) for b in B],
                           "orders": found.hex(), "instances": len(found)}
        if counter:
            out[f"{p}^{n}"]["counterexample"] = counter
            break
    return {
        "holds": holds,
        "summary": {k: {"bases": len(v["bases"]), "instances": v["instances"]} for k, v in out.items()}
                   | {"certificate_sha256": digest(out)},
        "certificate": out,
    }


def _det(m, p):
    n = len(m)
    if n == 1:
        return m[0][0] % p
    return sum((-1) ** j * m[0][j] * _det([row[:j] + row[j + 1:] for row in m[1:]], p)
               for j in range(n)) % p


def check(params, result):
    require(result["holds"], "a Rota counterexample would need independent proof that no grid exists")
    cert = result["certificate"]
    for p, n in params["cases"]:
        case = cert[f"{p}^{n}"]
        B = [tuple(tuple(v) for v in b) for b in case["bases"]]
        nb = prod(p ** n - p ** i for i in range(n)) // factorial(n)
        require(len(B) == nb == len({frozenset(b) for b in B}), f"GF({p})^{n}: expected {nb} distinct bases")
        require(all(_det([list(v) for v in b], p) for b in B), f"GF({p})^{n}: listed set is not a basis")
        perms = list(permutations(range(n)))
        codes = list(product(range(len(perms)), repeat=n - 1))
        orders = bytes.fromhex(case["orders"])
        instances = list(combinations_with_replacement(range(nb), n - 1))
        require(len(orders) == len(instances) == case["instances"],
                f"GF({p})^{n}: expected {len(instances)} instances")
        std = _standard(n)
        cache = {}
        for others, code_index in zip(instances, orders):
            require(code_index < len(codes), "row-order code out of range")
            code = codes[code_index]
            ordered = [tuple(B[i][k] for k in perms[c]) for i, c in zip(others, code)]
            for col in zip(std, *ordered):
                if col not in cache:
                    cache[col] = _det([list(v) for v in col], p)
                require(cache[col] != 0, f"GF({p})^{n}: a column is not a basis for {others}")
    require(result["summary"]["certificate_sha256"] == digest(cert), "certificate hash mismatch")
