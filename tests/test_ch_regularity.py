"""Finite checks of the algebraic reduction and the stronger CNF encoding."""
import io
import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch_regularity


class RegularityTests(unittest.TestCase):
    def test_six_vertex_counting_inequality_forces_indegree_at_most_one(self):
        # In any oriented digraph on 6 vertices with min outdegree 2 and
        # no 3-cycle, for every v, a=outdegree(v), b=indegree(v),
        # 2a <= a(a-1)/2 + a(5-a-b), hence a+2b <=5.
        # For a>=2 this forces b<=1, contradicting global degree sums.
        options = [(a, b) for a in range(2, 6) for b in range(6-a)
                   if 2*a <= a*(a-1)//2 + a*(5-a-b)]
        self.assertTrue(options)
        self.assertTrue(all(b <= 1 for a, b in options))
        self.assertGreater(6 * 2, 6 * 1)

    def test_regular_cnf_counts_and_hash(self):
        f = ch_regularity.RegularCNF()
        out = io.BytesIO()
        meta = f.output(out)
        self.assertEqual(meta["variables"], 3834)
        self.assertEqual(meta["clauses"], 15139)
        self.assertEqual(meta["by_category"], {
            "no_digons": 153, "no_triangles": 1632,
            "exact_outdegree": 6660, "exact_indegree": 6660,
            "root_symmetry": 34,
        })
        self.assertEqual(out.getvalue().count(b"\n") - 3, meta["clauses"])
        self.assertEqual(len(out.getvalue()), meta["bytes"])

    def test_incoming_cardinality_gates(self):
        f = ch_regularity.RegularCNF()
        circulant = {(u, (u+d) % 18) for u in range(18) for d in range(1, 7)}
        choices = [set(), circulant, {(u, (u+1) % 18) for u in range(18)},
                   {(u, v) for u in range(18) for v in range(18) if u != v}]
        for edges in choices:
            assignment = f.assigned(edges)
            degree_clauses = f.clauses[8445:8445 + 6660]
            holds = all(any(assignment[abs(lit)] == (lit > 0) for lit in clause)
                        for clause in degree_clauses)
            self.assertEqual(holds, all(sum((u, v) in edges for u in range(18) if u != v) == 6
                                        for v in range(18)))
            self.assertEqual(len(assignment), f.next_var - 1)

    def test_root_relabeling_preserves_arcs_and_pins_star(self):
        edges = {(u, (u+d) % 18) for u in range(18) for d in range(1, 7)}
        pinned, mapping = ch_regularity.relabel_root(edges, root=11)
        self.assertEqual(len(mapping), 18)
        self.assertEqual(mapping[11], 0)
        self.assertEqual(len(pinned), len(edges))
        f = ch_regularity.RegularCNF()
        assignment = f.assigned(pinned)
        symmetry_clauses = f.clauses[-34:]
        self.assertTrue(all(any(assignment[abs(lit)] == (lit > 0) for lit in clause)
                            for clause in symmetry_clauses))
        self.assertEqual([sum((u, v) in pinned for v in range(18) if u != v)
                          for u in range(18)], [6]*18)
        self.assertEqual([sum((u, v) in pinned for u in range(18) if u != v)
                          for v in range(18)], [6]*18)

    def test_invalid_root(self):
        with self.assertRaises(ValueError):
            ch_regularity.relabel_root([(0, 1)], root=0)
        with self.assertRaises(TypeError):
            ch_regularity.RegularCNF(fix_root=1)


if __name__ == "__main__":
    unittest.main()
