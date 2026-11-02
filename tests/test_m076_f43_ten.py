"""Adversarial tests for the sharp ten-deletion restricted candidate."""
import unittest
from itertools import combinations

from scripts import m076_f43_ten as ten
from scripts import m076_f43_nine as nine
from scripts import m076_f43_eight as eight
from scripts import m076_f43_stability as base


class TenDeletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = ten.check()

    def test_complete_ten_cover_scan(self):
        self.assertEqual(self.result["minimal_cover_templates"], 44)
        self.assertEqual(
            self.result["ten_cover_superset_visits_with_multiplicity"],
            10073118)
        self.assertEqual(
            self.result["high_capacity_visits_with_multiplicity"], 18730)
        self.assertEqual(self.result["distinct_high_capacity_ten_covers"], 9841)

    def test_high_capacity_distribution(self):
        self.assertEqual(self.result["high_capacity_distribution"],
                         {5: 6836, 6: 2597, 7: 372, 8: 36})

    def test_no_six_partitions(self):
        self.assertEqual(self.result["six_slot_subsets_checked"], 6209)
        self.assertEqual(self.result["outsider_equality_patterns_checked"], 35971)
        self.assertEqual(self.result["sharp_max_insertions"], 5)

    def test_minimal_cover_sizes(self):
        graphs = nine.representative_graphs()
        expected = {eight.INSIDE: {6: 32},
                    eight.OUTSIDE: {5: 2, 7: 2},
                    nine.THIRD: {9: 8}}
        for key, sizes in expected.items():
            covers = ten.minimal_covers(graphs[key])
            self.assertEqual(
                {s: sum(c.bit_count() == s for c in covers)
                 for s in sizes}, sizes)

    def test_nonminimal_cover_is_not_reported_minimal(self):
        edges = nine.representative_graphs()[eight.INSIDE]
        minimal = ten.minimal_covers(edges)
        s = next(iter(minimal))
        free = next(i for i in range(54) if not s & (1 << i))
        self.assertTrue(eight.is_cover(edges, s | (1 << free)))
        self.assertNotIn(s | (1 << free), minimal)

    def test_eleven_disjoint_pairs_exclude_other_orbits(self):
        graphs = nine.representative_graphs()
        for key, edges in graphs.items():
            if key in nine.SURVIVORS:
                continue
            matching = eight.greedy_matching(edges)[:11]
            self.assertEqual(len(matching), 11)
            self.assertEqual(sum(matching).bit_count(), 22)

    def test_literal_sharp_witness(self):
        self.assertEqual(ten.verify_witness(), (49, 18424))
        self.assertEqual(len(ten.DROP), 10)
        self.assertEqual(len(ten.INSERT), 5)

    def test_one_restored_old_set_breaks_witness(self):
        family = [a for i, a in enumerate(eight.FAMILY)
                  if i not in ten.DROP]
        family += [base.mask(p) for p in ten.INSERT]
        for i in ten.DROP:
            self.assertFalse(base.verify_family(family + [eight.FAMILY[i]]))

    def test_one_more_insertion_breaks_witness(self):
        family = [a for i, a in enumerate(eight.FAMILY)
                  if i not in ten.DROP]
        family += [base.mask(p) for p in ten.INSERT]
        sixth = base.mask((0, 1, 4, 18))
        self.assertNotIn(sixth, family)
        self.assertFalse(base.verify_family(family + [sixth]))

    def test_outsider_partitions(self):
        self.assertEqual(len(list(nine.set_partitions(5))), 52)
        self.assertEqual(len(list(nine.set_partitions(6))), 203)


if __name__ == "__main__":
    unittest.main()
