#!/usr/bin/env python3
"""Exact M073 seven-vertex rung motif and antiferromagnetic stability check.

Mathematical continuum proof: research/M073_RUNG_CORRELATION.md.
Finite calculations audit source incidences, two independent correlation paths,
and rational threshold separation; they are not an independent review.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from itertools import product
from math import prod
import json

from m073_assortative2 import load_faces, histogram
from sidorenko_twoblock import numerator_by_faces, numerator_by_elimination

Q = Fraction
# 0=point i, 1=face f, 2=point j, 3=point k,
# 4=other face on ij, 5=other face on ik, 6=other face on jk.
RUNG_EDGES = ((0, 1), (0, 4), (4, 2), (2, 1),
              (0, 5), (5, 3), (3, 1), (2, 6), (6, 3))
DENOMINATOR = {0: 1, 4: 3, 6: 4}
NUMERATOR = {1: 1, 3: 2, 5: 3, 7: 2}
OLD_DENOMINATOR = {0: 1, 4: 2, 6: 1}
OLD_NUMERATOR = {1: 1, 3: 2, 7: 1}


def motifs(faces):
    """Check the full nine-edge pattern at all 66 source incidences."""
    if len(faces) != 22 or any(len(f) != 3 or len(set(f)) != 3 for f in faces):
        raise ValueError("requires 22 distinct triples")
    result = []
    for fi, face in enumerate(faces):
        for i in face:
            j, k = (v for v in face if v != i)
            alternates = []
            for x, y in ((i, j), (i, k), (j, k)):
                matches = [idx for idx, f in enumerate(faces)
                           if idx != fi and x in f and y in f]
                if len(matches) != 1:
                    raise ValueError("pair lacks a unique other face")
                alternates.append(matches[0])
            if len(set(alternates)) != 3:
                raise ValueError("three alternate faces must be distinct")
            gj, gk, gh = (13 + v for v in alternates)
            f = 13 + fi
            actual = {(min(a, b), max(a, b)) for a, b in (
                (i, f), (i, gj), (gj, j), (j, f),
                (i, gk), (gk, k), (k, f), (j, gh), (gh, k))}
            if len({i, f, j, k, gj, gk, gh}) != 7 or len(actual) != 9:
                raise ValueError("degenerate rung motif")
            for a, b in actual:
                if a < 13:
                    if a not in faces[b - 13]:
                        raise ValueError("motif contains absent incidence")
                elif b not in faces[a - 13]:
                    raise ValueError("motif contains absent incidence")
            result.append((i, fi, tuple(alternates)))
    if len(result) != 66:
        raise ValueError("expected 66 source incidence motifs")
    return result


def boundary_polynomial(odd=(), edges=RUNG_EDGES):
    """Enumerate 2^9 edge subsets; each selected vertex parity is exact."""
    counts = Counter()
    for bits in range(1 << len(edges)):
        parity = [0] * 7
        for e, (u, v) in enumerate(edges):
            if bits & (1 << e):
                parity[u] ^= 1
                parity[v] ^= 1
        if all(parity[v] == int(v in odd) for v in range(7)):
            counts[bits.bit_count()] += 1
    return dict(sorted(counts.items()))


def evaluate(poly, q):
    return sum((coefficient * q**degree for degree, coefficient
                in poly.items()), Q(0))


def direct_correlation(q):
    """Independent 2^7 spin assignments, no parity polynomial used."""
    if not 0 <= q < 1:
        raise ValueError("q must lie in [0,1)")
    total = signed = Q(0)
    for spins in product((-1, 1), repeat=7):
        weight = Q(1)
        for u, v in RUNG_EDGES:
            weight *= 1 + q * spins[u] * spins[v]
        total += weight
        signed += weight * spins[0] * spins[1]
    return signed / total


def multiply(a, b):
    result = Counter()
    for i, x in a.items():
        for j, y in b.items():
            result[i + j] += x * y
    return {k: v for k, v in result.items() if v}


def subtract(a, b):
    result = Counter(a)
    result.subtract(b)
    return {k: v for k, v in result.items() if v}


def expected_difference():
    """2q^5(1-q^2)^3(1+q^2), strictly positive on 0<q<1."""
    return multiply({5: 2}, multiply({0: 1, 2: -3, 4: 3, 6: -1},
                                      {0: 1, 2: 1}))


def sample():
    """Old tube misses this exact rational host; rung tube certifies it."""
    q = Q(1, 3)
    h = Q(41, 200)
    R = 1 - h*h
    A = Q(1114, 729)
    old_kappa = evaluate(OLD_NUMERATOR, q) / evaluate(OLD_DENOMINATOR, q)
    new_kappa = evaluate(NUMERATOR, q) / evaluate(DENOMINATOR, q)
    old_exp = Q(66, 4) * (1 - old_kappa)
    new_exp = Q(66, 4) * (1 - new_kappa)
    if (old_kappa, new_kappa, old_exp, new_exp) != (
            Q(223, 561), Q(23, 57), Q(169, 17), Q(187, 19)):
        raise AssertionError("rung correlation or exponent drift")
    old_power = A**old_exp.denominator * R**old_exp.numerator
    new_power = A**new_exp.denominator * R**new_exp.numerator
    if not old_power < 1 < new_power:
        raise AssertionError("old/new tube separation failed")
    # a=241/400, b=400/400, c=159/400. Thus p=3/4 and h=41/200.
    faces = load_faces()
    W = ((241, 400), (400, 159))
    direct = numerator_by_faces(faces, W)
    profiles = histogram(faces)
    factors = [241**z * 400**(3-z) + 400**z * 159**(3-z)
               for z in range(4)]
    compressed = sum(m * prod(factors[z]**count for z, count in enumerate(profile))
                     for profile, m in profiles.items())
    eliminated = numerator_by_elimination(faces, W)
    if not direct == compressed == eliminated:
        raise AssertionError("three exact density paths disagree")
    ratio = Q((1 << 97) * direct, 1200**66)
    if ratio <= 1 or ratio**new_exp.denominator < new_power:
        raise AssertionError("exact source density contradicts bound")
    return {
        "weights": ["241/400", "1", "159/400"],
        "q": str(q), "h": str(h),
        "old_kappa": str(old_kappa), "new_kappa": str(new_kappa),
        "old_exponent": str(old_exp), "new_exponent": str(new_exp),
        "old_bound_below_one": old_power < 1,
        "new_bound_above_one": new_power > 1,
        "exact_density_paths_agree": direct == compressed == eliminated,
        "exact_density_ratio_approx": round(float(ratio), 10),
        "new_bound_ratio_approx": round(float(A) * float(R)**float(new_exp), 10),
    }


def audit():
    faces = load_faces()
    witness = motifs(faces)
    D = boundary_polynomial()
    N = boundary_polynomial((0, 1))
    if (D, N) != (DENOMINATOR, NUMERATOR):
        raise AssertionError("high-temperature polynomials drifted")
    difference = subtract(multiply(N, OLD_DENOMINATOR),
                          multiply(OLD_NUMERATOR, D))
    if difference != expected_difference():
        raise AssertionError("strict correlation improvement identity failed")
    for q in (Q(0), Q(1, 5), Q(1, 3), Q(1, 2), Q(3, 4)):
        if direct_correlation(q) != evaluate(N, q) / evaluate(D, q):
            raise AssertionError("direct spins disagree with even subsets")
    return {
        "source_motifs": len(witness),
        "rung_edges": len(RUNG_EDGES),
        "rung_vertices": 7,
        "denominator_coefficients": D,
        "numerator_coefficients": N,
        "strict_improvement_polynomial": difference,
        "sample": sample(),
        "boundary": "Restricted two-block graphons only; no global Sidorenko claim",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.check and not result["sample"]["new_bound_above_one"]:
        raise SystemExit("INVALID")


if __name__ == "__main__":
    main()
