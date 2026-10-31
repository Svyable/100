"""Exact arithmetic in the cyclotomic ring Z[zeta_m].

Elements are length-m integer tuples (coefficients of 1, z, ..., z^(m-1))
multiplied modulo z^m - 1; equality is tested modulo the cyclotomic
polynomial Phi_m, so all comparisons are exact (no floating point).
"""
from functools import lru_cache


def _poly_div_exact(num, den):
    num = list(num)
    out = [0] * (len(num) - len(den) + 1)
    for i in range(len(out) - 1, -1, -1):
        c = num[i + len(den) - 1] // den[-1]
        out[i] = c
        for j, d in enumerate(den):
            num[i + j] -= c * d
    if any(num):
        raise ArithmeticError("inexact polynomial division")
    return out


@lru_cache(maxsize=None)
def phi(m):
    """Coefficients of the m-th cyclotomic polynomial (lowest degree first)."""
    poly = [-1] + [0] * (m - 1) + [1]
    for d in range(1, m):
        if m % d == 0:
            poly = _poly_div_exact(poly, phi(d))
    return tuple(poly)


class Cyclotomic:
    def __init__(self, m):
        self.m = m
        self.phi = phi(m)

    def const(self, c):
        return (c,) + (0,) * (self.m - 1)

    def zeta(self, k):
        out = [0] * self.m
        out[k % self.m] = 1
        return tuple(out)

    def add(self, a, b):
        return tuple(x + y for x, y in zip(a, b))

    def neg(self, a):
        return tuple(-x for x in a)

    def mul(self, a, b):
        out = [0] * self.m
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    if y:
                        out[(i + j) % self.m] += x * y
        return tuple(out)

    def conj(self, a):
        """Complex conjugation: zeta -> zeta^-1."""
        out = [0] * self.m
        for i, x in enumerate(a):
            out[(-i) % self.m] += x
        return tuple(out)

    def reduce(self, a):
        """Canonical representative modulo Phi_m (degree < phi(m))."""
        rem = list(a)
        deg = len(self.phi) - 1
        for i in range(len(rem) - 1, deg - 1, -1):
            c = rem[i]
            if c:
                for j, d in enumerate(self.phi):
                    rem[i - deg + j] -= c * d
        return tuple(rem[:deg])

    def equal(self, a, b):
        return self.reduce(self.add(a, self.neg(b))) == (0,) * (len(self.phi) - 1)

    def as_integer(self, a):
        """Return the integer a represents, or None if it is not rational."""
        r = self.reduce(a)
        return r[0] if not any(r[1:]) else None
