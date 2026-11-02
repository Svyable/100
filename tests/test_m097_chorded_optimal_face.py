"""Adversarial exact tests of the M097 chorded optimal-face certificate."""
import unittest
from fractions import Fraction
from itertools import combinations, permutations
from scripts.m097_chorded_optimal_face import (
    graph, shortest, forbidden_and_routes, optimal_point, tour_point, mixture, audit, run,
    sparse_optimal_support,
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
        self.assertLessEqual(report["outside_support_mass"], report["slack"])
        self.assertGreater(report["outside_support_mass"], 0)

    def test_stability_coefficient_is_sharp(self):
        # A shortest-path metric tour of length 10, with the chord used once.
        # Here m=9 and its entire forbidden-pair mass is exactly 1.
        cycle = (0, 1, 3, 2, 4, 5, 7, 6)
        edges = [tuple(sorted((a, b))) for a, b in
                 zip(cycle, cycle[1:] + cycle[:1])]
        x = {e: Fraction(1) for e in edges}
        report = audit((3, 3, 3), x)
        self.assertEqual(report["cost"], 10)
        self.assertEqual(report["slack"], 1)
        self.assertEqual(report["forbidden_mass"], 1)
        self.assertEqual(report["outside_support_mass"], 1)

    def test_every_internal_interval_cut_is_tight(self):
        for lengths in [(2, 2), (3, 3, 3), (2, 3, 4), (3, 4, 5, 6)]:
            n, edges, paths = graph(lengths)
            report = audit(lengths, optimal_point(lengths, paths),
                           check_feasible=n <= 12)
            self.assertEqual(report["tight_intervals"],
                             sum(length * (length - 1) // 2 for length in lengths))

    def test_sparse_support_against_all_shortest_simple_paths(self):
        # An independent DFS classification, not the formula used by the
        # checker to generate the sparse support.
        for lengths in [(2, 2), (2, 2, 2), (2, 3, 4), (3, 3, 3), (4, 4, 4)]:
            n, edges, paths = graph(lengths)
            support = sparse_optimal_support(edges, paths)
            adj = [[] for _ in range(n)]
            for a, b in edges:
                adj[a].append(b)
                adj[b].append(a)
            internal = set(range(2, n))
            dfs_support = set()
            for a, b in combinations(range(n), 2):
                distance = len(shortest(n, edges, a, b)) - 1
                stack = [(a, (a,))]
                routes = []
                while stack:
                    v, route = stack.pop()
                    if len(route) - 1 > distance:
                        continue
                    if v == b:
                        if len(route) - 1 == distance:
                            routes.append(route)
                        continue
                    for w in adj[v]:
                        if w not in route:
                            stack.append((w, route + (w,)))
                self.assertTrue(routes)
                if all(not (set(route[1:-1]) & internal)
                       and not any({u, v} == {0, 1}
                                   for u, v in zip(route, route[1:]))
                       for route in routes):
                    dfs_support.add((a, b))
            self.assertEqual(dfs_support, support)

    def test_support_strictly_stronger_than_chord_exclusion(self):
        lengths = (4, 4, 4)
        n, edges, paths, chord_pairs, routes = forbidden_and_routes(lengths)
        support = sparse_optimal_support(edges, paths)
        all_pairs = set(combinations(range(n), 2))
        self.assertEqual((n, len(chord_pairs), len(support)), (11, 13, 18))
        self.assertFalse(chord_pairs & support)
        self.assertEqual(len(all_pairs - chord_pairs - support), 24)

    def test_all_small_tours_quantitative_mass_bound(self):
        # Independent enumeration of every tour, without calling the
        # LP audit or its route-load proof. A tour is always subtour-feasible.
        count = 0
        sharp = 0
        for lengths in [(2, 2), (3, 3), (4, 4), (2, 2, 2),
                        (2, 3, 3), (3, 3, 3)]:
            n, edges, paths = graph(lengths)
            support = sparse_optimal_support(edges, paths)
            distances = {(a, b): len(shortest(n, edges, a, b)) - 1
                         for a, b in combinations(range(n), 2)}
            for tail in permutations(range(1, n)):
                tour = (0,) + tail
                pairs = [tuple(sorted((a, b))) for a, b in
                         zip(tour, tour[1:] + tour[:1])]
                slack = sum(distances[e] for e in pairs) - sum(lengths)
                mass = sum(e not in support for e in pairs)
                self.assertLessEqual(mass, slack, (lengths, tour))
                count += 1
                if mass == slack and mass > 0:
                    sharp += 1
        self.assertEqual(count, 10950)
        self.assertGreater(sharp, 0)

    def test_all_exact_optimal_tours_respect_sparse_support(self):
        # Independent permutation enumeration of Hamiltonian tours for
        # instances with TSP=SEP. All forbidden-support tours must cost >m.
        for lengths in [(2, 2), (2, 3), (3, 3), (2, 2, 2), (2, 2, 3),
                        (2, 3, 3)]:
            n, edges, paths = graph(lengths)
            support = sparse_optimal_support(edges, paths)
            distances = {(a, b): len(shortest(n, edges, a, b)) - 1
                         for a, b in combinations(range(n), 2)}
            best = 10**9
            optimum_count = 0
            for tail in permutations(range(1, n)):
                tour = (0,) + tail
                pairs = [tuple(sorted((a, b))) for a, b in
                         zip(tour, tour[1:] + tour[:1])]
                cost = sum(distances[e] for e in pairs)
                best = min(best, cost)
                if cost == sum(lengths):
                    optimum_count += 1
                    self.assertTrue(set(pairs) <= support, (lengths, pairs))
            self.assertEqual(best, sum(lengths))
            self.assertGreater(optimum_count, 0)

    def test_forged_infeasible_point_rejected(self):
        lengths = (3, 3, 3)
        n, edges, paths = graph(lengths)
        x = optimal_point(lengths, paths)
        x[(0, 1)] = Fraction(1, 2)
        with self.assertRaises(AssertionError):
            audit(lengths, x)


if __name__ == "__main__":
    unittest.main()
