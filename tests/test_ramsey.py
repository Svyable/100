import io
from itertools import combinations
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ramsey


class TestRamseyVerifier(unittest.TestCase):
    def test_c5_certificate(self):
        fixture = json.loads((ROOT / "examples" / "R33_C5.json").read_text())
        self.assertEqual(fixture["format"], ramsey.FORMAT)
        self.assertTrue(ramsey.verify(fixture["n"], fixture["red_edges"], 3, 3)[0])

    def test_explicit_red_and_blue_clique_witnesses(self):
        red = [[0, 1], [0, 2], [1, 2]]
        ok, rh, bh = ramsey.verify(5, red, 3, 3)
        self.assertFalse(ok)
        self.assertEqual(set(rh), {0, 1, 2})
        self.assertIsNotNone(bh)

    def test_reject_malformed_edges(self):
        for edges in ([[[0, 2], [0, 2]], [[1, 1]], [[0, 6]], [[True, 1]], [[2, 0]]]):
            with self.subTest(edges=edges):
                with self.assertRaises(ValueError):
                    ramsey.verify(5, edges, 3, 3)

    def test_sat_encoding_equivalent_to_checker(self):
        n = 4
        edges = list(combinations(range(n), 2))
        clauses = list(ramsey.clauses(n, 3, 3))
        self.assertEqual(len(clauses), 8)
        for bits in range(1 << len(edges)):
            red = [list(e) for i, e in enumerate(edges) if bits & (1 << i)]
            checked = ramsey.verify(n, red, 3, 3)[0]
            sat = all(any((bits & (1 << (abs(lit)-1))) != 0 if lit > 0 else
                          (bits & (1 << (abs(lit)-1))) == 0 for lit in clause)
                      for clause in clauses)
            self.assertEqual(sat, checked)

    def test_dimacs_header(self):
        out = io.StringIO()
        ramsey.dimacs(5, 3, 3, out)
        self.assertIn("p cnf 10 20", out.getvalue())
        with self.assertRaises(ValueError):
            ramsey.dimacs(45, 5, 5, io.StringIO())

    def test_complete_toy_theorem(self):
        self.assertEqual(ramsey.demo(), 32768)


if __name__ == "__main__":
    unittest.main()
