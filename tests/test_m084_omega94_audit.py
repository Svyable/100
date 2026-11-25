import contextlib
import io
import unittest

from scripts import m084_omega94_audit as audit


class MatrixExponentFormulaTests(unittest.TestCase):
    def test_exact_grid(self):
        self.assertEqual(audit.check(audit.exponent), 216)

    def test_mutation_controls(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            audit.main()
        self.assertIn("4/4 mutants rejected", out.getvalue())

    def test_nonpositive_weights_rejected(self):
        for z in (0, -1):
            with self.assertRaises(ValueError):
                audit.exponent(1, 1, z)


if __name__ == "__main__":
    unittest.main()
