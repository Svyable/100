#!/usr/bin/env python3
"""Verify pinned M075 capped CNF/proof, then optionally replay external checkers.

Default --check audits bytes, schema and regenerates the CNF; it does NOT check
the DRAT inference trace. For certificate verification pass both *external*
tools compiled from the pinned drat-trim repository:

  python3 scripts/verify_frankl_triple_cert.py --check \
      --drat-trim /tmp/drat-trim/drat-trim --lrat-check /tmp/drat-trim/lrat-check

The separate tools must validate both the unsatisfiable DRAT proof and its
derived LRAT trace. This is a *finite theorem candidate* subject to specialist
mathematical and prior-art review; never set M075 or Solved to resolved.
"""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from frankl_triple_capped import build_capped, verify_positive_control
from frankl_triple_sat import require

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "proofs/certificates/m075_triple7_cap18_manifest.json"
EXPECTED_VERSION = 1
CHECKER_COMMIT = "2e5e29cb0019d5cfd547d4208dca1b3ec290349f"
EXPECTED_CLAIM = (
    "Every union-closed family F of distinct subsets of a seven-element universe "
    "containing empty set and the exact triple {0,1,2}, for which each of 0,1,2 "
    "belongs to STRICTLY fewer than half of F, has at least 19 members."
)
EXPECTED_BOUNDARY = (
    "Fixed seven-element, triple-local strengthening only; NOT Frankl's original "
    "conjecture, NOT general ground-set bound, NOT verified novel or independently "
    "specialist accepted."
)



def digest(data):
    return sha256(data).hexdigest()


def local_path(rel):
    require(isinstance(rel, str) and rel != ""
            and not rel.startswith("/") and "\\" not in rel
            and ".." not in Path(rel).parts, "Unsafe artifact path")
    path = (ROOT / rel).resolve()
    require(path.is_relative_to(ROOT.resolve()) and path.is_file(),
            "Missing certificate source: " + rel)
    return path


def check_manifest(manifest, compressed=None):
    """Offline integrity check. Return raw proof and source for optional replay."""
    require(type(manifest) is dict and manifest.get("version") == EXPECTED_VERSION,
            "Unknown manifest version")
    require(manifest.get("status") ==
            "candidate_exact_finite_bound_computationally_checked_review_pending",
            "Unreviewed result promoted")
    require(manifest.get("problem_id") == "M075"
            and manifest.get("claim") == EXPECTED_CLAIM
            and manifest.get("boundary") == EXPECTED_BOUNDARY,
            "Statement scope changed")
    require(manifest["checker"]["commit"] == CHECKER_COMMIT,
            "Independent tool source pin changed")
    cnf = build_capped(7, 18)
    expected_input = cnf.dimacs().encode("ascii")
    inp = manifest["cnf"]
    require(inp["variables"] == cnf.var_count and inp["clauses"] == len(cnf.clauses),
            "CNF dimensions not reproducible")
    require(local_path(inp["path"]).read_bytes() == expected_input,
            "Stored CNF differs from generated mathematical encoding")
    require(inp["bytes"] == len(expected_input) and inp["sha256"] == digest(expected_input),
            "CNF hash mismatch")

    proof = manifest["proof"]
    gz_bytes = local_path(proof["path"]).read_bytes() if compressed is None else compressed
    require(proof["compression"] == "gzip mtime=0"
            and proof["bytes"] == len(gz_bytes)
            and proof["sha256"] == digest(gz_bytes), "Compressed proof hash mismatch")
    require(0 < len(gz_bytes) <= 30_000_000, "Compressed proof size out of bounds")
    # Cap uncompressed data BEFORE expanding all of it to avoid archive bombs.
    chunks = []
    count = 0
    import io
    with gzip.GzipFile(fileobj=io.BytesIO(gz_bytes)) as stream:
        while True:
            block = stream.read(1 << 20)
            if not block:
                break
            count += len(block)
            require(count <= 100_000_000, "Expanded proof exceeds size guard")
            chunks.append(block)
    raw = b"".join(chunks)
    require(len(raw) == proof["raw_bytes"]
            and digest(raw) == proof["raw_sha256"], "DRAT proof hash mismatch")
    require(raw.rstrip().endswith(b"\n0"), "No terminating empty clause")

    w = manifest["witness"]
    fixture = local_path(w["path"])
    require(digest(fixture.read_bytes()) == w["sha256"] and w["size"] == 19,
            "19-set published fixture changed")
    require(verify_positive_control(19)["satisfies"], "19-set SAT control failed")
    require(not verify_positive_control(18)["satisfies"],
            "The published 19-set witness incorrectly satisfies cap18")
    require(isinstance(proof["lrat_sha256"], str)
            and len(proof["lrat_sha256"]) == 64, "Missing LRAT pin")
    return expected_input, raw


def check_external(manifest, source_bytes, drat_bytes, drat_trim, lrat_check):
    """Invoke pinned independent C checkers, requiring explicit VERIFIED output."""
    for tool in (drat_trim, lrat_check):
        require(Path(tool).is_file(), "Missing independent checker executable: " + tool)
    with TemporaryDirectory(prefix="m075-proof-") as t:
        tmp = Path(t)
        source, drat, lrat = (tmp / "input.cnf", tmp / "proof.drat", tmp / "proof.lrat")
        source.write_bytes(source_bytes)
        drat.write_bytes(drat_bytes)

        first = subprocess.run([drat_trim, str(source), str(drat),
                                "-L", str(lrat)], capture_output=True, text=True,
                               timeout=240)
        require(first.returncode == 0 and "s VERIFIED" in first.stdout + first.stderr,
                "External DRAT-trim REJECTED certificate: " + (first.stdout + first.stderr)[-800:])
        require(lrat.is_file(), "Independent checker omitted LRAT trace")
        require(digest(lrat.read_bytes()) == manifest["proof"]["lrat_sha256"],
                "Reconstructed LRAT does not match pinned source")
        second = subprocess.run([lrat_check, str(source), str(lrat)],
                                capture_output=True, text=True, timeout=120)
        require(second.returncode == 0 and "c VERIFIED" in second.stdout + second.stderr,
                "Independent LRAT checker REJECTED certificate: " +
                (second.stdout + second.stderr)[-800:])

        # Negative control: an invalid refutation of a SAT CNF must be refused.
        sat = tmp / "true.cnf"
        false_proof = tmp / "false.drat"
        sat.write_text("p cnf 1 1\n1 0\n", encoding="ascii")
        false_proof.write_text("0\n", encoding="ascii")
        negative = subprocess.run([drat_trim, str(sat), str(false_proof)],
                                  capture_output=True, text=True, timeout=30)
        require(negative.returncode != 0 and
                "s NOT VERIFIED" in negative.stdout + negative.stderr,
                "DRAT checker failed the satisfiable negative control")
        return {"drat": "externally_verified", "lrat": "externally_verified",
                "negative_control": "rejected", "lrat_sha256": digest(lrat.read_bytes()),
                "specialist_review": "still_required"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    p.add_argument("--drat-trim", type=Path, help="pinned, independently built drat-trim")
    p.add_argument("--lrat-check", type=Path, help="pinned, independently built lrat-check")
    args = p.parse_args()
    require(bool(args.drat_trim) == bool(args.lrat_check),
            "Both external tools required for independent proof replay")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    source, proof = check_manifest(manifest)
    result = {
        "certificate_status": "hash_and_generator_checked",
        "source_sha256": digest(source),
        "proof_sha256": digest(proof),
        "covered_sizes": list(range(2, 19)),
        "scope": "seven-element triple-local only",
        "external_proof_replay": "NOT_RUN",
        "novelty_assessed": False,
        "independent_specialist_accepted": False,
    }
    if args.drat_trim:
        result["external_proof_replay"] = check_external(
            manifest, source, proof, str(args.drat_trim.resolve()),
            str(args.lrat_check.resolve()))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, subprocess.TimeoutExpired) as exc:
        print("M075 certificate verification failed: " + str(exc), file=sys.stderr)
        sys.exit(1)
