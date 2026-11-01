import json
import copy
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import next as reservoir


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.refs = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag in ("a","script","link"):
            self.refs.append(a.get("href", a.get("src")))


class Next100Tests(unittest.TestCase):
    def test_source_and_page_snapshot_match(self):
        self.assertEqual(reservoir.OUTPUT.read_text(encoding="utf-8"), reservoir.render())

    def test_reservoir_is_separate_from_the_fixed_100(self):
        doc = reservoir.build()
        self.assertGreaterEqual(doc["count"], 120)
        self.assertGreaterEqual(len(doc["domains"]), 15)
        self.assertEqual(len(json.loads(reservoir.ACTIVE.read_text(encoding="utf-8"))),100)
        self.assertEqual(doc["available_count"] + doc["promoted_count"],doc["count"])
        self.assertEqual([c["discovery_rank"] for c in doc["candidates"]],
                         list(range(1, doc["count"] + 1)))
        self.assertEqual(doc["candidates"],sorted(doc["candidates"],
                         key=lambda c:(-c["score"], c["id"])))
        self.assertTrue(all(c["evidence_state"]=="unvetted_hypothesis"
                            and len(set(c["spillovers"]))>=2 for c in doc["candidates"]))

    def test_reject_duplicate_candidates_and_bad_promotion(self):
        entries=reservoir.candidates()
        active=reservoir.read(reservoir.ACTIVE)
        self.assertTrue(reservoir.validate(entries,[],active))
        with self.assertRaisesRegex(ValueError,"Duplicate candidate ID"):
            reservoir.validate(entries + [entries[0]],[],active)
        with self.assertRaisesRegex(ValueError,"Promotion"):
            reservoir.validate(entries,[{"next_id":entries[0]["id"],"active_id":"M001"}],active)

    def test_near_duplicate_and_review_queue_guards(self):
        entries = reservoir.candidates()
        near = copy.deepcopy(entries[0])
        near["id"] = "N9001"
        near["title"] += " variation"
        with self.assertRaisesRegex(ValueError, "Near-duplicate"):
            reservoir.validate(entries + [near], [], reservoir.read(reservoir.ACTIVE))
        queue = reservoir.read(reservoir.REVIEW_QUEUE)
        self.assertEqual(len(queue), 12)
        self.assertTrue(reservoir.validate_review_queue(queue, entries))
        invalid = copy.deepcopy(queue)
        invalid[0]["candidate_id"] = "N9999"
        with self.assertRaisesRegex(ValueError, "Unknown or repeated"):
            reservoir.validate_review_queue(invalid, entries)
        self.assertEqual(len(reservoir.similarity_pairs(entries, minimum=0.84)), 0)

    def test_pages_assets_and_links(self):
        docs=ROOT/"docs"
        for p in ("next/index.html","next/app.js","next/next.css","data/next.json"):
            self.assertTrue((docs/p).is_file(),p)
        page=PageLinks()
        page.feed((docs/"next/index.html").read_text(encoding="utf-8"))
        self.assertTrue({"next-search","next-domain","next-stage","next-status",
                         "next-sort","next-list","next-more","next-results",
                         "next-reset","stat-available","stat-domains",
                         "stat-promoted","reservoir","review-queue","next-review-list"}.issubset(page.ids))
        self.assertTrue({"./app.js","./next.css","../assets/style.css"}.issubset(page.refs))
        script=(docs/"next/app.js").read_text(encoding="utf-8")
        self.assertIn("../data/next.json",script)
        home=(docs/"index.html").read_text(encoding="utf-8")
        self.assertIn('href="./next/"',home)


if __name__ == "__main__":
    unittest.main()
