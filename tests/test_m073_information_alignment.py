"""Controls independent of the spin transform, including edge-subset exhaustion."""
import copy
from itertools import combinations
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import m073_information_alignment as alignment
import sidorenko_regular2 as regular
import sidorenko_twoblock as baseline


def direct_edge_subsets(faces, points):
    edges = [(v, points+j) for j, face in enumerate(faces) for v in face]
    counts = [0] * (len(faces)+1)
    for mask in range(1 << len(edges)):
        odd = set()
        for i, edge in enumerate(edges):
            if mask >> i & 1:
                odd.symmetric_difference_update(edge)
        if not odd:
            counts[mask.bit_count()//2] += 1
    return counts


class InformationAlignmentTests(unittest.TestCase):
    def test_exhaustive_small_hypergraphs(self):
        triples = list(combinations(range(4), 3))
        for mask in range(1 << len(triples)):
            faces = [f for i, f in enumerate(triples) if mask >> i & 1]
            expected = direct_edge_subsets(faces, 4)
            self.assertEqual(alignment.coefficients_by_spins(faces, 4), expected)
            self.assertEqual(alignment.coefficients_by_parity(faces, 4), expected)

    def test_isolates_empty_and_repeated_triples(self):
        for points, faces in ((0, []), (5, []), (5, [(0,1,2)]),
                              (3, [(0,1,2), (0,1,2)])):
            expected = direct_edge_subsets(faces, points)
            self.assertEqual(alignment.coefficients_by_spins(faces, points), expected)
            self.assertEqual(alignment.coefficients_by_parity(faces, points), expected)

    def test_complete_pinned_spectrum(self):
        report = alignment.make_certificate()
        self.assertEqual(report['coefficients'][:7], [1,0,33,88,823,4232,24831])
        self.assertEqual(report['coefficients'][-1], 7805139)
        self.assertEqual(sum(report['coefficients']), 2**32)
        self.assertEqual(sum(report['monochromatic_face_histogram']), 2**13)
        self.assertEqual(report['monochromatic_face_histogram'][0], 96)

    def test_coefficient_and_histogram_tampering(self):
        report = alignment.make_certificate()
        for key, index in (('coefficients',4), ('monochromatic_face_histogram',0)):
            altered = copy.deepcopy(report)
            altered[key][index] += 1
            with self.assertRaises(AssertionError):
                alignment.check_certificate(altered)

    def test_exact_pairwise_graphon_replay(self):
        faces = baseline.read_faces()
        coefficients = alignment.coefficients_by_spins(faces, 13)
        for a,b in ((0,0),(0,1),(1,0),(1,1),(1,3),(3,1)):
            alignment.graphon_replay(coefficients, faces, 13, a, b)
        coefficients[4] += 1
        with self.assertRaises(AssertionError):
            alignment.graphon_replay(coefficients, faces, 13, 1, 3)

    def test_relabeling_and_face_order(self):
        faces = baseline.read_faces()
        relabeled = [tuple(12-v for v in f) for f in reversed(faces)]
        self.assertEqual(alignment.coefficients_by_spins(faces, 13),
                         alignment.coefficients_by_parity(relabeled, 13))

    def test_invalid_domains(self):
        for faces, points in (([(0,0,1)],3), ([(0,1,3)],3),
                              ([(0,1,True)],3), ([(0,1)],3), ([],True)):
            for method in (alignment.coefficients_by_spins, alignment.coefficients_by_parity):
                with self.assertRaises(ValueError):
                    method(faces, points)

    def test_eight_edge_count_is_not_just_simple_cycles(self):
        faces = baseline.read_faces()
        c8 = regular.cycles_by_graph_dfs(35, regular.incidence_edges(faces), 8)
        squares = []
        for u,v in combinations(range(13), 2):
            incident = [j for j,f in enumerate(faces) if u in f and v in f]
            for a,b in combinations(incident,2):
                squares.append(frozenset(((u,a),(v,a),(u,b),(v,b))))
        unions = {a|b for a,b in combinations(squares,2) if not a & b}
        self.assertEqual(c8 + len(unions), 823)
        self.assertLess(c8, 823)


if __name__ == '__main__':
    unittest.main()
