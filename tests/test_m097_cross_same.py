"""Adversarial tests for the M097 same-hub cross-edge restricted candidate."""
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m097_cross_same as m


class CrossSameTests(unittest.TestCase):
    def test_ordered_exact_sweep(self):
        self.assertEqual(m.run(max_vertices=11, max_length=5, max_k=5)["instances"], 168)

    def test_three_path_half_exception(self):
        for L, lp, tsp in [
            ((3, 3, 2), "15/2", 8),
            ((3, 3, 3), "17/2", 9),
            ((4, 4, 2), "19/2", 10),
        ]:
            r = m.exact_check(L)
            self.assertEqual((r["lp"], r["tsp"]), (lp, tsp))

    def test_order_is_not_full_symmetry(self):
        self.assertEqual(m.predicted((3, 3, 2)), (Fraction(15, 2), 8))
        self.assertEqual(m.predicted((2, 3, 3)), (Fraction(7), 7))
        self.assertEqual(m.predicted((3, 2, 3)), (Fraction(7), 7))

    def test_five_path_sharp_ratio(self):
        self.assertEqual(m.predicted((3, 3, 3, 3, 3)), (Fraction(14), 15))
        self.assertEqual(m.exact_check((3, 3, 3, 3, 3))["min_cut"], "2")

    def test_even_path_integral(self):
        for L in ((3, 3, 3, 3), (3, 3, 2, 3), (2, 2, 2, 2, 2, 2)):
            lp, tsp = m.predicted(L)
            self.assertEqual(lp, tsp)
            self.assertEqual(m.exact_check(L)["tsp"], tsp)

    def test_odd_uncrossed_short_requires_other_connection(self):
        self.assertEqual(m.predicted((3, 3, 2)), (Fraction(15, 2), 8))
        self.assertEqual(m.predicted((3, 3, 2, 3, 3)), (Fraction(13), 13))
        self.assertEqual(m.exact_check((3, 3, 2, 3, 3))["tsp"], 13)

    def test_long_path_boundary(self):
        for L in ((3, 6, 2), (3, 3, 2, 2, 3), (2, 6, 4, 3)):
            self.assertEqual(m.exact_check(L)["min_cut"], "2")

    def test_invalid_lengths(self):
        for L in ((), (2,), (2, 2), (2, 1, 3), (2, 0, 3),
                  (2, True, 3), (2, 2.0, 3), (2, "2", 3)):
            with self.assertRaises(ValueError):
                m.instance(L)

    def test_degree_tamper_detected(self):
        L = (3, 3, 3)
        n, paths, _ = m.instance(L)
        x = m.candidate_lp(L)
        m.add(x, 0, paths[0][1], Fraction(1, 3))
        self.assertNotEqual(
            sum((w for (a, b), w in x.items() if 0 in (a, b)), Fraction(0)),
            2,
        )

    def test_disconnected_two_factor_is_not_subtour_feasible(self):
        # All degree equations hold, but the separating cut has zero mass.
        n, _, _ = m.instance((3, 3, 3))
        self.assertEqual(n, 8)
        x = {}
        for cycle in ((0, 1, 2, 3), (4, 5, 6, 7)):
            for i in range(4):
                m.add(x, cycle[i], cycle[(i + 1) % 4], 1)
        self.assertTrue(all(
            sum((w for (a, b), w in x.items() if v in (a, b)), Fraction(0)) == 2
            for v in range(n)
        ))
        self.assertEqual(sum((w for (a, b), w in x.items()
                              if (a in (0, 1, 2, 3)) != (b in (0, 1, 2, 3))),
                             Fraction(0)), 0)

    def test_eulerian_witness_tamper(self):
        n, _, _ = m.instance((3, 3, 3, 3))
        e = m.eulerian_witness((3, 3, 3, 3))
        e.pop(next(iter(e)))
        with self.assertRaises(AssertionError):
            m.shortcut_euler(n, e)


if __name__ == "__main__":
    unittest.main()
