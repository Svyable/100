import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import approach
import research


class ApproachTests(unittest.TestCase):
    def setUp(self):
        self.items, self.program, _ = research.load()
        self.rows = approach.rows(self.items, self.program)
        self.by_id = {row["problem_id"]: row for row in self.rows}

    def test_every_problem_is_ranked_once(self):
        self.assertEqual(len(self.rows), 100)
        self.assertEqual([row["dispatch_rank"] for row in self.rows], list(range(1, 101)))
        self.assertEqual(
            self.rows,
            sorted(self.rows, key=lambda row: (-row["dispatch_score"], row["problem_id"])),
        )
        for row in self.rows:
            self.assertEqual(
                row["dispatch_score"], row["score"] + row["readiness"] + row["action_bonus"])

    def test_work_order_prefers_witnesses_and_refuses_dominated_ranges(self):
        self.assertEqual(self.rows[0]["problem_id"], "M071")
        self.assertEqual(self.by_id["M071"]["action"], "replay_claim_witness")
        self.assertLess(self.by_id["M044"]["dispatch_rank"], self.by_id["M074"]["dispatch_rank"])
        self.assertLess(self.by_id["M074"]["dispatch_rank"], self.by_id["M041"]["dispatch_rank"])
        self.assertEqual(self.by_id["M041"]["action"], "stop_range")
        self.assertTrue(self.by_id["M041"]["next_step"].startswith("Do not"))
        self.assertNotIn("degree 4", self.by_id["M041"]["next_step"].split(":", 1)[0].lower())
        self.assertEqual(self.by_id["M001"]["action"], "stop_range")
        self.assertTrue(self.by_id["M001"]["next_step"].startswith("Do not"))
        self.assertEqual(self.by_id["M002"]["action"], "replay_published")
        self.assertIn("primitive character", self.by_id["M002"]["next_step"])
        self.assertEqual(self.by_id["M088"]["action"], "lock_restriction")
        self.assertTrue(self.by_id["M088"]["next_step"].startswith("Lock"))
        doc = json.loads(approach.SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(self.by_id["M098"]["action"], "specify_shape")
        self.assertEqual(
            self.by_id["M098"]["action_bonus"],
            doc["actions"]["specify_shape"]["bonus"],
        )
        self.assertNotIn("2610.15217", self.by_id["M098"]["next_step"])
        self.assertLess(sum(row["action"] == "stop_range" for row in self.rows), 5)
        self.assertGreater(sum(row["action"] == "specify_shape" for row in self.rows), 50)

    def test_shapes_are_shared_and_claims_use_the_review_text(self):
        reviews = {r["id"]: r for r in json.loads(approach.CLAIMS.read_text(encoding="utf-8"))["reviews"]}
        for pid in ("M044", "M049", "M071", "M073"):
            self.assertEqual(self.by_id[pid]["next_step"], reviews[pid]["next_review"])
        self.assertEqual(self.by_id["M072"]["next_step"], self.by_id["M076"]["next_step"])
        self.assertNotEqual(self.by_id["M072"]["next_step"], self.by_id["M081"]["next_step"])
        covered = {pid for job in approach.jobs(self.rows) for pid in job["problem_ids"]}
        self.assertEqual(covered, {row["problem_id"] for row in self.rows})
        generic = approach.GENERIC
        self.assertNotIn(generic, approach.OUTPUT.read_text(encoding="utf-8"))
        self.assertNotIn(generic, research.QUEUE.read_text(encoding="utf-8"))

    def test_generated_approach_is_fresh(self):
        self.assertEqual(
            approach.OUTPUT.read_text(encoding="utf-8"),
            approach.render(self.items, self.program),
        )

    def test_rules_reject_a_refused_range_that_does_not_say_so(self):
        doc = json.loads(approach.SOURCE.read_text(encoding="utf-8"))
        doc["campaign_actions"]["M041"]["next_step"] = "Enumerate degree-4 maps anyway and call it progress."
        with self.assertRaises(approach.ApproachError):
            approach.rows(self.items, self.program, doc)
        dropped = copy.deepcopy(doc)
        dropped["campaign_actions"]["M041"]["next_step"] = (
            "Do not enumerate degree-4 maps with coefficients in {-1,0,1}."
        )
        dropped["methods"][0]["problems"] = dropped["methods"][0]["problems"][1:]
        with self.assertRaises(approach.ApproachError):
            approach.rows(self.items, self.program, dropped)
        witness = json.loads(approach.SOURCE.read_text(encoding="utf-8"))
        witness["campaign_actions"]["M071"]["action"] = "mine_structure"
        with self.assertRaises(approach.ApproachError):
            approach.rows(self.items, self.program, witness)

    def test_roadmap_cannot_recommend_a_refused_range(self):
        with self.assertRaises(approach.ApproachError):
            approach.assert_roadmap({
                "items": [{
                    "id": "X", "horizon": "now", "title": "Extend the Jacobian census",
                    "outcome": "Search degree 4 on small coefficients.",
                    "problems": ["M041"],
                }]
            })


if __name__ == "__main__":
    unittest.main()
