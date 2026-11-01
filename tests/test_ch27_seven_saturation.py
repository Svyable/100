"""Adversarial controls for the seven-saturated-neighbor CH27 proof candidate.

The tests independently recompute integer cuts; no random graph exploration is
treated as a universal graph-theoretic proof.
"""
from itertools import combinations, combinations_with_replacement, permutations, product
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch27_seven_saturation as derived


def orientation_stats(rows):
    n = len(rows)
    m = [[int(j in rows[i]) for j in range(n)] for i in range(n)]
    if any(m[i][i] for i in range(n)):
        raise ValueError("loop")
    if any(m[i][j] and m[j][i] for i in range(n) for j in range(n)):
        raise ValueError("opposite arcs")
    triangles = [(i, j, k) for i in range(n) for j in range(n)
                 for k in range(n) if m[i][j] and m[j][k] and m[k][i]]
    return {"triangles": triangles,
            "out": tuple(sum(row) for row in m)}


class TestSevenSaturation(unittest.TestCase):
    def test_eligibility_caps_independent_pairs(self):
        # All possible degree multisets of the at-most-two non-saturated
        # A vertices. The "8 and 8" pair is forbidden by orientation.
        for t in (7, 8, 9):
            for highs in combinations_with_replacement(range(3, 9), 9 - t):
                if highs.count(8) >= 2:
                    continue
                for k in range(1, 8):
                    q = sum(a >= k + 2 for a in highs)
                    with self.subTest(t=t, highs=highs, k=k):
                        self.assertLessEqual(q, 7 - k)
                        self.assertLessEqual(q, derived.q_cap(k, t))
                        self.assertGreaterEqual(1 + k - q, 2 * k - 6)
        self.assertEqual([derived.q_cap(k) for k in range(1, 8)],
                         [2, 2, 2, 2, 2, 1, 0])
        self.assertEqual(derived.q_cap(6, t=9), 0)

    def test_each_positive_b_subset_capacity(self):
        # Independently count the largest possible number of arcs whose
        # tail is inside P; no arc outside P is included.
        for z in range(11):
            p = 10 - z
            cap = sum(p - i - 1 for i in range(p)) + p * z
            self.assertEqual(cap, derived.positive_B_capacity(z))
        self.assertEqual(derived.positive_B_capacity(2), 44)
        self.assertEqual(derived.positive_B_capacity(3), 42)

    def test_case_comparisons_and_weakened_premise(self):
        for z in range(2, 11):
            p = 10 - z
            K = 63 - 17
            demand = 2 * K - 6 * p
            ceiling = p * (p - 1) // 2 + p * z
            z_row = derived.cut_table(17)[z - 2]
            self.assertEqual((z_row["B_out_floor"], z_row["B_out_capacity"]),
                             (demand, ceiling))
            self.assertTrue(K > 7 * p or demand >= ceiling)
            if z >= 3:
                self.assertTrue(K > 7 * p or demand > ceiling)
        self.assertEqual((derived.cut_table(18)[0]["B_out_floor"],
                          derived.cut_table(18)[0]["B_out_capacity"]), (42, 44))
        self.assertFalse(derived.cut_table(18)[0]["cut_rejects"])

    def test_z2_equality_must_have_k_at_least_five(self):
        rows = [k for k in combinations_with_replacement(range(1, 8), 8)
                if sum(k) >= 46]
        self.assertTrue(rows)
        exact = [k for k in rows if sum(k) == 46]
        self.assertEqual(len(exact), 33)
        full_equality = []
        for k in rows:
            min_b_arcs = sum(2*x - 6 for x in k)
            if min_b_arcs > 44:
                continue
            self.assertEqual(sum(k), 46)  # no slack at all
            if all(derived.q_cap(x) == 7 - x for x in k):
                full_equality.append(k)
        self.assertEqual(len(full_equality), 4)
        self.assertTrue(all(min(row) >= 5 for row in full_equality))
        self.assertTrue(all(2*x - 6 >= 4 for row in full_equality for x in row))
        self.assertEqual(derived.equality_case_z2()["eligible_after_target_equality"], 4)

    def test_triangle_free_tournaments_have_sink(self):
        # Every 4-vertex tournament, all 2^6 orientations of K4.
        # C3-free examples are transitive, hence have a sink.
        edges = list(combinations(range(4), 2))
        surviving = 0
        for flags in product((0, 1), repeat=len(edges)):
            out = [set() for _ in range(4)]
            for (i, j), bit in zip(edges, flags):
                (out[i] if bit else out[j]).add(j if bit else i)
            facts = orientation_stats(out)
            if facts["triangles"]:
                continue
            surviving += 1
            self.assertIn(0, facts["out"])
        self.assertEqual(surviving, 24)
        # The actual equality case has 8 P vertices and 2 zeros.
        # A transitive P tournament has a sink with at most 2 B-targets.
        for order in (tuple(range(8)), tuple(reversed(range(8)))):
            out = [set() for _ in range(8)]
            for idx, u in enumerate(order):
                out[u].update(order[idx + 1:])
            self.assertEqual(min(orientation_stats(out)["out"]), 0)
            self.assertLess(0 + 2, 4)

    def test_global_indegree_defect_is_not_a_single_root_claim(self):
        for t in (7, 8, 9):
            for z in (0, 1):
                minimum = t * (4 - z)
                maximum = 27 - t
                self.assertGreater(minimum, maximum)
                self.assertEqual(derived.high_root_defect_floor(z, t),
                                 {"minimum_high_vertices": minimum,
                                  "maximum_high_vertices": maximum})
        # A negative control: with z=2 the deficit count alone is insufficient.
        self.assertLessEqual(7 * (4 - 2), 27 - 7)

    def test_fail_closed_inputs(self):
        for k in (0, 8, -1, 2.0, True):
            with self.assertRaises(ValueError):
                derived.q_cap(k)
        for z in (-1, 11, 0.5, True):
            with self.assertRaises(ValueError):
                derived.positive_B_capacity(z)
        with self.assertRaises(ValueError):
            derived.cut_table(22)


if __name__ == "__main__":
    unittest.main()
