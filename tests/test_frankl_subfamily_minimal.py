"""Full finite subfamily-search tests with sound positive and negative controls."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import frankl_subfamily_minimal as mincheck


def fixture(name):
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


class InclusionMinimalityTests(unittest.TestCase):
    def test_published_2026_nineteen_set_family_inclusion_minimal(self):
        obj = fixture("FRANKL_VAN_DER_HOUT_ROOS_19.json")
        result = mincheck.search_proper(obj["sets"], obj["triple"])
        self.assertTrue(result["inclusion_minimal"])
        self.assertEqual((result["family_size"], result["closure_clauses"],
                          result["forced_absences"], result["nodes"]),
                         (19, 82, 18, 1516))

    def test_published_1990_twentyseven_set_family_inclusion_minimal(self):
        obj = fixture("FRANKL_SARVATE_RENAUD.json")
        result = mincheck.search_proper(obj["sets"], obj["triple"])
        self.assertTrue(result["inclusion_minimal"])
        self.assertEqual((result["family_size"], result["closure_clauses"],
                          result["forced_absences"], result["nodes"]),
                         (27, 211, 26, 17944))

    def test_augmented_family_is_not_inclusion_minimal(self):
        obj = fixture("FRANKL_SARVATE_RENAUD.json")
        extended = obj["sets"] + [[]]  # Empty set preserves union closure.
        result = mincheck.search_proper(extended, obj["triple"])
        self.assertFalse(result["inclusion_minimal"])
        ids = result["proper_subfamily_indices"]
        self.assertLess(len(ids), len(extended))
        self.assertEqual(len(ids), 19)
        mincheck.check_family([extended[i] for i in ids], obj["triple"])

    def test_refuse_nonclosed_duplicate_and_nonfalsifier(self):
        with self.assertRaises(ValueError):
            mincheck.search_proper([[0], [1]], [0, 1, 2])
        with self.assertRaises(ValueError):
            mincheck.search_proper([[0, 1, 2], [0, 1, 2]], [0, 1, 2])
        with self.assertRaises(ValueError):
            mincheck.search_proper([[0, 1, 2]], [0, 1, 2])
        with self.assertRaises(ValueError):
            mincheck.search_proper([[], [0, 1], [1, 2]], [0, 1, 2])

    def test_2026_example_has_empty_set_and_1990_does_not(self):
        newer = fixture("FRANKL_VAN_DER_HOUT_ROOS_19.json")
        older = fixture("FRANKL_SARVATE_RENAUD.json")
        self.assertIn([], newer["sets"])
        self.assertNotIn([], older["sets"])


if __name__ == "__main__":
    unittest.main()
