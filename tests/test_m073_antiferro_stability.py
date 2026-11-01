"""Adversarial exact checks for the M073 antiferromagnetic stability lemma."""
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m073_antiferro_stability as target
from m073_assortative2 import load_faces, graph_counts

Q = Fraction


class AntiferroStabilityTests(unittest.TestCase):
    def test_pinned_source_and_cycle_coefficients(self):
        self.assertEqual(graph_counts(load_faces()), target.EXPECTED)

    def test_strict_offdiagonal_rational_certificate(self):
        result = target.sample_certificate()
        self.assertTrue(result["strict_sufficient_condition"])
        self.assertTrue(result["two_exact_density_paths_agree"])
        self.assertTrue(result["exact_gap_positive"])
        self.assertEqual(result["sample_weights"], ["19/32", "32/32", "13/32"])
        self.assertGreater(Q(1114, 729) * Q(247, 256)**11, 1)

    def test_direct_small_bipartite_density_checks(self):
        self.assertEqual(target.adversarial_audit()["relative_checks"], 8)

    def test_boundary_delta_zero(self):
        edges = [(0, 1), (1, 2), (2, 3)]
        t0 = target.density(4, edges, Q(1, 2), Q(1), Q(0))
        self.assertGreaterEqual(t0, Q(3, 4)**len(edges))
        self.assertTrue(target.exact_relative_bound(
            4, edges, Q(1, 2), Q(1), Q(0)))

    def test_nonbipartite_edge_correlation_is_not_ferromagnetic(self):
        tri = [(0, 1), (1, 2), (0, 2)]
        c = target.edge_spin_correlation(3, tri, Q(1, 2), Q(1), (0, 1))
        self.assertEqual(c, Q(-3, 13))
        self.assertGreater(c, Q(-1, 3))

    def test_invalid_weights_fail_closed(self):
        for u, b, d in [(Q(0), Q(1), Q(0)),
                        (Q(1), Q(1, 2), Q(0)),
                        (Q(1, 2), Q(1), Q(3, 4))]:
            with self.subTest(u=u, b=b, d=d):
                with self.assertRaises(ValueError):
                    target.density(2, [(0, 1)], u, b, d)

    def test_invalid_edges_fail_closed(self):
        for edges in [[(0, 0)], [(0, 2)], [(0, 1), (1, 0)]]:
            with self.subTest(edges=edges):
                with self.assertRaises(ValueError):
                    target.density(2, edges, Q(1, 2), Q(1), Q(1, 8))

    def test_source_mutation_is_rejected(self):
        import json
        import tempfile
        from pathlib import Path
        original = Path(__file__).resolve().parents[1] / "data/reference/sidorenko_faces.json"
        data = json.loads(original.read_text())
        data["faces"][0] = [0, 1, 4]
        with tempfile.TemporaryDirectory() as tmp:
            mutated = Path(tmp) / "faces.json"
            mutated.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                load_faces(mutated)

    def test_correlation_requires_existing_edge(self):
        with self.assertRaises(ValueError):
            target.edge_spin_correlation(
                3, [(0, 1)], Q(1, 2), Q(1), (1, 2))

    def test_all_bipartite_graphs_on_four_labeled_vertices(self):
        # Exhaust all 2^4 edge subsets of K_{2,2}; no graph-level
        # heuristic or floating point enters this small exact check.
        possible = [(0, 2), (0, 3), (1, 2), (1, 3)]
        for mask in range(1, 1 << len(possible)):
            edges = [e for j, e in enumerate(possible) if mask & (1 << j)]
            with self.subTest(mask=mask):
                self.assertTrue(target.exact_relative_bound(
                    4, edges, Q(1, 2), Q(1), Q(3, 32)))


if __name__ == "__main__":
    unittest.main()
