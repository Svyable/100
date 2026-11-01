"""M001 - Riemann Hypothesis: every zero of zeta with 0 < Im s < T is on the critical line.

Search side: certify the exact zero count N(T) = theta(T)/pi + 1 + S(T) by tracking
arg zeta along 2 -> 2+iT -> 1/2+iT with interval boxes, each inside an open
half-plane, then place points on (0, T] until the Hardy function Z(t) shows N(T)
certified sign changes. N(T) zeros counted with multiplicity and N(T) distinct sign
changes of the real function Z on the line together prove that every zero up to
height T is on the line and simple.
Check side: recomputes the count from the declared boxes and the sign of Z at every
point with a different precision, Euler-Maclaurin truncation and Stirling shift, and
requires Im(e^(i theta) zeta) to contain 0 at every point (a live test of theta).
A failure to find enough sign changes is a search failure, never a counterexample.
"""
from fractions import Fraction

from . import lfunctions as LF
from .core import digest, require
from .intervals import RI

PROBE = {
    "id": "zeta_zeros",
    "problem_id": "M001",
    "title": "Certified zero count and critical-line location of every Riemann zero up to height T",
    "engines": ["interval_arithmetic", "l_functions"],
    "frontier": ("Known: every zero with 0 < Im s <= 3*10^12 is on the critical line and simple "
                 "(Platt & Trudgian 2021); the first 10^13 zeros were located by Gourdon (2004). "
                 "These heights reproduce classical computations (Gram, Backlund, Hutchinson)."),
    "levels": {"smoke": {"height": 100}, "deep": {"height": 1000}},
}

SEARCH = {"p": 100, "factor": Fraction(1, 2), "extra": 8, "terms": None, "shift": 24, "gterms": 24}
CHECK = {"p": 128, "factor": Fraction(2, 3), "extra": 11, "terms": 50, "shift": 31, "gterms": 27}


def scope(params):
    return (f"Exactly N(T) zeros of zeta(s) with 0 < Im s < T = {params['height']} (counted with multiplicity, "
            "certified by the argument principle), and Z(t) has that many certified sign changes on (0, T]: "
            "all of them are simple zeros on Re s = 1/2.")


def _text(x):
    return f"{float(x):.6f}"


def _z(series, t, cfg):
    re, im = LF.hardy_z(series, RI.exact(t, cfg["p"]), 0, cfg["factor"], cfg["extra"], cfg["terms"],
                        cfg["shift"], cfg["gterms"])
    return re, im


def search(params):
    T = Fraction(params["height"])
    cfg = SEARCH
    series = LF.LSeries(1, [1], cfg["p"])
    pieces = LF.find_pieces(series, T, cfg["factor"], cfg["extra"], cfg["terms"])
    n, _ = LF.argument_count(series, T, 0, pieces, cfg["factor"], cfg["extra"], cfg["terms"],
                             cfg["shift"], cfg["gterms"], pole=True)

    def evaluate(t):
        re, im = _z(series, t, cfg)
        if not im.contains_zero():
            raise RuntimeError(f"Im(e^(i theta) zeta) excludes 0 at t = {t}: theta or zeta enclosure is wrong")
        return re.sign(), float(re)

    pts, vals = LF.sample_points(series, T, 0, n, evaluate)
    signs = [vals[x][0] for x in pts]
    changes = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1) if signs[i] != signs[i + 1]]
    if len(changes) != n:
        raise RuntimeError(f"search found {len(changes)} sign changes for N(T) = {n}; refine the sampler")
    cert = {
        "height": str(T),
        "zero_count": n,
        "pieces": [list(x) for x in pieces],
        "points": [_text(x) for x in pts],
        "signs": signs,
    }
    return {
        "holds": True,
        "summary": {
            "height": str(T), "zeros": n, "sign_changes": len(changes), "points": len(pts),
            "boxes": len(pieces),
            "first_zero_bracket": [_text(changes[0][0]), _text(changes[0][1])] if changes else None,
            "last_zero_bracket": [_text(changes[-1][0]), _text(changes[-1][1])] if changes else None,
            "certificate_sha256": digest(cert),
        },
        "certificate": cert,
    }


def check(params, result):
    cert = result["certificate"]
    T = Fraction(params["height"])
    require(cert["height"] == str(T), "height differs from the parameters")
    require(result["holds"] is True, "this probe never reports counterexamples; a mismatch is a search failure")
    cfg = CHECK
    series = LF.LSeries(1, [1], cfg["p"])
    try:
        n, _ = LF.argument_count(series, T, 0, [tuple(x) for x in cert["pieces"]], cfg["factor"], cfg["extra"],
                                 cfg["terms"], cfg["shift"], cfg["gterms"], pole=True)
    except ValueError as exc:
        require(False, f"argument-principle certificate rejected: {exc}")
    require(n == cert["zero_count"], f"zero count {cert['zero_count']} differs from recomputed {n}")
    pts = [Fraction(x) for x in cert["points"]]
    require(len(pts) == len(cert["signs"]) and all(s in (1, -1) for s in cert["signs"]), "malformed signs")
    require(all(0 < a < b for a, b in zip(pts, pts[1:])) and pts and pts[0] > 0 and pts[-1] <= T,
            "points must increase strictly inside (0, T]")
    for t, sgn in zip(pts, cert["signs"]):
        re, im = _z(series, t, cfg)
        require(im.contains_zero(), f"Im(e^(i theta) zeta) excludes 0 at t = {t}")
        require(re.sign() == sgn, f"sign of Z({t}) not confirmed")
    changes = sum(1 for a, b in zip(cert["signs"], cert["signs"][1:]) if a != b)
    require(changes == n, f"{changes} sign changes do not account for N(T) = {n}")
    s = result["summary"]
    require(s["zeros"] == n and s["sign_changes"] == changes and s["points"] == len(pts)
            and s["boxes"] == len(cert["pieces"]), "summary mismatch")
    require(s["certificate_sha256"] == digest(cert), "certificate hash mismatch")
