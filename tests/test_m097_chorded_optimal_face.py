"""Adversarial exact tests of the M097 chorded optimal-face certificate."""
import unittest
from fractions import Fraction
from itertools import combinations
from scripts.m097_chorded_optimal_face import (
    graph, shortest, forbidden_and_routes, optimal_point, tour_point, mixture, audit, run,
)


def exhaustive_chord_geodesics(n, edges):
    """Independent simple-path DFS, not the two-hub distance decomposition."""
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    forbidden = set()
    for a, b in combinations(range(n), 2):
        distance = len(shortest(n, edges, a, b)) - 1
        stack = [(a, (a,), False)]
        while stack:
            vertex, path, uses_chord = stack.pop()
            if len(path) - 1 > distance:
                continue
            if vertex == b:
                if len(path) - 1 == distance and uses_chord:
                    forbidden.add((a, b))
                    break
                continue
            for next_vertex in adj[vertex]:
                if next_vertex not in path:
                    stack.append((next_vertex, path + (next_vertex,),
                                  uses_chord or {vertex, next_vertex} == {0, 1}))
    return forbidden


class OptimalFaceTests(unittest.TestCase):
    def test_exact_optimal_and_perturbed_sweep(self):
        self.assertEqual(run(9), {"optimal_instances": 26, "perturbed_instances": 52})

    def test_forbidden_pairs_against_all_simple_paths(self):
        for lengths in [(2, 2), (2, 2, 2), (3, 3, 3), (2, 3, 3)]:
            n, edges, paths, forbidden, routes = forbidden_and_routes(lengths)
            self.assertEqual(forbidden, exhaustive_chord_geodesics(n, edges))
            self.assertIn((0, 1), forbidden)
            self.assertGreater(len(forbidden), 1 if min(lengths) >= 3 else 0)
            for pair in forbidden:
                route = routes[pair]
                self.assertTrue(any({a, b} == {0, 1}
                                    for a, b in zip(route, route[1:])))

    def test_all_optimal_witnesses_avoid_chord_geodesics(self):
        for lengths in [(2, 2), (2, 2, 2), (3, 3, 3), (2, 3, 4), (3, 4, 5, 6)]:
            n, edges, paths = graph(lengths)
            report = audit(lengths, optimal_point(lengths, paths),
                           check_feasible=n <= 12)
            self.assertEqual(report["slack"], 0)
            self.assertEqual(report["forbidden_mass"], 0)
            self.assertEqual(report["chord_load"], 0)

    def test_quantitative_stability_on_nonoptimal_feasible_point(self):
        lengths = (3, 3, 3)
        n, edges, paths = graph(lengths)
        x = optimal_point(lengths, paths)
        tour = tour_point(n)
        report = audit(lengths, mixture(x, tour, Fraction(2, 5)))
        self.assertGreater(report["slack"], 0)
        self.assertGreater(report["forbidden_mass"], 0)
        self.assertLessEqual(report["forbidden_mass"], report["slack"])

    def test_forged_infeasible_point_rejected(self):
        lengths = (3, 3, 3)
        n, edges, paths = graph(lengths)
        x = optimal_point(lengths, paths)
        x[(0, 1)] = Fraction(1, 2)
        with self.assertRaises(AssertionError):
            audit(lengths, x)


if __name__ == "__main__":
    unittest.main()
