"""No mock benchmark trial is ever written by these tests."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pda_trial as pda


class PerceiveDecideActTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.perception = pda.perceive("sequential", 11, "example-model-2026-10")
        cls.decision = pda.decide(cls.perception)

    def test_offline_perception_is_source_bound(self):
        p = self.perception
        self.assertEqual(p["task_id"], "K42-REPLAY")
        self.assertEqual(p["corpus_count"], 328)
        self.assertEqual(p["corpus_sha256"], pda.vm.SOURCE_SHA256)
        self.assertEqual(len(p["candidate_witnesses"]), 4)
        self.assertEqual(self.decision["roles"], ["proposer"])
        self.assertEqual(self.decision["max_output_tokens_per_call"], 1800)
        self.assertIn("not", p["interpretation"].lower())

    def test_frozen_arms_and_role_order(self):
        expected = {
            "sequential": ("proposer",),
            "independent": ("worker_1", "worker_2", "worker_3"),
            "conversation": ("proposer", "critic", "reviser"),
            "proof_exchange": ("scout", "adversary", "checker"),
        }
        self.assertEqual(pda.ROLE_MAP, expected)
        for arm, roles in expected.items():
            with self.subTest(arm=arm):
                p = pda.perceive(arm, 11, "exact-version-1")
                self.assertEqual(tuple(pda.decide(p)["roles"]), roles)
                self.assertEqual(p["manifest_sha256"], self.perception["manifest_sha256"])

    def test_invalid_seed_arm_model_rejected_before_api(self):
        for arm, seed, model in (
            ("not-arm", 11, "x-1"), ("sequential", 14, "x-1"),
            ("sequential", 11, "latest"),
            ("sequential", 11, "version/latest"),
        ):
            with self.subTest(arm=arm, seed=seed, model=model):
                with self.assertRaises(pda.TrialError):
                    pda.perceive(arm, seed, model)

    def test_exact_candidate_accepted_by_both_independent_algorithms(self):
        c = self.perception["candidate_witnesses"][0]
        response = json.dumps({"index": c["index"], "graph6": c["graph6"],
                               "scope": "known_reproduction", "explanation": "replay"})
        checked = pda.check_candidate(response, self.perception)
        self.assertTrue(checked["accepted"])
        self.assertTrue(checked["bitset_K5_free"])
        self.assertTrue(checked["triangle_K5_free"])

    def test_mutation_index_and_scope_drift_rejected(self):
        c = self.perception["candidate_witnesses"][0]
        original = {"index": c["index"], "graph6": c["graph6"],
                    "scope": "known_reproduction"}
        for bad in (
            {**original, "index": 9},
            {**original, "index": 1},
            {**original, "graph6": c["graph6"][:-1] + "!"},
            {**original, "scope": "new_theorem"},
            {**original, "index": True},
        ):
            with self.subTest(bad=repr(bad)[:60]):
                checked = pda.check_candidate(json.dumps(bad), self.perception)
                self.assertFalse(checked["accepted"])
        self.assertFalse(pda.check_candidate("not json", self.perception)["accepted"])

    def test_provider_receipt_and_model_are_strict(self):
        response = {
            "id": "r1", "status": "completed", "model": "pinned-version",
            "usage": {"input_tokens": 21, "output_tokens": 8, "total_tokens": 29},
            "output": [{"type": "message", "content": [
                {"type": "output_text", "text": '{"index": 0}'}
            ]}],
        }
        answer, total = pda.read_provider_response(response, "pinned-version")
        self.assertEqual(answer, '{"index": 0}')
        self.assertEqual(total, 29)
        for mutation in (
            {"usage": None},
            {"usage": {"input_tokens": 21, "output_tokens": 8}},
            {"usage": {"input_tokens": 21, "output_tokens": 8, "total_tokens": 28}},
            {"usage": {"input_tokens": 21, "output_tokens": True, "total_tokens": 22}},
            {"model": "unpinned-version"},
            {"status": "incomplete"},
            {"output": []},
        ):
            with self.subTest(mutation=mutation):
                invalid = {**response, **mutation}
                with self.assertRaises(pda.TrialError):
                    pda.read_provider_response(invalid, "pinned-version")

    def test_earlier_messages_only_shared_in_communicating_arms(self):
        p = self.perception
        base = pda.prompt_for(p, "proposer", [])
        with_prior = pda.prompt_for(p, "critic", [
            {"role": "proposer", "output": '{"scope": "new theorem"}'}
        ])
        self.assertIn("published", base.lower())
        self.assertIn("untrusted", with_prior)
        self.assertIn("new theorem", with_prior)
        self.assertNotIn("Earlier model responses", base)

    def test_no_credential_no_run_no_side_effect(self):
        # Invoke the action directly: no network calls, files or synthetic trial.
        with self.assertRaisesRegex(pda.TrialError, "OPENAI_API_KEY"):
            pda.act(self.perception, self.decision, "")
        self.assertEqual(pda.benchmark.load_runs(), [])

    def test_checker_rejects_incomplete_json_and_does_not_promote_novelty(self):
        self.assertFalse(pda.check_candidate("{}", self.perception)["accepted"])
        self.assertFalse(pda.check_candidate('{"index": 0}', self.perception)["accepted"])
        self.assertEqual(pda.benchmark.load_runs(), [])


if __name__ == "__main__":
    unittest.main()
