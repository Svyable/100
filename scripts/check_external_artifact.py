#!/usr/bin/env python3
"""Check proof-asset bytes against a pinned external claim manifest.

A matching SHA-256 authenticates bytes relative to a manifest, NOT the
mathematical validity of the source proof or independent acceptance.
No downloads, extraction, network access or untrusted commands.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "external_claims.json"
SHA_PATTERN = re.compile(r"^[a-f0-9]{64}$")
COMMIT_PATTERN = re.compile(r"^[a-f0-9]{40}$")


def valid_https(value):
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate_entries(entries):
    if not isinstance(entries, list):
        raise ValueError("External-claim manifest must be a list")
    seen = set()
    for entry in entries:
        for key in ("id", "problem_id", "claim_scope", "claim_state", "source_url",
                    "source_commit", "artifact_filename", "expected_sha256", "note"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                raise ValueError(f"Missing {key}")
        if entry["id"] in seen:
            raise ValueError("Duplicate external artifact ID")
        seen.add(entry["id"])
        if not valid_https(entry["source_url"]):
            raise ValueError("External source must use HTTPS")
        if not COMMIT_PATTERN.fullmatch(entry["source_commit"]):
            raise ValueError("Pinned source commit must be a 40-character hex SHA")
        if type(entry.get("expected_bytes")) is not int or entry["expected_bytes"] < 1:
            raise ValueError("Expected byte count must be positive")
        if not SHA_PATTERN.fullmatch(entry["expected_sha256"]):
            raise ValueError("SHA-256 must be lowercase 64-character hex")
        if entry["claim_state"] != "external_unreviewed":
            raise ValueError("Only externally unreviewed claims are inventoried here")
        if entry.get("integrity_checked_here") is not False or (
            entry.get("mathematical_proof_reviewed_here") is not False
        ):
            raise ValueError("Do not assert a verification that has not been recorded")
        if ("/" in entry["artifact_filename"] or
                "\\" in entry["artifact_filename"] or
                entry["artifact_filename"] in (".", "..")):
            raise ValueError("Artifact name must be basename only")
    return entries


def check_file(path, entry, block_size=1024*1024):
    if block_size < 1:
        raise ValueError("block size must be positive")
    actual_size = 0
    hasher = sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(block_size)
            if not block:
                break
            actual_size += len(block)
            hasher.update(block)
    digest = hasher.hexdigest()
    return {
        "id": entry["id"],
        "actual_bytes": actual_size,
        "actual_sha256": digest,
        "bytes_match": actual_size == entry["expected_bytes"],
        "hash_matches": digest == entry["expected_sha256"],
        "integrity_match": actual_size == entry["expected_bytes"] and
                           digest == entry["expected_sha256"],
        "proof_verified": False
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", help="Pinned external artifact ID")
    parser.add_argument("--file", type=Path, help="Existing, locally obtained proof corpus")
    parser.add_argument("--validate-only", action="store_true",
                        help="Validate manifest schema without claiming any replay")
    args = parser.parse_args()
    try:
        entries = validate_entries(json.loads(MANIFEST.read_text(encoding="utf-8")))
        if args.validate_only:
            print(f"Manifest schema valid: {len(entries)} unreviewed external proof assets")
            return 0
        if not args.id or args.file is None:
            raise ValueError("--id and --file are required unless --validate-only")
        matches = [entry for entry in entries if entry["id"] == args.id]
        if len(matches) != 1:
            raise ValueError("Unknown or ambiguous external artifact ID")
        report = check_file(args.file, matches[0])
        print(json.dumps(report, indent=2, sort_keys=True))
        print("NOTICE: matching bytes do not constitute mathematical proof review")
        return 0 if report["integrity_match"] else 1
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
