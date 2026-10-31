import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import digraph
import digraph_orbits


class OrbitTests(unittest.TestCase):
    def test_complete_orbits_and_burnside(self):
        for n in (2, 3, 4, 5):
            result = digraph_orbits.enumerate_orbits(n)
            self.assertEqual(result["unlabeled_orbits"], digraph_orbits.KNOWN_ALL[n])
            self.assertEqual(result["burnside_orbits"], result["unlabeled_orbits"])
            self.assertEqual(result["oriented_unlabeled"], digraph_orbits.KNOWN_ORIENTED[n])
            self.assertEqual(result["labeled_graphs"], 2**(n*(n-1)))
            self.assertEqual(result["by_minimum_r"]["1"]["unlabeled"],
                             result["eligible_min_degree_classes"])

    def test_deterministic_n5_representatives(self):
        self.assertEqual(
            digraph_orbits.enumerate_orbits(5)["representative_sha256"],
            "e658bbb3b3344f8358144e9ce940185138eb7eb46867c686f98a36cf5ad8cab1"
        )

    def test_vertex_relabeling_preserves_girth(self):
        n = 4
        arcs, lookup = digraph_orbits.arc_index(n)
        mappings = digraph_orbits.permutations_of_arcs(n, arcs, lookup)
        mask = 1443
        g = digraph.directed_girth(digraph_orbits.adjacency(mask, arcs, n))
        self.assertEqual(len(mappings), 24)
        for mapping in mappings:
            image = digraph_orbits.image_of(mask, mapping)
            self.assertEqual(g, digraph.directed_girth(
                digraph_orbits.adjacency(image, arcs, n)))


if __name__ == "__main__":
    unittest.main()
