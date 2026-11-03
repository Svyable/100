"""Adversarial replay tests for M095's claimed Ramsey lower-bound colourings."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from probes import ramsey_witness
from probes.core import ProbeFailure, digest


class RamseyWitnessIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Small enough for independent, exhaustive subset replay in each test.
        cls.params = {"witnesses": ["paley5", "circ8_1_4", "paley17"]}
        cls.good = ramsey_witness.search(cls.params)
        ramsey_witness.check(cls.params, cls.good)

    def rejected(self, mutate):
        bad = copy.deepcopy(self.good)
        mutate(bad)
        with self.assertRaises(ProbeFailure):
            ramsey_witness.check(self.params, bad)

    def test_untampered_and_reordered_edges_are_valid(self):
        candidate = copy.deepcopy(self.good)
        candidate["certificate"]["paley17"]["edges"].reverse()
        candidate["summary"]["witnesses_sha256"] = digest(candidate["certificate"])
        ramsey_witness.check(self.params, candidate)

    def test_empty_certificate_cannot_pass_vacuously(self):
        self.rejected(lambda r: r.__setitem__("certificate", {}))

    def test_partial_certificate_cannot_drop_weakest_witness(self):
        self.rejected(lambda r: r["certificate"].pop("paley5"))

    def test_extra_certificate_cannot_substitute_for_requested_witness(self):
        self.rejected(lambda r: r["certificate"].__setitem__(
            "unexpected", copy.deepcopy(r["certificate"]["paley5"])))

    def test_request_must_be_nonempty_unique_and_known(self):
        for names in ([], ["paley5", "paley5"], ["not_a_witness"]):
            with self.subTest(names=names), self.assertRaises(ProbeFailure):
                ramsey_witness.check({"witnesses": names}, self.good)

    def test_wrong_vertex_count_is_rejected(self):
        self.rejected(lambda r: r["certificate"]["paley5"].__setitem__("vertices", 6))

    def test_wrong_ramsey_threshold_is_rejected(self):
        self.rejected(lambda r: r["certificate"]["paley5"].__setitem__("s", 4))

    def test_duplicate_edges_are_rejected(self):
        self.rejected(lambda r: r["certificate"]["paley5"]["edges"].append(
            r["certificate"]["paley5"]["edges"][0][:]))

    def test_malformed_edges_are_rejected(self):
        for value in ([2, 1], [0, 5], [True, 2], [0, "2"], [0], [0, 1, 2]):
            with self.subTest(value=value):
                self.rejected(lambda r, v=value:
                              r["certificate"]["paley5"]["edges"].append(v))

    def test_false_certification_flag_is_rejected(self):
        self.rejected(lambda r: r["certificate"]["paley5"].__setitem__("certifies", False))

    def test_fake_clique_count_is_rejected(self):
        self.rejected(lambda r: r["certificate"]["paley5"].__setitem__("clique_number", 1))

    def test_fake_independence_count_is_rejected(self):
        self.rejected(lambda r: r["certificate"]["paley5"].__setitem__(
            "independence_number", 1))

    def test_false_holds_is_rejected(self):
        self.rejected(lambda r: r.__setitem__("holds", False))

    def test_forged_published_lower_bound_is_rejected(self):
        self.rejected(lambda r: r["summary"].__setitem__("paley5", "R(3,3) > 100"))

    def test_stale_digest_is_rejected(self):
        self.rejected(lambda r: r["summary"].__setitem__("witnesses_sha256", "0" * 64))

    def test_mutated_witness_edges_fail_even_with_rehashed_summary(self):
        def mutate(r):
            r["certificate"]["paley5"]["edges"] = []
            r["summary"]["witnesses_sha256"] = digest(r["certificate"])
        self.rejected(mutate)


if __name__ == "__main__":
    unittest.main()
