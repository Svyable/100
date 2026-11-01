#!/usr/bin/env python3
"""Check the sharp eight-vertex local witness for M074's irregular (24,8) branch.

This does not enumerate 24-vertex digraphs and is not a Caccetta-Haggkvist proof.
The local lower bound also relies on the proved indegree bounds in
research/M074_ELEMENTARY_24_REGULAR.md; this file independently checks the
explicit graph witness and the elementary integer budget.
"""

WITNESS = (
    (3, 6),
    (0, 7),
    (1, 5),
    (2, 4),
    (1, 2, 5),
    (0, 1, 7),
    (2, 3, 4),
    (0, 3, 6),
)


def verify_local_graph(outneighbors):
    """Return exact degree statistics; reject loops, digons and directed triangles."""
    n = len(outneighbors)
    if n != 8:
        raise ValueError("the local witness must have exactly 8 vertices")
    arcs = set()
    for u, row in enumerate(outneighbors):
        if len(row) != len(set(row)):
            raise ValueError("duplicate arc")
        for v in row:
            if not isinstance(v, int) or v < 0 or v >= n or u == v:
                raise ValueError("invalid endpoint or loop")
            arcs.add((u, v))
    if any((v, u) in arcs for u, v in arcs):
        raise ValueError("digon")
    if any((v, w) in arcs and (w, u) in arcs
           for u, v in arcs for w in range(n)):
        raise ValueError("directed triangle")
    outdegrees = tuple(len(row) for row in outneighbors)
    if min(outdegrees) < 2:
        raise ValueError("local minimum outdegree below 2")
    indegrees = tuple(sum((u, v) in arcs for u in range(n)) for v in range(n))
    return {
        "arcs": len(arcs),
        "outdegrees": outdegrees,
        "indegrees": indegrees,
        "degree_two_vertices": sum(d == 2 for d in outdegrees),
    }


def budget_lower_bound(m):
    """Consequences of min outdegree 2, max indegree 3 and indegree 3 => outdegree 2.

    q >= 24-m by the outdegree sum. q >= m-16 by the indegree sum
    and the indegree-three implication. These hypotheses are external
    mathematical lemmas, not verified by an enumeration here.
    """
    if not isinstance(m, int) or not 16 <= m <= 21:
        raise ValueError("local arc budget must be an integer in [16, 21]")
    return max(24 - m, m - 16)


def main():
    data = verify_local_graph(WITNESS)
    assert data == {
        "arcs": 20,
        "outdegrees": (2, 2, 2, 2, 3, 3, 3, 3),
        "indegrees": (3, 3, 3, 3, 2, 2, 2, 2),
        "degree_two_vertices": 4,
    }
    bounds = {m: budget_lower_bound(m) for m in range(16, 22)}
    assert bounds == {16: 8, 17: 7, 18: 6, 19: 5, 20: 4, 21: 5}
    print("verified: eight-vertex 20-arc C3-free oriented witness with four degree-two vertices")
    print("integer local degree-two bounds by arc count:", bounds)
    print("scope: local structural check only; no 24-vertex or novelty certificate")


if __name__ == "__main__":
    main()
