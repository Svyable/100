import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ch_sat


class CHSATTests(unittest.TestCase):
    def test_cnf_matches_independent_graph_checker(self):
        for n, r in ((3, 1), (4, 2)):
            arcs = [(u, v) for u in range(n) for v in range(n) if u != v]
            for mask in range(1 << len(arcs)):
                edges = [list(pair) for i, pair in enumerate(arcs)
                         if mask & (1 << i)]
                self.assertEqual(
                    ch_sat.assignment_satisfies(n, r, edges),
                    ch_sat.verify_arcs(n, r, edges)["is_valid_sat_witness"],
                    msg=(n, r, mask)
                )

    def test_n18_r6_reproducible_formula_hash(self):
        counts = ch_sat.formula_counts(18, 6)
        self.assertEqual(counts["variables"], 306)
        self.assertEqual(counts["no_2cycles"], 153)
        self.assertEqual(counts["no_3cycles"], 1632)
        self.assertEqual(counts["min_degree"], 111384)
        data = io.BytesIO()
        result = ch_sat.encode(18, 6, data)
        self.assertEqual(result["clauses"], 113169)
        self.assertEqual(result["bytes"], 5125375)
        self.assertEqual(
            result["sha256"],
            "32ae7c559724172e1213fbc9ee34053b2d02b791b2db47a6521482d2587f13e2"
        )

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            ch_sat.formula_counts(18, 2)
        with self.assertRaises(ValueError):
            ch_sat.formula_counts(31, 15)


if __name__ == "__main__":
    unittest.main()
