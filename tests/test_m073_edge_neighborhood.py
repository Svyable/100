"""Adversarial checks of the source-pinned two-square Ising correlation theorem."""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m073_edge_neighborhood as target
from m073_assortative2 import load_faces

Q = Fraction


class EdgeNeighborhoodTests(unittest.TestCase):
    def test_all_source_incidences_and_independent_census(self):
        faces = load_faces()
        found = target.source_motifs(faces)
        self.assertEqual(len(found), 66)
        self.assertEqual(len({(f, i) for f, i, _, _ in found}), 66)
        self.assertEqual(Counter(kind for _, _, kind, _ in found),
                         {"A": 54, "B": 12})
        self.assertEqual(target.independent_source_counts(faces),
                         {"A": 54, "B": 12})
        self.assertTrue(all(len(set(vertices)) == 11 for _, _, _, vertices in found))

    def test_mutated_source_is_rejected(self):
        faces = list(load_faces())
        faces[0] = (0, 1, 4)
        with self.assertRaises(ValueError):
            target.source_motifs(faces)
        with self.assertRaises(ValueError):
            target.independent_source_counts(faces)

    def test_malformed_source_is_rejected(self):
        faces = list(load_faces())
        faces[0] = (0, 0, 1)
        with self.assertRaises(ValueError):
            target.source_motifs(faces)
        with self.assertRaises(ValueError):
            target.source_motifs(faces[:-1])

    def test_exact_high_temperature_polynomials(self):
        for edges, numerator in ((target.EDGES_A, target.NUM_A),
                                 (target.EDGES_B, target.NUM_B)):
            self.assertEqual(target.boundary_polynomial(edges), target.DEN)
            self.assertEqual(target.boundary_polynomial(edges, (0, 1)), numerator)
            self.assertEqual(sum(target.DEN.values()), 32)

    def test_independent_full_spin_sum(self):
        for edges, numerator in ((target.EDGES_A, target.NUM_A),
                                 (target.EDGES_B, target.NUM_B)):
            for q in (Q(0), Q(1, 10), Q(1, 3), Q(1, 2), Q(9, 10)):
                with self.subTest(edges=edges, q=q):
                    self.assertEqual(target.spin_correlation(edges, q),
                                     target.evaluate(numerator, q) /
                                     target.evaluate(target.DEN, q))

    def test_strict_uniform_gain_polynomial(self):
        difference = target.poly_sub(
            target.poly_mul(target.NUM_B, target.RUNG_DEN),
            target.poly_mul(target.RUNG_NUM, target.DEN))
        self.assertEqual(difference, target.improvement_polynomial())
        for q in (Q(1, 100), Q(1, 3), Q(9, 10)):
            self.assertGreater(target.evaluate(difference, q), 0)

    def test_strict_A_over_B_polynomial(self):
        self.assertEqual(target.poly_sub(target.NUM_A, target.NUM_B),
                         {5: 1, 7: -3, 9: 3, 11: -1})
        for q in (Q(1, 100), Q(1, 3), Q(9, 10)):
            self.assertGreater(target.evaluate(target.NUM_A, q),
                               target.evaluate(target.NUM_B, q))

    def test_cut_square_edge_erases_its_gain(self):
        # A two-edge pendant path contributes no spin correlation.
        one_square = target.RUNG + target.FIRST_SQUARE
        with_broken_second = one_square + target.SECOND_A[:-1]
        for odd in ((), (0, 1)):
            self.assertEqual(target.boundary_polynomial(one_square, odd),
                             target.boundary_polynomial(with_broken_second, odd))
        # Breaking both squares reduces exactly to the rung.
        broken_both = target.RUNG + target.FIRST_SQUARE[:-1] + target.SECOND_A[:-1]
        self.assertEqual(target.boundary_polynomial(broken_both), target.RUNG_DEN)
        self.assertEqual(target.boundary_polynomial(broken_both, (0, 1)),
                         target.RUNG_NUM)

    def test_full_spectrum_comparison_not_just_cycle_truncation(self):
        sample = target.source_sample(load_faces())
        self.assertEqual(sample["full_even_subgraph_coefficients"], 23)
        self.assertEqual(sample["weights"],
                         ["12443/20000", "1", "7557/20000"])
        self.assertTrue(sample["rung_plus_full_spectrum_below_one"])
        self.assertTrue(sample["two_square_plus_full_spectrum_above_one"])
        self.assertTrue(sample["density_paths_agree"])

    def test_bad_q_rejected(self):
        for q in (Q(-1, 10), Q(1), Q(11, 10)):
            with self.assertRaises(ValueError):
                target.spin_correlation(target.EDGES_A, q)


if __name__ == "__main__":
    unittest.main()
