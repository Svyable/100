"""Guard the 2026 claim-review inventory against scope/status drift.

This checks metadata, not the validity of any mathematical proof.
"""
import json
import unittest
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
IDS = {
    "M014", "M030", "M037", "M038", "M044", "M049", "M054", "M055",
    "M056", "M060", "M071", "M073", "M085", "M098", "M100",
}
SCOPE_RELATIONS = {
    "matches", "matches_with_qualification", "matches_if_consequence_valid",
    "narrower", "different_statement",
}
VALIDATION_STATES = {
    "not_established", "independent_reconstruction_preprint",
    "separate_claim_not_verification", "formal_statement_check_only",
    "formalized_different_statement",
}


def source_url(value):
    parsed = urlparse(value) if isinstance(value, str) else None
    return parsed is not None and parsed.scheme == "https" and bool(parsed.netloc)


class ClaimReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads(
            (ROOT / "data/claim_reviews_2026.json").read_text(encoding="utf-8")
        )
        cls.registry = {
            p["id"]: p for p in json.loads(
                (ROOT / "data/problems.json").read_text(encoding="utf-8")
            )
        }

    def test_exact_issue_3_coverage(self):
        records = self.audit["reviews"]
        self.assertEqual(len(records), 15)
        self.assertEqual({r["id"] for r in records}, IDS)
        self.assertEqual([r["id"] for r in records], sorted(IDS))
        self.assertTrue(IDS <= set(self.registry))

    def test_primary_sources_scope_and_dates(self):
        self.assertEqual(self.audit["schema_version"], 1)
        self.assertEqual(self.audit["reviewed_on"], "2026-10-31")
        for item in self.audit["reviews"]:
            with self.subTest(id=item["id"]):
                self.assertTrue(source_url(item["primary_url"]))
                self.assertLessEqual(
                    date.fromisoformat(item["preprint_date"]),
                    date.fromisoformat(self.audit["reviewed_on"]),
                )
                self.assertIn(item["scope_relation"], SCOPE_RELATIONS)
                self.assertIn(item["independent_validation"], VALIDATION_STATES)
                self.assertTrue(item["claimed_theorem"].strip())
                self.assertTrue(item["scope_note"].strip())
                self.assertTrue(item["known_caveats"].strip())
                self.assertTrue(item["next_review"].strip())
                self.assertTrue(all(source_url(u) for u in item["independent_evidence_urls"]))
                # A bibliography or successful Lean compilation does not resolve a conjecture.
                self.assertNotEqual(self.registry[item["id"]]["evidence_state"], "resolved")

    def test_scope_mismatches_are_not_claimed_as_solutions(self):
        by_id = {row["id"]: row for row in self.audit["reviews"]}
        self.assertEqual(by_id["M098"]["scope_relation"], "different_statement")
        self.assertEqual(by_id["M056"]["scope_relation"], "narrower")
        self.assertEqual(by_id["M038"]["independent_validation"], "independent_reconstruction_preprint")
        self.assertEqual(by_id["M044"]["primary_url"], by_id["M049"]["primary_url"])

    def test_source_revision_and_upstream_formalization_scope(self):
        release = self.audit["source_revision"]
        sha = release["commit"]
        self.assertEqual(release["repository"], "openai/math")
        self.assertEqual(len(sha), 40)
        for item in self.audit["reviews"]:
            with self.subTest(id=item["id"]):
                urls = [item["primary_url"], *item["independent_evidence_urls"]]
                if item.get("formalization_scope_url"):
                    urls.append(item["formalization_scope_url"])
                for url in urls:
                    if "github.com/openai/math/blob/" in url:
                        self.assertIn("/blob/" + sha + "/", url)
                        self.assertNotIn("/blob/main/", url)
        # The later all-dimensional claim is now the review's primary source,
        # but its strict interior range still needs an exact statement match.
        m056 = next(r for r in self.audit["reviews"] if r["id"] == "M056")
        self.assertEqual(m056["preprint_date"], "2026-10-25")
        self.assertEqual(m056["scope_relation"], "narrower")
        self.assertIn("local-smoothing", m056["primary_url"].lower())
        m049 = next(r for r in self.audit["reviews"] if r["id"] == "M049")
        self.assertIn("outside", m049["known_caveats"])

    def test_no_unsupported_solved_archive_entries(self):
        solved = json.loads((ROOT / "data/solved.json").read_text(encoding="utf-8"))
        self.assertFalse(IDS & {row["original_problem_id"] for row in solved})


if __name__ == "__main__":
    unittest.main()
