import copy
import gzip
from hashlib import sha256
import json
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import frankl_triple_sat as original
import frankl_triple_capped as target
import verify_frankl_triple_cert as verifier


def direct(members, n=7, cap=18):
    if not 2 <= len(members) <= cap:
        return False
    try:
        original.independent_check(members, n=n)
        return True
    except ValueError:
        return False


class CappedProofTests(unittest.TestCase):
    def test_all_small_families_semantics_exhaustively(self):
        # All 256 possible families over n=3, independent of the SAT solver.
        for cap in range(2, 9):
            cnf = target.build_capped(n=3, cap=cap)
            for system in range(256):
                members = [s for s in range(8) if system & (1 << s)]
                self.assertEqual(cnf.satisfies(cnf.extend(members)),
                                 direct(members, n=3, cap=cap),
                                 (cap, members))

    def test_n4_independent_random_semantics(self):
        rng = random.Random(6111)
        for cap in (5, 8, 12, 16):
            cnf = target.build_capped(n=4, cap=cap)
            for _ in range(200):
                members = rng.sample(range(16), rng.randrange(17))
                self.assertEqual(cnf.satisfies(cnf.extend(members)),
                                 direct(members, n=4, cap=cap),
                                 (cap, members))

    def test_n7_published_nineteen_control(self):
        obj = json.loads(target.FIXTURE.read_text(encoding="utf-8"))
        members = [original.set_mask(s, 7) for s in obj["sets"]]
        cnf18 = target.build_capped(n=7, cap=18)
        cnf19 = target.build_capped(n=7, cap=19)
        self.assertFalse(cnf18.satisfies(cnf18.extend(members)))
        self.assertTrue(cnf19.satisfies(cnf19.extend(members)))
        self.assertEqual(target.verify_positive_control(19)["frequencies"],
                         {0: 9, 1: 9, 2: 9})
        self.assertFalse(target.verify_positive_control(18)["satisfies"])

    def test_exact_size_selector_is_unique(self):
        cnf = target.build_capped(n=4, cap=7)
        self.assertEqual(set(cnf.selectors), set(range(2, 8)))
        for size in range(0, 10):
            values = cnf.extend(range(size))
            self.assertEqual({s for s, var in cnf.selectors.items() if values[var]},
                             ({size} if 2 <= size <= 7 else set()))

    def test_six_redundant_lemma_units_exist(self):
        cnf = target.build_capped(n=7, cap=18)
        self.assertEqual(cnf.base_vars, 128)
        for mask in (1, 2, 3, 4, 5, 6):
            self.assertIn([-(mask + 1)], cnf.clauses)
        self.assertIn([1], cnf.clauses)  # empty member required
        self.assertIn([8], cnf.clauses)  # designated triple

    def test_refuse_bad_parameters(self):
        for n, cap in ((2, 3), (7, 1), (7, 129)):
            with self.assertRaises(ValueError):
                target.build_capped(n=n, cap=cap)
        with self.assertRaises(ValueError):
            target.build_capped(7, 18, triple=(0, 0, 2))

    def test_source_and_certificate_integrity(self):
        m = json.loads(verifier.MANIFEST_PATH.read_text(encoding="utf-8"))
        cnf, drat = verifier.check_manifest(m)
        self.assertEqual(sha256(cnf).hexdigest(), m["cnf"]["sha256"])
        self.assertEqual(sha256(drat).hexdigest(), m["proof"]["raw_sha256"])
        self.assertEqual(len(drat), m["proof"]["raw_bytes"])
        self.assertTrue(drat.rstrip().endswith(b"\n0"))

    def test_claim_promotion_and_tampering_are_rejected(self):
        m = json.loads(verifier.MANIFEST_PATH.read_text(encoding="utf-8"))
        corrupt = copy.deepcopy(m)
        corrupt["status"] = "accepted_new_theorem"
        with self.assertRaisesRegex(ValueError, "promoted"):
            verifier.check_manifest(corrupt)
        corrupt = copy.deepcopy(m)
        corrupt["claim"] += " This solves the general conjecture."
        with self.assertRaisesRegex(ValueError, "Statement scope changed"):
            verifier.check_manifest(corrupt)
        corrupt = copy.deepcopy(m)
        corrupt["cnf"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "CNF hash"):
            verifier.check_manifest(corrupt)
        corrupt = copy.deepcopy(m)
        corrupt["proof"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Compressed proof"):
            verifier.check_manifest(corrupt, compressed=b"bad")

    def test_binary_tamper_rejected_even_with_unmodified_manifest(self):
        m = json.loads(verifier.MANIFEST_PATH.read_text(encoding="utf-8"))
        gz = verifier.local_path(m["proof"]["path"]).read_bytes()
        modified = bytearray(gz)
        modified[17] ^= 1
        with self.assertRaisesRegex(ValueError, "Compressed proof"):
            verifier.check_manifest(m, compressed=bytes(modified))

    def test_path_traversal_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            verifier.local_path("../repo-secret.txt")
        with self.assertRaisesRegex(ValueError, "Missing"):
            verifier.local_path("proofs/certificates/missing.bin")


if __name__ == "__main__":
    unittest.main()
