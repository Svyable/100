"""Adversarial exact checks for the seven-vertex M073 rung-correlation proof."""
import sys
import unittest
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m073_rung_correlation as target
from m073_assortative2 import load_faces

Q = Fraction


class RungCorrelationTests(unittest.TestCase):
    def test_all_sixty_six_incidence_motifs(self):
        witnesses = target.motifs(load_faces())
        self.assertEqual(len(witnesses), 66)
        self.assertEqual(len({(p, f) for p, f, _ in witnesses}), 66)
        self.assertTrue(all(len(set(alt)) == 3 for _, _, alt in witnesses))

    def test_independent_pair_multiplicity(self):
        faces = load_faces()
        pairs = Counter(tuple(sorted((f[i], f[j])))
                        for f in faces for i in range(3) for j in range(i + 1, 3))
        self.assertEqual(len(pairs), 33)
        self.assertEqual(set(pairs.values()), {2})

    def test_source_incidence_mutation_fails(self):
        faces = list(load_faces())
        faces[0] = (0, 1, 4)
        with self.assertRaises(ValueError):
            target.motifs(faces)

    def test_exact_even_subset_polynomials(self):
        self.assertEqual(target.boundary_polynomial(), {0: 1, 4: 3, 6: 4})
        self.assertEqual(target.boundary_polynomial((0, 1)),
                         {1: 1, 3: 2, 5: 3, 7: 2})
        self.assertEqual(sum(target.boundary_polynomial().values()), 8)

    def test_direct_spins_independently_match_polynomials(self):
        for q in (Q(0), Q(1, 10), Q(1, 3), Q(1, 2), Q(9, 10)):
            with self.subTest(q=q):
                self.assertEqual(
                    target.direct_correlation(q),
                    target.evaluate(target.NUMERATOR, q) /
                    target.evaluate(target.DENOMINATOR, q))

    def test_rung_edge_removal_erases_gain(self):
        # A one-edge pendant connector cannot improve endpoint correlation.
        edges = target.RUNG_EDGES[:-1]
        self.assertEqual(target.boundary_polynomial(edges=edges),
                         target.OLD_DENOMINATOR)
        self.assertEqual(target.boundary_polynomial((0, 1), edges),
                         target.OLD_NUMERATOR)

    def test_improvement_polynomial_identity(self):
        difference = target.subtract(
            target.multiply(target.NUMERATOR, target.OLD_DENOMINATOR),
            target.multiply(target.OLD_NUMERATOR, target.DENOMINATOR))
        self.assertEqual(difference, target.expected_difference())
        for q in (Q(1, 100), Q(1, 3), Q(9, 10)):
            self.assertGreater(target.evaluate(difference, q), 0)

    def test_exact_new_only_rational_host(self):
        result = target.sample()
        self.assertEqual(result["weights"], ["241/400", "1", "159/400"])
        self.assertEqual(result["old_kappa"], "223/561")
        self.assertEqual(result["new_kappa"], "23/57")
        self.assertEqual(result["new_exponent"], "187/19")
        self.assertTrue(result["old_bound_below_one"])
        self.assertTrue(result["new_bound_above_one"])
        self.assertTrue(result["exact_density_paths_agree"])

    def test_exact_integer_threshold_separation(self):
        R, A = Q(38319, 40000), Q(1114, 729)
        self.assertLess(R**169 * A**17, 1)
        self.assertGreater(R**187 * A**19, 1)

    def test_invalid_correlation_parameters(self):
        for q in (Q(-1, 10), Q(1), Q(3, 2)):
            with self.assertRaises(ValueError):
                target.direct_correlation(q)


if __name__ == "__main__":
    unittest.main()
