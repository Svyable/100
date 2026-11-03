import importlib.util
from fractions import Fraction as Q
from itertools import combinations, permutations
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "scripts/m097_subdivision_core.py"
SPEC = importlib.util.spec_from_file_location("subdivision_core", PATH)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class SubdivisionCoreTests(unittest.TestCase):
    def test_cycle_basis_against_literal_parities(self):
        for n, edges in [(4, list(combinations(range(4), 2))),
                         (3, [(0, 1), (0, 1), (1, 2), (0, 2)])]:
            expected = set()
            for mask in range(1 << len(edges)):
                deg = [0] * n
                for i, (a, b) in enumerate(edges):
                    if mask >> i & 1:
                        deg[a] += 1
                        deg[b] += 1
                if all(d % 2 == 0 for d in deg):
                    expected.add(mask)
            masks = list(m.even_masks(n, edges))
            self.assertEqual(set(masks), expected)
            self.assertEqual(len(masks), len(expected))

    def test_bridge_is_doubled(self):
        row = m.check_instance(3, [(0, 1), (1, 2)], [3, 2])
        self.assertEqual((row["sep"], row["tsp"]), (10, 10))

    def test_asymmetric_parallel_paths(self):
        row = m.check_instance(2, [(0, 1)] * 3, [3, 4, 5])
        self.assertEqual((row["sep"], row["tsp"]), (12, 13))

    def test_literal_permutations(self):
        n, edges, _ = m.expand(3, [(0, 1), (1, 2), (2, 0)], [2, 2, 2])
        d = m.metric(n, edges)
        actual = min(sum(d[a][b] for a, b in zip((0,) + p, p + (0,)))
                     for p in permutations(range(1, n)))
        self.assertEqual(m.tour_dp(d), actual)
        self.assertEqual(actual, 6)

    def test_articulation_requires_gluing(self):
        core = [(0,1),(1,2),(2,0),(0,3),(3,4),(4,0)]
        n, edges, _ = m.expand(5, core, [2]*6)
        bad = m.star_point(range(n), edges)
        self.assertEqual(m.mincut(n, bad)[0], Q(5, 3))
        with self.assertRaises(AssertionError):
            m.check_primal(n, edges, bad)
        good = m.primal(range(n), edges)
        self.assertEqual(m.check_primal(n, edges, good), 12)

    def test_tampered_primal_rejected(self):
        n, edges, _ = m.expand(2, [(0,1)]*3, [2,3,3])
        point = m.primal(range(n), edges)
        point[next(iter(point))] += Q(1, 100)
        with self.assertRaises(AssertionError):
            m.check_primal(n, edges, point)

    def test_tampered_dual_rejected(self):
        core, lengths = [(0,1)]*3, [2,3,3]
        n, edges, _ = m.expand(2, core, lengths)
        cuts, _ = m.dual(2, core, lengths)
        cuts[0] = cuts[0][0], cuts[0][1] + Q(1, 100)
        with self.assertRaises(AssertionError):
            m.check_dual(n, edges, cuts)

    def test_connectivity_correction_is_necessary(self):
        # Empty even subset: without c-1 connecting paths the support is disconnected.
        core, lengths = [(0,1),(1,2)], [2,2]
        n, edges, paths = m.expand(3, core, lengths)
        bad = {e: 2 for e in edges}
        for p in paths:
            bad[m.edge(p[0], p[1])] = 0
        with self.assertRaises(AssertionError):
            m.check_walk(n, edges, bad)
        self.assertEqual(sum(m.walk_certificate(3, core, lengths, 0).values()), 8)

    def test_invalid_even_mask_rejected(self):
        with self.assertRaises(ValueError):
            m.walk_certificate(2, [(0,1)]*3, [2]*3, 1)

    def test_invalid_input_rejected(self):
        inputs = [(2, [(0,1)], [1]), (2, [(0,1)], [True]),
                  (2, [(0,0)], [2]), (3, [(0,1)], [2]),
                  (2, [(0,2)], [2]), (2, [(0,1)], [])]
        for data in inputs:
            with self.subTest(data=data), self.assertRaises(ValueError):
                m.expand(*data)

    def test_short_edges_break_lp_identity(self):
        # Outside the shared theorem domain: K4 has SEP=TSP=4, not m=6.
        edges = set(combinations(range(4), 2))
        x = {e: Q(2, 3) for e in edges}
        self.assertEqual(m.check_primal(4, edges, x, exhaustive=True), 4)
        self.assertEqual(m.tour_dp(m.metric(4, edges)), 4)

    def test_double_octahedron_phase_change(self):
        n, edges = m.double_octahedron()
        profile = m.uniform_profile(n, edges)
        self.assertEqual(profile["minimum_join_size"], 2)
        self.assertNotIn(3, profile["minimum_components_by_join_size"])
        self.assertEqual(profile["minimum_join_complement_components"], 2)
        self.assertEqual(profile["stabilization_length"], 3)
        for L, value in [(2,52),(3,82),(4,110),(1000000,27999998)]:
            with self.subTest(length=L):
                self.assertEqual(m.optimum(n, edges, [L]*26)[0], value)

    def test_large_two_subdivision_primal_and_explicit_walk(self):
        n, core = m.double_octahedron()
        N, expanded, _ = m.expand(n, core, [2]*26)
        deleted = {(0,2),(1,2),(6,8),(7,8)}
        mask = sum(1 << i for i, e in enumerate(core) if e not in deleted)
        walk = m.walk_certificate(n, core, [2]*26, mask)
        self.assertEqual(m.check_walk(N, expanded, walk), 52)
        self.assertEqual(m.check_primal(N, expanded, m.primal(range(N), expanded)), 52)

    def test_uniform_stabilization_on_all_four_vertex_cores(self):
        pairs = list(combinations(range(4), 2))
        for mask in range(1, 1 << len(pairs)):
            edges = [e for i, e in enumerate(pairs) if mask >> i & 1]
            if len(m.components(range(4), edges)) != 1:
                continue
            p = m.uniform_profile(4, edges)
            start = p["stabilization_length"]
            for L in range(start, start + 3):
                self.assertEqual(m.optimum(4, edges, [L]*len(edges))[0],
                                 p["eventual_slope"]*L + p["eventual_intercept"])
            if start > 2:
                L = start - 1
                self.assertLess(m.optimum(4, edges, [L]*len(edges))[0],
                                p["eventual_slope"]*L + p["eventual_intercept"])


if __name__ == "__main__":
    unittest.main()
