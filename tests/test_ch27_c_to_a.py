"""Independent histogram replay for the proposed CH27 C-to-A cut."""
from collections import Counter
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import ch27_b_internal as old
import ch27_c_to_a as new


def histograms(total, bins):
    if bins == 1:
        yield (total,)
    else:
        for x in range(total + 1):
            for tail in histograms(total-x,bins-1):
                yield (x,)+tail


def upper_independent(alpha):
    low = sum(v == 2 for v in alpha)
    high = [v for v in alpha if v>2]
    result=0
    for a in high:
        possible=len(high)-1
        if low and a==8:
            possible=0
        elif low and 8 in high:
            possible-=1
        if a<=possible:
            result+=a-2
    return result


class CToATests(unittest.TestCase):
    def test_complete_independent_histogram_replay(self):
        aa = {tuple(2+i for i,h in enumerate(hist) for _ in range(h))
              for hist in histograms(9,7) if sum(i*h for i,h in enumerate(hist))<=11}
        kk = {(0,)*4+tuple(1+i for i,h in enumerate(hist) for _ in range(h))
              for hist in histograms(6,7)}
        self.assertEqual((len(aa),len(kk)),(166,924))
        self.assertEqual(aa,set(old.alpha_profiles()))
        self.assertEqual(kk,set(old.k_profiles_with_four_zeros()))
        counts=Counter()
        endpoints=Counter()
        previously_excluded_sink = set()
        for a in aa:
            for k in kk:
                if old.classify(a,k)=='z4_sink_cut':
                    # The later sink lemma arrived AFTER the original 288
                    # bottleneck count was frozen. These four *also* fail
                    # C-to-A but have already been classified earlier.
                    lower, upper = new.bound_C_to_A(a,k)
                    self.assertLess(upper, lower)
                    self.assertEqual(new.classify(a,k),'z4_sink_cut')
                    previously_excluded_sink.add((a,k))
                    continue
                if old.classify(a,k)!='unresolved':
                    continue
                lower=max(2,42-sum(k))
                upper=upper_independent(a)
                self.assertEqual((lower,upper),new.bound_C_to_A(a,k))
                if upper<lower:
                    counts['coarse']+=1
                else:
                    endpoints[(a,sum(k))]+=1
                    self.assertNotEqual(new.classify(a,k),'unresolved')
        self.assertEqual(len(previously_excluded_sink),4)
        self.assertEqual(counts['coarse'],284)
        self.assertEqual(counts['coarse']+len(previously_excluded_sink),288)
        self.assertEqual(sum(endpoints.values()),7)
        self.assertEqual(284+4+7,295)
        self.assertEqual(endpoints,{
            ((2,)*3+(3,)*5+(8,),37):1,
            ((2,)*2+(3,)*5+(4,6),34):3,
            ((2,)+(3,)*7+(6,),34):3,
        })

    def test_exact_partition_and_negative_controls(self):
        r=new.report()
        self.assertEqual(r['total_profiles'],153384)
        self.assertEqual(r['survivors'],[])
        self.assertEqual(r['stages']['c_to_a_bottleneck'],284)
        self.assertEqual(r['stages']['z4_sink_cut'],4)
        self.assertEqual(r['stages']['c_to_a_bottleneck'] +
                         r['stages']['z4_sink_cut'] +
                         r['stages']['five_protected_threes_overfill_five_vertices'] +
                         r['stages']['protected_A_forces_C_tournament_sink'] +
                         r['stages']['eight_vertex_degree_defect'],295)
        self.assertEqual(r['stages']['five_protected_threes_overfill_five_vertices'],1)
        self.assertEqual(r['stages']['protected_A_forces_C_tournament_sink'],3)
        self.assertEqual(r['stages']['eight_vertex_degree_defect'],3)
        # A four-profile sink cut is now classified BEFORE C-to-A, although
        # its independent C-to-A lower/upper bounds still contradict.
        sink_a=(2,)*7+(6,8)
        sink_k=(0,)*4+(4,6,6,6,7,7)
        self.assertEqual(old.classify(sink_a,sink_k),'z4_sink_cut')
        self.assertEqual(new.classify(sink_a,sink_k),'z4_sink_cut')
        self.assertEqual(new.bound_C_to_A(sink_a,sink_k),(6,0))
        # A different profile remains a genuine new C-to-A rejection.
        a=(2,)*7+(7,7);k=(0,)*4+(5,5,6,6,7,7)
        self.assertEqual(old.classify(a,k),'unresolved')
        self.assertEqual(new.classify(a,k),'c_to_a_bottleneck')
        self.assertEqual(new.bound_C_to_A(a,k),(6,0))
        for bad_a,bad_k in [(a,k[:-1]),(a,(0,)*3+(1,)*7),((2,)*8+(True,),k)]:
            with self.assertRaises(ValueError):
                new.bound_C_to_A(bad_a,bad_k)

    def test_three_terminal_proof_arithmetic(self):
        self.assertGreater(5*3,5*4//2)
        self.assertGreaterEqual(25-20,5)
        self.assertGreater(6+2+4,10)
        self.assertFalse(any(6+2*b==9 for b in range(8)))
        self.assertGreaterEqual(27-23,4)
        self.assertLess(4+3,8)


if __name__ == '__main__':
    unittest.main()
