import json
import random
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import frankl_triple_sat as target


def directly_feasible(members, n=7, k=None):
    try:
        target.independent_check(members, n=n, size=k)
        return True
    except ValueError:
        return False


def fixture():
    obj = json.loads((ROOT / "examples/FRANKL_VAN_DER_HOUT_ROOS_19.json").read_text())
    return [target.set_mask(s, obj["n"]) for s in obj["sets"]]


class TripleSATTests(unittest.TestCase):
    def test_independent_published_nineteen_member_control(self):
        members = fixture()
        result = target.independent_check(members, n=7, size=19)
        self.assertEqual(result["frequencies"], {0: 9, 1: 9, 2: 9})
        self.assertEqual(result["members"], 19)
        self.assertIn("NOT a Frankl counterexample", result["scope"])

    def test_nineteen_control_satisfies_full_encoded_cnf(self):
        members = fixture()
        cnf = target.build(n=7, size=19)
        self.assertTrue(cnf.satisfies(cnf.extend(members)))
        wrong_size = target.build(n=7, size=18)
        self.assertFalse(wrong_size.satisfies(wrong_size.extend(members)))

    def test_exhaustive_three_element_truth_table(self):
        # Includes illegal families: closure, mandatory subset, all three
        # strict inequalities and cardinality must match the independent check.
        for size in (2, 3, 4, 5, 6):
            cnf = target.build(n=3, size=size)
            for mask in range(1 << 8):
                members = [subset for subset in range(8) if mask & (1 << subset)]
                self.assertEqual(cnf.satisfies(cnf.extend(members)),
                                 directly_feasible(members, n=3, k=size),
                                 (size, members))

    def test_four_element_deterministic_fuzz(self):
        rng = random.Random(115)
        for size in (5, 7, 10):
            cnf = target.build(n=4, size=size)
            for _ in range(150):
                members = rng.sample(range(16), rng.randint(0, 16))
                self.assertEqual(cnf.satisfies(cnf.extend(members)),
                                 directly_feasible(members, n=4, k=size))

    def test_tamper_controls(self):
        members = fixture()
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            target.independent_check(members + [members[0]])
        with self.assertRaisesRegex(ValueError, "Element outside"):
            target.set_mask([7], 7)
        with self.assertRaisesRegex(ValueError, "Repeated set"):
            target.set_mask([1, 1], 7)
        with self.assertRaises(ValueError):
            target.independent_check([x for x in members if x != 127], n=7)
        with self.assertRaisesRegex(ValueError, "Family size"):
            target.independent_check(members, n=7, size=18)

    def test_malformed_sat_models_rejected(self):
        cnf = target.build(n=3, size=2)
        with self.assertRaisesRegex(ValueError, "explicit SATISFIABLE"):
            target.parse_solver_model("s UNSATISFIABLE\n", cnf)
        with self.assertRaisesRegex(ValueError, "omits"):
            target.parse_solver_model("s SATISFIABLE\nv 1 2 0\n", cnf)
        with self.assertRaisesRegex(ValueError, "Contradictory"):
            target.parse_solver_model("s SATISFIABLE\nv 1 -1 0\n", cnf)
        with self.assertRaisesRegex(ValueError, "out of range"):
            target.parse_solver_model(f"s SATISFIABLE\nv {cnf.var_count+1} 0\n", cnf)
        all_base = " ".join(str(x) for x in range(1, 9))
        with self.assertRaisesRegex(ValueError, "does not satisfy"):
            target.parse_solver_model("s SATISFIABLE\nv " + all_base + " 0\n", cnf)

    def test_valid_model_parsing_and_aux_tamper(self):
        members = fixture()
        cnf = target.build(7, 19)
        vals = cnf.extend(members)
        output = ("s SATISFIABLE\nv " + " ".join(
            str(i if vals[i] else -i) for i in range(1, cnf.var_count + 1)) + " 0\n")
        self.assertEqual(sorted(target.parse_solver_model(output, cnf)), sorted(members))
        wrong = output.replace(f"{cnf.base_vars + 1} ", f"-{cnf.base_vars + 1} ", 1)
        with self.assertRaises(ValueError):
            target.parse_solver_model(wrong, cnf)

    def test_dimacs_header_and_determinism(self):
        cnf = target.build(4, 7)
        text = cnf.dimacs()
        data = text.splitlines()
        self.assertEqual(data[2], f"p cnf {cnf.var_count} {len(cnf.clauses)}")
        self.assertEqual(len(data), len(cnf.clauses) + 3)
        self.assertEqual(text, target.build(4, 7).dimacs())
        self.assertTrue(all(line.endswith(" 0") for line in data[3:]))
        self.assertTrue(all(c for c in cnf.clauses))

    def test_cli_witness(self):
        out = subprocess.run([sys.executable, "scripts/frankl_triple_sat.py",
                              "--check-witness", "examples/FRANKL_VAN_DER_HOUT_ROOS_19.json"],
                             cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout)["members"], 19)

    def test_invalid_inputs_and_no_false_unsat_claim(self):
        for n, size in ((2, 2), (7, 1), (7, 129)):
            with self.assertRaises(ValueError):
                target.build(n, size)
        cnf = target.build(7, 18)
        self.assertEqual(cnf.base_vars, 128)
        self.assertGreater(len(cnf.clauses), 10000)
        self.assertTrue(cnf.dimacs().startswith("c triple-local"))


if __name__ == "__main__":
    unittest.main()
