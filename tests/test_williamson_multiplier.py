"""Adversarial controls for the n=29 Williamson multiplier gate."""
import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import williamson_multiplier as wm


class MultiplierGateTests(unittest.TestCase):
    def test_orbits_partition_and_invariance(self):
        for g, sizes in ((12, [1] + [4] * 7), (7, [1, 14, 14]),
                         (28, [1] + [2] * 14)):
            orbits = wm.multiplier_orbits(29, g)
            self.assertEqual(sorted(map(len, orbits)), sorted(sizes))
            self.assertEqual(sorted(x for orbit in orbits for x in orbit),
                             list(range(29)))
            for orbit in orbits:
                for x in orbit:
                    self.assertIn((-x) % 29, orbit)
                    self.assertIn((g * x) % 29, orbit)

    def test_independent_expanded_sequences(self):
        # Directly expand every orbit assignment to 29 signs and recount,
        # without using the row-sum enumeration helper.
        for g in (12, 7):
            orbits = wm.multiplier_orbits(29, g)
            observed = set()
            for assignment in itertools.product((-1, 1), repeat=len(orbits)):
                row = [0] * 29
                for orbit, sign in zip(orbits, assignment):
                    for x in orbit:
                        row[x] = sign
                self.assertTrue(all(x in (-1, 1) for x in row))
                self.assertTrue(all(row[x] == row[(g*x) % 29] ==
                                    row[-x % 29] for x in range(29)))
                observed.add(sum(row))
            self.assertEqual(observed, set(wm.row_sums_from_orbits(orbits)))

    def test_two_restricted_no_go(self):
        for g, eligible in ((12, {-5, -3, 3, 5}), (7, {-1, 1})):
            result = wm.row_sum_screen(29, g)
            self.assertEqual(set(result["eligible_row_sums"]), eligible)
            self.assertTrue(result["row_sum_obstructed"])
            self.assertIsNone(result["four_square_witness"])
            self.assertTrue(wm.independent_n29_gate(g))

    def test_reversal_only_is_not_excluded(self):
        control = wm.row_sum_screen(29, 28)
        self.assertFalse(control["row_sum_obstructed"])
        four = control["four_square_witness"]
        self.assertEqual(sum(s*s for s in four), 116)
        # Passing a necessary test does NOT certify a Williamson quadruple.
        self.assertNotIn("Williamson", control)

    def test_mutations_and_invalid_inputs(self):
        with self.assertRaises(ValueError):
            wm.multiplier_orbits(29, 0)
        with self.assertRaises(ValueError):
            wm.multiplier_orbits(28, 12)
        with self.assertRaises(ValueError):
            wm.independent_n29_gate(28)
        # Tampered orbit sizes can spuriously remove the obstruction:
        # verify the exact orbit partition, not just a guessed row sum.
        true = wm.multiplier_orbits(29, 12)
        fake = (tuple(range(29)),)
        self.assertNotEqual(wm.row_sums_from_orbits(true),
                            wm.row_sums_from_orbits(fake))
        self.assertEqual(sorted(x for o in true for x in o), list(range(29)))

    def test_scope_flags(self):
        result = wm.audit()
        self.assertEqual(result["full_williamson_n29_search"], "NOT PERFORMED")
        self.assertEqual(result["hadamard_116_nonexistence"], "NOT CLAIMED")


if __name__ == "__main__":
    unittest.main()
