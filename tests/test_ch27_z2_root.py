"""Adversarial controls for M074 z=2 relaxed profile obstruction."""
import unittest
from itertools import combinations
from scripts import ch27_z2_root as z

class TestZ2Root(unittest.TestCase):
    def test_profile_counts(self):
        self.assertEqual(len(list(z.alphas())),166)
        self.assertEqual(len(list(z.ks())),3003)
        counts,patterns,three,forbidden=z.audit()
        self.assertEqual(sum(counts.values()),498498)
        self.assertEqual(sum(patterns.values()),475)
        self.assertEqual(sum(three.values()),287)
        self.assertEqual(sum(forbidden.values()),226)
        self.assertEqual(sum(three.values())-sum(forbidden.values()),61)

    def test_four_cycle_literal_enumeration(self):
        self.assertEqual(z.directed_four_cycle_control(),6)

    def test_indegree_budget_and_equality_case(self):
        self.assertEqual(sum(z.P1),29)
        self.assertLess(3*4+3+5*2,29)
        self.assertEqual(sum(z.P2),29)
        self.assertLess(3*4+5*3,29)
        self.assertEqual(sum(z.P3),29)
        self.assertLess(4*4+2*3+2*2+2,29)
        self.assertEqual(sum(z.P4),28)
        self.assertEqual(4*4+2*3+3*2,28)

    def test_sharp_known_witness_not_overexcluded(self):
        out={i:{(i+1)%7,(i+2)%7} for i in range(7)}
        out[7]=set(range(7));out[8]=set(range(8))
        self.assertEqual(sum(map(len,out.values())),29)
        self.assertEqual(tuple(sorted(map(len,out.values()))),(2,)*7+(7,8))
        self.assertNotIn(tuple(sorted(map(len,out.values()))),z.FORBIDDEN)
        self.assertFalse(any(j in out[i] and k in out[j] and i in out[k]
                             for i in out for j in out for k in out
                             if len({i,j,k})==3))

    def test_rank_deficit_permutation_invariant(self):
        for a in z.FORBIDDEN:
            self.assertGreaterEqual(z.rank_deficit(a),0)
            self.assertEqual(z.rank_deficit(a),z.rank_deficit(tuple(reversed(a))))

if __name__=="__main__":
    unittest.main()
