"""Adversarial controls for the enumeration-free CH (24,8) proof audit."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch24_weighted_deficit as wd


class WeightedDeficitTests(unittest.TestCase):
    def test_exact_relaxed_cover(self):
        result = wd.audit()
        self.assertEqual((result["alpha_histograms"], result["k_histograms"]),
                         (19, 5005))
        self.assertEqual((result["cut_profiles"], result["weighted_excluded"],
                          result["capacity_excluded"], result["unresolved"]),
                         (20500, 20287, 213, 0))

    def test_one_unit_cut_mutation_fails(self):
        result = wd.audit(cut_slack=1)
        self.assertEqual(result["unresolved"], 2)
        self.assertEqual(result["unresolved_histograms"], [
            ((7, 0, 0, 0, 0, 1), (3, 0, 0, 0, 0, 5, 1)),
            ((7, 0, 0, 0, 0, 1), (3, 0, 0, 0, 1, 3, 2)),
        ])

    def test_local_B_capacity_is_not_vacuous(self):
        # Six positive k=6 force 42 outgoing B-arcs, capacity only 33.
        alpha = (7, 0, 0, 1, 0, 0)  # (2^7,5), admissible A profile
        self.assertTrue(wd.capacity_violation(alpha, (3, 0, 0, 0, 0, 0, 6)))
        # All-zero incoming k has no forced B-outdegree; this passes.
        self.assertFalse(wd.capacity_violation((7, 0, 0, 0, 0, 1),
                                               (9, 0, 0, 0, 0, 0, 0)))

    def test_histogram_generation_is_complete_and_bounded(self):
        alphas = wd.alpha_histograms()
        self.assertEqual(len(alphas), 19)
        self.assertEqual(len(set(alphas)), 19)
        for hist in alphas:
            self.assertEqual(sum(hist), 8)
            self.assertLessEqual(sum(j * hist[j] for j in range(6)), 5)
        ks = wd.k_histograms()
        self.assertEqual(len(ks), 5005)
        self.assertEqual(len(set(ks)), 5005)
        self.assertTrue(all(sum(hist) == 9 for hist in ks))

    def test_invalid_cut_slack_rejected(self):
        for value in (-1, 0.5, True):
            with self.assertRaises(ValueError):
                wd.audit(value)


if __name__ == "__main__":
    unittest.main()
