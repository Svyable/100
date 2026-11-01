import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import formal


class TestFormalCatalogue(unittest.TestCase):
    def test_catalogue_validates_and_certificates_replay(self):
        doc = formal.validate()
        self.assertGreaterEqual(len(doc["entries"]), 9)
        self.assertEqual(len(formal.replay()), 6)

    def test_rejects_unknown_problem_and_missing_declaration(self):
        doc = formal.load()
        bad = copy.deepcopy(doc)
        bad["entries"][0]["problem_id"] = "M999"
        with self.assertRaises(formal.FormalError):
            formal.validate(bad)
        bad = copy.deepcopy(doc)
        bad["entries"][0]["statement"] = "NoSuchStatement"
        with self.assertRaises(formal.FormalError):
            formal.validate(bad)
        bad = copy.deepcopy(doc)
        bad["entries"][0]["kernel_checked"] = [{"decl": "missing_theorem", "claim": "x"}]
        with self.assertRaises(formal.FormalError):
            formal.validate(bad)

    def test_forbidden_escape_hatches_are_detected(self):
        for word in ("sorry", "admit", "axiom", "native_decide"):
            self.assertTrue(formal.FORBIDDEN.search(f"theorem t : True := by {word}"))
        self.assertIsNone(formal.FORBIDDEN.search(formal.strip_comments("-- sorry\n/- axiom -/ theorem t : True := trivial")))

    def test_every_entry_is_imported_and_lean_has_no_escape_hatch(self):
        root = (ROOT / "lean" / "Hundred.lean").read_text(encoding="utf-8")
        for path in (ROOT / "lean" / "Hundred").glob("*.lean"):
            self.assertIn(f"import Hundred.{path.stem}", root)
            self.assertIsNone(formal.FORBIDDEN.search(formal.strip_comments(path.read_text(encoding="utf-8"))), path)


if __name__ == "__main__":
    unittest.main()
