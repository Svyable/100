#!/usr/bin/env python3
"""A C-to-A bottleneck for the CH(27,9) indegree-ten, z=4 branch.

Integer *necessary* degree profiles only; never a whole-graph satisfiability
or a proof of the original Caccetta-Haggkvist conjecture.
"""
import argparse
from collections import Counter
import json

import ch27_b_internal as b_internal


def bound_C_to_A(alpha, k):
    """(necessary C->A lower, safe C->A upper) for a z=4 root.

    The upper bound only counts A vertices which COULD avoid all alpha-two
    vertices in A; each can receive at most alpha-2 arcs from C. If A
    contains an alpha-eight vertex, its other A neighbors cannot point to
    it, making their internal-high capacity one smaller.
    """
    if (len(alpha) != 9 or any(type(a) is not int or not 2 <= a <= 8 for a in alpha)
            or len(k) != 10 or any(type(q) is not int or not 0 <= q <= 7 for q in k)
            or k.count(0) != 4):
        raise ValueError("expected nine valid alpha values and ten k values with four zeros")
    low = alpha.count(2)
    high = len(alpha) - low
    universal_source = 8 in alpha
    upper = 0
    for a in alpha:
        if a == 2:
            continue  # all seven C-vertices are out-neighbors of this A vertex
        if low and universal_source and a == 8:
            continue  # points to all other A vertices, including a low one
        allowed = high - 1 - int(low > 0 and universal_source)
        if a <= allowed:
            upper += a - 2
    # e(C,C) <= C(7,2)=21 and e(C,B)=sum k, so e(C,A) >=42-sum k.
    # When z=4, six k=7 is impossible: six B vertices of internal outdegree
    # at least 8 would exceed the 45 oriented pairs of B. Consequently,
    # e(C,A)>=2 (if <=1, C would be a transitive tournament with a sink
    # that cannot send nine arcs into only six eligible B plus <=1 A).
    lower = max(2, 42 - sum(k))
    return lower, upper


def endpoint_obstruction(alpha, k):
    """Finite three-case closure of the only seven coarse survivors.

    Each label refers to an elementary proof in proofs/M074_C_TO_A_BOTTLENECK.md,
    not a SAT/UNSAT claim. The checker additionally validates the counts.
    """
    if alpha == (2,) * 3 + (3,) * 5 + (8,) and sum(k) == 37:
        return "five_protected_threes_overfill_five_vertices"
    if alpha == (2,) * 2 + (3,) * 5 + (4, 6) and sum(k) == 34:
        return "protected_A_forces_C_tournament_sink"
    if alpha == (2,) + (3,) * 7 + (6,) and sum(k) == 34:
        return "eight_vertex_degree_defect"
    return None


def classify(alpha, k):
    old = b_internal.classify(alpha, k)
    # Replay the original 295-profile baseline even after the independent
    # z4 sink filter was added to the shared B-stage classifier. Both proofs
    # must be testable on their own and neither should mask the other.
    if old not in ("unresolved", "z4_sink_cut"):
        return old
    lower, upper = bound_C_to_A(alpha, k)
    if upper < lower:
        return "c_to_a_bottleneck"
    return endpoint_obstruction(alpha, k) or "unresolved"


def report():
    counts = Counter()
    survivors = []
    for a in b_internal.alpha_profiles():
        for k in b_internal.k_profiles_with_four_zeros():
            classification = classify(a, k)
            counts[classification] += 1
            if classification == "unresolved":
                lower, upper = bound_C_to_A(a, k)
                survivors.append({"alpha": a, "k": k,
                                  "needed_c_to_a": lower, "possible_c_to_a_upper": upper})
    return {"scope": "Necessary integer profiles for one CH(27,9) indegree-ten root with z=4; not graphs",
            "total_profiles": sum(counts.values()),
            "stages": dict(sorted(counts.items())),
            "survivors": survivors,
            "claim": "All 295 formerly unresolved z=4 integer profiles excluded, conditional on the stated local prerequisites"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = report()
    if args.check:
        assert result["total_profiles"] == 153384
        assert result["stages"] == {
            "cut": 149396, "subset_capacity": 3515, "triangle_three": 132,
            "minout_two_5": 22, "minout_two_6": 24,
            "c_to_a_bottleneck": 288,
            "five_protected_threes_overfill_five_vertices": 1,
            "protected_A_forces_C_tournament_sink": 3,
            "eight_vertex_degree_defect": 3,
        }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
