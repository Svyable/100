"""Independent CH27 indegree-ten B-small-subset tests."""
import sys
import unittest
from itertools import combinations_with_replacement
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch27_b_internal as b


def compositions(n, bins):
    if bins == 1:
        yield (n,)
    else:
        for first in range(n + 1):
            for tail in compositions(n - first, bins - 1):
                yield (first,) + tail


def independent_histograms():
    alpha = set()
    for h in compositions(9, 7):
        if sum(i * h[i] for i in range(7)) <= 11:
            alpha.add(tuple(2 + i for i in range(7) for _ in range(h[i])))
    k = set()
    for h in compositions(6, 7):
        k.add((0,)*4 + tuple(i + 1 for i in range(7) for _ in range(h[i])))
    return alpha, k


def independent_floors(alpha, k):
    # Count eligible targets by explicit pairs rather than the production q array.
    return tuple(sorted((max(0, 1 + val -
                             len([a for a in alpha if a >= val + 2]))
                         for val in k), reverse=True))


class CH27BInternalTests(unittest.TestCase):
    def test_independent_histogram_generators(self):
        a, k = independent_histograms()
        self.assertEqual((len(a),len(k)), (166,924))
        self.assertEqual(a,set(b.alpha_profiles()))
        self.assertEqual(k,set(b.k_profiles_with_four_zeros()))

    def test_exact_profile_audit(self):
        r = b.audit()
        self.assertEqual(r["pairs"], 153384)
        self.assertEqual(r["stages"], {
            "cut": 149396,
            "subset_capacity": 3515,
            "triangle_three": 132,
            "minout_two_5": 22,
            "minout_two_6": 24,
            "unresolved": 295,
        })
        self.assertEqual(r["sample_unresolved_profile"],
                         ((2,)*7 + (6,8), (0,)*4 + (4,6,6,6,7,7)))

    def test_triangle_rule_mutation_detected(self):
        exact = b.audit()
        weak = b.audit(include_triangle=False)
        self.assertEqual(weak["stages"]["unresolved"]-
                         exact["stages"]["unresolved"], 132)
        self.assertEqual(weak["stages"]["unresolved"], 427)

    def test_independent_floors_and_boundary_controls(self):
        a=(2,)*7+(6,8)
        false_survivor=(0,)*4+(4,5,6,7,7,7)
        actual=(0,)*4+(4,6,6,6,7,7)
        self.assertEqual(b.internal_B_floors(a,false_survivor),
                         independent_floors(a,false_survivor))
        self.assertEqual(b.classify(a,false_survivor), "triangle_three")
        self.assertTrue(b.subset_capacity_ok(b.internal_B_floors(a,false_survivor)))
        self.assertEqual(b.classify(a,actual), "unresolved")
        self.assertEqual(b.internal_B_floors(a,actual),
                         independent_floors(a,actual))

    def test_small_set_thresholds_and_positive_control(self):
        self.assertEqual(b.forbidden_small_set((8,8,8)+(0,)*7), "triangle_three")
        self.assertIsNone(b.forbidden_small_set((8,8,8)+(0,)*7,
                                                include_triangle=False))
        self.assertEqual(b.forbidden_small_set((7,)*5+(0,)*5), "minout_two_5")
        self.assertEqual(b.forbidden_small_set((6,)*6+(0,)*4), "minout_two_6")
        # A 4-cycle has min-outdegree one and no directed triangle.
        # It must not be rejected by any min-outdegree-two rule.
        self.assertIsNone(b.forbidden_small_set((7,)*4+(0,)*6))
        self.assertIsNone(b.forbidden_small_set((0,)*10))

    def test_malformed_arrays(self):
        for a,k in [((2,)*8,(0,)*10),((2,)*9,(0,)*9),
                    ((2,)*8+(True,),(0,)*10),((2,)*9,(0,)*9+(8,))]:
            with self.assertRaises(ValueError):
                b.internal_B_floors(a,k)
        with self.assertRaises(ValueError):
            b.forbidden_small_set((8,7)+(0,)*8)


if __name__=="__main__":
    unittest.main()
