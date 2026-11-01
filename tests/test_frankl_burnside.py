import json
import sys
import unittest
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import frankl_burnside as b
import frankl_canonical as c


class BurnsideFranklTests(unittest.TestCase):
    def test_subset_orbits_are_disjoint_and_preserve_cardinality(self):
        for perm in permutations(range(4)):
            blocks = b.subset_orbits(perm)
            self.assertEqual(
                sorted(s for block in blocks for s in block),
                list(range(1 << 4))
            )
            self.assertTrue(all(len({s.bit_count() for s in block}) == 1
                                for block in blocks))
            self.assertEqual(blocks[0], (15,))

    def test_fixed_family_count_against_independent_n3_bruteforce(self):
        candidates = list(c.full_support_families(3))
        self.assertEqual(len(candidates), 90)
        for perm in permutations(range(3)):
            action = tuple(sum(1 << perm[i] for i in range(3) if subset >> i & 1)
                           for subset in range(8))
            brute = sum(c.relabel_family(f, action) == f for f in candidates)
            self.assertEqual(b.fixed_family_count(perm), brute)

    def test_nontrivial_orbit_inclusion_checks_internal_unions(self):
        # Blocks A={01}, B={12} require their union {012} even if
        # both are included in the same orbit under a symmetry.
        self.assertFalse(b.can_add_orbit(1 << 0, (3, 6)))
        self.assertTrue(b.can_add_orbit((1 << 0) | (1 << 7), (3, 6)))

    def test_burnside_n4_equals_direct_orbit_canonicalization(self):
        report = b.burnside(4)
        self.assertEqual(report["fixed_points_weighted_sum"], 7920)
        self.assertEqual(report["orbit_count"], 330)
        self.assertEqual(
            len(list(c.canonical_representatives(4))),
            report["orbit_count"]
        )

    def test_n5_complete_cycle_type_census_and_pinned_report(self):
        calculated = b.report()
        frozen = json.loads(b.REPORT.read_text(encoding="utf-8"))
        self.assertEqual(calculated, frozen)
        five = calculated["n5"]
        self.assertEqual(five["group_order"], 120)
        self.assertEqual(five["fixed_points_weighted_sum"], 3475200)
        self.assertEqual(five["orbit_count"], 28960)
        self.assertEqual(len(five["classes"]), 7)
        self.assertEqual(sum(x["permutations"] for x in five["classes"]), 120)
        self.assertNotIn("solved", calculated)

    def test_reject_nonpermutations(self):
        for item in ((0, 0, 1), (0, 3, 1), (True, 0), (0,) * 6, [0, 1]):
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    b.checked_permutation(item)
        with self.assertRaises(ValueError):
            b.burnside(6)


if __name__ == "__main__":
    unittest.main()
