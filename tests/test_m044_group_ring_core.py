import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from m044_group_ring_core import check, cyclic, multiply, validate


class GroupRingCoreTests(unittest.TestCase):
    def test_exhaustive(self):
        self.assertIn('passed', check())

    def test_reject_out_of_range(self):
        with self.assertRaises(ValueError):
            multiply(8, 1, cyclic(3))
        with self.assertRaises(ValueError):
            multiply(-1, 1, cyclic(3))

    def test_nonassociative_latin_loop(self):
        # Standard order-five Latin quasigroup x*y = 2x-y mod 5:
        # Latin but lacks a two-sided identity.
        with self.assertRaises(ValueError):
            validate([[(2*i-j) % 5 for j in range(5)] for i in range(5)])


if __name__ == '__main__':
    unittest.main()
