"""M041 - Plane Jacobian conjecture on exhaustive classes of small integer maps.

Class(d, C): F = (f, g) with f, g of degree <= d, no constant term (translations
are harmless), all coefficients in C. For every F whose Jacobian determinant is a
nonzero constant, search builds an explicit polynomial inverse G with
deg G <= d: by Gabber's bound (deg F^-1 <= (deg F)^(n-1) for automorphisms of C^n),
an F with no such inverse would be a counterexample to the conjecture.

Search: since J(f, g) is linear in the coefficients of g, constant-Jacobian maps
are the lattice points of a kernel (exact RREF over Q). Inverses come from an
exact linear system. Check: completeness is re-derived from a *different*
linear system (evaluations of J on a grid, fraction-free integer elimination), and
every inverse is verified by composing both ways with independent dense arithmetic.
"""
from fractions import Fraction
from itertools import product
from math import gcd

from . import polynomials as P
from .core import digest, require

PROBE = {
    "id": "jacobian",
    "problem_id": "M041",
    "title": "Plane Jacobian conjecture on exhaustive classes of small integer polynomial maps",
    "engines": ["polynomial_algebra"],
    "frontier": ("Known: true for plane maps of degree <= 100 (Moh 1983) and in degree <= 2 in every "
                 "dimension (Wang 1980); open in general. Reproduction only."),
    "levels": {"smoke": {"degree": 2, "coefficients": [-1, 0, 1]},
               "deep": {"degree": 3, "coefficients": [-1, 0, 1]}},
}


def scope(params):
    return (f"Every plane map (f, g) with deg <= {params['degree']}, zero constant terms and coefficients in "
            f"{{{', '.join(map(str, params['coefficients']))}}} whose Jacobian is a nonzero constant has an "
            f"explicit polynomial inverse of degree <= {params['degree']}.")


def _poly(coeffs, mons):
    return {m: c for m, c in zip(mons, coeffs) if c}


def constant_jacobian_maps(d, values):
    mons = P.monomials(d, constant=False)
    basis_j = None
    found = []
    for a in product(values, repeat=len(mons)):
        f = _poly(a, mons)
        if not (f.get((1, 0)) or f.get((0, 1))):
            continue  # J(0,0) = f_x(0) g_y(0) - f_y(0) g_x(0) would vanish
        cols = [P.jacobian(f, {m: 1}) for m in mons]
        keys = sorted({k for c in cols for k in c if k != (0, 0)})
        matrix = [[c.get(k, 0) for c in cols] for k in keys]
        for b in (P.lattice_kernel(matrix, values) if keys else product(values, repeat=len(mons))):
            const = sum(bk * c.get((0, 0), 0) for bk, c in zip(b, cols))
            if const != 0:
                found.append((list(a), list(b), const))
    return mons, found


def inverse(f, g, d):
    table = P.powers_table(f, g, d)
    keys = P.monomials(d)
    columns = [table[k] for k in keys]
    p = P.solve_linear(columns, {(1, 0): 1})
    q = P.solve_linear(columns, {(0, 1): 1})
    if p is None or q is None:
        return None
    return ({k: v for k, v in zip(keys, p) if v}, {k: v for k, v in zip(keys, q) if v})


def _ser(p):
    return sorted([list(k), str(v)] for k, v in p.items())


def search(params):
    d, values = params["degree"], params["coefficients"]
    mons, maps = constant_jacobian_maps(d, values)
    rows, holds, counter = [], True, None
    for a, b, const in maps:
        f, g = _poly(a, mons), _poly(b, mons)
        inv = inverse(f, g, d)
        if inv is None:
            holds, counter = False, [a, b]
            break
        rows.append({"f": a, "g": b, "jacobian": const, "p": _ser(inv[0]), "q": _ser(inv[1])})
    return {
        "holds": holds,
        "summary": {"monomials": len(mons), "class_size": len(values) ** (2 * len(mons)),
                    "constant_jacobian_maps": len(maps),
                    "max_inverse_terms": max((len(r["p"]) + len(r["q"]) for r in rows), default=0),
                    "certificate_sha256": digest(rows)},
        "certificate": {"rows": rows, "counterexample": counter},
    }


# ---------------------------------------------------------------- check side

def _dense(p, size):
    out = [[Fraction(0)] * size for _ in range(size)]
    for (i, j), c in p.items():
        out[i][j] += Fraction(c)
    return out


def _dmul(a, b, size):
    """Dense product keeping every term of total degree < size (callers keep true degrees below it)."""
    out = [[Fraction(0)] * size for _ in range(size)]
    terms_b = [(k, l, b[k][l]) for k in range(size) for l in range(size) if b[k][l]]
    for i in range(size):
        for j in range(size - i):
            if a[i][j]:
                for k, l, v in terms_b:
                    if i + j + k + l < size:
                        out[i + k][j + l] += a[i][j] * v
    return out


def _dcompose(p, f, g, size):
    """Dense composition p(f, g), truncation-free because size exceeds the true degree."""
    out = [[Fraction(0)] * size for _ in range(size)]
    deg = max((i + j for (i, j) in p), default=0)
    fpow, gpow = [_dense({(0, 0): 1}, size)], [_dense({(0, 0): 1}, size)]
    for _ in range(deg):
        fpow.append(_dmul(fpow[-1], f, size))
        gpow.append(_dmul(gpow[-1], g, size))
    for (i, j), c in p.items():
        term = _dmul(fpow[i], gpow[j], size)
        for r in range(size):
            for s in range(size):
                out[r][s] += Fraction(c) * term[r][s]
    return out


def _identity_check(out, which, size):
    for r in range(size):
        for s in range(size):
            want = 1 if (r, s) == which else 0
            if out[r][s] != want:
                return False
    return True


def _value(p, x, y, ddx=0, ddy=0):
    """Integer value at (x, y) of p differentiated ddx times in x and ddy times in y (ddx, ddy <= 1)."""
    total = 0
    for (i, j), c in p.items():
        if i >= ddx and j >= ddy:
            total += c * (i if ddx else 1) * (j if ddy else 1) * x ** (i - ddx) * y ** (j - ddy)
    return total


def _bareiss_kernel(matrix, values):
    """Fraction-free integer elimination; enumerate kernel lattice points within ``values``."""
    m = [list(map(int, row)) for row in matrix]
    rows, cols = len(m), len(m[0])
    piv_cols, r = [], 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        for i in range(rows):
            if i != r and m[i][c]:
                m[i] = [m[r][c] * m[i][k] - m[i][c] * m[r][k] for k in range(cols)]
                g = 0
                for v in m[i]:
                    g = gcd(g, v)
                if g > 1:
                    m[i] = [v // g for v in m[i]]
        piv_cols.append(c)
        r += 1
    free = [c for c in range(cols) if c not in piv_cols]
    out = []
    for choice in product(sorted(values), repeat=len(free)):
        b = [0] * cols
        for c, v in zip(free, choice):
            b[c] = v
        ok = True
        for i, c in enumerate(piv_cols):
            num = -sum(m[i][fc] * b[fc] for fc in free)
            if num % m[i][c] or num // m[i][c] not in values:
                ok = False
                break
            b[c] = num // m[i][c]
        if ok:
            out.append(b)
    return out


def check(params, result):
    require(result["holds"], "a missing inverse needs an independent nonexistence proof before any claim")
    d, values = params["degree"], params["coefficients"]
    mons = P.monomials(d, constant=False)
    rows = result["certificate"]["rows"]
    claimed = {(tuple(r["f"]), tuple(r["g"])) for r in rows}
    require(len(claimed) == len(rows), "duplicate maps in certificate")
    # completeness via evaluation: J(f,g)(pt) - J(f,g)(0,0) = 0 on a (2d-1) x (2d-1) grid,
    # which forces the degree <= 2d-2 polynomial J(f,g) to be constant.
    grid = [(x, y) for x in range(2 * d - 1) for y in range(2 * d - 1)]
    mon_dx = [[_value({m: 1}, x, y, 1, 0) for x, y in grid] for m in mons]
    mon_dy = [[_value({m: 1}, x, y, 0, 1) for x, y in grid] for m in mons]
    found = set()
    for a in product(values, repeat=len(mons)):
        f = {m: c for m, c in zip(mons, a) if c}
        if not (f.get((1, 0)) or f.get((0, 1))):
            continue
        fx = [_value(f, x, y, 1, 0) for x, y in grid]
        fy = [_value(f, x, y, 0, 1) for x, y in grid]
        jac = [[fx[t] * mon_dy[k][t] - fy[t] * mon_dx[k][t] for t in range(len(grid))]
               for k in range(len(mons))]  # jac[k][t] = J(f, m_k) at grid point t; grid[0] = (0, 0)
        matrix = [[jac[k][t] - jac[k][0] for k in range(len(mons))] for t in range(1, len(grid))]
        for b in _bareiss_kernel(matrix, set(values)):
            if sum(bk * jac[k][0] for k, bk in enumerate(b)) != 0:
                found.add((tuple(a), tuple(b)))
    require(found == claimed, f"constant-Jacobian maps differ: {len(found)} found vs {len(claimed)} certified")
    size = d * d + 2
    for r in rows:
        f = {m: c for m, c in zip(mons, r["f"]) if c}
        g = {m: c for m, c in zip(mons, r["g"]) if c}
        p = {tuple(k): Fraction(v) for k, v in r["p"]}
        q = {tuple(k): Fraction(v) for k, v in r["q"]}
        require(max(i + j for i, j in list(p) + list(q)) <= d, "inverse exceeds Gabber degree bound")
        df, dg = _dense(f, size), _dense(g, size)
        require(_identity_check(_dcompose(p, df, dg, size), (1, 0), size) and
                _identity_check(_dcompose(q, df, dg, size), (0, 1), size), f"G o F != id for {r['f']}, {r['g']}")
        dp, dq = _dense(p, size), _dense(q, size)
        require(_identity_check(_dcompose(f, dp, dq, size), (1, 0), size) and
                _identity_check(_dcompose(g, dp, dq, size), (0, 1), size), f"F o G != id for {r['f']}, {r['g']}")
    require(result["summary"]["certificate_sha256"] == digest(rows), "certificate hash mismatch")
