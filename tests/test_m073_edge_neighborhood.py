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
        self.assertEqual(sample["uniform_exponent"], "174031/17799")
        self.assertTrue(sample["uniform_two_square_plus_full_spectrum_below_one"])
        self.assertTrue(sample["weighted_two_square_plus_full_spectrum_above_one"])
        self.assertTrue(sample["density_paths_agree"])

    def test_surface_link_structural_lemma_on_two_other_spheres(self):
        # Octahedron: six degree-four points, eight faces, all B.
        octa = [tuple(sorted((pole, 2+i, 2+(i+1) % 4)))
                for pole in (0, 1) for i in range(4)]
        # Icosahedron: twelve degree-five points, twenty faces, all A.
        ico = []
        for i in range(5):
            a, b = 1+i, 1+(i+1) % 5
            c, d = 6+i, 6+(i+1) % 5
            ico.extend(((0, a, b), (11, c, d), (a, b, c), (b, c, d)))
        for faces, n, expected, degrees in (
                (octa, 6, {"A": 0, "B": 24}, {4: 6}),
                (ico, 12, {"A": 60, "B": 0}, {5: 12})):
            with self.subTest(points=n):
                classes, hist = target.surface_link_certificate(faces, n)
                self.assertEqual(classes, expected)
                self.assertEqual(hist, degrees)
                # Independently build both square-completion faces at every root.
                for fi, f in enumerate(faces):
                    for i in f:
                        j, k = sorted(set(f) - {i})
                        g = [next(t for t, tri in enumerate(faces)
                                  if t != fi and set(pair) <= set(tri))
                             for pair in ((i, j), (i, k), (j, k))]
                        x = [next(v for v in faces[t] if v not in f) for t in g]
                        h = [next(t for t, tri in enumerate(faces)
                                  if t != g0 and {v, p} <= set(tri))
                             for v, p, g0 in zip((i, i, j), x, g)]
                        self.assertNotEqual(h[0], h[2])
                        kind = "A" if h[0] != h[1] else "B"
                        self.assertEqual(kind, "B" if n == 6 else "A")
                        z = 1 if kind == "A" else 2
                        vertices = (i, n+fi, j, k, n+g[0], n+g[1],
                                    n+g[2], x[0], n+h[0], x[z], n+h[z])
                        self.assertEqual(len(set(vertices)), 11)

    def test_nonmanifold_or_low_degree_surface_rejected(self):
        octa = [tuple(sorted((pole, 2+i, 2+(i+1) % 4)))
                for pole in (0, 1) for i in range(4)]
        with self.assertRaises(ValueError):
            target.surface_link_certificate(octa[:-1], 6)
        # Boundary of tetrahedron has degree three: squares collide.
        tetra = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
        with self.assertRaises(ValueError):
            target.surface_link_certificate(tetra, 4)

    def test_bad_q_rejected(self):
        for q in (Q(-1, 10), Q(1), Q(11, 10)):
            with self.assertRaises(ValueError):
                target.spin_correlation(target.EDGES_A, q)


if __name__ == "__main__":
    unittest.main()
