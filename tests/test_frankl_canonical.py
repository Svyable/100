import itertools
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import frankl_canonical as fc
from union_closed import is_union_closed


def members(encoded, n):
    return {s for s in range(1 << n) if encoded >> s & 1}


class CanonicalUnionClosedTests(unittest.TestCase):
    def test_full_support_generator_exhausts_n4_independently(self):
        generated = set(fc.full_support_families(4))
        self.assertEqual(len(generated), 4542)
        # Separate brute-force universe filter; this is cheap only at n<=4.
        full = (1 << 4) - 1
        expected = {
            mask for mask in range(1 << (1 << 4))
            if mask >> full & 1
            and is_union_closed(members(mask, 4))
        }
        self.assertEqual(generated, expected)

    def test_orbit_count_agrees_with_independent_mine(self):
        self.assertEqual(
            {n: len(set(fc.canonical_representatives(n))) for n in range(1, 5)},
            {1: 2, 2: 6, 3: 28, 4: 330}
        )
        self.assertEqual(sum(fc.ORBIT_COUNTS.values()), 366)
        self.assertEqual(
            sum(__import__("math").comb(4, k) * fc.EXHAUSTIVE_COUNTS[k]
                for k in range(1, 5)),
            4958
        )

    def test_relabeling_preserves_canonical_code_at_n5(self):
        examples = list(itertools.islice(fc.full_support_families(5), 40))
        actions = fc.subset_actions(5)
        self.assertEqual(len(actions), 120)
        for family in examples:
            witness = fc.canonical(family, 5)
            for action in (actions[1], actions[33], actions[-1]):
                transformed = fc.relabel_family(family, action)
                self.assertEqual(fc.canonical(transformed, 5), witness)
                self.assertEqual(fc.is_canonical(transformed, 5),
                                 transformed == witness)

    def test_prefix_n5_has_one_per_orbit_without_full_exhaustion(self):
        reps = list(itertools.islice(fc.canonical_representatives(5), 100))
        self.assertEqual(len(reps), 100)
        self.assertEqual(len(set(reps)), len(reps))
        for family in reps:
            self.assertTrue(fc.is_canonical(family, 5))
            self.assertTrue(is_union_closed(members(family, 5)))
            self.assertIn(31, members(family, 5))

    def test_invalid_encoding_and_size_rejected(self):
        with self.assertRaises(ValueError):
            list(fc.full_support_families(6))
        with self.assertRaises(ValueError):
            fc.canonical(1 << 32, 5)
        with self.assertRaises(ValueError):
            fc.canonical(True, 5)
        with self.assertRaises(ValueError):
            fc.canonical(3, 0)
        with self.assertRaises(ValueError):
            fc.is_canonical(-1, 4)

    def test_monotone_completion_constraint_rejects_forced_missing_union(self):
        # F={{0,1},{1,2}}: introducing {0} would require {0,1,2}.
        family = (1 << 3) | (1 << 6)
        self.assertFalse(fc.includes_unions(family, 1))
        self.assertTrue(fc.includes_unions(family | (1 << 7), 1))


if __name__ == "__main__":
    unittest.main()
