#!/usr/bin/env python3
"""Finite integer certificate for the (24,8) regular cross-cut obstruction.

This enumerates only possible degree *profiles*, not 24-vertex graphs.
See research/M074_ELEMENTARY_24_REGULAR.md for the mathematical proof.
"""
import itertools
import json


def admissible_profiles():
    """All sorted internal out-/in-degree profiles allowed by the 8-local arc budget."""
    return tuple(
        xs for xs in itertools.combinations_with_replacement(range(2, 8), 8)
        if sum(xs) <= 23
    )


def admissible_cross_pairs(alpha, beta):
    """Necessary (not sufficient) triangle-avoidance condition on a B->A arc."""
    return sum(a + b >= 9 for a in alpha for b in beta)


def required_cross_edges(alpha, beta):
    """Lower bound from regularity and the two root-neighborhood arc budgets."""
    return max(64 - 2 * sum(alpha), 64 - 2 * sum(beta))


def certificate():
    profiles = admissible_profiles()
    max_allowed = -1
    min_required = 65
    max_surplus = -65
    best = None
    violating = []
    for a in profiles:
        for b in profiles:
            allowed = admissible_cross_pairs(a, b)
            required = required_cross_edges(a, b)
            if allowed > max_allowed:
                max_allowed = allowed
                best = (a, b)
            min_required = min(min_required, required)
            max_surplus = max(max_surplus, allowed - required)
            if allowed >= required:
                violating.append((a, b, allowed, required))
    return {
        "profile_count": len(profiles),
        "ordered_profile_pairs": len(profiles) ** 2,
        "maximum_eligible_cross_pairs": max_allowed,
        "minimum_required_cross_edges": min_required,
        "maximum_allowed_minus_required": max_surplus,
        "eligible_ge_required_count": len(violating),
        "max_eligible_profile_a": best[0],
        "max_eligible_profile_b": best[1],
    }


def main():
    result = certificate()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if (result["profile_count"] == 42
                 and result["maximum_eligible_cross_pairs"] == 15
                 and result["minimum_required_cross_edges"] == 18
                 and result["eligible_ge_required_count"] == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
