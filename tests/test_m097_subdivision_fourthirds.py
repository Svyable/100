import importlib.util
from fractions import Fraction as Q
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1] / 'scripts'


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, BASE / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


b = load('subdivision_fourthirds', 'm097_subdivision_fourthirds.py')
core = load('subdivision_core', 'm097_subdivision_core.py')


class SharpSubdividedFourThirds(unittest.TestCase):
    def test_full_falsifier_and_negative_controls(self):
        result = b.falsifier_sweep()
        self.assertGreaterEqual(result['checked_instances'], 2000)
        self.assertEqual(result['negative_controls'], 2)

    def test_bridge_eulerian_class_has_exact_lp(self):
        for data in [(2, [(0, 1)], [17]),
                     (3, [(0, 1), (0, 1), (0, 2)], [2, 13, 5]),
                     (3, [(0, 1), (0, 1), (0, 2)], [9, 11, 10])]:
            r = b.check_instance(*data)
            self.assertTrue(r['even_bridgeless_core'])
            self.assertEqual(r['TSP'], r['SEP'])

    def test_non_eulerian_can_still_have_lp_exact_at_length_two(self):
        r = b.check_instance(2, [(0, 1)] * 3, [2, 7, 8])
        self.assertFalse(r['even_bridgeless_core'])
        self.assertTrue(r['LP_exact'])
        self.assertEqual((r['TSP'], r['SEP']), (17, 17))
        r = b.check_instance(2, [(0, 1)] * 3, [3, 7, 8])
        self.assertFalse(r['LP_exact'])
        self.assertEqual((r['TSP'], r['SEP']), (19, 18))

    def test_theta_sharp_additive_constant(self):
        for L in (2, 3, 7, 20):
            row = b.check_instance(2, [(0, 1)] * 3, [L] * 3)
            self.assertEqual(row['TSP'], Q(4 * row['M'], 3) - 2)
            self.assertEqual(row['SEP'], 3 * L)

    def test_pendant_bridge_sharp_additive_constant(self):
        for L in (2, 3, 11):
            for K in (2, 5, 17):
                row = b.check_instance(3, [(0, 1)] * 3 + [(0, 2)],
                                       [L] * 3 + [K])
                self.assertEqual(row['TSP'],
                                 Q(4 * row['M'] + 2 * row['B'], 3) - 2)

    def test_odd_cut_mutant_caught(self):
        self.assertFalse(b.fractional_odd_cut_check(
            3, [(0, 1), (1, 2)], frozenset(),
            override=[Q(1, 3), Q(1, 3)]))
        self.assertTrue(b.fractional_odd_cut_check(
            3, [(0, 1), (1, 2)], frozenset({0, 1})))

    def test_cross_check_old_parity_engine(self):
        instances = [(2, [(0, 1)] * 3, [4, 2, 8]),
                     (3, [(0, 1), (1, 2), (0, 2)], [2, 4, 3]),
                     (4, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)],
                      [3, 2, 4, 2, 5]),
                     (4, [(0, 1), (1, 2), (2, 3)], [4, 5, 7]),
                     (4, [(0, 1), (0, 1), (1, 2), (2, 3), (3, 0)],
                      [2, 4, 2, 4, 3])]
        for n, edges, lengths in instances:
            with self.subTest(edges=edges, lengths=lengths):
                row = b.check_instance(n, edges, lengths)
                self.assertEqual(row['TSP'],
                                 core.optimum(n, edges, lengths)[0])
                self.assertEqual(row['SEP'], sum(lengths) +
                                 sum(lengths[i] for i in b.bridge_indices(n, edges)))

    def test_length_one_rejected(self):
        with self.assertRaises(AssertionError):
            b.check_instance(2, [(0, 1)], [1])


if __name__ == '__main__':
    unittest.main()
