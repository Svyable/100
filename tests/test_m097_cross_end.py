"""Adversarial checks for X-M097-CROSS-END, claim #232."""
import unittest

from scripts.m097_cross_end import (
    graph, recombined_paths, distances, fractional_witness,
    check_witness, expected, eulerian_witness, tour_dp, run,
)


class CrossEndTests(unittest.TestCase):
    def test_bad_parameters(self):
        for lengths in [(), (2, 2), (1, 2, 3), (3, 1, 4)]:
            with self.assertRaises(ValueError):
                graph(lengths)

    def test_recombined_path_is_spanning(self):
        for lengths in [(2, 2, 2), (3, 4, 5), (2, 3, 4, 2)]:
            n, edges, paths = graph(lengths)
            qs = recombined_paths(paths)
            self.assertEqual(len(qs), len(lengths) - 1)
            self.assertEqual(sum(len(q) - 1 for q in qs), sum(lengths) - 1)
            self.assertEqual(set.union(*(set(q) for q in qs)), set(range(n)))
            for q in qs:
                self.assertTrue(all(tuple(sorted((a, b))) in edges
                                    for a, b in zip(q, q[1:])))

    def test_fractional_witness_exact(self):
        for lengths in [(3, 3, 3, 3), (2, 2, 2, 2), (2, 3, 4, 5),
                        (3, 3, 3, 3, 3), (2, 2, 2, 2, 2)]:
            self.assertEqual(check_witness(lengths), sum(lengths) - 1)

    def test_parity_witness_cases(self):
        for lengths in [(3, 3, 3), (3, 3, 3, 3), (2, 3, 3, 3),
                        (3, 2, 3, 3), (3, 3, 2, 3), (3, 3, 3, 3, 3)]:
            y = eulerian_witness(lengths)
            self.assertEqual(sum(y.values()), expected(lengths)[1])

    def test_sharp_12_over_11(self):
        self.assertEqual(expected((3, 3, 3, 3)), (11, 12))
        self.assertEqual(tour_dp((3, 3, 3, 3)), 12)

    def test_cross_edge_location_matters(self):
        # An edge between the two FIRST internal vertices is not
        # covered by the theorem; it destroys the Hamiltonian 8-cycle.
        self.assertEqual(tour_dp((3, 3, 3), cross="end"), 8)
        self.assertEqual(tour_dp((3, 3, 3), cross="first"), 9)

    def test_mutated_fractional_witness_rejected(self):
        lengths = (3, 3, 3, 3)
        _, _, paths = graph(lengths)
        x = fractional_witness(paths)
        edge = next(iter(x))
        x[edge] = 0
        self.assertNotEqual(sum(w for (a, b), w in x.items()
                                if edge[0] in (a, b)), 2)

    def test_exhaustive_labeled_sweep(self):
        self.assertEqual(run(max_vertices=10)["instances"], 166)


if __name__ == "__main__":
    unittest.main()
