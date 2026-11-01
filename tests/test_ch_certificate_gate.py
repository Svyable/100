"""Fail-closed controls: no missing proof or checker can certify a theorem."""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ch_certificate_gate import check

class CertificateGateTests(unittest.TestCase):
    def test_missing_artifacts_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            with self.assertRaises(ValueError):
                check("pivot", p / "missing.proof", p / "missing-checker")

    def test_false_checker_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            proof = p / "fake.proof"
            proof.write_text("UNSAT is not a certificate")
            checker = p / "reject"
            checker.write_text("#!/bin/sh\nexit 1\n")
            checker.chmod(0o755)
            with self.assertRaisesRegex(ValueError, "rejected"):
                check("pivot", proof, checker)

if __name__ == "__main__":
    unittest.main()
