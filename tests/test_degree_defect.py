"""Independent small graph audits of the general degree-defect transfer lemma."""
from itertools import combinations, product
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import degree_defect


def independent_audit(n, r):
    """Separate adjacency-matrix count, no call to degree_defect.inspect."""
    options = [list(combinations([v for v in range(n) if v != u], r))
               for u in range(n)]
    tally = dict(total=0, cap=0, high=0, saturated=0,
                 nonsaturated_with_low_arcs=0, regular=0)
    for rows in product(*options):
        tally["total"] += 1
        incoming = [sum(v in row for row in rows) for v in range(n)]
        if max(incoming) > r + 1:
            continue
        tally["cap"] += 1
        high = [i for i in range(n) if incoming[i] == r+1]
        low = [i for i in range(n) if incoming[i] < r]
        if not high:
            tally["regular"] += 1
            self_check = bool(low)
            if self_check:
                raise AssertionError("regular indegrees with a deficit")
            continue
        tally["high"] += 1
        h, ell = len(high), len(low)
        assert h == sum(r-incoming[i] for i in low)
        cut = sum(v in low for u in high for v in rows[u])
        q = min(sum(v in low for v in rows[u]) for u in high)
        assert cut >= q*h
        assert cut <= r*ell-h
        assert (q+1)*h <= r*ell
        low_edges = sum(v in low for u in low for v in rows[u])
        if q >= r-1:
            tally["saturated"] += 1
            assert h == ell
            assert all(incoming[i] == r-1 for i in low)
            assert low_edges == 0
            assert all(v not in low for u in range(n) if u not in high
                       for v in rows[u])
            assert all(sum(v in low for v in rows[u]) == r-1 for u in high)
        elif low_edges:
            tally["nonsaturated_with_low_arcs"] += 1
    return tally


class DegreeDefectTests(unittest.TestCase):
    def test_independent_exhaustive_small_graph_audits(self):
        expected = degree_defect.EXPECTED
        for n, r in ((4, 1), (5, 2)):
            with self.subTest(n=n, r=r):
                key = f"{n},{r}"
                self.assertEqual(independent_audit(n, r), expected[key])
                self.assertEqual(degree_defect.audit(n, r), expected[key])

    def test_saturated_nonregular_example(self):
        # 2-outregular, indegrees (3,2,3,1,2,1), high={0,2}, low={3,5}.
        # Each high sends one arc into low; there is no low-to-low arc.
        out = ((5, 2), (2, 4), (1, 3), (4, 0), (2, 0), (1, 0))
        row = degree_defect.inspect(out)
        self.assertEqual(row["indegrees"], [3, 2, 3, 1, 2, 1])
        self.assertEqual(row["high"], [0, 2])
        self.assertEqual(row["low"], [3, 5])
        self.assertTrue(row["saturated"])
        self.assertEqual((row["high_to_low"], row["nonhigh_to_low"],
                          row["low_to_low"]), (2, 0, 0))

    def test_nonsaturated_case_with_internal_low_arcs(self):
        # Shows that dropping the r-1 high-to-low condition changes the result.
        out = ((5, 4), (2, 0), (4, 3), (4, 2), (1, 3), (3, 2))
        row = degree_defect.inspect(out)
        self.assertEqual(row["indegrees"], [1, 1, 3, 3, 3, 1])
        self.assertEqual(row["q_min"], 0)
        self.assertFalse(row["saturated"])
        self.assertEqual(row["low_to_low"], 2)

    def test_larger_saturated_case(self):
        out = ((2, 1, 4), (4, 3, 0), (6, 3, 5), (2, 4, 0),
               (5, 6, 1), (2, 4, 1), (2, 3, 0))
        row = degree_defect.inspect(out)
        self.assertEqual((row["n"], row["r"]), (7, 3))
        self.assertEqual(row["indegrees"], [3, 3, 4, 3, 4, 2, 2])
        self.assertEqual((row["high"], row["low"]), ([2, 4], [5, 6]))
        self.assertEqual(row["q_min"], 2)
        self.assertTrue(row["saturated"])
        self.assertEqual(row["nonhigh_to_low"], 0)

    def test_excess_indegree_and_invalid_graphs_fail_closed(self):
        too_high = ((3, 5), (4, 2), (5, 0), (2, 4), (2, 3), (4, 2))
        with self.assertRaisesRegex(ValueError, "maximum indegree"):
            degree_defect.inspect(too_high)
        bad = [
            ((1, 1), (0, 2), (0, 1)),
            ((0,), (0,), (1,)),
            ((1,), (0, 2), (0,)),
            ((True,), (0,), (1,)),
            ((1,), (1,), (1,)),
        ]
        for item in bad:
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    degree_defect.inspect(item)
        with self.assertRaises(ValueError):
            degree_defect.audit(24, 8)


if __name__ == "__main__":
    unittest.main()
