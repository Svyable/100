"""Adversarial tests for the bounded M080 GF(2)^4 repeated-basis gate."""
import importlib.util
from pathlib import Path
import unittest
from itertools import permutations
from math import comb

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("m080_repeated", ROOT / "scripts" / "m080_repeated.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class M080RepeatedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bases = m.all_bases()
        cls.reps = m.orbit_representatives(cls.bases)
        cls.data = m.DATA.read_bytes()

    def test_basis_count_independent_determinants(self):
        self.assertEqual(len(self.bases), 840)
        self.assertEqual(len(set(self.bases)), 840)
        self.assertTrue(all(m.determinant(b) for b in self.bases))
        self.assertFalse(m.determinant((1, 2, 3, 4)))
        self.assertTrue(m.determinant((1, 2, 4, 8)))

    def test_full_stabilizer_coverage(self):
        covered = {m.transform_basis(b, p) for b in self.reps for p in m.PERMS}
        self.assertEqual(covered, set(self.bases))
        self.assertEqual(len(self.reps), 51)
        self.assertEqual(len(set(self.reps)), 51)

    def test_burnside_count_and_strata(self):
        table, classes, orbit_counts = m.orbit_table(self.bases)
        self.assertEqual(orbit_counts, (51, 29956, 4111138, 4141145))
        self.assertEqual(sum(classes.values()), 24)
        self.assertEqual(sum(classes[k]*v[4] for k,v in table.items()), 24*4141145)
        self.assertEqual(comb(842, 3), 99137080)
        self.assertEqual(sum(orbit_counts[:3]), orbit_counts[3])

    def test_independent_fixed_power_cycle_counts(self):
        # Independent action check via fixed points of sigma, sigma^2 and sigma^3.
        index = {b:i for i,b in enumerate(self.bases)}
        for p in m.PERMS:
            action = [index[m.transform_basis(b,p)] for b in self.bases]
            f1 = sum(action[i] == i for i in range(840))
            f2 = sum(action[action[i]] == i for i in range(840))
            f3 = sum(action[action[action[i]]] == i for i in range(840))
            c2 = (f2-f1)//2
            c3 = (f3-f1)//3
            self.assertEqual((f2-f1)%2, 0)
            self.assertEqual((f3-f1)%3, 0)
            self.assertEqual((f1,c2,c3), m.EXPECTED_CLASSES[m.cycle_type(p)][:3])

    def test_all_repeated_instances_independent_checker(self):
        self.assertTrue(m.replay_certificate(self.data, self.bases, self.reps))

    def test_tamper_and_shape_rejection(self):
        with self.assertRaises(ValueError):
            m.replay_certificate(self.data[:-1], self.bases, self.reps)
        with self.assertRaises(ValueError):
            m.verify_grid(self.reps[0], self.bases[0], (24,0,0))
        # First row is E; corrupt the three repeated/other rows to all equal:
        # then the columns are rank at most two.
        with self.assertRaises(AssertionError):
            m.verify_grid((1,2,4,8), (1,2,4,8), (0,0,0))
        # A dependent 'other' row is rejected by the independent checker.
        with self.assertRaises(AssertionError):
            m.verify_grid((1,2,4,8), (1,2,3,4), (0,1,2))

    def test_certificate_digest(self):
        from hashlib import sha256
        self.assertEqual(sha256(self.data).hexdigest(),
                         "6cee3dfcf6e5f9359b69d0e1e9244a37c9dd4cdacfa4d2d7c61e30552e5eb24b")


if __name__ == "__main__":
    unittest.main()
