import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import analogues


class StructuralAnaloguesTests(unittest.TestCase):
    def test_ledger_validates(self):
        doc = analogues.validate()
        self.assertGreaterEqual(len(doc["entries"]), 8)
        self.assertIn("M088", {e["problem_id"] for e in doc["entries"]})

    def test_rejects_non_structural(self):
        doc = analogues.load()
        bad = {
            **doc,
            "entries": [
                {
                    "problem_id": "M006",
                    "analogue": "should fail modality gate here",
                    "certificate": "should fail modality gate here",
                    "proposed_engine": "primes",
                    "status": "aspirational",
                }
            ],
        }
        with self.assertRaises(ValueError):
            analogues.validate(bad)


if __name__ == "__main__":
    unittest.main()
