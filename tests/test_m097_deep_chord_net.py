import itertools
import unittest
from fractions import Fraction

from scripts import m097_deep_chord_net as net


class DeepChordNetworkTests(unittest.TestCase):
    def test_all_fixed_exact(self):
        for lengths, chords in net.fixed_cases():
            with self.subTest(lengths=lengths, chords=chords):
                r = net.check(lengths, chords, tours=12)
                self.assertEqual(r["sep"], sum(lengths))

    def test_seeded_sweep(self):
        cases = list(net.random_cases())
        self.assertEqual(len(cases), 49)
        for lengths, chords in cases:
            net.check(lengths, chords, tours=1)

    def test_sharp_multi_chord_triangle(self):
        lengths, chords = net.fixed_cases()[1]
        r = net.check(lengths, chords)
        self.assertEqual((r["chords"], r["sep"], r["tsp"]), (3, 12, 13))
        self.assertEqual(Fraction(r["tsp"], r["sep"]), Fraction(13, 12))

    def test_same_path_chord_is_allowed(self):
        lengths, chords = net.fixed_cases()[4]
        r = net.check(lengths, chords)
        self.assertEqual((r["sep"], r["tsp"]), (13, 14))

    def test_reject_shallow_endpoint(self):
        with self.assertRaisesRegex(ValueError, "near a hub"):
            net.make_graph((4, 4, 3), [((0, 2), (1, 3))])

    def test_reject_close_marks(self):
        with self.assertRaisesRegex(ValueError, "too close"):
            net.make_graph((5, 4, 3),
                           [((0, 2), (1, 2)), ((0, 3), (2, 2))])

    def test_reject_duplicate_chord(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            net.make_graph((4, 4, 4),
                           [((0, 2), (1, 2)), ((0, 2), (1, 2))])

    def test_corrupt_primal_detected(self):
        paths, edges, n = net.make_graph((4, 4, 4),
                                        [((0, 2), (1, 2)), ((1, 2), (2, 2))])
        x = net.primal(paths)
        x[(0, 1)] = Fraction(1, 3)
        self.assertNotEqual(sum(w for (a, b), w in x.items() if 0 in (a, b)), 2)

    def test_shallow_falsifies_unrestricted_formula(self):
        # No claim that this graph meets the separation hypothesis.
        paths, edges, n = net.make_graph((4, 4, 3), [])
        edges.add(tuple(sorted((paths[0][2], paths[1][3]))))
        d = net.distances(n, edges)
        self.assertEqual(net.tour_dp(d), 11)
        self.assertLess(11, sum((4, 4, 3)) + 1)

    def test_independent_brute_tour_semantics(self):
        paths, edges, n = net.make_graph((3, 3, 2), [])
        d = net.distances(n, edges)
        literal = min(sum(d[p[i]][p[(i+1) % n]] for i in range(n))
                      for rest in itertools.permutations(range(1, n))
                      for p in [(0,) + rest])
        self.assertEqual(net.tour_dp(d), literal)


if __name__ == "__main__":
    unittest.main()
