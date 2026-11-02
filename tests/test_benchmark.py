import copy
import json
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import benchmark


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.doc = benchmark.load_manifest()

    def run_row(self, task="K42-REPLAY", classification="known_reproduction"):
        return {
            "manifest_sha256": benchmark.digest(self.doc),
            "task_id": task, "arm": "sequential", "seed": 11,
            "status": "completed", "classification": classification,
            "resources": {"model_tokens": 200, "tool_calls": 2, "elapsed_seconds": 10},
            # Synthetic test fixtures only: these are not experiment results.
            "evidence": {
                "artifact": "benchmarks/PROTOCOL.md",
                "checker_log": "scripts/benchmark.py",
                "scope_audit": "data/benchmark_prereg.json",
                "independent_review_urls": [],
            },
        }

    def test_manifest_is_preregistered_and_actual_runs_validate(self):
        observed = benchmark.load_runs()
        benchmark.validate_runs(self.doc, observed)
        self.assertEqual([t["class"] for t in self.doc["tasks"]],
                         ["replay", "structural", "dependency"])
        report = benchmark.summarize(self.doc, [])
        self.assertEqual(report["expected_trials"], 36)
        self.assertEqual(report["missing_trials"], 36)
        live = benchmark.summarize(self.doc, observed)
        self.assertEqual(live["recorded_trials"], len(observed))
        self.assertEqual(live["missing_trials"], 36 - len(observed))
        self.assertFalse(report["comparable"])
        self.assertEqual(report["by_arm"]["proof_exchange"]["reviewed_restricted"], 0)

    def test_independently_checkable_reproduction_does_not_count_novel(self):
        row = self.run_row()
        report = benchmark.summarize(self.doc, [row])
        self.assertEqual(report["by_arm"]["sequential"]["known_reproductions"], 1)
        self.assertEqual(report["by_arm"]["sequential"]["reviewed_restricted"], 0)
        self.assertFalse(report["comparable"])

    def test_replay_cannot_be_launched_as_novel_result(self):
        with self.assertRaisesRegex(ValueError, "known replay"):
            benchmark.validate_runs(
                self.doc, [self.run_row(classification="externally_reviewed_restricted")])

    def test_novel_result_requires_two_separate_review_domains(self):
        row = self.run_row("FRANKL-TRANSFER", "externally_reviewed_restricted")
        with self.assertRaisesRegex(ValueError, "two reviews"):
            benchmark.validate_runs(self.doc, [row])
        row["evidence"]["independent_review_urls"] = [
            "https://one.example.org/a", "https://one.example.org/b",
        ]
        with self.assertRaisesRegex(ValueError, "distinct hosts"):
            benchmark.validate_runs(self.doc, [row])
        row["evidence"]["independent_review_urls"][1] = "https://two.example.net/b"
        benchmark.validate_runs(self.doc, [row])
        # This is deliberately only a shape test, NOT real independent review.

    def test_postfreeze_ch24_exposure_blocks_novelty(self):
        row = self.run_row("CH24-IRREGULAR", "externally_reviewed_restricted")
        row["evidence"]["independent_review_urls"] = [
            "https://independent.example.org/review-one",
            "https://other.example.net/review-two",
        ]
        with self.assertRaisesRegex(ValueError, "contaminated"):
            benchmark.validate_runs(self.doc, [row])
        report = benchmark.summarize(self.doc, [])
        self.assertIn("CH24-IRREGULAR", report["novelty_contaminated_tasks"])
        self.assertFalse(report["comparable"])

    def test_full_trial_coverage_does_not_mean_completed_trials(self):
        # Synthetic records cover every preregistered cell, not observed runs.
        rows = [{
            "manifest_sha256": benchmark.digest(self.doc),
            "task_id": task["id"], "arm": arm, "seed": seed,
            "status": "completed", "classification": "none",
            "resources": {"model_tokens": 200, "tool_calls": 2, "elapsed_seconds": 10},
            "evidence": None,
        } for task in self.doc["tasks"]
          for arm in self.doc["arms"] for seed in self.doc["seeds"]]
        with patch.dict(benchmark.NOVELTY_CONTAMINATED, {}, clear=True):
            all_complete = benchmark.summarize(self.doc, rows)
            self.assertEqual(all_complete["recorded_trials"], 36)
            self.assertTrue(all_complete["all_cells_recorded"])
            self.assertTrue(all_complete["matched_trials_completed"])
            self.assertTrue(all_complete["comparable"])

            # No rows went missing; failure is observational, not coverage.
            rows[0]["status"] = "timeout"
            rows[-1]["status"] = "error"
            interrupted = benchmark.summarize(self.doc, rows)
            self.assertEqual(interrupted["missing_trials"], 0)
            self.assertTrue(interrupted["all_cells_recorded"])
            self.assertEqual(interrupted["completed_trials"], 34)
            self.assertEqual(interrupted["timeout_trials"], 1)
            self.assertEqual(interrupted["error_trials"], 1)
            self.assertFalse(interrupted["matched_trials_completed"])
            self.assertFalse(interrupted["comparable"])
            self.assertEqual(sum(a["timeouts"] for a in interrupted["by_arm"].values()), 1)
            self.assertEqual(sum(a["errors"] for a in interrupted["by_arm"].values()), 1)

            # A missing row is not a successful completed-grid claim either.
            missing = benchmark.summarize(self.doc, rows[:-1])
            self.assertFalse(missing["all_cells_recorded"])
            self.assertFalse(missing["matched_trials_completed"])
            self.assertFalse(missing["comparable"])

        # Post-freeze exposure still blocks comparability in the real design.
        self.assertFalse(benchmark.summarize(self.doc, [
            {**row, "status": "completed"} for row in rows
        ])["comparable"])

    def test_scope_drift_refused(self):
        row = self.run_row()
        row["manifest_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "different preregistered"):
            benchmark.validate_runs(self.doc, [row])

    def test_over_budget_and_boolean_tokens_refused(self):
        row = self.run_row()
        row["resources"]["model_tokens"] = self.doc["resource_caps"]["model_tokens"] + 1
        with self.assertRaisesRegex(ValueError, "over-budget"):
            benchmark.validate_runs(self.doc, [row])
        row["resources"]["model_tokens"] = True
        with self.assertRaisesRegex(ValueError, "over-budget"):
            benchmark.validate_runs(self.doc, [row])

    def test_missing_and_path_traversal_evidence_refused(self):
        row = self.run_row()
        row["evidence"]["checker_log"] = "../other"
        with self.assertRaisesRegex(ValueError, "unsafe"):
            benchmark.validate_runs(self.doc, [row])
        row["evidence"]["checker_log"] = "docs/does-not-exist-benchmark.log"
        with self.assertRaisesRegex(ValueError, "missing"):
            benchmark.validate_runs(self.doc, [row])

    def test_duplicates_and_wrong_seed_refused(self):
        row = self.run_row()
        with self.assertRaisesRegex(ValueError, "duplicated"):
            benchmark.validate_runs(self.doc, [row, copy.deepcopy(row)])
        row["seed"] = 99
        with self.assertRaisesRegex(ValueError, "Unknown"):
            benchmark.validate_runs(self.doc, [row])

    def test_timeout_cannot_claim_scientific_success(self):
        row = self.run_row()
        row["status"] = "timeout"
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            benchmark.validate_runs(self.doc, [row])

    def test_manifest_mutation_rejected(self):
        doc = copy.deepcopy(self.doc)
        doc["tasks"][0]["eligible_for_novelty"] = True
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Known replays"):
                benchmark.load_manifest(path)


if __name__ == "__main__":
    unittest.main()
