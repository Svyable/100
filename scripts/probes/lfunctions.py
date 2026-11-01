"""Rigorous evaluation of zeta and real Dirichlet L-functions, and certified zero counts.

Everything here is built on :mod:`intervals`, so each returned enclosure contains
the true value whenever the stated theorems hold:

* Euler-Maclaurin summation for L(s, chi) = sum_n chi(n) n^-s with chi periodic
  mod q (q = 1 gives zeta). Writing n = qk + a, the tail over k >= N of each residue
  class a is

      u^(1-s)/(q(s-1)) + u^-s/2 + sum_{j=1}^{M} B_2j/(2j)! (s)_{2j-1} q^(2j-1) u^(-s-2j+1) + R,

  where u = qN + a and |R| <= |B_2M|/(2M)! |(s)_{2M}| q^(2M-1) u^(1-sigma-2M) / (sigma+2M-1)
  (the periodic Bernoulli function is bounded by |B_2M|).
* Stirling's series for log Gamma after shifting z by K, with the remainder bound
  sec^(2m)(arg(z)/2) times the first omitted term (DLMF 5.11.ii).
* The exact counting formula (Backlund; Titchmarsh 9.3) N(T) = theta(T)/pi + 1 + S(T)
  for zeta, and its analogue N(T, chi) = (theta(T, chi) + Delta arg L)/pi - N_0/2 for a
  primitive real character, where Delta arg L is the continuous change of the argument
  along 2 -> 2+iT -> 1/2+iT and N_0 counts real zeros in (0, 1). On Re s = 2 the real part
  of L is at least 2 - pi^2/6 > 0, so the variation there is the principal value. Along
  the horizontal segment the change is certified by boxes, each inside an open half-plane.

A zero count N, together with N certified sign changes of the real Hardy function
Z(t) = e^(i theta(t)) L(1/2+it) on (0, T), proves that every zero with 0 < Im < T lies on
the critical line and is simple.
"""
import cmath
import math
from fractions import Fraction
from functools import lru_cache

from .intervals_cert import CENTER, CI, RI, arg_in_window, atan, exp, half_plane, in_half_plane, log, pi, sincos


@lru_cache(maxsize=None)
def bernoulli(n):
    """Exact Bernoulli numbers B_0..B_n (B_1 = -1/2)."""
    B = [Fraction(0)] * (n + 1)
    for m in range(n + 1):
        A = [Fraction(0)] * (m + 1)
        for j in range(m + 1):
            A[j] = Fraction(1, j + 1)
            for k in range(j, 0, -1):
                A[k - 1] = k * (A[k - 1] - A[k])
        B[m] = A[0]
    if n >= 1:
        B[1] = Fraction(-1, 2)
    return tuple(B)


def _fact(n):
    return math.factorial(n)


class LSeries:
    """L(s, chi) for a periodic real coefficient table chi[0..q-1] (chi[n % q]); q = 1 is zeta."""

    def __init__(self, q, chi, p):
        if len(chi) != q:
            raise ValueError("character table must have length q")
        self.q, self.chi, self.p = q, tuple(chi), p
        self.mean_zero = sum(chi) == 0
        self._log = {}
        self._halfpow = {}

    # ---------------------------------------------------------- helpers
    def logn(self, n):
        if n not in self._log:
            self._log[n] = log(RI.exact(n, self.p))
        return self._log[n]

    def powers(self, sigma, t, top):
        """n^-s for n = 1..top as complex intervals, built multiplicatively from primes."""
        p = self.p
        exact_half = sigma.lo == sigma.hi == 1 << (p - 1)
        table = [None, CI.exact(1, 0, p)]
        spf = list(range(top + 1))
        for i in range(2, int(top ** 0.5) + 1):
            if spf[i] == i:
                for j in range(i * i, top + 1, i):
                    if spf[j] == j:
                        spf[j] = i
        for n in range(2, top + 1):
            f = spf[n]
            if f != n:
                table.append(table[f] * table[n // f])
                continue
            L = self.logn(n)
            if exact_half:
                if n not in self._halfpow:
                    self._halfpow[n] = RI.exact(1, p) / RI.exact(n, p).sqrt()
                mag = self._halfpow[n]
            else:
                mag = exp(-(sigma * L))
            sn, cs = sincos(t * L)
            table.append(CI(mag * cs, -(mag * sn)))
        return table

    # -------------------------------------------------------- evaluation
    def value(self, sigma, t, factor=Fraction(1, 2), extra=8, terms=None):
        """Enclosure of L(sigma + i t) for real intervals sigma, t (t = 0 handles s = 1 when sum chi = 0)."""
        p, q = self.p, self.q
        M = terms if terms is not None else p // 3 + 6
        s_abs = max(abs(sigma).upper(), Fraction(1)) + abs(t).upper()
        # keep |s + 2M| q / (2 pi u) small so every correction term shrinks geometrically
        N = int((s_abs + 2 * M) * factor) + extra
        top = q * N + q
        table = self.powers(sigma, t, top)
        s = CI(sigma, t)
        total = CI.exact(0, 0, p)
        for n in range(1, q * N + 1):
            c = self.chi[n % q]
            if c == 1:
                total = total + table[n]
            elif c == -1:
                total = total - table[n]
        B = bernoulli(2 * M)
        one = 1 << p
        through_pole = t.lo == 0 and t.hi == 0 and sigma.lo <= one <= sigma.hi
        # integral terms: sum_a chi(a) u_a^(1-s) / (q (s - 1))
        if through_pole:
            if not self.mean_zero:
                raise ZeroDivisionError("s = 1 is a pole")
            # g(s) = sum chi(a) u_a^(1-s) has g(1) = 0, so g(s)/(s-1) = g'(xi) for xi between s and 1
            xi = RI(min(sigma.lo, RI.exact(1, p).lo), max(sigma.hi, RI.exact(1, p).hi), p)
            acc = RI.exact(0, p)
            for a in range(1, q + 1):
                c = self.chi[a % q]
                if c:
                    u = q * N + a
                    term = self.logn(u) * exp((1 - xi) * self.logn(u))
                    acc = acc - term if c == 1 else acc + term
            total = total + CI(acc / q, RI.exact(0, p))
        else:
            inv = (s - 1).recip()
            for a in range(1, q + 1):
                c = self.chi[a % q]
                if c:
                    u = q * N + a
                    piece = table[u] * u * inv / q
                    total = total + piece if c == 1 else total - piece
        # half terms, Bernoulli corrections and the remainder, per residue class
        sig_lo = sigma.lower()
        if sig_lo + 2 * M - 1 <= 0:
            raise ValueError("Euler-Maclaurin needs sigma + 2M - 1 > 0")
        rising = Fraction(1)  # upper bound for |(s)_{2M}|
        for i in range(2 * M):
            rising *= _coarse_up((s + i).abs_upper().upper())
        for a in range(1, q + 1):
            c = self.chi[a % q]
            if not c:
                continue
            u = q * N + a
            # w_j = B_2j/(2j)! (s)_{2j-1} (q/u)^(2j-1), advanced by exact rational ratios so that
            # no tiny constant is ever rounded to fixed point before being multiplied by a large one
            w = s * RI.exact(B[2] / 2 * Fraction(q, u), p)
            corr = CI.exact(Fraction(1, 2), 0, p)
            for j in range(1, M + 1):
                corr = corr + w
                if j < M:
                    step = B[2 * j + 2] * _fact(2 * j) / (B[2 * j] * _fact(2 * j + 2)) * Fraction(q, u) ** 2
                    w = w * (s + (2 * j - 1)) * (s + 2 * j) * RI.exact(step, p)
            piece = table[u] * corr
            # remainder: |B_2M|/(2M)! |(s)_2M| q^(2M-1) u^(1 - sigma - 2M) / (sigma + 2M - 1)
            mag_u = exp(-(RI.exact(sig_lo, p) * self.logn(u))).upper() * u  # u^(1 - sigma_lo)
            bound = (abs(B[2 * M]) / _fact(2 * M) * rising * Fraction(q, u) ** (2 * M)
                     * _coarse_up(mag_u) / q / (sig_lo + 2 * M - 1))
            r = int(bound * (1 << p)) + 2
            piece = CI(piece.re.widen(r), piece.im.widen(r))
            total = total + piece if c == 1 else total - piece
        return total


def _coarse_up(x):
    x = Fraction(x)
    return Fraction(-((-x.numerator << 40) // x.denominator), 1 << 40)


def _coarse_down(x):
    x = Fraction(x)
    return Fraction((x.numerator << 40) // x.denominator, 1 << 40)


# ============================================================ log Gamma

def im_log_gamma(x, y, shift=24, terms=24):
    """Im log Gamma(x + i y) for rational x > 0 and a real interval y (principal branch, real on (0, inf))."""
    p = y.p
    x = Fraction(x)
    if x <= 0:
        raise ValueError("needs Re z > 0")
    xs = RI.exact(x + shift, p)
    z = CI(xs, y)
    arg = atan(y / xs)
    r2 = xs.sqr() + y.sqr()
    main = (xs - Fraction(1, 2)) * arg + y * (log(r2) * Fraction(1, 2)) - y
    B = bernoulli(2 * terms)
    w = z.recip()
    w2 = w * w
    coef = [B[2 * k] / (2 * k * (2 * k - 1)) for k in range(1, terms)]
    term = w * RI.exact(coef[0], p)  # c_k w^(2k-1), advanced by exact ratios c_(k+1)/c_k
    series = RI.exact(0, p)
    for k in range(1, terms):
        series = series + term.im
        if k < terms - 1:
            term = term * w2 * RI.exact(coef[k] / coef[k - 1], p)
    r = r2.sqrt()
    r_lo, r_hi = _coarse_down(r.lower()), _coarse_up(r.upper())
    xv = x + shift
    sec2 = _coarse_up(2 * r_hi / (r_hi + xv))  # sec^2(arg z / 2) = 2|z| / (|z| + Re z)
    first = abs(B[2 * terms]) / (2 * terms * (2 * terms - 1)) / r_lo ** (2 * terms - 1)
    bound = sec2 ** terms * first
    total = (main + series).widen(int(bound * (1 << p)) + 2)
    for k in range(shift):
        total = total - atan(y / RI.exact(x + k, p))
    return total


def theta(t, q=1, parity=0, shift=24, terms=24):
    """theta(t, chi) = Im log Gamma((1/2 + a + i t)/2) + (t/2) log(q/pi); q = 1 is Riemann-Siegel theta."""
    p = t.p
    g = im_log_gamma(Fraction(1 + 2 * parity, 4), t * Fraction(1, 2), shift, terms)
    return g + t * Fraction(1, 2) * (log(RI.exact(q, p)) - log(pi(p)))


def hardy_z(series, t, parity, factor=Fraction(1, 2), extra=8, terms=None, shift=24, gterms=24):
    """Z(t) = e^(i theta) L(1/2 + i t): returns (real part, imaginary part); the latter must contain 0."""
    p = series.p
    L = series.value(RI.exact(Fraction(1, 2), p), t, factor, extra, terms)
    th = theta(t, series.q, parity, shift, gterms)
    sn, cs = sincos(th)
    return L.re * cs - L.im * sn, L.re * sn + L.im * cs


# ======================================================= zero counting

def lifted_direction(ks):
    """Lift a sequence of half-plane indices to a window centre D (quarter turns, D = CENTER[k] mod 4).

    The first box contains L(2 + iT), whose continuous argument is the principal value in
    (-pi/2, pi/2) because Re L > 0 on Re s = 2; so the first window is centred at CENTER[k0]
    (k0 = 2 is impossible). Neighbouring boxes share a point, so their half-planes are never
    opposite and the centre moves by -1, 0 or +1 quarter turn. Returns None if inconsistent.
    """
    if not ks or ks[0] == 2:
        return None
    D = CENTER[ks[0]]
    for prev, cur in zip(ks, ks[1:]):
        step = (cur - prev) % 4
        if step == 2:
            return None
        D += {0: 0, 1: 1, 3: -1}[step]
    return D


def argument_count(series, T, parity, pieces, factor, extra, terms, shift, gterms, pole):
    """Certify N(T) from declared pieces [(sigma_hi, sigma_lo, k)], running 2 -> 1/2. Returns (N, interval)."""
    p = series.p
    t = RI.exact(T, p)
    prev = Fraction(2)
    ks = []
    for hi, lo, k in pieces:
        hi, lo = Fraction(hi), Fraction(lo)
        if hi != prev or not lo < hi:
            raise ValueError("pieces must tile [1/2, 2] from 2 downward")
        if not _box_in_half_plane(series, lo, hi, t, k, factor, extra, terms, depth=3):
            raise ValueError(f"box on [{lo}, {hi}] is not inside half-plane {k}")
        ks.append(k)
        prev = lo
    if prev != Fraction(1, 2):
        raise ValueError("pieces must end at sigma = 1/2")
    D = lifted_direction(ks)
    if D is None:
        raise ValueError("inconsistent half-plane sequence")
    end = series.value(RI.exact(Fraction(1, 2), p), t, factor, extra, terms)
    shift_quarters = D - CENTER[ks[-1]]
    if shift_quarters % 4:
        raise ValueError("lifted direction inconsistent with the last half-plane")
    A = arg_in_window(end, ks[-1]) + pi(p) * Fraction(shift_quarters, 2)
    total = (theta(t, series.q, parity, shift, gterms) + A) / pi(p) + (1 if pole else 0)
    n = math.floor(float(total) + 0.5)
    if not (total.lower() > n - Fraction(1, 2) and total.upper() < n + Fraction(1, 2)):
        raise ValueError("zero count is not certified to a unique integer")
    return n, total


def _box_in_half_plane(series, lo, hi, t, k, factor, extra, terms, depth):
    """Is L([lo, hi] + i t) inside half-plane k? Bisect up to `depth` times (a cover by smaller boxes is a proof)."""
    p = series.p
    box = series.value(RI(RI.exact(lo, p).lo, RI.exact(hi, p).hi, p), t, factor, extra, terms)
    if in_half_plane(box, k):
        return True
    if depth == 0:
        return False
    mid = (lo + hi) / 2
    return (_box_in_half_plane(series, lo, mid, t, k, factor, extra, terms, depth - 1) and
            _box_in_half_plane(series, mid, hi, t, k, factor, extra, terms, depth - 1))


def _inflate(box, factor=2):
    def grow(v):
        w = v.hi - v.lo
        return v.widen((w * (factor - 1) + 1) // 2 + 1)
    return CI(grow(box.re), grow(box.im))


def find_pieces(series, T, factor, extra, terms, start=Fraction(1, 8), min_width=Fraction(1, 1 << 14)):
    """Adaptive subdivision of [1/2, 2] into boxes each inside an open half-plane (search side).

    A piece is accepted only if its box, inflated to twice its width, still lies in the half-plane,
    so a checker using a different truncation (and slightly wider boxes) can confirm it.
    """
    p = series.p
    t = RI.exact(T, p)
    out, hi, width, prev_k = [], Fraction(2), start, None
    while hi > Fraction(1, 2):
        lo = max(Fraction(1, 2), hi - width)
        box = _inflate(series.value(RI(RI.exact(lo, p).lo, RI.exact(hi, p).hi, p), t, factor, extra, terms))
        k = prev_k if prev_k is not None and in_half_plane(box, prev_k) else half_plane(box)
        if k is None or (prev_k is not None and (k - prev_k) % 4 == 2):
            width /= 2
            if width < min_width:
                raise ValueError("could not separate the horizontal segment from zero")
            continue
        out.append((str(hi), str(lo), k))
        hi, prev_k = lo, k
        width = min(width * 2, start)
    return out


def lipschitz_real(chi):
    """Upper bound for |L'(sigma, chi)| on sigma >= 1/2 for a non-principal periodic chi.

    Partial summation with A(x) = sum_{n <= x} chi(n), |A| <= A_max (zero sum over a period), and
    f(x) = log(x) x^-sigma, whose total variation on [1, inf) is 2/(e sigma), gives
    |L'(sigma)| <= 2 A_max / (e sigma) <= 4 A_max / e < 4 A_max / 2.718.
    """
    q = len(chi)
    if sum(chi) != 0:
        raise ValueError("needs a non-principal character")
    acc, a_max = 0, 0
    for n in range(1, q + 1):
        acc += chi[n % q]
        a_max = max(a_max, abs(acc))
    return Fraction(4 * a_max) * Fraction(1000, 2718)


def real_axis_pieces(series, start=Fraction(1, 4), min_radius=Fraction(1, 1 << 12)):
    """Search side: cover [1/2, 1] by intervals [c - r, c + r] with |L(c)| > r * Lip (so no zero inside)."""
    p = series.p
    zero = RI.exact(0, p)
    lip = lipschitz_real(series.chi)
    out, lo, r = [], Fraction(1, 2), start
    while lo < 1:
        r = min(r, (1 - lo) / 2)
        c = lo + r
        v = series.value(RI.exact(c, p), zero)
        if abs(v.re).lower() > r * lip:
            out.append((str(c), str(r), v.re.sign()))
            lo = c + r
            r = min(r * 2, start)
            continue
        r /= 2
        if r < min_radius:
            raise ValueError("could not certify L(sigma) != 0 on [1/2, 1]")
    return out


def check_real_axis(series, pieces):
    """Every [c - r, c + r] must satisfy |L(c)| > r * Lip, and the intervals must tile [1/2, 1]."""
    p = series.p
    zero = RI.exact(0, p)
    lip = lipschitz_real(series.chi)
    prev = Fraction(1, 2)
    for c, r, sgn in pieces:
        c, r = Fraction(c), Fraction(r)
        if c - r != prev or r <= 0:
            raise ValueError("real-axis pieces must tile [1/2, 1]")
        v = series.value(RI.exact(c, p), zero)
        if not (abs(v.re).lower() > r * lip and v.re.sign() == sgn):
            raise ValueError(f"L(sigma) not certified nonzero on [{c - r}, {c + r}]")
        prev = c + r
    if prev != 1:
        raise ValueError("real-axis pieces must end at 1")


# ------------------------------------------------------ search heuristics (floats only pick points)

def _float_theta(t, q, parity):
    z = complex((0.5 + parity) / 2 + 12, t / 2)
    val = (z - 0.5) * cmath.log(z) - z
    B = bernoulli(16)
    for k in range(1, 8):
        val += float(B[2 * k]) / (2 * k * (2 * k - 1)) / z ** (2 * k - 1)
    for k in range(12):
        val -= cmath.log(complex((0.5 + parity) / 2 + k, t / 2))
    return val.imag + t / 2 * math.log(q / math.pi)


def gram_points(T, q, parity):
    """Approximate Gram points g_n (theta(g_n) = n pi) in the increasing region below T."""
    t0 = max(2 * math.pi / q * 1.5, 1.0)
    pts = []
    n = math.ceil(_float_theta(t0, q, parity) / math.pi)
    t = t0
    while True:
        target = n * math.pi
        for _ in range(60):
            d = 0.5 * math.log(max(q * t / (2 * math.pi), 1.0001))
            step = (_float_theta(t, q, parity) - target) / d
            t -= step
            t = max(t, t0)
            if abs(step) < 1e-10:
                break
        if t >= T:
            break
        if t > t0 and (not pts or t > pts[-1]):
            pts.append(t)
        n += 1
    return pts, t0


def sample_points(series, T, parity, needed, evaluate, rounds=12):
    """Choose points in (0, T] with certified signs of Z until `needed` sign changes are found.

    Gram points (where Z usually alternates) plus a coarse grid below the first one; then every
    interval whose ends share a sign is trisected, round after round. Any choice of points is
    sound: a sign change always encloses a zero, so a bad choice can only fail to certify.
    """
    gram, t0 = gram_points(T, series.q, parity)
    pts = {Fraction(f"{x:.6f}") for x in gram} | {Fraction(k, 2) for k in range(1, int(t0 * 2) + 1)} | {T}
    vals = {}

    def add(x):
        if 0 < x <= T and x not in vals:
            v = evaluate(x)
            if v[0]:
                vals[x] = v

    for x in sorted(pts):
        add(x)

    def same_sign():
        xs = sorted(vals)
        return xs, [(a, b) for a, b in zip(xs, xs[1:]) if vals[a][0] == vals[b][0]]

    for _ in range(rounds):
        xs, same = same_sign()
        if sum(1 for a, b in zip(xs, xs[1:]) if vals[a][0] != vals[b][0]) >= needed:
            break
        for a, b in same:
            if b - a > Fraction(1, 10 ** 5):
                for m in (a + (b - a) / 3, a + 2 * (b - a) / 3):
                    add(Fraction(f"{float(m):.6f}"))
    pts = sorted(vals)
    return pts, vals
