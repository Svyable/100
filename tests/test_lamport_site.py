"""The Lamport Pages view is a projection, never a second proof-status ledger."""
import json
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site
import proof_obligations
import sitegen


class TestLamportExplorer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / "data/proof_obligations.json").read_text(encoding="utf-8"))
        cls.nodes = proof_obligations.validate(cls.source)
        cls.files = build_site.site_files()
        cls.html = cls.files["lamport/index.html"]
        cls.api = json.loads(cls.files["api/lamport.json"])

    def test_ledger_is_the_single_source_of_truth(self):
        self.assertEqual(self.api["protocol"], "svyable.lamport.v1")
        self.assertEqual(self.api["obligations"], self.nodes)
        self.assertEqual(self.api["count"], len(self.nodes))
        self.assertIn("not proof validity", self.api["meaning"])
        self.assertEqual(self.html.count('class="lamport-node-head"'), len(self.nodes))
        self.assertEqual(self.html.count('class="lamport-audit"'), len(self.nodes))
        self.assertIn('"proof_obligations"', self.files["api/index.json"])
        search = json.loads(self.files["api/search.json"])
        proof_items = [x for x in search if x["k"] == "proof"]
        self.assertEqual(len(proof_items), len(self.nodes))
        self.assertIn("lamport/?problem=M074#audit-O-M074-03",
                      [x["u"] for x in proof_items])

    def test_exact_dependency_edges_are_linked_and_labeled(self):
        for n in self.nodes:
            oid = n["id"]
            self.assertIn('data-obligation="' + oid + '"', self.html)
            self.assertIn('data-depends="' + " ".join(n["depends_on"]) + '"', self.html)
            self.assertIn('id="audit-' + oid + '"', self.html)
            self.assertIn('href="#audit-' + oid + '"', self.html)
            self.assertIn(sitegen.E(n["statement"]), self.html)
            self.assertIn(sitegen.E(n["falsifier"]), self.html)
            for dep in n["depends_on"]:
                self.assertIn('href="#audit-' + dep + '"', self.html)

    def test_statuses_and_certificate_boundary(self):
        from collections import Counter
        counts = Counter(n["status"] for n in self.nodes)
        self.assertEqual(sum(counts.values()), self.api["count"])
        self.assertEqual(self.html.count("No discharge certificate is recorded"), counts["open"] + counts["blocked"])
        self.assertIn("These are ledger states, not independent proof judgments", self.html)
        self.assertIn("identity, not evidence", self.html)
        self.assertNotIn("proved conjecture", self.html.lower())

    def test_navigation_and_progressive_enhancement(self):
        self.assertIn('href="lamport/"', self.files["index.html"])
        self.assertIn('src="../assets/lamport.js"', self.html)
        self.assertIn('id="lamport-controls" hidden', self.html)
        self.assertIn('href="../../lamport/?problem=M074#M074"', self.files["problems/M074/index.html"])
        self.assertIn("Lamport proof map", self.files["work/index.html"])
        self.assertIn('href="lamport.json"', self.files["api/index.html"])
        self.assertIn('id="M074"', self.html)
        self.assertIn('style="--lamport-columns:2;', self.html)

    def test_depth_not_mistaken_for_proof(self):
        nodes = [n for n in self.nodes if n["problem_id"] == "M074"]
        layers = sitegen.lamport_layers(nodes)
        self.assertEqual(layers, {"O-M074-01": 0, "O-M074-02": 0, "O-M074-03": 1})
        self.assertEqual(self.api["count"], len(self.source["obligations"]))

    def test_untrusted_text_html_escaped(self):
        payload = '<img src=x onerror=alert(1)>'
        site = sitegen.Site(build_site.build())
        site.obligations[0]["statement"] = payload
        site.obligations[0]["falsifier"] = payload
        rendered = sitegen.render_lamport(site)
        self.assertNotIn(payload, rendered)
        self.assertIn(sitegen.E(payload), rendered)
        self.assertNotIn("<img ", rendered)


if __name__ == "__main__":
    unittest.main()
