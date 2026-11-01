"""Rigorous interval arithmetic on fixed-point integers (no floating point).

A real interval [lo, hi] * 2^-p stores two Python integers and a precision p.
Every operation rounds outward, so the true value of any expression built
from these operations lies in the computed interval. Elementary functions
(exp, log, sin, cos, atan, sqrt, pi) are computed with extra guard bits from
truncated series *plus* an explicit enclosure of the truncation remainder, so
they are rigorous too. Python's float type is never used for a value that a
certificate depends on; floats appear only to pick reduction constants, which
affect speed and never correctness.

Complex intervals are rectangles (real interval, imaginary interval).
"""
from fractions import Fraction

GUARD = 32


def _ceil_shift(x, k):
    return -((-x) >> k)


def _coarse(q):
    """A short rational upper bound for a nonnegative Fraction (keeps tail bounds cheap)."""
    return Fraction(-((-q.numerator << 24) // q.denominator), 1 << 24)


class RI:
    """Closed real interval [lo/2^p, hi/2^p] with integer endpoints."""
    __slots__ = ("lo", "hi", "p")

    def __init__(self, lo, hi, p):
        if lo > hi:
            raise ValueError("empty interval")
        self.lo, self.hi, self.p = lo, hi, p

    # ------------------------------------------------------------ build
    @classmethod
    def exact(cls, value, p):
        """Tightest enclosure of an int or Fraction (or decimal string)."""
        q = Fraction(value)
        num = q.numerator << p
        return cls(num // q.denominator, -((-num) // q.denominator), p)

    @classmethod
    def hull(cls, a, b):
        a._same(b)
        return cls(min(a.lo, b.lo), max(a.hi, b.hi), a.p)

    def _same(self, other):
        if other.p != self.p:
            raise ValueError("mixed interval precisions")

    def _co(self, other):
        if isinstance(other, RI):
            self._same(other)
            return other
        return RI.exact(other, self.p)

    def with_precision(self, p):
        if p >= self.p:
            return RI(self.lo << (p - self.p), self.hi << (p - self.p), p)
        k = self.p - p
        return RI(self.lo >> k, _ceil_shift(self.hi, k), p)

    def widen(self, radius_units):
        """Add [-r, r] for r given in units of 2^-p (a nonnegative integer)."""
        return RI(self.lo - radius_units, self.hi + radius_units, self.p)

    # ------------------------------------------------------------ query
    def contains_zero(self):
        return self.lo <= 0 <= self.hi

    def positive(self):
        return self.lo > 0

    def negative(self):
        return self.hi < 0

    def sign(self):
        """+1, -1, or 0 when the sign is not certified."""
        return 1 if self.lo > 0 else (-1 if self.hi < 0 else 0)

    def contains(self, value):
        q = Fraction(value)
        return Fraction(self.lo, 1 << self.p) <= q <= Fraction(self.hi, 1 << self.p)

    def lower(self):
        return Fraction(self.lo, 1 << self.p)

    def upper(self):
        return Fraction(self.hi, 1 << self.p)

    def width(self):
        return Fraction(self.hi - self.lo, 1 << self.p)

    def mid(self):
        return (self.lo + self.hi) >> 1

    def rad(self):
        """Radius in units of 2^-p, rounded up."""
        return (self.hi - self.lo + 1) >> 1

    def __float__(self):
        return ((self.lo + self.hi) / 2) / (1 << self.p)

    def __repr__(self):
        return f"[{self.lo / (1 << self.p):.17g}, {self.hi / (1 << self.p):.17g}]"

    # ------------------------------------------------------- arithmetic
    def __add__(self, other):
        o = self._co(other)
        return RI(self.lo + o.lo, self.hi + o.hi, self.p)

    __radd__ = __add__

    def __neg__(self):
        return RI(-self.hi, -self.lo, self.p)

    def __sub__(self, other):
        o = self._co(other)
        return RI(self.lo - o.hi, self.hi - o.lo, self.p)

    def __rsub__(self, other):
        return self._co(other) - self

    def __mul__(self, other):
        if isinstance(other, int):
            a, b = self.lo * other, self.hi * other
            return RI(min(a, b), max(a, b), self.p)
        o = self._co(other)
        a, b, c, d = self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi
        p = self.p
        return RI(min(a, b, c, d) >> p, _ceil_shift(max(a, b, c, d), p), p)

    __rmul__ = __mul__

    def sqr(self):
        lo, hi, p = self.lo, self.hi, self.p
        if lo >= 0:
            return RI((lo * lo) >> p, _ceil_shift(hi * hi, p), p)
        if hi <= 0:
            return RI((hi * hi) >> p, _ceil_shift(lo * lo, p), p)
        return RI(0, _ceil_shift(max(lo * lo, hi * hi), p), p)

    def recip(self):
        if self.lo > 0:
            one = 1 << (2 * self.p)
            return RI(one // self.hi, -((-one) // self.lo), self.p)
        if self.hi < 0:
            return -((-self).recip())
        raise ZeroDivisionError("interval contains zero")

    def __truediv__(self, other):
        if isinstance(other, int):
            if other == 0:
                raise ZeroDivisionError
            if other < 0:
                return (-self) / (-other)
            return RI(self.lo // other, -((-self.hi) // other), self.p)
        return self * self._co(other).recip()

    def __rtruediv__(self, other):
        return self._co(other) * self.recip()

    def shift(self, k):
        """Multiply by 2^k (k may be negative; rounding is outward)."""
        if k >= 0:
            return RI(self.lo << k, self.hi << k, self.p)
        return RI(self.lo >> -k, _ceil_shift(self.hi, -k), self.p)

    def __abs__(self):
        if self.lo >= 0:
            return self
        if self.hi <= 0:
            return -self
        return RI(0, max(-self.lo, self.hi), self.p)

    def __pow__(self, k):
        if not isinstance(k, int) or k < 0:
            raise ValueError("only nonnegative integer powers")
        result, base = RI.exact(1, self.p), self
        while k:
            if k & 1:
                result = result * base
            k >>= 1
            if k:
                base = base.sqr()
        return result

    def sqrt(self):
        if self.hi < 0:
            raise ValueError("sqrt of a negative interval")
        lo = max(self.lo, 0)
        from math import isqrt
        p = self.p
        r_lo = isqrt(lo << p)
        x = self.hi << p
        r_hi = isqrt(x)
        if r_hi * r_hi < x:
            r_hi += 1
        return RI(r_lo, r_hi, p)


# ================================================================ constants

_CACHE = {}


def _atan_inv_series(m, p):
    """Enclosure of atan(1/m) for an integer m >= 2 at precision p."""
    one = RI.exact(1, p)
    x = one / m
    x2 = x.sqr()
    total, term, k = RI.exact(0, p), x, 0
    while True:
        total = total + (term / (2 * k + 1) if k % 2 == 0 else -(term / (2 * k + 1)))
        term = term * x2
        k += 1
        bound = term.upper() / (2 * k + 1)
        if bound < Fraction(1, 1 << (p + 2)):
            break
    # alternating series with decreasing terms: |remainder| <= next term
    return total.widen(_ceil_shift(term.hi, 0) // (2 * k + 1) + 2)


def pi(p):
    key = ("pi", p)
    if key not in _CACHE:
        q = p + GUARD
        val = _atan_inv_series(5, q) * 16 - _atan_inv_series(239, q) * 4
        _CACHE[key] = val.with_precision(p)
    return _CACHE[key]


def log2(p):
    key = ("log2", p)
    if key not in _CACHE:
        q = p + GUARD
        _CACHE[key] = (_atanh_series(RI.exact(Fraction(1, 3), q)) * 2).with_precision(p)
    return _CACHE[key]


def _atanh_series(z):
    """atanh(z) for an interval z with |z| <= 1/2: sum z^(2k+1)/(2k+1) plus tail."""
    p = z.p
    z2 = z.sqr()
    zmax = _coarse(abs(z).upper())
    if zmax > Fraction(1, 2):
        raise ValueError("atanh series needs |z| <= 1/2")
    total, term, k = RI.exact(0, p), z, 0
    eps = Fraction(1, 1 << (p + 2))
    while True:
        total = total + term / (2 * k + 1)
        term = term * z2
        k += 1
        tail = zmax ** (2 * k + 1) / ((2 * k + 1) * (1 - zmax * zmax))
        if tail < eps:
            break
    return total.widen(int(tail * (1 << p)) + 2)


# ========================================================= point functions

def _exp_point(X, p):
    """Enclosure of exp(X / 2^p) at precision p (X an integer)."""
    j = max(0, (abs(X) >> p).bit_length() + 2)
    q = p + GUARD + 2 * j
    y = RI(X << (q - p), X << (q - p), q).shift(-j)  # |y| <= 1/4
    ymax = _coarse(abs(y).upper())
    total, term, k = RI.exact(1, q), RI.exact(1, q), 0
    eps = Fraction(1, 1 << (q + 2))
    fact = 1
    while True:
        k += 1
        term = term * y / k
        total = total + term
        fact *= k + 1
        tail = 2 * ymax ** (k + 1) / fact  # |y| <= 1/2 so the tail is at most twice the next term
        if tail < eps:
            break
    total = total.widen(int(tail * (1 << q)) + 2)
    for _ in range(j):
        total = total.sqr()
    return total.with_precision(p)


def exp(x):
    """exp is increasing: enclose by the endpoint values."""
    if x.lo == x.hi:
        return _exp_point(x.lo, x.p)
    return RI(_exp_point(x.lo, x.p).lo, _exp_point(x.hi, x.p).hi, x.p)


def _log_point(X, p):
    if X <= 0:
        raise ValueError("log of a nonpositive number")
    q = p + GUARD
    b = X.bit_length()
    e = b - 1 - p  # X/2^p = m * 2^e with m = X / 2^(b-1) in [1, 2)
    m = RI(X, X, b - 1).with_precision(q) if b - 1 <= q else RI(X >> (b - 1 - q), _ceil_shift(X, b - 1 - q), q)
    if m.upper() > Fraction(17, 12):  # sqrt(2) < 17/12: use m/2 in [0.70, 1]
        m = m.shift(-1)
        e += 1
    z = (m - 1) / (m + 1)
    val = _atanh_series(z) * 2 + log2(q) * e
    return val.with_precision(p)


def log(x):
    """Natural log (increasing) of a positive interval."""
    if x.lo <= 0:
        raise ValueError("log of an interval that is not positive")
    if x.lo == x.hi:
        return _log_point(x.lo, x.p)
    return RI(_log_point(x.lo, x.p).lo, _log_point(x.hi, x.p).hi, x.p)


def _sincos_point(X, p):
    """Enclosures (sin, cos) of X / 2^p."""
    mag = (abs(X) >> p).bit_length()
    q = p + GUARD + mag
    x = RI(X << (q - p), X << (q - p), q)
    half = pi(q).shift(-1)
    k = round((X / (1 << p)) / 1.5707963267948966)  # any integer is valid; this one keeps |r| small
    r = x - half * k
    rmax = _coarse(abs(r).upper())
    if rmax > Fraction(1):
        raise ValueError("argument reduction failed")
    r2 = r.sqr()
    eps = Fraction(1, 1 << (q + 2))
    s_tot, c_tot = RI.exact(0, q), RI.exact(0, q)
    s_term, c_term = r, RI.exact(1, q)
    n = 0
    while True:
        s_tot = s_tot + s_term
        c_tot = c_tot + c_term
        s_term = -(s_term * r2 / ((2 * n + 2) * (2 * n + 3)))
        c_term = -(c_term * r2 / ((2 * n + 1) * (2 * n + 2)))
        n += 1
        if rmax ** (2 * n) / _fact(2 * n) < eps:
            break
    # Taylor remainder after the degree-(2n-1) / (2n-2) partial sums is at most |r|^(2n)/(2n)!.
    tail = int(rmax ** (2 * n) / _fact(2 * n) * (1 << q)) + 2
    s, c = s_tot.widen(tail), c_tot.widen(tail)
    s, c = {0: (s, c), 1: (c, -s), 2: (-s, -c), 3: (-c, s)}[k % 4]
    one = RI.exact(1, q)
    s, c = _clip(s, one), _clip(c, one)
    return s.with_precision(p), c.with_precision(p)


def _fact(n):
    out = 1
    for i in range(2, n + 1):
        out *= i
    return out


def _clip(v, one):
    return RI(max(v.lo, -one.hi), min(v.hi, one.hi), v.p)


def sincos(x):
    """(sin x, cos x) for an interval x: point value at the midpoint, widened by the radius (|f'| <= 1)."""
    s, c = _sincos_point(x.mid(), x.p)
    r = x.rad() + 1
    one = RI.exact(1, x.p)
    return _clip(s.widen(r), one), _clip(c.widen(r), one)


def _atan_point(X, p):
    """Enclosure of atan(X / 2^p)."""
    if X < 0:
        return -_atan_point(-X, p)
    q = p + GUARD
    x = RI(X, X, p).with_precision(q)
    if X == 0:
        return RI(0, 0, p)
    invert = x.lo > (1 << q)
    if invert:
        x = x.recip()
    one = RI.exact(1, q)
    for _ in range(2):  # atan(x) = 2 atan(x / (1 + sqrt(1 + x^2)))
        x = x / (one + (one + x.sqr()).sqrt())
    xmax = _coarse(abs(x).upper())
    x2 = x.sqr()
    total, term, k = RI.exact(0, q), x, 0
    eps = Fraction(1, 1 << (q + 2))
    while True:
        total = total + (term / (2 * k + 1) if k % 2 == 0 else -(term / (2 * k + 1)))
        term = term * x2
        k += 1
        tail = xmax ** (2 * k + 1) / (2 * k + 1)
        if tail < eps:
            break
    val = total.widen(int(tail * (1 << q)) + 2) * 4
    if invert:
        val = pi(q).shift(-1) - val
    return val.with_precision(p)


def atan(x):
    """atan is increasing: enclose by the endpoint values."""
    if x.lo == x.hi:
        return _atan_point(x.lo, x.p)
    return RI(_atan_point(x.lo, x.p).lo, _atan_point(x.hi, x.p).hi, x.p)


# ================================================================ complex

class CI:
    """Complex rectangle re + i*im with real-interval parts."""
    __slots__ = ("re", "im")

    def __init__(self, re, im):
        re._same(im)
        self.re, self.im = re, im

    @classmethod
    def exact(cls, re, im, p):
        return cls(RI.exact(re, p), RI.exact(im, p))

    @property
    def p(self):
        return self.re.p

    def __add__(self, o):
        if isinstance(o, CI):
            return CI(self.re + o.re, self.im + o.im)
        return CI(self.re + o, self.im)

    __radd__ = __add__

    def __sub__(self, o):
        if isinstance(o, CI):
            return CI(self.re - o.re, self.im - o.im)
        return CI(self.re - o, self.im)

    def __neg__(self):
        return CI(-self.re, -self.im)

    def __mul__(self, o):
        if isinstance(o, CI):
            return CI(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)
        return CI(self.re * o, self.im * o)

    __rmul__ = __mul__

    def conj(self):
        return CI(self.re, -self.im)

    def abs2(self):
        return self.re.sqr() + self.im.sqr()

    def abs_upper(self):
        return self.abs2().sqrt()

    def recip(self):
        d = self.abs2()
        return CI(self.re / d, -self.im / d)

    def __truediv__(self, o):
        if isinstance(o, CI):
            return self * o.recip()
        return CI(self.re / o, self.im / o)

    def contains_zero(self):
        return self.re.contains_zero() and self.im.contains_zero()

    def __repr__(self):
        return f"({self.re!r} + i{self.im!r})"


# Half-planes used for argument tracking. CENTER[k] is the direction (in units of pi/2) at the
# middle of the argument window that arg_in_window returns for half-plane k.
HALF_PLANES = {0: "Re>0", 1: "Im>0", 2: "Re<0", 3: "Im<0"}
CENTER = {0: 0, 1: 1, 2: 2, 3: -1}


def half_plane(z):
    """First quarter-turn k (0..3) such that the box z lies strictly in that open half-plane, else None."""
    if z.re.positive():
        return 0
    if z.im.positive():
        return 1
    if z.re.negative():
        return 2
    if z.im.negative():
        return 3
    return None


def in_half_plane(z, k):
    return {0: z.re.positive, 1: z.im.positive, 2: z.re.negative, 3: z.im.negative}[k]()


def arg_in_window(z, k):
    """Argument of every point of z in the open window of width pi centred at CENTER[k]*pi/2.

    z must lie in half-plane k. The windows are (-pi/2, pi/2), (0, pi), (pi/2, 3pi/2), (-pi, 0).
    """
    if not in_half_plane(z, k):
        raise ValueError("box not inside the declared half-plane")
    half = pi(z.p).shift(-1)
    if k == 0:
        return atan(z.im / z.re)
    if k == 1:
        return half - atan(z.re / z.im)
    if k == 2:
        return half * 2 + atan(z.im / z.re)
    return -half - atan(z.re / z.im)
