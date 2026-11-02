"""Adversarial checks for one-step extensions of the pinned ten-deletion witness."""
import unittest
from itertools import combinations

from scripts import m076_f43_eleven as eleven
from scripts.m076_f43_stability import base_family, mask, sunflower


class ElevenWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = eleven.check()

    def test_exact_two_path_classification(self):
        self.assertEqual(self.result['admissible_labeled_pairs_on_23_points'], 22)
        self.assertEqual(self.result['candidate_deletion_pairs_tested'], 387024)
        self.assertEqual(eleven.pair_intersection_scan()[0], eleven.EXPECTED)

    def test_labeled_extension_pattern(self):
        self.assertEqual(len(eleven.EXPECTED), 22)
        self.assertEqual(set(j for j, _ in eleven.EXPECTED), {19, 20, 22, 23})
        self.assertTrue(all(sum(x >= 18 for x in c) == 1
                            for _, c in eleven.EXPECTED))

    def test_independent_literal_witness(self):
        dropped = eleven.TEN_DROP | {19}
        added = [mask(x) for x in eleven.TEN_INSERT] + [mask((3, 6, 8, 18))]
        family = [a for j, a in enumerate(base_family()) if j not in dropped]
        family += added
        self.assertEqual(len(family), 49)
        self.assertEqual(len(set(family)), 49)
        self.assertEqual(sum(sunflower(a, b, c)
                             for a, b, c in combinations(family, 3)), 0)

    def test_ambient_outside_relabeling(self):
        self.assertTrue(eleven.literal_verify(19, (3, 6, 8, 10_000)))
        self.assertTrue(eleven.literal_verify(23, (3, 7, 8, 23_000)))
        self.assertFalse(eleven.literal_verify(19, (5, 6, 8, 23_000)))

    def test_forged_deletion_and_repeated_candidate(self):
        self.assertFalse(eleven.literal_verify(21, (3, 6, 8, 18)))
        self.assertFalse(eleven.literal_verify(19, (3, 6, 8, 8)))
        self.assertFalse(eleven.literal_verify(0, (3, 6, 8, 18)))

    def test_no_extra_old_set_restored(self):
        self.assertFalse(eleven.literal_verify(19, (0, 1, 3, 18)))
        self.assertFalse(eleven.literal_verify(19, (3, 6, 7, 18)))


if __name__ == '__main__':
    unittest.main()
