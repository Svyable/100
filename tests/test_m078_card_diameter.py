"""Adversarial tests for the paired tree-card diameter obstruction."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","scripts"))
from m078_card_diameter import (parameters,tree,validate,balls,diameter,
                                 degree_card,joint_signature,check)

class M078CardDiameterTests(unittest.TestCase):
    def test_three_residues_and_next_period(self):
        for n in range(48,52):
            with self.subTest(n=n):self.assertTrue(check(3,n,True)["literal_motifs"])
    def test_four_motifs(self):
        self.assertTrue(check(4,64,True)["literal_motifs"])
    def test_five_rooted_ball(self):
        self.assertEqual(check(5,80,False)["rooted_types"],9)
    def test_every_card_diameter(self):
        for k,n in ((3,48),(4,64),(5,80)):
            A=parameters(k,n)[2]
            for variant in (0,1):
                g=tree(k,n,variant);validate(g)
                self.assertEqual(diameter(g,0),A-1)
                self.assertTrue(all(diameter(g,v)==2*A for v in range(1,n)))
    def test_paired_counts(self):
        a,b=tree(3,48,0),tree(3,48,1)
        self.assertEqual(joint_signature(a,3),joint_signature(b,3))
    def test_short_spur_mutation_falsifies(self):
        a,b=tree(3,48,0),tree(3,48,1)
        # Transfer a leaf from a length-three spur to the length-five spur.
        # The altered length-two spur violates the 2r-1 separation condition.
        a[41].remove(42);a[42].remove(41)
        a[47].add(42);a[42].add(47)
        validate(a)
        self.assertNotEqual(balls(a,2),balls(b,2))
        self.assertNotEqual(joint_signature(a,3),joint_signature(b,3))
    def test_invalid_graph(self):
        g=tree(3,48,0);g[0].add(47);g[47].add(0)
        with self.assertRaises(AssertionError):validate(g)
    def test_invalid_parameters(self):
        for k,n in ((2,40),(3,47),(4,63)):
            with self.assertRaises(ValueError):parameters(k,n)
        with self.assertRaises(ValueError):tree(3,48,2)
    def test_old_spider_fails_diameter(self):
        def spider(legs):
            g=[set() for _ in range(1+sum(legs))];j=1
            for length in legs:
                p=0
                for _ in range(length):
                    g[p].add(j);g[j].add(p);p=j;j+=1
            return g
        a,b=spider((3,3,5)),spider((3,4,4))
        self.assertNotEqual(sorted(diameter(a,v) for v in range(len(a))),
                            sorted(diameter(b,v) for v in range(len(b))))
    def test_independent_cpp(self):
        compiler=shutil.which("c++") or shutil.which("g++")
        if not compiler:self.skipTest("C++17 compiler unavailable")
        source=os.path.join(os.path.dirname(__file__),"..","scripts",
                            "m078_card_diameter_direct.cpp")
        with tempfile.TemporaryDirectory() as d:
            exe=os.path.join(d,"check")
            subprocess.run([compiler,"-std=c++17","-O2",source,"-o",exe],
                           check=True,timeout=60)
            result=subprocess.run([exe],capture_output=True,text=True,
                                  check=True,timeout=60)
            self.assertEqual(result.stdout.count("PASS"),5)

if __name__=="__main__":unittest.main()
