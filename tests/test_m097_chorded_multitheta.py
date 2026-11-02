import unittest
from fractions import Fraction
from scripts.m097_chorded_multitheta import build, distances, lp_point, check_lp, formula, tour_dp, run


class ChordedMultithetaTest(unittest.TestCase):
    def test_boundary(self):
        for lengths, expected in [((2, 2), (4, 4)), ((2, 2, 2), (6, 6)), ((3, 3, 3), (9, 10)), ((4, 4, 4), (12, 13)), ((3, 4, 5, 6), (18, 18)), ((2, 3, 3), (8, 8))]:
            self.assertEqual(formula(lengths), expected)
            n, e, p = build(lengths)
            self.assertEqual(tour_dp(distances(n, e)), expected[1])
            self.assertEqual(check_lp(lengths), expected[0])

    def test_bad_lengths(self):
        for lengths in [(), (2,), (1, 2), (2, 0)]:
            with self.assertRaises(ValueError):
                build(lengths)

    def test_hub_chord_present(self):
        n, e, p = build((3, 3, 3))
        self.assertIn((0, 1), e)
        self.assertEqual(len(e), 10)

    def test_tamper_degree(self):
        n, e, p = build((3, 3, 3))
        x = lp_point((3, 3, 3), p)
        x[(0, p[0][1])] += Fraction(1, 10)
        self.assertNotEqual(sum(w for (a, b), w in x.items() if a == 0 or b == 0), 2)

    def test_naive_extension_false(self):
        self.assertEqual(check_lp((3, 3, 3)), 9)
        self.assertNotEqual(check_lp((3, 3, 3)), 10)

    def test_direct_edge_not_integralizer(self):
        self.assertEqual(formula((3, 3, 3)), (9, 10))

    def test_sweep(self):
        self.assertEqual(run(10)['checked'], 50)


if __name__ == '__main__':
    unittest.main()
