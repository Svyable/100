"""Adversarial exact tests for the seven-deletion sunflower neighborhood."""
import unittest
from itertools import combinations

from scripts import m076_f43_stability as base
from scripts import m076_f43_seven as target


class SevenDeletionTests(unittest.TestCase):
    def test_full_certificate_and_literal_replay(self):
        result = target.check(literal=True)
        self.assertEqual(result["max_insertions"], 2)
        self.assertEqual(result["seven_cover_patterns_checked"], 3762)
        self.assertEqual(result["sharp_example_final_size"], 49)

    def test_independent_cover_enumerators_agree(self):
        reps, _ = base.orbit_representatives()
        for key, expected in ((target.INSIDE, 1456), (target.OUTSIDE, 2306)):
            edges = target.forbidden_edges(base.mask(reps[key]))
            a = target.product_seven_covers(edges)
            b = target.branch_seven_covers(edges)
            self.assertEqual(a, b)
            self.assertEqual(len(a), expected)

    def test_outside_and_inside_catalog_exact(self):
        inside, outside = target.candidate_catalog()
        self.assertEqual((len(inside), len(outside)), (162, 108))
        self.assertEqual(len(set(inside + outside)), 270)
        self.assertTrue(all(c not in target.FAMILY for c in inside + outside))

    def test_direct_no_orbit_22_point_sweep(self):
        inside, outside = target.candidate_catalog()
        count, normalized = target.direct_22_sweep()
        self.assertEqual(count, 594)
        self.assertEqual(normalized, set(inside + outside))

    def test_all_sixteen_excluded_orbits_have_eight_disjoint_edges(self):
        reps, _ = base.orbit_representatives()
        for key, points in reps.items():
            if key in (target.INSIDE, target.OUTSIDE):
                continue
            edges = target.forbidden_edges(base.mask(points))
            matching = target.greedy_matching(edges)
            self.assertGreaterEqual(len(matching), 8, key)
            self.assertEqual(sum(matching).bit_count(), 2 * len(matching))

    def test_two_outsiders_impossible_at_seven_deletions(self):
        candidate = base.mask((0, 1, 18, 19))
        edges = target.forbidden_edges(candidate)
        self.assertGreaterEqual(len(target.greedy_matching(edges)), 8)
        self.assertEqual(target.product_seven_covers(edges), set())

    def test_forged_cover_detected(self):
        reps, _ = base.orbit_representatives()
        edges = target.forbidden_edges(base.mask(reps[target.INSIDE]))
        valid = next(iter(target.product_seven_covers(edges)))
        missing = next(e for e in edges if e & valid)
        # Add an impossible new forbidden pair entirely outside a valid cover.
        free = [i for i in range(54) if not valid & (1 << i)]
        forged = (1 << free[0]) | (1 << free[1])
        self.assertNotIn(forged, edges)
        self.assertFalse(target.cover_valid(edges + (forged,), valid))
        self.assertLess(len(target.product_seven_covers(edges + (forged,))),
                        len(target.product_seven_covers(edges)))

    def test_two_insertions_attained_with_seven_deletions(self):
        dropped = target.SHARP_DROP
        kept = [a for i, a in enumerate(target.FAMILY) if i not in dropped]
        new = [base.mask(target.SHARP_TRIPLE + (18,)),
               base.mask(target.SHARP_TRIPLE + (19,))]
        self.assertTrue(base.verify_family(kept + new))
        self.assertEqual(len(kept + new), 49)
        self.assertEqual(sum(1 for _ in combinations(range(49), 3)), 18424)

    def test_three_completions_form_sunflower(self):
        dropped = target.SHARP_DROP
        kept = [a for i, a in enumerate(target.FAMILY) if i not in dropped]
        new = [base.mask(target.SHARP_TRIPLE + (x,)) for x in (18, 19, 20)]
        self.assertFalse(base.verify_family(kept + new))
        self.assertTrue(base.sunflower(*new))

    def test_two_completions_blocked_by_surviving_old_superset(self):
        # A five-deletion cover has one old set containing the triple.
        dropped = frozenset((1, 2, 24, 25, 26))
        kept = [a for i, a in enumerate(target.FAMILY) if i not in dropped]
        triple = base.mask(target.SHARP_TRIPLE)
        self.assertGreaterEqual(sum((a & triple) == triple for a in kept), 1)
        new = [base.mask(target.SHARP_TRIPLE + (x,)) for x in (18, 19)]
        self.assertFalse(base.verify_family(kept + new))

    def test_literal_graph_independent_representation(self):
        inside, outside = target.candidate_catalog()
        for c in inside[::17] + outside[::13]:
            self.assertEqual(set(target.forbidden_edges(c)),
                             target.literal_edges(c))


if __name__ == "__main__":
    unittest.main()
