#!/usr/bin/env python3
"""Exact M073 spectrum via spin characters and a separate parity-state census.

Classical identities; source-specific certificate, not a novelty/acceptance claim.
Coefficients[k] counts even incidence-edge subsets of size 2*k.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from math import comb
from pathlib import Path

import sidorenko_twoblock as baseline

ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE = ROOT / "data/experiments/m073_information_alignment.json"


def validate_faces(faces, points):
    if type(points) is not int or points < 0:
        raise ValueError("nonnegative integer point count required")
    faces = tuple(tuple(f) for f in faces)
    if any(len(f) != 3 or len(set(f)) != 3 or
           any(type(v) is not int or not 0 <= v < points for v in f)
           for f in faces):
        raise ValueError("three distinct in-range integer points per face required")
    # Repeated triples are allowed: they represent distinct incidence vertices.
    return faces


def monochromatic_histogram(faces, points):
    """Full point-spin census, including isolated points and global spin flips."""
    faces = validate_faces(faces, points)
    histogram = [0] * (len(faces) + 1)
    for mask in range(1 << points):
        monochromatic = sum(
            ((mask >> u) & 1) == ((mask >> v) & 1) == ((mask >> w) & 1)
            for u, v, w in faces)
        histogram[monochromatic] += 1
    return histogram


def coefficients_by_spins(faces, points):
    """Expand E[(1+3x)^A (1-x)^(f-A)] exactly, x=r^2."""
    faces = validate_faces(faces, points)
    f = len(faces)
    hist = monochromatic_histogram(faces, points)
    numerators = [0] * (f + 1)
    for a, count in enumerate(hist):
        for i in range(a + 1):
            for j in range(f - a + 1):
                numerators[i+j] += count * comb(a, i) * 3**i * comb(f-a, j) * (-1)**j
    denominator = 1 << points
    if any(n % denominator for n in numerators):
        raise AssertionError("nonintegral even-subgraph coefficient")
    result = [n // denominator for n in numerators]
    if any(n < 0 for n in result):
        raise AssertionError("negative even-subgraph coefficient")
    return result


def coefficients_by_parity(faces, points):
    """Independent combinatorial DP: choose zero or two edges at each face.

    State = (odd-degree point bitmask, number of selected edge pairs).
    No spin histogram, cancellation, division, or polynomial transform is used.
    """
    faces = validate_faces(faces, points)
    states = {0: [1]}
    for face in faces:
        length = len(next(iter(states.values()))) + 1
        updated = {}
        toggles = [(1 << u) | (1 << v) for u, v in combinations(face, 2)]
        for mask, counts in states.items():
            target = updated.setdefault(mask, [0] * length)
            for k, count in enumerate(counts):
                target[k] += count
            for toggle in toggles:
                target = updated.setdefault(mask ^ toggle, [0] * length)
                for k, count in enumerate(counts):
                    target[k+1] += count
        states = updated
    return states[0]


def graphon_replay(coefficients, faces, points, a, b):
    """Integer identity at W=[[a,b],[b,a]], with normalization cross-multiplied.

    Dividing a,b by any positive D >= max(a,b) gives a graphon; D cancels.
    """
    if any(type(v) is not int or v < 0 for v in (a, b)):
        raise ValueError("nonnegative integer weights required")
    m, n = 3 * len(faces), points + len(faces)
    polynomial = sum(c * (a-b)**(2*k) * (a+b)**(m-2*k)
                     for k, c in enumerate(coefficients))
    edges = [(v, points+j) for j, face in enumerate(faces) for v in face]
    numerator = baseline.numerator_by_edges(n, edges, baseline.weights(a, b, a))
    if (1 << m) * numerator != (1 << n) * polynomial:
        raise AssertionError("pairwise-edge graphon replay differs from spectrum")


def make_certificate():
    faces = baseline.read_faces()
    coefficients = coefficients_by_spins(faces, 13)
    alternate = coefficients_by_parity(faces, 13)
    if coefficients != alternate:
        raise AssertionError("spin transform and parity DP disagree")
    if coefficients[:4] != [1, 0, 33, 88] or sum(coefficients) != 2**32:
        raise AssertionError("known low coefficients or cycle-rank checksum differ")
    return {
        "schema": "svyable.m073.information-alignment.v1",
        "face_sha256": baseline.FACES_SHA256,
        "points": 13, "faces": 22, "edges": 66,
        "variable": "x=r^2; coefficient[k] counts even edge subsets of size 2*k",
        "monochromatic_face_histogram": monochromatic_histogram(faces, 13),
        "coefficients": coefficients,
        "total_even_subgraphs": sum(coefficients),
        "cross_check": "all coefficients equal direct parity-state dynamic program",
        "boundary": "Equal-mass equal-diagonal two-block graphons only. Classical identities; historical novelty and independent mathematical review not established."
    }


def check_certificate(record):
    if record != make_certificate():
        raise AssertionError("stored spectrum certificate differs from exact replay")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = make_certificate()
    if args.write:
        CERTIFICATE.write_text(json.dumps(report, indent=2) + "\n")
    if args.check:
        if json.loads(CERTIFICATE.read_text()) != report:
            raise AssertionError("stored certificate differs from exact replay")
        faces = baseline.read_faces()
        for a, b in ((0, 0), (1, 1), (1, 0), (0, 1), (1, 3), (3, 1)):
            graphon_replay(report["coefficients"], faces, 13, a, b)
        print("M073: all 23 coefficients agree by spin/parity paths; 6 exact edge-factor replays passed")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
