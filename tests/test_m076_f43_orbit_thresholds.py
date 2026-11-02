"""Adversarial controls for the M076 one-insertion threshold certificate."""
import unittest
from itertools import combinations
from scripts import m076_f43_orbit_thresholds as m


class OrbitThresholdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.family = m.base_family()
        cls.reps, cls.sizes = m.representatives(set(cls.family))

    def test_exact_spectrum_and_full_sweep(self):
        data = m.check()
        self.assertEqual(data["orbit_free_candidates_checked"], 7261)
        self.assertEqual(data["table_sha256"], "25affd4db98cb19db6bf91729c54c5dfd03c2479b589d71239f182c365ffb435")

    def test_orbit_counts(self):
        self.assertEqual(len(self.reps), 18)
        self.assertEqual(sum(self.sizes.values()), 7261)

    def test_structural_colors_cover_every_edge(self):
        for c in self.reps.values():
            colors = m.structural_colors(self.family, c)
            self.assertTrue(all(colors[i] != colors[j]
                                for i, j in m.conflict_edges(self.family, c)))

    def test_matching_and_cover_certificates(self):
        for c in self.reps.values():
            edges = m.conflict_edges(self.family, c)
            match, cover = m.matching_and_cover(edges, m.structural_colors(self.family, c), 54)
            self.assertEqual(len(match), len(cover))
            self.assertTrue(all(i in cover or j in cover for i, j in edges))
            self.assertEqual(m.verify_witness(self.family, c, cover), 55-len(cover))

    def test_minimum_five_and_cross_component_eleven(self):
        for k, c in self.reps.items():
            edges = m.conflict_edges(self.family, c)
            match, _ = m.matching_and_cover(edges, m.structural_colors(self.family, c), 54)
            if k == (1, ((2, 1, 0), (0, 0, 0))):
                self.assertEqual(len(match), 5)
            if k == (0, ((2, 1, 0), (1, 0, 0))):
                self.assertEqual(len(match), 11)

    def test_missing_cover_vertex_is_rejected(self):
        c = self.reps[(0, ((2, 1, 0), (1, 0, 0)))]
        edges = m.conflict_edges(self.family, c)
        _, cover = m.matching_and_cover(edges, m.structural_colors(self.family, c), 54)
        for i in cover:
            damaged = set(cover) - {i}
            self.assertTrue(any(a not in damaged and b not in damaged for a, b in edges))

    def test_non_bipartite_conflict_graph_can_exist_elsewhere(self):
        # Five edges of C5: sunflower-free 2-sets; disjointness graph is C5.
        other = tuple(frozenset((i, (i+1) % 5)) for i in range(5))
        self.assertFalse(any(m.literal_sunflower(a, b, c)
                             for a, b, c in combinations(other, 3)))
        edges = m.conflict_edges(other, frozenset((5, 6)))
        adj = {i: [] for i in range(5)}
        for i, j in edges:
            adj[i].append(j)
            adj[j].append(i)
        self.assertEqual(sorted(len(x) for x in adj.values()), [2]*5)
        with self.assertRaises(AssertionError):
            m.matching_and_cover(edges, {i: i % 2 for i in range(5)}, 5)


if __name__ == "__main__":
    unittest.main()
