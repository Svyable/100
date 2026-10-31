"""Finite fields GF(q) for prime powers q, with quadratic characters.

Elements are integers 0..q-1 encoding coefficient vectors base p
(c0 + c1*p + ... is c0 + c1*x + ...) modulo a monic irreducible polynomial.
Shared by the Hadamard, projective-plane, MDS-arc, Ramsey and Rota probes.
"""
from functools import lru_cache


def smallest_prime_factor(n):
    if n % 2 == 0:
        return 2
    f = 3
    while f * f <= n:
        if n % f == 0:
            return f
        f += 2
    return n


def prime_power(q):
    """Return (p, k) with q == p**k, or None."""
    if type(q) is not int or q < 2:
        return None
    p = smallest_prime_factor(q)
    k, m = 0, q
    while m % p == 0:
        m //= p
        k += 1
    return (p, k) if m == 1 else None


def _poly_mod(a, m, p):
    """Remainder of polynomial a modulo monic m (lowest degree first)."""
    a = list(a)
    dm = len(m) - 1
    while len(a) - 1 >= dm and any(a):
        if a[-1] % p == 0:
            a.pop()
            continue
        c = a[-1] % p
        shift = len(a) - 1 - dm
        for i, coeff in enumerate(m):
            a[shift + i] = (a[shift + i] - c * coeff) % p
        a.pop()
    while a and a[-1] % p == 0:
        a.pop()
    return [x % p for x in a]


def _monic_polys(degree, p):
    for code in range(p ** degree):
        coeffs = []
        for _ in range(degree):
            coeffs.append(code % p)
            code //= p
        yield coeffs + [1]


def is_irreducible(m, p):
    degree = len(m) - 1
    if degree < 1 or m[-1] != 1:
        return False
    for d in range(1, degree // 2 + 1):
        for f in _monic_polys(d, p):
            if not _poly_mod(m, f, p):
                return False
    return True


def first_irreducible(p, k):
    for m in _monic_polys(k, p):
        if m[0] != 0 and is_irreducible(m, p):
            return m
    raise ArithmeticError("no irreducible polynomial found")


class GF:
    def __init__(self, q):
        pk = prime_power(q)
        if pk is None:
            raise ValueError(f"GF({q}) does not exist: q must be a prime power")
        self.q, (self.p, self.k) = q, pk
        if self.k == 1:
            self.modulus = [0, 1]
            self._add = self._mul = None
        else:
            self.modulus = first_irreducible(self.p, self.k)
            self._build_tables()
        squares = {self.mul(x, x) for x in range(1, q)}
        self.chi = [0] + [1 if x in squares else -1 for x in range(1, q)]

    def _digits(self, a):
        out = []
        for _ in range(self.k):
            out.append(a % self.p)
            a //= self.p
        return out

    def _encode(self, coeffs):
        coeffs = list(coeffs) + [0] * (self.k - len(coeffs))
        value = 0
        for c in reversed(coeffs[:self.k]):
            value = value * self.p + c
        return value

    def _build_tables(self):
        q, p = self.q, self.p
        digits = [self._digits(a) for a in range(q)]
        self._add = [[self._encode([(x + y) % p for x, y in zip(digits[a], digits[b])])
                      for b in range(q)] for a in range(q)]
        mul = [[0] * q for _ in range(q)]
        for a in range(q):
            for b in range(a, q):
                prod = [0] * (2 * self.k - 1)
                for i, x in enumerate(digits[a]):
                    if x:
                        for j, y in enumerate(digits[b]):
                            prod[i + j] = (prod[i + j] + x * y) % p
                mul[a][b] = mul[b][a] = self._encode(_poly_mod(prod, self.modulus, p))
        self._mul = mul

    def add(self, a, b):
        return (a + b) % self.q if self._add is None else self._add[a][b]

    def mul(self, a, b):
        return (a * b) % self.q if self._mul is None else self._mul[a][b]

    def neg(self, a):
        if self._add is None:
            return (-a) % self.q
        return self._encode([(-d) % self.p for d in self._digits(a)])

    def sub(self, a, b):
        return self.add(a, self.neg(b))

    def inv(self, a):
        if a == 0:
            raise ZeroDivisionError("0 has no inverse")
        if self._mul is None:
            return pow(a, self.q - 2, self.q)
        return next(b for b in range(1, self.q) if self._mul[a][b] == 1)


@lru_cache(maxsize=None)
def field(q):
    return GF(q)


def projective_points(F, dim=3):
    """Normalised representatives (first nonzero coordinate equal to 1)."""
    points = []
    for lead in range(dim):
        free = dim - lead - 1
        for code in range(F.q ** free):
            tail = []
            for _ in range(free):
                tail.append(code % F.q)
                code //= F.q
            points.append(tuple([0] * lead + [1] + tail))
    return points
