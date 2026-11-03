"""Adversarial tests for the M019 fixed-shift negative certificate."""
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import straus_shift_gate as gate


class ShiftGateTests(unittest.TestCase):
    def test_exact_prime_and_factors(self):
        self.assertTrue(gate.prime(1129))
        self.assertFalse(gate.prime(1129 * 71))
        self.assertEqual(gate.factor(1129 * 284), {2: 2, 71: 1, 1129: 1})

    def test_shift3_subgroup_obstruction(self):
        mres, residues = gate.subgroup_residues(1129, 3)
        self.assertEqual((mres, residues), (1, {1}))
        self.assertNotIn((-mres) % 3, residues)
        self.assertIsNone(gate.witness(1129, 3))

    def test_shift7_subgroup_obstruction(self):
        mres, residues = gate.subgroup_residues(1129, 7)
        self.assertEqual((mres, residues), (1, {1, 2, 4}))
        self.assertNotIn((-mres) % 7, residues)
        self.assertIsNone(gate.witness(1129, 7))

    def test_shift11_positive_control(self):
        x, y, z, d = gate.witness(1129, 11)
        self.assertEqual((x, y, z, d), (285, 29260, 99103620, 95))
        self.assertEqual(Fraction(4, 1129),
                         Fraction(1, x) + Fraction(1, y) + Fraction(1, z))

    def test_two_independent_positive_controls(self):
        self.assertIsNotNone(gate.witness(97, 3))
        self.assertIsNotNone(gate.witness(73, 7))

    def test_divisor_completeness_small_m(self):
        self.assertEqual(gate.divisors_from_factors({2: 2, 3: 1}),
                         [1, 2, 3, 4, 6, 12])
        for n in (5, 9, 13, 17, 21):
            for c in (3, 7):
                x = (n + c) // 4
                m = n * x
                exists = any((m + d) % c == 0 and (m + m*m//d) % c == 0
                             for d in range(1, m*m + 1) if m*m % d == 0)
                self.assertEqual(exists, gate.witness(n, c) is not None)

    def test_smallest_both_fail(self):
        failing = [n for n in range(25, 1130)
                   if n % 24 == 1 and gate.prime(n)
                   and gate.witness(n, 3) is None and gate.witness(n, 7) is None]
        self.assertEqual(failing, [1129])

    def test_invalid_inputs(self):
        for n, c in [(1, 3), (73, 0), (73, 5)]:
            with self.assertRaises(ValueError):
                gate.witness(n, c)


if __name__ == "__main__":
    unittest.main()
