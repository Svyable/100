import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import portfolio_triage as t

class TriageTests(unittest.TestCase):
    def setUp(self):
        self.active = json.loads(t.REGISTRY.read_text(encoding="utf-8"))
        self.doc = json.loads(t.TRIAGE.read_text(encoding="utf-8"))

    def test_valid_screening(self):
        self.assertEqual(sum(t.validate(self.doc, self.active).values()), 15)

    def test_duplicate_unknown_id_rejected(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"].append(copy.deepcopy(bad["entries"][0]))
        with self.assertRaises(ValueError):
            t.validate(bad, self.active)
        bad = copy.deepcopy(self.doc)
        bad["entries"][0]["id"] = "M999"
        with self.assertRaises(ValueError):
            t.validate(bad, self.active)

    def test_claim_without_source_and_premature_promotion_rejected(self):
        bad = copy.deepcopy(self.doc)
        next(e for e in bad["entries"] if e["concern"] == "resolution_claim")["lead_urls"] = []
        with self.assertRaises(ValueError):
            t.validate(bad, self.active)
        bad = copy.deepcopy(self.doc)
        bad["admission_candidates"][0]["admission_state"] = "verified_open"
        with self.assertRaises(ValueError):
            t.validate(bad, self.active)

    def test_missing_evidence_and_duplicate_active_name_rejected(self):
        bad = copy.deepcopy(self.doc)
        bad["entries"][0]["evidence_needed"] = ""
        with self.assertRaises(ValueError):
            t.validate(bad, self.active)
        bad = copy.deepcopy(self.doc)
        bad["admission_candidates"][0]["name"] = self.active[0]["name"]
        with self.assertRaises(ValueError):
            t.validate(bad, self.active)

if __name__ == "__main__":
    unittest.main()
