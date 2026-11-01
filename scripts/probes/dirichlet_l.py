"""M002 — Generalized Riemann hypothesis for three real characters.

The interval engine certifies the zeros of L(s, χ) for the primitive real
characters χ₄, χ₃ and (at the deep level) the Legendre symbol modulo 5.
Each has root number +1. A matching argument count and sign changes of the
associated real Z-function show that every non-trivial zero up to the stated
height is simple and on the critical line. Three characters are not the
generalized Riemann hypothesis.
"""
from fractions import Fraction

from .core import ProbeFailure, require
from .zeta import (CHECK, CHI3, CHI4, CHI5, CertificationError, SEARCH,
                   certify_character, replay_character)

CHARACTERS = {"chi4": CHI4, "chi3": CHI3, "chi5": CHI5}

PROBE = {
    "id": "dirichlet_l",
    "problem_id": "M002",
    "title": "Critical-line zero counts for the real characters modulo 3, 4 and 5",
    "engines": ["interval_arithmetic"],
    "frontier": ("Known: zeros of Dirichlet L-functions have been tabulated far beyond "
                 "these heights. The certificate covers three real primitive characters "
                 "only. Reproduction only, and not a proof of GRH."),
    "levels": {
        "smoke": {"chi4_height": 11, "chi4_zeros": 2, "chi3_height": 9, "chi3_zeros": 1},
        "deep": {"chi4_height": 17, "chi4_zeros": 4, "chi3_height": 15, "chi3_zeros": 2,
                 "chi5_height": 12, "chi5_zeros": 3},
    },
}


def _requested(params):
    found = []
    for name in CHARACTERS:
        height, zeros = f"{name}_height", f"{name}_zeros"
        if height in params or zeros in params:
            if height not in params or zeros not in params:
                raise ProbeFailure(f"{name} needs both a height and a zero count")
            found.append(name)
    if not found:
        raise ProbeFailure("no character requested")
    return found


def scope(params):
    labels = {"chi4": "χ₄", "chi3": "χ₃", "chi5": "χ₅ (Legendre symbol mod 5)"}
    pieces = []
    for name in _requested(params):
        height, zeros = params[f"{name}_height"], params[f"{name}_zeros"]
        pieces.append(f"{labels[name]} on (0, {height}] with N({height}) = {zeros}")
    return ("Critical-line certificates for " + "; ".join(pieces) +
            ". Each argument count equals the number of disjoint intervals where that "
            "character's real Z-function changes sign, so every non-trivial zero in those "
            "ranges is simple and on the critical line.")


def _pack(intervals):
    return [[f"{a.numerator}/{a.denominator}", f"{b.numerator}/{b.denominator}"] for a, b in intervals]


def search(params):
    certificate = {}
    try:
        for name in _requested(params):
            chi = CHARACTERS[name]
            found = certify_character(params[f"{name}_height"], params[f"{name}_zeros"], SEARCH, chi)
            certificate[name] = {
                "height": str(params[f"{name}_height"]),
                "zeros": params[f"{name}_zeros"],
                "intervals": _pack(found),
            }
    except CertificationError as exc:
        raise ProbeFailure(str(exc)) from exc
    return {
        "holds": True,
        "summary": {"characters": list(certificate), "truncation": SEARCH.label(),
                    "zeros": {name: row["zeros"] for name, row in certificate.items()}},
        "certificate": certificate,
    }


def check(params, result):
    cert = result["certificate"]
    require(result["holds"] is True, "a failed zero count is an engine error, not a counterexample")
    names = _requested(params)
    require(set(cert) == set(names), "certificate characters do not match the request")
    for name in names:
        row = cert[name]
        height, zeros = params[f"{name}_height"], params[f"{name}_zeros"]
        require(row["height"] == str(height) and row["zeros"] == zeros, f"{name}: height mismatch")
        require(len(row["intervals"]) == zeros, f"{name}: interval count mismatch")
        try:
            intervals = [(Fraction(a), Fraction(b)) for a, b in row["intervals"]]
            replay_character(height, zeros, intervals, CHECK, CHARACTERS[name])
        except (CertificationError, ValueError) as exc:
            raise ProbeFailure(str(exc)) from exc
    require(result["summary"]["truncation"] == SEARCH.label(), "search truncation mismatch")
    require(result["summary"]["zeros"] == {name: params[f"{name}_zeros"] for name in names},
            "summary mismatch")
