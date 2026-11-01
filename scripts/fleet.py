#!/usr/bin/env python3
"""Deterministic, budget-limited planning for up to 10,000 research experiments.

No agents, models, GitHub issues or mathematical verifiers run here. A plan is
not a proof, an outcome, a claim reservation or an observed performance result.

    python3 scripts/fleet.py --count 100 --check
    python3 scripts/fleet.py --count 100 --json > /tmp/fleet-plan.json
    python3 scripts/fleet.py --count 10000
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "data" / "experiments" / "runs.jsonl"
PROTOCOL = "svyable.fleet.v1"
MAX_SLOTS = 10000
DEFAULT_CAPS = {"model_tokens": 45000, "tool_calls": 120, "elapsed_seconds": 3600}
FIELDS = {"protocol", "experiment_id", "work_id", "scope_sha256", "attempt",
          "campaign", "status", "classification", "resources", "resource_caps", "evidence"}
RESOURCE_KEYS = set(DEFAULT_CAPS)
STATUSES = {"completed", "timeout", "error"}
CLASSES = {"none", "known_reproduction", "restricted_unreviewed"}
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
LABEL = re.compile(r"[a-z0-9][a-z0-9-]{0,63}\Z")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def positive_caps(caps):
    if (not isinstance(caps, dict) or set(caps) != RESOURCE_KEYS or
            any(type(value) is not int or value <= 0 for value in caps.values())):
        raise ValueError("Resource caps must have exactly three positive integer fields")
    return dict(caps)


def eligible(items):
    """Honor the existing work queue's dependency and stop-range refusals."""
    result, ids = [], set()
    for item in items:
        if item["status"] != "runnable" or "stop_range" in item["id"]:
            continue
        wid = item["id"]
        if wid in ids:
            raise ValueError("Duplicate runnable work id: " + wid)
        ids.add(wid)
        if not isinstance(item.get("scope_sha256"), str) or not HEX64.fullmatch(item["scope_sha256"]):
            raise ValueError("Work item missing source-bound scope digest: " + wid)
        if not item.get("deliverable") or not item.get("acceptance") or not item.get("boundary"):
            raise ValueError("Incomplete work contract: " + wid)
        result.append(item)
    if not result:
        raise ValueError("No runnable work items")
    return result


def identity(campaign, work_id, scope_sha256, attempt):
    return digest({"protocol": PROTOCOL, "campaign": campaign, "work_id": work_id,
                   "scope_sha256": scope_sha256, "attempt": attempt})


def plan(items, count=100, campaign="dry-run-001", caps=None, total_caps=None):
    """Construct immutable *identities* for experiments, not executions.

    One distinct work packet is scheduled before any second attempt of it.
    Additional attempts share one claim, never create another independent claim.
    """
    if type(count) is not int or not 1 <= count <= MAX_SLOTS:
        raise ValueError("Count must be between 1 and 10000")
    if not isinstance(campaign, str) or not LABEL.fullmatch(campaign):
        raise ValueError("Campaign must be a 1-64 character lowercase slug")
    caps = positive_caps(DEFAULT_CAPS if caps is None else caps)
    if total_caps is not None:
        totals = positive_caps(total_caps)
        if any(count * caps[k] > totals[k] for k in RESOURCE_KEYS):
            raise ValueError("Planned maximum exceeds the aggregate resource budget")
    queue = eligible(items)
    source_sha256 = digest([{"id": w["id"], "scope_sha256": w["scope_sha256"]} for w in queue])
    packets = []
    for index in range(count):
        w = queue[index % len(queue)]
        attempt = index // len(queue)
        eid = identity(campaign, w["id"], w["scope_sha256"], attempt)
        packets.append({
            "experiment_id": eid,
            "work_id": w["id"],
            "scope_sha256": w["scope_sha256"],
            "attempt": attempt,
            "problems": list(w["problems"]),
            "kind": w["kind"],
            "deliverable": w["deliverable"],
            "acceptance": list(w["acceptance"]),
            "boundary": w["boundary"],
            "falsifier": w.get("falsifier", ""),
            "claim_title": w["claim_title"],
            "existing_claims_url": w["existing_claims_url"],
            "resource_caps": caps.copy(),
            "execution": "not_run",
        })
    assert len({p["experiment_id"] for p in packets}) == count
    return {
        "protocol": PROTOCOL,
        "campaign": campaign,
        "mode": "plan_only",
        "source_sha256": source_sha256,
        "slots": count,
        "unique_work_items": len({p["work_id"] for p in packets}),
        "problems_touched": len({x for p in packets for x in p["problems"]}),
        "repeated_attempts": count - len({p["work_id"] for p in packets}),
        "maximum_resources": {k: count * caps[k] for k in RESOURCE_KEYS},
        "packets": packets,
    }


def _safe_file(root, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts:
        raise ValueError("Unsafe evidence path")
    path = root / value
    if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Missing or escaping evidence file: " + value)


def validate_runs(rows, root=ROOT):
    """Validate observed trial data without attributing theorem truth to a schema."""
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != FIELDS or row["protocol"] != PROTOCOL:
            raise ValueError("Unknown fleet run schema or protocol")
        campaign, wid, scope, attempt = (row[k] for k in ("campaign", "work_id", "scope_sha256", "attempt"))
        if (not isinstance(campaign, str) or not LABEL.fullmatch(campaign) or
                not isinstance(wid, str) or not wid or not isinstance(scope, str) or
                not HEX64.fullmatch(scope) or type(attempt) is not int or attempt < 0):
            raise ValueError("Invalid run identity fields")
        eid = identity(campaign, wid, scope, attempt)
        if row["experiment_id"] != eid or eid in seen:
            raise ValueError("Duplicate or modified experiment identity")
        seen.add(eid)
        if row["status"] not in STATUSES or row["classification"] not in CLASSES:
            raise ValueError("Invalid run status or classification")
        caps = positive_caps(row["resource_caps"])
        spent = row["resources"]
        if not isinstance(spent, dict) or set(spent) != RESOURCE_KEYS:
            raise ValueError("Resource accounting must have exactly three fields")
        if any(type(spent[k]) is not int or spent[k] < 0 or spent[k] > caps[k] for k in RESOURCE_KEYS):
            raise ValueError("Negative, invalid or over-budget resource use")
        if row["status"] != "completed" and row["classification"] != "none":
            raise ValueError("Incomplete run cannot classify an artifact")
        evidence = row["evidence"]
        if row["classification"] == "none":
            if evidence is not None:
                raise ValueError("No-result run cannot supply claimed evidence")
        else:
            if not isinstance(evidence, dict) or set(evidence) != {"artifact", "checker_log", "scope_audit"}:
                raise ValueError("Artifact requires exact evidence fields")
            for path in evidence.values():
                _safe_file(root, path)
    return len(seen)


def load_runs(path=RUNS):
    path = Path(path)
    if not path.is_file():
        raise ValueError("Missing experiment ledger")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def source_items():
    """Use the 100-slot proof exchange ordering, then remaining runnable work."""
    import work
    import scale
    items = work.snapshot()["items"]
    wave = scale.report(budget=100, mode="wave")
    rank = {p["id"]: i for i, p in enumerate(wave["selected_packets"])}
    return sorted(items, key=lambda w: rank.get(w["id"], 100000 + items.index(w)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--campaign", default="dry-run-001")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--runs", type=Path, default=RUNS)
    parser.add_argument("--max-model-tokens", type=int, default=DEFAULT_CAPS["model_tokens"])
    parser.add_argument("--max-tool-calls", type=int, default=DEFAULT_CAPS["tool_calls"])
    parser.add_argument("--max-wall-seconds", type=int, default=DEFAULT_CAPS["elapsed_seconds"])
    args = parser.parse_args()
    caps = {"model_tokens": args.max_model_tokens, "tool_calls": args.max_tool_calls,
            "elapsed_seconds": args.max_wall_seconds}
    result = plan(source_items(), count=args.count, campaign=args.campaign, caps=caps)
    recorded = validate_runs(load_runs(args.runs))
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Fleet {}: {} planned, {} distinct work items, {} problems, {} repeated attempts".format(
            result["campaign"], result["slots"], result["unique_work_items"],
            result["problems_touched"], result["repeated_attempts"]))
        print("Plan-only: 0 agents executed; {} observed runs in ledger".format(recorded))
        print("Maximum envelope: {} tokens, {} calls, {} wall seconds (not actual usage)".format(
            *(result["maximum_resources"][k] for k in ("model_tokens", "tool_calls", "elapsed_seconds"))))
    if args.check:
        print("Fleet plan and run-ledger schema valid; no mathematical claims promoted")


if __name__ == "__main__":
    main()
