"""Adversarial tests for the sharp 2/5 chain-plus-five restricted candidate."""
from __future__ import annotations
import itertools
import random
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m079_chain5_sharp as target
from m079_chain5_sharp_verify import gapblock, literal_balance_sparse

WITNESS = [(-4, 0), (-1, 0), (-1, 1), (0, 1), (0, 4)]

def residual():
    short = [(a, a + L - 1) for L in range(2, 6)
             for a in range(1 - L, 1)]
    for x in range(-15, 1):
        for others in itertools.combinations(short, 4):
            iv = tuple(sorted(((x, x + 15),) + others))
            if max(a for a, b in iv) != 0 or min(b for a, b in iv) != 0:
                continue
            s = sum((Fraction(4, b - a + 4) for a, b in others), Fraction())
            if s > Fraction(11, 4):
                yield iv

class ChainFiveSharpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="m079_sharp_test_")
        cls.binary = Path(cls.tmp.name) / "checker"
        target.compile_checker(cls.binary)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def instance(self, iv):
        arg = ",".join(f"{a}:{b}" for a, b in iv)
        return subprocess.run([str(self.binary), "--instance", arg],
                              capture_output=True, text=True)

    def test_analytic_profile_cutoffs(self):
        self.assertLessEqual(Fraction(21, 5 * 18 + 16), Fraction(1, 5))
        self.assertGreater(Fraction(21, 5 * 17 + 16), Fraction(1, 5))
        self.assertLessEqual(
            (1 + Fraction(44, 15)) / (17 + Fraction(44, 15)), Fraction(1, 5))
        self.assertGreater(
            (1 + Fraction(14, 5)) / (16 + Fraction(14, 5)), Fraction(1, 5))
        self.assertLessEqual(
            (1 + Fraction(8, 3)) / (16 + Fraction(8, 3)), Fraction(1, 5))
        self.assertEqual(target.count_formula(15), 40_355_371)
        self.assertEqual(target.count_formula(17), 112_875_904)

    def test_512_boundary_cases_three_representations(self):
        profiles = {}
        seen = set()
        minimum = Fraction(1)
        for iv in residual():
            self.assertNotIn(iv, seen)
            seen.add(iv)
            lengths = tuple(sorted(b - a + 1 for a, b in iv if b - a + 1 != 16))
            profiles[lengths] = profiles.get(lengths, 0) + 1
            e, best = gapblock(iv)
            self.assertEqual((e, best), literal_balance_sparse(iv))
            self.assertGreaterEqual(5 * best, 2 * e)
            minimum = min(minimum, Fraction(best, e))
        self.assertEqual(profiles, {
            (2, 2, 3, 3): 48, (2, 2, 3, 4): 192,
            (2, 2, 3, 5): 240, (2, 3, 3, 3): 32})
        self.assertEqual(len(seen), 512)
        self.assertEqual(minimum, Fraction(227, 500))

    def test_dual_dp_smoke_and_combinatorial_count(self):
        r = target.run_census(self.binary, 8)
        self.assertEqual(r["cases"], 226_135)
        self.assertEqual(r["exact_base"], 148_421)
        self.assertEqual(r["sharp_base"], 1)
        self.assertEqual(r["fnv64"], target.SMOKE_DIGEST)

    def test_witness_and_wrong_count_negative_control(self):
        self.assertEqual(gapblock(WITNESS), (1405, 562))
        self.assertEqual(literal_balance_sparse(WITNESS), (1405, 562))
        p = self.instance(WITNESS)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout.strip(), "E=1405 best=562")
        self.assertNotEqual(1405, __import__("math").prod(b-a+1 for a,b in WITNESS))

    def test_duality_relabeling_translation(self):
        variants = list(itertools.permutations(WITNESS))[:50]
        variants += [[(-b, -a) for a, b in WITNESS],
                     [(a + 100, b + 100) for a, b in WITNESS]]
        for iv in variants:
            p = self.instance(iv)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(p.stdout.strip(), "E=1405 best=562")

    def test_invalid_scopes_rejected(self):
        for iv in [[(-1, 1)] * 5, [(-1, 0)] * 4 + [(0, 0)],
                   [(-3, -1), (0, 1), (-1, 1), (0, 2), (0, 1)],
                   [(-1, 0), (0, 1), (-1, 1), (0, 2), (2, 1)]]:
            self.assertEqual(self.instance(iv).returncode, 2)

    def test_seeded_three_way_comparison(self):
        rng = random.Random(20261102)
        tested = 0
        for _ in range(600):
            iv = [(-rng.randrange(0, 5), rng.randrange(0, 5))
                  for i in range(5)]
            if any(b-a < 1 for a, b in iv):
                continue
            if max(a for a, b in iv) != 0 or min(b for a, b in iv) != 0:
                continue
            e, best = gapblock(iv)
            self.assertEqual((e, best), literal_balance_sparse(iv))
            p = self.instance(iv)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(p.stdout.strip(), f"E={e} best={best}")
            tested += 1
        self.assertGreaterEqual(tested, 100)

if __name__ == "__main__":
    unittest.main()
