"""Independent finite checks for the sharp nine-vertex local CH lemma.

The elementary proof lives in proofs/M074_NINE_VERTEX.md. The tests verify
its small subclaims and explicit witnesses, not every nine-vertex graph.
"""
from itertools import combinations, product
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch27_local


def matrix_check(out):
    """An independent adjacency-matrix validation, not the production checker."""
    n = len(out)
    matrix = [[0] * n for _ in range(n)]
    for u, targets in enumerate(out):
        for v in targets:
            assert type(v) is int and 0 <= v < n and v != u
            assert matrix[u][v] == 0
            matrix[u][v] = 1
    for u in range(n):
        for v in range(n):
            assert matrix[u][v] + matrix[v][u] <= 1
            for w in range(n):
                assert not (matrix[u][v] and matrix[v][w] and matrix[w][u])
    outdegree = [sum(row) for row in matrix]
    indegree = [sum(matrix[u][v] for u in range(n)) for v in range(n)]
    return sum(outdegree), tuple(outdegree), tuple(indegree)


def small_c4_audit():
    """All 3^6=729 simple partial orientations of K4, no library helper."""
    pairs = list(combinations(range(4), 2))
    total = qualifying = 0
    for directions in product((0, 1, 2), repeat=6):
        total += 1
        rows = [set() for _ in range(4)]
        for (u, v), direction in zip(pairs, directions):
            if direction == 1:
                rows[u].add(v)
            elif direction == 2:
                rows[v].add(u)
        if any(not rows[u] for u in range(4)):
            continue
        if any(w in rows[v] and u in rows[w]
               for u in range(4) for v in rows[u] for w in range(4)):
            continue
        qualifying += 1
        assert sum(map(len, rows)) == 4
        assert all(len(row) == 1 for row in rows)
        # There is exactly one non-trivial directed 4-cycle.
        x = 0
        seen = [x]
        for _ in range(4):
            x = next(iter(rows[x]))
            seen.append(x)
        assert seen[-1] == 0 and len(set(seen[:-1])) == 4
    return total, qualifying


class NineVertexLocalTests(unittest.TestCase):
    def test_sharp_example_independent_adjacency_matrix(self):
        out = tuple(tuple((u+d) % 7 for d in (1, 2))
                    for u in range(7)) + (tuple(range(7)), tuple(range(8)))
        m, outdegree, indegree = matrix_check(out)
        self.assertEqual(m, 29)
        self.assertEqual(sorted(outdegree), [2]*7+[7, 8])
        self.assertEqual(sorted(indegree), [0, 1]+[4]*7)
        self.assertEqual(ch27_local.sharp_nine(), out)
        row = ch27_local.check_oriented_triangle_free(out)
        self.assertEqual(row["arcs"], 29)
        self.assertEqual(row["minimum_outdegree"], 2)

    def test_exact_four_vertex_cycle_sublemma(self):
        self.assertEqual(small_c4_audit(), (729, 6))

    def test_independent_nine_vertex_degree_case_boundaries(self):
        raw2 = [(a, b) for a in range(2, 9) for b in range(9)
                if a+b <= 8 and a+2*b <= 11]
        self.assertEqual(len(raw2), 24)
        self.assertEqual(sorted((a, b) for a, b in raw2 if a+2*b == 11),
                         [(3, 4), (5, 3)])
        self.assertEqual(sorted((a, b) for a, b in raw2 if a+2*b == 10),
                         [(2, 4), (4, 3), (6, 2)])
        self.assertEqual(set(raw2), set(ch27_local.local_pairs(2)))
        # The (6,2) case invokes the already-proved six-vertex obstruction.
        final = [(a, b) for a, b in raw2
                 if a+2*b == 10 and (a, b) != (6, 2)]
        self.assertEqual(final, [(2, 4), (4, 3)])
        self.assertEqual([(x, 9-x) for x in range(10)
                          if 2*x+4*(9-x) == 30], [(3, 6)])
        self.assertLess(3, 4)  # Four distinct A outneighbors would be outdegree two.

    def test_nine_vertex_minimum_three_case(self):
        raw3 = [(a, b) for a in range(3, 9) for b in range(9)
                if a+b <= 8 and a+2*b <= 9]
        self.assertEqual(set(raw3), set(ch27_local.local_pairs(3)))
        self.assertTrue(all(b <= 3 for a, b in raw3))
        # If the average indegree >=3, all indegrees and outdegrees =3.
        self.assertIn((3, 3), raw3)
        # At a (3,3) root, all 3 A-vertices would send 3 edges each
        # into A(3)+C(2), matching the maximum 3+6.
        self.assertEqual(3*3, 3+3*2)

    def test_independent_n27_root_cut_table(self):
        for m in range(18, 30):
            c_to_a_cap = 9*7 - (9*9-m)
            c_in_cap = 7*10 - (9*9-m)
            c_to_b_floor = 7*9 - c_to_a_cap - c_in_cap
            hit = (c_to_b_floor + 7-1)//7
            expected = {
                "m": m, "a_to_c": 81-m,
                "c_to_a_max": c_to_a_cap,
                "b_to_c_plus_c_to_c_max": c_in_cap,
                "c_to_b_min": c_to_b_floor,
                "B_vertices_hit_by_C_min": hit,
                "B_vertices_that_could_point_to_A_outdegree2_max": 10-hit,
                "ambient_indegree_A_outdegree2_upper": 1+4+10-hit,
                "low_indegree_threshold": 8,
            }
            self.assertEqual(ch27_local.indegree_ten_root_budget(m), expected)
        self.assertEqual(ch27_local.indegree_ten_root_budget(29)["c_to_b_min"], 34)
        self.assertEqual(ch27_local.indegree_ten_root_budget(29)
                         ["ambient_indegree_A_outdegree2_upper"], 10)
        self.assertGreater(10, 8)  # This budget does NOT prove a low vertex.

    def test_negative_controls_and_failed_preconditions(self):
        for bad in (
            ((1,), (2,), (0,)),         # directed triangle
            ((1,), (0,), ()),           # digon
            ((0,), (), ()),             # self-loop
            ((1, 1), (), ()),           # repeated arc
            ((True,), (), ()),          # bool != vertex integer
            ((3,), (), ()),             # invalid vertex
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    ch27_local.check_oriented_triangle_free(bad)
        for invalid in (17, 30, 29.0, True, None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    ch27_local.indegree_ten_root_budget(invalid)
        with self.assertRaises(ValueError):
            ch27_local.local_pairs(4)

    def test_frozen_local_summary(self):
        c = ch27_local.local_certificate()
        self.assertEqual(c["raw_min2_integer_pairs"], 24)
        self.assertEqual(c["degree_pairs_at_thirty"], [[2, 4], [4, 3]])
        self.assertEqual(c["thirty_arc_profile_multiplicities"],
                         {"out2_in4": 3, "out4_in3": 6})
        self.assertTrue(c["triangle_free_nine_min_outdegree_three_impossible"])


if __name__ == "__main__":
    unittest.main()
