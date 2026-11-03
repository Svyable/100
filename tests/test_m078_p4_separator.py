"""Exact independent and adversarial controls for M078's finite P4 separator."""
import copy
import json
import sys
import unittest
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from m078_p4_separator import (
    CERTIFICATE, _fingerprint, card_path4_count, derive, direct_path4_count,
    induced_path4_by_connectivity, induced_path4_by_degrees,
    sharpness_witness, verify,
)
from mines.deck_invariants import _adjacency_degrees, _direct_triangles
from probes.graphs import census


class P4SeparatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(CERTIFICATE.read_text())

    def test_certified_156_graph_census_separates_all_twenty(self):
        self.assertTrue(verify(self.doc))
        self.assertEqual((self.doc["graph_count"], self.doc["base_key_collision_pairs"],
                          self.doc["residual_collision_pairs"]), (156, 20, 0))
        records = self.doc["collision_pairs"]
        self.assertEqual(len(records), 20)
        self.assertEqual(Counter(abs(x["induced_p4_a"] - x["induced_p4_b"])
                                 for x in records), {1: 14, 3: 6})
        self.assertEqual(len({(r["graph_a"], r["graph_b"]) for r in records}), 20)
        self.assertEqual(self.doc["records_sha256"], _fingerprint(records))

    def test_certified_finite_scope_excludes_larger_claims(self):
        keys = defaultdict(list)
        for code in census(6):
            keys[(_adjacency_degrees(6, code), _direct_triangles(6, code))].append(code)
        ambiguous = [group for group in keys.values() if len(group) > 1]
        self.assertEqual(len(ambiguous), 20)
        self.assertEqual(sorted(map(len, ambiguous)), [2] * 20)
        for n in (3, 4, 5):
            keyset = {(_adjacency_degrees(n, code), _direct_triangles(n, code))
                      for code in census(n)}
            self.assertEqual(len(keyset), len(census(n)))

    def test_adversarial_star_is_not_an_induced_path(self):
        # Star K1,3: connected and three edges, but wrong degree pattern.
        star = [0b1110, 0b0001, 0b0001, 0b0001]
        # 0-1-2-3 path, exactly one induced P4.
        path = [0b0010, 0b0101, 0b1010, 0b0100]
        verts = (0, 1, 2, 3)
        for checker in (induced_path4_by_degrees, induced_path4_by_connectivity):
            self.assertFalse(checker(star, verts))
            self.assertTrue(checker(path, verts))

    def test_all_graphs_agree_by_direct_and_card_counting(self):
        for code in census(6):
            self.assertEqual(direct_path4_count(6, code), card_path4_count(6, code))
        for code in census(5):
            self.assertEqual(direct_path4_count(5, code), card_path4_count(5, code))
        with self.assertRaises(ValueError):
            card_path4_count(4, 0)

    def test_explicit_seven_vertex_obstruction_and_isolate_lifts(self):
        pinned = self.doc["sharpness_witness_n7"]
        self.assertEqual(pinned["order"], 7)
        self.assertEqual(pinned["common_sorted_degrees"], [1, 1, 1, 2, 2, 2, 3])
        self.assertEqual(pinned["common_triangles"], 1)
        self.assertEqual(pinned["common_induced_p4"], 0)
        for t in (0, 1, 2):
            witness = sharpness_witness(t)
            self.assertEqual(witness["order"], 7 + t)
            self.assertEqual(witness["common_sorted_degrees"],
                             [0] * t + [1, 1, 1, 2, 2, 2, 3])
            for item in (witness["first"], witness["second"]):
                self.assertEqual(direct_path4_count(7+t, item["edge_code"]), 0)
                self.assertEqual(card_path4_count(7+t, item["edge_code"]), 0)
        with self.assertRaises(ValueError):
            sharpness_witness(-1)
        with self.assertRaises(ValueError):
            sharpness_witness(True)

    def test_mutations_fail_closed(self):
        damaged = copy.deepcopy(self.doc)
        damaged["collision_pairs"][0]["induced_p4_a"] += 1
        with self.assertRaises(ValueError):
            verify(damaged)
        damaged = copy.deepcopy(self.doc)
        damaged["records_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            verify(damaged)
        damaged = copy.deepcopy(self.doc)
        damaged["graph_count"] = 155
        with self.assertRaises(ValueError):
            verify(damaged)

    def test_certificate_is_exact_deterministic_generated_output(self):
        self.assertEqual(self.doc, derive())
        self.assertEqual(CERTIFICATE.read_text(), json.dumps(derive(), indent=2,
                                                            ensure_ascii=False) + "\n")


if __name__ == "__main__":
    unittest.main()
