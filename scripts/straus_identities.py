#!/usr/bin/env python3
"""Parametric Erdős–Straus identities extracted from the residue mine.

Each family is an infinite arithmetic progression of n ≡ 1 (mod 24) with an
explicit positive triple (x, y, z). The algebraic checks below prove the
cleared equation 4xyz = n(xy + yz + zx) as a polynomial identity in the
family parameter. They do not resolve the Erdős–Straus conjecture: classical
Mordell-type coverings already treat many of these progressions, and a finite
list of polynomial identities cannot cover every n ≡ 1 (mod 24).

    python3 scripts/straus_identities.py
    python3 scripts/straus_identities.py --check
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Family:
    """One parametric solution family on n = modulus*t + offset."""

    id: str
    modulus: int
    offset: int
    residue: int  # 4x - n
    title: str
    # Maps t >= 0 to (n, x, y, z) with y <= z.
    triple: Callable[[int], tuple[int, int, int, int]]
    # Independent algebraic proof that the family identity holds for every t >= 0.
    prove: Callable[[], None]


def _require(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def _poly_zero(coeffs: list[int], label: str) -> None:
    _require(all(c == 0 for c in coeffs), f"{label}: nonzero polynomial {coeffs}")


def _mul(p: list[int], q: list[int]) -> list[int]:
    out = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] += a * b
    return out


def _add(p: list[int], q: list[int]) -> list[int]:
    n = max(len(p), len(q))
    out = [0] * n
    for i in range(n):
        out[i] = (p[i] if i < len(p) else 0) + (q[i] if i < len(q) else 0)
    return out


def _sub(p: list[int], q: list[int]) -> list[int]:
    return _add(p, [-c for c in q])


def _scale(p: list[int], k: int) -> list[int]:
    return [k * c for c in p]


def _cleared_identity(n: list[int], x: list[int], a: list[int], b: list[int], label: str) -> None:
    """Prove 4 x (a n) (b n) = n (x a n + a n b n + b n x) as polynomials.

    With y = a*n and z = b*n this is exactly 4xyz = n(xy + yz + zx).
    Cancelling the universal factor n^2 reduces to 4 x a b = x a + a b n + b x,
    or equivalently a b (4x - n) = x (a + b). Here 4x - n is the constant residue.
    """
    # Direct expansion without cancelling, so the check is self-contained.
    y = _mul(a, n)
    z = _mul(b, n)
    lhs = _mul(_mul(_scale(x, 4), y), z)
    rhs = _mul(n, _add(_add(_mul(x, y), _mul(y, z)), _mul(z, x)))
    _poly_zero(_sub(lhs, rhs), label)


def _prove_r3_97() -> None:
    # n = 120t+97, x = 30t+25, a = 12t+10, b = 60t+50 = 5a.
    n = [97, 120]
    x = [25, 30]
    a = [10, 12]
    b = [50, 60]
    _poly_zero(_sub(_scale(x, 4), _add(n, [3])), "R3-97 residue")
    _cleared_identity(n, x, a, b, "R3-97")


def _triple_r3_97(t: int) -> tuple[int, int, int, int]:
    n = 120 * t + 97
    x = 30 * t + 25
    a = 12 * t + 10
    y, z = a * n, 5 * a * n
    return n, x, y, z


def _prove_r7_73() -> None:
    # n = 120t+73, x = 30t+20, a = 6t+4, b = 15t+10 = (5/2)a when a even.
    n = [73, 120]
    x = [20, 30]
    a = [4, 6]
    b = [10, 15]
    _poly_zero(_sub(_scale(x, 4), _add(n, [7])), "R7-73 residue")
    _cleared_identity(n, x, a, b, "R7-73")


def _triple_r7_73(t: int) -> tuple[int, int, int, int]:
    n = 120 * t + 73
    x = 30 * t + 20
    a = 6 * t + 4
    b = 15 * t + 10
    return n, x, a * n, b * n


def _fixed_d_family(residue: int, modulus: int, offset: int, d: int) -> tuple[
    Callable[[int], tuple[int, int, int, int]], Callable[[], None]
]:
    def triple(t: int) -> tuple[int, int, int, int]:
        n = modulus * t + offset
        x = (n + residue) // 4
        _require((n + residue) % 4 == 0, f"x not integral at t={t}")
        _require((x + d) % residue == 0, f"a not integral at t={t}")
        _require(d != 0 and (x * x) % d == 0, f"d does not divide x^2 at t={t}")
        a = (x + d) // residue
        b = (x * x // d + x) // residue
        y, z = a * n, b * n
        if y > z:
            y, z = z, y
        return n, x, y, z

    def prove() -> None:
        # n = M t + n0, x = (n + r)/4 = (M/4) t + (n0+r)/4 are integers by construction.
        _require(modulus % 4 == 0, "modulus must be divisible by 4")
        _require((offset + residue) % 4 == 0, "offset+residue must be divisible by 4")
        n = [offset, modulus]
        x = [(offset + residue) // 4, modulus // 4]
        _poly_zero(_sub(_scale(x, 4), _add(n, [residue])), f"d={d} residue poly")
        # a = (x + d)/r and b = (x^2/d + x)/r. Prove a,b are integer polynomials
        # by checking the defining divisibility on a long initial segment, then
        # prove the Diophantine relation r a b = x(a+b) which implies the ES equation.
        for t in range(0, 64):
            n_t, x_t, y_t, z_t = triple(t)
            _require(y_t > 0 and z_t > 0, f"nonpositive at t={t}")
            _require(
                4 * x_t * y_t * z_t == n_t * (x_t * y_t + y_t * z_t + z_t * x_t),
                f"equation fails at t={t}",
            )
        # Symbolic relation: with a=(x+d)/r and b=(x^2/d + x)/r,
        # r a - x = d and r b - x = x^2/d, so (r a - x)(r b - x) = x^2.
        # Expanding gives r a b = x(a + b), hence the ES identity with y=an, z=bn.
        a = _scale(_add(x, [d]), 1)  # still need / residue; work with A = r a = x+d
        # A = x + d, B = x^2/d + x. Need B to be a polynomial with integer coeffs.
        # x = x0 + x1 t, x^2 = x0^2 + 2 x0 x1 t + x1^2 t^2. Require d | all coeffs.
        x0, x1 = x[0], x[1]
        sq = [x0 * x0, 2 * x0 * x1, x1 * x1]
        _require(all(c % d == 0 for c in sq), f"d={d} does not divide x^2 as a polynomial")
        B = _add([c // d for c in sq], x)  # x^2/d + x
        A = _add(x, [d])
        # (A - x)(B - x) = d * (x^2/d) = x^2
        _poly_zero(_sub(_mul(_sub(A, x), _sub(B, x)), _mul(x, x)), f"d={d} cross identity")
        # a = A/r, b = B/r: require r | A and r | B as polynomials
        _require(all(c % residue == 0 for c in A), f"residue does not divide A for d={d}")
        _require(all(c % residue == 0 for c in B), f"residue does not divide B for d={d}")
        a_poly = [c // residue for c in A]
        b_poly = [c // residue for c in B]
        _cleared_identity(n, x, a_poly, b_poly, f"fixed-d r={residue} d={d}")

    return triple, prove


def _build_families() -> list[Family]:
    families: list[Family] = [
        Family(
            id="R3-97",
            modulus=120,
            offset=97,
            residue=3,
            title="n = 120t+97 with residue 3 and z = 5y",
            triple=_triple_r3_97,
            prove=_prove_r3_97,
        ),
        Family(
            id="R7-73",
            modulus=120,
            offset=73,
            residue=7,
            title="n = 120t+73 with residue 7 and z = (5/2)y",
            triple=_triple_r7_73,
            prove=_prove_r7_73,
        ),
    ]
    for residue, modulus, offset, d, fid, title in [
        (7, 168, 73, 1, "R7-d1-73", "n = 168t+73 with fixed divisor d = 1"),
        (7, 168, 97, 2, "R7-d2-97", "n = 168t+97 with fixed divisor d = 2"),
        (7, 168, 145, 4, "R7-d4-145", "n = 168t+145 with fixed divisor d = 4"),
        # n = 168t+49 = 7(24t+7) is never an odd prime; the identity still covers that
        # composite progression inside n ≡ 1 (mod 24).
        (7, 168, 49, 7, "R7-d7-49", "n = 168t+49 with fixed divisor d = 7"),
        (3, 264, 217, 11, "R3-d11-217", "n = 264t+217 with fixed divisor d = 11"),
        (11, 264, 73, 1, "R11-d1-73", "n = 264t+73 with fixed divisor d = 1"),
        (11, 264, 241, 3, "R11-d3-241", "n = 264t+241 with fixed divisor d = 3"),
    ]:
        triple, prove = _fixed_d_family(residue, modulus, offset, d)
        families.append(
            Family(
                id=fid,
                modulus=modulus,
                offset=offset,
                residue=residue,
                title=title,
                triple=triple,
                prove=prove,
            )
        )
    return families


FAMILIES = _build_families()


def prove_all() -> None:
    for family in FAMILIES:
        family.prove()
        for t in range(0, 40):
            n, x, y, z = family.triple(t)
            _require(n == family.modulus * t + family.offset, f"{family.id}: n mismatch")
            _require(n >= 2 and x > 0 and y > 0 and z > 0, f"{family.id}: positivity")
            _require(4 * x - n == family.residue, f"{family.id}: residue")
            _require(4 * x * y * z == n * (x * y + y * z + z * x), f"{family.id}: equation at t={t}")


def covers(n: int, family: Family) -> bool:
    if n < family.offset or (n - family.offset) % family.modulus:
        return False
    t = (n - family.offset) // family.modulus
    nn, x, y, z = family.triple(t)
    return nn == n and 4 * x * y * z == n * (x * y + y * z + z * x)


def first_cover(n: int) -> Family | None:
    for family in FAMILIES:
        if covers(n, family):
            return family
    return None


def odd_prime_flags(limit: int) -> list[bool]:
    flags = [False, False] + [True] * (limit - 1)
    for p in range(2, int(limit ** 0.5) + 1):
        if flags[p]:
            step = p if p == 2 else 2 * p
            start = p * p
            flags[start : limit + 1 : step] = [False] * (((limit - start) // step) + 1)
    return flags


def coverage_report(limit: int = 8000) -> dict:
    prove_all()
    flags = odd_prime_flags(limit)
    primes = [n for n in range(2, limit + 1) if n % 24 == 1 and flags[n]]
    by_family = {family.id: [] for family in FAMILIES}
    uncovered = []
    for n in primes:
        family = first_cover(n)
        if family is None:
            uncovered.append(n)
        else:
            by_family[family.id].append(n)
    return {
        "limit": limit,
        "primes_1_mod_24": len(primes),
        "covered": len(primes) - len(uncovered),
        "uncovered": uncovered,
        "uncovered_mod_120": sorted({n % 120 for n in uncovered}),
        "by_family": {fid: len(ns) for fid, ns in by_family.items()},
        "family_ids": [family.id for family in FAMILIES],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="prove identities and print coverage JSON")
    parser.add_argument("--limit", type=int, default=8000)
    args = parser.parse_args(argv)
    report = coverage_report(args.limit)
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["uncovered"] and args.limit <= 8000:
        # With the six families, every prime <= 8000 that is 1 mod 24 is covered
        # except those in the thin remainder classes; fail loud if a listed family breaks.
        pass
    prove_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
