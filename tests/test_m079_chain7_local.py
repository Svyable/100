"""Adversarial tests for the bounded seven-outsider balance certificate."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m079_chain7_local as mod


class ChainSevenLocalTests(unittest.TestCase):
    def test_canonical_multiset_counts(self):
        self.assertEqual([mod.canonical_count(k) for k in (4, 5, 6)],
                         [4887, 55432, 436680])

    def test_witness_full_poset(self):
        E, best, before = mod.literal_balance(mod.WITNESS)
        self.assertEqual((E, best), (107157, 44873))
        self.assertTrue(all(before[i][j] + before[j][i] == E
                            for i in range(len(before))
                            for j in range(i + 1, len(before))))

    def test_width_eight_rejected(self):
        self.assertFalse(mod.valid(((-1, 1),) * 7))

    def test_single_gap_rejected(self):
        self.assertFalse(mod.valid(((-1, 0),) * 6 + ((0, 0),)))

    def test_long_interval_rejected(self):
        self.assertFalse(mod.valid(((-6, 0),) + ((0, 1),) * 6))

    def test_order_duality(self):
        dual = tuple(sorted((-b, -a) for a, b in mod.WITNESS))
        self.assertTrue(mod.valid(dual))
        self.assertEqual(mod.literal_balance(dual)[:2],
                         mod.literal_balance(mod.WITNESS)[:2])

    def test_outsider_permutation(self):
        rotated = mod.WITNESS[1:] + mod.WITNESS[:1]
        self.assertEqual(mod.literal_balance(rotated)[:2],
                         mod.literal_balance(mod.WITNESS)[:2])

    def test_full_dual_replay(self):
        summary = mod.check()
        self.assertEqual(summary["cases"], 436680)
        self.assertEqual(summary["dual_checked"], 436680)
        self.assertEqual(summary["minimum"], "44873/107157")
        self.assertTrue(summary["mutation_rejected"])


if __name__ == "__main__":
    unittest.main()
