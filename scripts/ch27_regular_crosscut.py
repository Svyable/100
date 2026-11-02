#!/usr/bin/env python3
"""Exact integer cross-cut certificate for the *regular* CH (27,9) branch.

NOT a graph enumerator: the mathematical reductions are proved separately in
proofs/M074_27_REGULAR.md. A passing check says nothing about the irregular
indegree-ten branch, independent review, or the general conjecture.
"""
import argparse
from itertools import combinations_with_replacement
import json


def profiles(arc_cap=29):
    """All sorted nine-entry internal degree profiles from the local lemma."""
    if type(arc_cap) is not int or not 18 <= arc_cap <= 30:
        raise ValueError("arc_cap must be an integer from 18 to 30")
    return tuple(xs for xs in combinations_with_replacement(range(2, 9), 9)
                 if sum(xs) <= arc_cap)


def eligible_cross_pairs(alpha, beta, threshold=10):
    """Necessary (not sufficient) triangle-avoidance condition on B->A."""
    if len(alpha) != 9 or len(beta) != 9:
        raise ValueError("both profiles must have nine entries")
    if type(threshold) is not int:
        raise ValueError("integer threshold required")
    return sum(a + b >= threshold for a in alpha for b in beta)


def required_cross_arcs(alpha, beta):
    """Regular indegree and outdegree force this many B->A arcs."""
    return max(81 - 2 * sum(alpha), 81 - 2 * sum(beta))


def certificate(arc_cap=29, threshold=10):
    samples = profiles(arc_cap)
    max_eligible = -1
    min_required = 82
    max_gap = -100
    possible = 0
    best_pair = None
    max_count = 0
    for alpha in samples:
        for beta in samples:
            allowed = eligible_cross_pairs(alpha, beta, threshold)
            required = required_cross_arcs(alpha, beta)
            if allowed > max_eligible:
                max_eligible = allowed
                best_pair = (alpha, beta)
                max_count = 0
            if allowed == max_eligible:
                max_count += 1
            min_required = min(min_required, required)
            max_gap = max(max_gap, allowed - required)
            if allowed >= required:
                possible += 1
    return {
        "profile_count": len(samples),
        "ordered_profile_pairs": len(samples) ** 2,
        "maximum_eligible_pairs": max_eligible,
        "minimum_required_cross_arcs": min_required,
        "maximum_allowed_minus_required": max_gap,
        "abstract_profiles_meeting_cross_requirement": possible,
        "maximizer_count": max_count,
        "example_maximizer_alpha": list(best_pair[0]),
        "example_maximizer_beta": list(best_pair[1]),
        "scope": ("Integer relaxations of regular 27-vertex C3-free oriented "
                  "candidates; no realizable global graph is asserted."),
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    args = p.parse_args(argv)
    result = certificate()
    if args.check:
        expected = {
            "profile_count": 166,
            "ordered_profile_pairs": 27556,
            "maximum_eligible_pairs": 22,
            "minimum_required_cross_arcs": 23,
            "maximum_allowed_minus_required": -1,
            "abstract_profiles_meeting_cross_requirement": 0,
        }
        for key, value in expected.items():
            if result[key] != value:
                raise SystemExit(f"CH27 regular certificate drift: {key}: {result[key]} != {value}")
        if certificate(30)["abstract_profiles_meeting_cross_requirement"] != 60:
            raise SystemExit("negative control failed: relaxing local 29-arc cap")
        if certificate(29, 9)["abstract_profiles_meeting_cross_requirement"] != 173:
            raise SystemExit("negative control failed: weakening triangle eligibility")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
