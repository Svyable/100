"""M002 — Generalized Riemann hypothesis for one Dirichlet character.

The same interval engine certifies the zeros of L(s, χ₄), the Dirichlet beta
function, up to a small height. χ₄ is the non-principal mod-4 character. A
matching argument count and Hardy-type sign changes show that every
non-trivial zero with imaginary part in (0, T] is simple and on the critical
line. This is one L-function at a classical height, not the generalized
Riemann hypothesis.
"""
from fractions import Fraction

from .core import ProbeFailure, require
from .zeta import CHECK, CertificationError, SEARCH, certify_chi4, replay_chi4

PROBE = {
    "id": "dirichlet_l",
    "problem_id": "M002",
    "title": "Critical-line zero count for L(s, chi_4) up to a small height",
    "engines": ["interval_arithmetic"],
    "frontier": ("Known: the first zeros of Dirichlet L-functions, including L(s, χ₄), "
                 "have been tabulated far beyond this height. The certificate is for the "
                 "single character χ₄. Reproduction only, and not a proof of GRH."),
    "levels": {"smoke": {"height": 11, "zeros": 2}, "deep": {"height": 17, "zeros": 4}},
}


def scope(params):
    height, zeros = params["height"], params["zeros"]
    return (f"Every non-trivial zero of L(s, χ₄) with imaginary part in (0, {height}] is simple "
            f"and lies on the critical line: the argument principle gives N({height}) = {zeros}, "
            "equal to the number of disjoint intervals where the associated real Z-function changes sign.")


def _pack(intervals):
    return [[f"{a.numerator}/{a.denominator}", f"{b.numerator}/{b.denominator}"] for a, b in intervals]


def search(params):
    try:
        found = certify_chi4(params["height"], params["zeros"], SEARCH)
    except CertificationError as exc:
        raise ProbeFailure(str(exc)) from exc
    return {
        "holds": True,
        "summary": {"height": params["height"], "zeros": params["zeros"],
                    "character": "chi_4", "truncation": SEARCH.label()},
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
        replay_chi4(params["height"], params["zeros"], intervals, CHECK)
    except (CertificationError, ValueError) as exc:
        raise ProbeFailure(str(exc)) from exc
    require(result["summary"]["character"] == "chi_4", "summary mismatch")
    require(result["summary"]["truncation"] == SEARCH.label(), "search truncation mismatch")
