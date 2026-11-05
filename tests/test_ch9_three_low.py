"""Adversarial controls for the sharp nine-vertex three-low LRAT proof."""
import gzip
import random
import tempfile
import unittest
from itertools import combinations
from pathlib import Path

from scripts import ch9_three_low as target


class NineThreeLowTests(unittest.TestCase):
    def test_all_seven_proofs_replay(self):
        report = target.run_check()
        self.assertEqual(set(report["cases"]), set(target.CERT_SHA256))
        self.assertEqual([x["clauses"] for x in report["cases"].values()], [464, 500] + [544] * 5)
        self.assertEqual(report["sharp_witness_arcs"], 24)

    def test_encoding_degree_truth_table(self):
        # The direct cardinality encoding has no auxiliary variables.
        # Test all 2^8 possible rows independently of the SAT solver.
        for low in (False, True):
            for mask in range(256):
                row = {i + 1 for i in range(8) if mask >> i & 1}
                # Separate from the implementation: all 7- or 6-subsets
                # must contain a selected outneighbor; 3-subsets may not
                # all be selected for a designated low vertex.
                lower = all(row.intersection(set(s)) for s in
                            combinations(range(1, 9), 7 if low else 6))
                upper = not low or all(not set(s).issubset(row) for s in
                                       combinations(range(1, 9), 3))
                self.assertEqual(lower and upper,
                                 len(row) == 2 if low else len(row) >= 3)

    def test_clause_semantics_on_random_adjacencies(self):
        # Independent adjacency-matrix evaluator (not the LRAT checker).
        rng = random.Random(20261102)
        for case in target.CERT_SHA256:
            rows = ({0: (1, 2, 3)} if case == "zero_low" else
                    {0: (1, 2)} if case == "one_low" else
                    dict(enumerate(target.CASES[case])))
            clauses = target.formula(case)
            for _ in range(80):
                matrix = [[False] * 9 for _ in range(9)]
                for i in range(9):
                    for j in range(9):
                        if i != j:
                            matrix[i][j] = bool(rng.getrandbits(1))
                values = {target.var(i, j): matrix[i][j]
                          for i in range(9) for j in range(9) if i != j}
                encoded = all(any(values[abs(lit)] == (lit > 0)
                                  for lit in clause) for clause in clauses)
                outdegree = [sum(row) for row in matrix]
                expected_degrees = (
                    outdegree[0] == 3 and min(outdegree[1:]) >= 3
                    if case == "zero_low" else
                    outdegree[0] == 2 and min(outdegree[1:]) >= 3
                    if case == "one_low" else
                    outdegree[0] == outdegree[1] == 2
                    and min(outdegree[2:]) >= 3
                )
                graph_valid = (
                    all(not (matrix[i][j] and matrix[j][i])
                        for i in range(9) for j in range(9))
                    and all(not (matrix[i][j] and matrix[j][k] and matrix[k][i])
                            for i in range(9) for j in range(9) for k in range(9))
                    and expected_degrees
                    and all(tuple(j for j in range(9) if matrix[i][j]) == out
                            for i, out in rows.items())
                )
                self.assertEqual(encoded, graph_valid)

    def test_reject_mutated_lrat_hint(self):
        case = 'edge_overlap'
        source = target.ROOT / (case + '.lrat.gz')
        lines = gzip.decompress(source.read_bytes()).decode().splitlines()
        for i, line in enumerate(lines):
            if ' d ' not in line:
                tokens = line.split()
                tokens[-2] = '999999999'
                lines[i] = ' '.join(tokens)
                break
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'tampered.lrat.gz'
            with gzip.open(path, 'wt') as f:
                f.write('\n'.join(lines) + '\n')
            with self.assertRaises(ValueError):
                target.check_lrat(target.formula(case), path)

    def test_reject_mutated_cnf(self):
        case = 'edge_overlap'
        clauses = target.formula(case)
        # Replace every input clause with a tautology. The original
        # proof's unit-propagation hints can no longer establish conflict.
        changed = [(1, -1)] * len(clauses)
        with self.assertRaises(ValueError):
            target.check_lrat(changed, target.ROOT / (case + '.lrat.gz'))

    def test_sharpness_and_triangle_control(self):
        self.assertTrue(target.verify_witness())
        witness = [list(row) for row in target.WITNESS]
        witness[0].append(1)
        self.assertFalse(target.verify_witness(witness))
        # The circulant with two shortened rows has exactly two lows but
        # contains a directed triangle, so it does not falsify the theorem.
        bad = [tuple((i + j) % 9 for j in ((1, 2) if i < 2 else (1, 2, 3)))
               for i in range(9)]
        self.assertEqual([len(row) for row in bad].count(2), 2)
        self.assertFalse(target.verify_witness(bad))

    def test_five_case_partition(self):
        # Exhaust all ordered pairs of two-element outgoing sets for 0,1,
        # conditional on 1->0 being absent and orientation. Check that
        # the invariant (0->1?, overlap) takes precisely five values.
        seen = set()
        for a in combinations(range(1, 9), 2):
            for b in combinations(range(2, 9), 2):
                if 1 in a:
                    seen.add(('edge', len(set(a) & set(b))))
                else:
                    seen.add(('nonedge', len(set(a) & set(b))))
        self.assertEqual(seen, {('edge', 0), ('edge', 1),
                                ('nonedge', 0), ('nonedge', 1), ('nonedge', 2)})


if __name__ == '__main__':
    unittest.main()
