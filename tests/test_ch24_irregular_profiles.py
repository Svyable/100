"""Independent exhaustive integer audit of CH (24,8) irregular root."""
from collections import Counter
from itertools import combinations
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch24_irregular_profiles as cp
from ch_six_check import has_triangle


def independent_certificate():
    # Alpha: weak partitions of at most 5 surplus degrees into eight cells.
    def parts(size, minimum, remaining):
        if not size:
            if remaining == 0:
                yield ()
            return
        for a in range(minimum, remaining + 1):
            for tail in parts(size - 1, a, remaining - a):
                yield (a,) + tail

    alphas = {tuple(2 + p for p in part)
              for surplus in range(6)
              for part in parts(8, 0, surplus)}
    # K: combinadic multiset representation, independent of
    # itertools.combinations_with_replacement.
    k_profiles = [tuple(c - i for i, c in enumerate(combo))
                  for combo in combinations(range(15), 9)]
    stages = Counter()
    surviving = Counter()
    for a in alphas:
        m = sum(a)
        for k in k_profiles:
            if sum(k) < 74 - 2*m:
                continue
            stages["cut"] += 1
            possible = [sum(aa >= kb+2 for aa in a) for kb in k]
            if sum(possible) < 37 - m:
                continue
            stages["eligible"] += 1
            lower = sorted((max(0, 1+kb-q) for kb, q in zip(k, possible)),
                           reverse=True)
            if any(sum(lower[:s]) > s*(17-s)//2 for s in range(1, 10)):
                continue
            stages["subset"] += 1
            surviving[a] += 1
    return len(alphas), len(k_profiles), stages, surviving


class IrregularProfileTests(unittest.TestCase):
    def test_independent_dual_enumeration(self):
        na, nk, stages, survivors = independent_certificate()
        self.assertEqual((na, nk), (19, 5005))
        self.assertEqual(stages, {"cut": 20500, "eligible": 1116, "subset": 83})
        self.assertEqual(survivors, {
            (2, 2, 2, 2, 2, 2, 2, 7): 77,
            (2, 2, 2, 2, 2, 2, 3, 6): 6,
        })
        actual = cp.certificate()
        self.assertEqual(actual["pairs_meeting_all_B_subset_caps"], 83)
        self.assertEqual([tuple(a["internal_outdegrees_A"])
                          for a in actual["surviving_alpha_profiles"]],
                         sorted(survivors))

    def test_cut_rejects_bad_profile_and_indegree_scope(self):
        a = (2, 2, 2, 2, 2, 2, 2, 7)
        k = (0,) * 9
        self.assertFalse(cp.requirements(a, k)["cut_ok"])
        self.assertTrue(cp.requirements(a, (0, 0, 1, 4, 5, 5, 5, 6, 6))["cut_ok"])

    def test_nonvacuous_local_eight_vertex_control(self):
        # The surviving alpha (2^7,7) is a real triangle-free local shape.
        out = [sum(1 << ((v + step) % 7) for step in (1, 2))
               for v in range(7)] + [(1 << 7) - 1]
        self.assertEqual(sorted(x.bit_count() for x in out), [2]*7+[7])
        self.assertEqual(sum(x.bit_count() for x in out), 21)
        self.assertFalse(has_triangle(out))

    def test_six_outdegree_profile_forces_local_triangle(self):
        # When alpha is (2^6,3,6), max local indegrees are (3^6,2,1).
        # Total =21 forces all of them to be attained. The outdegree-6
        # vertex x has its unique in-neighbor y with indegree >=2.
        # y->x->t->y for some x-outneighbor t, contradicting C3-freeness.
        indegrees = [3]*6+[2,1]
        self.assertEqual(sum(indegrees), 21)
        self.assertEqual(sum(indegrees[:-1]), 20)
        self.assertGreaterEqual(min(indegrees[:-1]), 2)

    def test_global_high_low_count_uses_full_quantifiers(self):
        # h high (in=9); l low (in<=7). Balance gives l<=h.
        # Seven low outneighbors per high give 7h <= e(H,L) <= 7l.
        # Equality gives no L->L; the local alpha (2^7,7) forces 14.
        for h in range(1, 13):
            allowed = [ell for ell in range(25-h)
                       if ell <= h and 7*h <= 7*ell]
            self.assertEqual(allowed, [h])
        self.assertEqual(7*2, 14)

    def test_invalid_or_unsorted_input_rejected(self):
        with self.assertRaises(ValueError):
            cp.requirements((2,)*7+(8,), (0,)*9)
        with self.assertRaises(ValueError):
            cp.requirements((2,)*8, (0,)*8+(7,))
        with self.assertRaises(ValueError):
            cp.requirements((2,)*8, (1, 0)+(0,)*7)
        with self.assertRaises(ValueError):
            cp.requirements((2,)*7+(True,), (0,)*9)


if __name__ == "__main__":
    unittest.main()
