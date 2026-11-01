#!/usr/bin/env python3
"""Necessary small-subset obstruction for a CH (27,9) indegree-ten root.

This enumerates *integer degree profiles*, not 27-vertex digraphs.
Mathematics: proofs/M074_B_INTERNAL_GIRTH.md.
"""
from collections import Counter
from itertools import combinations_with_replacement

import ch27_z4_sink
import json


def alpha_profiles():
    return tuple(a for a in combinations_with_replacement(range(2, 9), 9)
                 if sum(a) <= 29)


def k_profiles_with_four_zeros():
    return tuple((0,) * 4 + positive for positive
                 in combinations_with_replacement(range(1, 8), 6))


def internal_B_floors(alpha, k):
    if (len(alpha) != 9 or any(type(x) is not int or x < 2 or x > 8 for x in alpha)
            or len(k) != 10 or any(type(x) is not int or x < 0 or x > 7 for x in k)):
        raise ValueError("invalid local degree arrays")
    q = tuple(sum(a >= degree + 2 for a in alpha) for degree in k)
    return tuple(sorted((max(0, 1 + degree - eligible)
                         for degree, eligible in zip(k, q)), reverse=True))


def subset_capacity_ok(floors):
    return all(sum(floors[:s]) <= s * (19 - s) // 2
               for s in range(1, 11))


def forbidden_small_set(floors, include_triangle=True):
    """The floor conditions imply a forbidden induced min-outdegree."""
    if len(floors) != 10 or tuple(sorted(floors, reverse=True)) != tuple(floors):
        raise ValueError("expected ten descending lower bounds")
    if include_triangle and floors[2] >= 8:
        return "triangle_three"
    for s in (4, 5, 6):
        if floors[s - 1] >= 12 - s:
            return f"minout_two_{s}"
    return None


def classify(alpha, k, include_triangle=True):
    m = sum(alpha)
    if sum(k) < 92 - 2*m:
        return "cut"
    floors = internal_B_floors(alpha, k)
    if not subset_capacity_ok(floors):
        return "subset_capacity"
    prior_cut = forbidden_small_set(floors, include_triangle)
    if prior_cut:
        return prior_cut
    # Scope: z=4 and alpha=(2^7,a,8), 2<=a<=6, ONLY.
    # Hand proof: proofs/M074_27_Z4_SINK.md (seven-vertex cap prerequisite).
    if ch27_z4_sink.target_profile(alpha, k):
        return "z4_sink_cut"
    return "unresolved"


def audit(include_triangle=True):
    alphas = alpha_profiles()
    ks = k_profiles_with_four_zeros()
    counts = Counter()
    survivor = None
    for alpha in alphas:
        for k in ks:
            result = classify(alpha, k, include_triangle)
            counts[result] += 1
            if result == "unresolved" and survivor is None:
                survivor = (alpha, k)
    return {
        "alpha_profiles": len(alphas),
        "k_profiles_z4": len(ks),
        "pairs": len(alphas) * len(ks),
        "stages": dict(sorted(counts.items())),
        "sample_unresolved_profile": survivor,
        "scope": "Relaxed z=4 necessary integer profiles; no graph realizability claim",
    }


def main():
    baseline = audit()
    mutated = audit(include_triangle=False)
    example = ((2,)*7 + (6,8), (0,)*4 + (4,5,6,7,7,7))
    result = {"exact": baseline, "triangle_guard_removed": mutated,
              "former_boundary_case": {
                  "alpha": example[0], "k": example[1],
                  "floors": internal_B_floors(*example),
                  "rejection": classify(*example),
              }}
    print(json.dumps(result, indent=2, sort_keys=True))
    if (baseline["alpha_profiles"], baseline["k_profiles_z4"], baseline["pairs"]) != (166,924,153384):
        raise SystemExit("INVALID: profile generator")
    expected = {
        "cut": 149396,
        "subset_capacity": 3515,
        "triangle_three": 132,
        "minout_two_5": 22,
        "minout_two_6": 24,
        "z4_sink_cut": 4,
        "unresolved": 291,
    }
    if baseline["stages"] != expected or mutated["stages"].get("unresolved") != 421:
        raise SystemExit("INVALID: small-set cut audit drift")
    if result["former_boundary_case"]["rejection"] != "triangle_three":
        raise SystemExit("INVALID: triangle guard did not reject control")


if __name__ == "__main__":
    main()
