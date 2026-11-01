"""M001 — Riemann hypothesis, as a finite zero count.

N(T) is computed from the argument principle (Riemann–von Mangoldt) and
compared with sign changes of the Hardy Z-function. Agreement certifies that
every non-trivial zero with imaginary part in (0, T] is simple and on the
critical line. The search and the check use different Euler–Maclaurin and
Stirling truncations. Nothing here reaches the published verification heights,
and nothing is a proof of the Riemann hypothesis.
"""
from fractions import Fraction

from .core import ProbeFailure, require
from .zeta import (CHECK, CertificationError, SEARCH, certify_riemann, replay_riemann)

PROBE = {
    "id": "riemann",
    "problem_id": "M001",
    "title": "Critical-line zero count for zeta up to a small height",
    "engines": ["interval_arithmetic"],
    "frontier": ("Known: every non-trivial zero with imaginary part up to at least "
                 "3*10^12 lies on the critical line (Platt and Trudgian, and later "
                 "computations go further). T <= 36 is classical. Reproduction only."),
    "levels": {"smoke": {"height": 23, "zeros": 2}, "deep": {"height": 36, "zeros": 5}},
}


def scope(params):
    height, zeros = params["height"], params["zeros"]
    return (f"Every non-trivial zero of zeta with imaginary part in (0, {height}] is simple and "
            f"lies on the critical line: the argument principle gives N({height}) = {zeros}, equal "
            "to the number of disjoint intervals where the Hardy Z-function changes sign.")


def _pack(intervals):
    return [[f"{a.numerator}/{a.denominator}", f"{b.numerator}/{b.denominator}"] for a, b in intervals]


def search(params):
    try:
        found = certify_riemann(params["height"], params["zeros"], SEARCH)
    except CertificationError as exc:
        raise ProbeFailure(str(exc)) from exc
    return {
        "holds": True,
        "summary": {"height": params["height"], "zeros": params["zeros"],
                    "truncation": SEARCH.label()},
        "certificate": {"height": str(params["height"]), "zeros": params["zeros"],
                        "intervals": _pack(found)},
    }


def check(params, result):
    cert = result["certificate"]
    require(result["holds"] is True, "a failed zero count is an engine error, not a counterexample")
    require(cert["height"] == str(params["height"]) and cert["zeros"] == params["zeros"],
            "certificate does not match the requested height")
    require(len(cert["intervals"]) == params["zeros"], "interval count mismatch")
    try:
        intervals = [(Fraction(a), Fraction(b)) for a, b in cert["intervals"]]
        replay_riemann(params["height"], params["zeros"], intervals, CHECK)
    except (CertificationError, ValueError) as exc:
        raise ProbeFailure(str(exc)) from exc
    require(result["summary"]["zeros"] == params["zeros"], "summary mismatch")
    require(result["summary"]["truncation"] == SEARCH.label(), "search truncation mismatch")
