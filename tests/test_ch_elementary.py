"""Independent finite and negative controls for the M074 elementary proof."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ch_six_check import has_triangle, search_six


class ElementaryExclusionTests(unittest.TestCase):
    def test_all_partial_orientations_of_k6_are_excluded(self):
        result = search_six()
        self.assertIsNone(result["witness"])
        self.assertEqual(result["visited"], 42002)
        self.assertEqual(result["pruned_triangle"], 20164)
        self.assertEqual(result["pruned_degree"], 63841)

    def test_seven_vertex_control_is_not_excluded_by_six_lemma(self):
        # Cyclic arcs of length 1 and 2 mod 7: three positive steps
        # sum to at most six, so cannot close a directed triangle.
        out = [sum(1 << ((u + d) % 7) for d in (1, 2)) for u in range(7)]
        self.assertTrue(all(row.bit_count() == 2 for row in out))
        self.assertFalse(has_triangle(out))

    def test_a_triangle_is_detected(self):
        out = [1 << 1, 1 << 2, 1 << 0]
        self.assertTrue(has_triangle(out))


if __name__ == "__main__":
    unittest.main()
