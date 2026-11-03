"""Adversarial exact checks for M097 block-sum restricted proof candidate."""
import itertools
import random
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m097_block_sum as m


class BlockSumTests(unittest.TestCase):
    def test_bridge_two_vertex_convention(self):
        self.assertEqual(m.check_instance(m.block("bridge", ()))["lp"], "2")

    def test_cycle_triangle(self):
        self.assertEqual(m.check_instance(m.block("cycle", (3,)))["tsp"], 3)

    def test_theta_odd_gap(self):
        self.assertEqual(m.check_instance(m.block("theta", (3, 3, 3)))["ratio"], "10/9")

    def test_even_theta_integral(self):
        self.assertEqual(m.check_instance(m.block("theta", (2, 3, 2, 3)))["ratio"], "1")

    def test_hub_glue(self):
        g = m.glue(m.block("theta", (3, 3, 3)), m.block("bridge", ()), 0, 0)
        self.assertEqual(m.check_instance(g)["ratio"], "12/11")

    def test_internal_glue(self):
        g = m.glue(m.block("theta", (3, 3, 3)), m.block("cycle", (3,)), 2, 0)
        self.assertEqual(m.check_instance(g)["ratio"], "13/12")

    def test_two_odd_blocks(self):
        g = m.glue(m.block("theta", (3, 3, 3)), m.block("theta", (3, 3, 3)), 2, 0)
        self.assertEqual(m.check_instance(g)["ratio"], "10/9")

    def test_all_cuts_dual_cover(self):
        for name, g in m.fixtures():
            with self.subTest(name=name):
                self.assertEqual(m.dual_cut_cover(g)[0], sum(b["lp"] for b in g.blocks))

    def test_primal_tamper(self):
        g = m.block("cycle", (4,))
        g.x[(0, 1)] += Q(1, 5)
        with self.assertRaises(AssertionError):
            m.check_primal(g)

    def test_dual_tamper(self):
        g = m.block("cycle", (4,))
        g.edges.remove((0, 1))
        with self.assertRaises(AssertionError):
            m.dual_cut_cover(g)

    def test_invalid_blocks(self):
        for kind, lengths in (("theta", (2,)), ("theta", (1, 3)),
                              ("cycle", (2,)), ("bogus", ())):
            with self.subTest(kind=kind, lengths=lengths):
                with self.assertRaises(ValueError):
                    m.block(kind, lengths)

    def test_invalid_articulation(self):
        with self.assertRaises(ValueError):
            m.glue(m.block("cycle", (3,)), m.block("bridge", ()), 9, 0)

    def test_bruteforce_tours(self):
        g = m.glue(m.block("cycle", (3,)), m.block("cycle", (4,)), 1, 0)
        d = m.metric(g)
        brute = min(sum(d[p[i]][p[(i+1) % len(p)]] for i in range(len(p)))
                    for p in ((0,) + q for q in itertools.permutations(range(1, g.n))))
        self.assertEqual(brute, m.tsp_independent(d))
        self.assertEqual(brute, sum(b["tsp"] for b in g.blocks))

    def test_seeded_random_block_trees(self):
        rng = random.Random(189)
        for trial in range(40):
            g = m.block("cycle", (rng.choice([3, 4]),))
            for _ in range(rng.randint(1, 3)):
                h = (m.block("bridge", ()) if rng.randrange(2) == 0
                     else m.block("cycle", (3,)))
                g = m.glue(g, h, rng.randrange(g.n), rng.randrange(h.n))
            with self.subTest(trial=trial):
                m.check_instance(g)

    def test_two_vertex_overlap_breaks_additivity(self):
        # Two triangles share an EDGE, not just an articulation vertex.
        # Their naive block sum is 3+3=6, but the diamond has a 4-tour.
        g = m.Graph(4, {(0, 1), (1, 2), (0, 2), (0, 3), (1, 3)}, {}, [])
        self.assertEqual(m.tsp_independent(m.metric(g)), 4)
        self.assertNotEqual(m.tsp_independent(m.metric(g)), 6)

    def test_no_four_thirds_violation(self):
        for name, g in m.fixtures():
            with self.subTest(name=name):
                r = m.check_instance(g)["ratio"]
                self.assertLess(Q(r), Q(4, 3))


if __name__ == "__main__":
    unittest.main()
