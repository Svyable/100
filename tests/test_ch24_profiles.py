import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ch24_profiles


class CH24ProfileTests(unittest.TestCase):
    def test_independent_histogram_enumerators_agree(self):
        a = ch24_profiles.histograms_from_indegrees()
        b = ch24_profiles.histograms_from_deficit_partitions()
        self.assertEqual(a, b)
        self.assertEqual(len(a), 1076)
        for hist in a:
            self.assertEqual(len(hist), 10)
            self.assertEqual(sum(hist), 24)
            self.assertEqual(sum(d * n for d, n in enumerate(hist)), 192)

    def test_four_low_neighbors_arithmetic(self):
        bounds = ch24_profiles.local_degree_lower_bound()
        self.assertEqual(bounds[20], 4)
        self.assertEqual(bounds[21], 5)
        self.assertTrue(all(bound >= 4 for bound in bounds.values()))

    def test_local_sharpness_witness_no_triangle(self):
        w = ch24_profiles.local_witness_check()
        self.assertEqual(w["arcs"], 20)
        self.assertEqual(w["outdegree_two_count"], 4)
        self.assertEqual(sum(w["outdegrees"]), 20)
        self.assertEqual(sum(w["indegrees"]), 20)

    def test_witness_rejects_digons_and_triangles(self):
        edges = list(ch24_profiles.LOCAL_EDGES)
        edges[0] = (0, 2)  # Reverse an edge: profile check must reject.
        with self.assertRaises(ValueError):
            ch24_profiles.local_witness_check(tuple(edges))
        edges = list(ch24_profiles.LOCAL_EDGES)
        edges[1] = (0, 4)  # Reversal creates a directed triangle.
        with self.assertRaises(ValueError):
            ch24_profiles.local_witness_check(tuple(edges))
        edges = list(ch24_profiles.LOCAL_EDGES)
        edges[1] = (2, 0)  # Duplicate arc.
        with self.assertRaises(ValueError):
            ch24_profiles.local_witness_check(tuple(edges))

    def test_numeric_profile_filter_not_a_graph_solver(self):
        stats = ch24_profiles.check()
        self.assertEqual(stats["histograms_with_indegree_nine"], 1075)
        self.assertEqual(stats["histograms_surviving_necessary_5h_le_8l"], 83)
        self.assertEqual(stats["numeric_histograms_excluded_after_irregular_branch"], 992)
        self.assertIn("no 24-vertex graph existence", stats["note"])

    def test_filter_accepts_balanced_irregular_profile(self):
        # One 9, one 7, twenty-two 8: 5h <= 8l, but no graph claim.
        hist = [0] * 10
        hist[9], hist[7], hist[8] = 1, 1, 22
        self.assertTrue(ch24_profiles.admissible_histogram(tuple(hist)))
        # A high count of nine-degree vertices with one low-degree sink is impossible.
        hist = [0] * 10
        hist[9], hist[6], hist[8] = 2, 1, 21
        self.assertFalse(ch24_profiles.admissible_histogram(tuple(hist)))


if __name__ == "__main__":
    unittest.main()
