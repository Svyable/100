"""Exact adversarial checks for the M078 exponential joint-local-card fiber."""
import sys
import unittest
from itertools import combinations
from pathlib import Path
from math import comb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import m078_exponential_fibers as f


class FiberTests(unittest.TestCase):
    def test_exact_graph_shape_and_order(self):
        for k,m,extras in ((3,4,(0,0,0,0,0,0)),
                           (3,4,(0,1,0,2,0,3)),
                           (4,5,(1,0,0,0,1,0,2))):
            with self.subTest(k=k,m=m,extras=extras):
                g=f.fiber_tree(k,m,extras)
                self.assertEqual(len(g),m+(m+2)*(2*k-3)+sum(extras))
                self.assertEqual(sum(map(len,g)),2*(len(g)-1))
                self.assertEqual(sum(len(x)==3 for x in g),m)
                self.assertEqual(sum(len(x)==1 for x in g),m+2)
                seen={0}
                frontier=[0]
                while frontier:
                    frontier=[w for v in frontier for w in g[v] if w not in seen]
                    seen.update(frontier)
                self.assertEqual(len(seen),len(g))

    def test_bad_scope_rejected(self):
        for values in ((2,4,(0,)*6),(3,3,(0,)*5),
                       (3,4,(0,)*5),(3,4,(0,0,-1,0,0,1)),
                       (3,4,(0,0,1.0,0,0,1))):
            with self.subTest(values=values), self.assertRaises(ValueError):
                f.fiber_tree(*values)

    def test_four_vertex_unlabeled_classification(self):
        self.assertTrue(f.check_four_vertex_degree_classification())

    def test_exhaustive_joint_cards_k3_six_binary_positions(self):
        info=f.check_small(3,6,2,deep=True)
        self.assertEqual(info['nonisomorphic'],4)
        self.assertEqual(info['n'],32)

    def test_radius_three_fiber_and_nonisomorphism(self):
        info=f.check_small(4,5,1,deep=False)
        self.assertEqual(info['nonisomorphic'],2)

    def test_all_126_compositions_and_eight_to_one_count(self):
        info=f.quantitative_fiber(3,4,4,direct=False)
        self.assertEqual(info['compositions'],comb(9,5))
        self.assertEqual(info['nonisomorphic'],31)
        self.assertGreaterEqual(8*info['nonisomorphic'],info['compositions'])

    def test_endpoint_padding_does_not_break_joint_pairs(self):
        x=f.family_tree(3,6,(1,3),endpoint_padding=7)
        y=f.family_tree(3,6,(2,3),endpoint_padding=7)
        self.assertNotEqual(f.spine_code(x), f.spine_code(y))
        self.assertEqual(f.direct_joint_cards(x,3),f.direct_joint_cards(y,3))
        self.assertEqual(f.balls(x,3),f.balls(y,3))

    def test_arbitrary_weak_compositions_keep_joint_cards(self):
        # Go beyond the binary-extra family: move all four units between
        # endpoints and internal hubs while preserving 26 vertices.
        allocations=((4,0,0,0,0,0),(0,0,4,0,0,0),
                     (0,0,1,1,1,1),(0,0,0,0,0,4))
        graphs=[f.fiber_tree(3,4,x) for x in allocations]
        self.assertEqual(len({f.spine_code(g) for g in graphs}),3)
        self.assertTrue(all(f.direct_joint_cards(g,3)==f.direct_joint_cards(graphs[0],3)
                            for g in graphs))

    def test_every_sufficiently_large_order_arithmetic(self):
        for k in range(3,8):
            L=2*k-3
            for n in range(12*k-10,12*k+31):
                m=(n-2*L)//(L+2)
                s=n-2*L-(L+1)*m
                self.assertGreaterEqual(m,4)
                self.assertGreaterEqual(s,m)
                self.assertEqual(n,m+(m+2)*L+s)
                self.assertGreaterEqual((m+1)*comb(s+m+1,m+1),4**m)

    def test_card_perturbation_is_detected(self):
        g=f.family_tree(3,5,(1,))
        h=f.family_tree(3,5,(2,))
        self.assertEqual(f.direct_joint_cards(g,3),f.direct_joint_cards(h,3))
        # Make one extra edge (introduce a cycle); a counterfeit graph cannot
        # keep the exact paired card motif statistics.
        tampered=[set(x) for x in h]
        u,v=next((a,b) for a in range(len(h)) for b in range(a+1,len(h))
                 if b not in h[a])
        tampered[u].add(v)
        tampered[v].add(u)
        self.assertNotEqual(f.direct_joint_cards(g,3),
                            f.direct_joint_cards(tuple(frozenset(x) for x in tampered),3))


if __name__ == '__main__':
    unittest.main()
