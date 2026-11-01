#!/usr/bin/env python3
"""Small, independent integer audit of the CH(24,8) weighted-deficit proof.

The certificate is *not* a graph search, a Lean proof, a new CH bound, or
independent specialist review. Its inequalities are proved in the linked note.
"""
from itertools import combinations_with_replacement
import json


def local_a_profiles():
    """All weakly sorted eight-tuples with alpha >=2 and sum alpha <=21."""
    return tuple(alpha for alpha in combinations_with_replacement(range(2, 8), 8)
                 if sum(alpha) <= 21)


def b_outgoing_lower(alpha, positives):
    """Necessary lower bound on B-internal outgoing arcs from chosen B vertices.

    Here alpha is the complete internal outdegree profile of A. Positive k's
    are the numbers of incoming C arcs at the selected B vertices.
    """
    return sum(1 + k - sum(a >= k + 2 for a in alpha) for k in positives)


def z3_audit(cut_slack=0):
    """Enumerate *relaxed integer profiles*, not 24-vertex graphs."""
    if type(cut_slack) is not int or cut_slack < 0:
        raise ValueError("cut_slack must be a nonnegative integer")
    total = 0
    minimum = None
    example = None
    for alpha in local_a_profiles():
        m = sum(alpha)
        for ks in combinations_with_replacement(range(1, 7), 6):
            if sum(ks) < 74 - 2 * m - cut_slack:
                continue
            total += 1
            floor = b_outgoing_lower(alpha, ks)
            if minimum is None or floor < minimum:
                minimum, example = floor, (alpha, ks)
    return {"relaxed_profiles": total, "minimum_B_outgoing": minimum,
            "witness_profile": example, "capacity": 33}


def z2_exception_audit():
    """Independently exercise the unique m=21,z=2,t=3 A profile."""
    alpha = (2, 2, 2, 3, 3, 3, 3, 3)
    assert sum(alpha) == 21
    checked = 0
    by_ones = {0: 0, 1: 0, 2: 0}
    smallest_seven_bound = None
    for ks in combinations_with_replacement(range(1, 7), 7):
        if sum(ks) < 32:
            continue
        checked += 1
        u = ks.count(1)
        assert u <= 2
        by_ones[u] += 1
        if u <= 1:
            # q(k)=0 when k>=2 and exactly five A vertices have alpha=3.
            lower = sum(1 + k for k in ks if k >= 2)
            assert lower >= 37 > 35  # s=7 capacity
            smallest_seven_bound = (lower if smallest_seven_bound is None
                                    else min(smallest_seven_bound, lower))
        else:
            assert ks == (1, 1, 6, 6, 6, 6, 6)
            assert 5 * 7 == 35 > 30  # s=5 capacity
    return {"relaxed_profiles": checked, "ones_cases": by_ones,
            "minimum_seven_subset_bound_when_u_at_most_one": smallest_seven_bound}


def certificate():
    # Independently audit the two discrete ingredients used by the short
    # proof: sum alpha-2 <=5 and floor(5/k) <= 6-k for k=2..6.
    assert len(local_a_profiles()) == 19
    per_k = {k: (5 // k, 6 - k) for k in range(2, 7)}
    assert all(lhs <= rhs for lhs, rhs in per_k.values())
    assert all(sum(a >= k + 2 for a in alpha) <= 6 - k
               for alpha in local_a_profiles() for k in range(2, 7))
    exact = z3_audit()
    assert exact["minimum_B_outgoing"] == 34 > exact["capacity"]
    assert exact["witness_profile"] == (
        (2, 2, 2, 2, 2, 2, 2, 7), (5, 5, 5, 5, 6, 6))
    weakened = z3_audit(1)
    assert weakened["minimum_B_outgoing"] <= weakened["capacity"]
    # Concrete one-unit countermodel to the *arithmetic cut implication*,
    # not an actual directed graph and not a CH counterexample.
    one_unit_profile = (
        (2, 2, 2, 2, 2, 2, 2, 7), (4, 5, 5, 5, 6, 6))
    assert sum(one_unit_profile[1]) == 31
    assert b_outgoing_lower(*one_unit_profile) == 33
    exception = z2_exception_audit()
    assert exception["relaxed_profiles"] == 106
    return {
        "local_A_profiles": 19,
        "floor_checks": per_k,
        "z3_exact": exact,
        "z3_one_unit_weakened": weakened,
        "weakened_cut_arithmetic_boundary": one_unit_profile,
        "z2_exception": exception,
        "scope": "necessary relaxed integer constraints only; no graph or external review",
    }


if __name__ == "__main__":
    print(json.dumps(certificate(), indent=2, sort_keys=True))
