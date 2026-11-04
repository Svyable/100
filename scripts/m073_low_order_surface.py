#!/usr/bin/env python3
"""Exact low-order even-subgraph spectrum for closed triangular 2-manifolds.

Combinatorial prediction uses the 1-skeleton only. Independent control counts
literal simple cycles in the bipartite point/face incidence graph.
Not a general Sidorenko proof or a claim of historical novelty.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from math import comb
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/reference/sidorenko_faces.json"


def validate(faces, points):
    if type(points) is not int or points < 4:
        raise ValueError("at least four vertices required")
    f = [tuple(sorted(t)) for t in faces]
    if any(len(t) != 3 or len(set(t)) != 3 or
           any(type(v) is not int or v < 0 or v >= points for v in t) for t in f):
        raise ValueError("invalid simplicial triangle")
    if len(f) != len(set(f)):
        raise ValueError("repeated face")
    edge_faces = defaultdict(list)
    links = [defaultdict(set) for _ in range(points)]
    for j, (a,b,c) in enumerate(f):
        for u,v in ((a,b),(b,c),(a,c)):
            edge_faces[tuple(sorted((u,v)))].append(j)
        for u,v,w in ((a,b,c),(b,a,c),(c,a,b)):
            links[u][v].add(w)
            links[u][w].add(v)
    if any(len(fs) != 2 for fs in edge_faces.values()):
        raise ValueError("non-closed edge incidence")
    for link in links:
        if len(link) < 3 or any(len(nbr) != 2 for nbr in link.values()):
            raise ValueError("non-manifold vertex link")
        # Reject disconnected links, including wedges of closed surfaces.
        start = next(iter(link))
        visited, todo = set(), [start]
        while todo:
            v = todo.pop()
            if v in visited:
                continue
            visited.add(v)
            todo.extend(link[v] - visited)
        if len(visited) != len(link):
            raise ValueError("disconnected vertex link")
    if len(edge_faces) * 2 != 3 * len(f):
        raise AssertionError("edge-face incidence identity")
    return f, dict(edge_faces)


def nonfacial_triangles(faces, points, edge_faces):
    face_set = set(faces)
    edges = set(edge_faces)
    return [t for t in combinations(range(points), 3)
            if t not in face_set and all(tuple(sorted(e)) in edges
                                         for e in combinations(t, 2))]


def four_cycles_skeleton(edge_faces, points):
    edges = set(edge_faces)
    for verts in combinations(range(points), 4):
        start = verts[0]
        for rest in permutations(verts[1:]):
            if rest[0] > rest[-1]:
                continue
            cycle = (start,) + rest
            if all(tuple(sorted((cycle[i],cycle[(i+1)%4]))) in edges
                   for i in range(4)):
                yield cycle


def predicted(faces, points):
    faces, edge_faces = validate(faces, points)
    f, e = len(faces), len(edge_faces)
    s = len(nonfacial_triangles(faces, points, edge_faces))
    c8 = 0
    skeleton_cycles = 0
    for cycle in four_cycles_skeleton(edge_faces, points):
        skeleton_cycles += 1
        choices = [edge_faces[tuple(sorted((cycle[i],cycle[(i+1)%4])))]
                   for i in range(4)]
        c8 += sum(len(set(assignment)) == 4 for assignment in product(*choices))
    disjoint_squares = comb(e, 2) - 3*f
    return dict(faces=f, edges=e, nonfacial_triangles=s,
                squares=e, hexagons=4*f+8*s, octagons=c8,
                square_pairs=disjoint_squares, c8=c8+disjoint_squares,
                skeleton_four_cycles=skeleton_cycles)


def incidence_cycles(faces, points, lengths=(4,6,8)):
    """Literal DFS on H, no 1-skeleton triangle or 4-cycle formula used."""
    n = points + len(faces)
    adj = [set() for _ in range(n)]
    for j, face in enumerate(faces):
        for v in face:
            adj[v].add(points+j)
            adj[points+j].add(v)
    out = {}
    for length in lengths:
        found = set()
        for root in range(n):
            stack = [(root, (root,))]
            while stack:
                v, path = stack.pop()
                if len(path) == length:
                    if root in adj[v] and path[1] < path[-1]:
                        found.add(tuple(path))
                    continue
                for w in adj[v]:
                    if w > root and w not in path:
                        stack.append((w, path+(w,)))
        out[length] = len(found)
    return out


def octahedron():
    return list(product((0,1),(2,3),(4,5))), 6


def icosahedron():
    upper = [1,2,3,4,5]
    lower = [6,7,8,9,10]
    f = []
    for i in range(5):
        j = (i+1)%5
        f.extend(((0,upper[i],upper[j]), (11,lower[i],lower[j]),
                  (upper[i],upper[j],lower[i]),
                  (upper[j],lower[i],lower[j])))
    return f, 12


def glued_octahedra():
    a, _ = octahedron()
    # Identify second octahedron vertices (0,2,4) with the first face.
    remap = {0:0,2:2,4:4,1:6,3:7,5:8}
    b = [tuple(remap[v] for v in t) for t in a]
    removed = frozenset((0,2,4))
    return ([t for t in a if frozenset(t) != removed]
            + [t for t in b if frozenset(t) != removed]), 9


def split_octahedron_three_edges():
    """Nine-vertex no-separator sphere: split (0,2), (0,3), (1,2)."""
    faces, points = octahedron()
    for u,v in ((0,2),(0,3),(1,2)):
        hits = [t for t in faces if u in t and v in t]
        assert len(hits) == 2
        others = [next(w for w in t if w not in (u,v)) for t in hits]
        faces = [t for t in faces if t not in hits]
        faces.extend((u,points,w) for w in others)
        faces.extend((v,points,w) for w in others)
        points += 1
    validate(faces,points)
    return faces,points


def source():
    d = json.loads(SOURCE.read_text())
    return d["faces"], d["point_count"]


def check_instance(faces, points):
    a = predicted(faces, points)
    b = incidence_cycles(faces, points)
    assert (a["squares"],a["hexagons"],a["octagons"]) == (b[4],b[6],b[8]), (a,b)
    assert a["c8"] == a["octagons"] + a["square_pairs"]
    return a


def check():
    samples = {"tetrahedron":(list(combinations(range(4),3)),4),
               "octahedron":octahedron(),
               "icosahedron":icosahedron(),
               "glued_octahedra":glued_octahedra(),
               "split_octahedron":split_octahedron_three_edges(),
               "source_H":source()}
    out = {name:check_instance(*case) for name,case in samples.items()}
    assert out["glued_octahedra"]["nonfacial_triangles"] == 1
    assert out["glued_octahedra"]["hexagons"] == 64
    assert out["split_octahedron"]["hexagons"] == 56
    assert out["split_octahedron"]["faces"] == out["glued_octahedra"]["faces"] == 14
    assert out["split_octahedron"]["edges"] == out["glued_octahedra"]["edges"] == 21
    assert out["source_H"]["nonfacial_triangles"] == 0
    assert (out["source_H"]["squares"],out["source_H"]["hexagons"],
            out["source_H"]["c8"]) == (33,88,823)
    assert (out["source_H"]["octagons"],out["source_H"]["square_pairs"]) == (361,462)
    return out


if __name__ == "__main__":
    print(json.dumps(check(), indent=2, sort_keys=True))
