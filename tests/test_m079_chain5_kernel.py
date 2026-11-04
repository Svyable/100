"""Adversarial semantic tests for the chain-plus-five quantitative proof candidate.

Third checker: order ideals of the *explicit relation matrix* of the poset.
It neither uses gap-block weights nor the C++ (chain-prefix, outsider-mask) DP.
"""
from __future__ import annotations

import functools
import itertools
import random
import re
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m079_chain5_kernel as target


def explicit_predecessors(intervals):
    """Build a literal n-element poset relation graph, not a gap-counting DP."""
    lo = min(a for a, _ in intervals)
    hi = max(b for _, b in intervals)
    m = hi - lo
    n = m + 5
    pred = [0] * n
    for t in range(m):
        pred[t] |= (1 << t) - 1
    for i, (a, b) in enumerate(intervals):
        a -= lo
        b -= lo
        pred[m + i] |= (1 << a) - 1
        for t in range(b, m):
            pred[t] |= 1 << (m + i)
    return pred, m


def literal_ideal_count(predecessors):
    """Independent bitmask recursion on all n individual vertices."""
    n = len(predecessors)
    full = (1 << n) - 1

    @functools.lru_cache(None)
    def count(mask):
        if mask == full:
            return 1
        total = 0
        for v in range(n):
            if not (mask & (1 << v)) and (predecessors[v] & ~mask) == 0:
                total += count(mask | (1 << v))
        return total

    return count(0)


def literal_pair_counts(intervals):
    pred, m = explicit_predecessors(intervals)
    e = literal_ideal_count(pred)
    pair = {}
    for i in range(5):
        for j in range(i + 1, 5):
            after = pred.copy()
            after[m + j] |= 1 << (m + i)
            pair[i, j] = literal_ideal_count(after)
        for t in range(m):
            after = pred.copy()
            after[t] |= 1 << (m + i)
            pair[i, 5 + t] = literal_ideal_count(after)
    return e, pair


def parse_instance(output):
    rows = output.splitlines()
    match = re.fullmatch(r"E=(\d+) best=(\d+) delta=(\d+)/(\d+)", rows[0])
    assert match, output
    e, best, num, den = map(int, match.groups())
    assert (e, best) == (den, num)
    pairs = [int(x) for x in rows[1].split("=", 1)[1].split(",") if x]
    weights = [[int(x) for x in row.split("=", 1)[1].split(",") if x]
               for row in rows[2:7]]
    assert len(pairs) == 10 and len(weights) == 5
    return e, best, pairs, weights


class ChainFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="m079_chain5_tests_")
        cls.binary = target.compile_checker(cls.temp.name)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def instance(self, intervals, expected_returncode=0, mutate=False):
        value = ",".join(f"{a}:{b}" for a, b in intervals)
        command = [str(self.binary), "--instance", value]
        if mutate:
            command.append("--mutate-tie")
        return subprocess.run(command, capture_output=True, text=True,
                              check=False)

    def test_full_40355371_two_path_certificate(self):
        result = target.run_census(self.binary, max_length=15, dual=True)
        self.assertEqual(result["cases"], 40_355_371)
        self.assertEqual(result["dual_checked"], result["cases"])
        self.assertEqual(result["minimum"], "562/1405")
        self.assertEqual(result["sharp_multisets"], 1)
        self.assertEqual(result["negative"], 0)
        self.assertEqual(result["first_minimum_witness"],
                         "[-4,0][-1,0][-1,1][0,1][0,4]")
        if target.EXPECTED_FNV64 is not None:
            self.assertEqual(result["fnv64"], target.EXPECTED_FNV64)

    def test_small_residual_and_independent_case_formula(self):
        for length, cases in [(2, 4), (6, 21250), (8, 226135),
                              (10, 1426356), (12, 6421954),
                              (15, 40355371)]:
            self.assertEqual(target.number_of_multisets(length), cases)
        small = target.run_census(self.binary, max_length=6, dual=True)
        self.assertEqual(small["cases"], 21250)
        self.assertEqual(small["minimum"], "562/1405")

    def test_witness_full_relation_matrix(self):
        iv = [(-4, 0), (-1, 0), (-1, 1), (0, 1), (0, 4)]
        result = self.instance(iv)
        self.assertEqual(result.returncode, 0, result.stderr)
        e, best, pairs, weights = parse_instance(result.stdout)
        self.assertEqual((e, best), (1405, 562))
        self.assertEqual(Fraction(best, e), Fraction(2, 5))
        le, counts = literal_pair_counts(iv)
        self.assertEqual(le, e)
        for i in range(5):
            for j in range(i + 1, 5):
                idx = i * (2 * 5 - i - 1) // 2 + j - i - 1
                self.assertEqual(pairs[idx], counts[i, j], (i, j))
            for t in range(len(weights[i]) - 1):
                self.assertEqual(sum(weights[i][:t + 1]),
                                 counts[i, 5 + t], (i, t))
        self.assertEqual(max(min(x, e - x) for x in counts.values()), best)
        self.assertLess(Fraction(2, 5), Fraction(25, 61))

    def test_small_random_relation_matrix_replay(self):
        rng = random.Random(201079)
        tested = 0
        while tested < 20:
            iv = []
            for _ in range(5):
                length = rng.randint(2, 4)
                a = rng.randint(1 - length, 0)
                iv.append((a, a + length - 1))
            if max(a for a, _ in iv) != min(b for _, b in iv):
                continue
            result = self.instance(iv)
            self.assertEqual(result.returncode, 0, result.stderr)
            e, best, pairs, weights = parse_instance(result.stdout)
            le, counts = literal_pair_counts(iv)
            self.assertEqual(e, le)
            self.assertEqual(best, max(min(x, e - x) for x in counts.values()))
            for i in range(5):
                for j in range(i + 1, 5):
                    idx = i * (2 * 5 - i - 1) // 2 + j - i - 1
                    self.assertEqual(pairs[idx], counts[i, j])
            tested += 1

    def test_invalid_scope_is_rejected(self):
        for iv in [
            [(-1, 1)] * 5,  # shared two or more gaps => width six
            [(-1, 0), (0, 1), (-1, 1), (0, 0), (0, 1)],  # singleton
            [(-3, -1), (0, 1), (-1, 1), (0, 2), (0, 1)],  # no common gap
            [(-1, 0), (0, 1), (-1, 1), (0, 2), (2, 1)],  # reversed endpoints
        ]:
            self.assertEqual(self.instance(iv).returncode, 2, iv)

    def test_outsider_relabeling_duality_and_translation(self):
        iv = [(-4, 0), (-1, 0), (-1, 1), (0, 1), (0, 4)]
        baseline = parse_instance(self.instance(iv).stdout)[:2]
        for perm in itertools.permutations(iv):
            self.assertEqual(parse_instance(self.instance(perm).stdout)[:2],
                             baseline)
        dual = [(-b, -a) for a, b in iv]
        translated = [(a + 37, b + 37) for a, b in iv]
        for other in [dual, translated]:
            self.assertEqual(parse_instance(self.instance(other).stdout)[:2],
                             baseline)

    def test_general_k_atom_inequality_exact(self):
        # Exhaust the integer parameter range of the conditional insertion proof.
        for k in range(2, 9):
            for length in range(1, 51):
                bound = Fraction(k, length + k - 1)
                for t in range(k):
                    for s in range(t, k):
                        self.assertLessEqual(Fraction(1 + t, length + s), bound)
            self.assertEqual(2 * k + 1,
                             next(length for length in range(1, 100)
                                  if Fraction(k, length + k - 1) <= Fraction(1, 3)))

    def test_long_interval_symbolic_boundary(self):
        # k=5, L>=16 gives P(gap) <= 5/(L+4) <= 1/4.
        self.assertEqual(Fraction(5, 16 + 4), Fraction(1, 4))
        self.assertGreater(Fraction(5, 15 + 4), Fraction(1, 4))
        iv = [(-15, 0), (-1, 0), (-2, 0), (0, 1), (-1, 1)]
        e, best, _, weights = parse_instance(self.instance(iv).stdout)
        self.assertGreaterEqual(8 * best, 3 * e)
        self.assertLessEqual(4 * max(weights[0]), e)

    def test_same_gap_mutation_detected(self):
        iv = [(-4, 0), (-1, 0), (-1, 1), (0, 1), (0, 4)]
        bad = self.instance(iv, mutate=True)
        self.assertEqual(bad.returncode, 3)
        self.assertIn("mismatch", bad.stderr)

    def test_naive_product_formula_fails(self):
        iv = [(-4, 0), (-1, 0), (-1, 1), (0, 1), (0, 4)]
        e, _, _, _ = parse_instance(self.instance(iv).stdout)
        product = 1
        for a, b in iv:
            product *= b - a + 1
        self.assertNotEqual(e, product)


if __name__ == "__main__":
    unittest.main()
