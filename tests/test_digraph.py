import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import digraph


class DigraphTests(unittest.TestCase):
    def test_directed_four_cycle(self):
        c=digraph.check(4,[[0,1],[1,2],[2,3],[3,0]],1)
        self.assertEqual(c["girth"],4)
        self.assertEqual(c["bound"],4)
        self.assertFalse(c["counterexample"])

    def test_dag(self):
        g=digraph.check(4,[[0,1],[1,2],[2,3]],1)
        self.assertIsNone(g["girth"])
        self.assertFalse(g["hypothesis_met"])
        self.assertFalse(g["counterexample"])

    def test_reject_invalid_arcs(self):
        for edges in ([[[0,0]],[[0,4]],[[0,1],[0,1]],[[True,1]]]):
            with self.subTest(edges=edges):
                with self.assertRaises(ValueError):
                    digraph.validate_digraph(4,edges)

    def test_exhaustive_small(self):
        for n in (2,3,4):
            count,eligible=digraph.exhaustive(n)
            self.assertEqual(count,1<<(n*(n-1)))
            self.assertGreater(eligible,0)


if __name__=="__main__":
    unittest.main()
