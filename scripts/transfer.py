#!/usr/bin/env python3
"""Evidence-bound OpenAI/math intake, reusable instruments, and dependency impact.

This is an OFFLINE provenance validator, not a mathematical proof checker or
a live upstream status checker. It never upgrades a conjecture or benchmark run.

    python3 scripts/transfer.py --check
    python3 scripts/transfer.py --json
    python3 scripts/transfer.py --changed proofs/M074_IRREGULAR_24.md
    python3 scripts/transfer.py --upstream-sha <new 40-hex commit>
"""
import argparse
from datetime import date
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TRANSFER_FILE = ROOT / "data/openai_math_transfer.json"
INSTRUMENT_FILE = ROOT / "data/instruments.json"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
RESULT_ID = re.compile(r"[0-9]{3}\Z")
LOCAL_STATES = {"candidate_unreviewed", "known_reproduction"}
TRANSFER_STATES = {"author_claim_unreviewed"}
KINDS = {"lemma", "method", "verifier"}
TRANSFER_KEYS = {"id", "result_id", "title", "problem_ids", "source_url",
                 "claim_review_ids", "related_repo_paths", "status",
                 "scope_boundary", "transfer_hypothesis", "falsifier", "next_action"}
INSTRUMENT_KEYS = {"id", "title", "kind", "origin_problem_id", "claim_state",
                   "depends_on", "proposed_reuse_problem_ids", "sources",
                   "exact_scope", "scope_gap", "falsifier", "next_action"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value, field):
    require(isinstance(value, str) and bool(value.strip()), "Missing " + field)


def unique_strings(values, field, allow_empty=False):
    require(isinstance(values, list) and (allow_empty or bool(values)),
            "Missing list: " + field)
    require(all(isinstance(x, str) and bool(x.strip()) for x in values),
            "Invalid element: " + field)
    require(len(values) == len(set(values)), "Duplicate value: " + field)


def safe_path(root, path):
    nonempty(path, "path")
    pure = PurePosixPath(path)
    require(not pure.is_absolute() and str(pure) == path
            and ".." not in pure.parts and "\\" not in path,
            "Unsafe path: " + path)
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()), "Escaping path: " + path)
    require(resolved.is_file(), "Missing source: " + path)
    return resolved


def validate(transfers, instruments, root=ROOT, check_pins=True):
    require(set(transfers) == {"schema_version", "as_of", "upstream",
                              "interpretation", "transfers"}
            and transfers["schema_version"] == 1, "Invalid transfer schema")
    require(set(instruments) == {"schema_version", "as_of", "interpretation",
                                "instruments"} and instruments["schema_version"] == 1,
            "Invalid instrument schema")
    for obj in (transfers, instruments):
        date.fromisoformat(obj["as_of"])
        nonempty(obj["interpretation"], "interpretation")
    upstream = transfers["upstream"]
    require(set(upstream) == {"repository", "commit", "overview_url"}
            and upstream["repository"] == "openai/math", "Invalid upstream")
    commit = upstream["commit"]
    require(isinstance(commit, str) and HEX40.fullmatch(commit),
            "Unpinned upstream commit")
    prefix = "https://github.com/openai/math/blob/" + commit + "/"
    require(upstream["overview_url"] == prefix + "overview.tex",
            "Upstream overview must use pinned commit")
    problem_ids = {p["id"] for p in read_json(root / "data/problems.json")}
    review_ids = {p["id"] for p in read_json(root / "data/claim_reviews_2026.json")["reviews"]}
    require(isinstance(transfers["transfers"], list) and transfers["transfers"],
            "Empty transfer catalogue")
    require(isinstance(instruments["instruments"], list) and instruments["instruments"],
            "Empty instrument catalogue")

    by_transfer = {}
    result_ids = set()
    for item in transfers["transfers"]:
        require(set(item) == TRANSFER_KEYS, "Invalid transfer fields")
        ident = item["id"]
        nonempty(ident, "transfer ID")
        require(ident.startswith("T-OAI-") and ident not in by_transfer,
                "Duplicate or malformed transfer ID: " + ident)
        by_transfer[ident] = item
        rid = item["result_id"]
        require(isinstance(rid, str) and RESULT_ID.fullmatch(rid)
                and rid not in result_ids, "Duplicate or malformed upstream result ID")
        result_ids.add(rid)
        require(ident == "T-OAI-" + rid, "Transfer/result ID mismatch")
        require(item["status"] in TRANSFER_STATES, "Unreviewed upstream claim upgraded")
        require(isinstance(item["source_url"], str)
                and item["source_url"].startswith(prefix + "preprints/")
                and item["source_url"].endswith(".pdf"), "Unpinned source URL")
        unique_strings(item["problem_ids"], ident + ".problem_ids")
        require(set(item["problem_ids"]) <= problem_ids, "Unknown problem in " + ident)
        unique_strings(item["claim_review_ids"], ident + ".claim_review_ids", True)
        require(set(item["claim_review_ids"]) <= review_ids, "Missing claim review for " + ident)
        require(set(item["claim_review_ids"]) <= set(item["problem_ids"]),
                "Unrelated claim review for " + ident)
        unique_strings(item["related_repo_paths"], ident + ".related_repo_paths")
        for path in item["related_repo_paths"]:
            safe_path(root, path)
        for field in ("title", "scope_boundary", "transfer_hypothesis",
                      "falsifier", "next_action"):
            nonempty(item[field], ident + "." + field)

    by_instrument = {}
    for item in instruments["instruments"]:
        require(set(item) == INSTRUMENT_KEYS, "Invalid instrument fields")
        ident = item["id"]
        nonempty(ident, "instrument ID")
        require(ident.startswith("I-M") and ident not in by_instrument,
                "Duplicate or malformed instrument ID")
        by_instrument[ident] = item
        require(item["kind"] in KINDS and item["claim_state"] in LOCAL_STATES,
                "Unknown kind or unsafe instrument claim state")
        require(item["origin_problem_id"] in problem_ids, "Unknown origin problem")
        unique_strings(item["proposed_reuse_problem_ids"], ident + ".reuse")
        require(set(item["proposed_reuse_problem_ids"]) <= problem_ids,
                "Unknown proposed reuse target")
        unique_strings(item["depends_on"], ident + ".depends_on", True)
        require(isinstance(item["sources"], list) and item["sources"],
                "Instrument missing source path")
        paths = []
        for source in item["sources"]:
            require(set(source) == {"path", "sha256"}, "Malformed pinned source")
            path = safe_path(root, source["path"])
            paths.append(source["path"])
            digest = source["sha256"]
            require(isinstance(digest, str) and HEX64.fullmatch(digest),
                    "Missing source SHA256 for " + source["path"])
            if check_pins:
                require(sha256(path.read_bytes()).hexdigest() == digest,
                        "Source changed; review and repin: " + source["path"])
        require(len(paths) == len(set(paths)), "Duplicate source paths in " + ident)
        for field in ("title", "exact_scope", "scope_gap", "falsifier", "next_action"):
            nonempty(item[field], ident + "." + field)

    # DFS refuses missing dependencies, self-edges and indirect cycles.
    visited = set()
    visiting = set()

    def visit(ident):
        require(ident in by_instrument, "Unknown instrument dependency: " + ident)
        require(ident not in visiting, "Cycle in instrument dependencies: " + ident)
        if ident in visited:
            return
        visiting.add(ident)
        for dep in by_instrument[ident]["depends_on"]:
            visit(dep)
        visiting.remove(ident)
        visited.add(ident)

    for ident in by_instrument:
        visit(ident)
    return by_transfer, by_instrument


def impact(transfers, instruments, root=ROOT, changed=(), upstream_sha=None):
    by_transfer, by_instrument = validate(transfers, instruments, root, check_pins=False)
    given = set(changed)
    # A changed source digest is actionable even without an explicit --changed flag.
    drift = {s["path"] for item in by_instrument.values() for s in item["sources"]
             if sha256(safe_path(root, s["path"]).read_bytes()).hexdigest() != s["sha256"]}
    changed_paths = given | drift
    for path in given:
        safe_path(root, path)
    upstream_changed = (upstream_sha is not None
                        and upstream_sha != transfers["upstream"]["commit"])
    if upstream_sha is not None:
        require(isinstance(upstream_sha, str) and HEX40.fullmatch(upstream_sha),
                "Invalid supplied upstream SHA")
    full_transfer = "data/openai_math_transfer.json" in changed_paths
    full_instrument = "data/instruments.json" in changed_paths
    transfer_ids = sorted(ident for ident, item in by_transfer.items()
                          if upstream_changed or full_transfer or
                          bool(set(item["related_repo_paths"]) & changed_paths))
    impacted_ids = {ident for ident, item in by_instrument.items()
                    if full_instrument or
                    bool({s["path"] for s in item["sources"]} & changed_paths)}
    changed_ = True
    while changed_:
        before = len(impacted_ids)
        impacted_ids |= {ident for ident, item in by_instrument.items()
                         if set(item["depends_on"]) & impacted_ids}
        changed_ = len(impacted_ids) != before
    return {"changed_paths": sorted(changed_paths),
            "digest_drift": sorted(drift),
            "upstream_commit_changed": upstream_changed,
            "transfers_requiring_review": transfer_ids,
            "instruments_requiring_review": sorted(impacted_ids),
            "note": "Impact only queues review; no theorem, evidence state or Solved record is changed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="strict offline schema and pinned-source check")
    parser.add_argument("--json", action="store_true", help="JSON validation summary")
    parser.add_argument("--changed", action="append", default=[], metavar="PATH",
                        help="local changed path; repeat for additional paths")
    parser.add_argument("--upstream-sha", help="externally observed upstream commit SHA")
    args = parser.parse_args()
    transfers, instruments = read_json(TRANSFER_FILE), read_json(INSTRUMENT_FILE)
    if args.changed or args.upstream_sha:
        print(json.dumps(impact(transfers, instruments, changed=args.changed,
                                upstream_sha=args.upstream_sha), indent=2))
    else:
        ts, ins = validate(transfers, instruments)
        result = {"transfers": len(ts), "instruments": len(ins), "pinned_upstream": transfers["upstream"]["commit"],
                  "validated": True, "math_reviewed_by_validator": False}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("Transfer registry valid: {transfers} scoped intakes, {instruments} pinned instruments "
                  "(no theorem acceptance)".format(**result))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError, TypeError) as exc:
        print("Transfer validation failed: " + str(exc), file=sys.stderr)
        sys.exit(1)
