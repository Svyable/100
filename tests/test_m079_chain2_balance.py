"""Adversarial checks for the M079 chain-plus-two sharp balance candidate."""
import itertools
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m079_chain2_balance as target


def brute_counts(ix, iy):
    """Third route: enumerate permutations and check every cover constraint."""
    m = max(ix[1], iy[1])
    n = m + 2
    x, y = m, m + 1
    orders = []
    for order in itertools.permutations(range(n)):
        pos = {v: order.index(v) for v in range(n)}
        if any(pos[k] > pos[k + 1] for k in range(m - 1)):
            continue
        good = True
        for v, (a, b) in ((x, ix), (y, iy)):
            if a and not pos[a - 1] < pos[v]:
                good = False
            if b < m and not pos[v] < pos[b]:
                good = False
        if good:
            orders.append(pos)
    counts = {}
    for name in target.probabilities(ix, iy)[1]:
        u, v = target.pair_indices(name, m)
        counts[name] = Fraction(sum(p[u] < p[v] for p in orders), len(orders))
    return len(orders), counts


class ChainPlusTwoTests(unittest.TestCase):
    def test_exact_residual_exhaustion(self):
        self.assertEqual(target.verify_residual(), 27)

    def test_large_interval_symbolic_boundary(self):
        target.verify_large_atom_inequality()
        self.assertEqual(Fraction(3, 12), Fraction(1, 4))
        self.assertLess(Fraction(1, 4), Fraction(3, 11))

    def test_sharp_five_element_width_three_case(self):
        ix, iy = (1, 3), (0, 2)
        n, probs = target.probabilities(ix, iy)
        self.assertEqual(n, 11)
        self.assertEqual(target.balance(probs), Fraction(4, 11))
        self.assertEqual(probs["x,c2"], Fraction(4, 11))

    def test_4_over_11_is_sharp_not_5_over_11(self):
        _, probs = target.probabilities((1, 3), (0, 2))
        self.assertLess(target.balance(probs), Fraction(5, 11))

    def test_brute_permutations_independent_of_dp(self):
        for lx in range(2, 5):
            for ly in range(2, 5):
                for delta in range(-(ly - 1), lx):
                    ix, iy = target.canonical_intervals(lx, ly, delta)
                    if target.overlap(ix, iy) < 2:
                        continue
                    n, closed = target.probabilities(ix, iy)
                    brute_n, brute_p = brute_counts(ix, iy)
                    self.assertEqual(n, brute_n, (lx, ly, delta))
                    self.assertEqual(closed, brute_p, (lx, ly, delta))

    def test_all_table_entries_are_distinct(self):
        self.assertEqual(len(target.ROWS), len({row[:3] for row in target.ROWS}))

    def test_random_adversarial_dp(self):
        self.assertGreater(target.verify_random(trials=320), 150)

    def test_non_width_three_overlap_one_is_rejected(self):
        ix, iy = target.canonical_intervals(2, 2, 1)
        self.assertEqual(target.overlap(ix, iy), 1)
        self.assertRaises(ValueError, target.probabilities, (0, 1), (3, 4))

    def test_invalid_intervals_fail_closed(self):
        for ix, iy in (((2, 1), (0, 2)), ((-1, 1), (0, 2))):
            with self.assertRaises(ValueError):
                target.probabilities(ix, iy)

    def test_same_gap_multiplicity_mutation_detected(self):
        ix, iy = (1, 3), (0, 2)
        n, _ = target.probabilities(ix, iy)
        self.assertEqual(n, 11)
        self.assertNotEqual(n, 3 * 3)

    def test_extremizer_has_an_induced_n_and_width_three(self):
        # Five-element extremizer: c1<c2<c3, c1<x, y<c3.
        ix, iy = (1, 3), (0, 2)
        self.assertEqual(target.overlap(ix, iy), 2)
        m = 3
        vertices = {"y": m + 1, "c1": 0, "c3": 2, "x": m}
        forced = set()
        for a, b in itertools.permutations(vertices, 2):
            u, v = vertices[a], vertices[b]
            if target.order_ideal_count(ix, iy, (v, u)) == 0:
                forced.add((a, b))
        self.assertEqual(forced, {("y", "c3"), ("c1", "c3"), ("c1", "x")})
        # x, y and c2 are pairwise incomparable: a genuine width-three case.
        for u, v in ((m, m + 1), (m, 1), (m + 1, 1)):
            self.assertGreater(target.order_ideal_count(ix, iy, (u, v)), 0)
            self.assertGreater(target.order_ideal_count(ix, iy, (v, u)), 0)



if __name__ == "__main__":
    unittest.main()
