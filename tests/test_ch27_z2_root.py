"""Adversarial controls for M074 z=2 relaxed profile obstruction."""
import unittest
from itertools import combinations
from scripts import ch27_z2_root as z

class TestZ2Root(unittest.TestCase):
    def test_profile_counts(self):
        self.assertEqual(len(list(z.alphas())),166)
        self.assertEqual(len(list(z.ks())),3003)
        counts,patterns,three,forbidden,final=z.audit()
        self.assertEqual(sum(counts.values()),498498)
        self.assertEqual(sum(patterns.values()),475)
        self.assertEqual(sum(three.values()),287)
        self.assertEqual(sum(forbidden.values()),226)
        self.assertEqual(sum(three.values())-sum(forbidden.values()),61)
        self.assertEqual(sum(final.values()),475)
        self.assertNotIn("unresolved",final)
        self.assertEqual(final["eight_vertex_26_arc_extremal"],1)

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

    def test_eight_vertex_extremal_orientation_control(self):
        # At 26 arcs and minimum outdegree one, a shortest directed
        # four-cycle has exactly its two missing diagonals. The four
        # outside vertices form a transitive tournament, each either
        # dominating or dominated by the cycle. Check all 16 patterns.
        from itertools import product
        Q=range(4);T=range(4,8)
        admissible=[]
        for bits in product((0,1),repeat=4):
            edges={(i,(i+1)%4) for i in Q}
            edges.update((i,j) for i,j in combinations(T,2))
            for t,b in zip(T,bits):
                edges.update((t,q) if b else (q,t) for q in Q)
            triangle=any((i,j) in edges and (j,k) in edges and (k,i) in edges
                         for i in range(8) for j in range(8) for k in range(8)
                         if len({i,j,k})==3)
            mindeg=min(sum((i,j) in edges for j in range(8)) for i in range(8))
            if not triangle and mindeg>=1:
                admissible.append(tuple(sorted(sum((i,j) in edges for j in range(8))
                                               for i in range(8))))
        self.assertEqual(admissible,[(1,1,1,1,4,5,6,7)])

    def test_rank_deficit_permutation_invariant(self):
        for a in z.FORBIDDEN:
            self.assertGreaterEqual(z.rank_deficit(a),0)
            self.assertEqual(z.rank_deficit(a),z.rank_deficit(tuple(reversed(a))))

if __name__=="__main__":
    unittest.main()
