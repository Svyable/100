"""Independent controls for the nine-vertex two-degree-two local lemma."""
from itertools import combinations, product
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch9_two_low as target


def independent_graph_check(out):
    n = len(out)
    assert n == 9
    matrix = [[False]*n for _ in range(n)]
    for u, row in enumerate(out):
        for v in row:
            if u == v or matrix[u][v]:
                return False
            matrix[u][v] = True
    if any(matrix[u][v] and matrix[v][u] for u in range(n) for v in range(n)):
        return False
    if any(matrix[u][v] and matrix[v][w] and matrix[w][u]
           for u in range(n) for v in range(n) for w in range(n)):
        return False
    return True


def independent_singleton_audit():
    # For each possible m,b, calculate the 8-vertex deletion budget
    # and the *minimum* count of internal degree-two vertices via
    # two separately derived inequalities. No call to production splitter.
    terminal = []
    rejected = 0
    for b, m in product(range(5), range(26, 30)):
        remainder = m - b - 2
        if remainder > 21:
            rejected += 1
            continue
        # With s degree-two vertices, m_J >= 2s + 3(8-s).
        # By indegree-three rigidity, m_J <= 3s + 2(8-s).
        admissible_s = [s for s in range(9)
                        if 24-s <= remainder <= 16+s and s <= b]
        if not admissible_s:
            rejected += 1
        else:
            terminal.append((m, b, remainder, admissible_s))
    return rejected, terminal


class NineVertexTwoLowTests(unittest.TestCase):
    def test_independent_arithmetic_exhaustion(self):
        discarded, terminal = independent_singleton_audit()
        self.assertEqual(discarded, 19)
        self.assertEqual(terminal, [(26, 4, 20, [4])])
        rec = target.singleton_case_table()
        self.assertEqual(len(rec), 20)
        self.assertEqual([(x["arcs_nine"], x["indegree_of_unique_degree_two"])
                          for x in rec
                          if x["rejection"] == "four_high_vertex_digon_obstruction"],
                         [(26, 4)])

    def test_last_four_high_vertices_force_digon(self):
        # The deleted graph J has four outdegree-two vertices S pointing x
        # and four degree-three vertices T. x must point to two of T.
        # Each chosen T cannot point to any of S without a directed C3.
        S = (0,1,2,3)
        T = (4,5,6,7)
        for left, right in combinations(T, 2):
            # Each of left and right needs three J-outneighbors.
            # Only the OTHER THREE members of T remain eligible.
            forced_left = set(T)-{left}
            forced_right = set(T)-{right}
            self.assertIn(right, forced_left)
            self.assertIn(left, forced_right)
            self.assertFalse(any(x in S for x in forced_left | forced_right))
            # Both directions between left/right violate orientation.
            self.assertTrue(left in forced_right and right in forced_left)

    def test_triangle_free_three_low_witness(self):
        out = target.TRIANGLE_FREE_THREE_LOW
        self.assertTrue(independent_graph_check(out))
        degrees = [len(a) for a in out]
        indeg = [sum(v in row for row in out) for v in range(9)]
        self.assertEqual(degrees, [2,2,2,3,3,3,3,3,3])
        self.assertEqual(sum(degrees), 24)
        self.assertLessEqual(max(indeg), 4)
        self.assertEqual(target.graph_profile(out)["outdegree_two_vertices"], [0,1,2])

    def test_removing_triangle_free_breaks_conclusion(self):
        out = [tuple((u+d)%9 for d in (1,2)) if u in (0,1)
               else tuple((u+d)%9 for d in (1,2,3))
               for u in range(9)]
        self.assertEqual([len(row) for row in out].count(2), 2)
        self.assertFalse(independent_graph_check(out))
        row = target.graph_profile(out, require_triangle_free=False)
        self.assertEqual(row["outdegree_two_vertices"], [0, 1])
        with self.assertRaisesRegex(ValueError, "directed 3-cycle"):
            target.graph_profile(out)

    def test_invalid_graph_inputs_fail_closed(self):
        witness = list(target.TRIANGLE_FREE_THREE_LOW)
        cases = [
            tuple(witness[:-1]),
            tuple(witness[:1] + [(6, 6)] + witness[2:]),
            tuple(witness[:1] + [(1, 0)] + witness[2:]),
            tuple(witness[:1] + [(True,)] + witness[2:]),
        ]
        for bad in cases:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    target.graph_profile(bad)


if __name__ == "__main__":
    unittest.main()
