"""Adversarial checks for surface incidence Ising coefficients.

Compares a 1-skeleton formula, literal incidence cycles, and the existing
face-elimination parity DP (distinct representations).
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
from random import Random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m073_low_order_surface as surf
import m073_information_alignment as parity


def flip(faces, points, edge):
    faces = [tuple(sorted(f)) for f in faces]
    a,b = edge
    hits = [f for f in faces if a in f and b in f]
    if len(hits) != 2:
        return None
    c = next(v for v in hits[0] if v not in edge)
    d = next(v for v in hits[1] if v not in edge)
    if c == d or any(c in f and d in f for f in faces):
        return None
    result = [f for f in faces if f not in hits]
    result += [(a,c,d),(b,c,d)]
    surf.validate(result, points)
    return result


class LowOrderSurfaceTests(unittest.TestCase):
    def test_four_independent_fixture_families(self):
        report = surf.check()
        self.assertEqual(report["source_H"]["c8"], 823)
        self.assertEqual(report["source_H"]["hexagons"], 88)
        self.assertEqual(report["glued_octahedra"]["nonfacial_triangles"], 1)
        self.assertEqual(report["split_octahedron"]["nonfacial_triangles"], 0)
        self.assertEqual(report["split_octahedron"]["hexagons"], 56)
        self.assertEqual(report["glued_octahedra"]["hexagons"], 64)

    def test_parity_dp_not_cycle_based(self):
        for faces,points in (surf.octahedron(),surf.icosahedron(),
                             surf.glued_octahedra(),surf.split_octahedron_three_edges(),
                             surf.source()):
            a = surf.predicted(faces,points)
            c = parity.coefficients_by_parity(faces,points)
            self.assertEqual((c[2],c[3],c[4]),
                             (a["squares"],a["hexagons"],a["c8"]))

    def test_nine_vertex_sphere_pair_has_same_f_vector_and_min_degree_four(self):
        for faces,points in (surf.glued_octahedra(),
                             surf.split_octahedron_three_edges()):
            f,edge_faces = surf.validate(faces,points)
            self.assertEqual((points,len(edge_faces),len(f)),(9,21,14))
            deg = [0]*points
            adj = [set() for _ in range(points)]
            for u,v in edge_faces:
                deg[u] += 1
                deg[v] += 1
                adj[u].add(v)
                adj[v].add(u)
            self.assertGreaterEqual(min(deg),4)
            seen,todo = set(),[0]
            while todo:
                v = todo.pop()
                if v not in seen:
                    seen.add(v)
                    todo.extend(adj[v]-seen)
            self.assertEqual(len(seen),points)
            self.assertEqual(points-len(edge_faces)+len(f),2)

    def test_stronger_face_only_formula_fails(self):
        faces,points = surf.glued_octahedra()
        a = surf.predicted(faces,points)
        self.assertEqual(a["hexagons"]-4*len(faces),8)
        self.assertEqual(a["nonfacial_triangles"],1)

    def test_seeded_flips_and_relabeling(self):
        rng = Random(20261102)
        for original,points in (surf.octahedron(),surf.icosahedron(),
                                surf.glued_octahedra()):
            faces = list(original)
            successes = 0
            for _ in range(30):
                _,edge_faces = surf.validate(faces,points)
                edge = rng.choice(sorted(edge_faces))
                modified = flip(faces,points,edge)
                if modified is not None:
                    faces = modified
                    successes += 1
                    surf.check_instance(faces,points)
            self.assertGreater(successes,0)
            relabel = list(range(points))
            rng.shuffle(relabel)
            renamed = [tuple(relabel[v] for v in t) for t in faces]
            self.assertEqual(surf.predicted(faces,points)["hexagons"],
                             surf.predicted(renamed,points)["hexagons"])

    def test_reject_boundary_duplicate_and_bad_link(self):
        faces,points = surf.octahedron()
        for invalid,n in ((faces[:-1],points),(faces+[faces[0]],points),
                          ([(0,1,2)],3),([(0,1,2)],4)):
            with self.assertRaises(ValueError):
                surf.validate(invalid,n)
        # Two tetrahedral spheres wedged at one point: every edge is
        # still in two faces, but the common vertex link is disconnected.
        a = list(combinations(range(4),3))
        b = [tuple({0:0,1:4,2:5,3:6}[v] for v in t) for t in a]
        with self.assertRaises(ValueError):
            surf.validate(a+b,7)

    def test_reject_mutated_face(self):
        faces,points = surf.glued_octahedra()
        changed = list(faces)
        changed[0] = (0,1,8)
        with self.assertRaises(ValueError):
            surf.validate(changed,points)


if __name__ == "__main__":
    unittest.main()
