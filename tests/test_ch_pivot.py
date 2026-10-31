import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ch_pivot import PivotCNF


class PivotTests(unittest.TestCase):
    def test_clauses_and_frozen_hash(self):
        f = PivotCNF()
        stream = io.BytesIO()
        meta = f.output(stream)
        self.assertEqual(meta["variables"], 3834)
        self.assertEqual(meta["clauses"], 15160)
        self.assertEqual(meta["by_category"]["pivot_symmetry"], 21)
        self.assertEqual(meta["bytes"], 233876)
        self.assertEqual(meta["sha256"],
                         "18f4a672b3294b59202f4656641d361e8e2ca6b9fc63af7a823ee85108825fff")
        self.assertEqual(len(stream.getvalue()), meta["bytes"])
        self.assertEqual(stream.getvalue().count(b"\n") - 4, 15160)

    def test_pivot_unit_template_is_jointly_consistent(self):
        f = PivotCNF()
        arcs = {(0, v) for v in range(1, 7)}
        arcs |= {(v, 0) for v in range(7, 13)}
        arcs |= {(1, 2), (8, 7)}
        arcs |= {(1, v) for v in range(13, 18)}
        arcs |= {(v, 7) for v in range(13, 18)}
        assignment = f.assigned(arcs)
        for clause in f.clauses[-55:]:  # root + pivot unit clauses
            self.assertEqual(len(clause), 1)
            self.assertEqual(assignment[abs(clause[0])], clause[0] > 0)
        self.assertNotIn((7, 1), arcs)


if __name__ == "__main__":
    unittest.main()
