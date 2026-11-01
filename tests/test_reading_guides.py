import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site
import sitegen

FILES = build_site.site_files()


class TestReadingGuides(unittest.TestCase):
    def test_all_problem_pages_label_the_evidence_boundary(self):
        for pid in (f"M{i:03d}" for i in range(1, 101)):
            html = FILES[f"problems/{pid}/index.html"]
            self.assertIn('id="evidence-map"', html, pid)
            self.assertIn("This project records no accepted full solution", html, pid)
            self.assertIn("THE QUESTION UNDER STUDY", html, pid)
            self.assertIn('id="related"', html, pid)

    def test_three_annotated_guides_and_homepage_entrypoints(self):
        index = FILES["index.html"]
        for pid in ("M071", "M074", "M075"):
            html = FILES[f"problems/{pid}/index.html"]
            for excerpt in ("Understand the problem", "What a meaningful check would establish",
                            "Editorial explanation", 'id="reading-guide"'):
                self.assertIn(excerpt.lower(), html.lower(), (pid, excerpt))
            self.assertIn(f"problems/{pid}/#reading-guide", index)
        self.assertNotIn('id="reading-guide"', FILES["problems/M001/index.html"])

    def test_method_neighbours_are_labelled_as_similarity_not_implication(self):
        html = FILES["problems/M071/index.html"]
        self.assertIn("Methodological similarity only", html)
        self.assertIn("Canonical representatives", FILES["problems/M075/index.html"])

    def test_curated_data_is_valid_and_exactly_three_entries(self):
        doc = json.loads((ROOT / "data" / "reading_guides.json").read_text(encoding="utf-8"))
        self.assertEqual(doc["version"], 1)
        guides, notice = sitegen.load_reading_guides({f"M{i:03d}" for i in range(1,101)})
        self.assertEqual(set(guides), {"M071", "M074", "M075"})
        self.assertIn("not new mathematical results", notice)
