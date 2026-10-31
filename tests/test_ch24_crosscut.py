"""Independent arithmetic / adversarial checks for CH (24,8) cross-cut proof."""
import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch24_crosscut
from ch_six_check import has_triangle


def profiles_independent():
    """Enumerate partitions of <=5 surplus units into eight slots, not combinations_with_replacement."""
    def distribute(slots, remaining, lower):
        if slots == 0:
            if remaining == 0:
                yield ()
            return
        for x in range(lower, remaining + 1):
            yield from ((x,) + rest
                        for rest in distribute(slots - 1, remaining - x, x))
    return {
        tuple(2 + x for x in p)
        for total in range(6)
        for p in distribute(8, total, 0)
        if max(p) <= 5
    }


class CrossCutTests(unittest.TestCase):
    def test_independent_profile_enumeration(self):
        left = set(ch24_crosscut.admissible_profiles())
        right = profiles_independent()
        self.assertEqual(left, right)
        self.assertEqual(len(left), 19)

    def test_full_integer_bound(self):
        result = ch24_crosscut.certificate()
        self.assertEqual(result["ordered_profile_pairs"], 361)
        self.assertEqual(result["maximum_eligible_cross_pairs"], 15)
        self.assertEqual(result["minimum_required_cross_edges"], 22)
        self.assertEqual(result["maximum_allowed_minus_required"], -7)
        self.assertEqual(result["eligible_ge_required_count"], 0)

    def test_sharp_abstract_upper_bound_and_tamper(self):
        alpha = (2, 2, 2, 2, 2, 2, 2, 7)
        self.assertEqual(ch24_crosscut.admissible_cross_pairs(alpha, alpha), 15)
        # Relaxing the sum budget is material: one cannot silently allow
        # profiles with 25 internal arcs while retaining the theorem.
        bad = (2, 2, 2, 2, 2, 2, 6, 7)
        self.assertEqual(sum(bad), 25)
        self.assertGreater(ch24_crosscut.admissible_cross_pairs(bad, bad), 15)

    def test_sharp_21_arc_local_example(self):
        # Z7 with steps {1,2} has 14 arcs, and a new dominating
        # source contributes exactly seven more without creating C3.
        n = 8
        out = [sum(1 << ((u + d) % 7) for d in (1, 2)) for u in range(7)]
        out.append((1 << 7) - 1)
        self.assertEqual(sum(row.bit_count() for row in out), 21)
        self.assertTrue(all(row.bit_count() >= 2 for row in out))
        self.assertFalse(has_triangle(out))
        self.assertEqual(max(sum(out[u] >> v & 1 for u in range(n))
                             for v in range(n)), 3)

    def test_eight_vertex_local_degree_count(self):
        # The local counting inequality for minimum outdegree k forces
        # a+2b <= 13-2k on each vertex of an 8-vertex oriented C3-free graph.
        for k in (2, 3):
            possibilities = [
                (a, b) for a in range(k, 8) for b in range(8 - a)
                if a + 2 * b <= 13 - 2 * k
            ]
            self.assertTrue(possibilities)
            self.assertLessEqual(max(b for _, b in possibilities), 3 if k == 2 else 2)
        self.assertFalse(any(
            3 + 2 * 3 <= 13 - 2 * 3 for _ in range(1)
        ))

    def test_nonvacuous_eight_vertex_local_control(self):
        # Directed circulant on Z8, steps 1,2, has min outdegree two
        # and no directed 3-cycle (sum of three steps <8).
        n = 8
        out = [sum(1 << ((u + d) % n) for d in (1, 2)) for u in range(n)]
        self.assertFalse(has_triangle(out))
        self.assertTrue(all(row.bit_count() == 2 for row in out))


if __name__ == "__main__":
    unittest.main()
