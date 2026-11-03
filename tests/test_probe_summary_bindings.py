"""Mutation controls: a valid certificate cannot certify a forged verdict or summary.

These are author-side negative controls, not independent mathematical review.
"""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from probes import hadamard, held_karp
from probes.core import ProbeFailure, digest


class HadamardSummaryBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params = {"limit": 24, "williamson_max": 0}
        cls.valid = hadamard.search(cls.params)
        hadamard.check(cls.params, cls.valid)

    def assert_rejects(self, result):
        with self.assertRaises(ProbeFailure):
            hadamard.check(self.params, result)

    def test_rejects_flipped_verdict(self):
        altered = copy.deepcopy(self.valid)
        altered["holds"] = False
        self.assert_rejects(altered)

    def test_rejects_each_unbound_summary_field(self):
        mutations = {
            "limit": lambda s: s.update(limit=self.params["limit"] + 4),
            "constructed_orders": lambda s: s.update(constructed_orders=0),
            "orders_divisible_by_4": lambda s: s.update(orders_divisible_by_4=0),
            "recipes": lambda s: s["recipes"].update({"4": "invented/4"}),
        }
        for name, mutation in mutations.items():
            with self.subTest(field=name):
                altered = copy.deepcopy(self.valid)
                mutation(altered["summary"])
                self.assert_rejects(altered)

    def test_rejects_zero_order_even_with_consistent_hash_and_counts(self):
        altered = copy.deepcopy(self.valid)
        altered["certificate"]["matrices"]["0"] = []
        altered["summary"]["constructed_orders"] += 1
        altered["summary"]["matrices_sha256"] = digest(altered["certificate"]["matrices"])
        altered["summary"]["recipes"]["0"] = "sylvester/0"
        self.assert_rejects(altered)

    def test_rejects_noncanonical_matrix_key(self):
        altered = copy.deepcopy(self.valid)
        altered["certificate"]["matrices"]["04"] = altered["certificate"]["matrices"].pop("4")
        altered["summary"]["matrices_sha256"] = digest(altered["certificate"]["matrices"])
        altered["summary"]["recipes"]["04"] = altered["summary"]["recipes"].pop("4")
        self.assert_rejects(altered)


class HeldKarpSummaryBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params = {"max_n": 3}
        cls.valid = held_karp.search(cls.params)
        held_karp.check(cls.params, cls.valid)

    def assert_rejects(self, result):
        with self.assertRaises(ProbeFailure):
            held_karp.check(self.params, result)

    def test_rejects_flipped_verdict(self):
        altered = copy.deepcopy(self.valid)
        altered["holds"] = not altered["holds"]
        self.assert_rejects(altered)

    def test_rejects_forged_instance_count(self):
        altered = copy.deepcopy(self.valid)
        altered["summary"]["instances"] += 1
        self.assert_rejects(altered)

    def test_rejects_forged_worst_instance(self):
        altered = copy.deepcopy(self.valid)
        altered["summary"]["max_ratio_instance"] = {"n": 3, "graph": -1}
        self.assert_rejects(altered)


if __name__ == "__main__":
    unittest.main()
