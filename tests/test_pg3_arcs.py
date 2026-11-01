"""Exact adversarial tests for M093 PG(3,q) frame enumeration."""
import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pg3_arcs as a


class PG3ArcTests(unittest.TestCase):
    def test_all_supported_fields_are_fields(self):
        for q in a.FIELDS:
            f = a.Field(q)
            for x in range(q):
                self.assertEqual(f.add[x][f.neg[x]], 0)
                if x:
                    self.assertEqual(f.mul[x][f.inv[x]], 1)
                for y in range(q):
                    self.assertEqual(f.mul[x][y], f.mul[y][x])
                    for z in range(q):
                        self.assertEqual(f.mul[x][f.add[y][z]],
                                         f.add[f.mul[x][y]][f.mul[x][z]])

    def test_non_prime_power_rejected(self):
        with self.assertRaises(ValueError):
            a.Field(6)

    def test_frame_and_candidate_counts(self):
        for q in a.FIELDS:
            f = a.Field(q)
            self.assertTrue(a.is_arc(f, a.FRAME, "permutation"))
            cs = a.candidates(f)
            self.assertEqual(len(cs), max(0, (q-2)*(q-3)*(q-4)))
            for v in cs:
                self.assertTrue(a.is_arc(f, a.FRAME+(v,)))

    def test_independent_determinant_path(self):
        for q in a.FIELDS:
            f = a.Field(q)
            vectors = a.FRAME + tuple(a.candidates(f)[:3])
            for rows in itertools.combinations(vectors, 4):
                self.assertEqual(f.determinant(rows),
                                 f.determinant_permutation(rows))

    def test_complete_low_field_brute_force(self):
        f = a.Field(2)
        points = [tuple((n >> i) & 1 for i in range(4))
                  for n in range(1, 16)]
        self.assertEqual(sum(a.is_arc(f, s)
                             for s in itertools.combinations(points, 5)), 168)
        self.assertEqual(sum(a.is_arc(f, s)
                             for s in itertools.combinations(points, 6)), 0)

    def test_all_q_maxima_exact(self):
        for q, n in [(2, 5), (3, 5), (4, 5), (5, 6),
                     (7, 8), (8, 9), (9, 10)]:
            with self.subTest(q=q):
                result = a.run(q)
                self.assertEqual(result["lower_bound"], n)
                self.assertEqual(result["upper_target"], n+1)
                self.assertEqual(result["upper_status"], "UNSAT")
                self.assertTrue(a.is_arc(a.Field(q), result["witness"],
                                         "permutation"))

    def test_tamper_controls(self):
        f = a.Field(8)
        good = a.run(8)["witness"]
        self.assertTrue(a.is_arc(f, good))
        self.assertFalse(a.is_arc(f, good + (good[0],), "permutation"))
        bad = [list(v) for v in good]
        bad[5] = list(good[0])
        self.assertFalse(a.is_arc(f, bad, "permutation"))

    def test_cutoff_never_reports_unsat(self):
        r = a.search(a.Field(9), 6, max_nodes=1000)
        self.assertEqual(r["status"], "UNKNOWN")
        self.assertIsNone(r["witness"])


if __name__ == "__main__":
    unittest.main()
