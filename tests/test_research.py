import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import rank
import research


class ResearchProgramTests(unittest.TestCase):
    def setUp(self):
        self.items,self.program,self.solved=research.load()

    def test_program_has_100_active_and_archive_validated(self):
        self.assertEqual(len(self.items),100)
        self.assertIsInstance(self.solved,list)
        self.assertGreaterEqual(len(self.program["campaigns"]),1)
        self.assertGreaterEqual(len(self.program["milestones"]),1)
        self.assertTrue(all(m["classification"] in research.MILESTONE_CLASSES
                            for m in self.program["milestones"]))
        active={p["id"]:p for p in self.items}
        research.validate_solved(self.solved,active)

    def test_execution_ranks_are_deterministic_and_bounded(self):
        order=research.execution_order(self.items,self.program)
        self.assertEqual(len(order),100)
        self.assertEqual(sorted(v["execution_rank"] for v in order.values()),
                         list(range(1,101)))
        self.assertTrue(all(0<=v["readiness"]<=10 for v in order.values()))
        for p in self.items:
            entry=order[p["id"]]
            self.assertEqual(entry["execution_score"],
                             rank.score(p)+entry["readiness"])
        self.assertGreaterEqual(sum(v["readiness"]>0 for v in order.values()),1)
        for c in self.program["campaigns"]:
            if c["problem_id"] in order and c["stage"] == "benchmark_reproduced":
                self.assertGreaterEqual(order[c["problem_id"]]["readiness"],7)

    def test_rendered_execution_queue_fresh(self):
        self.assertEqual(research.QUEUE.read_text(encoding="utf-8"),
                         research.render_queue(self.items,self.program,self.solved))

    def test_solved_gates_reject_unreviewed_and_active(self):
        active={p["id"]:p for p in self.items}
        sample={
            "original_problem_id":"M999","name":"SYNTHETIC TEST ONLY",
            "full_statement":"All synthetic instances satisfy P",
            "resolution":"proved","proof_url":"https://example.org/proof",
            "accepted_on":"2026-10-31",
            "verification_notes":"This is a synthetic validation record, not a claim of any mathematical discovery or an accepted theorem.",
            "replacement_id":"M001","independent_review_urls":[
                "https://review.example.net/report",
                "https://review.example.edu/report"
            ]
        }
        self.assertEqual(len(research.validate_solved([sample],active)),1)
        with self.assertRaises(ValueError):
            research.validate_solved([dict(sample,original_problem_id="M075")],active)
        with self.assertRaises(ValueError):
            research.validate_solved([dict(sample,independent_review_urls=[])],active)
        with self.assertRaises(ValueError):
            research.validate_solved([dict(sample,independent_review_urls=[
                "https://same.example.com/a","https://same.example.com/b"])],active)
        with self.assertRaises(ValueError):
            research.validate_solved([sample,sample],active)
        with self.assertRaises(ValueError):
            research.validate_solved([dict(sample,proof_url="http://unsafe/proof")],active)

    def test_no_executable_verifier_from_untrusted_registry(self):
        self.assertTrue({
            "python3 scripts/ramsey.py demo",
            "python3 scripts/union_closed.py exhaustive --n 4",
            "python3 scripts/digraph.py exhaustive --n 4",
        }.issubset(set(research.RUNNABLE)))
        for c in self.program["campaigns"]:
            for verifier in research.campaign_verifiers(c):
                self.assertIn(verifier,research.RUNNABLE)

    def test_probes_are_wired_into_campaigns(self):
        broken=copy.deepcopy(self.program)
        broken["campaigns"]=[c for c in broken["campaigns"] if c["problem_id"]!="M094"]
        broken["milestones"]=[m for m in broken["milestones"] if m["problem_id"]!="M094"]
        with self.assertRaises(ValueError):
            research.load(broken)
        extra=copy.deepcopy(self.program)
        for c in extra["campaigns"]:
            if c["problem_id"]=="M095":
                c["additional_verifiers"]=["python3 scripts/evil.py"]
        with self.assertRaises(ValueError):
            research.load(extra)


if __name__=="__main__":
    unittest.main()
