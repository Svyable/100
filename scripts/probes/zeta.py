"""Rigorous values of zeta, Dirichlet L(s, χ₄), and zero-counting contours.

Intervals come from ``intervals.py``. Two classical bounds are used as stated,
not refitted:

* Euler–Maclaurin for the Hurwitz zeta function. With ``σ = Re s`` and
  ``σ + 2M > 1``, ``s ≠ 1``,

      ζ(s, a) = Σ_{k=0}^{N-1} (a+k)^{-s} + (a+N)^{1-s}/(s-1) + 1/(2(a+N)^s)
                + Σ_{j=1}^{M} B_{2j}/(2j)! (s)_{2j-1} (a+N)^{-(s+2j-1)} + R,

  and ``|R| ≤ 4 |(s)_{2M}| (2π)^{-2M} (a+N)^{1-σ-2M} / (σ+2M-1)``.
  The factor 4 is ``|B_{2M}| = 2 (2M)! ζ(2M) / (2π)^{2M} < 4 (2M)! / (2π)^{2M}``,
  since ``ζ(2M) < 2``, together with ``|B_{2M}({x})| ≤ |B_{2M}|``.

* Stirling's series for ``log Γ(z)``, truncated after ``n`` terms, with the
  Stieltjes remainder

      |R_n(z)| ≤ |B_{2n+2}| / ((2n+2)(2n+1) |z|^{2n+1}) · sec^{2n+2}(φ/2),

  valid for ``|φ| < π``, ``φ = arg z`` (Nemes, arXiv:1310.0166, records this
  bound of Stieltjes). The series itself is the standard one:
  ``(z-1/2) log z - z + log(2π)/2 + Σ_{k=1}^{n} B_{2k}/(2k(2k-1) z^{2k-1})``.

The zero count ``N(T)`` is the exact Riemann–von Mangoldt formula: ``θ(T)/π + 1``
plus ``(1/π)`` times the continuous argument of ``ζ`` along the segment from
``2`` to ``2+iT`` to ``1/2+iT``, started at ``arg ζ(2) = 0``. A sign change of
the Hardy function ``Z`` is a critical-line zero of odd multiplicity. When the
two counts agree, every non-trivial zero with imaginary part in ``(0, T]`` is
simple and on the critical line.
"""
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import comb

from . import intervals as iv


class CertificationError(RuntimeError):
    """The enclosure was too weak to certify the requested count."""


@dataclass(frozen=True)
class Params:
    N: int
    M: int
    stirling: int

    def label(self):
        return f"N={self.N}, M={self.M}, stirling={self.stirling}"


# Two truncations. The probe's search and check each pin one of them, so a
# certificate is accepted only when a second truncation reproduces it.
SEARCH = Params(16, 8, 6)
CHECK = Params(22, 10, 8)

_MAX_ARC = iv.SCALE // 2  # 0.5 radian
_LOG_CACHE = {}


@lru_cache(maxsize=None)
def bernoulli(m):
    """Bernoulli number B_m with the convention B_1 = -1/2."""
    if m == 0:
        return Fraction(1)
    total = sum(comb(m + 1, k) * bernoulli(k) for k in range(m))
    return -total / (m + 1)


def _log_positive(fr):
    fr = Fraction(fr)
    cached = _LOG_CACHE.get(fr)
    if cached is None:
        cached = iv.log_iv(iv.iv_fraction(fr))
        _LOG_CACHE[fr] = cached
    return cached


def _cpow(base, exponent):
    """``base`` a positive rational, ``exponent`` a complex rectangle."""
    return iv.cexp(iv.cscale(exponent, _log_positive(base)))


def _cneg(z):
    return iv.Cv(iv.neg(z.re), iv.neg(z.im))


def _pochhammer(s, m):
    acc = iv.Cv(iv.iv_int(1), iv.iv_int(0))
    for j in range(m):
        acc = iv.cmul(acc, iv.Cv(iv.add(s.re, iv.iv_int(j)), s.im))
    return acc


def _pow_lower(units, n):
    acc = iv.SCALE
    for _ in range(n):
        acc = (acc * units) // iv.SCALE
    return acc


def _remainder(s, base, M):
    """Upper bound, in fixed-point units, of the Euler–Maclaurin remainder."""
    sigma_lo = s.re.lo
    if sigma_lo <= (1 - 2 * M) * iv.SCALE:
        raise CertificationError("Euler–Maclaurin remainder diverges on this rectangle")
    poch = _pochhammer(s, 2 * M)
    mod_hi = iv.hypot_upper(poch.re, poch.im)
    twopi_lo = _pow_lower(iv.two_pi().lo, 2 * M)
    # (base)^{1-σ-2M} = exp((1-σ-2M) log base), maximised at the smallest σ.
    expo = iv.Iv((1 - 2 * M) * iv.SCALE - s.re.hi, (1 - 2 * M) * iv.SCALE - s.re.lo)
    log_base = _log_positive(base)
    power_hi = iv._exp_upper(iv.mul(expo, log_base).hi)
    denom_lo = sigma_lo + (2 * M - 1) * iv.SCALE
    if twopi_lo <= 0 or denom_lo <= 0:
        raise CertificationError("remainder denominator is not positive")
    # units(4 * mod * power / twopi / denom) = ceil(4 * mod * power * SCALE / (twopi * denom))
    num = 4 * mod_hi * power_hi * iv.SCALE
    den = twopi_lo * denom_lo
    return iv._ceil_div(num, den)


def hurwitz(s, a, params):
    """Hurwitz zeta ζ(s, a) for rational a > 0, as a complex rectangle."""
    a = Fraction(a)
    if a <= 0:
        raise ValueError("Hurwitz parameter must be positive")
    total = iv.Cv(iv.iv_int(0), iv.iv_int(0))
    for k in range(params.N):
        total = iv.cadd(total, _cpow(a + k, _cneg(s)))
    base = a + params.N
    one_minus_s = iv.Cv(iv.sub(iv.iv_int(1), s.re), iv.neg(s.im))
    pole = iv.Cv(iv.sub(s.re, iv.iv_int(1)), s.im)
    total = iv.cadd(total, iv.cdiv(_cpow(base, one_minus_s), pole))
    total = iv.cadd(total, iv.cscale(_cpow(base, _cneg(s)), iv.iv_fraction(Fraction(1, 2))))
    for j in range(1, params.M + 1):
        coef = iv.iv_fraction(bernoulli(2 * j) / Fraction(math_fact(2 * j)))
        poch = _pochhammer(s, 2 * j - 1)
        shift = iv.Cv(iv.add(s.re, iv.iv_int(2 * j - 1)), s.im)
        term = iv.cscale(iv.cmul(poch, _cpow(base, _cneg(shift))), coef)
        total = iv.cadd(total, term)
    radius = _remainder(s, base, params.M)
    return iv.cadd(total, iv.Cv(iv.Iv(-radius, radius), iv.Iv(-radius, radius)))


def math_fact(n):
    out = 1
    for k in range(2, n + 1):
        out *= k
    return out


def zeta(s, params):
    return hurwitz(s, 1, params)


def _stirling_radius(z, n):
    """Stieltjes remainder after n terms, in fixed-point units."""
    mod_lo = iv.hypot_lower(z.re, z.im)
    if mod_lo <= 0:
        raise CertificationError("Stirling requires |z| bounded away from 0")
    arc = iv.arg_arc(z)
    if arc is None:
        raise CertificationError("argument of the Gamma input is not a short arc")
    phi = max(abs(arc.lo), abs(arc.hi))
    # sec(φ/2) = 1/cos(φ/2). φ is a fixed-point magnitude.
    half_phi = iv.Iv(0, iv._ceil_div(phi, 2))
    cos_lo = iv.cos_iv(half_phi).lo
    if cos_lo <= 0:
        raise CertificationError("Stirling sector reaches the branch cut")
    sec = iv._ceil_div(iv.SCALE * iv.SCALE, cos_lo)
    sec_pow = iv.SCALE
    for _ in range(2 * n + 2):
        sec_pow = iv._ceil_div(sec_pow * sec, iv.SCALE)
    index = 2 * n + 2
    coef = abs(bernoulli(index)) / (index * (index - 1))
    coef_hi = iv.iv_fraction(coef).hi
    mod_pow = _pow_lower(mod_lo, index - 1)
    if mod_pow <= 0:
        raise CertificationError("Stirling modulus power vanished")
    return iv._ceil_div(coef_hi * sec_pow, mod_pow)


def log_gamma(z, n_terms):
    logz = iv.c_log(z)
    half = iv.iv_fraction(Fraction(1, 2))
    main = iv.csub(iv.cmul(iv.Cv(iv.sub(z.re, half), z.im), logz), z)
    log_two_pi = iv.add(iv.log2(), iv.log_iv(iv.pi()))
    main = iv.cadd(main, iv.Cv(iv.mul(log_two_pi, half), iv.iv_int(0)))
    for k in range(1, n_terms + 1):
        coef = iv.iv_fraction(bernoulli(2 * k) / (2 * k * (2 * k - 1)))
        power = iv.cexp(iv.cscale(logz, iv.iv_int(1 - 2 * k)))
        main = iv.cadd(main, iv.cscale(power, coef))
    radius = _stirling_radius(z, n_terms)
    return iv.cadd(main, iv.Cv(iv.Iv(-radius, radius), iv.Iv(-radius, radius)))


def _point(height):
    return iv.iv_fraction(Fraction(height))


def theta(height, n_terms):
    """Riemann–Siegel θ(t) = Im log Γ(1/4 + it/2) − (t/2) log π."""
    t = _point(height)
    z = iv.Cv(iv.iv_fraction(Fraction(1, 4)), iv.div_small(t, 2))
    imag = log_gamma(z, n_terms).im
    return iv.sub(imag, iv.mul(iv.div_small(t, 2), iv.log_iv(iv.pi())))


def hardy_z(height, params):
    phase = iv.cexp(iv.Cv(iv.iv_int(0), theta(height, params.stirling)))
    s = iv.Cv(iv.iv_fraction(Fraction(1, 2)), _point(height))
    return iv.cmul(phase, zeta(s, params))


def sign_z(height, params):
    """+1 or -1 when the Hardy Z enclosure lies in an open half-plane, else 0."""
    value = hardy_z(height, params)
    if value.re.lo > 0:
        return 1
    if value.re.hi < 0:
        return -1
    return 0


def _units(height):
    box = _point(height)
    if box.lo != box.hi:
        raise CertificationError("height is not an exact fixed-point rational")
    return box.lo


def _segment_image(s0, s1, params):
    box = iv.Cv(iv.Iv(min(s0[0], s1[0]), max(s0[0], s1[0])),
                iv.Iv(min(s0[1], s1[1]), max(s0[1], s1[1])))
    return zeta(box, params)


def _cover(s0, s1, params, depth):
    image = _segment_image(s0, s1, params)
    arc = iv.arg_arc(image)
    if arc is not None and arc.width() <= _MAX_ARC:
        return [arc]
    if depth >= 14:
        raise CertificationError(
            "argument enclosure failed; the contour passes too near a zero "
            "or the truncation is too coarse")
    mid = ((s0[0] + s1[0]) // 2, (s0[1] + s1[1]) // 2)
    return _cover(s0, mid, params, depth + 1) + _cover(mid, s1, params, depth + 1)


def _lift(arc, target, contain):
    """Lift ``arc`` by a multiple of 2π so that it meets ``target``.

    ``contain`` asks for the stronger condition that the lift covers ``target``
    (used at the start, where the argument is known to be 0).
    """
    found = None
    for k in range(-6, 7):
        lifted = iv.add(arc, iv.mul_small(iv.two_pi(), k))
        if contain:
            hit = lifted.lo <= target.lo and target.hi <= lifted.hi
        else:
            hit = lifted.lo <= target.hi and target.lo <= lifted.hi
        if hit:
            if found is not None:
                return None
            found = lifted
    return found


def argument_on_critical_line(height, params):
    """Continuous arg ζ(1/2+iT), started from arg ζ(2) = 0."""
    t = _units(height)
    right = _units(2)
    half = _units(Fraction(1, 2))
    vertical = []
    step = _units(2)
    y = 0
    while y < t:
        y2 = min(t, y + step)
        vertical += _cover((right, y), (right, y2), params, 0)
        y = y2
    horizontal = []
    x = right
    step_x = _units(Fraction(1, 4))
    while x > half:
        x2 = max(half, x - step_x)
        horizontal += _cover((x, t), (x2, t), params, 0)
        x = x2
    arcs = vertical + horizontal
    acc = _lift(arcs[0], iv.Iv(0, 0), contain=True)
    if acc is None:
        raise CertificationError("the contour does not start at argument 0")
    for arc in arcs[1:]:
        acc = _lift(arc, acc, contain=False)
        if acc is None:
            raise CertificationError("argument chain broke; subdivide the contour")
    return acc


def N_riemann(height, params):
    """Exact N(T): number of zeros with 0 < Im ρ ≤ T."""
    main = iv.add(iv.div(theta(height, params.stirling), iv.pi()), iv.iv_int(1))
    correction = iv.div(argument_on_critical_line(height, params), iv.pi())
    return iv.unique_integer(iv.add(main, correction))


def isolate_sign_changes(height, params, start=8, step=1):
    """Disjoint subintervals of (0, height) on which Z changes sign.

    Samples lie on a fixed rational grid. A sample whose enclosure contains 0
    is nudged by a few exact dyadic offsets. The returned endpoints are
    :class:`Fraction` instances.
    """
    height = Fraction(height)
    samples = []
    t = Fraction(start)
    offsets = (0, Fraction(1, 4), Fraction(-1, 4), Fraction(1, 2), Fraction(-1, 2),
               Fraction(1, 8), Fraction(-1, 8))
    while t < height:
        placed = False
        for delta in offsets:
            tt = t + delta
            if not 0 < tt < height:
                continue
            sign = sign_z(tt, params)
            if sign:
                samples.append((tt, sign))
                placed = True
                break
        if not placed:
            raise CertificationError(f"no certified Hardy sign near t = {t}")
        t += Fraction(step)
    sign_T = sign_z(height, params)
    if not sign_T:
        raise CertificationError(f"Z({height}) enclosure is not signed; pick another height")
    samples.append((height, sign_T))
    samples.sort()
    intervals = []
    for (t0, s0), (t1, s1) in zip(samples, samples[1:]):
        if s0 != s1 and t0 < t1:
            intervals.append((t0, t1))
    return intervals


def certify_riemann(height, zeros, params):
    """Return isolating intervals whose count equals N(height)."""
    found = isolate_sign_changes(height, params)
    count = N_riemann(height, params)
    if count is None:
        raise CertificationError("N(T) enclosure contains more than one integer")
    if count != len(found) or count != zeros:
        raise CertificationError(
            f"N({height}) = {count}, sign changes = {len(found)}, claimed = {zeros}")
    return found


def replay_riemann(height, zeros, intervals, params):
    """Independent replay: recompute N(T) and the sign at every endpoint."""
    if len(intervals) != zeros:
        raise CertificationError("interval count does not match the claimed zero count")
    previous = Fraction(0)
    for left, right in intervals:
        left, right = Fraction(left), Fraction(right)
        if not 0 < left < right <= Fraction(height) or left < previous:
            raise CertificationError("isolating intervals are not ordered inside (0, T]")
        s0, s1 = sign_z(left, params), sign_z(right, params)
        if s0 == 0 or s1 == 0 or s0 == s1:
            raise CertificationError(f"Z does not change sign on ({left}, {right})")
        previous = right
    count = N_riemann(height, params)
    if count != zeros:
        raise CertificationError(f"replay N({height}) = {count}, claimed {zeros}")
    return count


# --- Dirichlet L(s, χ₄), the Dirichlet beta function ----------------------

def L_chi4(s, params):
    """L(s, χ₄) = 4^{-s} (ζ(s, 1/4) − ζ(s, 3/4))."""
    scale = _cpow(4, _cneg(s))
    return iv.cmul(scale, iv.csub(hurwitz(s, Fraction(1, 4), params),
                                   hurwitz(s, Fraction(3, 4), params)))


def theta_chi4(height, n_terms):
    """Phase that makes Λ(1/2+it, χ₄) real when the root number is +1.

    χ₄ is the primitive odd character modulo 4. Its Gauss sum is 2i, so
    ε = τ(χ) / (i^a √q) = 1 with a = 1 and q = 4. Thus
    θ(t) = Im log Γ(3/4 + it/2) − (t/2) log(π/4).
    """
    t = _point(height)
    z = iv.Cv(iv.iv_fraction(Fraction(3, 4)), iv.div_small(t, 2))
    log_factor = iv.sub(iv.log_iv(iv.pi()), iv.log_iv(iv.iv_int(4)))
    return iv.sub(log_gamma(z, n_terms).im, iv.mul(iv.div_small(t, 2), log_factor))


def hardy_chi4(height, params):
    phase = iv.cexp(iv.Cv(iv.iv_int(0), theta_chi4(height, params.stirling)))
    s = iv.Cv(iv.iv_fraction(Fraction(1, 2)), _point(height))
    return iv.cmul(phase, L_chi4(s, params))


def sign_chi4(height, params):
    value = hardy_chi4(height, params)
    if value.re.lo > 0:
        return 1
    if value.re.hi < 0:
        return -1
    return 0


def _image_L(s0, s1, params):
    box = iv.Cv(iv.Iv(min(s0[0], s1[0]), max(s0[0], s1[0])),
                iv.Iv(min(s0[1], s1[1]), max(s0[1], s1[1])))
    return L_chi4(box, params)


def _cover_L(s0, s1, params, depth):
    arc = iv.arg_arc(_image_L(s0, s1, params))
    if arc is not None and arc.width() <= _MAX_ARC:
        return [arc]
    if depth >= 14:
        raise CertificationError("L-function argument enclosure failed on a contour segment")
    mid = ((s0[0] + s1[0]) // 2, (s0[1] + s1[1]) // 2)
    return _cover_L(s0, mid, params, depth + 1) + _cover_L(mid, s1, params, depth + 1)


def argument_chi4(height, params):
    """Continuous arg L(1/2+iT, χ₄), started from arg L(2, χ₄) = 0.

    The path is the segment from 2 up to 2+iT and then left to 1/2+iT, the
    same path used for ζ. There is no pole on it.
    """
    t = _units(height)
    right = _units(2)
    half = _units(Fraction(1, 2))
    arcs = []
    y, step = 0, _units(2)
    while y < t:
        y2 = min(t, y + step)
        arcs += _cover_L((right, y), (right, y2), params, 0)
        y = y2
    x, step_x = right, _units(Fraction(1, 4))
    while x > half:
        x2 = max(half, x - step_x)
        arcs += _cover_L((x, t), (x2, t), params, 0)
        x = x2
    acc = _lift(arcs[0], iv.Iv(0, 0), contain=True)
    if acc is None:
        raise CertificationError("L(2, χ₄) is not enclosed as a positive real")
    for arc in arcs[1:]:
        acc = _lift(arc, acc, contain=False)
        if acc is None:
            raise CertificationError("L-function argument chain broke")
    return acc


def N_chi4(height, params):
    """Non-trivial zeros of L(s, χ₄) with 0 < Im s ≤ T.

    χ₄ is primitive and non-principal, so Λ(s, χ₄) is entire and the counting
    formula has no pole term: N(T) = θ(T)/π + (1/π) arg L(1/2+iT). The root
    number +1 is already built into ``theta_chi4``.
    """
    main = iv.div(theta_chi4(height, params.stirling), iv.pi())
    correction = iv.div(argument_chi4(height, params), iv.pi())
    return iv.unique_integer(iv.add(main, correction))


def isolate_chi4(height, params, start=4, step=1):
    height = Fraction(height)
    samples = []
    t = Fraction(start)
    offsets = (0, Fraction(1, 4), Fraction(-1, 4), Fraction(1, 2), Fraction(-1, 2))
    while t < height:
        placed = False
        for delta in offsets:
            tt = t + delta
            if not 0 < tt < height:
                continue
            sign = sign_chi4(tt, params)
            if sign:
                samples.append((tt, sign))
                placed = True
                break
        if not placed:
            raise CertificationError(f"no certified χ₄ sign near t = {t}")
        t += Fraction(step)
    sign_T = sign_chi4(height, params)
    if not sign_T:
        raise CertificationError(f"Z_χ({height}) enclosure is not signed")
    samples.append((height, sign_T))
    samples.sort()
    intervals = []
    for (t0, s0), (t1, s1) in zip(samples, samples[1:]):
        if s0 != s1 and t0 < t1:
            intervals.append((t0, t1))
    return intervals


def certify_chi4(height, zeros, params):
    found = isolate_chi4(height, params)
    count = N_chi4(height, params)
    if count is None or count != len(found) or count != zeros:
        raise CertificationError(
            f"χ₄ N({height}) = {count}, sign changes = {len(found)}, claimed = {zeros}")
    return found


def replay_chi4(height, zeros, intervals, params):
    if len(intervals) != zeros:
        raise CertificationError("interval count does not match the claimed zero count")
    previous = Fraction(0)
    for left, right in intervals:
        left, right = Fraction(left), Fraction(right)
        if not 0 < left < right <= Fraction(height) or left < previous:
            raise CertificationError("isolating intervals are not ordered inside (0, T]")
        s0, s1 = sign_chi4(left, params), sign_chi4(right, params)
        if s0 == 0 or s1 == 0 or s0 == s1:
            raise CertificationError(f"Z_χ does not change sign on ({left}, {right})")
        previous = right
    count = N_chi4(height, params)
    if count != zeros:
        raise CertificationError(f"replay χ₄ N({height}) = {count}, claimed {zeros}")
    return count
