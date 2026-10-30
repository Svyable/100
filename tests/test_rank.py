import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import rank

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.items=json.loads(rank.REGISTRY.read_text(encoding="utf-8"))
    def test_count_and_schema(self):
        self.assertEqual(len(rank.validate(self.items)),100)
    def test_all_scores_within_range(self):
        self.assertTrue(all(20<=rank.score(p)<=100 for p in self.items))
    def test_generated_rank_is_fresh(self):
        self.assertEqual(rank.RANKED.read_text(encoding="utf-8"),rank.render(self.items))
    def test_claims_explicitly_flagged(self):
        self.assertTrue(any(p["evidence_state"]=="claim_needs_review" for p in self.items))
if __name__=="__main__":
    unittest.main()
