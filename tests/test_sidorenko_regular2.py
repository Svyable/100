"""Falsification controls for a quantitative M073 regular two-block restriction."""
import itertools
from collections import Counter
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sidorenko_regular2 as reg
import sidorenko_twoblock as old


def even_subgraph_coefficients(n, edges):
    """Independent direct 2^m subset parity census (only tiny cases)."""
    result = Counter()
    for mask in range(1 << len(edges)):
        degrees = [0] * n
        for i, (u, v) in enumerate(edges):
            if mask >> i & 1:
                degrees[u] += 1
                degrees[v] += 1
        if all(d % 2 == 0 for d in degrees):
            result[mask.bit_count()] += 1
    return result


class GeneralParityIdentity(unittest.TestCase):
    def test_direct_even_subset_census_matches_spin_sum(self):
        families = (
            (3, [(0, 1), (1, 2), (2, 0)]),  # nonbipartite, odd coeff possible
            (4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
            (6, [(i, (i+1) % 6) for i in range(6)]),
            (5, [(0, 1), (1, 2)]),  # isolated vertices
            (4, [(0, 1), (0, 2), (0, 3)]),
        )
        for n, edges in families:
            coeff = even_subgraph_coefficients(n, edges)
            for a, b in itertools.product((0, 1, 2, 3), repeat=2):
                if a + b == 0:
                    continue
                with self.subTest(n=n, edges=edges, a=a, b=b):
                    T = old.numerator_by_edges(n, edges, old.weights(a, b, a))
                    m = len(edges)
                    expression = sum(num * (a-b)**k * (a+b)**(m-k)
                                     for k, num in coeff.items())
                    self.assertEqual((1 << m) * T, (1 << n) * expression)

    def test_bipartite_all_even_subgraphs_have_even_edge_count(self):
        for n, edges in (
                (4, [(0,1),(1,2),(2,3),(3,0)]),
                (6, [(i,(i+1)%6) for i in range(6)]),
                (5, [(0,1),(0,2),(1,3),(2,3),(3,4)])):
            coeff = even_subgraph_coefficients(n, edges)
            self.assertTrue(all(k%2==0 for k in coeff))

    def test_naive_nonbipartite_extension_false(self):
        triangle = [(0,1),(1,2),(2,0)]
        coeff = even_subgraph_coefficients(3, triangle)
        self.assertEqual(coeff, {0: 1, 3: 1})
        W = old.weights(0, 2, 0)  # cross-only equal-mass two-block graphon
        self.assertEqual(old.numerator_by_edges(3, triangle, W), 0)
        # p=1/2>0: t(K3,W)=0 is strictly less than p^3.


class PinnedM073Cycles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faces = old.read_faces()
        cls.edges = reg.incidence_edges(cls.faces)

    def test_pair_face_formula_and_graph_dfs_agree(self):
        self.assertEqual(reg.small_cycles_from_faces(self.faces), (33, 88))
        self.assertEqual(reg.cycles_by_graph_dfs(35, self.edges, 4), 33)
        self.assertEqual(reg.cycles_by_graph_dfs(35, self.edges, 6), 88)
        self.assertEqual(reg.cycles_by_graph_dfs(35, self.edges, 3), 0)

    def test_four_cycle_formula_handles_shared_faces(self):
        # In K2,2, each point pair occurs in two distinct faces.
        self.assertEqual(reg.small_cycles_from_faces(((0,1,2),(0,1,3))), (1, 0))
        # Triangular arrangement of three point-pairs in three distinct faces:
        self.assertEqual(reg.small_cycles_from_faces(((0,1,3),(1,2,4),(0,2,5))), (0, 1))

    def test_point_skeleton_explains_88_c6_without_dfs(self):
        skeleton = reg.point_skeleton_certificate(self.faces)
        self.assertEqual(skeleton["skeleton_edges"], 33)
        self.assertEqual(skeleton["skeleton_triangles"], 22)
        self.assertEqual(skeleton["six_cycles_from_four_choices_per_triangle"], 88)
        with self.assertRaises(AssertionError):
            reg.point_skeleton_certificate(self.faces[:-1])

    def test_cycle_space_boundary_independent_connected_check(self):
        cert = reg.certificate()
        self.assertEqual(cert["pattern_edges"], 66)
        self.assertEqual(cert["pattern_vertices"], 35)
        self.assertEqual(cert["cycle_space_dimension"], 32)
        self.assertEqual(cert["total_even_subgraphs_at_abs_r_one"], 2**32)
        self.assertEqual(cert["four_cycles"], 33)
        self.assertEqual(cert["six_cycles"], 88)

    def test_exact_rational_grid_and_strictness(self):
        for a in range(5):
            for b in range(5):
                r = reg.check_rational(a, b, independently_recount=(a,b) in ((0,4),(4,0),(2,2)))
                self.assertGreaterEqual(r["left"],r["right"])
                self.assertEqual(r["strict"], a != b)

    def test_reject_out_of_domain_and_boolean_weights(self):
        for a,b,d in ((0,5,4),(5,0,4),(-1,0,4),(True,1,4),(1,False,4),(1,1,True),
                      (1,1,0),(1,1,-1),(1,1,4.5)):
            with self.subTest(weights=(a,b,d)), self.assertRaises(ValueError):
                reg.check_rational(a,b,d)

    def test_no_false_continuum_proof_from_grid(self):
        cert = reg.certificate()
        self.assertIn("not all two-step", cert["boundary"].lower())
        self.assertIn("a,b real", cert["domain"])
        self.assertIn("33*r^4+88*r^6", cert["bound"])
        # The theorem's analytic proof is separate from finite rational probes.


if __name__ == "__main__":
    unittest.main()
