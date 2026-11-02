"""Independent adversarial tests for the regular CH (27,9) cross-cut."""
from collections import Counter
from itertools import product
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch27_regular_crosscut as target
import ch27_local


def independent_degree_multisets():
    """Integer partitions of <=11 surplus units; not combinations_with_replacement."""
    def build(slots, last, available):
        if slots == 0:
            yield ()
            return
        for value in range(last, min(6, available) + 1):
            for tail in build(slots-1, value, available-value):
                yield (value,) + tail
    return tuple(tuple(2 + x for x in part) for part in build(9, 0, 11))


def independent_audit(bound=29, threshold=10):
    """Compute pair counts from multiplicity products, independent of 81 pair scans."""
    samples = tuple(a for a in independent_degree_multisets() if sum(a) <= bound)
    stats = {"profiles": len(samples), "pairs": 0, "maximum": -1,
             "minimum_demand": 100, "maximum_gap": -100, "survivors": 0}
    close = []
    for alpha in samples:
        counts_a = Counter(alpha)
        for beta in samples:
            stats["pairs"] += 1
            counts_b = Counter(beta)
            eligible = sum(na*nb for a,na in counts_a.items()
                           for b,nb in counts_b.items() if a+b >= threshold)
            required = 81 - 2*min(sum(alpha), sum(beta))
            stats["maximum"] = max(stats["maximum"], eligible)
            stats["minimum_demand"] = min(stats["minimum_demand"], required)
            stats["maximum_gap"] = max(stats["maximum_gap"], eligible-required)
            if eligible >= required:
                stats["survivors"] += 1
            if required-eligible == 1:
                close.append((alpha, beta))
    return stats, close


class CH27RegularCrossCutTests(unittest.TestCase):
    def test_profile_exhaustion_from_independent_partitions(self):
        ours = independent_degree_multisets()
        theirs = target.profiles()
        self.assertEqual(set(ours), set(theirs))
        self.assertEqual(len(set(ours)), 166)
        self.assertEqual(len(ours), len(set(ours)))
        self.assertTrue(all(sum(a)<=29 and min(a)>=2 and max(a)<=8
                            for a in ours))

    def test_independent_crosscut_certificate(self):
        computed, close = independent_audit()
        self.assertEqual(computed, {
            "profiles":166, "pairs":27556, "maximum":22,
            "minimum_demand":23, "maximum_gap":-1, "survivors":0
        })
        expected_a = (2,2,2,2,2,2,2,7,8)
        expected_b = (2,2,2,3,3,3,3,3,8)
        self.assertEqual(set(close), {(expected_a,expected_b),
                                      (expected_b,expected_a)})
        produced = target.certificate()
        self.assertEqual(produced["maximizer_count"], 2)
        self.assertEqual(produced["abstract_profiles_meeting_cross_requirement"], 0)
        self.assertEqual(produced["maximum_allowed_minus_required"], -1)

    def test_arc_ceiling_and_triangle_requirement_necessary(self):
        relaxed_arc, _ = independent_audit(bound=30)
        self.assertEqual(relaxed_arc["profiles"], 220)
        self.assertEqual(relaxed_arc["survivors"], 60)
        weakened_triangle, _ = independent_audit(threshold=9)
        self.assertEqual(weakened_triangle["survivors"], 173)
        self.assertEqual(target.certificate(30)
                         ["abstract_profiles_meeting_cross_requirement"], 60)
        self.assertEqual(target.certificate(29, 9)
                         ["abstract_profiles_meeting_cross_requirement"], 173)

    def test_sharp_local_control_is_actually_realizable(self):
        out = ch27_local.sharp_nine()
        local = ch27_local.check_oriented_triangle_free(out)
        self.assertEqual(local["arcs"], 29)
        self.assertEqual(sorted(local["outdegrees"]),
                         [2,2,2,2,2,2,2,7,8])
        self.assertEqual(target.eligible_cross_pairs(
            (2,2,2,2,2,2,2,7,8),(2,2,2,3,3,3,3,3,8)), 22)
        self.assertEqual(target.required_cross_arcs(
            (2,2,2,2,2,2,2,7,8),(2,2,2,3,3,3,3,3,8)), 23)

    def test_negative_control_triangle_invalidates_a_to_b_prohibition(self):
        # At root v=0: v->a(1)->b(2)->v; A->B exists only
        # when the directed triangle-free condition is dropped.
        rows = ((1,), (2,), (0,))
        self.assertEqual(rows[0], (1,))
        self.assertEqual(rows[1], (2,))
        self.assertRaises(ValueError,
                          ch27_local.check_oriented_triangle_free, rows)

    def test_input_boundaries(self):
        for bad in (True, 17, 31, 29.0, None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    target.profiles(bad)
        with self.assertRaises(ValueError):
            target.eligible_cross_pairs((2,)*8, (2,)*9)
        with self.assertRaises(ValueError):
            target.eligible_cross_pairs((2,)*9, (2,)*8)
        with self.assertRaises(ValueError):
            target.eligible_cross_pairs((2,)*9, (2,)*9, threshold=True)


if __name__ == "__main__":
    unittest.main()
