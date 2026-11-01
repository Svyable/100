"""Exact positive/negative controls for a known Frankl proof boundary."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import frankl_pair_boundary as boundary


class PairBoundaryTests(unittest.TestCase):
    def test_doubleton_is_sharp(self):
        result = boundary.doubleton_certificate(3, [[], [0, 1]], 0, 1)
        self.assertEqual(result["partition"], {
            "neither": 1, "a_only": 0, "b_only": 0, "both": 1,
        })
        self.assertEqual(result["combined_frequency"], 2)
        self.assertEqual(result["family_size"], 2)
        self.assertEqual(result["injection_size"], 1)

    def test_all_three_element_universe_families(self):
        # An independent scan of every set family on [3] (2^8 masks).
        n = 3
        witnessed = 0
        for f in range(1, 1 << (1 << n)):
            members = {s for s in range(1 << n) if f & (1 << s)}
            if any((s | t) not in members for s in members for t in members):
                continue
            family = [[i for i in range(n) if s & (1 << i)] for s in members]
            for a in range(n):
                for b in range(a + 1, n):
                    if ((1 << a) | (1 << b)) not in members:
                        continue
                    cert = boundary.doubleton_certificate(n, family, a, b)
                    witnessed += 1
                    self.assertGreaterEqual(cert["combined_frequency"], len(members))
                    self.assertGreaterEqual(
                        max(cert["frequency_a"], cert["frequency_b"]) * 2,
                        len(members))
        self.assertGreater(witnessed, 0)

    def test_27_set_limit_to_local_triple(self):
        result = boundary.replay(ROOT / "examples/FRANKL_SARVATE_RENAUD.json")
        self.assertEqual(result["family_size"], 27)
        self.assertEqual(result["triple_frequencies"], [13, 13, 13])
        self.assertTrue(result["some_other_element_abundant"])
        self.assertEqual(result["minimum_set_size"], 3)

    def test_refuse_modified_nonclosed_certificate(self):
        data = json.loads(
            (ROOT / "examples/FRANKL_SARVATE_RENAUD.json").read_text())
        data["sets"].remove(list(range(9)))
        with self.assertRaisesRegex(ValueError, "not union-closed"):
            boundary.triple_local_falsifier(data["n"], data["sets"], data["triple"])

    def test_refuse_triple_with_abundant_element(self):
        with self.assertRaisesRegex(ValueError, "does not falsify"):
            boundary.triple_local_falsifier(3, [[0, 1, 2]], [0, 1, 2])

    def test_reject_bad_doubleton_witnesses(self):
        with self.assertRaisesRegex(ValueError, "exact doubleton"):
            boundary.doubleton_certificate(3, [[0, 1, 2]], 0, 1)
        with self.assertRaisesRegex(ValueError, "not union-closed"):
            boundary.doubleton_certificate(3, [[0, 1], [2]], 0, 1)
        with self.assertRaises(ValueError):
            boundary.doubleton_certificate(3, [[0, 1], [0, 1]], 0, 1)


if __name__ == "__main__":
    unittest.main()
