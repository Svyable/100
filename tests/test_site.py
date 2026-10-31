import json
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site


class LinksAndIds(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag in ("a", "script", "link"):
            self.links.append(a.get("href", a.get("src")))


class TestPages(unittest.TestCase):
    def test_snapshot_is_current(self):
        expected = build_site.render()
        self.assertEqual(build_site.OUTPUT.read_text(encoding="utf-8"), expected)

    def test_all_100_with_stable_ranks(self):
        doc = json.loads(build_site.OUTPUT.read_text(encoding="utf-8"))
        p = doc["problems"]
        self.assertEqual(len(p), 100)
        self.assertEqual([item["rank"] for item in p], list(range(1, 101)))
        self.assertEqual(len({item["id"] for item in p}), 100)
        self.assertEqual(sum(doc["status_counts"].values()), 100)
        self.assertEqual(sorted(p, key=lambda x: (-x["score"],x["id"])), p)
        self.assertTrue(all(20 <= item["score"] <= 100 for item in p))
        self.assertEqual(sorted(x["execution_rank"] for x in p),list(range(1,101)))
        self.assertTrue(all(x["execution_score"]==x["score"]+x["readiness"] for x in p))
        self.assertEqual(len(doc["execution_queue"]),5)
        self.assertEqual(doc["summary"]["reproduced_known"],3)
        self.assertEqual(doc["summary"]["fully_solved"],0)
        self.assertEqual(doc["solved"],[])
        self.assertEqual(len(doc["milestones"]),3)

    def test_static_pages_assets(self):
        docs = ROOT / "docs"
        for asset in (".nojekyll", "index.html", "assets/app.js",
                      "assets/style.css", "assets/favicon.svg"):
            self.assertTrue((docs / asset).is_file(), asset)
        page = LinksAndIds()
        page.feed((docs / "index.html").read_text(encoding="utf-8"))
        self.assertTrue({"rankings", "campaigns", "method", "problem-list",
                         "results-count", "load-more", "search-problems",
                         "filter-field", "filter-status", "sort-problems",
                         "workbench", "execution-queue", "solved", "solved-list",
                         "stat-solved", "milestone-list", "nav-solved-count"}.issubset(page.ids))
        self.assertIn("./assets/app.js", page.links)
        self.assertIn("./assets/style.css", page.links)
        self.assertIn("./assets/favicon.svg", page.links)
        self.assertIn("./data/portfolio.json",
                      (docs / "assets" / "app.js").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
