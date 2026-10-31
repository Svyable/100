import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import scale


class ProofExchangeTests(unittest.TestCase):
    def unit(self, id_, targets, anchors=()):
        return {"id": id_, "kind": "shape", "targets": list(targets),
                "verified_anchors": list(anchors), "work": "test",
                "certificate": "independent test", "falsifier": "counterexample"}

    def obligation(self, id_, status="open", deps=()):
        return {"id": id_, "problem_id": "M001", "kind": "lemma",
                "status": status, "depends_on": list(deps), "statement": "statement",
                "prior_art_boundary": "boundary", "falsifier": "falsifier",
                "next_action": "check"}

    def test_marginal_coverage_not_sum_of_overlap(self):
        pool = [self.unit("a", ["M001", "M002", "M003"]),
                self.unit("b", ["M002", "M003"]),
                self.unit("c", ["M004", "M005"])]
        picked = scale.greedy(pool, 2)
        self.assertEqual([p["id"] for p in picked], ["a", "c"])
        self.assertEqual([p["marginal_count"] for p in picked], [3, 2])
        self.assertEqual(picked[-1]["cumulative_count"], 5)

    def test_tie_prefers_more_existing_certified_anchors(self):
        pool = [self.unit("a", ["M001", "M002"]),
                self.unit("b", ["M003", "M004"], ["M003"])]
        self.assertEqual(scale.greedy(pool, 1)[0]["id"], "b")

    def test_empty_budget_and_zero_marginal(self):
        pool = [self.unit("a", ["M001"]), self.unit("b", ["M001"])]
        self.assertEqual(scale.greedy(pool, 0), [])
        self.assertEqual(len(scale.greedy(pool, 30)), 1)
        with self.assertRaises(ValueError):
            scale.greedy(pool, -1)

    def test_external_blocker_never_dispatched(self):
        dag = [self.obligation("a", "blocked"),
               self.obligation("b", "open"),
               self.obligation("c", "blocked", ["a", "b"]),
               self.obligation("d", "open", ["b"])]
        result = {x["id"]: x for x in scale.frontier(dag)}
        self.assertEqual(result["a"]["category"], "externally_blocked")
        self.assertEqual(result["b"]["category"], "runnable")
        self.assertEqual(result["c"]["category"], "waiting_on_dependencies")
        self.assertEqual(result["c"]["unmet"], ["a", "b"])
        self.assertEqual(result["d"]["category"], "waiting_on_dependencies")
        dag[1]["status"] = "discharged"
        result = {x["id"]: x for x in scale.frontier(dag)}
        self.assertEqual(result["d"]["category"], "runnable")
        self.assertEqual(result["c"]["unmet"], ["a"])

    def test_digest_binds_falsifier_scope_not_transient_rank(self):
        a = self.unit("a", ["M001"])
        digest = scale.packet_digest(a)
        self.assertEqual(len(digest), 64)
        a["cumulative_count"] = 999
        self.assertEqual(scale.packet_digest(a), digest)
        a["falsifier"] = "changed"
        self.assertNotEqual(scale.packet_digest(a), digest)

    def test_production_sources_are_parseable_and_all_targets_accounted(self):
        result = scale.report(budget=5)
        self.assertEqual(result["problem_count"], 100)
        self.assertEqual(result["method_count"], 30)
        self.assertTrue(0 < result["candidate_targets_touched"] <= 100)
        self.assertLessEqual(len(result["selected_packets"]), 5)
        for p in result["selected_packets"]:
            self.assertTrue(set(p["verified_anchors"]) <= set(p["targets"]))
            self.assertEqual(p["scope_sha256"], scale.packet_digest(p))
        self.assertEqual(sum(result["frontier_counts"].values()), len(result["obligation_frontier"]))


if __name__ == "__main__":
    unittest.main()
