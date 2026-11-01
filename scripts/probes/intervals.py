"""Directed fixed-point interval arithmetic.

Every real value is a closed interval of rationals with denominator ``SCALE``.
Operations round outward, so a result interval always contains the true image.
Complex values are axis-aligned rectangles. No floating-point rounding mode is
consulted: bounds are integer division with explicit floor and ceiling.
"""
from fractions import Fraction
from math import isqrt

SCALE = 10 ** 18
_PI_CACHE = None
_LOG2_CACHE = None


class Iv:
    """Closed real interval [lo, hi] in units of 1/SCALE."""

    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi):
        lo = int(lo)
        hi = int(hi)
        if lo > hi:
            raise ValueError(f"empty interval {(lo, hi)}")
        self.lo = lo
        self.hi = hi

    def width(self):
        return self.hi - self.lo

    def mid_float(self):
        return 0.5 * (self.lo + self.hi) / SCALE

    def contains_int(self, n):
        return self.lo <= n * SCALE <= self.hi

    def __repr__(self):
        return f"[{self.lo / SCALE:.12g}, {self.hi / SCALE:.12g}]"


class Cv:
    """Axis-aligned complex rectangle."""

    __slots__ = ("re", "im")

    def __init__(self, re, im):
        self.re = re
        self.im = im

    def contains_zero(self):
        return self.re.lo <= 0 <= self.re.hi and self.im.lo <= 0 <= self.im.hi

    def __repr__(self):
        return f"{self.re} + i{self.im}"


def _ceil_div(num, den):
    """ceil(num/den) for den > 0."""
    return -((-num) // den)


def iv_int(n):
    return Iv(n * SCALE, n * SCALE)


def iv_fraction(fr):
    fr = Fraction(fr)
    num = fr.numerator * SCALE
    den = fr.denominator
    return Iv(num // den, _ceil_div(num, den))


def iv_pow10(exp):
    """Exact 10^exp when it is a multiple of 1/SCALE."""
    if exp >= 0:
        return iv_int(10 ** exp)
    return iv_fraction(Fraction(1, 10 ** (-exp)))


def add(a, b):
    return Iv(a.lo + b.lo, a.hi + b.hi)


def sub(a, b):
    return Iv(a.lo - b.hi, a.hi - b.lo)


def neg(a):
    return Iv(-a.hi, -a.lo)


def _mul_corners(a, b):
    los, his = [], []
    for x in (a.lo, a.hi):
        for y in (b.lo, b.hi):
            prod = x * y
            los.append(prod // SCALE)
            his.append(_ceil_div(prod, SCALE))
    return min(los), max(his)


def mul(a, b):
    return Iv(*_mul_corners(a, b))


def mul_small(a, n):
    """Multiply by a small Python int."""
    if n < 0:
        return neg(mul_small(a, -n))
    if n == 0:
        return Iv(0, 0)
    return Iv(a.lo * n, a.hi * n)


def div_small(a, n):
    if n < 0:
        return neg(div_small(a, -n))
    if n == 0:
        raise ZeroDivisionError
    return Iv(a.lo // n, _ceil_div(a.hi, n))


def inv(a):
    if a.lo <= 0 <= a.hi:
        raise ZeroDivisionError("interval reciprocal crosses 0")
    # 1/x in fixed point is SCALE^2 / x_units.
    span = SCALE * SCALE
    if a.lo > 0:
        return Iv(span // a.hi, _ceil_div(span, a.lo))
    return Iv(span // a.lo, _ceil_div(span, a.hi))


def div(a, b):
    return mul(a, inv(b))


def abs_upper(a):
    return max(abs(a.lo), abs(a.hi))


def sqrt_iv(a):
    """Nonnegative square root. ``a`` must lie in [0, +∞)."""
    if a.lo < 0:
        raise ValueError("sqrt of an interval that meets negatives")
    def floor_sqrt(units):
        return isqrt(units * SCALE)
    def ceil_sqrt(units):
        root = isqrt(units * SCALE)
        if root * root < units * SCALE:
            root += 1
        return root
    return Iv(floor_sqrt(a.lo), ceil_sqrt(a.hi))


def hypot_lower(re, im):
    """Lower bound of sqrt(x^2+y^2) over the rectangle, in fixed-point units."""
    def axis(iv):
        if iv.lo > 0:
            return iv.lo
        if iv.hi < 0:
            return -iv.hi
        return 0
    dx, dy = axis(re), axis(im)
    # units(hypot) = sqrt(dx^2 + dy^2), since each coordinate is already scaled.
    return isqrt(dx * dx + dy * dy)


def hypot_upper(re, im):
    his = []
    for x in (re.lo, re.hi):
        for y in (im.lo, im.hi):
            sq = x * x + y * y
            root = isqrt(sq)
            if root * root < sq:
                root += 1
            his.append(root)
    return max(his)


def _pow_abs_upper(units, n):
    """ceil(|x|^n) in fixed point, x given as absolute fixed-point units."""
    acc = SCALE
    for _ in range(n):
        acc = _ceil_div(acc * units, SCALE)
    return acc


def _fact(n):
    out = 1
    for k in range(2, n + 1):
        out *= k
    return out


def _remainder_upper(x, n):
    """ceil(|x|^n / n!) in fixed point."""
    bound = _pow_abs_upper(abs_upper(x), n)
    return _ceil_div(bound, _fact(n))


def exp_iv(a):
    """Exponential, using monotonicity on the endpoints."""
    return Iv(_exp_lower(a.lo), _exp_upper(a.hi))


def _exp_series(x_units):
    """Outward enclosure of exp at one exact fixed-point endpoint.

    The running term bounds contain the true Taylor term, so their sum contains
    the truncated series. The geometric tail past the last term is added on.
    """
    term_lo = term_hi = SCALE
    total_lo = total_hi = SCALE
    last = 1
    for k in range(1, 120):
        num_lo = term_lo * x_units
        num_hi = term_hi * x_units
        prod_lo, prod_hi = (num_lo, num_hi) if num_lo <= num_hi else (num_hi, num_lo)
        den = k * SCALE
        term_lo = prod_lo // den
        term_hi = _ceil_div(prod_hi, den)
        total_lo += term_lo
        total_hi += term_hi
        last = k
        if max(abs(term_lo), abs(term_hi)) <= 2 and k > abs(x_units) // SCALE + 2:
            break
    # |tail| <= |next| / (1 - |x|/(k+1)) once k+1 > |x|. next ≈ |term| |x|/(k+1).
    ax = abs(x_units)
    if (last + 1) * SCALE <= ax:
        raise ValueError("exp series stopped before the terms decreased")
    next_abs = _ceil_div(max(abs(term_lo), abs(term_hi)) * ax, (last + 1) * SCALE)
    shrink = (last + 1) * SCALE - ax
    tail = _ceil_div(next_abs * SCALE, shrink) + 4
    return total_lo - tail, total_hi + tail


def _exp_lower(x_units):
    if x_units < 0:
        # exp(-x) = 1/exp(x). Positive series avoids cancellation.
        upper = _exp_upper(-x_units)
        if upper <= 0:
            raise ValueError("exp overflow")
        return (SCALE * SCALE) // upper
    return _exp_series(x_units)[0]


def _exp_upper(x_units):
    if x_units < 0:
        lower = _exp_lower(-x_units)
        if lower <= 0:
            raise ValueError("exp underflow")
        return _ceil_div(SCALE * SCALE, lower)
    return _exp_series(x_units)[1]


def _atan_unit(x):
    """atan on an interval strictly inside (-1, 1), via the integral remainder."""
    # atan x = sum_{n=0}^{N-1} (-1)^n x^{2n+1}/(2n+1) + R, |R| <= |x|^{2N+1}/(2N+1).
    if x.lo <= -SCALE or x.hi >= SCALE:
        raise ValueError("atan series requires |x| < 1")
    n_terms = 40
    power = x  # x^1
    total = Iv(0, 0)
    x2 = mul(x, x)
    for n in range(n_terms):
        term = div_small(power, 2 * n + 1)
        total = add(total, term if n % 2 == 0 else neg(term))
        power = mul(power, x2)
    rest = _ceil_div(_pow_abs_upper(abs_upper(x), 2 * n_terms + 1), 2 * n_terms + 1)
    return Iv(total.lo - rest, total.hi + rest)


def _atan_positive_units(units):
    """Outward enclosure of atan(units/SCALE) for units >= 0."""
    if units < 0:
        raise ValueError
    if units == 0:
        return Iv(0, 0)
    if units == SCALE:
        return div_small(pi(), 4)
    if units > SCALE:
        # atan(x) = π/2 - atan(1/x), and 0 < 1/x < 1.
        recip = Iv(SCALE * SCALE // units, _ceil_div(SCALE * SCALE, units))
        return sub(div_small(pi(), 2), _atan_unit(recip))
    return _atan_unit(Iv(units, units))


def atan_iv(a):
    """atan on any real interval. atan is increasing, so endpoints suffice."""
    if a.lo >= 0:
        lo = _atan_positive_units(a.lo).lo
        hi = _atan_positive_units(a.hi).hi
        return Iv(lo, hi)
    if a.hi <= 0:
        # atan(-x) = -atan(x): the lower endpoint is the more negative input.
        lo = -_atan_positive_units(-a.hi).hi
        hi = -_atan_positive_units(-a.lo).lo
        return Iv(lo, hi)
    return Iv(-_atan_positive_units(-a.lo).hi, _atan_positive_units(a.hi).hi)


def pi():
    global _PI_CACHE
    if _PI_CACHE is None:
        # Machin: pi = 16 atan(1/5) - 4 atan(1/239).
        fifth = iv_fraction(Fraction(1, 5))
        inv239 = iv_fraction(Fraction(1, 239))
        _PI_CACHE = sub(mul_small(_atan_unit(fifth), 16), mul_small(_atan_unit(inv239), 4))
    return _PI_CACHE


def two_pi():
    return mul_small(pi(), 2)


def log2():
    global _LOG2_CACHE
    if _LOG2_CACHE is None:
        # log 2 = 2 atanh(1/3) = 2 sum_{k=0}^∞ (1/3)^{2k+1}/(2k+1)
        # |R| after N terms <= (1/3)^{2N+1}/(2N+1) / (1 - 1/9) = (3/8) (1/3)^{2N+1}/(2N+1) * 3?
        # atanh u = sum u^{2k+1}/(2k+1), |R_N| <= u^{2N+1}/((2N+1)(1-u^2)).
        u = iv_fraction(Fraction(1, 3))
        n_terms = 40
        power = u
        total = Iv(0, 0)
        u2 = mul(u, u)
        for k in range(n_terms):
            total = add(total, div_small(power, 2 * k + 1))
            power = mul(power, u2)
        u_abs = abs_upper(u)
        tail_pow = _pow_abs_upper(u_abs, 2 * n_terms + 1)
        one_minus = SCALE - _ceil_div(u_abs * u_abs, SCALE)
        rest = _ceil_div(tail_pow * SCALE, (2 * n_terms + 1) * one_minus)
        atanh = Iv(total.lo - rest, total.hi + rest)
        _LOG2_CACHE = mul_small(atanh, 2)
    return _LOG2_CACHE


def log_iv(a):
    """Natural log on a positive interval."""
    if a.lo <= 0:
        raise ValueError("log of a non-positive interval")
    return Iv(_log_endpoint(a.lo, lower=True), _log_endpoint(a.hi, lower=False))


def _log_endpoint(units, lower):
    """log(units/SCALE) by writing the argument as m * 2^e with m in [1, 2)."""
    if units <= 0:
        raise ValueError("log of non-positive")
    # value = units/SCALE = m * 2^e with m in [1, 2).
    num, den = units, SCALE
    e = 0
    while num >= 2 * den:
        den *= 2
        e += 1
    while num < den:
        num *= 2
        e -= 1
    # Now m = num/den in [1, 2), but den may be large. Reduce by gcd-free shift:
    # m = num/den, log m = 2 atanh((m-1)/(m+1)).
    # (m-1)/(m+1) = (num-den)/(num+den).
    u = iv_fraction(Fraction(num - den, num + den))
    n_terms = 50
    power = u
    total = Iv(0, 0)
    u2 = mul(u, u)
    for k in range(n_terms):
        total = add(total, div_small(power, 2 * k + 1))
        power = mul(power, u2)
    u_abs = abs_upper(u)
    # |u| < 1/3 for m in [1, 2). |R| <= |u|^{2N+1} / ((2N+1) (1-u^2)).
    tail_pow = _pow_abs_upper(u_abs, 2 * n_terms + 1)
    one_minus = SCALE - _ceil_div(u_abs * u_abs, SCALE)
    if one_minus <= 0:
        raise ValueError("atanh tail bound failed")
    rest = _ceil_div(tail_pow * SCALE, (2 * n_terms + 1) * one_minus)
    atanh = Iv(total.lo - rest, total.hi + rest)
    main = add(mul_small(atanh, 2), mul_small(log2(), e))
    return main.lo if lower else main.hi


def _sin_cos(a):
    """sin and cos on an interval reduced into [-2π, 2π] approximately."""
    # Range-reduce by an integer multiple of 2π.
    half = (a.lo + a.hi) // 2
    tp = two_pi()
    tp_mid = (tp.lo + tp.hi) // 2
    k = int(round(half / tp_mid)) if tp_mid else 0
    reduced = sub(a, mul_small(tp, k))
    return _sin_series(reduced), _cos_series(reduced)


def _sin_series(x):
    n_terms = 22
    power = x
    total = Iv(0, 0)
    x2 = mul(x, x)
    for n in range(n_terms):
        term = div_small(power, _fact(2 * n + 1))
        total = add(total, term if n % 2 == 0 else neg(term))
        power = mul(power, x2)
    rest = _remainder_upper(x, 2 * n_terms + 1)
    return Iv(total.lo - rest, total.hi + rest)


def _cos_series(x):
    n_terms = 22
    power = iv_int(1)
    total = Iv(0, 0)
    x2 = mul(x, x)
    for n in range(n_terms):
        term = div_small(power, _fact(2 * n))
        total = add(total, term if n % 2 == 0 else neg(term))
        power = mul(power, x2)
    rest = _remainder_upper(x, 2 * n_terms)
    return Iv(total.lo - rest, total.hi + rest)


def sin_iv(a):
    return _sin_cos(a)[0]


def cos_iv(a):
    return _sin_cos(a)[1]


def cadd(a, b):
    return Cv(add(a.re, b.re), add(a.im, b.im))


def csub(a, b):
    return Cv(sub(a.re, b.re), sub(a.im, b.im))


def cmul(a, b):
    return Cv(
        sub(mul(a.re, b.re), mul(a.im, b.im)),
        add(mul(a.re, b.im), mul(a.im, b.re)),
    )


def cdiv(a, b):
    den = add(mul(b.re, b.re), mul(b.im, b.im))
    return Cv(
        div(add(mul(a.re, b.re), mul(a.im, b.im)), den),
        div(sub(mul(a.im, b.re), mul(a.re, b.im)), den),
    )


def cscale(a, iv):
    return Cv(mul(a.re, iv), mul(a.im, iv))


def cexp(a):
    """exp(x+iy) = exp(x) (cos y + i sin y)."""
    mag = exp_iv(a.re)
    s, c = _sin_cos(a.im)
    return Cv(mul(mag, c), mul(mag, s))


def atan2_iv(y, x):
    """Argument of one point-like or wide rectangle corner, as an interval."""
    if x.lo > 0:
        return atan_iv(div(y, x))
    pi_iv = pi()
    if x.hi < 0 and y.lo >= 0:
        return add(atan_iv(div(y, x)), pi_iv)
    if x.hi < 0 and y.hi <= 0:
        return sub(atan_iv(div(y, x)), pi_iv)
    if x.hi < 0:
        # Crosses the negative real direction: arg is not a short interval.
        raise ValueError("atan2 crosses the branch cut")
    # x interval contains 0.
    if y.lo > 0:
        return div_small(pi_iv, 2) if x.lo == 0 and x.hi == 0 else _atan2_wide(y, x)
    if y.hi < 0:
        return neg(div_small(pi_iv, 2)) if x.lo == 0 and x.hi == 0 else _atan2_wide(y, x)
    raise ValueError("atan2 of a rectangle containing 0")


def _atan2_wide(y, x):
    corners = []
    for xv in (x.lo, x.hi):
        for yv in (y.lo, y.hi):
            corners.append(atan2_iv(Iv(yv, yv), Iv(xv, xv)))
    return Iv(min(c.lo for c in corners), max(c.hi for c in corners))


def arg_arc(rect):
    """Smallest argument arc of a rectangle that does not contain 0.

    Returns an ``Iv`` of length < π, or None when 0 is inside or the rectangle
    subtends π or more (so the continuous argument is not unique).
    """
    if rect.contains_zero():
        return None
    corners = []
    try:
        for xv in (rect.re.lo, rect.re.hi):
            for yv in (rect.im.lo, rect.im.hi):
                corners.append(atan2_iv(Iv(yv, yv), Iv(xv, xv)))
    except ValueError:
        return None
    mids = [((c.lo + c.hi) // 2, i, c) for i, c in enumerate(corners)]
    mids.sort()
    n = len(mids)
    gaps = []
    for i in range(n - 1):
        gaps.append((mids[i + 1][0] - mids[i][0], i))
    gaps.append((mids[0][0] + two_pi().lo - mids[-1][0], n - 1))
    _gap, i = max(gaps)
    # Arc from the corner after the largest gap, forward to the corner before it.
    start_i = (i + 1) % n
    # Collect the corners on the complementary arc in order and read off bounds.
    ordered = []
    idx = start_i
    for _ in range(n):
        ordered.append(mids[idx][2])
        if idx == i:
            break
        idx = (idx + 1) % n
    # Express every selected corner on a single unwrapped branch starting near
    # the first midpoint.
    origin = mids[start_i][0]
    lo = None
    hi = None
    tp = two_pi()
    for corner in ordered:
        mid = (corner.lo + corner.hi) // 2
        shift = 0
        while mid - origin < -tp.hi // 2:
            mid += (tp.lo + tp.hi) // 2
            shift += 1
        while mid - origin > tp.hi // 2:
            mid -= (tp.lo + tp.hi) // 2
            shift -= 1
        lifted = add(corner, mul_small(tp, shift)) if shift else corner
        lo = lifted.lo if lo is None else min(lo, lifted.lo)
        hi = lifted.hi if hi is None else max(hi, lifted.hi)
    if lo is None or hi - lo >= pi().lo:
        return None
    return Iv(lo, hi)


def c_log(rect):
    """Principal log of a rectangle contained in the open right half-plane."""
    if rect.re.lo <= 0:
        raise ValueError("log branch requires positive real part")
    mod_sq = add(mul(rect.re, rect.re), mul(rect.im, rect.im))
    mod = sqrt_iv(mod_sq)
    arc = arg_arc(rect)
    if arc is None:
        raise ValueError("log branch requires a short argument arc")
    return Cv(log_iv(mod), arc)


def unique_integer(iv):
    """The unique integer in the interval, or None."""
    n_min = _ceil_div(iv.lo, SCALE)
    n_max = iv.hi // SCALE
    if n_min == n_max:
        return n_min
    return None
