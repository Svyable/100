#!/usr/bin/env python3
"""Nine-vertex local stability: at least TWO outdegree-two vertices.

Proof: proofs/M074_NINE_TWO_LOW.md. This checker replays only the short
integer case split and explicit valid/invalid controls, not all 9-vertex
oriented graphs or the CH (27,9) theorem.
"""
import argparse
import json


TRIANGLE_FREE_THREE_LOW = (
    (6, 7), (0, 3), (1, 8),
    (0, 6, 7), (1, 5, 8), (1, 2, 8),
    (2, 4, 5), (2, 4, 5), (0, 1, 3),
)


def graph_profile(rows, require_triangle_free=True):
    """Check a simple loopless oriented graph and optional C3-freeness."""
    if not isinstance(rows, (list, tuple)) or len(rows) != 9:
        raise ValueError("nine vertex adjacency lists required")
    adj = []
    for u, targets in enumerate(rows):
        if not isinstance(targets, (tuple, list)):
            raise ValueError("invalid outgoing row")
        if (any(type(v) is not int or not 0 <= v < 9 or v == u
                for v in targets) or len(targets) != len(set(targets))):
            raise ValueError("duplicate, loop, or invalid arc")
        adj.append(set(targets))
    for u in range(9):
        for v in adj[u]:
            if u in adj[v]:
                raise ValueError("digon")
            if require_triangle_free and any(u in adj[w] for w in adj[v]):
                raise ValueError("directed 3-cycle")
    indeg = [sum(v in adj[u] for u in range(9)) for v in range(9)]
    outdeg = [len(adj[u]) for u in range(9)]
    return {
        "arcs": sum(outdeg), "outdegrees": outdeg, "indegrees": indeg,
        "outdegree_two_vertices": [u for u,d in enumerate(outdeg) if d == 2],
        "minimum_outdegree": min(outdeg),
        "maximum_indegree": max(indeg),
    }


def singleton_case_table():
    """Necessary arithmetic when there is exactly ONE degree-two vertex x.

    Nine-vertex local lemma: indeg(x)<=4, total arcs m<=29.
    Eight-vertex deletion lemma: H-x has minout>=2, m_J<=21.
    In H-x at least max(24-m_J,m_J-16) vertices have internal outdeg 2.
    Since x is the UNIQUE global outdeg-two vertex, all must point to x.
    """
    result = []
    for m in range(26, 30):
        for b in range(5):
            mj = m - 2 - b
            if mj > 21:
                reason = "eight_vertex_arc_cap"
            else:
                deg_two_lb = max(24 - mj, mj - 16)
                if deg_two_lb > b:
                    reason = "too_many_two_outdegree_inneighbors"
                else:
                    reason = "four_high_vertex_digon_obstruction"
            result.append({"arcs_nine":m, "indegree_of_unique_degree_two":b,
                           "arcs_after_deletion":mj, "rejection":reason})
    return result


def certificate():
    cases = singleton_case_table()
    surviving = [(x["arcs_nine"], x["indegree_of_unique_degree_two"])
                 for x in cases
                 if x["rejection"] == "four_high_vertex_digon_obstruction"]
    witness = graph_profile(TRIANGLE_FREE_THREE_LOW)
    # Remove one edge at vertices 0 and 1 from Z9 steps {1,2,3}.
    # Orientation and minout2 persist, but the remaining 3-step cycles
    # show why the no-C3 hypothesis is material.
    negative = tuple(
        tuple((u+d) % 9 for d in (1, 2) if u in (0, 1))
        if u in (0, 1) else tuple((u+d) % 9 for d in (1, 2, 3))
        for u in range(9))
    mutated = graph_profile(negative, require_triangle_free=False)
    return {
        "singleton_degree_two_integer_cases": len(cases),
        "remaining_case_for_graph_argument": surviving,
        "remaining_case_reason": (
            "H-x has four outdegree-two vertices sending to x and four "
            "outdegree-three vertices; two x-outneighbors in the latter "
            "must point to each other in both directions, a digon."),
        "triangle_free_witness_three_low": witness,
        "directed_triangle_negative_control": mutated,
        "scope": "Only local nine-vertex lemma; CH27 high-root implication conditional on z<=3",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = certificate()
    if args.check:
        assert result["singleton_degree_two_integer_cases"] == 20
        assert result["remaining_case_for_graph_argument"] == [(26, 4)]
        w = result["triangle_free_witness_three_low"]
        assert w["arcs"] == 24
        assert w["outdegree_two_vertices"] == [0, 1, 2]
        assert w["minimum_outdegree"] == 2
        assert w["maximum_indegree"] <= 4
        bad = result["directed_triangle_negative_control"]
        assert bad["outdegree_two_vertices"] == [0, 1]
        assert bad["minimum_outdegree"] == 2
        try:
            graph_profile(tuple(
                tuple((u+d) % 9 for d in (1, 2)) if u in (0, 1)
                else tuple((u+d) % 9 for d in (1, 2, 3))
                for u in range(9)))
        except ValueError as e:
            assert str(e) == "directed 3-cycle", str(e)
        else:
            raise AssertionError("triangle-negative control did not fail")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
