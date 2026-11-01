"""Human entry points and agent metadata must agree with canonical generated ledgers."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site
import sitegen

FILES = build_site.site_files()


class TestDualAudience(unittest.TestCase):
    def test_no_javascript_entry_points_and_discovery(self):
        home = FILES["index.html"]
        start = FILES["start/index.html"]
        self.assertIn('href="start/"', home)
        self.assertIn('href="start/#people"', home)
        self.assertIn('href="start/#agents"', home)
        self.assertEqual(start.count("<h1"), 1)
        for target in ('id="people"', 'id="review"', 'id="agents"',
                       "api/agent.json", "api/agent/tasks.json", "llms.txt"):
            self.assertIn(target, start)
        for path in ("index.html", "start/index.html", "problems/M071/index.html"):
            self.assertIn('title="100 — agent research contract"', FILES[path])
            self.assertIn('title="100 — machine-readable site guide"', FILES[path])
        self.assertIn(sitegen.SITE_URL + "start/", FILES["sitemap.xml"])

    def test_agent_contract_has_explicit_epistemic_and_temporal_limits(self):
        manifest = json.loads(FILES["api/agent.json"])
        index = json.loads(FILES["api/index.json"])
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["repository"], "https://github.com/Svyable/100")
        self.assertEqual(index["endpoints"]["agent_manifest"], sitegen.SITE_URL + "api/agent.json")
        self.assertIn("GitHub claim availability", manifest["not_live"])
        self.assertIn("finite", manifest["evidence_boundaries"]["finite_probe"])
        self.assertIn("review", manifest["evidence_boundaries"]["independent_review"].lower())
        for uri in manifest["endpoints"].values():
            self.assertTrue(uri.startswith(sitegen.SITE_URL), uri)

    def test_tasks_are_only_runnable_real_derived_queue_items(self):
        full = json.loads(FILES["api/work.json"])
        data = json.loads(FILES["api/agent/tasks.json"])
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["task_count"], min(20, full["by_status"]["runnable"]))
        self.assertEqual(data["runnable_in_snapshot"], full["by_status"]["runnable"])
        self.assertIn("unknown", data["live_claim_status"])
        expected = [w for w in full["items"] if w["status"] == "runnable"][:20]
        self.assertEqual([w["id"] for w in data["tasks"]], [w["id"] for w in expected])
        for task, item in zip(data["tasks"], expected):
            self.assertEqual(task["scope_sha256"], item["scope_sha256"])
            self.assertEqual(task["acceptance"], item["acceptance"])
            self.assertEqual(task["boundary"], item["boundary"])
            self.assertEqual(task["depends_on"], item["depends_on"])
            self.assertEqual(task["existing_claims_url"], item["existing_claims_url"])
            self.assertEqual(task["open_claim_url"], item["open_claim_url"])
            self.assertEqual(task["task_url"], sitegen.SITE_URL + f"work/{item['id']}/")
            self.assertEqual(task["status"], "runnable")
            self.assertEqual(len(task["scope_sha256"]), 64)

    def test_llms_txt_matches_live_source_snapshot_not_fake_verification(self):
        txt = FILES["llms.txt"]
        agent = json.loads(FILES["api/agent.json"])
        self.assertTrue(txt.startswith("# 100 — Svyable"))
        self.assertIn("NOT a list of 100 independently confirmed unsolved", txt)
        self.assertIn(agent["snapshot_as_of"], txt)
        self.assertIn("api/agent/tasks.json", txt)
        self.assertIn("NOT a live claim-availability check", txt)
        self.assertIn("cannot be self-awarded", txt)

    def test_no_generated_drift(self):
        drift, stale = build_site.check(FILES)
        self.assertEqual(drift, [])
        self.assertEqual(stale, [])
