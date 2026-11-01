"""Adversarial and exact controls for M073's monotone unequal-mass wedge result."""
from collections import Counter
from itertools import product
from pathlib import Path
import copy
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import sidorenko_monotone as m
import sidorenko_twoblock as old


def brute(n,edges,a,b,c,P,Q):
    w=((a,b),(b,c))
    mu=(P,Q-P)
    result=0
    for colors in product((0,1),repeat=n):
        term=1
        for x in colors:term*=mu[x]
        for u,v in edges:term*=w[colors[u]][colors[v]]
        result+=term
    return result


class WedgeStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.edges=m.source_edges()
        cls.data=m.read_witness()

    def test_full_exact_witness_and_independent_reconstruction(self):
        self.assertEqual(len(self.edges),66)
        self.assertEqual(m.verify_pairing(self.data),33)
        self.assertEqual(m.construct_pairing(35,self.edges),self.data["wedges"])
        self.assertEqual(Counter(tuple(e) for _,es in self.data["wedges"] for e in es),
                         Counter(self.edges))

    def test_strictness_pair_shares_exactly_one_vertex(self):
        a,b=self.data["wedges"][:2]
        self.assertEqual(a,[0,[[0,13],[0,14]]])
        self.assertEqual(b,[0,[[0,15],[0,16]]])
        self.assertEqual(set(sum(a[1],[]))&set(sum(b[1],[])),{0})

    def test_tampered_pairing_rejected(self):
        def fail(mut):
            bad=copy.deepcopy(self.data);mut(bad)
            with self.assertRaises(ValueError):m.verify_pairing(bad)
        fail(lambda d:d.__setitem__("source_faces_sha256","0"*64))
        fail(lambda d:d.__setitem__("vertices",34))
        fail(lambda d:d["wedges"].pop())
        fail(lambda d:d["wedges"][0][1].__setitem__(1,d["wedges"][0][1][0]))
        fail(lambda d:d["wedges"][0].__setitem__(0,11))
        fail(lambda d:d["wedges"][0][1][0].__setitem__(0,99))
        fail(lambda d:d["wedges"][0][1][0].reverse())
        fail(lambda d:d["wedges"][0][1][0].__setitem__(1,17))

    def test_pairing_algorithm_on_small_graphs_and_invalid_inputs(self):
        for n,edges in ((5,((0,1),(1,2),(2,3),(3,4))),
                        (4,((0,1),(1,2),(2,3),(0,3))),
                        (5,((0,1),(0,2),(0,3),(0,4)))):
            w={"problem_id":"M073","vertices":n,"edges":len(edges),
               "source_faces_sha256":old.FACES_SHA256,
               "wedges":m.construct_pairing(n,edges)}
            self.assertEqual(m.verify_pairing(w,edges,n),len(edges)//2)
        for n,edges in ((3,((0,1),)),(4,((0,1),(2,3))),(3,((0,1),(1,0))),
                        (3,((0,0),(1,2))),(3,((0,1),(0,4)))):
            with self.subTest((n,edges)),self.assertRaises(ValueError):
                m.construct_pairing(n,edges)


class ExactDensityTests(unittest.TestCase):
    def test_independent_face_vs_edges_vs_brute_tiny(self):
        tiny=(
            (3,((0,1,2),)),
            (4,((0,1,2),(0,2,3))),
            (4,((0,1,2),(1,2,3))),
        )
        for points,faces in tiny:
            edges=[(x,points+j) for j,face in enumerate(faces) for x in face]
            for a,b,c,P,Q in ((2,1,0,1,2),(0,1,2,1,3),(2,2,2,2,3),
                               (0,0,0,1,2),(2,1,0,0,2),(1,2,0,1,2)):
                expected=brute(points+len(faces),edges,a,b,c,P,Q)
                with self.subTest(faces=faces,params=(a,b,c,P,Q)):
                    self.assertEqual(expected,m.face_numerator(faces,a,b,c,P,Q,points))
                    self.assertEqual(expected,m.edge_numerator(points+len(faces),edges,a,b,c,P,Q))

    def test_85_preregistered_rational_cases(self):
        result=m.audit()
        self.assertEqual(result["wedges"],33)
        self.assertEqual(result["grid_cases"],85)
        self.assertEqual(result["grid_strict"],42)
        self.assertEqual(result["grid_zero_gap"],43)
        self.assertEqual(result["independent_full_graph_recounts"],4)
        self.assertEqual(result["source_faces_sha256"],old.FACES_SHA256)

    def test_strictness_and_endpoints(self):
        for P,Q in ((0,3),(3,3),(1,3),(2,3),(1,2)):
            for a,b,c in ((2,1,0),(0,1,2),(1,1,1),(2,2,1),(1,0,0)):
                result=m.compare(a,b,c,2,P,Q)
                self.assertEqual(result["strict"],0<P<Q and a!=c)
                self.assertEqual(result["density_gap_numerator"]>0,result["strict"])

    def test_symmetry_under_swapping_classes(self):
        for a,b,c,P,Q in ((3,2,1,1,3),(3,1,0,2,3),(0,2,3,1,2)):
            left=m.compare(a,b,c,3,P,Q)
            right=m.compare(c,b,a,3,Q-P,Q)
            self.assertEqual(left["hom_numerator"],right["hom_numerator"])
            self.assertEqual(left["density_gap_numerator"],right["density_gap_numerator"])

    def test_reject_nonmonotone_but_do_not_claim_counterexample(self):
        for a,b,c,P,Q,D in ((2,0,2,1,2,2),(0,2,0,1,2,2),
                            (0,2,1,1,2,2),(2,0,1,1,2,2)):
            with self.assertRaises(ValueError):
                m.compare(a,b,c,D,P,Q)

    def test_invalid_probabilities_and_boolean_inputs(self):
        for a,b,c,D,P,Q in ((-1,0,0,2,1,2),(3,2,1,2,1,2),
                            (2,1,0,0,1,2),(2,1,0,2,-1,2),
                            (2,1,0,2,3,2),(2,1,0,2,1,0),
                            (True,1,0,2,1,2),(2,1,0,True,1,2),
                            (2,1,0,2,1,False)):
            with self.subTest(params=(a,b,c,D,P,Q)),self.assertRaises(ValueError):
                m.compare(a,b,c,D,P,Q)


if __name__=="__main__":
    unittest.main()
