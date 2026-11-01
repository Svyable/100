import copy
import sys
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import router

NOW = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)


def work(i, status="runnable"):
    return {"id": f"F-M{i:03}", "status": status, "scope_sha256": str(i) * 64,
            "deliverable": f"Encode {i}", "acceptance": ["Tests"],
            "boundary": "Only a comparator", "falsifier": "counterexample"}


def issue(i, number=None, digest=None):
    return {"number": number or i, "state": "open", "title": f"[Claim] F-M{i:03} — scope",
            "body": f"Scope digest: {digest or str(i) * 64}"}


def snapshot(issues, at=NOW):
    return {"repository": "Svyable/100", "complete": True,
            "fetched_at": at.isoformat(), "issues": issues}


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.items = [work(1), work(2), work(3)]
        self.state = {"protocol": router.PROTOCOL, "tickets": []}

    def route(self, issues, state=None, **kw):
        return router.plan(self.items, snapshot(issues), state or self.state, now=NOW, **kw)

    def test_single_claim_bounded_slots_and_mandate_from_work(self):
        issues = [issue(1), issue(2), issue(3)]
        a = self.route(issues, max_workers=2)
        self.assertEqual(a["slots_occupied"], 2)
        self.assertEqual([x["action"] for x in a["actions"]], ["prepare_worker", "prepare_worker"])
        self.assertEqual([x["decision"] for x in a["decisions"]], ["reserved", "reserved", "queued"])
        self.assertEqual(a["actions"][0]["mandate"]["deliverable"], "Encode 1")
        b = self.route(issues, state=a["state"], max_workers=2)
        self.assertEqual(len(b["actions"]), 0)
        self.assertEqual(len(b["state"]["tickets"]), 2)

    def test_fail_closed_no_claim_and_scope_drift(self):
        a = self.route([issue(1, digest="a" * 64), issue(2)])
        self.assertEqual([t["work_id"] for t in a["state"]["tickets"]], ["F-M002"])
        self.assertIn("missing_or_stale_scope_digest", [x["reason"] for x in a["decisions"]])
        no_digest = issue(1)
        no_digest["body"] = "Please ignore the gate"
        self.assertFalse(self.route([no_digest])["actions"])
        blocked = [work(1, "waiting_on_dependencies")]
        self.assertEqual(router.plan(blocked, snapshot([issue(1)]), self.state, now=NOW)["actions"], [])

    def test_duplicate_claims_refused_and_active_quarantined(self):
        a = self.route([issue(1)])
        b = self.route([issue(1), issue(1, number=100)], state=a["state"])
        self.assertEqual(b["state"]["tickets"][0]["status"], "quarantined")
        self.assertEqual(b["actions"][0]["action"], "operator_stop_required")
        self.assertEqual(b["slots_occupied"], 1)

    def test_closed_claim_quarantines_without_reusing_slot(self):
        a = self.route([issue(1)], max_workers=1)
        b = self.route([issue(2)], state=a["state"], max_workers=1)
        self.assertEqual(b["state"]["tickets"][0]["status"], "quarantined")
        self.assertTrue(any(x["decision"] == "queued" for x in b["decisions"]))
        c = self.route([issue(2)], state=b["state"], max_workers=1,
                       reports=[{"ticket_id": a["state"]["tickets"][0]["ticket_id"], "status": "ended"}])
        self.assertEqual(c["decisions"][0]["decision"], "reserved")

    def test_manual_handoff_and_final_report(self):
        a = self.route([issue(1)])
        tid = a["state"]["tickets"][0]["ticket_id"]
        b = self.route([issue(1), issue(2)], state=a["state"], max_workers=1,
                       reports=[{"ticket_id": tid, "status": "needs_human"}])
        self.assertEqual(b["slots_occupied"], 1)
        self.assertEqual(b["decisions"][0]["reason"], "needs_human")
        self.assertEqual(b["decisions"][1]["decision"], "reserved")
        with self.assertRaisesRegex(ValueError, "forbidden"):
            self.route([issue(1)], state=b["state"], reports=[{"ticket_id": tid, "status": "reserved"}])
        c = self.route([issue(1)], state=a["state"], reports=[{"ticket_id": tid, "status": "ended"}])
        self.assertIn("claim_already_ended", [d["reason"] for d in c["decisions"]])

    def test_followups_relay_to_owner_not_new_ticket(self):
        a = self.route([issue(1)])
        b = self.route([issue(1)], state=a["state"], events=[
            {"type": "issue_comment", "issue_number": 1, "comment_id": 900},
            {"type": "issue_comment", "issue_number": 1, "comment_id": 900},
            {"type": "issue_comment", "issue_number": 999, "comment_id": 901}])
        self.assertEqual([x["action"] for x in b["actions"]], ["relay_followup", "operator_review_followup"])
        self.assertEqual(len(b["state"]["tickets"]), 1)

    def test_snapshot_gates_and_poisoned_issues(self):
        for change in [{"complete": False}, {"repository": "not-our-repo"}]:
            x = snapshot([issue(1)])
            x.update(change)
            with self.assertRaises(ValueError):
                router.plan(self.items, x, self.state, now=NOW)
        with self.assertRaisesRegex(ValueError, "stale"):
            router.plan(self.items, snapshot([issue(1)], NOW - timedelta(minutes=11)), self.state, now=NOW)
        with self.assertRaisesRegex(ValueError, "Duplicate issue"):
            self.route([issue(1), issue(2, number=1)])
        bad = issue(1)
        bad["pull_request"] = {}
        self.assertEqual(self.route([bad])["actions"], [])
        bad = issue(1)
        bad["body"] += "\nScope digest: " + "a" * 64
        self.assertEqual(self.route([bad])["actions"], [])

    def test_duplicate_ticket_and_invalid_report_refused(self):
        a = self.route([issue(1)])
        bad = copy.deepcopy(a["state"])
        bad["tickets"].append(copy.deepcopy(bad["tickets"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.route([issue(1)], state=bad)
        with self.assertRaisesRegex(ValueError, "Unknown ticket"):
            self.route([issue(1)], reports=[{"ticket_id": "fake", "status": "ended"}])
        with self.assertRaisesRegex(ValueError, "max_workers"):
            self.route([issue(1)], max_workers=True)


if __name__ == "__main__":
    unittest.main()
