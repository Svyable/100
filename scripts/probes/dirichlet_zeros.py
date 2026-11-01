"""M002 - Generalized Riemann Hypothesis for real primitive characters, up to height T.

For each fundamental discriminant D the Kronecker symbol chi_D(n) = (D/n) is a real
primitive character mod |D| with chi_D(-1) = sign(D). Search side, per character:
certify that L(sigma, chi_D) != 0 on [1/2, 1] (so, by the functional equation, there
is no real zero in (0, 1)); certify the exact count N(T, chi) = (theta(T, chi) + Delta arg L)/pi
by the argument principle along 2 -> 2+iT -> 1/2+iT; and find N(T, chi) certified sign
changes of Z(t, chi) = e^(i theta(t, chi)) L(1/2+it, chi) on (0, T]. Real characters
have zeros symmetric about the real axis, so every zero with |Im s| < T is on the line.
Check side: re-derives the character table (complete multiplicativity, primitivity,
parity, Euler's criterion at every prime below |D|), certifies the root number +1 from
the Gauss sum, and recomputes every certificate with a different precision and
truncation. A failure to find enough sign changes is a search failure, never a counterexample.
"""
from fractions import Fraction
from math import gcd

from . import lfunctions as LF
from .core import digest, require
from .intervals_cert import CI, RI, pi, sincos

PROBE = {
    "id": "dirichlet_zeros",
    "problem_id": "M002",
    "title": "GRH up to height T for the real primitive characters of small conductor",
    "engines": ["interval_arithmetic", "l_functions"],
    "frontier": ("Known: GRH verified for every primitive character of modulus q <= 400,000 up to height at "
                 "least 10^8/q (Platt, Math. Comp. 2016), and for q <= 13 to height 10,000 (Rumely 1993). "
                 "Reproduction only."),
    "levels": {
        "smoke": {"discriminants": [-4, -3, 5], "height": 20},
        "deep": {"discriminants": [-3, -4, 5, -7, 8, -8, -11, 12, 13, -15, 17, -19, -20, 21, -23, -24, 24],
                 "height": 30},
    },
}

# Sign certification needs ~40 bits, so fewer Euler-Maclaurin terms keep the direct sums (about q|s|/2 terms) short.
SEARCH = {"p": 80, "factor": Fraction(2, 5), "extra": 4, "terms": 16, "shift": 20, "gterms": 16}
CHECK = {"p": 96, "factor": Fraction(1, 2), "extra": 6, "terms": 20, "shift": 26, "gterms": 18}


def scope(params):
    ds = ", ".join(str(d) for d in params["discriminants"])
    return (f"For chi_D with D in {{{ds}}}: L(s, chi_D) has no real zero in (0, 1), and every zero with "
            f"|Im s| < {params['height']} is simple and on Re s = 1/2 (certified count = certified sign changes).")


def jacobi(a, n):
    if n <= 0 or n % 2 == 0:
        raise ValueError("Jacobi symbol needs odd positive n")
    a %= n
    result = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n
    return result if n == 1 else 0


def kronecker(D, n):
    """Kronecker symbol (D/n) for n >= 1."""
    result = 1
    while n % 2 == 0:
        n //= 2
        if D % 2 == 0:
            return 0
        result *= 1 if D % 8 in (1, 7) else -1
    return result * jacobi(D, n) if n > 1 else result


def squarefree(m):
    m = abs(m)
    f = 2
    while f * f <= m:
        if m % (f * f) == 0:
            return False
        f += 1
    return True


def fundamental(D):
    if D in (0, 1):
        return False
    if D % 4 == 1:
        return squarefree(D)
    return D % 4 == 0 and (D // 4) % 4 in (2, 3) and squarefree(D // 4)


def character(D):
    q = abs(D)
    return q, [0] + [kronecker(D, n) for n in range(1, q)], 0 if D > 0 else 1


def _text(x):
    return f"{float(x):.6f}"


def _one(D, T, cfg):
    q, chi, a = character(D)
    series = LF.LSeries(q, chi, cfg["p"])
    real_pieces = LF.real_axis_pieces(series)
    pieces = LF.find_pieces(series, T, cfg["factor"], cfg["extra"], cfg["terms"])
    n, _ = LF.argument_count(series, T, a, pieces, cfg["factor"], cfg["extra"], cfg["terms"],
                             cfg["shift"], cfg["gterms"], pole=False)

    def evaluate(t):
        re, im = LF.hardy_z(series, RI.exact(t, cfg["p"]), a, cfg["factor"], cfg["extra"], cfg["terms"],
                            cfg["shift"], cfg["gterms"])
        if not im.contains_zero():
            raise RuntimeError(f"D={D}: Im(e^(i theta) L) excludes 0 at t = {t}")
        return re.sign(), float(re)

    pts, vals = LF.sample_points(series, T, a, n, evaluate)
    signs = [vals[x][0] for x in pts]
    changes = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1) if signs[i] != signs[i + 1]]
    if len(changes) != n:
        raise RuntimeError(f"D={D}: {len(changes)} sign changes for N(T) = {n}; refine the sampler")
    return {
        "D": D, "q": q, "parity": a, "chi": chi, "real_axis": [list(x) for x in real_pieces],
        "zero_count": n, "pieces": [list(x) for x in pieces],
        "points": [_text(x) for x in pts], "signs": signs,
        "first_zero_bracket": [_text(changes[0][0]), _text(changes[0][1])] if changes else None,
    }


def search(params):
    T = Fraction(params["height"])
    rows = [_one(D, T, SEARCH) for D in params["discriminants"]]
    cert = {"height": str(T), "characters": rows}
    return {
        "holds": True,
        "summary": {
            "height": str(T), "characters": len(rows), "zeros_upper_half": sum(r["zero_count"] for r in rows),
            "per_character": {str(r["D"]): r["zero_count"] for r in rows},
            "certificate_sha256": digest(cert),
        },
        "certificate": cert,
    }


def _check_character(D, q, chi, parity):
    require(fundamental(D) and q == abs(D) and len(chi) == q, f"D={D} is not a fundamental discriminant table")
    require(all(v in (-1, 0, 1) for v in chi), f"D={D}: values must be real")
    for n in range(q):
        require((chi[n] == 0) == (gcd(n, q) != 1), f"D={D}: chi({n}) must vanish exactly off the units")
        for m in range(q):
            require(chi[m * n % q] == chi[m] * chi[n], f"D={D}: not completely multiplicative")
    require(chi[q - 1] == (1 if D > 0 else -1) and parity == (0 if D > 0 else 1), f"D={D}: parity mismatch")
    for d in range(1, q):
        if q % d == 0:
            require(any(gcd(n, q) == 1 and n % d == 1 % d and chi[n] != 1 for n in range(q)),
                    f"D={D}: induced from modulus {d}, not primitive")
    for p_ in range(2, q):
        if all(p_ % f for f in range(2, p_)) and q % p_:
            if p_ == 2:
                expected = 1 if D % 8 in (1, 7) else -1
            else:
                e = pow(D % p_, (p_ - 1) // 2, p_)
                expected = 1 if e == 1 else -1
            require(chi[p_ % q] == expected, f"D={D}: chi({p_}) contradicts Euler's criterion")


def _check_root_number(q, chi, parity, p):
    """Gauss sum tau(chi) must be i^parity sqrt(q) (root number +1), not its negative."""
    tau = CI.exact(0, 0, p)
    two_pi = pi(p) * 2
    for n in range(1, q):
        if chi[n]:
            s, c = sincos(two_pi * Fraction(n, q))
            tau = tau + CI(c, s) * chi[n]
    root = RI.exact(q, p).sqrt()
    target = CI(root, RI.exact(0, p)) if parity == 0 else CI(RI.exact(0, p), root)
    diff = (tau - target).abs2()
    return diff.upper() < Fraction(1, 10 ** 6) and (tau + target).abs2().lower() > 1


def check(params, result):
    cert = result["certificate"]
    T = Fraction(params["height"])
    require(result["holds"] is True, "this probe never reports counterexamples; a mismatch is a search failure")
    require(cert["height"] == str(T), "height differs from the parameters")
    rows = cert["characters"]
    require([r["D"] for r in rows] == list(params["discriminants"]), "character list differs")
    cfg = CHECK
    for r in rows:
        D, q, chi, a = r["D"], r["q"], r["chi"], r["parity"]
        _check_character(D, q, chi, a)
        require(_check_root_number(q, chi, a, cfg["p"]), f"D={D}: root number is not +1")
        series = LF.LSeries(q, chi, cfg["p"])
        try:
            LF.check_real_axis(series, [tuple(x) for x in r["real_axis"]])
            n, _ = LF.argument_count(series, T, a, [tuple(x) for x in r["pieces"]], cfg["factor"], cfg["extra"],
                                     cfg["terms"], cfg["shift"], cfg["gterms"], pole=False)
        except ValueError as exc:
            require(False, f"D={D}: certificate rejected: {exc}")
        require(n == r["zero_count"], f"D={D}: zero count {r['zero_count']} differs from recomputed {n}")
        pts = [Fraction(x) for x in r["points"]]
        require(len(pts) == len(r["signs"]) and all(s in (1, -1) for s in r["signs"]), f"D={D}: malformed signs")
        require(pts and pts[0] > 0 and pts[-1] <= T and all(x < y for x, y in zip(pts, pts[1:])),
                f"D={D}: points must increase strictly inside (0, T]")
        for t, sgn in zip(pts, r["signs"]):
            re, im = LF.hardy_z(series, RI.exact(t, cfg["p"]), a, cfg["factor"], cfg["extra"], cfg["terms"],
                                cfg["shift"], cfg["gterms"])
            require(im.contains_zero(), f"D={D}: Im(e^(i theta) L) excludes 0 at t = {t}")
            require(re.sign() == sgn, f"D={D}: sign of Z({t}) not confirmed")
        changes = sum(1 for x, y in zip(r["signs"], r["signs"][1:]) if x != y)
        require(changes == n, f"D={D}: {changes} sign changes do not account for N(T) = {n}")
    s = result["summary"]
    require(s["characters"] == len(rows) and s["zeros_upper_half"] == sum(r["zero_count"] for r in rows)
            and s["per_character"] == {str(r["D"]): r["zero_count"] for r in rows}, "summary mismatch")
    require(s["certificate_sha256"] == digest(cert), "certificate hash mismatch")
