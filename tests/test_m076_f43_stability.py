"""Adversarial tests for M076's 54-set local stability obstruction."""
import unittest
import hashlib
from itertools import combinations
from scripts import m076_f43_stability as m


class M076StabilityTests(unittest.TestCase):
    def test_base_counts_and_full_triples(self):
        self.assertEqual(len(m.base_family()), 54)
        self.assertTrue(m.verify_family(m.base_family()))
        self.assertEqual(sum(1 for _ in combinations(range(54), 3)), 24804)

    def test_oeis_source_digest(self):
        rows = ["{" + ", ".join(str(i + 1) for i in range(18) if x & (1 << i)) + "}"
                for x in m.base_family()]
        digest = hashlib.sha256(("\n".join(rows) + "\n").encode()).hexdigest()
        self.assertEqual(digest, "b84ccc5d91526d89d372e19de5025bc2ff63994c615390a715516831c391a646")

    def test_certificate_orbit_coverage(self):
        reps, counts = m.orbit_representatives()
        self.assertEqual(len(reps), 18)
        self.assertEqual(sum(counts.values()), 7261)
        self.assertEqual(set(reps), set(m.MATCHING_WITNESSES))
        self.assertEqual(sum(1 for k in reps if k[0] == 0), 8)

    def test_all_matching_certificates(self):
        self.assertEqual(sum(m.check_certificates().values()), 7261)

    def test_independent_no_symmetry_sweep(self):
        self.assertTrue(m.independent_full_sweep())

    def test_five_cover_classification(self):
        self.assertEqual(m.enumerate_five_covers(), {
            frozenset((0, 2, 24, 25, 26)),
            frozenset((1, 2, 24, 25, 26)),
        })
        self.assertTrue(m.check_five_deletion_rigidity())

    def test_independent_five_cover_sweep(self):
        self.assertEqual(m.independent_cover_sweep(), 2)

    def test_two_outside_insertions_rejected(self):
        family = m.base_family()
        for drop in m.enumerate_five_covers():
            kept = [a for i, a in enumerate(family) if i not in drop]
            self.assertFalse(m.verify_family(kept + [
                m.mask((0, 1, 3, 18)), m.mask((0, 1, 3, 19))]))

    def test_duplicate_old_member_rejected(self):
        family = list(m.base_family())
        family[-1] = family[0]
        self.assertFalse(m.verify_family(family))

    def test_injected_sunflower_rejected(self):
        family = list(m.base_family())
        family.append(m.mask((0, 1, 3, 18)))
        self.assertFalse(m.verify_family(family))

    def test_tamper_reused_matching_vertex_rejected(self):
        reps, _ = m.orbit_representatives()
        key = (1, (2, 1, 0), (0, 0, 0))
        pairs = list(m.MATCHING_WITNESSES[key])
        pairs[1] = (pairs[0][0], pairs[1][1])
        self.assertFalse(m.check_matching(key, reps[key], pairs))

    def test_tamper_false_sunflower_pair_rejected(self):
        reps, _ = m.orbit_representatives()
        key = (1, (2, 1, 0), (0, 0, 0))
        pairs = list(m.MATCHING_WITNESSES[key])
        pairs[0] = (0, 27)
        self.assertFalse(m.check_matching(key, reps[key], pairs))

    def test_sharpness_five_deletions(self):
        family = m.base_family()
        candidate = m.mask(m.SHARP_OUTSIDE)
        kept = [a for i, a in enumerate(family) if i not in m.DROP_OUTSIDE]
        self.assertTrue(m.verify_family(kept + [candidate]))
        self.assertEqual(len(kept) + 1, 50)

    def test_sharpness_six_deletions(self):
        family = m.base_family()
        candidate = m.mask(m.SHARP_INSIDE)
        kept = [a for i, a in enumerate(family) if i not in m.DROP_INSIDE]
        self.assertTrue(m.verify_family(kept + [candidate]))
        self.assertEqual(len(kept) + 1, 49)

    def test_wrong_deletion_control_rejected(self):
        family = m.base_family()
        kept = [a for i, a in enumerate(family) if i not in (0, 1, 2, 3, 4)]
        self.assertFalse(m.verify_family(kept + [m.mask(m.SHARP_OUTSIDE)]))

    def test_orbit_key_invariant_under_relabel(self):
        self.assertEqual(
            m.orbit_key((0, 1, 3, 18)),
            m.orbit_key((2, 1, 5, 22)),
        )


if __name__ == "__main__":
    unittest.main()
