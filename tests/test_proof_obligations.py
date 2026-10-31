import copy
import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import proof_obligations as obligations


class ProofObligationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = {"version": 1, "obligations": obligations.load()}

    def sample(self):
        return copy.deepcopy(self.seed)

    @staticmethod
    def node(items, oid):
        return next(x for x in items if x["id"] == oid)

    @staticmethod
    def purely_synthetic_bundle(item):
        # A structurally well-formed bundle is NOT a real proof or a review.
        return {
            "statement_sha256": hashlib.sha256(
                item["statement"].encode("utf-8")).hexdigest(),
            "artifact": "docs/LAMPORT_PROTOCOL.md",
            "checker": "scripts/proof_obligations.py",
            "scope_audit": "docs/LAMPORT_PROTOCOL.md",
            "independent_review_urls": [
                "https://synthetic.example.org/review-a",
                "https://synthetic.example.net/review-b",
            ],
        }

    def test_pilots_are_current_and_unproved(self):
        entries = obligations.load()
        self.assertEqual(len(entries), 6)
        self.assertEqual({x["problem_id"] for x in entries}, {"M074", "M075", "M095"})
        self.assertTrue(all(x["status"] in {"open", "blocked"} for x in entries))
        self.assertTrue(all(x["evidence"] is None for x in entries))

    def test_duplicate_ids_rejected(self):
        data = self.sample()
        data["obligations"].append(copy.deepcopy(data["obligations"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            obligations.validate(data)

    def test_out_of_scope_or_unknown_target_rejected(self):
        data = self.sample()
        self.node(data["obligations"], "O-M095-01")["problem_id"] = "M074"
        with self.assertRaisesRegex(ValueError, "bind"):
            obligations.validate(data)

    def test_missing_dependency_rejected(self):
        data = self.sample()
        self.node(data["obligations"], "O-M075-02")["depends_on"] = ["O-M075-99"]
        with self.assertRaisesRegex(ValueError, "Unknown"):
            obligations.validate(data)

    def test_cycle_rejected(self):
        data = self.sample()
        self.node(data["obligations"], "O-M075-01")["depends_on"] = ["O-M075-02"]
        with self.assertRaisesRegex(ValueError, "Cyclic"):
            obligations.validate(data)

    def test_false_proof_on_open_node_rejected(self):
        data = self.sample()
        item = self.node(data["obligations"], "O-M095-01")
        item["evidence"] = self.purely_synthetic_bundle(item)
        with self.assertRaisesRegex(ValueError, "Unclosed"):
            obligations.validate(data)

    def test_discharge_requires_exact_hash_and_bundle(self):
        data = self.sample()
        item = self.node(data["obligations"], "O-M095-01")
        item["status"] = "discharged"
        item["evidence"] = self.purely_synthetic_bundle(item)
        # This demonstrates ONLY structural acceptance, never mathematical truth.
        obligations.validate(data)
        item["statement"] += " Changing the theorem scope."
        with self.assertRaisesRegex(ValueError, "different statement"):
            obligations.validate(data)

    def test_discharge_cannot_launder_open_dependency(self):
        data = self.sample()
        item = self.node(data["obligations"], "O-M075-02")
        item["status"] = "discharged"
        item["evidence"] = self.purely_synthetic_bundle(item)
        with self.assertRaisesRegex(ValueError, "depends on an open"):
            obligations.validate(data)

    def test_review_distinct_domains_and_paths(self):
        data = self.sample()
        item = self.node(data["obligations"], "O-M095-01")
        item["status"] = "discharged"
        item["evidence"] = self.purely_synthetic_bundle(item)
        item["evidence"]["independent_review_urls"] = [
            "https://synthetic.example.org/a", "https://synthetic.example.org/b"
        ]
        with self.assertRaisesRegex(ValueError, "distinct"):
            obligations.validate(data)
        item["evidence"] = self.purely_synthetic_bundle(item)
        item["evidence"]["artifact"] = "../outside.txt"
        with self.assertRaisesRegex(ValueError, "missing or escapes"):
            obligations.validate(data)


if __name__ == "__main__":
    unittest.main()
