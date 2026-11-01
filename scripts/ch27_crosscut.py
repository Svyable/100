#!/usr/bin/env python3
"""Exact integer cross-cut audit for the (27,9) in/out-regular CH case.

The mathematical nine-vertex 29-arc lemma and saturated-pivot cut
are proved separately in proofs/M074_27_REGULAR.md.
This program does not enumerate 27-vertex digraphs.
"""
import json
from itertools import combinations_with_replacement


def profiles(local_arc_cap=29):
    """Sorted nine-vertex internal outdegree multisets; min outdegree two."""
    if type(local_arc_cap) is not int or local_arc_cap < 18:
        raise ValueError("local_arc_cap must be an integer >= 18")
    return tuple(p for p in combinations_with_replacement(range(2, 9), 9)
                 if sum(p) <= local_arc_cap)


def required_cross_arcs(alpha, beta):
    return max(81 - 2 * sum(alpha), 81 - 2 * sum(beta))


def eligible_cross_pairs(alpha, beta, threshold=10):
    return sum(a + b >= threshold for a in alpha for b in beta)


def audit(local_arc_cap=29, threshold=10):
    pp = profiles(local_arc_cap)
    violations = []
    maximum_eligible = -1
    minimum_required = 81
    maximum_margin = -1000
    extremal = None
    for alpha in pp:
        for beta in pp:
            demand = required_cross_arcs(alpha, beta)
            eligible = eligible_cross_pairs(alpha, beta, threshold)
            margin = eligible - demand
            maximum_eligible = max(maximum_eligible, eligible)
            minimum_required = min(minimum_required, demand)
            if margin > maximum_margin:
                maximum_margin = margin
                extremal = (alpha, beta, demand, eligible)
            if margin >= 0:
                violations.append((alpha, beta, demand, eligible))
    return {
        "local_arc_cap": local_arc_cap,
        "eligibility_threshold": threshold,
        "profiles": len(pp),
        "profile_pairs": len(pp) ** 2,
        "minimum_required_cross_arcs": minimum_required,
        "maximum_eligible_cross_pairs": maximum_eligible,
        "maximum_eligible_minus_required": maximum_margin,
        "not_excluded_pairs": len(violations),
        "sample_not_excluded": violations[:2],
        "max_margin_witness": extremal,
    }


def sharp_local_witness():
    """Seven-vertex step-{1,2} circulant plus two successive sources."""
    graph = {i: {(i + 1) % 7, (i + 2) % 7} for i in range(7)}
    graph[7] = set(range(7))
    graph[8] = set(range(8))
    return graph


def irregular_relaxed_obstruction():
    """Necessary-profile escape at a 10-indegree root, NOT a 27-vertex graph."""
    alpha = (2,) * 7 + (7, 8)
    incoming = (0,) * 4 + (5,) * 4 + (7,) * 2
    m = sum(alpha)
    q = [sum(a >= k + 2 for a in alpha) for k in incoming]
    floors = sorted((max(0, 1 + k - q_b)
                     for k, q_b in zip(incoming, q)), reverse=True)
    feasible_B_caps = all(sum(floors[:s]) <= s * (19-s) // 2
                          for s in range(1, 11))
    return {"alpha": alpha, "k": incoming, "m": m,
            "cut_required": 92 - 2 * m, "cut_observed": sum(incoming),
            "zero_k_vertices": incoming.count(0), "B_outdegree_floors": floors,
            "B_subset_caps_pass": feasible_B_caps}


def main():
    exact = audit()
    mutated = audit(local_arc_cap=30)
    graph = sharp_local_witness()
    sharp = {"vertices": len(graph), "arcs": sum(map(len, graph.values())),
             "min_outdegree": min(map(len, graph.values()))}
    print(json.dumps({"sharp_local_example": sharp, "exact": exact,
                      "weakened_local_arc_cap": mutated,
                      "irregular_relaxed_obstruction": irregular_relaxed_obstruction()},
                     indent=2))
    if ((exact["profiles"], exact["profile_pairs"],
         exact["minimum_required_cross_arcs"],
         exact["maximum_eligible_cross_pairs"],
         exact["maximum_eligible_minus_required"],
         exact["not_excluded_pairs"]) != (166, 27556, 23, 22, -1, 0)
        or mutated["not_excluded_pairs"] != 60
        or sharp != {"vertices": 9, "arcs": 29, "min_outdegree": 2}
        or not irregular_relaxed_obstruction()["B_subset_caps_pass"]):
        raise SystemExit("INVALID: (27,9) cross-cut audit drift")


if __name__ == "__main__":
    main()
