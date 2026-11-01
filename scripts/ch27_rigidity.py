#!/usr/bin/env python3
"""Rigidity transfer at the CH (27,9) indegree-ten root.

The eight-vertex equality theorem is proved in
proofs/M074_EIGHT_VERTEX_RIGIDITY.md. This program only checks the
necessary *integer* implications for the historical z=4 profile
universe before later C-to-A and sink cuts. All z=4 cases were subsequently
excluded by stronger other work. This is neither an independently current
search frontier, nor a 27-vertex graph enumeration, nor a novelty review.
"""
import argparse
from collections import Counter
from itertools import combinations_with_replacement
import json

from ch27_b_internal import (
    alpha_profiles, k_profiles_with_four_zeros, internal_B_floors,
    subset_capacity_ok, forbidden_small_set,
)

RIGID_ALPHA = (2,) * 7 + (7, 8)


def rigidity_falsifier(alpha):
    """Return True for a profile contrary to the proved source-chain lemma."""
    if len(alpha) != 9 or tuple(sorted(alpha)) != tuple(alpha):
        raise ValueError("nine sorted internal outdegrees required")
    m = sum(alpha)
    return m == 29 and alpha[-1] == 8 and tuple(alpha) != RIGID_ALPHA


def c_cut_falsifier(alpha, k):
    """The pre-existing sharp seven-vertex cap, applied when seven alpha=2."""
    if len(alpha) != 9 or len(k) != 10:
        raise ValueError("need nine alpha and ten k values")
    return alpha.count(2) >= 7 and 81 - sum(alpha) - sum(k) > 16


def historical_z4_baseline(alpha, k):
    """The frozen B-subset/small-girth necessary filter from before z4 sink cuts.

    Later C-to-A and sink-cut results are intentionally NOT applied here:
    this checks the original 295-pair comparison for independent reproducibility.
    """
    if sum(k) < 92 - 2 * sum(alpha):
        return False
    floors = internal_B_floors(alpha, k)
    return subset_capacity_ok(floors) and forbidden_small_set(floors) is None


def equality_degree_profiles():
    """Independent *arithmetic* audit of the 21-arc equality proof.

    All 8 indegrees are at most 3, and the improved local outdegree bounds
    for indegree b = 0,1,2,3 are respectively 7,5,3,2.
    This checks the degree sum obstruction, not realizability.
    """
    possible = []
    for seq in combinations_with_replacement(range(4), 8):
        if sum(seq) != 21:
            continue
        cap = sum({0: 7, 1: 5, 2: 3, 3: 2}[b] for b in seq)
        possible.append({"indegrees": seq, "outdegree_upper_sum": cap})
    return possible


def profile_audit():
    counts = Counter()
    sample_remaining = None
    for alpha in alpha_profiles():
        for k in k_profiles_with_four_zeros():
            if not historical_z4_baseline(alpha, k):
                continue
            counts["previously_unexcluded"] += 1
            if rigidity_falsifier(alpha):
                counts["removed_by_new_rigidity"] += 1
            elif c_cut_falsifier(alpha, k):
                counts["removed_by_existing_c_cap"] += 1
            else:
                counts["remaining"] += 1
                if sample_remaining is None:
                    sample_remaining = [list(alpha), list(k)]
    return {
        "scope": "Necessary sorted z=4 integer profiles, not 27-vertex graphs",
        "counts": dict(sorted(counts.items())),
        "sample_unexcluded_integer_profile": sample_remaining,
    }


def certificate():
    return {
        "eight_vertex_equality_degree_audit": equality_degree_profiles(),
        "nine_vertex_source_outdegree_sequence": list(RIGID_ALPHA),
        "root_profile_audit": profile_audit(),
        "proof": "proofs/M074_EIGHT_VERTEX_RIGIDITY.md",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = certificate()
    if args.check:
        assert result["eight_vertex_equality_degree_audit"] == [
            {"indegrees": (0,) + (3,) * 7, "outdegree_upper_sum": 21},
            {"indegrees": (1, 2) + (3,) * 6, "outdegree_upper_sum": 20},
            {"indegrees": (2,) * 3 + (3,) * 5, "outdegree_upper_sum": 19},
        ], "eight-vertex integer equality drift"
        assert result["root_profile_audit"]["counts"] == {
            "previously_unexcluded": 295,
            "removed_by_new_rigidity": 120,
            "removed_by_existing_c_cap": 20,
            "remaining": 155,
        }, "CH27 root-profile filter drift"
        assert result["root_profile_audit"]["sample_unexcluded_integer_profile"] is not None
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
