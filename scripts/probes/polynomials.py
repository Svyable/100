"""Exact bivariate polynomial algebra over Q, plus lattice solving of linear systems.

Polynomials are dicts {(i, j): coefficient} for x^i y^j with nonzero
coefficients (ints or Fractions). Used for Jacobians, composition and
inverse construction for plane polynomial maps.
"""
from fractions import Fraction
from itertools import product


def clean(p):
    return {k: v for k, v in p.items() if v != 0}


def add(p, q, s=1):
    out = dict(p)
    for k, v in q.items():
        out[k] = out.get(k, 0) + s * v
    return clean(out)


def mul(p, q):
    out = {}
    for (a, b), u in p.items():
        for (c, d), v in q.items():
            out[(a + c, b + d)] = out.get((a + c, b + d), 0) + u * v
    return clean(out)


def scale(p, s):
    return clean({k: s * v for k, v in p.items()})


def dx(p):
    return clean({(i - 1, j): i * v for (i, j), v in p.items() if i})


def dy(p):
    return clean({(i, j - 1): j * v for (i, j), v in p.items() if j})


def jacobian(f, g):
    return add(mul(dx(f), dy(g)), mul(dy(f), dx(g)), -1)


def degree(p):
    return max((i + j for i, j in p), default=-1)


def monomials(d, constant=True):
    return [(i, k - i) for k in range(0 if constant else 1, d + 1) for i in range(k, -1, -1)]


def powers_table(f, g, d):
    """{(i, j): f^i g^j} for i + j <= d."""
    fp, gp = [{(0, 0): 1}], [{(0, 0): 1}]
    for _ in range(d):
        fp.append(mul(fp[-1], f))
        gp.append(mul(gp[-1], g))
    return {(i, j): mul(fp[i], gp[j]) for i, j in monomials(d)}


def compose(p, f, g, table=None):
    """p(f(x, y), g(x, y))."""
    table = table or powers_table(f, g, degree(p))
    out = {}
    for k, c in p.items():
        out = add(out, scale(table[k], c))
    return out


def solve_linear(columns, target):
    """Exact solution c of sum_k c_k columns[k] = target (polynomial dicts), or None."""
    keys = sorted({m for col in columns for m in col} | set(target))
    rows = [[Fraction(col.get(m, 0)) for col in columns] + [Fraction(target.get(m, 0))] for m in keys]
    n = len(columns)
    piv_cols, r = [], 0
    for c in range(n):
        piv = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        pv = rows[r][c]
        rows[r] = [v / pv for v in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                f = rows[i][c]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        piv_cols.append(c)
        r += 1
    if any(row[-1] != 0 for row in rows[r:]):
        return None
    sol = [Fraction(0)] * n
    for i, c in enumerate(piv_cols):
        sol[c] = rows[i][-1]
    return sol


def lattice_kernel(matrix, values):
    """All integer vectors b with entries in ``values`` and matrix @ b = 0 (exact RREF)."""
    m = [[Fraction(v) for v in row] for row in matrix]
    n = len(m[0]) if m else 0
    piv_cols, r = [], 0
    for c in range(n):
        piv = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        pv = m[r][c]
        m[r] = [v / pv for v in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        piv_cols.append(c)
        r += 1
    free = [c for c in range(n) if c not in piv_cols]
    allowed = set(values)
    out = []
    for choice in product(values, repeat=len(free)):
        b = [0] * n
        for c, v in zip(free, choice):
            b[c] = v
        ok = True
        for i, c in enumerate(piv_cols):
            v = -sum(m[i][fc] * b[fc] for fc in free)
            if v.denominator != 1 or int(v) not in allowed:
                ok = False
                break
            b[c] = int(v)
        if ok:
            out.append(b)
    return out
