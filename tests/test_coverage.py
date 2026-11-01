"""Independent allocations and anti-overclaiming checks for depth coverage."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import coverage as cov
import scale


def packet(name, kind, targets, leverage=100):
    p = {"id": name, "kind": kind, "problems": targets,
         "status": "runnable", "priority_rank": 1, "leverage": leverage,
         "deliverable": "bounded artifact", "acceptance": ["test"],
         "boundary": "no theorem claim", "roles": {"scout": "inspect"}}
    p["packet_sha256"] = scale.packet_digest(p)
    return p


class BreadthSelectionTests(unittest.TestCase):
    def test_two_routes_before_third_duplicate_kind(self):
        pool = [packet("alpha", "comparator", ["M001", "M002"], 300),
                packet("beta", "comparator", ["M001"], 500),
                packet("gamma", "status_audit", ["M001", "M002"], 1),
                packet("delta", "job", ["M003"], 1)]
        chosen = cov.choose_breadth_first(pool, 3)
        self.assertEqual([p["id"] for p in chosen], ["alpha", "delta", "gamma"])

    def test_permutation_invariant_and_nonmutation(self):
        pool = [packet("a", "job", ["M001", "M002"]),
                packet("b", "comparator", ["M001"]),
                packet("c", "status_audit", ["M002"])]
        original = copy.deepcopy(pool)
        forward = cov.choose_breadth_first(pool, 3)
        backwards = cov.choose_breadth_first(list(reversed(pool)), 3)
        self.assertEqual([p["id"] for p in forward],
                         [p["id"] for p in backwards])
        self.assertEqual(original, pool)

    def test_refuses_invalid_or_tampered_inputs(self):
        p = packet("a", "job", ["M001"])
        bad = [dict(p, status="waiting_on_dependencies"),
               dict(p, status="externally_blocked"),
               dict(p, problems=[]),
               dict(p, problems=["M001", "M001"]),
               dict(p, packet_sha256="0"*64)]
        for item in bad:
            with self.subTest(item=item), self.assertRaises(ValueError):
                cov.choose_breadth_first([item], 1)
        with self.assertRaises(ValueError):
            cov.choose_breadth_first([p, p], 2)
        for budget in (-1, 2.0, True):
            with self.assertRaises(ValueError):
                cov.choose_breadth_first([p], budget)

    def test_empty_schedule_is_valid(self):
        self.assertEqual(cov.choose_breadth_first([], 4), [])
        self.assertEqual(cov.choose_breadth_first([packet("a", "job", ["M001"])], 0), [])


class PortfolioCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = cov.build()

    def test_coverage_depth_real_queue(self):
        d = self.doc
        self.assertEqual(d["schema"], "svyable.coverage-depth.v1")
        self.assertEqual(d["budget_slots"], 200)
        self.assertEqual(d["selected_count"], 200)
        self.assertEqual(d["breadth_first"]["problems_touched"], 100)
        self.assertEqual(d["breadth_first"]["two_distinct_work_kinds"], 100)
        self.assertGreater(d["breadth_first"]["two_distinct_work_kinds"],
                           d["existing_ranked_at_same_budget"]["two_distinct_work_kinds"])
        self.assertEqual(len(d["problem_matrix"]), 100)
        self.assertEqual(len({p["id"] for p in d["selected_packets"]}), 200)
        self.assertTrue(all(p["status"] == "runnable" for p in d["selected_packets"]))
        self.assertTrue(all(p["packet_sha256"] == scale.packet_digest(p)
                            for p in d["selected_packets"]))

    def test_evidence_is_read_only_and_separate_from_routes(self):
        d = self.doc
        rows = d["problem_matrix"]
        self.assertEqual(d["breadth_first"]["exact_probe_targets"],
                         d["existing_ranked_at_same_budget"]["exact_probe_targets"])
        self.assertEqual(d["breadth_first"]["formal_statement_targets"],
                         d["existing_ranked_at_same_budget"]["formal_statement_targets"])
        self.assertEqual(d["breadth_first"]["documented_campaigns"],
                         d["existing_ranked_at_same_budget"]["documented_campaigns"])
        self.assertTrue(all(len(r["planned_work_kinds"]) >= 2 for r in rows))
        self.assertIn("not independently verified", d["evidence_boundary"])
        self.assertNotIn("solved", d["schema"])

    def test_matrix_does_not_infer_evidence_from_planning(self):
        fake = [{"id": "M001", "field": "F", "evidence_state": "needs_review",
                 "checked_on": None, "source_url": None}]
        rows = cov.coverage_matrix(
            [packet("foo", "job", ["M001"]),
             packet("bar", "status_audit", ["M001"])], fake,
            set(), set(), set())
        self.assertEqual(rows[0]["planned_work_kinds"], ["job", "status_audit"])
        self.assertFalse(rows[0]["registry_source_recorded"])
        self.assertFalse(rows[0]["exact_probe_recorded"])
        self.assertFalse(rows[0]["formal_statement_recorded"])

    def test_generated_report_up_to_date(self):
        self.assertEqual((ROOT / "COVERAGE.md").read_text(encoding="utf-8"),
                         cov.render(self.doc))


if __name__ == "__main__":
    unittest.main()
