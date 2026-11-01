#!/usr/bin/env python3
"""Sharp nine-vertex local lemma and the bounded CH (27,9) reduction.

The mathematical proof is in proofs/M074_NINE_VERTEX.md. This checker
replays integer boundaries and an explicit sharp example, not a general
nine-vertex graph search or an UNSAT certificate for 27 vertices.
"""
import argparse
import json


def check_oriented_triangle_free(out):
    """Strictly validate a finite oriented C3-free digraph."""
    if not isinstance(out, (list, tuple)) or not out:
        raise ValueError("nonempty adjacency sequence required")
    n = len(out)
    rows = []
    for u, targets in enumerate(out):
        if not isinstance(targets, (list, tuple)):
            raise ValueError("adjacency row must be a sequence")
        if any(type(v) is not int or not 0 <= v < n or v == u
               for v in targets) or len(targets) != len(set(targets)):
            raise ValueError("invalid directed edge")
        rows.append(set(targets))
    for u in range(n):
        for v in rows[u]:
            if u in rows[v]:
                raise ValueError("digon")
            if any(u in rows[w] for w in rows[v]):
                raise ValueError("directed triangle")
    indeg = tuple(sum(v in rows[u] for u in range(n)) for v in range(n))
    outdeg = tuple(len(x) for x in rows)
    return {"n": n, "arcs": sum(outdeg), "indegrees": indeg,
            "outdegrees": outdeg, "minimum_outdegree": min(outdeg)}


def sharp_nine():
    """Z7(steps 1,2), a dominating source, then another dominating source."""
    return tuple(
        tuple((u+d) % 7 for d in (1, 2)) for u in range(7)
    ) + (tuple(range(7)), tuple(range(8)))


def local_pairs(k):
    """Degree pairs surviving the *necessary* rooted k-outdegree inequality.

    A vertex of outdegree a and indegree b in a loopless oriented C3-free
    digraph of order 9 and minimum outdegree >=k satisfies:
    a>=k, a+b<=8, a+2b<=15-2k.
    """
    if k not in (2, 3):
        raise ValueError("only proved k=2/3 nine-vertex cases")
    return tuple((a, b) for a in range(k, 9) for b in range(9-a)
                 if a+2*b <= 15-2*k)


def local_certificate():
    raw = set(local_pairs(2))
    boundary = tuple(sorted((a,b) for a,b in raw if a+2*b == 11))
    if boundary != ((3, 4), (5, 3)):
        raise AssertionError("eleven-boundary changed")
    # (3,4): 3-outneighborhood tournament forces C3.
    # (5,3): 5-outneighborhood has minout2, impossible on five vertices.
    reduced = raw - set(boundary)
    equality = tuple(sorted((a,b) for a,b in reduced if a+2*b == 10))
    if equality != ((2, 4), (4, 3), (6, 2)):
        raise AssertionError("ten-boundary changed")
    # (6,2): its 6-outneighborhood has minout2, impossible on 6 vertices.
    reduced.remove((6, 2))
    possible = tuple(sorted((a,b) for a,b in reduced if a+2*b == 10))
    if possible != ((2, 4), (4, 3)):
        raise AssertionError("equality profiles changed")
    # If 30 arcs, 3m=90 and EVERY vertex must satisfy a+2b=10.
    # With x copies of (2,4) and y copies of (4,3):
    # x+y=9, 2x+4y=30 -> x=3, y=6.
    x, y = 3, 6
    if x+y != 9 or 2*x+4*y != 30 or 4*x+3*y != 30:
        raise AssertionError("equality arithmetic drift")
    # A (4,3) vertex has A size4, C size1. Each outneighbor has
    # min internal outdegree1; triangle-free forces a directed C4,
    # no chords, and hence FOUR outdegree-two vertices in A.
    if not (y > 0 and x < 4):
        raise AssertionError("4-cycle impossibility premise changed")
    three = set(local_pairs(3))
    if any(b > 3 for a,b in three) or (3, 3) not in three:
        raise AssertionError("minimum-three indegree cap changed")
    witness = check_oriented_triangle_free(sharp_nine())
    if (witness["n"], witness["arcs"], witness["minimum_outdegree"],
            max(witness["indegrees"])) != (9, 29, 2, 4):
        raise AssertionError("sharpness witness drift")
    return {
        "raw_min2_integer_pairs": len(raw),
        "excluded_boundary_eleven": [list(p) for p in boundary],
        "excluded_zero_C_six_neighbor": [6, 2],
        "degree_pairs_at_thirty": [list(p) for p in possible],
        "thirty_arc_profile_multiplicities": {"out2_in4": x, "out4_in3": y},
        "thirty_arc_profile_requires_four_out2": True,
        "triangle_free_nine_min_outdegree_three_impossible": True,
        "sharp_nine_arc_ceiling": 29,
        "sharp_witness_arcs": witness["arcs"],
        "sharp_witness_outdegrees_sorted": sorted(witness["outdegrees"]),
        "sharp_witness_indegrees_sorted": sorted(witness["indegrees"]),
    }


def indegree_ten_root_budget(internal_arcs=29):
    """Necessary cuts at a hypothetical n=27, r=9 indegree-ten root.

    This table alone NEVER demonstrates the existence of a counterexample
    or excludes the 9-inregular branch.
    """
    if type(internal_arcs) is not int or not 18 <= internal_arcs <= 29:
        raise ValueError("nine-neighborhood arc count must lie in [18,29]")
    m = internal_arcs
    # Root: |A|=9, |B|=10, |C|=7, d+(every vertex)=9, d-(every vertex)<=10.
    needed = 92-2*m
    minimum_B_hit = (needed + 6)//7
    max_B_senders = 10-minimum_B_hit
    return {
        "m": m, "a_to_c": 81-m,
        "c_to_a_max": m-18,
        "b_to_c_plus_c_to_c_max": m-11,
        "c_to_b_min": needed,
        "B_vertices_hit_by_C_min": minimum_B_hit,
        "B_vertices_that_could_point_to_A_outdegree2_max": max_B_senders,
        "ambient_indegree_A_outdegree2_upper": 1+4+max_B_senders,
        "low_indegree_threshold": 8,
    }


def certificate():
    return {"local": local_certificate(),
            "n27_high_pivot_worst_case": indegree_ten_root_budget(29),
            "scope": ("Sharp 9-vertex local theorem plus n27 indegree cap 10. "
                      "No exclusion of either n27 regular or irregular case.")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    report = certificate()
    if args.check:
        assert report["local"]["raw_min2_integer_pairs"] == 24
        assert report["local"]["sharp_witness_outdegrees_sorted"] == [2]*7+[7,8]
        assert report["local"]["sharp_witness_indegrees_sorted"] == [0,1]+[4]*7
        assert report["n27_high_pivot_worst_case"] == {
            "m":29, "a_to_c":52, "c_to_a_max":11,
            "b_to_c_plus_c_to_c_max":18, "c_to_b_min":34,
            "B_vertices_hit_by_C_min":5,
            "B_vertices_that_could_point_to_A_outdegree2_max":5,
            "ambient_indegree_A_outdegree2_upper":10,
            "low_indegree_threshold":8,
        }
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
