#!/usr/bin/env python3
"""Sharp directed-girth edge deficit and a scoped CH(27,9) z=4 profile filter.

Proof: proofs/M074_GIRTH_DEFICIT.md.
The procedure enumerates NECESSARY INTEGER PROFILES, not digraphs or an
UNSAT certificate for the full 27-vertex problem.
"""
import argparse
from collections import Counter
import json

import ch27_b_internal as prior


def required_missing_edges(girth):
    """Chord deficit of a shortest directed cycle (girth >= 4)."""
    if type(girth) is not int or girth < 4:
        raise ValueError("oriented girth must be an integer >=4")
    return girth * (girth - 3) // 2


def first_girth_subset_violation(floors, missing=2):
    """For N=10: a high-floor s-set has minout 1 and >=missing nonedges."""
    if (len(floors) != 10 or
            tuple(sorted(floors, reverse=True)) != tuple(floors) or
            any(type(f) is not int or f < 0 for f in floors) or
            type(missing) is not int or missing < 0):
        raise ValueError("expected ten descending nonnegative floors and deficit")
    for s in range(4, 11):
        if floors[s - 1] >= 11-s:
            demand = sum(floors[:s])
            capacity = s * (19-s) // 2 - missing
            if demand > capacity:
                return s
    return None


def c_cut_violation(alpha, k):
    """Only asserted for at least seven fully C-saturating A-neighbors."""
    if len(alpha) != 9 or len(k) != 10:
        raise ValueError("unexpected profile sizes")
    return alpha.count(2) >= 7 and sum(k) < 65 - sum(alpha)


def classify(alpha, k, missing=2, include_c=True):
    baseline = prior.classify(alpha, k)
    if baseline != "unresolved":
        return baseline
    violation = first_girth_subset_violation(prior.internal_B_floors(alpha, k), missing)
    if violation is not None:
        return f"girth_subset_{violation}"
    if include_c and c_cut_violation(alpha, k):
        return "seven_vertex_c_cut"
    return "unresolved"


def audit(missing=2, include_c=True):
    counts = Counter()
    first_remaining = None
    for a in prior.alpha_profiles():
        for k in prior.k_profiles_with_four_zeros():
            classification = classify(a, k, missing, include_c)
            counts[classification] += 1
            if classification == "unresolved" and first_remaining is None:
                first_remaining = (a, k)
    return {"total_pairs": sum(counts.values()),
            "classification": dict(sorted(counts.items())),
            "baseline_survivors": 295,
            "remaining": counts["unresolved"],
            "first_remaining_relaxed_profile": first_remaining,
            "scope": "relaxed z=4 degree profiles only; no graph realization"}


def certificate():
    return {
        "girth4_missing_edge_deficit": required_missing_edges(4),
        "girth5_missing_edge_deficit": required_missing_edges(5),
        "exact": audit(),
        "weakened_one_missing_edge": audit(missing=1),
        "no_new_B_cut": audit(missing=0),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = certificate()
    print(json.dumps(result, sort_keys=True, indent=2))
    if args.check:
        x = result["exact"]
        assert x["total_pairs"] == 153384
        assert x["classification"] == {
            "cut": 149396, "subset_capacity": 3515,
            "triangle_three": 132, "minout_two_5": 22,
            "minout_two_6": 24,
            "girth_subset_4": 74, "girth_subset_5": 49,
            "girth_subset_6": 29, "seven_vertex_c_cut": 15,
            "unresolved": 128,
        }, x["classification"]
        assert x["first_remaining_relaxed_profile"] == (
            (2,)*7 + (7, 8), (0,)*4 + (5, 5, 6, 6, 7, 7)
        )
        assert result["weakened_one_missing_edge"]["remaining"] == 191
        assert result["no_new_B_cut"]["remaining"] == 275
        assert result["girth4_missing_edge_deficit"] == 2
        assert result["girth5_missing_edge_deficit"] == 5


if __name__ == "__main__":
    main()
