"""Adversarial and independent replay tests for a pinned K42 extension refutation."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ramsey_extension import (
    CERT, constraints_bitset, generate_first, generate_tree,
    independent_k4_clauses, source_records, verify_tree, verify_all,
)
from verify_mckay import decode_graph6


class RamseyExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adj = decode_graph6(source_records()[0])
        cls.cert = json.loads(CERT.read_text())

    def test_frozen_certificate_replays(self):
        self.assertEqual(generate_first(), self.cert["proofs"][0])

    def test_all_328_independent_refutations(self):
        self.assertEqual(verify_all(self.cert), {
            "records": 328, "nonextendible": 328, "max_nodes": 51,
            "node_distribution": {39: 215, 41: 66, 43: 39, 45: 6, 47: 1, 51: 1},
            "max_depth": 9, "depth_distribution": {5: 217, 6: 66, 7: 37, 8: 6, 9: 2},
        })

    def test_reject_missing_record(self):
        bad = dict(self.cert)
        bad["proofs"] = self.cert["proofs"][:-1]
        with self.assertRaises(ValueError):
            verify_all(bad)

    def test_reject_source_digest_mutation(self):
        bad = dict(self.cert)
        bad["source_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            verify_all(bad)

    def test_independent_k4_enumeration(self):
        generator, counts = constraints_bitset(self.adj)
        checker = independent_k4_clauses(self.adj)
        self.assertEqual(len(generator), sum(counts))
        self.assertEqual(set(generator), set(checker))

    def test_frozen_unsat_tree(self):
        stats = verify_tree(self.adj, self.cert["proofs"][0]["tree"])
        self.assertEqual(stats, {"branches": 20, "conflicts": 21, "clauses": 2313})

    def test_reject_early_leaf(self):
        with self.assertRaises(ValueError):
            verify_tree(self.adj, None)

    def test_reject_incomplete_branch(self):
        tree = list(self.cert["proofs"][0]["tree"])
        tree[1] = None
        with self.assertRaises(ValueError):
            verify_tree(self.adj, tree)

    def test_reject_bad_branch_variable(self):
        tree = list(self.cert["proofs"][0]["tree"])
        tree[0] = 42
        with self.assertRaises(ValueError):
            verify_tree(self.adj, tree)

    def test_reject_nonbinary_tree(self):
        with self.assertRaises(ValueError):
            verify_tree(self.adj, [0, None])

    def test_positive_satisfiable_control(self):
        # Four mutually red vertices; a new all-blue vertex is valid.
        adj = [sum(1 << j for j in range(4) if j != i) for i in range(4)]
        clauses, counts = constraints_bitset(adj)
        self.assertEqual(counts, (1, 0))
        solution, nodes = generate_tree(clauses, n=4)
        self.assertIsInstance(solution, dict)
        self.assertGreaterEqual(nodes, 1)
        with self.assertRaises(ValueError):
            verify_tree(adj, None)

    def test_bad_source_record_rejected(self):
        # The graph6 parser rejects an invalid order prefix.
        with self.assertRaises(ValueError):
            decode_graph6(b"?")


if __name__ == "__main__":
    unittest.main()
