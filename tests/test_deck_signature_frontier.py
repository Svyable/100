import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import deck_signature_frontier as frontier


class DeckMotifFrontier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(frontier.OUTPUT.read_text(encoding="utf-8"))

    def test_frozen_exact_counts(self):
        table = self.data["table"]
        self.assertEqual([table[str(i)]["isomorphism_classes_burnside"] for i in range(3, 9)],
                         [4, 11, 34, 156, 1044, 12346])
        self.assertEqual([table[str(i)]["degree_triangle_excess"] for i in range(3, 9)],
                         [0, 0, 0, 0, 0, 89])
        self.assertEqual([table[str(i)]["degree_triangle_square_excess"] for i in range(3, 9)],
                         [0, 0, 0, 0, 0, 0])
        self.assertEqual(table["8"]["tested_graphs"], 1044 * 128)

    def test_witness_fails_S3_but_not_S4(self):
        a, b = [frontier.adjacency(8, edges) for edges in frontier.WITNESS]
        self.assertEqual(frontier.independent_signature(a), frontier.independent_signature(b))
        self.assertEqual(frontier.fast_signature(a), frontier.fast_signature(b))
        self.assertNotEqual(frontier.independent_signature(a, True),
                            frontier.independent_signature(b, True))
        self.assertEqual([frontier.four_cycles(a), frontier.four_cycles(b)], [2, 1])
        self.assertEqual(sum(x.bit_count() for x in a), 20)
        self.assertEqual(sum(x.bit_count() for x in b), 20)

    def test_relabeling_preserves_card_invariants(self):
        a = frontier.adjacency(8, frontier.WITNESS[0])
        permutation = [6, 2, 0, 5, 7, 1, 3, 4]
        edges = [
            sorted((permutation[i], permutation[j]))
            for i in range(8) for j in range(i + 1, 8) if a[i] >> j & 1
        ]
        permuted = frontier.adjacency(8, edges)
        self.assertEqual(frontier.fast_signature(a), frontier.independent_signature(permuted))
        self.assertEqual(frontier.fast_signature(a, True), frontier.independent_signature(permuted, True))

    def test_edge_mutation_is_detected(self):
        a = frontier.adjacency(8, frontier.WITNESS[0])
        changed = copy.deepcopy(frontier.WITNESS[0])
        changed.remove([0, 4])
        tampered = frontier.adjacency(8, changed)
        self.assertNotEqual(frontier.fast_signature(a), frontier.fast_signature(tampered))
        self.assertNotEqual(frontier.independent_signature(a, True),
                            frontier.independent_signature(tampered, True))

    def test_malformed_edge_list_rejected(self):
        for edges in ([[0, 4], [0, 4]], [[4, 0]], [[-1, 7]], [[0, 8]]):
            with self.assertRaises(ValueError):
                frontier.adjacency(8, edges)

    def test_fast_and_independent_agree_on_every_small_graph(self):
        for n in range(3, 7):
            for a in frontier.instances(n):
                self.assertEqual(frontier.fast_signature(a),
                                 frontier.independent_signature(a))
                self.assertEqual(frontier.fast_signature(a, True),
                                 frontier.independent_signature(a, True))

    def test_no_claim_of_full_reconstruction(self):
        self.assertEqual(self.data["mathematical_novelty"].split(";")[0], "unconfirmed")
        self.assertIn("NOT a same-deck pair", self.data["counterexample_S3_n8"]["note"])


if __name__ == "__main__":
    unittest.main()
