"""Independent controls for the CH(27,9) z=4, alpha=(2^7,a,8) sink lemma."""
import sys
import unittest
from itertools import combinations, combinations_with_replacement
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch27_z4_sink as sink
import ch27_b_internal as b


def independent_arcs(out):
    """Matrix checker independent of the orientation bitmasks in production."""
    n = len(out)
    a = [[int(j in row) for j in range(n)] for row in out]
    return (sum(sum(row) for row in a),
            tuple(sum(a[i][j] for i in range(n)) for j in range(n)),
            any(a[i][j] and a[j][k] and a[k][i]
                for i in range(n) for j in range(n) for k in range(n)))


def independent_q(alpha, k):
    return len([x for x in alpha if x >= k + 2])


class SharpSixTests(unittest.TestCase):
    def test_sharp_13_arc_positive_witness(self):
        arcs, indeg, triangle = independent_arcs(sink.SIX_SHARP)
        self.assertEqual(arcs, 13)
        self.assertEqual(indeg, (0, 1, 3, 3, 3, 3))
        self.assertFalse(triangle)
        self.assertEqual(sink.graph_facts(sink.SIX_SHARP)["max_indegree"], 3)

    def test_dense_six_orientations(self):
        cert = sink.dense_six_orientation_audit()
        self.assertEqual(cert, {"orientations": 16384,
                                "indegree_cap_survivors": 4512,
                                "triangle_free_and_cap": 0})
        # Independently count indegree-capped orientations from vertex pairs.
        pairs = list(combinations(range(6), 2))
        pairs.remove((0, 1))
        count = 0
        for bits in range(1 << len(pairs)):
            incoming = [0] * 6
            for idx, (u, v) in enumerate(pairs):
                incoming[u if bits & (1 << idx) else v] += 1
            if max(incoming) <= 3:
                count += 1
        self.assertEqual(count, 4512)

    def test_directed_triangle_or_digon_is_rejected(self):
        for graph in (((1,), (0,), (), (), (), ()),
                      ((1,), (2,), (0,), (), (), ())):
            with self.assertRaises(ValueError):
                sink.graph_facts(graph)


class CutAndBoundaryTests(unittest.TestCase):
    def test_all_eligible_q_inequalities(self):
        for a in range(2, 7):
            alpha = tuple(sorted((2,)*7 + (a, 8)))
            self.assertTrue(all(independent_q(alpha, k) <= 7-k
                                for k in range(1, 8)))
        # a=7 changes m=29 and prevents the sixteen-arc equality.
        self.assertEqual(22-7, 15)
        self.assertEqual(22-6, 16)

    def test_all_relaxed_necessary_profiles(self):
        r = sink.report()["by_remaining_A_degree"]
        self.assertEqual(r["6"]["relaxed_profiles_after_B_cuts"], 8)
        self.assertEqual(r["6"]["k_sum_values"], {36: 6, 37: 2})
        self.assertTrue(all(r[str(a)]["relaxed_profiles_after_B_cuts"] == 0
                            for a in range(2, 6)))

    def test_four_previously_unresolved_profiles_now_excluded(self):
        alpha = (2,)*7 + (6, 8)
        chosen = []
        for k in b.k_profiles_with_four_zeros():
            if b.classify(alpha, k) == "z4_sink_cut":
                chosen.append(k)
                self.assertTrue(sink.target_profile(alpha, k))
                cut = sink.b_six_cut(alpha, k)
                self.assertLessEqual(cut["sum_k"], 37)
                self.assertGreaterEqual(cut["C_internal_lower"], 16)
        self.assertEqual(len(chosen), 4)

    def test_a_seven_is_not_excluded(self):
        alpha = (2,)*7 + (7, 8)
        k = (0,)*4 + (5, 6, 6, 6, 7, 7)
        self.assertFalse(sink.target_profile(alpha, k))
        self.assertTrue(sink.eligible_profile(alpha, k))
        self.assertEqual(b.classify(alpha, k), "unresolved")
        self.assertEqual(sink.b_six_cut(alpha, k)["C_internal_lower"], 15)

    def test_inputs_fail_closed(self):
        alpha = (2,)*7 + (6, 8)
        for bad in ((0,)*10, (0,)*4 + (1,)*5 + (8,), (0,)*3+(1,)*7):
            with self.assertRaises(ValueError):
                sink.b_six_cut(alpha, bad)


if __name__ == "__main__":
    unittest.main()
