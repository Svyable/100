#!/usr/bin/env python3
"""Integer audit for the conditional saturated-shadow lemma.

This recomputes cut capacities; it is NOT a graph search, novelty certificate,
kernel proof, or verification of the global Caccetta--Haggkvist conjecture.
Full derivation: research/M074_SATURATED_SHADOW.md
"""
import argparse
import json

from ch27_local import check_oriented_triangle_free, sharp_nine


def budget(r, s):
    """Necessary capacities if >=r-s A-neighbors have internal outdegree two.

    Requires: |V|=3r, every outdegree r, indegree(v)=r+1,
    max indegree<=r+1, oriented, C3-free, and 1<=s<=3.
    """
    if type(r) is not int or type(s) is not int or r < 4 or s not in (1, 2, 3) or r <= s:
        raise ValueError("require integer r>=4, s in {1,2,3}, r>s")
    c_size = r - 2
    b_size = r + 1
    # At (8,1), the six-vertex min-outdegree-two obstruction rules
    # out equality in the naive internal-C indegree bound.
    six_vertex_gain = int((r, s) == (8, 1))
    c_internal_cap = (s + 1) * c_size - six_vertex_gain
    c_to_b_floor = r * c_size - c_internal_cap
    b_internal_floor = c_to_b_floor - (s - 1) * b_size
    b_internal_cap = b_size * (b_size - 1) // 2
    return {
        "r": r,
        "s": s,
        "min_saturated_neighbors": r - s,
        "c_to_a": 0,
        "c_internal_indegree_cap": s + 1,
        "c_internal_arcs_cap": c_internal_cap,
        "six_vertex_gain": six_vertex_gain,
        "c_to_b_arcs_floor": c_to_b_floor,
        "b_internal_arcs_floor": b_internal_floor,
        "b_internal_arcs_cap": b_internal_cap,
        "margin_twice": 2 * (b_internal_floor - b_internal_cap),
        "forced_contradiction": b_internal_floor > b_internal_cap,
    }


def polynomial(r, s):
    """Algebraically independent expansion of the two-sided capacity gap."""
    return r * r - (4 * s + 5) * r + 2 * (s + 3)


def n27_seven_saturated():
    """At an indegree-ten pivot, *if* exactly seven alpha=2, sharpen C."""
    r, low, c_size, b_size = 9, 7, 7, 10
    # Existing sharp C3-free seven-vertex maximum-indegree-three theorem.
    c_internal_arcs_cap = 16
    c_to_b_floor = r * c_size - c_internal_arcs_cap
    minimum_b_hit = (c_to_b_floor + c_size - 1) // c_size
    no_c_predecessor_max = b_size - minimum_b_hit
    # From the separately proved nine-vertex local indegree<=4 bound.
    low_indegree_cap = 1 + 4 + no_c_predecessor_max
    min_internal_arcs_a = 2 * low + 3 * (9 - low)
    min_low_induced_arcs = min_internal_arcs_a - 16
    return {
        "conditional_exact_saturated_neighbors": low,
        "c_internal_arcs_cap": c_internal_arcs_cap,
        "c_to_b_arcs_floor": c_to_b_floor,
        "b_vertices_hit_from_c_min": minimum_b_hit,
        "b_vertices_without_c_predecessor_max": no_c_predecessor_max,
        "saturated_neighbors_indegree_cap": low_indegree_cap,
        "a_internal_arcs_min": min_internal_arcs_a,
        "low_to_low_arcs_floor": min_low_induced_arcs,
    }


def certificate():
    thresholds = []
    for s in (1, 2, 3):
        below_r, first_r = (7, 8) if s == 1 else (4*s+4, 4*s+5)
        below = budget(below_r, s)
        first = budget(first_r, s)
        # The single-arc C gain applies only at (8,1).
        assert below["margin_twice"] == polynomial(below["r"], s) + 2*below["six_vertex_gain"]
        assert first["margin_twice"] == polynomial(first["r"], s) + 2*first["six_vertex_gain"]
        thresholds.append({
            "s": s, "last_noncontradictory_cut": below,
            "first_strict_cut_contradiction": first,
        })
    local = check_oriented_triangle_free(sharp_nine())
    return {
        "scope": ("Necessary conditional inequalities; graph realizability, "
                  "originality, and independent specialist review not established."),
        "thresholds": thresholds,
        "n27_if_exactly_seven": n27_seven_saturated(),
        "nine_vertex_control": {
            "n": local["n"], "arcs": local["arcs"],
            "minimum_outdegree": local["minimum_outdegree"],
            "internal_outdegrees_sorted": sorted(local["outdegrees"]),
        },
    }


def check(doc):
    for row in doc["thresholds"]:
        s = row["s"]
        lo = row["last_noncontradictory_cut"]
        hi = row["first_strict_cut_contradiction"]
        assert (lo["r"], hi["r"]) == ((7, 8) if s == 1 else (4*s+4, 4*s+5))
        assert lo["forced_contradiction"] is False
        assert hi["forced_contradiction"] is True
        assert hi["margin_twice"] == (2 if s == 1 else 2*(s+3))
        assert lo["margin_twice"] == (-6 if s == 1 else 2-2*s)
        assert all(budget(r, s)["forced_contradiction"] for r in range(hi["r"], hi["r"]+30))
    assert doc["n27_if_exactly_seven"] == {
        "conditional_exact_saturated_neighbors": 7,
        "c_internal_arcs_cap": 16,
        "c_to_b_arcs_floor": 47,
        "b_vertices_hit_from_c_min": 7,
        "b_vertices_without_c_predecessor_max": 3,
        "saturated_neighbors_indegree_cap": 8,
        "a_internal_arcs_min": 20,
        "low_to_low_arcs_floor": 4,
    }
    assert doc["nine_vertex_control"] == {
        "n": 9, "arcs": 29, "minimum_outdegree": 2,
        "internal_outdegrees_sorted": [2]*7 + [7,8],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    doc = certificate()
    if args.check:
        check(doc)
        print("OK: conditional saturation cuts r=8,13,17; six-vertex control and n=27 local budget")
    else:
        print(json.dumps(doc, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
