"""Boundary and adversarial checks for the shorter CH(24,8) capacity argument."""
import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch24_z3_capacity as z3


class UniformCutTests(unittest.TestCase):
    def test_local_profiles_and_surplus_necessity(self):
        profiles = z3.local_a_profiles()
        self.assertEqual(len(profiles), 19)
        self.assertTrue(all(len(a) == 8 and min(a) >= 2 and sum(a) <= 21
                            for a in profiles))
        for alpha in profiles:
            for k in range(2, 7):
                q = len([a for a in alpha if a >= k+2])
                self.assertLessEqual(q, 6-k)
        # Without the *proved* 21-arc cap, q<=6-k is not unconditional.
        invalid = (2, 2, 2, 2, 2, 7, 7, 7)
        self.assertEqual(sum(invalid), 31)
        self.assertGreater(sum(a >= 7 for a in invalid), 6-5)

    def test_z3_requires_34_exceeding_33(self):
        cert = z3.z3_audit()
        self.assertEqual(cert["relaxed_profiles"], 107)
        self.assertEqual(cert["minimum_B_outgoing"], 34)
        self.assertEqual(cert["capacity"], 33)
        alpha, ks = cert["witness_profile"]
        # Independent q computation from direct set cardinalities.
        q = tuple(len(set(i for i, a in enumerate(alpha) if a >= k+2))
                  for k in ks)
        self.assertEqual(q, (1, 1, 1, 1, 0, 0))
        self.assertEqual(sum(1+k-qi for k, qi in zip(ks, q)), 34)

    def test_one_unit_weaker_cut_is_not_enough(self):
        exact = z3.z3_audit()
        weakened = z3.z3_audit(1)
        self.assertLessEqual(weakened["minimum_B_outgoing"], 33)
        self.assertEqual(weakened["minimum_B_outgoing"], 32)
        self.assertEqual(exact["minimum_B_outgoing"], 34)
        alpha = (2,)*7 + (7,)
        ks = (4, 5, 5, 5, 6, 6)
        self.assertEqual(sum(ks), 31)
        self.assertEqual(z3.b_outgoing_lower(alpha, ks), 33)
        self.assertLess(sum(ks), 74-2*sum(alpha))
        # These are relaxed integer constraints, not a graph witness.

    def test_z2_remaining_branch_has_capacity_violation(self):
        result = z3.z2_exception_audit()
        self.assertEqual(result["relaxed_profiles"], 106)
        self.assertEqual(result["ones_cases"], {0: 87, 1: 18, 2: 1})
        self.assertEqual(
            result["minimum_seven_subset_bound_when_u_at_most_one"], 37)
        self.assertGreater(5*7, 5*(17-5)//2)

    def test_reject_invalid_cut_slack(self):
        for x in (-1, 0.5, True):
            with self.subTest(x=x), self.assertRaises(ValueError):
                z3.z3_audit(x)


if __name__ == "__main__":
    unittest.main()
