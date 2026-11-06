"""Exact adversarial controls for the M079 seven-outsider eight-gap boundary."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m079_chain7_eightgap as mod


class ChainSevenEightGapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="test_m079_eightgap_")
        cls.binary = mod.compile_cpp(Path(cls.tmp.name))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_canonical_count(self):
        self.assertEqual([mod.canonical_count(k) for k in (6,7,8)],
                         [436680,2612268,12610738])

    def test_old_witness_independent(self):
        old = ((-5,0),(-2,0),(-2,2),(-1,0),(0,1),(0,2),(0,5))
        self.assertEqual(mod.replay_literal(self.binary,old)[:2],(107157,44873))

    def test_invalid_width_singleton_and_long(self):
        self.assertFalse(mod.valid(((-1,1),)*7))
        self.assertFalse(mod.valid(((0,0),)+((-1,0),)*6))
        self.assertFalse(mod.valid(((-7,1),)+((0,1),)*6))

    def test_order_dual(self):
        old = ((-5,0),(-2,0),(-2,2),(-1,0),(0,1),(0,2),(0,5))
        dual = tuple(sorted((-b,-a) for a,b in old))
        self.assertEqual(mod.replay_literal(self.binary,dual)[:2],(107157,44873))

    def test_sampled_full_posets(self):
        for iv in mod.sample_cases():
            self.assertEqual(mod.literal_balance(iv),mod.cpp_instance(self.binary,iv))

    def test_noncentral_gap_atom_inequality(self):
        # Exact all-orders inequality: at a noncentral gap at least one
        # other outsider is forbidden, improving the generic 7/(L+6).
        for iv in mod.sample_cases():
            E,_,_,gaps = mod.literal_balance(iv)
            lo = min(a for a,b in iv)
            for i,(a,b) in enumerate(iv):
                L = b-a+1
                for q,w in enumerate(gaps[i]):
                    if q+lo == 0:
                        self.assertLessEqual(w*(L+6),7*E)
                    else:
                        self.assertLessEqual(w*(L+5),6*E)

    def test_same_gap_mutation_rejected(self):
        old = ((-5,0),(-2,0),(-2,2),(-1,0),(0,1),(0,2),(0,5))
        self.assertIsNone(mod.cpp_instance(self.binary,old,mutation=True))

    def test_widening_is_not_balance_monotone(self):
        old = ((-6,0),(-4,0),(-3,0),(-3,1),(-3,2),(-1,3),(0,4))
        new = ((-6,0),(-4,0),(-3,0),(-3,1),(-3,3),(-1,3),(0,4))
        E,B,*_ = mod.replay_literal(self.binary,old)
        e,b,*_ = mod.replay_literal(self.binary,new)
        self.assertEqual((E,B,e,b),(836706,417008,935968,458980))
        self.assertLess(b*E,B*e)

    def test_short_complete_dual(self):
        p = subprocess.run([str(self.binary),"--max-length","4","--dual"],
                           text=True,capture_output=True,check=True)
        m = mod.SUMMARY.search(p.stderr)
        self.assertIsNotNone(m)
        self.assertEqual((int(m[1]),int(m[2]),int(m[3])),(4887,4887,0))


if __name__ == "__main__":
    unittest.main()
