"""Adversarial checks for the M073 two-spin assortative cone."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/m073_assortative2.py"
spec = importlib.util.spec_from_file_location("m073_assortative2", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestAssortativeTwoBlock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faces = mod.load_faces()
        cls.profiles = mod.histogram(cls.faces)

    @staticmethod
    def direct_T(A, B, C, faces):
        # Independent point-label enumeration, no histogram compression.
        T = 0
        for mask in range(8192):
            term = 1
            for face in faces:
                z = sum(1 for i in face if (mask & (1 << i)) == 0)
                term *= A**z * B**(3-z) + B**z * C**(3-z)
            T += term
        return T

    def test_graph_counts_independent_wedge_count(self):
        degrees = [sum(i in f for f in self.faces) for i in range(13)]
        self.assertEqual(sorted(degrees), [4]*3+[5]*6+[6]*4)
        self.assertEqual(sum(d*(d-1)//2 for d in degrees)+22*3, 204)
        self.assertEqual(mod.graph_counts(self.faces), mod.EXPECTED)
        # Coefficient of s^2*r*p^(m-3) counts paths centered at an edge.
        self.assertEqual(sum(2*d*(d-1) for d in degrees), 552)

    def test_independent_exact_density_path(self):
        for A, B, C in ((0,0,0), (2,2,2), (1,0,1), (5,4,3), (10,10,9)):
            T = self.direct_T(A,B,C,self.faces)
            P,S,R=A+2*B+C,A-C,A-2*B+C
            base,bound=mod.exact_gap(A,B,C,self.profiles)
            self.assertEqual(base,(1<<97)*T-P**66)
            self.assertEqual(bound,(1<<97)*T-(P**66+204*S*S*P**64+
                            33*R**4*P**62+88*R**6*P**60))

    def test_cone_strict_and_constant_equality(self):
        for weights in ((1,0,1),(5,4,3),(3,1,2),(0,0,1)):
            self.assertGreater(mod.exact_gap(*weights,self.profiles)[1],0)
        for x in (0,1,2):
            self.assertEqual(mod.exact_gap(x,x,x,self.profiles),(0,0))

    def test_outside_cone_falsifier_is_not_sidorenko_falsifier(self):
        ordinary,enhanced=mod.exact_gap(10,10,9,self.profiles)
        self.assertGreater(ordinary,0)
        self.assertLess(enhanced,0)
        self.assertLess(10+9,2*10)

    def test_mutated_source_fails_closed(self):
        source=Path(__file__).resolve().parents[1]/"data/reference/sidorenko_faces.json"
        obj=json.loads(source.read_text())
        obj["faces"][0][0]=12
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"bad.json"
            path.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):
                mod.load_faces(path)

    def test_bad_integer_weights_rejected(self):
        for bad in ((-1,0,0),(1,0.5,0),(True,0,0)):
            with self.assertRaises(ValueError):
                mod.exact_gap(*bad,self.profiles)

    def test_histogram_integrity(self):
        self.assertEqual(sum(self.profiles.values()),8192)
        self.assertEqual(len(self.profiles),372)
        self.assertEqual(self.profiles[(0,0,0,22)],1)
        self.assertEqual(self.profiles[(22,0,0,0)],1)


if __name__ == "__main__":
    unittest.main()
