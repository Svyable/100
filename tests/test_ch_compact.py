import io
import itertools
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ch_compact


class CompactEncodingTests(unittest.TestCase):
    def test_gate_truth_table(self):
        # Four clauses iff z = a OR (b AND x), independent of any graph.
        for a, b, x, z in itertools.product((False, True), repeat=4):
            clauses = [(not a or z), (not b or not x or z),
                       (not z or a or b), (not z or a or x)]
            self.assertEqual(all(clauses), z == (a or (b and x)))

    def test_exact_degree_and_cycle_constraints_by_exhaustive_arcs(self):
        for n, r in ((3, 1), (4, 2)):
            f = ch_compact.CompactCNF(n, r)
            arcs = list(f.arc)
            for bits in range(1 << len(arcs)):
                chosen = {edge for i, edge in enumerate(arcs) if bits & (1 << i)}
                degrees = [sum((u, v) in chosen for v in range(n) if v != u)
                           for u in range(n)]
                has_digon = any((v, u) in chosen for u, v in chosen)
                has_triangle = any((u, v) in chosen and
                                   (v, w) in chosen and
                                   (w, u) in chosen
                                   for u, v, w in itertools.permutations(range(n), 3))
                exact = all(d == r for d in degrees)
                should_hold = exact and not has_digon and (
                    f.bound < 3 or not has_triangle)
                self.assertEqual(f.holds(f.assigned(chosen)), should_hold,
                                 msg=(n, r, bits))
                if min(degrees) >= r and not has_digon and (
                    f.bound < 3 or not has_triangle):
                    pruned = {(u, v) for u in range(n) for v in
                              sorted(w for w in range(n) if (u, w) in chosen)[:r]}
                    self.assertTrue(f.holds(f.assigned(pruned)))

    def test_compact_fixture_hash_and_size(self):
        f = ch_compact.CompactCNF(18, 6)
        out = io.BytesIO()
        meta = f.output(out)
        self.assertEqual(meta["variables"], 2070)
        self.assertEqual(meta["arc_variables"], 306)
        self.assertEqual(meta["auxiliary_variables"], 1764)
        self.assertEqual(meta["clauses"], 8445)
        self.assertEqual(meta["by_category"], {
            "no_digons": 153, "no_triangles": 1632, "exact_outdegree": 6660
        })
        self.assertEqual(len(out.getvalue()), 127597)
        self.assertEqual(meta["sha256"],
                         "8a2eebf9618bbc9b5dcf2c1fcc5f35736acf852d6466869cb569641fafc00fca")

    def test_reject_unsupported_parameter_ranges(self):
        for n, r in ((18, 2), (31, 15), (3, 0), (5, 5)):
            with self.subTest(n=n, r=r):
                with self.assertRaises(ValueError):
                    ch_compact.CompactCNF(n, r)


if __name__ == "__main__":
    unittest.main()
