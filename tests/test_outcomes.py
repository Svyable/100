import copy
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import outcomes
import work

BASE = {"version": 1, "resource_unit": "agent_hour", "outcomes": []}
REC = {"work_id": "F-M079", "scope_sha256": "0123456789abcdef", "author": "agent-a",
       "outcome": "merged_pending_review", "claim_url": "https://github.com/Svyable/100/issues/1",
       "pr_url": "https://github.com/Svyable/100/pull/2", "claimed_on": "2026-11-01",
       "closed_on": "2026-11-02", "resources": {"agent_hours": 2.0, "ci_minutes": 5}}


def ledger(*records):
    doc = copy.deepcopy(BASE)
    doc["outcomes"] = [copy.deepcopy(r) for r in records]
    return doc


def accepted(**over):
    rec = dict(REC, outcome="accepted_independent", reviewer="human-b",
               review_url="https://github.com/Svyable/100/pull/3#review")
    rec.update(over)
    return rec


class TestValidation(unittest.TestCase):
    def test_committed_ledger_is_valid_and_report_current(self):
        outcomes.load()
        self.assertEqual((ROOT / "YIELD.md").read_text(encoding="utf-8"), outcomes.render())

    def test_accepted_requires_independent_named_reviewer_and_link(self):
        outcomes.validate(ledger(accepted()))
        for bad in (accepted(reviewer="agent-a"), accepted(reviewer="AGENT-A"), accepted(reviewer=""),
                    accepted(review_url=None)):
            with self.assertRaises(outcomes.OutcomeError):
                outcomes.validate(ledger(bad))

    def test_reviewer_only_on_accepted(self):
        with self.assertRaises(outcomes.OutcomeError):
            outcomes.validate(ledger(dict(REC, reviewer="human-b")))

    def test_rejects_malformed_records(self):
        for bad in (dict(REC, work_id="whatever"), dict(REC, scope_sha256="xyz"), dict(REC, outcome="solved"),
                    dict(REC, closed_on="2026-10-01"), dict(REC, resources={"agent_hours": -1}),
                    dict(REC, pr_url="http://insecure"), dict(REC, author=" ")):
            with self.subTest(bad=bad), self.assertRaises(outcomes.OutcomeError):
                outcomes.validate(ledger(bad))
        with self.assertRaises(outcomes.OutcomeError):
            outcomes.validate(ledger(REC, REC))


class TestMetrics(unittest.TestCase):
    def test_yield_counts_only_independent_acceptance(self):
        doc = ledger(REC, accepted(work_id="V-L004", scope_sha256="fedcba9876543210",
                                   resources={"agent_hours": 3.0}),
                     dict(REC, work_id="S-M012", scope_sha256="1111111111111111", outcome="gap_reported",
                          resources={"agent_hours": 5.0}))
        m = outcomes.metrics(doc, review_backlog=7)
        self.assertEqual(m["accepted_independent"], 1)
        self.assertEqual(m["agent_hours"], 10.0)
        self.assertEqual(m["accepted_per_10_agent_hours"], 1.0)
        self.assertEqual(m["by_family"]["review"]["accepted"], 1)
        self.assertEqual(m["by_family"]["comparator"]["accepted"], 0)
        self.assertEqual(m["median_days_claim_to_acceptance"], 1)
        self.assertEqual(m["review_backlog_items"], 7)

    def test_empty_ledger_reports_no_rate(self):
        m = outcomes.metrics(ledger(), review_backlog=0)
        self.assertIsNone(m["accepted_per_10_agent_hours"])
        self.assertIn("No outcomes recorded yet", outcomes.render(m))


class TestReviewFamily(unittest.TestCase):
    def test_review_items_track_unaccepted_artifacts(self):
        items = work.build()
        review = {w["id"] for w in items if w["kind"] == "review"}
        lean = {f"V-{t['id']}" for t in json.loads((ROOT / "data/lean_targets.json").read_text())
                if t["stage"] == "implemented"}
        formal = {f"V-F-{e['problem_id']}" for e in json.loads((ROOT / "data/formalization.json").read_text())["entries"]
                  if e["fidelity"] == "author_checked"}
        self.assertTrue(lean | formal <= review)
        for w in items:
            if w["kind"] == "review":
                self.assertTrue(any("not an author" in a for a in w["acceptance"]), w["id"])

    def test_accepted_review_clears_from_queue(self):
        with mock.patch.object(outcomes, "accepted_ids", return_value={"V-L004", "V-F-M006"}):
            ids = {w["id"] for w in work.build()}
        self.assertNotIn("V-L004", ids)
        self.assertNotIn("V-F-M006", ids)
        self.assertIn("V-L005", ids)


if __name__ == "__main__":
    unittest.main()
