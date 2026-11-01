import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('lean_verify', Path(__file__).resolve().parents[1] / 'scripts/lean_verify.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LeanAuditTests(unittest.TestCase):
    def test_registry(self):
        self.assertEqual(len(m.validate_registry()), 28)

    def test_no_axioms(self):
        self.assertEqual(m.parse_axioms("'Hundred.x' does not depend on any axioms", ['Hundred.x']), {'Hundred.x': []})

    def test_standard_axioms(self):
        m.parse_axioms("'Hundred.x' depends on axioms: [propext, Classical.choice,\n Quot.sound]", ['Hundred.x'])

    def test_reject_untrusted(self):
        for ax in ('sorryAx', 'customAssumption', 'Lean.ofReduceBool', 'x._native.native_decide.ax_1'):
            with self.subTest(ax=ax), self.assertRaises(ValueError):
                m.parse_axioms(f"'Hundred.x' depends on axioms: [{ax}]", ['Hundred.x'])

    def test_missing_unexpected_duplicate(self):
        for output in ('', "'Hundred.y' does not depend on any axioms", "'Hundred.x' does not depend on any axioms\n" * 2):
            with self.subTest(output=output), self.assertRaises(ValueError):
                m.parse_axioms(output, ['Hundred.x'])
