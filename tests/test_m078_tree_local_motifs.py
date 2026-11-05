"""Adversarial controls for bounded induced-motif tree-card obstructions."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from m078_tree_local_motifs import (spider, pair, rooted_ball, ball_histogram,
    card_degree_signature, card_motif_signature, canonical_maps)


class TreeLocalMotifTests(unittest.TestCase):
    def test_pair_k3(self):
        a,b=pair(3)
        self.assertEqual(len(a),12)
        self.assertEqual(ball_histogram(a,2),ball_histogram(b,2))
        self.assertEqual(card_motif_signature(a,3),card_motif_signature(b,3))

    def test_pair_k4(self):
        a,b=pair(4)
        self.assertEqual(len(a),18)
        self.assertEqual(ball_histogram(a,3),ball_histogram(b,3))
        self.assertEqual(card_motif_signature(a,4),card_motif_signature(b,4))

    def test_extra_vertices(self):
        for k in (3,4):
            a,b=pair(k,1)
            self.assertEqual(card_degree_signature(a),card_degree_signature(b))
            self.assertEqual(card_motif_signature(a,k),card_motif_signature(b,k))

    def test_shallow_boundary_falsifier(self):
        for k in (3,4):
            L=2*k-4
            a,b=spider((L,L,L+2)),spider((L,L+1,L+1))
            self.assertNotEqual(ball_histogram(a,k-1),ball_histogram(b,k-1))
            self.assertNotEqual(card_motif_signature(a,k),card_motif_signature(b,k))

    def test_degree_boundary_and_mutation(self):
        for n in range(10,25):
            a,b=spider((1,3,n-5)),spider((1,4,n-6))
            self.assertEqual(card_degree_signature(a),card_degree_signature(b))
        self.assertNotEqual(card_degree_signature(spider((1,3,5))),card_degree_signature(spider((1,2,6))))

    def test_induced_canonicalization(self):
        table=canonical_maps(3)
        self.assertEqual(len({table[x] for x in range(8)}),4)
        self.assertNotEqual(table[3],table[7])
        self.assertEqual(table[3],table[5])

    def test_rooted_ball_detects_changed_branch(self):
        a,b=spider((4,4,6)),spider((4,5,5))
        self.assertNotEqual(ball_histogram(a,3),ball_histogram(b,3))


if __name__=='__main__': unittest.main()
