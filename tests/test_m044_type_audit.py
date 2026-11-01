"""Independent finite sanity and mutation controls for M044 type data."""
import unittest

from scripts.m044_type_audit import (
    MOD, fano_complements, field_tables, gf_mul, projective_audit,
    type_audit, verify_extra_parity,
)


class M044TypeAuditTests(unittest.TestCase):
    def test_full_projective_incidence_census(self):
        self.assertEqual(projective_audit()["incidences"], 16513 * 129)

    def test_fano_type_parities(self):
        self.assertEqual(len(verify_extra_parity()), 7)
        self.assertEqual(type_audit()["A_D_vertices_per_type"], 161)
        self.assertFalse(type_audit()["group_ring_products_checked"])

    def test_tampered_fano_rejected(self):
        bad = fano_complements()
        bad[0].remove(next(iter(bad[0])))
        with self.assertRaises(ValueError):
            verify_extra_parity(bad)

    def test_duplicate_fano_rejected(self):
        bad = fano_complements()
        bad[0] = set(bad[1])
        with self.assertRaises(ValueError):
            verify_extra_parity(bad)

    def test_inadmissible_m_rejected(self):
        for m in (0, 1, 2, 6):
            with self.subTest(m=m), self.assertRaises(ValueError):
                type_audit(m)

    def test_nonfield_polynomial_rejected(self):
        # x^7 + 1 has x+1 as a factor; 0x83 must not be silently swapped.
        with self.assertRaises(ValueError):
            field_tables(0x81)

    def test_field_multiplicative_inverse(self):
        table, inv = field_tables(MOD)
        for a in range(1, 128):
            self.assertEqual(table[a][inv[a]], 1)
            self.assertEqual(gf_mul(a, inv[a]), 1)


if __name__ == "__main__":
    unittest.main()
