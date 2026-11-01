import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import frankl_augmentation as fa
from frankl_canonical import canonical, full_support_families


class TestCanonicalParentCounterexample(unittest.TestCase):
    def test_infinite_family_obstruction_3_4_5(self):
        for n in (3, 4, 5):
            with self.subTest(n=n):
                c = fa.obstruction(n)
                self.assertEqual(c["child_sets"], [1, 2, 3, (1 << n) - 1])
                self.assertEqual(c["deleted_subset"], 1)
                self.assertEqual(c["canonical_child"], canonical(c["canonical_child"], n))
                self.assertLess(c["canonical_parent"], c["deletion_parent"])
                self.assertTrue(fa.is_union_closed(c["deletion_parent"], n))

    def test_stronger_no_minimum_deletion_canonical_parent(self):
        for n in (4, 5):
            with self.subTest(n=n):
                row = fa.stronger_obstruction(n)
                self.assertEqual(row["minimum_cardinality_members"], [6, 9])
                self.assertTrue(fa.lacks_canonical_min_parent(
                    row["canonical_child"], n))
                self.assertTrue(all(c < p for c, p in zip(
                    row["canonical_parent_bitmasks"],
                    row["deletion_parent_bitmasks"])))

    def test_singleton_root_has_no_deletion_parent(self):
        for n in (1, 2, 3, 4):
            with self.assertRaisesRegex(ValueError, "nonroot"):
                fa.deletion_parent(1 << ((1 << n) - 1), n)

    def test_deletion_preserves_union_closure_for_every_n4_family(self):
        n = 4
        for family in full_support_families(n):
            if family.bit_count() <= 1:
                continue
            parent, s = fa.deletion_parent(family, n)
            self.assertFalse(parent & (1 << s))
            self.assertTrue(parent & (1 << ((1 << n) - 1)))
            self.assertTrue(fa.is_union_closed(parent, n))

    def test_invalid_augmented_family_detected(self):
        n = 3
        top = (1 << n) - 1
        invalid = (1 << top) | (1 << 1) | (1 << 2)
        self.assertFalse(fa.is_union_closed(invalid, n))
        # Adding the missing union makes the family union-closed.
        self.assertTrue(fa.is_union_closed(invalid | (1 << 3), n))


class TestOrbitCompleteness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = fa.verify()

    def test_counts_match_known_independent_generators(self):
        for n in range(1, 5):
            with self.subTest(n=n):
                row = self.report["records"][str(n)]
                self.assertEqual(row["per_family_size"], fa.EXPECTED_LEVELS[n])
                self.assertEqual(row["orbit_count"], sum(fa.EXPECTED_LEVELS[n]))
                self.assertEqual(
                    set().union(*fa.orbit_layers(n)),
                    set(fa.canonical_representatives(n)),
                )

    def test_raw_truth_table_matches_without_using_augmentation(self):
        for n in (1, 2, 3):
            with self.subTest(n=n):
                complete = set().union(*fa.orbit_layers(n))
                self.assertEqual(complete, fa.independent_census(n))

    def test_flawed_canonical_parent_filter_has_finite_false_negatives(self):
        for n in (3, 4):
            with self.subTest(n=n):
                flawed = fa.orbit_layers(n, naive_parent_test=True)
                self.assertEqual([len(x) for x in flawed], fa.NAIVE_LEVELS[n])
                self.assertLess(sum(map(len, flawed)),
                                sum(map(len, fa.orbit_layers(n))))

    def test_wrong_or_oversized_domain_is_rejected(self):
        for bad in (0, -1, 5, 1.5, True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    fa.orbit_layers(bad)
        with self.assertRaises(ValueError):
            fa.independent_census(4)


if __name__ == "__main__":
    unittest.main()
