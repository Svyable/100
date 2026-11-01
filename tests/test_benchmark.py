import copy
import json
import tempfile
import sys
import unittest
from pathlib import Path

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
                "artifact": "docs/BENCHMARK.md",
                "checker_log": "scripts/benchmark.py",
                "scope_audit": "data/benchmark_prereg.json",
                "independent_review_urls": [],
            },
        }

    def test_manifest_is_preregistered_and_no_results_exist(self):
        self.assertEqual(benchmark.load_runs(), [])
        self.assertEqual([t["class"] for t in self.doc["tasks"]],
                         ["replay", "structural", "dependency"])
        report = benchmark.summarize(self.doc, [])
        self.assertEqual(report["expected_trials"], 36)
        self.assertEqual(report["missing_trials"], 36)
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
