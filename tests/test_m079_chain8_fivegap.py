"""Adversarial tests for the bounded eight-outsider balance certificate."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import m079_chain8_fivegap as mod


class ChainEightFiveGapTests(unittest.TestCase):
    def test_canonical_multiset_counts(self):
        self.assertEqual([mod.canonical_count(k) for k in (3, 4, 5)],
                         [406, 10341, 156157])

    def test_independent_forced_relation_all_witness_pairs(self):
        # A fourth exact path: build only direct cover-like constraints,
        # add each proposed u<v relation, and recount all extensions.
        # Does not use the full-poset predecessor matrix or pair-event DP.
        from functools import cache
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

        E = count()
        self.assertEqual(E, 1204824)
        best = 0
        for u in range(n):
            for v in range(u + 1, n):
                uv = count((u, v))
                best = max(best, min(uv, E - uv))
        self.assertEqual(best, 543552)

    def test_literal_topological_sort_enumeration_small(self):
        # Independent literal recursion: count each complete topological sort
        # without forward/backward DP, gap blocks or a recurrence cache.
        intervals = ((-1, 0),) * 4 + ((0, 1),) * 4
        pred = mod.literal_poset(intervals)
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
        E, _, before = mod.literal_balance(intervals)
        self.assertEqual(total, E)
        self.assertEqual(counts, before)

    def test_witness_full_poset(self):
        E, best, before = mod.literal_balance(mod.WITNESS)
        self.assertEqual((E, best), (1204824, 543552))
        self.assertTrue(all(before[i][j] + before[j][i] == E
                            for i in range(len(before))
                            for j in range(i + 1, len(before))))

    def test_six_gap_boundary_falsifies_extension(self):
        self.assertFalse(mod.valid(mod.BOUNDARY6))
        self.assertTrue(mod.valid(mod.BOUNDARY6, limit=6))
        E, B, _ = mod.literal_balance(mod.BOUNDARY6)
        self.assertEqual((E, B), mod.BOUNDARY6_COUNTS)
        self.assertLess(B * mod.EXPECTED_MINIMUM[1], mod.EXPECTED_MINIMUM[0] * E)

    def test_width_nine_rejected(self):
        self.assertFalse(mod.valid(((-1, 1),) * 8))

    def test_single_gap_rejected(self):
        self.assertFalse(mod.valid(((-1, 0),) * 7 + ((0, 0),)))

    def test_long_interval_rejected(self):
        self.assertFalse(mod.valid(((-5, 0),) + ((0, 1),) * 7))

    def test_order_duality(self):
        dual = tuple(sorted((-b, -a) for a, b in mod.WITNESS))
        self.assertTrue(mod.valid(dual))
        self.assertEqual(mod.literal_balance(dual)[:2],
                         mod.literal_balance(mod.WITNESS)[:2])

    def test_outsider_permutation(self):
        rotated = mod.WITNESS[1:] + mod.WITNESS[:1]
        self.assertEqual(mod.literal_balance(rotated)[:2],
                         mod.literal_balance(mod.WITNESS)[:2])

    def test_full_dual_replay(self):
        summary = mod.check()
        self.assertEqual(summary["cases"], 156157)
        self.assertEqual(summary["dual_checked"], 156157)
        self.assertEqual(summary["minimum"], "543552/1204824")
        self.assertTrue(summary["mutation_rejected"])
        self.assertEqual(summary["six_gap_boundary"], "1425408/3193368")


if __name__ == "__main__":
    unittest.main()
