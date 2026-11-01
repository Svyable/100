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
        result = scale.report(budget=5, mode="coverage")
        self.assertEqual(result["problem_count"], 100)
        self.assertEqual(result["method_count"], 30)
        self.assertTrue(0 < result["candidate_targets_touched"] <= 100)
        self.assertLessEqual(len(result["selected_packets"]), 5)
        for p in result["selected_packets"]:
            self.assertTrue(set(p["verified_anchors"]) <= set(p["targets"]))
            self.assertEqual(p["scope_sha256"], scale.packet_digest(p))
        self.assertEqual(sum(result["frontier_counts"].values()), len(result["obligation_frontier"]))


class WaveScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wave = scale.report(budget=100, mode="wave")

    def test_wave_fills_budget_without_stop_range_or_waiting(self):
        self.assertEqual(self.wave["protocol"], scale.PROTOCOL)
        self.assertEqual(self.wave["budget_slots"], 100)
        self.assertEqual(self.wave["slots_filled"], 100)
        self.assertGreaterEqual(self.wave["problems_touched"], 40)
        ids = [p["id"] for p in self.wave["selected_packets"]]
        self.assertEqual(len(ids), len(set(ids)))
        for p in self.wave["selected_packets"]:
            self.assertEqual(p["status"], "runnable")
            self.assertNotIn("stop_range", p["id"])
            self.assertIn("scout", p["roles"])
            self.assertEqual(p["scope_sha256"], scale.packet_digest(p))
            self.assertTrue(p["claim_title"].startswith("[Claim]"))

    def test_external_blocker_not_claimable(self):
        packet_ids = {p["id"] for p in self.wave["selected_packets"]}
        self.assertNotIn("O-M074-01", packet_ids)
        reasons = {item["id"]: item["reason"] for item in self.wave["refused"]}
        self.assertIn("O-M074-01", reasons)
        self.assertIn("externally_blocked", reasons["O-M074-01"])

    def test_wave_prefers_obligations_and_jobs_over_audits(self):
        kinds = self.wave["by_kind"]
        self.assertGreaterEqual(kinds["obligation"], 10)
        self.assertGreaterEqual(kinds["job"], 20)
        # High-leverage families should dominate the first thirty slots.
        head = [p["kind"] for p in self.wave["selected_packets"][:30]]
        self.assertGreaterEqual(sum(k in ("obligation", "lean", "job", "roadmap") for k in head), 25)

    def test_refuses_dominated_range_jobs(self):
        refused_ids = {r["id"] for r in self.wave["refused"]}
        self.assertTrue(any("stop_range" in r["reason"] for r in self.wave["refused"]))
        self.assertTrue(any(i.endswith("-stop_range") or "stop_range" in i for i in refused_ids))

    def test_obligation_frontier_covers_all_campaigns_with_nodes(self):
        self.assertGreaterEqual(self.wave["frontier_counts"]["runnable"], 15)
        self.assertEqual(
            sum(self.wave["frontier_counts"].values()),
            len(self.wave["obligation_frontier"]),
        )

    def test_smaller_budget_is_prefix_by_leverage(self):
        small = scale.report(budget=10, mode="wave")
        self.assertEqual(len(small["selected_packets"]), 10)
        self.assertEqual(
            [p["id"] for p in small["selected_packets"]],
            [p["id"] for p in self.wave["selected_packets"][:10]],
        )


if __name__ == "__main__":
    unittest.main()
