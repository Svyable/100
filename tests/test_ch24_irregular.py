"""Independent graph-level and tamper checks for M074's degree-two local lemma."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch24_irregular


class CH24IrregularTests(unittest.TestCase):
    def test_sharp_eight_vertex_witness_independently(self):
        graph = ch24_irregular.WITNESS
        # An explicit set-based checker, separate from the script's verifier.
        edges = {(u, v) for u, row in enumerate(graph) for v in row}
        self.assertEqual(len(edges), 20)
        self.assertEqual([len(row) for row in graph], [2] * 4 + [3] * 4)
        self.assertEqual(
            [sum((u, v) in edges for u in range(8)) for v in range(8)],
            [3] * 4 + [2] * 4,
        )
        for u, v in edges:
            self.assertNotIn((v, u), edges)
            for w in range(8):
                self.assertFalse((v, w) in edges and (w, u) in edges)
        self.assertEqual(ch24_irregular.verify_local_graph(graph)["degree_two_vertices"], 4)

    def test_arithmetic_budget(self):
        self.assertEqual(
            [ch24_irregular.budget_lower_bound(m) for m in range(16, 22)],
            [8, 7, 6, 5, 4, 5],
        )
        self.assertEqual(min(ch24_irregular.budget_lower_bound(m)
                             for m in range(16, 22)), 4)
        for bad in (15, 22, 20.1):
            with self.assertRaises(ValueError):
                ch24_irregular.budget_lower_bound(bad)

    def test_reject_digon(self):
        graph = [list(row) for row in ch24_irregular.WITNESS]
        graph[6].append(0)  # 0 -> 6 already exists.
        with self.assertRaisesRegex(ValueError, "digon"):
            ch24_irregular.verify_local_graph(graph)

    def test_reject_directed_triangle(self):
        graph = [list(row) for row in ch24_irregular.WITNESS]
        graph[2].append(0)  # 0 -> 3 -> 2 -> 0.
        with self.assertRaisesRegex(ValueError, "directed triangle"):
            ch24_irregular.verify_local_graph(graph)

    def test_reject_loop(self):
        graph = [list(row) for row in ch24_irregular.WITNESS]
        graph[0].append(0)
        with self.assertRaisesRegex(ValueError, "loop"):
            ch24_irregular.verify_local_graph(graph)


if __name__ == "__main__":
    unittest.main()
