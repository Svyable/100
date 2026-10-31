"""M041 - Plane Jacobian conjecture: exhaustive low-degree maps with explicit polynomial inverses.

Statement covered (finite): every map F = (x + f, y + g) with f, g in Z[x, y] having only terms of
total degree 2..d, all coefficients in [-c, c], whose Jacobian determinant is the constant 1, has an
explicit polynomial inverse G with F(G(u,v)) = (u,v) and G(F(x,y)) = (x,y).

Search side: layer-by-layer exact coefficient pruning (the degree-m part of J-1 only depends on the
homogeneous layers of degree <= m+1), then the inverse by fixed-point iteration in Z[u,v].
Check side: a different algorithm. Completeness by brute force over the whole coefficient box using
integer evaluation on a unisolvent triangular grid (a polynomial of total degree <= D vanishes iff it
vanishes on all lattice points u, v >= 0, u + v <= D); inverses by integer evaluation, not by
symbolic composition.
"""
from itertools import product

from .core import digest, require
from .polyalg import compose, grid, jacobian_minus_one, monomials, pdeg, peval

PROBE = {
    "id": "jacobian",
    "problem_id": "M041",
    "title": "Plane Jacobian maps (x+f, y+g) of low degree: exhaustive census with explicit inverses",
    "engines": ["polynomial_algebra"],
    "frontier": ("Known: true for degree <= 2 (Wang 1980) and for maps of degree <= 100 (Moh 1983); the "
                 "conjecture is open in general, even in two variables. This range reproduces known "
                 "mathematics only."),
    "levels": {"smoke": {"max_degree": 2, "bound": 2}, "deep": {"max_degree": 3, "bound": 1}},
}

MAX_ITER = 64


def _all_monomials(d):
    return [m for k in range(2, d + 1) for m in monomials(k)]


def scope(params):
    d, c = params["max_degree"], params["bound"]
    total = (2 * c + 1) ** (2 * len(_all_monomials(d)))
    return (f"Every map (x+f, y+g) with f, g of total degree 2..{d}, coefficients in [-{c}, {c}] and "
            f"constant Jacobian 1 has an explicit polynomial inverse (complete census of all "
            f"{total:,} candidate maps).")


def _poly(monos, coeffs):
    return {m: c for m, c in zip(monos, coeffs) if c}


def _enc(p):
    return sorted([i, j, c] for (i, j), c in p.items())


def _dec(rows):
    return {(i, j): c for i, j, c in rows}


def _inverse(f, g):
    """Fixed-point iteration G <- (u - f(G), v - g(G)); returns (a, b) with F(G) = id, or None."""
    a, b = {(1, 0): 1}, {(0, 1): 1}
    for _ in range(MAX_ITER):
        na, nb = {(1, 0): 1}, {(0, 1): 1}
        for target, poly in ((na, compose(f, a, b)), (nb, compose(g, a, b))):
            for m, c in poly.items():
                target[m] = target.get(m, 0) - c
        na = {m: c for m, c in na.items() if c}
        nb = {m: c for m, c in nb.items() if c}
        if na == a and nb == b:
            return a, b
        a, b = na, nb
    return None


def search(params):
    d, c = params["max_degree"], params["bound"]
    layers = {k: monomials(k) for k in range(2, d + 1)}
    values = range(-c, c + 1)
    found = []

    def extend(k, f, g):
        if k > d:
            if not jacobian_minus_one(f, g):
                found.append((f, g))
            return
        mk = layers[k]
        for coeffs in product(values, repeat=2 * len(mk)):
            f2, g2 = dict(f), dict(g)
            f2.update(_poly(mk, coeffs[:len(mk)]))
            g2.update(_poly(mk, coeffs[len(mk):]))
            low = jacobian_minus_one(f2, g2)
            if all(sum(m) != k - 1 for m in low):
                extend(k + 1, f2, g2)

    extend(2, {}, {})
    entries = []
    for f, g in found:
        inv = _inverse(f, g)
        if inv is None:
            # Not a counterexample: the iteration merely failed to stabilise. check() refuses it.
            return {"holds": False, "summary": {"max_degree": d, "bound": c},
                    "certificate": {"counterexample": {"f": _enc(f), "g": _enc(g)}}}
        entries.append({"f": _enc(f), "g": _enc(g), "inverse": [_enc(inv[0]), _enc(inv[1])]})
    entries.sort(key=lambda e: (e["f"], e["g"]))
    nontrivial = [e for e in entries if e["f"] or e["g"]]
    degrees = [max(pdeg(_dec(e["inverse"][0])), pdeg(_dec(e["inverse"][1]))) for e in nontrivial]
    return {
        "holds": True,
        "summary": {
            "max_degree": d, "bound": c,
            "candidates": (2 * c + 1) ** (2 * len(_all_monomials(d))),
            "constant_jacobian_maps": len(entries),
            "nontrivial_maps": len(nontrivial),
            "max_inverse_degree": max(degrees, default=0),
            "maps_sha256": digest(entries),
        },
        "certificate": {"maps": entries},
    }


def check(params, result):
    d, c = params["max_degree"], params["bound"]
    require(result["holds"],
            "search reported a constant-Jacobian map without an iterated inverse; that is not a "
            "certified counterexample (non-invertibility is not proved), so it is rejected")
    entries = result["certificate"]["maps"]
    listed = {(tuple(map(tuple, e["f"])), tuple(map(tuple, e["g"]))) for e in entries}
    require(len(listed) == len(entries), "duplicate map in certificate")
    require(listed == _brute_force(d, c), "certificate census differs from brute-force census")
    for e in entries:
        f, g = _dec(e["f"]), _dec(e["g"])
        a, b = _dec(e["inverse"][0]), _dec(e["inverse"][1])
        bound = max(pdeg(f), pdeg(g), 1) * max(pdeg(a), pdeg(b), 1) + 1
        for u, v in grid(bound):
            x, y = peval(a, u, v), peval(b, u, v)
            require(x + peval(f, x, y) == u and y + peval(g, x, y) == v, "F(G(u,v)) != (u,v)")
        for x, y in grid(bound):
            u, v = x + peval(f, x, y), y + peval(g, x, y)
            require(peval(a, u, v) == x and peval(b, u, v) == y, "G(F(x,y)) != (x,y)")
    s = result["summary"]
    require(s["constant_jacobian_maps"] == len(entries)
            and s["nontrivial_maps"] == sum(1 for e in entries if e["f"] or e["g"])
            and s["maps_sha256"] == digest(entries), "summary does not match certificate")


def _brute_force(d, c):
    """All (f, g) in the box with J = 1, decided by evaluating J on a unisolvent grid only."""
    monos = _all_monomials(d)
    pts = grid(2 * (d - 1))
    n = len(pts)
    values = range(-c, c + 1)
    dx = [[i * x ** (i - 1) * y ** j if i else 0 for x, y in pts] for i, j in monos]
    dy = [[j * x ** i * y ** (j - 1) if j else 0 for x, y in pts] for i, j in monos]
    vecs = []
    for coeffs in product(values, repeat=len(monos)):
        nz = [(co, k) for k, co in enumerate(coeffs) if co]
        vx = [sum(co * dx[k][p] for co, k in nz) for p in range(n)]
        vy = [sum(co * dy[k][p] for co, k in nz) for p in range(n)]
        vecs.append((coeffs, vx, vy))
    res = set()
    for cf, fxv, fyv in vecs:
        for cg, gxv, gyv in vecs:
            if all((1 + fxv[p]) * (1 + gyv[p]) - fyv[p] * gxv[p] == 1 for p in range(n)):
                res.add((tuple(sorted((i, j, k) for (i, j), k in zip(monos, cf) if k)),
                         tuple(sorted((i, j, k) for (i, j), k in zip(monos, cg) if k))))
    return res
