import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import frankl_triple_support as support
import frankl_triple_sat as existing_checker


class TripleMinimumSupportTests(unittest.TestCase):
    def test_six_point_exact_witness_and_independent_checker(self):
        family = support.six_family()
        self.assertEqual(len(family), 19)
        direct = support.check_family(family, 6, (0, 1, 2))
        self.assertEqual(direct["frequencies"], [9, 9, 9, 14, 14, 14])
        self.assertTrue(direct["inclusion_minimal_target"])
        # Pre-existing CNF-independent source checker applies to n=6, too.
        independent = existing_checker.independent_check(family, n=6, size=19)
        self.assertEqual([independent["frequencies"][i] for i in (0, 1, 2)],
                         [9, 9, 9])
        self.assertEqual(sorted(support.published_projection()), family)
        doc = json.loads(support.SIX.read_text(encoding="utf-8"))
        self.assertEqual(sorted(support.mask(x) for x in doc["sets"]), family)

    def test_all_families_with_triple_and_empty_on_up_to_five_points(self):
        for n, expected in ((3, 45), (4, 1575), (5, 710830)):
            with self.subTest(n=n):
                result = support.closure_descending_count(n)
                self.assertEqual(result["families_with_empty_and_triple"], expected)
                self.assertEqual(result["triple_rare"], 0)
                if n <= 4:
                    self.assertEqual(support.direct_count(n), (expected, 0))

    def test_cloning_yields_nineteen_member_witness_for_any_target_size(self):
        for k in (3, 4, 5, 8):
            with self.subTest(k=k):
                witness = support.check_family(support.lifted_family(k), k + 3, range(k))
                self.assertEqual(witness["members"], 19)
                self.assertEqual(witness["frequencies"], [9] * k + [14] * 3)
                self.assertTrue(witness["inclusion_minimal_target"])

    def test_adversarial_corruptions_fail(self):
        members = support.six_family()
        with self.assertRaisesRegex(ValueError, "Not union-closed"):
            support.check_family([x for x in members if x != 63], 6, (0, 1, 2))
        with self.assertRaisesRegex(ValueError, "duplicated"):
            support.check_family(members + [members[0]], 6, (0, 1, 2))
        with self.assertRaisesRegex(ValueError, "exact target"):
            support.check_family([x for x in members if x != 7], 6, (0, 1, 2))
        with self.assertRaisesRegex(ValueError, "rare"):
            support.check_family([0, 7], 3, (0, 1, 2))
        with self.assertRaisesRegex(ValueError, "range"):
            support.closure_descending_count(6)

    def test_construction_requires_nontrivial_target(self):
        with self.assertRaisesRegex(ValueError, "k must be"):
            support.lifted_family(2)
        with self.assertRaisesRegex(ValueError, "k must be"):
            support.lifted_family(True)


if __name__ == "__main__":
    unittest.main()
