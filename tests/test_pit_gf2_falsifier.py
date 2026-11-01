import copy
import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pit_gf2_falsifier as pit


class GF2PITFalsifierTests(unittest.TestCase):
    def test_formal_obstruction_full_cube(self):
        c = pit.formal_obstruction()
        r = pit.analyze(c, [[0], [1]])
        self.assertEqual(r["formal_monomials"], [[0], [0, 0]])
        self.assertTrue(r["formal_falsifier"])
        self.assertFalse(r["functional_falsifier"])
        self.assertFalse(r["function_nonzero"])
        self.assertEqual([pit.evaluate(c, [x]) for x in (0, 1)], [0, 0])

    def test_functional_miss_and_full_cube_positive_control(self):
        c = pit.functional_obstruction()
        s = [[0, 0], [0, 1], [1, 0]]
        self.assertTrue(pit.analyze(c, s)["functional_falsifier"])
        self.assertFalse(pit.analyze(c, s + [[1, 1]])["functional_falsifier"])
        self.assertEqual(pit.evaluate(c, [1, 1]), 1)

    def test_cancellation_and_constants(self):
        c = {"n": 1, "gates": [{"op": "xor", "a": "x0", "b": "x0"}]}
        self.assertEqual(pit.formal_polynomial(c), set())
        self.assertFalse(pit.analyze(c, [[0], [1]])["formal_falsifier"])
        c["gates"] = [{"op": "mul", "a": "1", "b": "x0"}]
        self.assertEqual(pit.formal_polynomial(c), {(0,)})
        self.assertEqual(pit.evaluate(c, [1]), 1)

    def test_cross_check_all_two_input_polynomials_of_degree_at_most_two(self):
        # Distinct from circuit replay: monomial parity is evaluated directly.
        atoms = [(), (0,), (1,), (0, 0), (0, 1), (1, 1)]
        for c in [pit.formal_obstruction(), pit.functional_obstruction(),
                  {"n": 2, "gates": [
                      {"op": "mul", "a": "x0", "b": "x0"},
                      {"op": "xor", "a": "g0", "b": "x1"}]},
                  {"n": 2, "gates": [
                      {"op": "mul", "a": "x0", "b": "x1"},
                      {"op": "xor", "a": "g0", "b": "1"}]}]:
            monomials = pit.formal_polynomial(c)
            self.assertTrue(monomials.issubset(set(atoms)))
            for bits in itertools.product((0, 1), repeat=c["n"]):
                direct = 0
                for term in monomials:
                    product = 1
                    for index in term:
                        product &= bits[index]
                    direct ^= product
                self.assertEqual(pit.evaluate(c, bits), direct)

    def test_zero_variable_constant_circuits(self):
        c = {"n": 0, "gates": [{"op": "xor", "a": "0", "b": "1"}]}
        r = pit.analyze(c, [[]])
        self.assertTrue(r["formal_nonzero"])
        self.assertTrue(r["function_nonzero"])
        self.assertFalse(r["vanishes_on_supplied_set"])
        self.assertEqual(pit.formal_polynomial(c), {()})

    def test_rejects_malformed_or_out_of_lock(self):
        base = pit.functional_obstruction()
        invalid = [
            {"n": -1, "gates": base["gates"]},
            {"n": 9, "gates": base["gates"]},
            {"n": True, "gates": base["gates"]},
            {"n": 2, "gates": []},
            {"n": 2, "gates": base["gates"] * 21},
            {"n": 2, "gates": [{"op": "sub", "a": "x0", "b": "x1"}]},
            {"n": 2, "gates": [{"op": "mul", "a": "g0", "b": "x1"}]},
            {"n": 2, "gates": [{"op": "xor", "a": "x2", "b": "x1"}]},
            {"n": 2, "gates": [{"op": "xor", "a": "x00", "b": "x1"}]},
            {"n": 2, "gates": [{"op": "xor", "a": "x0", "b": "x1", "eval": "evil"}]},
            {"n": 2, "gates": [
                {"op": "mul", "a": "x0", "b": "x0"},
                {"op": "mul", "a": "g0", "b": "g0"}]},
            {"n": 2, "gates": [{"op": "mul", "a": "x0", "b": "x1"}], "extra": 1},
        ]
        for c in invalid:
            with self.subTest(c=c), self.assertRaises(ValueError):
                pit.validate(c)

    def test_rejects_bad_points(self):
        c = pit.functional_obstruction()
        for points in [[[0, 0], [0, 0]], [[0, 2]], [[0, True]], [[0]],
                       [[0, 1, 0]], ["00"], None]:
            with self.subTest(points=points), self.assertRaises(ValueError):
                pit.analyze(c, points)

    def test_does_not_assume_degree_of_reduced_polynomial(self):
        c = {"n": 1, "gates": [
            {"op": "xor", "a": "x0", "b": "x0"},
            {"op": "mul", "a": "g0", "b": "x0"},
            {"op": "mul", "a": "g1", "b": "x0"},
            {"op": "mul", "a": "g2", "b": "x0"},
        ]}
        with self.assertRaisesRegex(ValueError, "syntactic degree"):
            pit.validate(c)


if __name__ == "__main__":
    unittest.main()
