import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import frankl_triple_experiment as pilot
import frankl_triple_sat as core


class TriplePilotRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((ROOT / "data/experiments/frankl_triple7_pilot.json").read_text())

    def test_real_record_remains_two_inconclusive_runs(self):
        result = pilot.validate_record(copy.deepcopy(self.record))
        self.assertEqual(result["checked_records"], 2)
        self.assertEqual(result["unknown"], 2)
        self.assertEqual(result["sat"], 0)
        self.assertEqual(result["independent_unsat_proofs"], 0)

    def test_tampered_digest_refused(self):
        doc = copy.deepcopy(self.record)
        doc["records"][0]["cnf_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "CNF drift"):
            pilot.validate_record(doc)

    def test_fake_unsat_evidence_not_promoted(self):
        doc = copy.deepcopy(self.record)
        doc["records"][0]["status"] = "externally_verified_new_theorem"
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            pilot.validate_record(doc)

    def test_missing_budget_and_conflict_mismatch_refused(self):
        doc = copy.deepcopy(self.record)
        doc["records"][0]["resource_cap_conflicts"] += 1_000_000
        with self.assertRaisesRegex(ValueError, "budget"):
            pilot.validate_record(doc)
        doc = copy.deepcopy(self.record)
        doc["records"][0]["solver_stats"]["conflicts"] = -1
        with self.assertRaisesRegex(ValueError, "counters"):
            pilot.validate_record(doc)

    def test_invented_witness_on_unknown_refused(self):
        doc = copy.deepcopy(self.record)
        doc["records"][0]["witness"] = [{"set": [], "mask": 0}]
        with self.assertRaisesRegex(ValueError, "Uncertified"):
            pilot.validate_record(doc)

    def test_cli_record_validation_has_no_pysat_dependency(self):
        cmd = [sys.executable, "scripts/frankl_triple_experiment.py", "--check-record",
               "data/experiments/frankl_triple7_pilot.json"]
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["unknown"], 2)

    def test_pilot_rejects_wrong_budgets_without_model_calls(self):
        with self.assertRaisesRegex(ValueError, "Conflict limit"):
            pilot.pilot([18], 0)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            pilot.pilot([18, 18], 100)
        with self.assertRaisesRegex(ValueError, "Sizes"):
            pilot.pilot([19], 100)

    def test_result_classifier_never_calls_unsat_a_proof(self):
        self.assertEqual(pilot.classification(None), "unknown_budget_exhausted")
        self.assertEqual(pilot.classification(False), "unsat_solver_report_only")
        self.assertEqual(pilot.classification(True), "sat_verified_witness")


if __name__ == "__main__":
    unittest.main()
