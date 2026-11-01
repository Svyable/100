import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site
import discovery


class DiscoveryValidation(unittest.TestCase):
    def setUp(self):
        self.data = discovery.load()

    def test_sample_trails_are_sourced_and_safe(self):
        self.assertEqual(len(self.data["trails"]), 4)
        self.assertEqual(sum(len(t["nodes"]) for t in self.data["trails"]), 13)
        for trail in self.data["trails"]:
            self.assertTrue(all(node["sources"] for node in trail["nodes"]))
            self.assertFalse(any(node["status"] in ("verified", "solved", "accepted")
                                 for node in trail["nodes"]))

    def test_rejects_missing_source(self):
        data = copy.deepcopy(self.data)
        data["trails"][0]["nodes"][0]["sources"] = ["research/no-such-dossier.md"]
        with self.assertRaisesRegex(ValueError, "Missing discovery source"):
            discovery.validate(data)

    def test_rejects_dependency_to_future_node(self):
        data = copy.deepcopy(self.data)
        data["trails"][0]["nodes"][0]["motivated_by"] = ["canonical-encoding"]
        with self.assertRaisesRegex(ValueError, "dependency"):
            discovery.validate(data)

    def test_rejects_foreign_obligation(self):
        data = copy.deepcopy(self.data)
        data["trails"][0]["nodes"][0]["obligation_id"] = "O-M071-01"
        with self.assertRaisesRegex(ValueError, "Obligation"):
            discovery.validate(data)

    def test_rejects_unwarranted_accepted_state(self):
        data = copy.deepcopy(self.data)
        data["trails"][0]["nodes"][0]["status"] = "accepted"
        with self.assertRaisesRegex(ValueError, "Incomplete discovery"):
            discovery.validate(data)

    def test_site_and_api_preserve_research_boundaries(self):
        files = build_site.site_files()
        self.assertIn("discovery/index.html", files)
        self.assertIn("api/discovery.json", files)
        self.assertIn("Discovery", files["index.html"])
        index = files["discovery/index.html"]
        self.assertIn("Keep the reasoning.", index)
        for trail in self.data["trails"]:
            pid = trail["problem_id"]
            self.assertIn(f"discovery/{pid}/index.html", files)
            self.assertIn(f"api/discovery/{pid}.json", files)
            self.assertIn('id="discovery"', files[f"problems/{pid}/index.html"])
            one = json.loads(files[f"api/problems/{pid}.json"])
            self.assertEqual(one["discovery_trail"]["problem_id"], pid)
            self.assertEqual(one["discovery_url"], f"https://svyable.github.io/100/discovery/{pid}/")
            for n in trail["nodes"]:
                self.assertIn(f'id="step-{pid}-{n["id"]}"',
                              files[f"discovery/{pid}/index.html"])
        self.assertIsNone(json.loads(files["api/problems/M001.json"])["discovery_trail"])
        self.assertEqual(json.loads(files["api/discovery.json"])["version"], 1)


if __name__ == "__main__":
    unittest.main()
