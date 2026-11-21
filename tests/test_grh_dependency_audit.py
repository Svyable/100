import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import grh_dependency_audit as grh


class GRHDependencyAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads(grh.AUDIT.read_text(encoding="utf-8"))
        cls.problems = json.loads(grh.PROBLEMS.read_text(encoding="utf-8"))

    def test_current_scope_is_classified_but_not_verified_here(self):
        counts = grh.validate(self.audit, self.problems)
        self.assertEqual(sum(counts.values()), 18)
        self.assertFalse(self.audit["project_replayed"])
        self.assertFalse(self.audit["project_independently_reviewed"])
        self.assertEqual({entry["id"] for entry in self.audit["active_targets"]}, {"M001", "M002"})
        self.assertGreater(counts["eligible_audit"], 0)
        self.assertGreater(counts["blocked_stronger_family"], 0)

    def test_stronger_grh_cannot_be_labeled_eligible(self):
        for family in ("dedekind", "hecke", "artin", "automorphic"):
            audit = copy.deepcopy(self.audit)
            audit["consequences"][0]["requires_family"] = family
            with self.subTest(family=family), self.assertRaises(grh.ScopeError):
                grh.validate(audit, self.problems)

    def test_unresolved_dependency_cannot_be_promoted(self):
        audit = copy.deepcopy(self.audit)
        audit["consequences"][0]["requires_family"] = "unresolved"
        with self.assertRaises(grh.ScopeError):
            grh.validate(audit, self.problems)

    def test_no_self_attestation_or_target_substitution(self):
        for field in ("project_replayed", "project_independently_reviewed"):
            audit = copy.deepcopy(self.audit)
            audit[field] = True
            with self.subTest(field=field), self.assertRaises(grh.ScopeError):
                grh.validate(audit, self.problems)
        audit = copy.deepcopy(self.audit)
        audit["active_targets"][1]["requires_family"] = "hecke"
        with self.assertRaises(grh.ScopeError):
            grh.validate(audit, self.problems)
        audit = copy.deepcopy(self.audit)
        audit["active_targets"][0]["project_status"] = "resolved"
        with self.assertRaises(grh.ScopeError):
            grh.validate(audit, self.problems)

    def test_no_duplicate_claim_or_insecure_sources(self):
        audit = copy.deepcopy(self.audit)
        audit["consequences"].append(copy.deepcopy(audit["consequences"][0]))
        with self.assertRaises(grh.ScopeError):
            grh.validate(audit, self.problems)
        audit = copy.deepcopy(self.audit)
        audit["source_mit"] = "http://math.mit.edu/~drew/grh/"
        with self.assertRaises(grh.ScopeError):
            grh.validate(audit, self.problems)

    def test_registry_scope_drift_fails(self):
        problems = copy.deepcopy(self.problems)
        for row in problems:
            if row["id"] == "M002":
                row["question"] = "What about all Hecke L-functions?"
        with self.assertRaises(grh.ScopeError):
            grh.validate(self.audit, problems)


if __name__ == "__main__":
    unittest.main()
