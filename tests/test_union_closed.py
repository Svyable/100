import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import union_closed


class TestUnionClosed(unittest.TestCase):
    def test_exact_witness(self):
        item = json.loads((ROOT / "examples" / "FRANKL_SMALL.json").read_text())
        self.assertEqual(item["format"], union_closed.FORMAT)
        result = union_closed.verify(item["n"], item["sets"])
        self.assertEqual(result["abundance"], Fraction(1, 2))
        self.assertTrue(result["frankl_holds"])

    def test_invalid_family(self):
        with self.assertRaisesRegex(ValueError, "not union-closed"):
            union_closed.verify(2, [[0], [1]])
        with self.assertRaisesRegex(ValueError, "duplicate set"):
            union_closed.verify(2, [[0], [0]])
        with self.assertRaisesRegex(ValueError, "nonempty set"):
            union_closed.verify(2, [[]])
        with self.assertRaises(ValueError):
            union_closed.verify(2, [[True]])

    def test_exact_enumeration(self):
        for n in (1, 2, 3, 4):
            with self.subTest(n=n):
                total, closed, min_ratio = union_closed.exhaustive(n)
                self.assertEqual(total, 1 << (1 << n))
                self.assertGreater(closed, 0)
                self.assertEqual(min_ratio, Fraction(1, 2))

    def test_refuse_explosive_enumeration(self):
        with self.assertRaises(ValueError):
            union_closed.exhaustive(5)


if __name__ == "__main__":
    unittest.main()
