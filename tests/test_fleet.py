import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fleet


def item(i, status="runnable"):
    return {
        "id": f"F-M{i:03}", "status": status, "scope_sha256": fleet.digest({"id": i}),
        "kind": "comparator", "problems": [f"M{i:03}"],
        "deliverable": f"Encode target {i}", "acceptance": ["Kernel checks"],
        "boundary": "Only the comparator statement", "falsifier": "wrong instance",
        "claim_title": f"[Claim] F-M{i:03}",
        "existing_claims_url": "https://github.com/Svyable/100/issues?q=claim",
    }


class FleetTests(unittest.TestCase):
    def setUp(self):
        self.items = [item(1), item(2), item(3)]

    def test_deterministic_first_pass_and_shared_claim(self):
        a = fleet.plan(self.items, 8)
        b = fleet.plan(self.items, 8)
        self.assertEqual(a, b)
        self.assertEqual([p["work_id"] for p in a["packets"][:3]], [w["id"] for w in self.items])
        self.assertEqual([p["attempt"] for p in a["packets"]], [0, 0, 0, 1, 1, 1, 2, 2])
        self.assertEqual(a["unique_work_items"], 3)
        self.assertEqual(a["repeated_attempts"], 5)
        self.assertEqual(len({p["experiment_id"] for p in a["packets"]}), 8)
        self.assertEqual(a["mode"], "plan_only")
        self.assertTrue(all(p["execution"] == "not_run" for p in a["packets"]))
        self.assertEqual(a["packets"][0]["claim_title"], a["packets"][3]["claim_title"])

    def test_ten_thousand_possible_but_not_executed(self):
        report = fleet.plan(self.items, 10000)
        self.assertEqual(report["slots"], 10000)
        self.assertEqual(report["maximum_resources"]["model_tokens"], 450000000)
        self.assertEqual(report["maximum_resources"]["tool_calls"], 1200000)
        self.assertEqual(len({p["experiment_id"] for p in report["packets"]}), 10000)

    def test_refuse_blocked_and_stop_range(self):
        rows = self.items + [item(4, "waiting_on_dependencies"), item(5, "externally_blocked")]
        stopped = item(6)
        stopped["id"] = "J-foo-stop_range"
        rows.append(stopped)
        report = fleet.plan(rows, 3)
        self.assertEqual({p["work_id"] for p in report["packets"]}, {w["id"] for w in self.items})

    def test_reject_duplicate_work_and_scope_drift(self):
        with self.assertRaisesRegex(ValueError, "Duplicate runnable"):
            fleet.plan(self.items + [self.items[0]], 4)
        broken = copy.deepcopy(self.items)
        broken[0]["scope_sha256"] = "0"
        with self.assertRaisesRegex(ValueError, "scope digest"):
            fleet.plan(broken, 3)

    def test_budget_and_campaign_enforced(self):
        with self.assertRaisesRegex(ValueError, "aggregate"):
            fleet.plan(self.items, 3, total_caps={"model_tokens": 90000, "tool_calls": 360,
                                                  "elapsed_seconds": 10800})
        for count in [0, -1, 10001, True]:
            with self.assertRaises(ValueError):
                fleet.plan(self.items, count)
        for slug in ["", "NOT-LOWERCASE", "../unsafe"]:
            with self.assertRaises(ValueError):
                fleet.plan(self.items, 2, campaign=slug)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            fleet.plan(self.items, 3, caps={"model_tokens": True, "tool_calls": 1, "elapsed_seconds": 1})

    def row(self, classification="none", status="completed"):
        w = self.items[0]
        return {"protocol": fleet.PROTOCOL,
                "experiment_id": fleet.identity("dry-run-001", w["id"], w["scope_sha256"], 0),
                "work_id": w["id"], "scope_sha256": w["scope_sha256"], "attempt": 0,
                "campaign": "dry-run-001", "status": status, "classification": classification,
                "resources": {"model_tokens": 1000, "tool_calls": 5, "elapsed_seconds": 35},
                "resource_caps": fleet.DEFAULT_CAPS.copy(), "evidence": None}

    def test_empty_ledger_and_valid_no_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "runs.jsonl"
            ledger.write_text("", encoding="utf-8")
            self.assertEqual(fleet.load_runs(ledger), [])
            self.assertEqual(fleet.validate_runs([self.row()]), 1)

    def test_identity_replay_and_usage_fails_closed(self):
        row = self.row()
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            fleet.validate_runs([row, row])
        bad = copy.deepcopy(row)
        bad["experiment_id"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "identity"):
            fleet.validate_runs([bad])
        bad = copy.deepcopy(row)
        bad["resources"]["model_tokens"] = 45001
        with self.assertRaisesRegex(ValueError, "over-budget"):
            fleet.validate_runs([bad])
        bad = copy.deepcopy(row)
        bad["resources"]["model_tokens"] = True
        with self.assertRaisesRegex(ValueError, "resource use"):
            fleet.validate_runs([bad])

    def test_no_novel_result_and_evidence_is_verified_as_path_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("artifact", "check", "scope"):
                (root / name).write_text(name, encoding="utf-8")
            row = self.row("restricted_unreviewed")
            row["evidence"] = {"artifact": "artifact", "checker_log": "check", "scope_audit": "scope"}
            self.assertEqual(fleet.validate_runs([row], root=root), 1)
            bad = copy.deepcopy(row)
            bad["evidence"]["artifact"] = "../artifact"
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                fleet.validate_runs([bad], root=root)
            bad = copy.deepcopy(row)
            bad["classification"] = "externally_reviewed_restricted"
            with self.assertRaisesRegex(ValueError, "classification"):
                fleet.validate_runs([bad], root=root)
            bad = copy.deepcopy(row)
            bad["status"] = "timeout"
            with self.assertRaisesRegex(ValueError, "Incomplete"):
                fleet.validate_runs([bad], root=root)
            bad = copy.deepcopy(row)
            bad["classification"] = "none"
            with self.assertRaisesRegex(ValueError, "No-result"):
                fleet.validate_runs([bad], root=root)


if __name__ == "__main__":
    unittest.main()
