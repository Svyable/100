"""Adversarial tests for the exact eight-deletion restricted certificate."""
import unittest
from itertools import combinations

from scripts import m076_f43_eight as eight
from scripts import m076_f43_stability as base


class EightDeletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = eight.check(literal=True)

    def test_complete_counts(self):
        self.assertEqual(self.result["distinct_covers"], 68211)
        self.assertEqual(self.result["overlapping_covers"], 16)
        self.assertEqual(self.result["inside_eight_covers"], 32416)
        self.assertEqual(self.result["outside_eight_covers"], 35811)

    def test_sharp_upper(self):
        self.assertEqual(self.result["sharp_max_insertions"], 4)
        self.assertEqual(self.result["sharp_final_size"], 50)
        self.assertTrue(base.verify_family(eight.sharp_family()))
        self.assertTrue(eight.literal_sharp_check())

    def test_four_pattern_cases(self):
        self.assertIn({"patterns": 4, "upper_insertions": 4, "covers": 20},
                      self.result["distribution"])

    def test_nine_matching_tamper(self):
        reps, _ = base.orbit_representatives()
        key = next(iter(eight.NINE_PAIR_WITNESSES))
        c = base.mask(reps[key])
        pairs = eight.NINE_PAIR_WITNESSES[key]
        self.assertEqual(len({v for edge in pairs for v in edge}), 18)
        self.assertTrue(all(base.sunflower(eight.FAMILY[i], eight.FAMILY[j], c)
                            for i, j in pairs))
        self.assertFalse(base.sunflower(eight.FAMILY[0], eight.FAMILY[0], c))

    def test_forged_deletion_fails(self):
        reps, _ = base.orbit_representatives()
        edges = eight.forbidden_edges(base.mask(reps[eight.INSIDE]))
        covers = eight.product_eight_covers(edges)
        witness = next(iter(covers))
        self.assertTrue(eight.is_cover(edges, witness))
        forged = next((witness ^ (1 << i)) | (1 << j)
                      for i in range(54) if witness & (1 << i)
                      for j in range(54) if not witness & (1 << j)
                      if not eight.is_cover(edges, (witness ^ (1 << i)) | (1 << j)))
        self.assertEqual(forged.bit_count(), 8)
        self.assertFalse(eight.is_cover(edges, forged))

    def test_cover_enumerators_agree(self):
        reps, _ = base.orbit_representatives()
        for key in (eight.INSIDE, eight.OUTSIDE):
            edges = eight.forbidden_edges(base.mask(reps[key]))
            self.assertEqual(eight.product_eight_covers(edges),
                             eight.branch_eight_covers(edges))

    def test_outside_orbits_excluded(self):
        reps, _ = base.orbit_representatives()
        for key, pairs in eight.NINE_PAIR_WITNESSES.items():
            self.assertEqual(len(pairs), 9)
            self.assertTrue(all(base.sunflower(eight.FAMILY[i], eight.FAMILY[j],
                                                base.mask(reps[key]))
                                for i, j in pairs))

    def test_orbit_free_replay(self):
        inside, outside = eight.candidate_catalog()
        n, normalized = eight.literal_direct_sweep()
        self.assertEqual(n, 594)
        self.assertEqual(normalized, set(inside + outside))

    def test_fifth_candidate_rejected(self):
        family = eight.sharp_family()
        fifth = base.mask((0, 1, 3, 8))
        self.assertNotIn(fifth, family)
        self.assertFalse(base.verify_family(family + [fifth]))

    def test_all_19600_triples(self):
        family = eight.sharp_family()
        self.assertEqual(len(family), 50)
        self.assertEqual(sum(base.sunflower(a, b, c)
                             for a, b, c in combinations(family, 3)), 0)


if __name__ == "__main__":
    unittest.main()
