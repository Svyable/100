"""Adversarial exact tests for the all-rank one-exceptional-row Rota theorem.

A paper/Lean proof covers all ranks. These finite tests *only* challenge
implementation, boundary assumptions, exact counts and independent algorithms.
"""
import itertools
import json
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import m080_one_exceptional as m


class OneExceptionalTests(unittest.TestCase):
    def test_six_committed_fixtures(self):
        self.assertEqual(json.loads(m.CERT.read_text()), m.certificate())
        self.assertEqual(m.main(["--check"]), 0)
        rows = m.certificate()["examples"]
        self.assertEqual([x["status"] for x in rows],
                         ["grid", "grid", "hall_obstruction", "grid", "grid", "grid"])
        self.assertEqual([x["support_permanent"] for x in rows],
                         [1, 4, 0, 2, 24, 2])
        self.assertEqual([x.get("grid_count_formula") for x in rows],
                         [24, 96, 0, 48, 576, None])
        self.assertEqual([x.get("grid_count_independent") for x in rows],
                         [24, 96, 0, 48, 576, None])

    def test_latin_first_row_counts_directly(self):
        self.assertEqual([m.latin_fixed_first(n) for n in range(1, 5)],
                         [1, 1, 2, 24])
        with self.assertRaises(ValueError):
            m.latin_fixed_first(5)

    def test_support_from_two_independent_algorithms(self):
        for _, p, B, C in m.examples():
            self.assertEqual(m.exchange_masks(B, C, p),
                             m.independent_support_masks(B, C, p))
            masks = m.exchange_masks(B, C, p)
            self.assertEqual(m.support_permanent(masks), m.brute_permanent(masks))
            match = m.find_matching(masks)
            self.assertEqual(match is not None, m.support_permanent(masks) > 0)
            if match is not None:
                self.assertEqual(len(set(match)), len(match))
                self.assertTrue(all(masks[j] >> match[j] & 1
                                    for j in range(len(match))))

    def test_dependent_row_can_still_admit_a_grid(self):
        p, B, C = m.examples()[1][1:]
        self.assertFalse(m.independent(C, p))
        result = m.construct(B, C, p)
        self.assertEqual(result["support_permanent"], 4)
        self.assertTrue(m.verify_grid(B, C, p, result["rows"]))
        self.assertEqual(m.brute_grid_count(B, C, p), 96)

    def test_hall_deficiency_detected_even_for_large_rank(self):
        for n in (4, 12):
            B = m.identity(n)
            C = (B[0],) * (n - 1) + (B[1],)
            result = m.construct(B, C, 2)
            self.assertEqual(result["status"], "hall_obstruction")
            self.assertEqual(result["support_permanent"], 0)
            witness = result["hall_obstruction"]
            S = set(witness["columns"])
            N = {i for j in S for i in range(n) if result["support_masks"][j] >> i & 1}
            self.assertEqual(N, set(witness["neighbor_indices"]))
            self.assertLess(len(N), len(S))
        with self.assertRaises(ValueError):
            m.hall_obstruction([1, 2])

    def test_random_invertible_exceptional_basis_always_matches(self):
        rng = random.Random(8080)
        for p in (2, 3, 5, 7):
            for n in (1, 2, 3, 4, 5):
                B = m.identity(n)
                for _ in range(4):
                    for _ in range(200):
                        C = tuple(tuple(rng.randrange(p) for _ in range(n))
                                  for _ in range(n))
                        if m.independent(C, p):
                            break
                    else:
                        self.fail("failed to sample invertible exceptional basis")
                    out = m.construct(B, C, p)
                    self.assertEqual(out["status"], "grid")
                    self.assertGreaterEqual(out["support_permanent"], 1)
                    self.assertTrue(m.verify_grid(B, C, p, out["rows"]))
                    self.assertEqual(m.exchange_masks(B, C, p),
                                     m.independent_support_masks(B, C, p))

    def test_nonstandard_basis_and_five_rank_grid(self):
        for ex in m.examples()[3:]:
            _, p, B, C = ex
            self.assertNotEqual(B, ())
            result = m.construct(B, C, p)
            self.assertEqual(result["status"], "grid")
            self.assertTrue(m.verify_grid(B, C, p, result["rows"]))
            self.assertTrue(m.independent(C, p))

    def test_sharp_all_rank_bound_both_ends(self):
        # I+J has determinant n+1 and all nonzero coordinates over GF(11).
        import math
        for n in range(1, 7):
            B = m.identity(n)
            C = tuple(tuple(1 + int(i == j) for i in range(n))
                      for j in range(n))
            self.assertTrue(m.independent(C, 11))
            out = m.construct(B, C, 11)
            self.assertEqual(out["status"], "grid")
            self.assertEqual(out["support_permanent"], math.factorial(n))
            self.assertEqual(out["support_masks"], [(1 << n) - 1] * n)
            self.assertEqual(m.independent_support_masks(B, C, 11),
                             tuple([(1 << n) - 1] * n))
            if n <= 4:
                self.assertEqual(m.brute_grid_count(B, C, 11),
                                 math.factorial(n) * m.latin_fixed_first(n))
            lower = m.construct(B, B, 11)
            self.assertEqual(lower["support_permanent"], 1)

    def test_all_gf2_rank3_exceptional_rows(self):
        # 8^3 = 512 arbitrary exceptional rows, not only second bases.
        B = m.identity(3)
        vectors = tuple(itertools.product(range(2), repeat=3))
        for C in itertools.product(vectors, repeat=3):
            masks = m.exchange_masks(B, C, 2)
            count = m.support_permanent(masks) * m.latin_fixed_first(3)
            self.assertEqual(m.brute_grid_count(B, C, 2), count)
            self.assertEqual((m.find_matching(masks) is not None), count > 0)

    def test_two_independent_counts_on_all_small_row_types(self):
        # Every possible 2-vector row of length two over GF(2), including
        # zero, repeated elements, a basis and dependent but matchable rows.
        B = m.identity(2)
        vectors = tuple(itertools.product(range(2), repeat=2))
        for C in itertools.product(vectors, repeat=2):
            masks = m.exchange_masks(B, C, 2)
            self.assertEqual(m.support_permanent(masks), m.brute_permanent(masks))
            self.assertEqual(m.brute_grid_count(B, C, 2),
                             m.support_permanent(masks) * m.latin_fixed_first(2))
            result = m.construct(B, C, 2)
            self.assertEqual(result["status"] == "grid",
                             m.support_permanent(masks) > 0)

    def test_corrupt_grid_and_inputs_fail(self):
        _, p, B, C = m.examples()[0]
        valid = m.construct(B, C, p)["rows"]
        bad = json.loads(json.dumps(valid))
        bad[0][0] = bad[0][1]
        with self.assertRaises(ValueError):
            m.verify_grid(B, C, p, bad)
        bad = json.loads(json.dumps(valid))
        bad[-1][0] = [0]*len(B)
        with self.assertRaises(ValueError):
            m.verify_grid(B, C, p, bad)
        with self.assertRaises(ValueError):
            m.construct(B, C, 4)  # GF(4) not represented by modular Z/4
        with self.assertRaises(ValueError):
            m.construct(B[:3] + (B[0],), C, 2)
        with self.assertRaises(ValueError):
            m.construct(B, C[:3], 2)
        with self.assertRaises(ValueError):
            m.construct(B, C[:-1] + ((2, 0, 0, 0),), 2)
        with self.assertRaises(ValueError):
            m.construct(B, C, True)

    def test_generator_rejects_tampered_certificate(self):
        doc = m.certificate()
        changed = json.loads(json.dumps(doc))
        changed["examples"][0]["rows"][0][0] = [0,0,0,0]
        self.assertNotEqual(changed, doc)
        _, p, B, C = m.examples()[0]
        with self.assertRaises(ValueError):
            m.verify_grid(B, C, p, changed["examples"][0]["rows"])


if __name__ == "__main__":
    unittest.main()
