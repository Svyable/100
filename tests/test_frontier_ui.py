"""Regression checks for the evidence-scoped, progressive proof-frontier UI."""
import json
import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
API = ROOT / "docs" / "api"


class TestProofFrontier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = json.loads((API / "work.json").read_text(encoding="utf-8"))
        cls.problems = json.loads((API / "problems.json").read_text(encoding="utf-8"))["problems"]
        cls.frontier = (ASSETS / "frontier.js").read_text(encoding="utf-8")
        cls.bootstrap = (ASSETS / "app.js").read_text(encoding="utf-8")

    def test_frontier_uses_canonical_api_and_only_enhances_existing_pages(self):
        self.assertIn('root + "assets/frontier.js"', self.bootstrap)
        self.assertIn('fetchData("api/work.json")', self.frontier)
        self.assertIn('fetchData("api/problems.json")', self.frontier)
        self.assertIn('"api/problems/" + match[1] + ".json"', self.frontier)
        self.assertIn('document.querySelector(".problem-page .problem-main")', self.frontier)
        self.assertIn("problem.prepend(section)", self.frontier)
        self.assertIn("textContent", self.frontier)
        self.assertNotIn("innerHTML", self.frontier)  # untrusted mathematical data is text-only

    def test_every_candidate_has_a_method_and_generated_dossier(self):
        self.assertEqual(len(self.problems), 100)
        for p in self.problems:
            with self.subTest(problem=p["id"]):
                self.assertTrue(p["method_id"])
                self.assertTrue(p["method_title"])
                self.assertTrue((API / "problems" / (p["id"] + ".json")).is_file())
                self.assertTrue((ROOT / "docs" / "problems" / p["id"] / "index.html").is_file())

    def test_workbench_can_distinguish_runnable_blocked_and_dependent_claims(self):
        by_id = {w["id"]: w for w in self.work["items"]}
        obligations = [w for w in self.work["items"] if w["kind"] == "obligation"]
        self.assertTrue(any(w["status"] == "runnable" for w in obligations))
        self.assertTrue(any(w["status"] != "runnable" for w in obligations))
        for w in obligations:
            with self.subTest(work=w["id"]):
                self.assertTrue(w["boundary"])
                self.assertTrue(w["context"])
                self.assertTrue(w["deliverable"])
                self.assertTrue(w["falsifier"])
                self.assertTrue(w["problems"])
                for dependency in w["depends_on"]:
                    if dependency in by_id:
                        self.assertEqual(by_id[dependency]["kind"], "obligation")
                if w["status"] == "runnable":
                    self.assertTrue(w["existing_claims_url"].startswith("https://github.com/"))
        for pid in ("M074", "M075", "M095"):
            self.assertTrue(any(pid in w["problems"] for w in obligations))

    def test_reuse_is_marked_as_methodological_not_a_proof(self):
        self.assertIn("not proved implications", self.frontier)
        self.assertIn("not proved implications between conjectures", self.frontier)
        self.assertIn("method_id === record.method_id", self.frontier)
        self.assertIn("not an established result", self.frontier)
        self.assertIn("independent review", self.frontier)

    @unittest.skipUnless(shutil.which("node"), "Node.js is not available")
    def test_frontier_script_parses(self):
        subprocess.run(["node", "--check", str(ASSETS / "frontier.js")],
                       check=True, capture_output=True, text=True)
        subprocess.run(["node", "--check", str(ASSETS / "app.js")],
                       check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
