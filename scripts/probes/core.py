"""Shared contract for exact probes.

A probe is a small module with:

* ``PROBE``  - static metadata (id, problem_id, engines, frontier, levels).
* ``search(params) -> dict`` - computes a result with an exact certificate.
* ``check(params, result)`` - an *independent* replay that raises
  :class:`ProbeFailure` if anything in the certificate is wrong.
* ``scope(params) -> str`` - the exact finite statement a passing run covers.

``search`` returns ``{"holds": bool, "summary": {...}, "certificate": ...}``.
If ``holds`` is False the certificate must contain a ``counterexample`` that
``check`` confirms. Nothing here promotes any result to "solved".
"""
import hashlib
import json
from fractions import Fraction


class ProbeFailure(Exception):
    """The independent checker rejected a certificate or summary."""


def require(condition, message):
    if not condition:
        raise ProbeFailure(message)


def _default(value):
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"not JSON-serialisable: {type(value).__name__}")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, default=_default)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("ascii")).hexdigest()


def fraction_text(value):
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"
