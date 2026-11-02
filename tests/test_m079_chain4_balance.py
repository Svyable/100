"""Adversarial tests for the M079 chain-plus-four restricted balance candidate."""
from __future__ import annotations

import itertools
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import m079_chain4_balance as target


class ChainFourTests(unittest.TestCase):
    def test_two_path_census_smoke(self):
        result = target.census(8)
        self.assertEqual(result["cases"], 21511)
        self.assertEqual(result["minimum"], "25/61")
        self.assertEqual(result["sharp_interval_multisets"], 2)

    def test_full_residual_exhaustive_two_path(self):
        # Replay every finite residual instance, not only the 8-gap smoke.
        # The two C++ counters must agree on all pair numerators, and the
        # ordered 3,456,151-case transcript must match its pinned SHA-256.
        result = target.census(18)
        self.assertEqual(result["cases"], 3456151)
        self.assertEqual(result["minimum"], "25/61")
        self.assertEqual(result["sharp_interval_multisets"], 2)
        self.assertEqual(result["sha256"], target.FULL_SHA256)

    def test_sharp_literal_permutation_witness(self):
        r = target.check_witness()
        self.assertEqual((r["extensions"], r["best_numerator"]), (183, 75))
        self.assertEqual(r["pair_counts"][3, 6], 75)
        self.assertLess(Fraction(25, 61), Fraction(5, 12))
        self.assertGreater(Fraction(25, 61), Fraction(2, 5))

    def test_relabel_outsiders(self):
        witness = target.WITNESS
        baseline = target.literal_permutations(witness)
        for perm in itertools.permutations(range(4)):
            t = tuple(witness[i] for i in perm)
            r = target.literal_permutations(t)
            self.assertEqual((r["extensions"], r["best_numerator"]),
                             (baseline["extensions"], baseline["best_numerator"]))

    def test_order_duality(self):
        dual = tuple((-b, -a) for a, b in target.WITNESS)
        self.assertTrue(target.valid(dual))
        r = target.literal_permutations(dual)
        self.assertEqual((r["extensions"], r["best_numerator"]), (183, 75))

    def test_width_five_rejected(self):
        t = ((-1, 1), (-1, 1), (-1, 1), (-1, 1))
        self.assertFalse(target.valid(t))
        with self.assertRaises(ValueError):
            target.literal_permutations(t)

    def test_single_gap_outsider_rejected(self):
        t = ((0, 0), (-1, 0), (0, 1), (0, 1))
        self.assertFalse(target.valid(t))

    def test_disjoint_intervals_rejected(self):
        t = ((-3, -1), (-1, 0), (0, 1), (0, 1))
        self.assertFalse(target.valid(t))

    def test_bad_interval_rejected(self):
        t = ((1, 0), (-1, 0), (0, 1), (0, 1))
        self.assertFalse(target.valid(t))

    def test_same_gap_multiplicity_is_essential(self):
        r = target.check_witness()
        naive = 1
        for a, b in target.WITNESS:
            naive *= b - a + 1
        self.assertEqual(naive, 60)
        self.assertNotEqual(naive, r["extensions"])

    def test_mutated_same_gap_order_rejected(self):
        source = target.CPP.read_text()
        self.assertIn("out.pair[x][y]+=ways/2", source)
        mutation = source.replace("out.pair[x][y]+=ways/2",
                                  "out.pair[x][y]+=ways", 1)
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "mutant.cpp"
            binary = Path(tmp) / "mutant"
            src.write_text(mutation)
            subprocess.run(["c++", "-O2", "-std=c++17", str(src), "-o", str(binary)],
                           check=True, capture_output=True)
            r = subprocess.run([str(binary), "4"], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("COUNTER DISAGREEMENT", r.stderr)


    def test_witness_has_induced_N_and_three_plus_one(self):
        intervals = target.WITNESS
        lo = min(a for a, _ in intervals)
        hi = max(b for _, b in intervals)
        m = hi - lo
        relations = set()
        for i in range(m):
            for j in range(i + 1, m):
                relations.add((4 + i, 4 + j))
        for i, (a, b) in enumerate(intervals):
            for j in range(a - lo):
                relations.add((4 + j, i))
            for j in range(b - lo, m):
                relations.add((i, 4 + j))
        vertices = range(m + 4)
        has_N = False
        for four in itertools.combinations(vertices, 4):
            induced = {(a, b) for a, b in relations if a in four and b in four}
            for a, b, c, d in itertools.permutations(four):
                if induced == {(a, b), (c, b), (c, d)}:
                    has_N = True
                    break
            if has_N:
                break
        self.assertTrue(has_N)
        self.assertTrue(any(all((4 + q, x) not in relations and
                                (x, 4 + q) not in relations
                                for q in range(3)) for x in range(4)))

    def test_large_interval_threshold_exact(self):
        # For a target a=25/61, atom <=13/(4L) is small enough at L=19,
        # but not at L=18. The residual cutoff is not an arbitrary guess.
        self.assertLessEqual(Fraction(13, 4*19), 1 - 2*Fraction(25, 61))
        self.assertGreater(Fraction(13, 4*18), 1 - 2*Fraction(25, 61))


if __name__ == "__main__":
    unittest.main()
