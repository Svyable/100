#!/usr/bin/env python3
"""Exact rational audits for the M073 equal-mass assortative two-block cone.

The continuum proof is in research/M073_ASSORTATIVE_TWO_BLOCK.md. The checker
only validates its source-specific integer coefficients and sample instances.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

EXPECTED_FACE_SHA = "653fd38252aa4034512303dd71d738a42cc3685666b982d41f21c76c336c4b02"
EXPECTED = {"vertices": 35, "edges": 66, "wedges": 204, "c4": 33, "c6": 88}


def load_faces(path=None):
    if path is None:
        path = Path(__file__).resolve().parents[1] / "data/reference/sidorenko_faces.json"
    obj = json.loads(Path(path).read_text())
    faces = tuple(tuple(f) for f in obj["faces"])
    canonical = json.dumps(faces, separators=(",", ":"))
    if (sha256(canonical.encode()).hexdigest() != EXPECTED_FACE_SHA
            or len(faces) != 22 or any(len(f) != 3 or len(set(f)) != 3
                                    or min(f) < 0 or max(f) >= 13 for f in faces)):
        raise ValueError("source triple table differs from pinned M073 pattern")
    return faces


def graph_counts(faces):
    adj = [set() for _ in range(35)]
    for j, face in enumerate(faces):
        for v in face:
            adj[v].add(13 + j)
            adj[13 + j].add(v)
    edges = sum(map(len, adj)) // 2
    wedges = sum(len(neighbors) * (len(neighbors) - 1) // 2 for neighbors in adj)

    def cycles(length):
        total = 0
        for root in range(len(adj)):
            def walk(path):
                if len(path) == length:
                    return int(root in adj[path[-1]] and path[1] < path[-1])
                return sum(walk(path + [v]) for v in adj[path[-1]]
                           if v > root and v not in path)
            total += walk([root])
        return total
    return {"vertices": len(adj), "edges": edges, "wedges": wedges,
            "c4": cycles(4), "c6": cycles(6)}


def histogram(faces):
    """Exact point-assignment histogram, after integrating all 22 face labels."""
    result = Counter()
    for mask in range(1 << 13):
        counts = [0, 0, 0, 0]
        for face in faces:
            zeros = sum(not (mask >> i) & 1 for i in face)
            counts[zeros] += 1
        result[tuple(counts)] += 1
    return result


def exact_gap(A, B, C, profiles):
    """Numerators for t(H,W)-p^66 and t(H,W)-claimed lower bound.

    A,B,C are nonnegative integer block weights; any common denominator D
    cancels after multiplication by (4D)^66. Returns exact signed integers.
    """
    if any(type(x) is not int or x < 0 for x in (A, B, C)):
        raise ValueError("weights must be nonnegative integers")
    face = [A**k * B**(3-k) + B**k * C**(3-k) for k in range(4)]
    T = sum(mult * (face[0]**h[0]) * (face[1]**h[1])
            * (face[2]**h[2]) * (face[3]**h[3])
            for h, mult in profiles.items())
    P, S, R = A + 2*B + C, A - C, A - 2*B + C
    base = P**66
    bound = base + 204*S*S*P**64 + 33*R**4*P**62 + 88*R**6*P**60
    lhs = (1 << 97)*T
    return lhs-base, lhs-bound


def audit():
    faces = load_faces()
    counts = graph_counts(faces)
    if counts != EXPECTED:
        raise AssertionError(f"source graph counts drifted: {counts}")
    profiles = histogram(faces)
    if sum(profiles.values()) != 8192 or len(profiles) != 372:
        raise AssertionError("point-assignment histogram drift")
    checked = 0
    strict = 0
    for A, B, C in ((a,b,c) for a in range(4) for b in range(4)
                    for c in range(4) if a+c >= 2*b):
        base, enhanced = exact_gap(A, B, C, profiles)
        if base < 0 or enhanced < 0:
            raise AssertionError(f"cone inequality fails: {(A,B,C)}")
        if A+B+C and not (A == B == C) and enhanced <= 0:
            raise AssertionError(f"strictness fails: {(A,B,C)}")
        strict += int(enhanced > 0)
        checked += 1
    # Noncone falsifier: enhanced bound fails, ordinary Sidorenko bound holds.
    base, enhanced = exact_gap(10, 10, 9, profiles)
    if base <= 0 or enhanced >= 0:
        raise AssertionError("outside-cone negative control lost")
    return {"source_sha256": EXPECTED_FACE_SHA, "counts": counts,
            "assignments": sum(profiles.values()), "distinct_profiles": len(profiles),
            "cone_integer_grid_cases": checked, "strict_grid_cases": strict,
            "outside_cone_control": {"weights": [10,10,9],
                                     "ordinary_gap_positive": base > 0,
                                     "enhanced_gap_negative": enhanced < 0},
            "scope": "Exact rational checks only; continuum proof is algebraic, not the grid"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    print(json.dumps(audit(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
