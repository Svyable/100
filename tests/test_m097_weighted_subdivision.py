"""Adversarial tests for weighted subdivision parity/MST theorem and LP clone limit."""
import sys
import unittest
from fractions import Fraction
from itertools import permutations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m097_weighted_subdivision as w


class WeightedSubdivisionTests(unittest.TestCase):
    def compare(self, n, paths, expected=None):
        result = w.exact_core_tsp(n, paths)
        self.assertEqual(w.certificate(n, paths, result)["weight"], result["cost"])
        self.assertEqual(w.full_metric_tsp(n, paths), result["cost"])
        if expected is not None:
            self.assertEqual(result["cost"], Fraction(expected))
        return result

    def test_arbitrary_positive_rationals_and_parallel_edges(self):
        p = [(0, 1, (Fraction(1, 3), Fraction(5, 2))),
             (0, 1, (9, 2, 1)),
             (0, 1, (2, Fraction(7, 3)))]
        self.compare(2, p)
        self.assertEqual(w.exact_core_tsp(2, p)["core_states"], 4)

    def test_fully_weighted_tree_doubles_every_edge(self):
        p = [(0, 1, (5, 1, 9)), (1, 2, (8, 2)),
             (1, 3, (Fraction(1, 2), Fraction(5, 3)))]
        expected = 2 * sum(sum(Fraction(x) for x in q[2]) for q in p)
        self.compare(4, p, expected)

    def test_cycle_exact_closed_form_and_large_edge_omission(self):
        p = [(0, 1, (1, 2)), (1, 2, (7, 1)), (2, 0, (100, 1))]
        W = sum(sum(a[2]) for a in p)
        self.compare(3, p, min(W, 2 * (W - 100)))
        # Unweighted expression W + sum(L-2) would not capture this.
        self.assertNotEqual(w.exact_core_tsp(3, p)["cost"], 6)

    def test_path_internal_order_does_not_affect_exact_cost(self):
        a = [(0, 1, (1, 9, 2)), (0, 1, (3, 4, 6)),
             (0, 1, (Fraction(1, 2), Fraction(5, 2)))]
        b = [(0, 1, (9, 3)), (0, 1, (6, 3, 4)), (0, 1, (Fraction(5, 2), Fraction(1, 2)))]
        self.assertEqual([(sum(q[2]), max(q[2])) for q in a],
                         [(sum(q[2]), max(q[2])) for q in b])
        self.assertEqual(self.compare(2, a)["cost"], self.compare(2, b)["cost"])

    def test_articulation_with_two_cycles_and_bridges(self):
        p = [(0, 1, (2, 1)), (1, 2, (3, 2)), (2, 0, (1, 3)),
             (2, 3, (1, 4)), (3, 4, (2, 1)), (4, 2, (2, 5)),
             (3, 5, (1, 7))]
        result = w.exact_core_tsp(6, p)
        cert = w.certificate(6, p, result)
        self.assertEqual(cert["weight"], result["cost"])
        self.assertEqual(cert["distinct_vertices"], 6 + len(p))

    def test_bridge_or_duplicate_weight_key_does_not_break_connectivity(self):
        p = [(0, 1, (2, 2)), (0, 1, (2, 2)), (1, 2, (2, 2))]
        self.compare(3, p)

    def test_corrupted_construction_certificate_is_rejected(self):
        p = [(0, 1, (1, 3)), (0, 1, (2, 5))]
        good = w.exact_core_tsp(2, p)
        bad = dict(good, cost=good["cost"] + 1)
        with self.assertRaises(AssertionError):
            w.certificate(2, p, bad)
        bad2 = dict(good, through=())
        # The missing connectivity must be caught unless this is already the optimum.
        if good["through"]:
            with self.assertRaises(AssertionError):
                w.certificate(2, p, bad2)

    def test_full_hamiltonian_permutations_independent_of_dp(self):
        p = [(0, 1, (1, 7)), (0, 1, (3, 2)), (0, 1, (4, 1))]
        N, edges, _ = w.expand(2, p)
        d = w.metric_closure(N, edges)
        literal = min(
            sum(d[tour[i]][tour[(i + 1) % N]] for i in range(N))
            for tail in permutations(range(1, N))
            for tour in [(0,) + tail
            ]
        )
        self.assertEqual(literal, w.hamiltonian_dp(d))
        self.assertEqual(literal, w.exact_core_tsp(2, p)["cost"])

    def test_multiple_zero_twins_preserve_subtour_value(self):
        d = w.metric_closure(4, [(0, 1, 1), (1, 2, 4),
                                 (2, 3, 3), (3, 0, 8), (0, 2, 2)])
        old_sep = w.subtour_lp(d)
        old_tsp = w.hamiltonian_dp(d)
        augmented = w.clone_metric(w.clone_metric(d, 0), 2)
        self.assertEqual(w.subtour_lp(augmented), old_sep)
        self.assertEqual(w.hamiltonian_dp(augmented), old_tsp)

    def test_parameter_rejection(self):
        invalid = [
            (2, [(0, 0, (1, 2))]),
            (2, [(0, 1, (1,))]),
            (2, [(0, 1, (1, 0))]),
            (2, [(0, 1, (-1, 2))]),
            (3, [(0, 1, (1, 2))]),
            (2, [(0, 2, (1, 2))])
        ]
        for n, edges in invalid:
            with self.subTest(edges=edges), self.assertRaises(ValueError):
                w.exact_core_tsp(n, edges)

    def test_cloning_preserves_exact_rational_subtour_and_tsp(self):
        d = w.metric_closure(3, [(0, 1, 3), (0, 2, 9), (1, 2, 2)])
        base = w.subtour_lp(d), w.hamiltonian_dp(d)
        for v in range(3):
            cloned = w.clone_metric(d, v)
            self.assertEqual((w.subtour_lp(cloned), w.hamiltonian_dp(cloned)), base)

    def test_effective_integer_weight_gap_reduction(self):
        # The epsilon certificate depends only on n, min and max distances,
        # not on the unknown optimal tour or LP values.
        original = [(0, 1, 3), (0, 2, 7), (1, 2, 5)]
        d = w.metric_closure(3, original)
        tolerance = Fraction(1, 10)
        epsilon = w.epsilon_for_ratio_tolerance(d, tolerance)
        self.assertGreater(epsilon, 0)
        self.assertLess(epsilon, 1)
        source_ratio = w.hamiltonian_dp(d) / w.subtour_lp(d)
        N, expanded, _ = w.expand(3, w.weighted_2_subdivision(3, original, epsilon))
        dst = w.metric_closure(N, expanded)
        target_ratio = w.hamiltonian_dp(dst) / w.subtour_lp(dst)
        self.assertLessEqual(abs(target_ratio - source_ratio), tolerance)
        # Multiply every weight by the denominator to get strictly
        # positive integer edge weights without changing the metric ratio.
        common_denominator = epsilon.denominator
        integer_paths = [
            (u, v, (epsilon * common_denominator, Fraction(weight * common_denominator)))
            for u, v, weight in original
        ]
        self.assertTrue(all(x.denominator == 1 for _, _, pair in integer_paths for x in pair))
        integer_n, int_edges, _ = w.expand(3, integer_paths)
        dint = w.metric_closure(integer_n, int_edges)
        self.assertEqual(w.hamiltonian_dp(dint) / w.subtour_lp(dint), target_ratio)
        with self.assertRaises(ValueError):
            w.epsilon_for_ratio_tolerance(d, 0)

    def test_two_edge_weighted_subdivision_converges_to_clones(self):
        # K3 source metric: one subdivision vertex is an epsilon-near
        # duplicate of one endpoint of each original edge.
        original = [(0, 1, 3), (0, 2, 7), (1, 2, 5)]
        base = w.metric_closure(3, original)
        target_tsp = w.hamiltonian_dp(base)
        target_sep = w.subtour_lp(base)
        for eps in (Fraction(1, 2), Fraction(1, 10)):
            paths = w.weighted_2_subdivision(3, original, eps)
            N, expanded, _ = w.expand(3, paths)
            d = w.metric_closure(N, expanded)
            self.assertEqual(N, 6)
            tsp, sep = w.hamiltonian_dp(d), w.subtour_lp(d)
            self.assertGreaterEqual(tsp, target_tsp)
            self.assertGreaterEqual(sep, target_sep)
            self.assertLessEqual(tsp - target_tsp, N * N * eps)
            self.assertLessEqual(sep - target_sep, N * N * eps)

    def test_seeded_independent_full_metric_dp_sweep(self):
        result = w.run_check(trials=60, seed=287)
        self.assertTrue(result["all_passed"])
        self.assertGreaterEqual(result["instances"], 150)


if __name__ == "__main__":
    unittest.main()
