import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from m044_regular_rank import check, rank_gf2, left_regular_columns
from m044_group_ring_core import cyclic


class RegularRankTests(unittest.TestCase):
    def test_exhaustive_units(self):
        result = check()
        self.assertEqual(sum(result["C3"]), 8)
        self.assertEqual(sum(result["S3"]), 64)

    def test_singular_zero_and_identity(self):
        t = cyclic(3)
        self.assertEqual(rank_gf2(left_regular_columns(0, t), 3), 0)
        self.assertEqual(rank_gf2(left_regular_columns(1, t), 3), 3)

    def test_adversarial_rank_and_range(self):
        self.assertEqual(rank_gf2([3, 5, 6], 3), 2)
        with self.assertRaises(ValueError):
            rank_gf2([8], 3)
        with self.assertRaises(ValueError):
            left_regular_columns(8, cyclic(3))
