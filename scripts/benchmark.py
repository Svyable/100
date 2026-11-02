#!/usr/bin/env python3
"""Preregistered, evidence-gated evaluation of proof-exchange research runs.

No model calls are made here. An empty ledger means no experiment was run.
Passing structural validation NEVER authenticates reviews or proves a theorem.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "benchmark_prereg.json"
RUNS = ROOT / "data" / "benchmark_runs.jsonl"
ARMS = ("sequential", "independent", "conversation", "proof_exchange")
RESULTS = ("none", "known_reproduction", "restricted_unreviewed",
           "externally_reviewed_restricted")
STATUSES = ("completed", "timeout", "error")
RUN_FIELDS = {"manifest_sha256", "task_id", "arm", "seed", "status",
              "classification", "resources", "evidence"}
EVIDENCE_FIELDS = {"artifact", "checker_log", "scope_audit",
                   "independent_review_urls"}
RESOURCES = ("model_tokens", "tool_calls", "elapsed_seconds")
# The finite CH (24,8) irregular case acquired author-derived full-case
# proofs in public repo PRs #60 and #70 *after* this pilot was frozen.
# Do not turn exposure to those proofs into a claimed new result.
NOVELTY_CONTAMINATED = {
    "CH24-IRREGULAR": "Public finite-case proofs in PRs #60/#70 postdate the frozen protocol",
}


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def _safe_path(root, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError("Evidence path must be relative and nonempty")
    path = Path(value)
    if ".." in path.parts or not (root / path).is_file():
        raise ValueError("Evidence path missing or unsafe: " + value)
    if not (root / path).resolve().is_relative_to(root.resolve()):
        raise ValueError("Evidence path escapes root: " + value)


def load_manifest(path=MANIFEST):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if set(doc) != {"version", "preregistered_at", "source_commit", "arms",
                    "seeds", "resource_caps", "tasks", "interpretation"} or doc["version"] != 1:
        raise ValueError("Unsupported benchmark manifest")
    if len(doc["source_commit"]) != 40 or any(c not in "0123456789abcdef" for c in doc["source_commit"]):
        raise ValueError("Source commit must be full SHA-1")
    if doc["arms"] != list(ARMS) or doc["seeds"] != [11, 23, 37]:
        raise ValueError("Benchmark arms and seeds must be fixed before trials")
    limits = doc["resource_caps"]
    if set(limits) != set(RESOURCES) or any(type(v) is not int or v <= 0 for v in limits.values()):
        raise ValueError("All matched resource caps must be positive integers")
    tasks = doc["tasks"]
    if not isinstance(tasks, list) or len(tasks) != 3 or len({t["id"] for t in tasks}) != 3:
        raise ValueError("Expected three structurally distinct tasks")
    expected_fields = {"id", "problem_id", "class", "scope", "prior_art",
                       "acceptance", "source_paths", "eligible_for_novelty"}
    for t in tasks:
        if not isinstance(t, dict) or set(t) != expected_fields:
            raise ValueError("Invalid task contract")
        if t["class"] not in ("replay", "structural", "dependency"):
            raise ValueError("Unknown task class")
        if not all(isinstance(t[f], str) and t[f].strip()
                   for f in ("id", "problem_id", "scope", "prior_art", "acceptance")):
            raise ValueError("Empty task contract")
        if not isinstance(t["source_paths"], list) or not t["source_paths"]:
            raise ValueError("Task must list pinned repository paths")
        if any(not isinstance(x, str) or x.startswith("/") or ".." in Path(x).parts
               for x in t["source_paths"]):
            raise ValueError("Unsafe source path")
        if type(t["eligible_for_novelty"]) is not bool:
            raise ValueError("Invalid novelty eligibility flag")
    if {t["class"] for t in tasks} != {"replay", "structural", "dependency"}:
        raise ValueError("Missing task class")
    if any(t["eligible_for_novelty"] for t in tasks if t["class"] == "replay"):
        raise ValueError("Known replays cannot be counted as novel discoveries")
    return doc


def load_runs(path=RUNS):
    path = Path(path)
    if not path.exists():
        raise ValueError("Missing runs ledger; initialize as an empty JSONL file")
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def validate_runs(doc, runs, root=ROOT):
    expected = {(t["id"], arm, seed) for t in doc["tasks"]
                for arm in doc["arms"] for seed in doc["seeds"]}
    seen = set()
    for r in runs:
        if not isinstance(r, dict) or set(r) != RUN_FIELDS:
            raise ValueError("Run must have exact schema fields")
        key = (r["task_id"], r["arm"], r["seed"])
        if key not in expected or key in seen:
            raise ValueError("Unknown or duplicated trial " + str(key))
        seen.add(key)
        if r["manifest_sha256"] != digest(doc):
            raise ValueError("Trial used a different preregistered protocol")
        if r["status"] not in STATUSES or r["classification"] not in RESULTS:
            raise ValueError("Invalid run state or result class")
        usage = r["resources"]
        if not isinstance(usage, dict) or set(usage) != set(RESOURCES):
            raise ValueError("Resource use must have exact cost fields")
        for field, amount in usage.items():
            if type(amount) is not int or amount < 0 or amount > doc["resource_caps"][field]:
                raise ValueError("Invalid or over-budget resource: " + field)
        if r["status"] != "completed" and r["classification"] != "none":
            raise ValueError("Incomplete trials cannot claim a result")
        if r["classification"] == "none":
            if r["evidence"] is not None:
                raise ValueError("No-result trial cannot claim evidence")
            continue
        task = next(t for t in doc["tasks"] if t["id"] == r["task_id"])
        if task["class"] == "replay" and r["classification"] != "known_reproduction":
            raise ValueError("A known replay cannot be promoted to a novel result")
        ev = r["evidence"]
        if not isinstance(ev, dict) or set(ev) != EVIDENCE_FIELDS:
            raise ValueError("Every claimed artifact needs complete evidence fields")
        for field in ("artifact", "checker_log", "scope_audit"):
            _safe_path(root, ev[field])
        reviews = ev["independent_review_urls"]
        if not isinstance(reviews, list):
            raise ValueError("Review URLs must be a list")
        if r["classification"] == "externally_reviewed_restricted":
            if r["task_id"] in NOVELTY_CONTAMINATED:
                raise ValueError("Novelty task contaminated by post-freeze public results")
            if not task["eligible_for_novelty"] or len(reviews) < 2:
                raise ValueError("Novelty promotion requires eligible scope and two reviews")
        hosts = []
        for link in reviews:
            if not isinstance(link, str):
                raise ValueError("Invalid review URL")
            parsed = urlparse(link)
            if parsed.scheme != "https" or not parsed.hostname:
                raise ValueError("Review URL must use HTTPS")
            hosts.append(parsed.hostname.casefold())
        if r["classification"] == "externally_reviewed_restricted" and len(set(hosts)) < 2:
            raise ValueError("Reviews must be on distinct hosts")
    return expected - seen


def summarize(doc, runs):
    missing = validate_runs(doc, runs)
    contaminated = {k: reason for k, reason in NOVELTY_CONTAMINATED.items()
                    if k in {t["id"] for t in doc["tasks"]}}
    by_arm = {}
    for arm in doc["arms"]:
        subset = [r for r in runs if r["arm"] == arm]
        by_arm[arm] = {
            "recorded": len(subset),
            "completed": sum(r["status"] == "completed" for r in subset),
            "timeouts": sum(r["status"] == "timeout" for r in subset),
            "errors": sum(r["status"] == "error" for r in subset),
            "known_reproductions": sum(r["classification"] == "known_reproduction" for r in subset),
            "unreviewed_restricted": sum(r["classification"] == "restricted_unreviewed" for r in subset),
            "reviewed_restricted": sum(r["classification"] == "externally_reviewed_restricted" for r in subset),
            "total_model_tokens": sum(r["resources"]["model_tokens"] for r in subset),
            "total_tool_calls": sum(r["resources"]["tool_calls"] for r in subset),
            "total_elapsed_seconds": sum(r["resources"]["elapsed_seconds"] for r in subset),
        }
    return {
        "manifest_sha256": digest(doc),
        "expected_trials": len(doc["tasks"]) * len(doc["arms"]) * len(doc["seeds"]),
        "recorded_trials": len(runs),
        "missing_trials": len(missing),
        "completed_trials": sum(r["status"] == "completed" for r in runs),
        "timeout_trials": sum(r["status"] == "timeout" for r in runs),
        "error_trials": sum(r["status"] == "error" for r in runs),
        "all_cells_recorded": not missing,
        "matched_trials_completed": not missing and len(runs) > 0
                                    and all(r["status"] == "completed" for r in runs),
        "comparable": not missing and len(runs) > 0
                      and all(r["status"] == "completed" for r in runs) and not contaminated,
        "novelty_contaminated_tasks": contaminated,
        "by_arm": by_arm,
        "warning": ("No experimental speedup can be claimed until all matched trials "
                    "are completed and independent mathematical review is authenticated. "
                    "These validators check evidence *shape*, not mathematical truth."),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--runs", type=Path, default=RUNS)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    doc = load_manifest(args.manifest)
    runs = load_runs(args.runs)
    summary = summarize(doc, runs)
    if args.check:
        print("Benchmark protocol valid: {} recorded / {} planned trials; {} missing".format(
            summary["recorded_trials"], summary["expected_trials"], summary["missing_trials"]))
    elif args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("Proof-exchange benchmark: {} / {} matched trials recorded ({} completed, {} timeout, {} error)".format(
            summary["recorded_trials"], summary["expected_trials"],
            summary["completed_trials"], summary["timeout_trials"], summary["error_trials"]))
        print("All matched trials completed: " + ("yes" if summary["matched_trials_completed"] else "no"))
        print("Comparable completed experimental evidence: " + ("yes" if summary["comparable"] else "no"))
        for arm, row in summary["by_arm"].items():
            print("{}: {} completed, {} reviewed restricted, {} known reproductions".format(
                arm, row["completed"], row["reviewed_restricted"], row["known_reproductions"]))
        print(summary["warning"])


if __name__ == "__main__":
    main()
