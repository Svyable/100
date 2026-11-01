"""Proved quadratic identities for three arithmetic progressions of 4/n.

Every positive integer n ≡ 25, 73, or 97 (mod 120) has an explicit three-term
Egyptian fraction for 4/n. These classes sit inside the hard progression
n ≡ 1 (mod 24). The classes n ≡ 1 and n ≡ 49 (mod 120) are not claimed: both
are coprime to 120 and are squares modulo 120, which is the situation in which
Mordell showed one polynomial identity cannot cover the whole class. This is
not a proof of the Erdős–Straus conjecture and not a claim of priority.
"""
from math import lcm

from probes.core import require

MINE = {
    "id": "straus_identities",
    "problem_id": "M019",
    "title": "Proved Erdős–Straus identities for three classes mod 120",
    "engines": ["primes"],
    "frontier": ("Polynomial identities of this shape are classical (Mordell, Diophantine Equations, "
                 "1967, pp. 287–290). A complete covering system is impossible. The expansions below "
                 "are checked directly and leave n ≡ 1 and n ≡ 49 (mod 120) open."),
    "levels": {"smoke": {}},
}

# 4/n = 1/x + 1/y + 1/z with x = (n+r)/4, y = n(n+r)/s, z = n(n+r)/t and s+t = 4r.
IDENTITIES = (
    {"modulus": 120, "residue": 97, "r": 3, "s": 2, "t": 10},
    {"modulus": 120, "residue": 73, "r": 7, "s": 8, "t": 20},
    {"modulus": 120, "residue": 25, "r": 15, "s": 20, "t": 40},
)
UNCOVERED = (1, 49)


def scope(params):
    del params
    return ("Every positive integer n ≡ 25, 73, or 97 (mod 120) satisfies "
            "4/n = 1/x + 1/y + 1/z for explicit quadratic denominators. "
            "n ≡ 1 and n ≡ 49 (mod 120) are not covered.")


def _family(spec):
    return {key: spec[key] for key in ("modulus", "residue", "r", "s", "t")}


def _integrality(spec):
    modulus, residue, r, s, t = (spec[k] for k in ("modulus", "residue", "r", "s", "t"))
    step = lcm(4, s, t)
    require(1 <= s <= t and s + t == 4 * r, "s and t must be positive and sum to 4r")
    require(r % 4 == 3, "r must be 3 mod 4")
    require(modulus % step == 0 and (residue + r) % step == 0,
            "denominators are not integral on this progression")
    require(residue % 24 == 1, "the class must lie in n ≡ 1 (mod 24)")
    gcd_square_note(residue, modulus)
    return step


def gcd_square_note(residue, modulus):
    """25 mod 120 is a square but not coprime to 120, so Mordell's primitive-class ban does not apply."""
    from math import gcd
    if gcd(residue, modulus) == 1:
        squares = {pow(i, 2, modulus) for i in range(modulus)}
        require(residue not in squares, f"{residue} mod {modulus} is a primitive square class")
    return True


def _triple(spec, k):
    n = spec["modulus"] * k + spec["residue"]
    gap = n + spec["r"]
    require(gap % 4 == 0 and (n * gap) % spec["s"] == 0 and (n * gap) % spec["t"] == 0,
            f"non-integral denominator at k={k}")
    x, y, z = gap // 4, n * gap // spec["s"], n * gap // spec["t"]
    require(min(n, x, y, z) > 0, f"non-positive value at k={k}")
    return n, x, y, z


def _closed_coefficients(spec):
    """Expand 4xyz - n(xy + yz + zx) from the closed forms of x, y, z. No generic convolution."""
    modulus, residue, r, s, t = (spec[k] for k in ("modulus", "residue", "r", "s", "t"))
    # n = a + m k, gap = b + m k, x = gap/4, y = n*gap/s, z = n*gap/t.
    a, m, b = residue, modulus, residue + r
    require(m % 4 == 0 and b % 4 == 0 and m % s == 0 and b % s == 0 and m % t == 0 and b % t == 0,
            "closed forms are not integral")
    # y = (a + m k)(b + m k)/s = (a b + (a+b) m k + m^2 k^2)/s
    def quad(divisor):
        c0, c1, c2 = a * b, (a + b) * m, m * m
        require(c0 % divisor == 0 and c1 % divisor == 0 and c2 % divisor == 0, "quadratic split")
        return [c0 // divisor, c1 // divisor, c2 // divisor]

    x = [b // 4, m // 4]                 # degree 1
    y, z = quad(s), quad(t)              # degree 2
    # Multiply by distributing each monomial. Result degree <= 5.
    def term(coeff, degree, into):
        into[degree] = into.get(degree, 0) + coeff

    left, right = {}, {}
    # 4 x y z
    for i, cx in enumerate(x):
        for j, cy in enumerate(y):
            for k, cz in enumerate(z):
                term(4 * cx * cy * cz, i + j + k, left)
    # n (xy + yz + zx)
    def add_product(p, q, scale, into):
        for i, cp in enumerate(p):
            for j, cq in enumerate(q):
                # times n = a + m k, so degrees i+j and i+j+1
                term(scale * cp * cq * a, i + j, into)
                term(scale * cp * cq * m, i + j + 1, into)

    add_product(x, y, 1, right)
    add_product(y, z, 1, right)
    add_product(z, x, 1, right)
    width = max(max(left), max(right)) + 1
    return [left.get(i, 0) - right.get(i, 0) for i in range(width)]


def _summary():
    families = [_family(spec) for spec in IDENTITIES]
    covered = {item["residue"] for item in families}
    require(covered.isdisjoint(UNCOVERED), "an open square class was marked proved")
    require(covered | set(UNCOVERED) == {1, 25, 49, 73, 97},
            "the five classes of n ≡ 1 (mod 24) inside mod 120 must be partitioned")
    for spec in IDENTITIES:
        _integrality(spec)
    return {
        "families": families,
        "uncovered_mod_120": list(UNCOVERED),
    }


def search(params):
    del params
    summary = _summary()
    for spec in IDENTITIES:
        for k in range(6):
            n, x, y, z = _triple(spec, k)
            require(4 * x * y * z == n * (x * y + y * z + z * x), f"spot check failed at k={k}")
    return {"holds": True, "summary": summary, "certificate": summary}


def check(params, result):
    del params
    summary = _summary()
    require(result["summary"] == summary and result["certificate"] == summary,
            "identity certificate does not match the registered families")
    for spec in IDENTITIES:
        coeffs = _closed_coefficients(spec)
        require(len(coeffs) <= 6 and all(c == 0 for c in coeffs),
                f"polynomial for residue {spec['residue']} is not identically zero")
        # The same six integer points, recomputed here, are the roots of that polynomial.
        for k in range(6):
            n, x, y, z = _triple(spec, k)
            require(4 * x * y * z == n * (x * y + y * z + z * x), f"root check failed at k={k}")
