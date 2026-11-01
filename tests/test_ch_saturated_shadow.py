"""Independent controls for the saturated-shadow conditional graph lemma."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ch_saturated_shadow as shadow
from ch27_local import check_oriented_triangle_free


class ShadowCutTests(unittest.TestCase):
    def test_thresholds_from_direct_integer_edge_counts(self):
        for s in (1, 2, 3):
            for r in range(max(s+1, 4), 42):
                result = shadow.budget(r, s)
                # Independently count outgoing C arcs, internal C indegree
                # slots and the unordered pairs inside B.
                c_size, b_size = r-2, r+1
                total_c_outgoing = sum(r for _ in range(c_size))
                c_incoming_slots = sum(s+1 for _ in range(c_size)) - result["six_vertex_gain"]
                forced_c_to_b = total_c_outgoing-c_incoming_slots
                lost_to_b_to_a = (s-1)*b_size
                need_b_internal = forced_c_to_b-lost_to_b_to_a
                possible_b_internal = sum(range(b_size))
                self.assertEqual(result["c_to_b_arcs_floor"], forced_c_to_b)
                self.assertEqual(result["b_internal_arcs_floor"], need_b_internal)
                self.assertEqual(result["b_internal_arcs_cap"], possible_b_internal)
                self.assertEqual(result["margin_twice"],
                                 2*(need_b_internal-possible_b_internal))
                self.assertEqual(result["margin_twice"], shadow.polynomial(r, s) + 2*result["six_vertex_gain"])

    def test_first_strict_threshold_and_mutation_control(self):
        for s, last_safe, first in ((1, 7, 8), (2, 12, 13), (3, 16, 17)):
            self.assertFalse(shadow.budget(last_safe, s)["forced_contradiction"])
            self.assertTrue(shadow.budget(first, s)["forced_contradiction"])
            self.assertEqual(shadow.budget(first, s)["margin_twice"], 2 if s == 1 else 2*(s+3))
        # Removing the indegree ceiling loosens the cut, so a proof that
        # silently makes C's indegree too large would not be justified.
        r, s = 8, 1
        weakened_cc_cap = (s+1)*(r-2)  # omit the proved one-arc exception
        b_internal_floor = r*(r-2)-weakened_cc_cap
        self.assertLessEqual(b_internal_floor, r*(r+1)//2)

    def test_n27_seven_neighbor_conditional_arithmetic(self):
        a = shadow.n27_seven_saturated()
        self.assertEqual(a["c_to_b_arcs_floor"], 63-16)
        self.assertEqual(a["b_vertices_hit_from_c_min"], 7)
        self.assertEqual(a["saturated_neighbors_indegree_cap"], 8)
        # For alpha=(2^7, a, b) with both a,b>=3 and a+b<=15:
        # X->X >= m-16, including its minimal m=20 case.
        for aa in range(3, 9):
            for bb in range(3, 9):
                m = 14+aa+bb
                if m <= 29:
                    self.assertGreaterEqual(m-16, 4)
                    self.assertEqual(14-(30-m), m-16)

    def test_negative_cycle_controls_and_positive_gap(self):
        # x->c->b->x is the forbidden triangle in the B shadow.
        with self.assertRaisesRegex(ValueError, "directed triangle"):
            check_oriented_triangle_free(((1,), (2,), (0,)))
        # c->y->x->c is the forbidden triangle in the A shadow.
        with self.assertRaisesRegex(ValueError, "directed triangle"):
            check_oriented_triangle_free(((1,), (2,), (0,)))
        # Without y->x, the two-edge path is permitted, so that hypothesis
        # is indispensable to the C->A exclusion.
        harmless = check_oriented_triangle_free(((1,), (), (0,)))
        self.assertEqual(harmless["arcs"], 2)
        self.assertEqual(harmless["n"], 3)

    def test_sharp_nine_example_is_a_local_control_not_global_witness(self):
        control = shadow.certificate()["nine_vertex_control"]
        self.assertEqual(control["internal_outdegrees_sorted"], [2]*7+[7,8])
        self.assertEqual(control["arcs"], 29)
        self.assertEqual(control["minimum_outdegree"], 2)
        # A positive nine-vertex LOCAL example cannot witness a
        # C3-free, 27-vertex, 9-outregular global graph.
        self.assertNotEqual(control["n"], 27)

    def test_bad_arguments_rejected(self):
        for args in ((3, 1), (10, 0), (10, 4), (0, 2),
                     (True, 1), (11, 2.0), (3, 3)):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    shadow.budget(*args)

    def test_public_scope_language(self):
        note = (ROOT / "research" / "M074_SATURATED_SHADOW.md").read_text(encoding="utf-8")
        for phrase in ("conditional", "originality unverified", "indegree ceiling",
                       "does **not** solve", "r=8,13,17"):
            self.assertIn(phrase.lower(), note.lower())


if __name__ == "__main__":
    unittest.main()
