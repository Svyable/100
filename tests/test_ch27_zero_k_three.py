"""Independent and adversarial checks of the CH27 missing-edge propagation."""
import sys
import unittest
from itertools import combinations, product
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import ch27_zero_k_three as z

def comps(n,b):
    if b==1: yield (n,)
    else:
        for x in range(n+1):
            for rem in comps(n-x,b-1): yield (x,)+rem

def independent_profiles():
    aa=set()
    for h in comps(9,7):
        if sum(i*v for i,v in enumerate(h))<=11:
            aa.add(tuple(i+2 for i,v in enumerate(h) for _ in range(v)))
    kk=set((0,)*4+tuple(i+1 for i,v in enumerate(h) for _ in range(v))
           for h in comps(6,7))
    return aa,kk

def second_B_filter(a,k):
    f=sorted((max(0,1+x-sum(y>=x+2 for y in a)) for x in k),reverse=True)
    return (all(sum(f[:s])<=s*(19-s)//2 for s in range(1,11))
            and f[2]<=7 and f[4]<=6 and f[5]<=5)

def triangle_free(edges):
    return not any((u,v) in edges and (v,w) in edges and (w,u) in edges
                   for u in range(5) for v in range(5) for w in range(5))

class ZeroKThreeTests(unittest.TestCase):
    def test_histograms_independently_generated(self):
        a,k=independent_profiles()
        self.assertEqual((len(a),len(k)),(166,924))
        self.assertEqual(a,set(z.alpha_profiles()))
        self.assertEqual(k,set(z.z4_profiles()))

    def test_full_new_audit(self):
        r=z.audit()
        self.assertEqual(r["stages"],{
            "old_cut":149396,"old_B_capacity_or_girth":3693,
            "formerly_unexcluded":295,"newly_excluded":295})
        self.assertEqual(r["new_exclusions_by_max_alpha"],{6:33,7:102,8:160})

    def test_separately_implemented_integer_audit_and_mutation(self):
        A,K=independent_profiles()
        old=new=0
        by_max={}
        for a in A:
            m=sum(a)
            for k in K:
                total=sum(k)
                if total<92-2*m or not second_B_filter(a,k): continue
                old+=1
                p=max(a)
                missing=6 if p==8 else 5 if p==7 else 2 if (p in (5,6) or p==4 and m==29) else 0
                if total>=92-2*m+missing: new+=1
                else: by_max[p]=by_max.get(p,0)+1
        self.assertEqual((old,new),(295,0))
        self.assertEqual(by_max,{6:33,7:102,8:160})
        # Mutation: dropping the new missing-pair inequality restores 295.
        self.assertEqual(old-new,295)

    def test_triangle_defect_all_partial_orientations_on_five_vertices(self):
        pairs=list(combinations(range(5),2))
        checked=0
        for assignment in product(range(3),repeat=len(pairs)):
            E=set()
            for (u,v),choice in zip(pairs,assignment):
                if choice==1: E.add((u,v))
                if choice==2: E.add((v,u))
            if not triangle_free(E): continue
            checked+=1
            for a in range(3):
                for b in range(3):
                    if (a,b) not in E:continue
                    for c in range(3,5):
                        if (b,c) in E and (a,c) not in E:
                            self.assertNotIn((c,a),E)
        self.assertGreater(checked,10000)
        self.assertFalse(triangle_free({(0,1),(1,3),(3,0)}))

    def test_cases_and_wrong_inputs(self):
        self.assertEqual(z.missing_pair_floor((2,)*7+(7,8)),6)
        self.assertEqual(z.missing_pair_floor((2,)*7+(7,7)),5)
        self.assertEqual(z.missing_pair_floor((2,2,3,3,3,3,3,4,6)),2)
        self.assertEqual(z.missing_pair_floor((2,2,3,3,3,4,4,4,4)),2)
        self.assertEqual(z.maximum_C_to_B((2,)*7+(7,8)),37)
        self.assertEqual(z.maximum_C_to_B((2,)*7+(7,7)),36)
        self.assertEqual(z.maximum_C_to_B((2,2,3,3,3,4,4,4,4)),35)
        a=(2,)*7+(6,8)
        k=(0,)*4+(4,6,6,6,7,7)
        self.assertTrue(z.old_B_conditions(a,k))
        self.assertGreater(z.new_cut_gap(a,k),0)
        for a in [(2,)*8,(2,)*8+(True,),(8,8)+(2,)*7]:
            with self.assertRaises(ValueError):z.missing_pair_floor(a)
        with self.assertRaises(ValueError):z.new_cut_gap((2,)*9,(0,)*3+(7,)*7)

if __name__=="__main__":unittest.main()
