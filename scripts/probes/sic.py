"""M092 - Zauner/SIC: exact SIC-POVMs in dimensions 2 and 3.

d = 2: four Bloch vectors s/sqrt(3) of a regular tetrahedron; for qubit pure
states tr(P_a P_b) = (1 + n_a.n_b)/2, so all overlaps equal 1/3 = 1/(d+1).
d = 3: the Weyl-Heisenberg orbit of every fiducial in the alphabet
{0, +-1, +-w, +-w^2}^3 (w a primitive cube root of unity) is searched in exact
Z[w] arithmetic; the check recomputes every Gram entry independently.
"""
from fractions import Fraction
from itertools import product

from .core import digest, require
from .cyclotomic import Cyclotomic

PROBE = {
    "id": "sic",
    "problem_id": "M092",
    "title": "Exact SIC-POVMs in d = 2 (tetrahedron) and d = 3 (Weyl-Heisenberg in Z[w])",
    "engines": ["cyclotomic"],
    "frontier": ("Known: exact SICs are known in many dimensions and numerical ones far beyond; "
                 "no construction for every d. d = 2, 3 are classical (Zauner 1999, Renes et al. 2004)."),
    "levels": {"smoke": {"coefficient_bound": 0}, "deep": {"coefficient_bound": 1}},
}

R = Cyclotomic(3)


def _alphabet_text(bound):
    return ("{0, +-1, +-w, +-w^2}" if bound == 0 else
            "{a + b*w : a, b in [-%d, %d]}" % (bound, bound))


def scope(params):
    return ("d=2: 4 exact equiangular qubit states with overlap 1/3; d=3: every Weyl-Heisenberg "
            f"fiducial with entries in {_alphabet_text(params['coefficient_bound'])} found and its "
            "9 states certified with pairwise squared overlap 1/4.")


def _alphabet(bound):
    """bound 0: zero and the six units of Z[w]; bound b > 0: all a + b*w with |a|, |b| <= b."""
    if bound == 0:
        vals = [R.const(0)]
        for k in range(3):
            vals += [R.zeta(k), R.neg(R.zeta(k))]
        return vals
    rng = range(-bound, bound + 1)
    return [(a, b, 0) for a in rng for b in rng]


def wh_orbit(psi):
    """D_{a,b} psi = X^a Z^b psi with X|j> = |j+1>, Z|j> = w^j |j>."""
    out = []
    for a in range(3):
        for b in range(3):
            v = [None] * 3
            for j in range(3):
                v[(j + a) % 3] = R.mul(R.zeta(b * j), psi[j])
            out.append(v)
    return out


def inner(u, v):
    total = R.const(0)
    for x, y in zip(u, v):
        total = R.add(total, R.mul(R.conj(x), y))
    return total


def is_fiducial(psi):
    vecs = wh_orbit(psi)
    norm = R.as_integer(inner(psi, psi))
    if not norm:
        return False
    for i in range(9):
        for j in range(i + 1, 9):
            z = inner(vecs[i], vecs[j])
            if R.as_integer(R.mul(z, R.conj(z))) * 4 != norm * norm:
                return False
    return True


def search(params):
    tetra = [[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]]
    fiducials = []
    for psi in product(_alphabet(params["coefficient_bound"]), repeat=3):
        if is_fiducial(list(psi)):
            fiducials.append([list(x) for x in psi])
    return {
        "holds": bool(fiducials),
        "summary": {"d2_overlap": "1/3", "d3_fiducials_in_alphabet": len(fiducials),
                    "d3_overlap": "1/4", "certificate_sha256": digest([tetra, fiducials])},
        "certificate": {"d2_bloch_times_sqrt3": tetra, "d3_fiducials": fiducials},
    }


def _independent_overlaps_d3(psi):
    """Recompute using explicit complex numbers in exact form a + b*w with w^2 = -1 - w."""
    def red(c):  # c is a length-3 tuple over basis 1, w, w^2
        return (c[0] - c[2], c[1] - c[2])
    def mul(x, y):  # (a + b w)(c + d w) = ac + (ad + bc) w + bd w^2, w^2 = -1 - w
        a, b = x
        c, d = y
        return (a * c - b * d, a * d + b * c - b * d)
    def conj(x):  # conj(a + b w) = a + b w^2 = (a - b) - b w
        return (x[0] - x[1], -x[1])
    def add(x, y):
        return (x[0] + y[0], x[1] + y[1])
    w = [(1, 0), (0, 1), (-1, -1)]
    p = [red(x) for x in psi]
    vecs = []
    for a in range(3):
        for b in range(3):
            v = [None] * 3
            for j in range(3):
                v[(j + a) % 3] = mul(w[(b * j) % 3], p[j])
            vecs.append(v)
    def ip(u, v):
        t = (0, 0)
        for x, y in zip(u, v):
            t = add(t, mul(conj(x), y))
        return t
    n = ip(p, p)
    require(n[1] == 0 and n[0] > 0, "fiducial norm must be a positive integer")
    out = set()
    for i in range(9):
        for j in range(9):
            z = ip(vecs[i], vecs[j])
            m = mul(z, conj(z))
            require(m[1] == 0, "squared overlap must be rational")
            out.add((i == j, Fraction(m[0], n[0] * n[0])))
    return out


def check(params, result):
    cert = result["certificate"]
    tetra = cert["d2_bloch_times_sqrt3"]
    require(len(tetra) == 4 and all(sum(x * x for x in s) == 3 for s in tetra),
            "d=2: Bloch vectors must have length sqrt(3) before scaling")
    for i in range(4):
        for j in range(i + 1, 4):
            dot = Fraction(sum(a * b for a, b in zip(tetra[i], tetra[j])), 3)
            require((1 + dot) / 2 == Fraction(1, 3), "d=2: overlap is not 1/(d+1)")
    require(cert["d3_fiducials"], "d=3: no fiducial certified")
    for psi in cert["d3_fiducials"]:
        require(_independent_overlaps_d3([tuple(x) for x in psi]) ==
                {(True, Fraction(1)), (False, Fraction(1, 4))}, f"d=3: {psi} is not a SIC fiducial")
    require(result["summary"]["d3_fiducials_in_alphabet"] == len(cert["d3_fiducials"]),
            "summary count mismatch")
