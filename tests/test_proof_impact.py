import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from proof_impact import analyze


def node(oid, deps=(), status='open'):
    return {'id': oid, 'problem_id': 'M001', 'depends_on': list(deps), 'status': status}


class ProofImpactTests(unittest.TestCase):
    def rows(self, entries):
        return {row['id']: row for row in analyze(entries)}

    def test_chain_never_auto_discharges(self):
        rows = self.rows([node('a'), node('b', ['a']), node('c', ['b'])])
        self.assertEqual(rows['a']['downstream_open'], ['b', 'c'])
        self.assertEqual(rows['a']['if_discharged']['newly_runnable'], ['b'])
        self.assertEqual(rows['c']['unmet_ancestors'], ['a', 'b'])
        self.assertIsNone(rows['b']['if_discharged'])

    def test_diamond_deduplicates_and_preserves_conjunction(self):
        entries = [node('a'), node('b', ['a']), node('c', ['a']), node('d', ['b', 'c'])]
        rows = self.rows(entries)
        self.assertEqual(rows['a']['downstream_open'], ['b', 'c', 'd'])
        self.assertEqual(rows['a']['last_missing_for'], ['b', 'c'])
        self.assertEqual(rows['d']['unmet'], ['b', 'c'])
        self.assertEqual(rows['d']['unmet_ancestors'], ['a', 'b', 'c'])

    def test_external_block_preserved(self):
        rows = self.rows([node('a'), node('b', ['a'], 'blocked'), node('c', status='blocked')])
        self.assertEqual(rows['a']['if_discharged'], {'newly_runnable': [], 'newly_external_blocked': ['b']})
        self.assertIsNone(rows['c']['if_discharged'])

    def test_already_discharged_prerequisite(self):
        rows = self.rows([node('a', status='discharged'), node('b'), node('c', ['a', 'b'])])
        self.assertEqual(rows['c']['unmet_ancestors'], ['b'])
        self.assertEqual(rows['b']['last_missing_for'], ['c'])
        self.assertIsNone(rows['a']['if_discharged'])

    def test_deterministic_read_only(self):
        entries = [node('b', ['a']), node('a')]
        before = copy.deepcopy(entries)
        self.assertEqual(analyze(entries), analyze(list(reversed(entries))))
        self.assertEqual(entries, before)
        self.assertEqual(analyze([]), [])


if __name__ == '__main__':
    unittest.main()
