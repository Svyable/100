"""Adversarial author-side tests for M097 multitheta formula."""
import sys
import unittest
from fractions import Fraction
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m097_multitheta as m


class MultithetaTests(unittest.TestCase):
    def test_all_small(self):
        self.assertGreater(len(m.all_small(max_vertices=10)), 15)

    def test_three_path_fractional(self):
        r = m.check_instance((3, 3, 3))
        self.assertEqual((r["lp"], r["tsp"], r["ratio"]), ("9", 10, "10/9"))

    def test_even_path_integral(self):
        self.assertEqual(m.check_instance((3, 3, 3, 3))["ratio"], "1")

    def test_five_path_fractional(self):
        r = m.check_instance((3, 3, 3, 3, 3))
        self.assertEqual((r["lp"], r["tsp"], r["ratio"]), ("15", 16, "16/15"))

    def test_length_two_degeneracy(self):
        for ls in ((2, 2), (2, 2, 2), (2, 2, 3, 3, 3), (2, 3, 3)):
            self.assertEqual(m.check_instance(ls)["ratio"], "1")

    def test_path_order_invariant(self):
        self.assertEqual(m.check_instance((3, 2, 4))["ratio"],
                         m.check_instance((4, 3, 2))["ratio"])

    def test_invalid_paths(self):
        for ls in ((), (2,), (1, 3), (2, 0, 3), (2, True), (2, 2.0)):
            with self.assertRaises(ValueError):
                m.build_graph(ls)

    def test_tamper_spoke(self):
        _, x = m.primal((3, 3, 3))
        e = next(e for e in x if 0 in e)
        x[e] += Fraction(1, 6)
        with self.assertRaises(AssertionError):
            m.check_primal((3, 3, 3), x)

    def test_tamper_shortcut(self):
        _, x = m.primal((3, 3, 3, 3))
        e = next(e for e in x if e not in m.build_graph((3, 3, 3, 3))[1])
        del x[e]
        with self.assertRaises(AssertionError):
            m.check_primal((3, 3, 3, 3), x)

    def test_wrong_parity(self):
        self.assertNotEqual(m.check_instance((3, 3, 3))["tsp"], 9)

    def test_more_than_five_paths(self):
        self.assertEqual(m.check_instance((2,) * 7)["ratio"], "1")
        self.assertEqual(m.check_instance((3,) * 6)["ratio"], "1")

    def test_simple_graph(self):
        for ls in ((2, 2), (2, 2, 2, 2), (3, 3, 3), (2, 4, 5)):
            n, edges, _, _ = m.build_graph(ls)
            self.assertEqual(len(edges), sum(ls))
            self.assertEqual(n, 2 + sum(x - 1 for x in ls))
            self.assertTrue(all(u != v for u, v in edges))


if __name__ == "__main__":
    unittest.main()
