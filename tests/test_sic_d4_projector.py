"""Adversarial exact checks for the published dimension-four SIC replay."""
import copy
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sic_d4_projector as s


class SicD4Tests(unittest.TestCase):
    def test_published_certificate(self):
        cert = s.verify()
        self.assertEqual((cert["dimension"], cert["projectors"], cert["off_diagonal_pairs"]),
                         (4, 16, 120))
        self.assertEqual(cert["exact_off_diagonal_overlap"], "1/5")

    def test_field_relations_and_conjugation(self):
        self.assertEqual(s.mul(s.A, s.A), s.scalar(2))
        self.assertEqual(s.mul(s.B, s.B), s.scalar(5))
        self.assertEqual(s.mul(s.T, s.T), s.neg(s.add(s.ONE, s.B)))
        self.assertEqual(s.mul(s.I, s.I), s.neg(s.ONE))
        self.assertEqual(s.conj(s.T), s.neg(s.T))
        self.assertEqual(s.conj(s.I), s.neg(s.I))
        self.assertEqual(s.conj(s.mul(s.T, s.I)), s.mul(s.T, s.I))
        self.assertEqual(s.mul(s.add(s.A, s.B), s.add(s.T, s.I)),
                         s.add(s.add(s.mul(s.A, s.T), s.mul(s.A, s.I)),
                               s.add(s.mul(s.B, s.T), s.mul(s.B, s.I))))

    def test_phase_tampering_rejected_even_when_unit_norm_preserved(self):
        u = s.add(s.scale(s.mul(s.sub(s.B, s.ONE), s.A), Fraction(1, 4)),
                  s.scale(s.T, Fraction(1, 2)))
        phases = s.phase_table(u)
        # This remains a unit phase, so the independent character check
        # alone cannot detect it. Idempotence/Hermiticity must reject.
        phases[0][1] = s.conj(phases[0][1])
        with self.assertRaises(AssertionError):
            s.verify(phases)

    def test_nonunit_tampering_rejected(self):
        u = s.add(s.scale(s.mul(s.sub(s.B, s.ONE), s.A), Fraction(1, 4)),
                  s.scale(s.T, Fraction(1, 2)))
        phases = s.phase_table(u)
        phases[1][1] = s.scalar(2)
        with self.assertRaises(AssertionError):
            s.verify(phases)

    def test_displacement_conventions(self):
        tau = s.scale(s.mul(s.add(s.ONE, s.I), s.A), Fraction(-1, 2))
        self.assertEqual(s.power(tau, 8), s.ONE)
        self.assertEqual(s.power(tau, 2), s.I)
        for a in range(4):
            for b in range(4):
                d = s.displacement(a, b, tau, s.I)
                self.assertEqual(s.matmul(d, s.adj(d)),
                                 [[s.ONE if i == j else s.ZERO for j in range(4)]
                                  for i in range(4)])


if __name__ == "__main__":
    unittest.main()
