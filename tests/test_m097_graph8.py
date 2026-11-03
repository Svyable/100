"""Adversarial stdlib-only tests for the M097 eight-vertex graph-metric certificate."""
import itertools
import unittest
from fractions import Fraction
from scripts import m097_graph8 as m


class M097Graph8Tests(unittest.TestCase):
    def test_cut_representatives_and_tours(self):
        self.assertEqual(len(m.CUTS), 119)
        self.assertEqual(len(list(m.all_tours())), 2520)
        self.assertEqual(len(m.EDGES), 28)

    def test_graph6_decoder(self):
        self.assertEqual(len(m.graph6_edges("G~~~~{")), 28)
        self.assertEqual(m.graph_distances("G~~~~{"), (1,) * 28)
        with self.assertRaises(ValueError):
            m.graph6_edges("G~~~~~")  # nonzero padding
        with self.assertRaises(ValueError):
            m.graph6_edges("Gxxxx")  # invalid length

    def test_both_maximizers(self):
        self.assertTrue(m.check_winners())
        for g6 in m.EXPECTED["max_graph6"]:
            self.assertEqual(max(m.graph_distances(g6)), 3)
            self.assertEqual(m.independent_tsp(m.graph_distances(g6)), 10)

    def test_independent_bruteforce_tour_control(self):
        cost = m.graph_distances(m.EXPECTED["max_graph6"][0])
        brute = min(sum(cost[j] for j in tour) for tour in m.all_tours())
        self.assertEqual(brute, m.independent_tsp(cost))
        self.assertEqual(brute, 10)

    def test_primal_tamper_rejected(self):
        cost = m.graph_distances(m.EXPECTED["max_graph6"][0])
        primal = m.dense(m.WINNER_PRIMAL, 28)
        primal[0] = Fraction(0)
        with self.assertRaises(ValueError):
            m.check_lp(cost, primal, m.dense(m.WINNER_DEGREE_DUAL, 8),
                       m.dense(m.WINNER_CUT_DUAL, 119))

    def test_dual_tamper_rejected(self):
        cost = m.graph_distances(m.EXPECTED["max_graph6"][0])
        dual = m.dense(m.WINNER_DEGREE_DUAL, 8)
        dual[1] += Fraction(1, 2)
        with self.assertRaises(ValueError):
            m.check_lp(cost, m.dense(m.WINNER_PRIMAL, 28), dual,
                       m.dense(m.WINNER_CUT_DUAL, 119))

    def test_missing_cut_dual_rejected(self):
        cost = m.graph_distances(m.EXPECTED["max_graph6"][0])
        with self.assertRaises(ValueError):
            m.check_lp(cost, m.dense(m.WINNER_PRIMAL, 28),
                       m.dense(m.WINNER_DEGREE_DUAL, 8), [0] * 119)

    def test_disconnected_graph_rejected(self):
        # Empty eight-vertex graph: graph6 'G' + 5 zero-encoding chars.
        with self.assertRaises(ValueError):
            m.graph_distances("G?????")

    def test_graph_metric_not_one_two_control(self):
        for g6 in m.EXPECTED["max_graph6"]:
            cost = m.graph_distances(g6)
            self.assertEqual(max(cost), 3)
            self.assertNotEqual(cost, tuple(min(2, v) for v in cost))

    def test_digest_and_distribution_contract(self):
        self.assertEqual(sum(m.EXPECTED["ratio_histogram"].values()), 11117)
        self.assertEqual(m.EXPECTED["ratio_histogram"]["10/9"], 2)
        self.assertEqual(len(m.EXPECTED["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
