"""Adversarial exact controls for the bounded M073 two-step graphon audit."""
import itertools
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sidorenko_twoblock as s


def brute(points, faces, W):
    """Brute-force all binary assignments to all incidence vertices (tiny only)."""
    edges = [(i, points + j) for j, face in enumerate(faces) for i in face]
    n = points + len(faces)
    return sum(__import__("math").prod(W[mask[u]][mask[v]] for u, v in edges)
               for mask in itertools.product((0, 1), repeat=n))


class SmallGraphControls(unittest.TestCase):
    def test_independent_incidence_and_edge_methods_against_brute(self):
        families = (
            (3, ((0, 1, 2),)),                       # 3-star K1,3
            (4, ((0, 1, 2), (0, 2, 3))),             # overlapping faces
            (5, ((0, 1, 2), (2, 3, 4))),             # connected, 7 vertices
        )
        for a, b, c in itertools.product((0, 1, 2), repeat=3):
            W = s.weights(a, b, c)
            for points, faces in families:
                with self.subTest(W=W, points=points, faces=faces):
                    expected = brute(points, faces, W)
                    self.assertEqual(s.numerator_by_faces(faces, W, points), expected)
                    self.assertEqual(s.numerator_by_elimination(faces, W, points), expected)

    def test_odd_cycle_violates_analogue_negative_control(self):
        # With cross-edges only, p=1/2 but t(K3)=0. This confirms the
        # general edge-factor evaluator can represent an actual violation
        # for NONBIPARTITE patterns; it is not an M073 counterexample.
        W = s.weights(0, 2, 0)
        hom = s.numerator_by_edges(3, [(0, 1), (1, 2), (0, 2)], W)
        self.assertEqual(hom, 0)
        self.assertGreater((0 + 2*2 + 0)**3, hom * 2**(2*3-3))

    def test_isolated_vertex_and_malformed_graph(self):
        self.assertEqual(s.numerator_by_edges(2, [], s.weights(2, 2, 2)), 4)
        self.assertEqual(s.numerator_by_edges(0, [], s.weights(0, 0, 0)), 1)
        for edges in ([(0, 0)], [(0, 2)], [(-1, 1)], [(0, 1), (1, 0)]):
            with self.subTest(edges=edges), self.assertRaises(ValueError):
                s.numerator_by_edges(2, edges, s.weights(2, 1, 0))

    def test_weight_validation(self):
        for values in ((-1, 0, 1), (0, 1, 3), (True, 0, 1), (0, 1, 0.5)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                s.compare(((0, 1, 2),), *values, denominator=2)
        for D in (0, -1, True, 1.5):
            with self.subTest(D=D), self.assertRaises(ValueError):
                s.compare(((0, 1, 2),), 0, 0, 0, denominator=D)


class PinnedSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faces = s.read_faces()

    def test_baseline_grid_exact(self):
        result = s.audit_grid(self.faces)
        self.assertEqual(result["pattern_vertices"], 35)
        self.assertEqual(result["pattern_edges"], 66)
        self.assertEqual(result["grid_size"], 27)
        self.assertEqual(result["strict_violations"], 0)
        self.assertEqual(result["positive_gap_cases"], 24)
        self.assertEqual(result["equality_cases"], 3)
        self.assertEqual(result["equality_weights"], [[0, 0, 0], [1, 1, 1], [2, 2, 2]])
        self.assertEqual(result["violations"], [])

    def test_reject_mutated_faces_and_dimensions(self):
        original = json.loads(s.FACES_PATH.read_text(encoding="utf-8"))
        invalid = [
            {**original, "point_count": 12},
            {**original, "expected_edges": 65},
            {**original, "faces": original["faces"][:-1]},
            {**original, "faces": original["faces"][:-1] + [original["faces"][0]]},
            {**original, "faces": [original["faces"][0][::-1], *original["faces"][1:]]},
            {**original, "faces": [[0, 0, 1], *original["faces"][1:]]},
            {**original, "faces": [[0, 1, 13], *original["faces"][1:]]},
            {**original, "faces": [[0, 1, 4], *original["faces"][1:]]},
        ]
        for bad in invalid:
            with self.subTest(bad=bad.get("point_count", bad.get("faces", [])[0])):
                with tempfile.TemporaryDirectory() as d:
                    path = Path(d) / "faces.json"
                    path.write_text(json.dumps(bad), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        s.read_faces(path)

    def test_no_unregistered_grid_expansion(self):
        for values, denominator in [((0, 1), 1), ((0, 1, 2, 3), 3)]:
            with self.assertRaises(ValueError):
                s.audit_grid(self.faces, values, denominator)


if __name__ == "__main__":
    unittest.main()
