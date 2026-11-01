import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import transfer


class TransferLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.transfers = transfer.read_json(transfer.TRANSFER_FILE)
        cls.instruments = transfer.read_json(transfer.INSTRUMENT_FILE)

    def fixtures(self):
        return copy.deepcopy(self.transfers), copy.deepcopy(self.instruments)

    def test_current_catalogue_and_pin_integrity(self):
        a, b = transfer.validate(*self.fixtures())
        self.assertEqual(len(a), 7)
        self.assertEqual(len(b), 4)
        self.assertEqual(len({x["result_id"] for x in a.values()}), 7)
        self.assertTrue(all(x["status"] == "author_claim_unreviewed" for x in a.values()))

    def test_author_claim_must_not_be_automatically_promoted(self):
        a, b = self.fixtures()
        a["transfers"][0]["status"] = "resolved"
        with self.assertRaisesRegex(ValueError, "upgraded"):
            transfer.validate(a, b)

    def test_source_url_is_locked_to_specific_upstream_commit(self):
        a, b = self.fixtures()
        a["transfers"][0]["source_url"] = a["transfers"][0]["source_url"].replace(
            a["upstream"]["commit"], "main")
        with self.assertRaisesRegex(ValueError, "Unpinned"):
            transfer.validate(a, b)

    def test_unknown_problem_or_claim_review_fails(self):
        a, b = self.fixtures()
        a["transfers"][0]["problem_ids"] = ["M999"]
        with self.assertRaisesRegex(ValueError, "Unknown problem"):
            transfer.validate(a, b)
        a, b = self.fixtures()
        a["transfers"][0]["claim_review_ids"] = ["M046"]
        with self.assertRaisesRegex(ValueError, "Missing claim review"):
            transfer.validate(a, b)

    def test_missing_paths_and_traversal_fail_closed(self):
        a, b = self.fixtures()
        b["instruments"][0]["sources"][0]["path"] = "../outside"
        with self.assertRaisesRegex(ValueError, "Unsafe path"):
            transfer.validate(a, b)
        a, b = self.fixtures()
        a["transfers"][0]["related_repo_paths"] = ["research/not-here.md"]
        with self.assertRaisesRegex(ValueError, "Missing source"):
            transfer.validate(a, b)

    def test_changed_digest_fails_and_impact_reports_transitive_dependents(self):
        a, b = self.fixtures()
        b["instruments"][0]["sources"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "review and repin"):
            transfer.validate(a, b)
        report = transfer.impact(a, b)
        self.assertEqual(report["digest_drift"], ["research/M074_ELEMENTARY_24_REGULAR.md"])
        self.assertEqual(report["instruments_requiring_review"],
                         ["I-M074-CROSSCUT", "I-M074-IRREGULAR"])

    def test_explicit_dependency_impact_is_transitive(self):
        a, b = self.fixtures()
        report = transfer.impact(a, b, changed=["scripts/ch24_crosscut.py"])
        self.assertEqual(report["instruments_requiring_review"],
                         ["I-M074-CROSSCUT", "I-M074-IRREGULAR"])
        self.assertEqual(report["transfers_requiring_review"], [])

    def test_changing_claim_review_reopens_related_transfers(self):
        a, b = self.fixtures()
        report = transfer.impact(a, b, changed=["data/claim_reviews_2026.json"])
        self.assertEqual(report["transfers_requiring_review"],
                         ["T-OAI-079", "T-OAI-157", "T-OAI-161"])

    def test_upstream_sha_change_reopens_every_transfer(self):
        a, b = self.fixtures()
        report = transfer.impact(a, b, upstream_sha="f" * 40)
        self.assertTrue(report["upstream_commit_changed"])
        self.assertEqual(len(report["transfers_requiring_review"]), 7)
        self.assertEqual(report["instruments_requiring_review"], [])

    def test_unknown_dependency_and_cycle_are_rejected(self):
        a, b = self.fixtures()
        b["instruments"][0]["depends_on"] = ["I-NOTHERE"]
        with self.assertRaisesRegex(ValueError, "Unknown instrument dependency"):
            transfer.validate(a, b)
        a, b = self.fixtures()
        b["instruments"][0]["depends_on"] = ["I-M074-IRREGULAR"]
        with self.assertRaisesRegex(ValueError, "Cycle"):
            transfer.validate(a, b)

    def test_duplicate_result_rejected(self):
        a, b = self.fixtures()
        a["transfers"][1]["result_id"] = a["transfers"][0]["result_id"]
        with self.assertRaisesRegex(ValueError, "Duplicate or malformed"):
            transfer.validate(a, b)

    def test_no_changes_yield_no_review_queue(self):
        report = transfer.impact(*self.fixtures())
        self.assertEqual(report["digest_drift"], [])
        self.assertEqual(report["transfers_requiring_review"], [])
        self.assertEqual(report["instruments_requiring_review"], [])

    def test_cli_check_and_json(self):
        check = subprocess.run([sys.executable, str(ROOT / "scripts" / "transfer.py"), "--check"],
                               cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stderr)
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "transfer.py"), "--json"],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertFalse(json.loads(out.stdout)["math_reviewed_by_validator"])


if __name__ == "__main__":
    unittest.main()
