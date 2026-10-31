import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_external_artifact


class ExternalArtifactTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(check_external_artifact.MANIFEST.read_text())

    def test_manifest_schema_and_no_claimed_success(self):
        self.assertEqual(len(check_external_artifact.validate_entries(self.manifest)),1)
        self.assertFalse(self.manifest[0]["integrity_checked_here"])
        self.assertFalse(self.manifest[0]["mathematical_proof_reviewed_here"])

    def test_hash_good_and_bad_with_synthetic_local_bytes(self):
        payload = b"synthetic proof corpus data - not actual proof"
        record = dict(self.manifest[0],
                      expected_bytes=len(payload),
                      expected_sha256=hashlib.sha256(payload).hexdigest())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / record["artifact_filename"]
            path.write_bytes(payload)
            good = check_external_artifact.check_file(path, record, block_size=3)
            self.assertTrue(good["integrity_match"])
            self.assertFalse(good["proof_verified"])
            path.write_bytes(payload + b"x")
            bad = check_external_artifact.check_file(path, record, block_size=5)
            self.assertFalse(bad["integrity_match"])
            self.assertFalse(bad["proof_verified"])

    def test_manifest_rejects_invalid_or_self_attested_reviews(self):
        entry = self.manifest[0]
        for altered in [
            dict(entry, source_url="http://insecure.example"),
            dict(entry, expected_sha256="deadbeef"),
            dict(entry, expected_bytes=True),
            dict(entry, source_commit="not-a-commit"),
            dict(entry, mathematical_proof_reviewed_here=True),
            dict(entry, integrity_checked_here=True),
            dict(entry, artifact_filename="../escape.tar.zst"),
        ]:
            with self.subTest(altered=altered):
                with self.assertRaises(ValueError):
                    check_external_artifact.validate_entries([altered])
        with self.assertRaises(ValueError):
            check_external_artifact.validate_entries([entry, entry])


if __name__ == "__main__":
    unittest.main()
