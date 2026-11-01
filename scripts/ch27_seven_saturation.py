#!/usr/bin/env python3
"""Arithmetic controls for the elementary CH(27,9) seven-saturation proof.

This is NOT a search for 27-vertex digraphs, a proof assistant, or a
historical novelty certificate. The universal argument is written in
proofs/M074_SEVEN_SATURATION.md and uses earlier hand-proved local lemmas.
"""
import argparse
from itertools import combinations_with_replacement
import json


def q_cap(k, t=7):
    """Maximum A-targets for a B vertex with k>0 C-predecessors.

    At least seven A vertices have alpha=2. Only at most two can have alpha>2.
    At most one vertex can have alpha=8 in an oriented nine-vertex graph.
    """
    if type(k) is not int or not 1 <= k <= 7 or type(t) is not int or not 7 <= t <= 9:
        raise ValueError("k in 1..7 and t in 7..9 required")
    return min(9 - t, 1 if k == 6 else 0 if k == 7 else 7 - k)


def b_out_floor(k, t=7):
    return 1 + k - q_cap(k, t)


def positive_B_capacity(z):
    if type(z) is not int or not 0 <= z <= 10:
        raise ValueError("z must be in [0,10]")
    p = 10 - z
    return p * (p - 1) // 2 + p * z


def high_root_defect_floor(z, t=7):
    if type(z) is not int or z < 0 or type(t) is not int or not 7 <= t <= 9:
        raise ValueError("bad z or t")
    return {"minimum_high_vertices": t * max(0, 4 - z),
            "maximum_high_vertices": 27 - t}


def cut_table(c_arc_cap=17):
    """Necessary *coarse* C/B cut, deliberately before the z=2 equality lemma."""
    if type(c_arc_cap) is not int or not 0 <= c_arc_cap <= 21:
        raise ValueError("invalid seven-vertex arc ceiling")
    k_min = 63 - c_arc_cap
    rows = []
    for z in range(2, 11):
        p = 10 - z
        k_max = 7 * p
        b_floor = 2 * k_min - 6 * p
        capacity = positive_B_capacity(z)
        rows.append({"z": z, "positive_B": p, "C_to_B_min": k_min,
                     "C_to_B_max": k_max, "B_out_floor": b_floor,
                     "B_out_capacity": capacity,
                     "cut_rejects": k_min > k_max or b_floor > capacity,
                     "cut_ties": k_min <= k_max and b_floor == capacity})
    return rows


def equality_case_z2():
    """Independent arithmetic enumeration of the exact z=2 boundary."""
    profiles = tuple(k for k in combinations_with_replacement(range(1, 8), 8)
                     if sum(k) == 46)
    # Equality in every q(k) <= 7-k rule requires all k>=5.
    eligible = tuple(k for k in profiles if all(q_cap(v) == 7 - v for v in k))
    # A triangle-free 8-vertex tournament is transitive. Its sink has
    # zero P-outneighbors; at maximum 2 B-outneighbors (into the 2 zero-k B's).
    min_out_at_equality = min(2 * v - 6 for row in eligible for v in row)
    return {"sorted_positive_k_profiles_with_sum_46": len(profiles),
            "eligible_after_target_equality": len(eligible),
            "equality_profiles": [list(k) for k in eligible],
            "minimum_P_vertex_B_outdegree": min_out_at_equality,
            "tournament_sink_max_B_outdegree": 2,
            "equality_contradicts_sink": min_out_at_equality > 2}


def certificate():
    table = cut_table()
    deg = {str(z): high_root_defect_floor(z) for z in (0, 1)}
    return {
        "statement": "At an indegree-10 CH27 root, at most six A vertices have A-outdegree 2",
        "scope": "conditional oriented 27-vertex, 9-outregular, C3-free graph; no full finite resolution",
        "hand_seven_vertex_arc_cap": 17,
        "q_upper": {str(k): q_cap(k) for k in range(1, 8)},
        "degree_defect_cases": deg,
        "cut_cases": table,
        "z2_equality_and_sink": equality_case_z2(),
        "mutated_weaker_18_arc_cap": {
            "z2": cut_table(18)[0],
            "note": "weakened premise does not force the equality used by the proof"
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    c = certificate()
    if args.check:
        assert c["q_upper"] == {"1": 2, "2": 2, "3": 2, "4": 2,
                                "5": 2, "6": 1, "7": 0}
        assert c["degree_defect_cases"]["0"] == {
            "minimum_high_vertices": 28, "maximum_high_vertices": 20}
        assert c["degree_defect_cases"]["1"] == {
            "minimum_high_vertices": 21, "maximum_high_vertices": 20}
        z2, z3, z4 = c["cut_cases"][:3]
        assert (z2["C_to_B_min"], z2["B_out_floor"], z2["B_out_capacity"],
                z2["cut_ties"]) == (46, 44, 44, True)
        assert (z3["B_out_floor"], z3["B_out_capacity"], z3["cut_rejects"]) == (50, 42, True)
        assert (z4["C_to_B_max"], z4["cut_rejects"]) == (42, True)
        assert all(row["cut_rejects"] for row in c["cut_cases"][1:])
        eq = c["z2_equality_and_sink"]
        assert (eq["sorted_positive_k_profiles_with_sum_46"],
                eq["eligible_after_target_equality"],
                eq["minimum_P_vertex_B_outdegree"],
                eq["tournament_sink_max_B_outdegree"],
                eq["equality_contradicts_sink"]) == (33, 4, 4, 2, True)
        assert not c["mutated_weaker_18_arc_cap"]["z2"]["cut_ties"]
        assert not c["mutated_weaker_18_arc_cap"]["z2"]["cut_rejects"]
    print(json.dumps(c, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
