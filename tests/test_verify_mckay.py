import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_mckay as mckay


class McKayReplayTests(unittest.TestCase):
    def test_graph6_orientation_and_padded_bits(self):
        # Standard graph6 column-major bit order, not row-major.
        self.assertEqual(mckay.decode_graph6("CG"), [0, 1 << 2, 1 << 1, 0])
        self.assertEqual(mckay.decode_graph6("D~{"),
                         [(1 << 5) - 1 ^ (1 << i) for i in range(5)])
        self.assertEqual(mckay.decode_graph6("D??"), [0] * 5)

    def test_reject_bad_graph6(self):
        bad = ["", "A", "D~", "D~~", "D~~extra", "C\n", "å", b"\xff", b"~~"]
        for item in bad:
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    mckay.decode_graph6(item)

    def test_checker_finds_actual_monochromatic_five(self):
        full = [(1 << 5) - 1 ^ (1 << i) for i in range(5)]
        empty = [0] * 5
        self.assertEqual(mckay.triangle_checker(full),
                         ("red", (0, 1, 2, 3, 4)))
        self.assertEqual(mckay.triangle_checker(empty),
                         ("blue", (0, 1, 2, 3, 4)))
        for graph in (full, empty):
            with self.assertRaisesRegex(ValueError, "monochromatic K5"):
                mckay.independently_check(graph)

    def test_checker_accepts_five_cycle_and_rejects_asymmetry(self):
        cycle = [0] * 5
        for a, b in [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]:
            cycle[a] |= 1 << b
            cycle[b] |= 1 << a
        self.assertIsNone(mckay.triangle_checker(cycle))
        self.assertTrue(mckay.independently_check(cycle))
        cycle[0] ^= 1 << 2
        with self.assertRaisesRegex(ValueError, "asymmetric"):
            mckay.independently_check(cycle)

    def test_first_and_last_published_records(self):
        data = mckay.CATALOG.read_bytes()
        self.assertEqual(len(data), 47888)
        self.assertEqual(hashlib.sha256(data).hexdigest(), mckay.SOURCE_SHA256)
        records = data.splitlines()
        self.assertEqual(len(records), 328)
        for index in (0, len(records) - 1):
            with self.subTest(index=index):
                graph = mckay.decode_graph6(records[index])
                self.assertEqual(len(graph), 42)
                self.assertTrue(mckay.independently_check(graph))

    def test_corrupted_source_is_fail_closed(self):
        data = bytearray(mckay.CATALOG.read_bytes())
        data[1] ^= 1
        with tempfile.TemporaryDirectory() as path:
            suspect = Path(path) / "tampered.g6"
            suspect.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                mckay.replay(suspect)

    def test_frozen_report_matches_full_independent_replay(self):
        expected = json.loads(mckay.REPORT.read_text(encoding="utf-8"))
        actual = mckay.replay()
        self.assertEqual(expected, actual)
        self.assertEqual(actual["witnesses_including_color_swaps"], 656)
        self.assertNotIn("solved", actual)


if __name__ == "__main__":
    unittest.main()
