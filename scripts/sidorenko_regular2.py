#!/usr/bin/env python3
"""Quantitative continuous two-block Sidorenko bound for the pinned M073 graph.

Author-derived application of the classical high-temperature/even-subgraph
expansion. The 4- and 6-cycle coefficients are independently computed here;
external priority and specialist proof review are NOT established.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
import json
from math import comb

import sidorenko_twoblock as baseline


def incidence_edges(faces, points=13):
    return tuple(sorted((i, points + j) for j, face in enumerate(faces) for i in face))


def small_cycles_from_faces(faces):
    """C4: repeated point pairs; C6: three pair-faces all distinct."""
    pairs = defaultdict(list)
    for fid, triple in enumerate(faces):
        if len(set(triple)) != 3:
            raise ValueError("repeated incidence point")
        for edge in combinations(sorted(triple), 2):
            pairs[edge].append(fid)
    c4 = sum(comb(len(fs), 2) for fs in pairs.values())
    c6 = 0
    for a, b, c in combinations(sorted({v for f in faces for v in f}), 3):
        for x in pairs.get((a, b), ()):
            for y in pairs.get((b, c), ()):
                for z in pairs.get((a, c), ()):
                    if len({x, y, z}) == 3:
                        c6 += 1
    return c4, c6


def point_skeleton_certificate(faces):
    """Independent point-only triangle census for the special M073 table.

    Each of the 33 pairs appears in two triples, and the only triangles
    in the 13-vertex skeleton are exactly the 22 listed face triples.
    Consequently, four of the eight edge-face choices at each skeleton
    triangle have three DISTINCT faces: 22*4=88 six-cycles.
    """
    points = {x for face in faces for x in face}
    pair_mult = Counter(edge for face in faces for edge in combinations(sorted(face), 2))
    all_triangles = {
        triple for triple in combinations(sorted(points), 3)
        if all(pair_mult.get(edge, 0) for edge in combinations(triple, 2))
    }
    face_set = {tuple(sorted(face)) for face in faces}
    if (len(pair_mult) != 33 or set(pair_mult.values()) != {2}
            or len(all_triangles) != 22 or all_triangles != face_set):
        raise AssertionError("pinned M073 point skeleton does not have its asserted structure")
    return {"skeleton_edges": 33, "skeleton_triangles": len(all_triangles),
            "six_cycles_from_four_choices_per_triangle": 4 * len(all_triangles)}


def cycles_by_graph_dfs(nodes, edges, length):
    """Separate graph-only simple-cycle enumeration; each cycle once."""
    if length < 3:
        raise ValueError("cycle length must be >=3")
    adj = [set() for _ in range(nodes)]
    for u, v in edges:
        if u == v or u < 0 or v < 0 or u >= nodes or v >= nodes:
            raise ValueError("simple graph required")
        adj[u].add(v)
        adj[v].add(u)
    count = 0
    for origin in range(nodes):
        path = [origin]
        def walk():
            nonlocal count
            if len(path) == length:
                if origin in adj[path[-1]] and path[1] < path[-1]:
                    count += 1
                return
            for nxt in adj[path[-1]]:
                # origin is unique minimum of its cycle
                if nxt > origin and nxt not in path:
                    path.append(nxt)
                    walk()
                    path.pop()
        walk()
    return count


def certificate():
    faces = baseline.read_faces()  # SHA-256 pinned
    edges = incidence_edges(faces)
    assert len(edges) == 66 and len(set(edges)) == 66
    c4, c6 = small_cycles_from_faces(faces)
    skeleton = point_skeleton_certificate(faces)
    if c6 != skeleton["six_cycles_from_four_choices_per_triangle"]:
        raise AssertionError("point-skeleton triangle count differs from C6 result")
    alternate = (cycles_by_graph_dfs(35, edges, 4),
                 cycles_by_graph_dfs(35, edges, 6))
    if (c4, c6) != alternate:
        raise AssertionError("independent incidence and graph-cycle counts disagree")
    if (c4, c6) != (33, 88):
        raise AssertionError("cycle coefficient drift for frozen M073 pattern")
    # Independent structural checks: incidence graph bipartite/connected.
    adj = [set() for _ in range(35)]
    for u, v in edges:
        if u >= 13 or v < 13:
            raise AssertionError("wrong bipartition")
        adj[u].add(v)
        adj[v].add(u)
    reached = {0}
    todo = [0]
    while todo:
        for x in adj[todo.pop()]:
            if x not in reached:
                reached.add(x)
                todo.append(x)
    if len(reached) != 35:
        raise AssertionError("H is not connected, cycle-space checksum invalid")
    cycle_rank = len(edges) - 35 + 1
    return {
        "schema": "svyable.m073.regular2-bound.v1",
        "pattern_vertices": 35,
        "pattern_edges": 66,
        "connected": True,
        "bipartite": True,
        "four_cycles": c4,
        "point_skeleton": skeleton,
        "six_cycles": c6,
        "independent_dfs_four_cycles": alternate[0],
        "independent_dfs_six_cycles": alternate[1],
        "cycle_space_dimension": cycle_rank,
        "total_even_subgraphs_at_abs_r_one": 1 << cycle_rank,
        "fixed_face_sha256": baseline.FACES_SHA256,
        "bound": "t(H,W) >= p^66 * (1+33*r^4+88*r^6); p=(a+b)/2, r=(a-b)/(a+b)",
        "domain": "W=[[a,b],[b,a]], a,b real in [0,1], p>0; at p=0 both sides are 0",
        "equality": "a=b (including a=b=0); strict when a!=b",
        "boundary": ("Author-derived quantified restriction, standard high-temperature expansion. "
                     "Not all two-step graphons, not a full Sidorenko result, "
                     "no external novelty or specialist review certified."),
    }


def check_rational(a, b, denominator=4, independently_recount=False):
    """Exact integer inequality for rational graphon W=[[a,b],[b,a]]/D."""
    if (type(denominator) is not int or denominator <= 0
            or any(type(v) is not int or v < 0 or v > denominator for v in (a, b))):
        raise ValueError("rational weights require integer 0<=a,b<=denominator")
    faces = baseline.read_faces()
    matrix = baseline.weights(a, b, a)
    T = baseline.numerator_by_faces(faces, matrix)
    if independently_recount and T != baseline.numerator_by_elimination(faces, matrix):
        raise AssertionError("direct pair-factor replay mismatch")
    m, v = 66, 35
    if a+b == 0:
        assert T == 0
        return {"a":a,"b":b,"D":denominator,"left":0,"right":0,"strict":False}
    # Exact inequality 2^(m-v)*T >= (a+b)^m +
    # N4*(a-b)^4*(a+b)^(m-4) + N6*(a-b)^6*(a+b)^(m-6)
    left = (1 << (m-v)) * T
    right = ((a+b)**m +
             33*(a-b)**4*(a+b)**(m-4) +
             88*(a-b)**6*(a+b)**(m-6))
    if left < right or (left > right) != (a != b):
        raise AssertionError("quantitative theorem failed at rational test point")
    return {"a":a,"b":b,"D":denominator,"left":left,"right":right,
            "strict":left>right}


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = certificate()
    if args.check:
        for a in range(5):
            for b in range(5):
                check_rational(a,b,independently_recount=(a,b) in ((0,4),(1,3),(2,2),(4,0)))
        report["rational_grid_checked"] = 25
    print(json.dumps(report, indent=2, sort_keys=True) if args.json or args.check
          else f"M073: exact C4={report['four_cycles']}, C6={report['six_cycles']}; "
               f"continuum regular-two-block bound, novelty review outstanding")


if __name__ == "__main__":
    main()
