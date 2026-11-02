"""Adversarial checks for the M076 six-deletion local stability candidate."""
import unittest

from scripts import m076_f43_stability as base
from scripts import m076_f43_six as six


class SixDeletionTests(unittest.TestCase):
    def test_full_certificate_two_paths(self):
        result = six.check(include_literal=True)
        self.assertEqual(result["inside_six_covers"], 32)
        self.assertEqual(result["outside_six_covers"], 97)
        self.assertEqual(result["max_insertions_after_six_deletions"], 2)

    def test_all_orbit_matchings_and_independent_cover_counts(self):
        reps, _ = base.orbit_representatives()
        for key, points in reps.items():
            edges = six.forbidden_edges(base.mask(points))
            matching = six.disjoint_matching(edges)
            self.assertEqual(len(set(v for e in matching for v in e)),
                             2 * len(matching))
            self.assertTrue(all(e in edges for e in matching))
            if key not in (six.INSIDE, six.OUTSIDE):
                self.assertGreaterEqual(len(matching), 7)
            self.assertEqual(six.matching_six_covers(edges),
                             six.branch_six_covers(edges))

    def test_all_forbidden_graphs_recomputed_with_sets(self):
        inside, outside = six.candidate_catalog()
        for c in inside + outside:
            self.assertEqual(six.forbidden_edges(c), six.literal_edges(c))

    def test_candidate_types_and_old_members_excluded(self):
        inside, outside = six.candidate_catalog()
        self.assertEqual((len(inside), len(outside)), (162, 108))
        self.assertTrue(all(c not in six.FAMILY for c in inside + outside))
        self.assertTrue(all(base.orbit_key(
            tuple(i for i in range(22) if c & (1 << i))) == six.INSIDE
            for c in inside))
        self.assertTrue(all(base.orbit_key(
            tuple(i for i in range(22) if c & (1 << i))) == six.OUTSIDE
            for c in outside))

    def test_forged_cover_rejected(self):
        candidate = base.mask((0, 1, 3, 18))
        edges = six.forbidden_edges(candidate)
        self.assertTrue(six.valid_cover(edges, six.EXCEPTIONAL_DROP))
        self.assertFalse(six.valid_cover(edges, frozenset((3, 4, 5, 6, 7, 8))))

    def test_sharp_two_insertions_and_three_forbidden(self):
        kept = [a for i, a in enumerate(six.FAMILY)
                if i not in six.EXCEPTIONAL_DROP]
        t = six.EXCEPTIONAL_TRIPLE
        one = base.mask(t + (18,))
        two = base.mask(t + (19,))
        three = base.mask(t + (20,))
        self.assertTrue(base.verify_family(kept + [one, two]))
        self.assertFalse(base.verify_family(kept + [one, two, three]))
        self.assertEqual(len(kept) + 2, 50)

    def test_nonexceptional_outside_two_insertions_fail(self):
        rep = base.mask((0, 1, 3, 18))
        covers = six.matching_six_covers(six.forbidden_edges(rep))
        self.assertEqual(len(covers), 97)
        for dropped in covers:
            if dropped == six.EXCEPTIONAL_DROP:
                continue
            kept = [a for i, a in enumerate(six.FAMILY) if i not in dropped]
            self.assertFalse(base.verify_family(kept + [
                rep, base.mask((0, 1, 3, 19))
            ]))

    def test_inside_six_covers_admit_only_one_new_set(self):
        rep = base.mask((0, 1, 3, 6))
        covers = six.matching_six_covers(six.forbidden_edges(rep))
        inside, outside = six.candidate_catalog()
        self.assertEqual(len(covers), 32)
        for dropped in covers:
            admitted = [c for c in inside + outside
                        if six.valid_cover(six.forbidden_edges(c), dropped)]
            self.assertEqual(admitted, [rep])

    def test_tamper_sunflower_edge_and_representation(self):
        c = base.mask((0, 1, 3, 18))
        edges = six.forbidden_edges(c)
        self.assertIn((1, 0), edges)
        self.assertNotIn((27, 0), edges)
        self.assertEqual(edges, six.literal_edges(c))
        self.assertNotEqual(edges, six.literal_edges(base.mask((0, 1, 3, 6))))


if __name__ == "__main__":
    unittest.main()
