"""Arithmetic checks for the elementary (21,7) directed-triangle argument.

The proof is mathematical: these are exact integer guards and a small
control, not an exhaustive 21-vertex digraph search.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ch_six_check import has_triangle


class SevenVertexDegreeTests(unittest.TestCase):
    def test_seven_vertex_counting_forces_indegree_at_most_two(self):
        feasible = []
        for a in range(2, 7):
            for b in range(0, 7 - a):
                c = 6 - a - b
                if 2 * a <= a * (a - 1) // 2 + a * c:
                    feasible.append((a, b))
        self.assertIn((2, 2), feasible)
        self.assertTrue(all(b <= 2 for a, b in feasible))

    def test_sharp_seven_vertex_oriented_control(self):
        arcs = [sum(1 << ((u + d) % 7) for d in (1, 2)) for u in range(7)]
        self.assertFalse(has_triangle(arcs))
        self.assertTrue(all(row.bit_count() == 2 for row in arcs))
        self.assertTrue(all(sum(arcs[u] >> v & 1 for u in range(7)) == 2
                            for v in range(7)))

    def test_indegree_nine_or_more_forces_forbidden_internal_degree(self):
        for b in range(9, 14):
            remaining = 13 - b
            self.assertGreaterEqual(7 - remaining, 3)

    def test_indegree_eight_arc_budget_contradiction(self):
        c_to_b_min = 5 * 7 - 5
        max_b_without_c_predecessor = 8 - (c_to_b_min + 4) // 5
        max_b_to_a = max_b_without_c_predecessor * (7 - 1)
        max_in_a = 7 + 7 * 2 + max_b_to_a
        max_total = 8 + max_in_a + 8 * 8 + 5 * 8
        self.assertEqual(
            (c_to_b_min, max_b_without_c_predecessor, max_b_to_a,
             max_in_a, max_total),
            (30, 2, 12, 33, 145))
        self.assertLess(max_total, 21 * 7)

    def test_regular_case_forces_intersecting_c_sets(self):
        r, c_size, internal_degree = 7, 6, 2
        a_out_to_c = r - internal_degree
        c_in_to_b = r - internal_degree
        self.assertGreater(a_out_to_c + c_in_to_b, c_size)
        max_a_indegree = 1 + internal_degree + (c_size - a_out_to_c)
        self.assertEqual(max_a_indegree, 4)
        self.assertLess(max_a_indegree, r)


if __name__ == "__main__":
    unittest.main()
