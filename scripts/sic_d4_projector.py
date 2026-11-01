"""Exact d=4 Weyl-Heisenberg SIC projector replay (known 2017 construction).

Bengtsson, Foundations of Physics 47 (2017), DOI 10.1007/s10701-017-0078-3,
equations (3), (5), (7), (8). Rational arithmetic in
Q(sqrt(2), sqrt(5), t, i), t^2=-(1+sqrt(5)); no numerical tolerances.
This is a known finite reproduction, not a d>=5 construction or independent review.
"""
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import json

# Assertions are the certificate gate; never silently skip them under -O.
if not __debug__:
    raise RuntimeError("exact SIC verification requires assertions enabled")

N = 16
ZERO = (Fraction(0),) * N
ONE = (Fraction(1),) + (Fraction(0),) * (N - 1)


def scalar(x):
    return (Fraction(x),) + ZERO[1:]


def gen(bit):
    v = list(ZERO)
    v[bit] = Fraction(1)
    return tuple(v)


A, B, T, I = (gen(1), gen(2), gen(4), gen(8))


def add(x, y):
    return tuple(a + b for a, b in zip(x, y))


def neg(x):
    return tuple(-a for a in x)


def sub(x, y):
    return add(x, neg(y))


def scale(x, q):
    return tuple(a * Fraction(q) for a in x)


@lru_cache(None)
def monomial_product(i, j):
    """Reduce the four quadratic relations in the fixed ordered basis."""
    ea = (i & 1) + (j & 1)
    eb = ((i >> 1) & 1) + ((j >> 1) & 1)
    et = ((i >> 2) & 1) + ((j >> 2) & 1)
    ei = ((i >> 3) & 1) + ((j >> 3) & 1)
    c = (2 ** (ea // 2)) * (5 ** (eb // 2)) * (-1) ** (ei // 2)
    base = (ea % 2) | ((eb % 2) << 1) | ((et % 2) << 2) | ((ei % 2) << 3)
    if et < 2:
        return ((base, c),)
    # t^2 = -(1 + b), and b^2 = 5.
    if base & 2:
        return ((base, -c), (base ^ 2, -5 * c))
    return ((base, -c), (base | 2, -c))


def mul(x, y):
    out = [Fraction(0)] * N
    for i, a in enumerate(x):
        if a:
            for j, b in enumerate(y):
                if b:
                    for k, c in monomial_product(i, j):
                        out[k] += a * b * c
    return tuple(out)


def conj(x):
    # sqrt(2), sqrt(5) real; t=i*sqrt(1+sqrt(5)), i imaginary.
    return tuple((-v if ((k & 4) != 0) != ((k & 8) != 0) else v)
                 for k, v in enumerate(x))


def power(x, n):
    z = ONE
    for _ in range(n):
        z = mul(z, x)
    return z


def matzero():
    return [[ZERO for _ in range(4)] for _ in range(4)]


def matmul(x, y):
    return [[sum_alg(mul(x[r][k], y[k][c]) for k in range(4))
             for c in range(4)] for r in range(4)]


def sum_alg(xs):
    z = ZERO
    for x in xs:
        z = add(z, x)
    return z


def adj(x):
    return [[conj(x[c][r]) for c in range(4)] for r in range(4)]


def trace(x):
    return sum_alg(x[k][k] for k in range(4))


def displacement(a, b, tau, w):
    """D_ab = tau^(ab) X^a Z^b, indices 0..3, omega=i."""
    out = matzero()
    for j in range(4):
        out[(j + a) % 4][j] = mul(power(tau, a * b), power(w, b * j))
    return out


def phase_table(u):
    ui = conj(u)
    return [
        [None, u, neg(ONE), ui],
        [u, ui, neg(ui), ui],
        [neg(ONE), neg(u), neg(ONE), ui],
        [ui, u, u, u],
    ]


def reconstruct(phases):
    tau = scale(mul(add(ONE, I), A), Fraction(-1, 2))
    ds = {(a, b): displacement(a, b, tau, I)
          for a in range(4) for b in range(4)}
    p = matzero()
    for a in range(4):
        for b in range(4):
            # c_00=1, c_ab=phase_ab/sqrt(5) for nonidentity.
            c = ONE if (a, b) == (0, 0) else scale(mul(phases[a][b], B), Fraction(1, 5))
            d = adj(ds[(a, b)])
            for r in range(4):
                for s in range(4):
                    p[r][s] = add(p[r][s], scale(mul(c, d[r][s]), Fraction(1, 4)))
    return p, ds


def orbit(p, ds):
    return [matmul(matmul(d, p), adj(d)) for d in ds.values()]


def verify(phases=None):
    u = add(scale(mul(sub(B, ONE), A), Fraction(1, 4)), scale(T, Fraction(1, 2)))
    assert mul(u, conj(u)) == ONE, "published phase is not a unit"
    if phases is None:
        phases = phase_table(u)
    p, ds = reconstruct(phases)
    assert trace(p) == ONE, "projector trace"
    assert adj(p) == p, "projector is not Hermitian"
    assert matmul(p, p) == p, "projector is not idempotent"
    # Path 1: direct 16x16 pairwise projector Gram trace.
    ps = orbit(p, ds)
    for k, q in enumerate(ps):
        assert adj(q) == q and trace(q) == ONE, ("orbit projector", k)
        assert matmul(q, q) == q, ("orbit idempotence", k)
        for j, r in enumerate(ps):
            target = ONE if j == k else scalar(Fraction(1, 5))
            assert trace(matmul(q, r)) == target, ("pairwise Gram", k, j)
    # Path 2: independent displacement-character sum from the 16
    # Weyl coefficients, without constructing orbit projectors.
    # For nonzero displacement (a,b), trace(P D_ab P D_ab^*) =
    # (1/4) sum_{r,s} |c_rs|^2 i^(b*r-a*s).
    for a in range(4):
        for b in range(4):
            z = ZERO
            for r in range(4):
                for s in range(4):
                    c = ONE if (r, s) == (0, 0) else scale(mul(phases[r][s], B), Fraction(1, 5))
                    z = add(z, mul(mul(c, conj(c)), power(I, (b * r - a * s) % 4)))
            z = scale(z, Fraction(1, 4))
            assert z == (ONE if (a, b) == (0, 0) else scalar(Fraction(1, 5))), ("character overlap", a, b)
    cert = {
        "dimension": 4, "projectors": 16, "off_diagonal_pairs": 120,
        "exact_off_diagonal_overlap": "1/5",
        "field_relations": ["a^2=2", "b^2=5", "t^2=-(1+b)", "i^2=-1"],
        "source": "https://doi.org/10.1007/s10701-017-0078-3",
        "source_equations": [3, 5, 7, 8],
        "scope": "published d=4 WH-covariant SIC projector; no d>=5 or novelty claim",
    }
    cert["sha256"] = sha256(json.dumps(cert, sort_keys=True).encode()).hexdigest()
    return cert


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
