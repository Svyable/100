import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

spec = importlib.util.spec_from_file_location('lean_verify', Path(__file__).resolve().parents[1] / 'scripts/lean_verify.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LeanAuditTests(unittest.TestCase):
    def test_registry(self):
        self.assertEqual(set(m.validate_registry()), set(m.discover_theorems(Path(__file__).resolve().parents[1])))


    def test_public_theorem_discovery_masks_comments_and_private_helpers(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'lean/Hundred/Test.lean'
            source.parent.mkdir(parents=True)
            source.write_text("""namespace Hundred.Test
/- theorem bogus : False := by trivial
   /- lemma nested : False := by trivial -/
-/
-- theorem omitted : False := by trivial
private theorem helper : True := by trivial
@[simp] protected lemma registered : True := by trivial
theorem exported : True := by trivial
end Hundred.Test
""")
            self.assertEqual(set(m.discover_theorems(root)), {
                'Hundred.Test.registered', 'Hundred.Test.exported'
            })

    def test_registration_catches_new_exports_and_stale_names(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'data').mkdir()
            source = root / 'lean/Hundred/Test.lean'
            source.parent.mkdir(parents=True)
            (root / 'data/problems.json').write_text(json.dumps([{'id': 'M001'}]))
            targets = [{
                'id': 'L001', 'problem_id': 'M001', 'stage': 'implemented',
                'statement': 'Small verified example', 'scope_gap': 'Only an example',
                'next_step': 'Extend it', 'declarations': ['Hundred.Test.registered']
            }]
            (root / 'data/lean_targets.json').write_text(json.dumps(targets))
            source.write_text('namespace Hundred.Test\n'
                              'theorem registered : True := by trivial\n'
                              'end Hundred.Test\n')
            self.assertEqual(m.validate_registry(root), ['Hundred.Test.registered'])
            source.write_text('namespace Hundred.Test\n'
                              'theorem registered : True := by trivial\n'
                              'lemma unregistered : True := by trivial\n'
                              'end Hundred.Test\n')
            with self.assertRaisesRegex(ValueError, 'unregistered Lean theorems'):
                m.validate_registry(root)
            targets[0]['declarations'] = ['Hundred.Test.nonexistent']
            (root / 'data/lean_targets.json').write_text(json.dumps(targets))
            source.write_text('namespace Hundred.Test\n'
                              'theorem registered : True := by trivial\n'
                              'end Hundred.Test\n')
            with self.assertRaisesRegex(ValueError, 'unregistered Lean theorems'):
                m.validate_registry(root)

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
