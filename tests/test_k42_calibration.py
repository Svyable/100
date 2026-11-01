import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import benchmark
import k42_calibration as c
import verify_mckay as vm
from ramsey import verify as bitset_verify


class K42CalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recorded = json.loads(c.REPORT.read_text(encoding="utf-8"))
        cls.observed = c.observe()

    def test_frozen_calibration_still_replays(self):
        c.verify_evidence(self.observed, self.recorded)
        self.assertEqual(self.observed["records_checked"], 328)
        self.assertEqual(set(self.observed["independent_checker_passes"]),
                         {"bitset_K5", "triangle_common_neighbor_K5"})
        self.assertFalse(self.observed["trial_credit"])
        self.assertNotIn("arm", self.observed)
        self.assertNotIn("seed", self.observed)

    def test_one_edge_mutation_fails_both_checkers(self):
        graph = vm.decode_graph6(vm.CATALOG.read_bytes().splitlines()[0])
        graph[0] ^= 1 << 2
        graph[2] ^= 1 << 0
        result = bitset_verify(42, vm.to_red_edges(graph), 5, 5)
        hit = vm.triangle_checker(graph)
        self.assertFalse(result[0])
        self.assertEqual(hit[0], "red")

    def test_wrong_manifest_or_source_fingerprint_rejected(self):
        for field in ("manifest_sha256", "catalog_sha256", "source_file_sha256"):
            altered = copy.deepcopy(self.recorded)
            altered[field] = "tampered"
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "drift"):
                c.verify_evidence(self.observed, altered)

    def test_forged_trial_credit_and_checker_passes_rejected(self):
        altered = copy.deepcopy(self.recorded)
        altered["trial_credit"] = True
        with self.assertRaisesRegex(ValueError, "drift"):
            c.verify_evidence(self.observed, altered)
        altered = copy.deepcopy(self.recorded)
        altered["independent_checker_passes"]["bitset_K5"] -= 1
        with self.assertRaisesRegex(ValueError, "drift"):
            c.verify_evidence(self.observed, altered)

    def test_invalid_wall_time_rejected(self):
        for n in (0, -2, True, 3_600_000_000_001):
            altered = copy.deepcopy(self.recorded)
            altered["wall_ns"] = n
            with self.subTest(n=n), self.assertRaisesRegex(ValueError, "Invalid recorded"):
                c.verify_evidence(self.observed, altered)

    def test_checker_times_cannot_exceed_elapsed_time(self):
        altered = copy.deepcopy(self.recorded)
        altered["wall_ns"] = 1
        with self.assertRaisesRegex(ValueError, "Checker time exceeds"):
            c.verify_evidence(self.observed, altered)

    def test_source_sha256_matches_pinned_manifest_and_existing_catalog(self):
        self.assertEqual(self.recorded["manifest_sha256"],
                         benchmark.digest(benchmark.load_manifest()))
        self.assertEqual(self.recorded["catalog_sha256"], vm.SOURCE_SHA256)


if __name__ == "__main__":
    unittest.main()
