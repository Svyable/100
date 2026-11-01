"""Adversarial controls must fail closed when a scope or witness is corrupted."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import lemma_adversary


class LemmaAdversaryTests(unittest.TestCase):
    def setUp(self):
        self.ledger = json.loads(lemma_adversary.LEDGER.read_text(encoding="utf-8"))

    def test_pinned_controls_and_independent_certificates(self):
        result = lemma_adversary.report(self.ledger)
        self.assertEqual((result["controls"], result["false_auxiliary"],
                          result["known_positive"], result["open_conjectures_resolved"]),
                         (5, 4, 1, 0))
        for item in result["results"]:
            self.assertFalse(item["full_conjecture_resolved"])
        self.assertEqual(result["results"][0]["facts"]["triple_frequencies"], [13]*3)
        self.assertEqual(result["results"][1]["facts"]["all_frequencies"], [9,9,9,14,14,14,17])
        self.assertEqual(result["results"][3]["facts"]["low_to_low"], 2)
        self.assertEqual(result["results"][3]["facts"]["arcs"], 29)

    def test_rejects_semantic_misclassification(self):
        for idx, category in ((0, "known_theorem_positive_control"),
                              (1, "refuted_auxiliary_only"),
                              (3, "solved"),
                              (4, "new_unrestricted_theorem")):
            altered = copy.deepcopy(self.ledger)
            altered["cases"][idx]["classification"] = category
            with self.subTest(idx=idx), self.assertRaises(ValueError):
                lemma_adversary.report(altered)

    def test_rejects_dropped_or_unsupported_evaluators(self):
        missing = copy.deepcopy(self.ledger)
        missing["cases"].pop()
        with self.assertRaises(ValueError):
            lemma_adversary.validate(missing)
        renamed = copy.deepcopy(self.ledger)
        renamed["cases"][0]["evaluator"] = "__import__('os').system('echo test')"
        with self.assertRaises(ValueError):
            lemma_adversary.validate(renamed)

    def test_rejects_changed_expected_fact(self):
        tampered = copy.deepcopy(self.ledger)
        tampered["cases"][0]["expected"]["triple_frequencies"] = [14, 13, 13]
        with self.assertRaises(AssertionError):
            lemma_adversary.report(tampered)

    def test_rejects_modified_graph_witness(self):
        tampered = copy.deepcopy(self.ledger)
        tampered["cases"][3]["out"][0][0] = 0
        with self.assertRaises(ValueError):
            lemma_adversary.report(tampered)

    def test_rejects_bad_path_url_or_problem_id(self):
        for key, value in (("fixture", "../secrets"),
                           ("source", "javascript:alert(1)"),
                           ("problem_id", "M001"),
                           ("id", "A-M074-SOLVED")):
            tampered = copy.deepcopy(self.ledger)
            tampered["cases"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                lemma_adversary.validate(tampered)

    def test_2026_published_nineteen_set_incidence_matrix(self):
        sample = next(c for c in self.ledger["cases"] if c["id"] == "A-M075-TRIPLE19")
        report = lemma_adversary.run_case(sample)
        self.assertEqual(report["facts"]["family_size"], 19)
        self.assertEqual(report["facts"]["triple_frequencies"], [9,9,9])
        self.assertEqual(report["facts"]["all_frequencies"], [9,9,9,14,14,14,17])
        self.assertEqual(report["facts"]["minimum_set_size"], 0)

    def test_independent_oracle_rejects_nonclosed(self):
        with self.assertRaises(ValueError):
            lemma_adversary._independent_family(2, [[0], [1]])
        with self.assertRaises(ValueError):
            lemma_adversary._independent_graph(((1,), (0,)), True)

    def test_pinned_sharp_witness_prevents_unsound_strengthening(self):
        result = lemma_adversary.report(self.ledger)
        nine = result["results"][-1]["facts"]
        self.assertGreater(nine["arcs"], 28)
        self.assertEqual(nine["minimum_outdegree"], 2)


if __name__ == "__main__":
    unittest.main()
