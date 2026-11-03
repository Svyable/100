"""Adversarial and independent tests for the M079 chain-plus-three result."""
import itertools
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m079_chain3_balance as target


def brute(triple):
    """Third checker: literal permutations of a poset, no gap counting/DP."""
    lo=min(a for a,_ in triple)
    hi=max(b for _,b in triple)
    m=hi-lo
    out=[(a-lo,b-lo) for a,b in triple]
    n=m+3
    total=0
    counts={(i,j):0 for i in range(3) for j in range(i+1,3)}
    counts.update({(i,3+t):0 for i in range(3) for t in range(1,m+1)})
    for perm in itertools.permutations(range(n)):
        pos=[0]*n
        for t,v in enumerate(perm):
            pos[v]=t
        if any(pos[t]>=pos[t+1] for t in range(m-1)):
            continue
        if any((a and pos[a-1]>=pos[m+i]) or
               (b<m and pos[m+i]>=pos[b])
               for i,(a,b) in enumerate(out)):
            continue
        total+=1
        for i in range(3):
            for j in range(i+1,3):
                counts[i,j]+=pos[m+i]<pos[m+j]
            for t in range(1,m+1):
                counts[i,3+t]+=pos[m+i]<pos[t-1]
    return total,counts


class ChainThreeTests(unittest.TestCase):
    def test_full_residual_exhaustive_and_two_path(self):
        d=target.census(verify_dp=True)
        self.assertEqual(d["cases"],67392)
        self.assertEqual(d["sharp_cases"],12)
        self.assertEqual(d["minimum"],"11/28")
        self.assertEqual(d["sha256"],
                         "0414a61f4d9cbc33afa4fd6aeea4c0e70304498bb5a7e4a066d686fa8eb3facf")

    def test_sharp_seven_element_witness(self):
        t=((-3,0),(-1,0),(0,1))
        E,p=target.formula(t)
        self.assertEqual(E,28)
        self.assertEqual(target.best_balance(E,p),11)
        self.assertEqual(target.independent_dp(t),(E,p))
        self.assertEqual(brute(t),(E,p))
        self.assertLess(Fraction(11,28),Fraction(2,5))

    def test_literal_permutation_checker(self):
        for t in [
            ((-1,0),(-1,0),(0,1)),
            ((-2,0),(-1,0),(0,1)),
            ((-1,0),(0,2),(0,1)),
            ((-2,0),(0,1),(-1,0)),
        ]:
            self.assertEqual(target.formula(t),brute(t),t)

    def test_width_four_excluded(self):
        t=((0,1),(0,1),(0,1))
        self.assertFalse(target.valid_triple(t))
        with self.assertRaises(ValueError):
            target.formula(t)

    def test_singleton_outsider_excluded(self):
        t=((-1,0),(0,0),(0,1))
        self.assertFalse(target.valid_triple(t))
        with self.assertRaises(ValueError):
            target.independent_dp(t)

    def test_nonoverlap_excluded(self):
        t=((-3,-1),(0,1),(0,1))
        self.assertFalse(target.valid_triple(t))

    def test_invalid_interval_excluded(self):
        self.assertFalse(target.valid_triple(((2,1),(-1,0),(0,1))))

    def test_translation_invariance(self):
        t=((-3,0),(-1,0),(0,1))
        shifted=tuple((a+50,b+50) for a,b in t)
        self.assertEqual(target.formula(t),target.formula(shifted))
        self.assertEqual(target.independent_dp(t),target.independent_dp(shifted))

    def test_order_duality_balance(self):
        t=((-3,0),(-1,0),(0,1))
        dual=tuple((-b,-a) for a,b in t)
        e,p=target.formula(t)
        f,q=target.formula(dual)
        self.assertEqual(e,f)
        self.assertEqual(target.best_balance(e,p),target.best_balance(f,q))

    def test_naive_tie_mutation_detected(self):
        t=((-3,0),(-1,0),(0,1))
        E,_=target.independent_dp(t)
        lengths=[b-a+1 for a,b in t]
        self.assertNotEqual(E,lengths[0]*lengths[1]*lengths[2])

    def test_large_interval_threshold(self):
        target.verify_large_interval_lemma(60)
        self.assertGreater(Fraction(3,13),Fraction(3,14))
        self.assertEqual(Fraction(3,14),1-2*target.BOUND)

    def test_exact_random_interval_crosscheck(self):
        opts=list(target.intervals(7))
        checked=0
        for a in opts:
            for b in opts:
                for c in opts:
                    if max(a[0],b[0],c[0])==min(a[1],b[1],c[1]):
                        if (checked*17)%29==0:
                            self.assertEqual(target.formula((a,b,c)),
                                             target.independent_dp((a,b,c)))
                        checked+=1
        self.assertGreater(checked,1000)


if __name__=="__main__":
    unittest.main()
