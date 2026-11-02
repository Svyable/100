"""Adversarial and independently represented checks for M079 eight-outsider seven-gap result."""
import sys
import subprocess
import tempfile
import unittest
from functools import cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m079_chain8_sevengap as mod


class ChainEightSevenGapTests(unittest.TestCase):
    def test_exact_reduction_counts(self):
        self.assertEqual([mod.canonical_count(k) for k in (3, 4, 5, 6, 7)],
                         [406, 10341, 156157, 1604845, 12259764])
        self.assertEqual([mod.canonical_count(k, distinct=True) for k in (5, 6, 7)],
                         [2913, 113145, 1819530])

    def test_independent_forced_relation_on_critical_pairs(self):
        # Fourth representation: direct chain/outsider constraints, then add u<v.
        # No use of C++ gap transitions or Python pair-event recurrence.
        iv = mod.WITNESS
        lo = min(a for a, _ in iv)
        m = max(b for _, b in iv) - lo
        n = m + len(iv)

        def count(extra=None):
            pred = [0] * n
            for j in range(1, m):
                pred[j] |= 1 << (j - 1)
            for i, (a, b) in enumerate(iv):
                if a - lo > 0:
                    pred[m + i] |= 1 << (a - lo - 1)
                for j in range(b - lo, m):
                    pred[j] |= 1 << (m + i)
            if extra is not None:
                u, v = extra
                pred[v] |= 1 << u
            full = (1 << n) - 1

            @cache
            def visit(mask):
                if mask == full:
                    return 1
                return sum(visit(mask | (1 << j)) for j in range(n)
                           if not mask & (1 << j) and not pred[j] & ~mask)
            return visit(0)

        E, B, before = mod.literal_balance(iv)
        self.assertEqual(E, count())
        self.assertEqual((E, B), (939501, 418779))
        for u, v in [(5, 13), (6, 18), (12, 19), (0, 7)]:
            self.assertEqual(count((u, v)), before[u][v])
        self.assertEqual(min(count((5, 13)), E - count((5, 13))), B)

    def test_literal_topological_sort_small(self):
        iv = ((-1, 0),) * 4 + ((0, 1),) * 4
        pred = mod.literal_poset(iv)
        n = len(pred)
        counts = [[0] * n for _ in range(n)]
        order = []
        total = 0

        def visit(mask):
            nonlocal total
            if len(order) == n:
                total += 1
                for i, u in enumerate(order):
                    for v in order[i + 1:]:
                        counts[u][v] += 1
                return
            for v in range(n):
                if not mask & (1 << v) and pred[v] & ~mask == 0:
                    order.append(v)
                    visit(mask | (1 << v))
                    order.pop()

        visit(0)
        E, B, before = mod.literal_balance(iv)
        self.assertEqual(total, E)
        self.assertEqual(counts, before)
        self.assertEqual(2 * B, E)

    def test_cpp_witness_flag_matches_new_seven_gap_witness(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = mod.compile_cpp(Path(tmp))
            proc = subprocess.run([str(binary), "--witness"], check=True,
                                  capture_output=True, text=True)
            self.assertIn("E=939501 best=418779", proc.stdout)

    def test_witness_full_poset(self):
        E, B, before = mod.literal_balance(mod.WITNESS)
        self.assertEqual((E, B), (939501, 418779))
        self.assertTrue(all(before[i][j] + before[j][i] == E
                            for i in range(len(before))
                            for j in range(i + 1, len(before))))

    def test_six_gap_constant_strictly_fails_at_seven(self):
        self.assertTrue(mod.valid(mod.BOUNDARY6, limit=6))
        E, B, _ = mod.literal_balance(mod.BOUNDARY6)
        self.assertEqual((E, B), mod.BOUNDARY6_COUNTS)
        self.assertLess(mod.EXPECTED_MINIMUM[0] * E,
                        B * mod.EXPECTED_MINIMUM[1])

    def test_width_nine_rejected(self):
        self.assertFalse(mod.valid(((-1, 1),) * 8))

    def test_single_gap_rejected(self):
        self.assertFalse(mod.valid(((-1, 0),) * 7 + ((0, 0),)))

    def test_eight_gap_rejected(self):
        self.assertFalse(mod.valid(((-7, 0),) + ((0, 1),) * 7))

    def test_duplicate_automorphism_half_balance(self):
        iv = ((-1, 0),) * 4 + ((0, 1),) * 4
        E, B, _ = mod.literal_balance(iv)
        self.assertEqual(2 * B, E)

    def test_order_duality_self_dual_witness(self):
        dual = tuple(sorted((-b, -a) for a, b in mod.WITNESS))
        self.assertEqual(dual, mod.WITNESS)
        self.assertEqual(mod.literal_balance(dual)[:2],
                         mod.literal_balance(mod.WITNESS)[:2])

    def test_outsider_permutation(self):
        rotated = mod.WITNESS[1:] + mod.WITNESS[:1]
        self.assertEqual(mod.literal_balance(rotated)[:2],
                         mod.literal_balance(mod.WITNESS)[:2])

    def test_quick_checker_with_mutation_and_seven_gap_controls(self):
        summary = mod.check(full=False)
        self.assertEqual(summary["distinct_cases"], 1819530)
        self.assertEqual(summary["minimum"], "418779/939501")
        self.assertGreaterEqual(summary["seven_gap_controls"], 20)
        self.assertTrue(summary["mutation_rejected"])


if __name__ == "__main__":
    unittest.main()
