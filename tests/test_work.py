import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import work
import benchmark


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class TestWorkQueue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = work.snapshot()
        cls.items = cls.doc["items"]
        cls.by_id = {w["id"]: w for w in cls.items}

    def test_ids_unique_and_valid(self):
        self.assertEqual(len(self.by_id), len(self.items))
        problems = {p["id"] for p in _json("data/problems.json")}
        for w in self.items:
            self.assertTrue(set(w["problems"]) <= problems, w["id"])
            self.assertIn(w["kind"], work.FAMILIES)
            self.assertTrue(w["acceptance"] and w["boundary"] and w["deliverable"], w["id"])

    def test_derived_families_track_their_ledgers(self):
        formal = {e["problem_id"] for e in _json("data/formalization.json")["entries"]}
        drafts = {r["id"] for r in _json("data/statement_scope_reviews.json")["reviews"]}
        problems = _json("data/problems.json")
        self.assertEqual({w["problems"][0] for w in self.items if w["kind"] == "comparator"},
                         {p["id"] for p in problems} - formal)
        self.assertEqual({w["problems"][0] for w in self.items if w["kind"] == "status_audit"},
                         {p["id"] for p in problems if p["evidence_state"] not in ("official_open", "verified_open")} - drafts)
        open_obligations = {o["id"] for o in _json("data/proof_obligations.json")["obligations"] if o["status"] != "discharged"}
        self.assertEqual({w["id"] for w in self.items if w["kind"] == "obligation"}, open_obligations)
        self.assertEqual({w["id"] for w in self.items if w["kind"] == "lean"}, {t["id"] for t in _json("data/lean_targets.json")})
        stop_jobs = [w for w in self.items if w["kind"] == "job" and w["id"].endswith("-stop_range")]
        self.assertTrue(stop_jobs)
        for w in stop_jobs:
            self.assertEqual(w["status"], "externally_blocked", w["id"])
            self.assertIn("Refused range extension", w["boundary"])

    def test_verifier_review_packets_are_distinct_and_scoped(self):
        program = _json("data/research_program.json")
        targets = {c["problem_id"] for c in program["campaigns"] if c.get("verifier")}
        packets = {w["problems"][0]: w for w in self.items
                   if w["kind"] == "review" and w["id"].startswith("V-P-")}
        self.assertTrue(set(packets) <= targets)
        for pid, w in packets.items():
            self.assertEqual(w["id"], f"V-P-{pid}")
            self.assertIn("corrupt", w["deliverable"])
            self.assertIn("Reproduction", w["boundary"])

    def test_benchmark_cells_follow_actual_ledger(self):
        doc = benchmark.load_manifest()
        seen = {(r["task_id"], r["arm"], r["seed"]) for r in benchmark.load_runs()}
        expected = {(t["id"], a, seed) for t in doc["tasks"]
                    for a in doc["arms"] for seed in doc["seeds"]} - seen
        queue = {w["id"] for w in self.items if w["kind"] == "benchmark"}
        self.assertEqual(queue, {f"B-{t}-{a}-{seed}" for t, a, seed in expected})
        for w in self.items:
            if w["kind"] == "benchmark":
                self.assertEqual(w["status"], "runnable")
                self.assertIn(benchmark.digest(doc), w["context"])
                self.assertIn("data/benchmark_runs.jsonl", " ".join(w["acceptance"]))
                if w["id"].startswith("B-CH24-IRREGULAR"):
                    self.assertIn("POST-FREEZE PRIOR ART", w["boundary"])

    def test_obligation_dependencies_are_respected(self):
        for w in self.items:
            if w["kind"] == "obligation" and w["status"] == "runnable":
                for dep in w["depends_on"]:
                    self.assertNotIn(dep, self.by_id, f"{w['id']} runnable while {dep} is open")

    def test_runnable_first_then_family_then_dispatch(self):
        order = {k: i for i, k in enumerate(work.FAMILIES)}
        keys = [(work.STATUS_ORDER[w["status"]], order[w["kind"]], w["priority_rank"], w["id"]) for w in self.items]
        self.assertEqual(keys, sorted(keys))

    def test_digest_pins_scope_and_claim_is_deterministic(self):
        w = dict(self.items[0])
        self.assertEqual(work.digest(w), w["scope_sha256"])
        w["deliverable"] += " (widened)"
        self.assertNotEqual(work.digest(w), self.items[0]["scope_sha256"])
        self.assertEqual(self.items[0]["claim_title"], f"[Claim] {self.items[0]['id']} — {self.items[0]['title']}")
        self.assertIn("template=claim.yml", self.items[0]["open_claim_url"])
        self.assertTrue((ROOT / ".github" / "ISSUE_TEMPLATE" / "claim.yml").is_file())

    def test_cli(self):
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "work.py"), "--check"],
                             capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("work items", out.stdout)


class TestRegen(unittest.TestCase):
    def test_lists_generated_outputs(self):
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "regen.py"), "--list"],
                             capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(out.returncode, 0)
        for path in ("RANKED.md", "ATTACK_QUEUE.md", "LAB.md", "APPROACH.md", "ROADMAP.md",
                     "SCALE.md", "docs/data/next.json"):
            self.assertIn(path, out.stdout)

    def test_every_ci_check_is_covered(self):
        import regen
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
        covered = {step[1][0] for step in regen.STEPS}
        for script in ("rank.py", "build_site.py", "next.py", "approach.py", "research.py", "lab.py",
                       "mine.py", "formal.py", "portfolio_triage.py", "scale.py", "verify_claim_witnesses.py",
                       "outcomes.py"):
            self.assertIn(f"scripts/{script}", workflow)
            self.assertIn(script, covered)


if __name__ == "__main__":
    unittest.main()
