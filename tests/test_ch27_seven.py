"""Independent adjacency-matrix controls for the CH27 seven-vertex lemma."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch27_seven as seven


def independent_check(edges):
    mat = [[0] * 7 for _ in range(7)]
    for a, b in edges:
        if a == b or mat[a][b] or mat[b][a]:
            return None
        mat[a][b] = 1
    indegrees = [sum(mat[u][v] for u in range(7)) for v in range(7)]
    triangles = sum(mat[u][v] * mat[v][w] * mat[w][u]
                    for u in range(7) for v in range(7) for w in range(7))
    return len(edges), max(indegrees), triangles == 0


class DenseSevenTests(unittest.TestCase):
    def test_unique_dense_class_exhaustion(self):
        self.assertEqual(seven.enumerate_unique_dense_graph(), {
            "orientations": 262144, "indegree_cap_survivors": 19592,
            "triangle_free_and_cap": 0
        })

    def test_positive_witness_and_strict_validation(self):
        self.assertEqual(independent_check(seven.POSITIVE), (16, 3, True))
        self.assertEqual(seven.inspect_edges(seven.POSITIVE), {
            "arcs": 16, "maximum_indegree": 3, "triangle_free": True
        })
        for invalid in ([(0, 0)], [(0, 1), (1, 0)], [(0, 1), (0, 1)]):
            with self.assertRaises(ValueError):
                seven.inspect_edges(invalid)

    def test_triangle_negative_control(self):
        bad = [(0, 1), (1, 2), (2, 0)]
        self.assertEqual(independent_check(bad), (3, 1, False))
        self.assertFalse(seven.inspect_edges(bad)["triangle_free"])

    def test_old_irregular_profile_rejected_not_full_case(self):
        profile = seven.boundary_profile()
        self.assertTrue(profile["excluded"])
        self.assertEqual(profile["minimum_arcs_inside_C"], 18)
        self.assertEqual(profile["seven_vertex_arc_cap"], 17)


if __name__ == "__main__":
    unittest.main()
