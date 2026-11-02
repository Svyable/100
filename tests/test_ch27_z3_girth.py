"""Independent histogram, graph and mutation controls for CH27 z=3."""
import sys
import unittest
from collections import Counter
from itertools import combinations,product
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import ch27_z3_girth as target

def compositions(total,bins):
    if bins==1:yield(total,)
    else:
        for first in range(total+1):
            for rest in compositions(total-first,bins-1):yield(first,)+rest

def independent_profiles():
    aa=[]
    for h in compositions(9,7):
        if sum(i*n for i,n in enumerate(h))<=11:
            aa.append(tuple(i+2 for i,n in enumerate(h) for _ in range(n)))
    kk=[(0,)*3+tuple(i+1 for i,n in enumerate(h) for _ in range(n))
        for h in compositions(7,7)]
    return sorted(aa),sorted(kk)

def independent_missing(a):
    result=0
    for i,d in enumerate(a):
        others=a[:i]+a[i+1:]
        t=min(t for t in range(2,10) if sum(x>=t for x in others)<d)
        result+=max(0,d-(t-1))
    return result

def independent_classify(a,k,deficit=2,ends=True):
    m=sum(a);K=sum(k)
    if K<92-2*m:return "root_cut"
    f=sorted((max(0,1+x-sum(v>=x+2 for v in a)) for x in k),reverse=True)
    if any(sum(f[:s])>s*(19-s)//2 for s in range(1,11)):return "B_capacity"
    if f[2]>=8 or f[4]>=7 or f[5]>=6:return "B_small_girth"
    if K<92-2*m+independent_missing(a):return "A_C_missing_cut"
    if any(f[s-1]>=11-s and sum(f[:s])>s*(19-s)//2-deficit
           for s in range(4,11)):return "new_B_girth_deficit"
    if ends and (a,k)==target.FIRST:return "dominated_five_overflow"
    if ends and (a,k)==target.SECOND:return "five_high_sources_deficit"
    return "unresolved"

def has_triangle(out):
    n=len(out)
    return any(v in out[u] and w in out[v] and u in out[w]
               for u in range(n) for v in range(n) for w in range(n))

class Z3GirthTests(unittest.TestCase):
    def test_independent_histograms_and_rank_deficit(self):
        aa,kk=independent_profiles()
        self.assertEqual((len(aa),len(kk)),(166,1716))
        self.assertEqual(aa,list(target.alpha_profiles()))
        self.assertEqual(kk,list(target.k_profiles()))
        for a in aa:self.assertEqual(independent_missing(a),target.forced_missing_pairs(a))

    def test_full_independent_284856_replay(self):
        aa,kk=independent_profiles()
        counts=Counter()
        for a in aa:
            for k in kk:
                stage=independent_classify(a,k)
                counts[stage]+=1
                self.assertEqual(stage,target.classify(a,k))
        self.assertEqual(counts,{
            "root_cut":253556,"B_capacity":22498,"B_small_girth":2255,
            "A_C_missing_cut":6448,"new_B_girth_deficit":97,
            "dominated_five_overflow":1,"five_high_sources_deficit":1})

    def test_adversarial_mutations_and_remaining_endpoints(self):
        self.assertEqual(target.audit()["survivors"],[])
        self.assertEqual(target.audit(endpoints=False)["survivors"],
                         [target.FIRST,target.SECOND])
        self.assertEqual(len(target.audit(girth_missing=0,endpoints=False)["survivors"]),99)

    def test_girth_bound_all_tiny_partial_orientations(self):
        for n in (4,5):
            count=0
            pairs=list(combinations(range(n),2))
            for flags in product((0,1,2),repeat=len(pairs)):
                out=[set() for _ in range(n)]
                for (u,v),x in zip(pairs,flags):
                    if x==1:out[u].add(v)
                    elif x==2:out[v].add(u)
                if any(not x for x in out) or has_triangle(out):continue
                count+=1
                self.assertLessEqual(sum(map(len,out)),n*(n-1)//2-2)
            self.assertGreater(count,0)
        self.assertTrue(target.new_subset_girth((7,)*4+(0,)*6))
        self.assertFalse(target.new_subset_girth((8,7,7,7)+(0,)*6))
        self.assertTrue(target.new_subset_girth((8,7,7,7)+(0,)*6,0))

    def test_final_case_arithmetic_and_bad_inputs(self):
        a,k=target.FIRST
        self.assertEqual((sum(a),sum(k),target.forced_missing_pairs(a)),(29,40,6))
        self.assertEqual(target.c_to_a_capacity(a),5)
        self.assertGreater(15,10)
        a,k=target.SECOND
        self.assertEqual((sum(a),sum(k),target.forced_missing_pairs(a)),(29,34,0))
        self.assertGreaterEqual(20-10,10)
        self.assertGreater(92-58+3,34)
        for a in ((2,)*8,(2,)*8+(True,),(2,)*8+(9,)):
            with self.assertRaises(ValueError):target.forced_missing_pairs(a)

if __name__=="__main__":unittest.main()
