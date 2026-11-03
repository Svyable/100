"""Adversarial controls for nine-deletion sunflower stability candidate."""
import unittest
from itertools import combinations

from scripts import m076_f43_nine as nine
from scripts import m076_f43_eight as eight
from scripts import m076_f43_stability as base


class NineDeletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = nine.check(second_path=True)

    def test_complete_cover_counts(self):
        self.assertEqual(self.result["distinct_nine_covers"], 878401)
        self.assertEqual(self.result["high_capacity_covers"], 131)
        self.assertEqual(self.result["candidate_support_patterns"], 306)

    def test_distribution(self):
        self.assertEqual(self.result["capacity_distribution"], {
            1: 752354, 2: 115481, 3: 9104,
            4: 1331, 5: 80, 6: 51,
        })

    def test_five_insertion_obstruction(self):
        self.assertEqual(self.result["no_five_literal_search"], {
            "tested_five_subsets": 386,
            "tested_outside_partitions": 1118,
        })
        self.assertEqual(self.result["sharp_max_insertions"], 4)

    def test_ten_disjoint_pairs(self):
        graphs = nine.representative_graphs()
        self.assertEqual(len(graphs), 18)
        for key, edges in graphs.items():
            if key not in nine.SURVIVORS:
                matching = eight.greedy_matching(edges)[:10]
                self.assertEqual(len(matching), 10)
                self.assertEqual((sum(e.bit_count() for e in matching),
                                  len(set(v for e in matching
                                          for v in range(54) if e & (1 << v)))),
                                 (20, 20))

    def test_third_orbit_only_eight_covers(self):
        graphs = nine.representative_graphs()
        third, terminals = nine.branch_nine_covers(graphs[nine.THIRD])
        outside, _ = nine.branch_nine_covers(graphs[eight.OUTSIDE])
        self.assertEqual((len(third), terminals), (8, 8))
        self.assertTrue(third <= outside)

    def test_forged_cover_is_rejected(self):
        graphs = nine.representative_graphs()
        edges = graphs[nine.THIRD]
        covers, _ = nine.branch_nine_covers(edges)
        d = next(iter(covers))
        forged = next((d ^ (1 << i)) | (1 << j)
                      for i in range(54) if d & (1 << i)
                      for j in range(54) if not d & (1 << j)
                      if not eight.is_cover(edges, (d ^ (1 << i)) | (1 << j)))
        self.assertEqual(forged.bit_count(), 9)
        self.assertFalse(eight.is_cover(edges, forged))

    def test_outside_partitions_are_complete(self):
        self.assertEqual(len(list(nine.set_partitions(4))), 15)
        self.assertEqual(len(list(nine.set_partitions(6))), 203)
        self.assertEqual(list(nine.set_partitions(0)), [()])

    def test_literal_orbit_free_replay(self):
        n, normalized = nine.literal_direct_sweep()
        self.assertEqual(n, 630)
        self.assertEqual(normalized, set(sum(nine.candidates(), ())))

    def test_sharp_example_literal(self):
        self.assertEqual(len(nine.NINE_DROP), 9)
        self.assertTrue(nine.literal_sharp_check())
        family = [a for j, a in enumerate(eight.FAMILY)
                  if j not in nine.NINE_DROP]
        family += [base.mask(p) for p in nine.NINE_INSERT]
        self.assertEqual(len(family), 49)
        self.assertEqual(sum(base.sunflower(a, b, c)
                             for a, b, c in combinations(family, 3)), 0)

    def test_added_fifth_fails(self):
        family = [a for j, a in enumerate(eight.FAMILY)
                  if j not in nine.NINE_DROP]
        family += [base.mask(p) for p in nine.NINE_INSERT]
        fifth = base.mask((0, 1, 3, 8))
        self.assertNotIn(fifth, family)
        self.assertFalse(base.verify_family(family + [fifth]))


if __name__ == "__main__":
    unittest.main()
