#!/usr/bin/env python3
"""Proof-exchange routing: source-bound packets and marginal-reuse scheduling.

This is an *opportunity* graph, not a theorem prover, performance forecast,
or claim that applying an engine to a listed method is already justified.
"""
import argparse
import hashlib
import json
from pathlib import Path

import proof_obligations

ROOT = Path(__file__).resolve().parents[1]


def _read(root, path):
    return json.loads((root / path).read_text(encoding="utf-8"))


def inputs(root=ROOT):
    problems = _read(root, "data/problems.json")
    methods = _read(root, "data/methods.json")["methods"]
    lab = _read(root, "data/lab_results.json")["levels"]["deep"]
    obligations = proof_obligations.load(root / "data/proof_obligations.json", root)
    ids = [p["id"] for p in problems]
    if len(ids) != 100 or len(ids) != len(set(ids)):
        raise ValueError("Active registry must contain 100 distinct targets")
    assigned = [pid for method in methods for pid in method["problems"]]
    if sorted(assigned) != sorted(ids):
        raise ValueError("Every problem must occur in exactly one method shape")
    if len({m["id"] for m in methods}) != len(methods):
        raise ValueError("Duplicate method shape")
    verified = {}
    for probe, item in lab.items():
        if item["problem_id"] not in ids:
            raise ValueError("Unknown problem in lab: " + probe)
        if item["holds"] is True:
            for engine in item["engines"]:
                verified.setdefault(engine, set()).add(item["problem_id"])
    return ids, methods, verified, obligations


def units(methods, verified):
    """Method routing and hypothetical engine transfer, never verified proof reuse."""
    output = []
    for method in methods:
        output.append({
            "id": "shape:" + method["id"], "kind": "shape",
            "targets": sorted(method["problems"]),
            "verified_anchors": [],
            "work": method["lead"],
            "certificate": method["certificate"],
            "falsifier": method["falsifier"],
        })
    names = sorted({e for method in methods for e in method["engines"]})
    for name in names:
        targets = sorted({p for m in methods if name in m["engines"] for p in m["problems"]})
        output.append({
            "id": "engine:" + name, "kind": "engine",
            "targets": targets,
            "verified_anchors": sorted(set(targets) & verified.get(name, set())),
            "work": "Test reusable engine " + name + " on explicitly scoped targets",
            "certificate": "Per-target exact input, independently replayable output, checker and scope audit",
            "falsifier": "An engine application fails its exact checker or the claimed reduction misses a hypothesis",
        })
    return sorted(output, key=lambda u: u["id"])


def greedy(units_list, budget):
    """Deterministic, equal-slot greedy maximum unique *candidate* coverage.

    Coverage is monotone submodular. For this unit-cost objective, choosing
    the highest marginal gain is a (1 - 1/e) approximation to max coverage.
    It is NOT a guarantee about theorem throughput, time or scientific value.
    """
    if not isinstance(budget, int) or budget < 0:
        raise ValueError("Budget must be a nonnegative integer")
    chosen, seen = [], set()
    remaining = list(units_list)
    for _ in range(min(budget, len(remaining))):
        ranked = sorted(
            remaining,
            key=lambda u: (
                -len(set(u["targets"]) - seen),
                -len(set(u["verified_anchors"]) & (set(u["targets"]) - seen)),
                u["id"],
            ),
        )
        best = ranked[0]
        newly = sorted(set(best["targets"]) - seen)
        if not newly:
            break
        chosen.append({**best, "marginal_targets": newly,
                       "marginal_count": len(newly),
                       "cumulative_count": len(seen) + len(newly)})
        seen.update(newly)
        remaining.remove(best)
    return chosen


def frontier(entries):
    """Dispatch only open obligations with discharged prerequisites.

    A 'blocked' node with all dependencies discharged remains externally blocked.
    A structurally well-formed evidence object is not independent proof review.
    """
    by_id = {x["id"]: x for x in entries}
    result = []
    for item in entries:
        if item["status"] == "discharged":
            category = "discharged"
            missing = []
        else:
            missing = sorted(d for d in item["depends_on"] if by_id[d]["status"] != "discharged")
            if missing:
                category = "waiting_on_dependencies"
            elif item["status"] == "blocked":
                category = "externally_blocked"
            else:
                category = "runnable"
        dependent_count = sum(item["id"] in x["depends_on"] for x in entries)
        result.append({
            "id": item["id"], "problem_id": item["problem_id"],
            "kind": item["kind"], "category": category,
            "unmet": missing, "immediate_dependents": dependent_count,
            "statement": item["statement"],
            "prior_art_boundary": item["prior_art_boundary"],
            "falsifier": item["falsifier"],
            "next_action": item["next_action"],
        })
    order = {"runnable": 0, "externally_blocked": 1,
             "waiting_on_dependencies": 2, "discharged": 3}
    return sorted(result, key=lambda x: (order[x["category"]], -x["immediate_dependents"], x["id"]))


def packet_digest(packet):
    scope = {k: packet[k] for k in ("id", "kind", "targets", "work", "certificate", "falsifier")}
    return hashlib.sha256(json.dumps(scope, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def report(root=ROOT, budget=5, unit_type="all"):
    ids, methods, verified, obligations = inputs(root)
    pool = units(methods, verified)
    if unit_type not in ("all", "shape", "engine"):
        raise ValueError("Invalid unit type")
    if unit_type != "all":
        pool = [u for u in pool if u["kind"] == unit_type]
    batch = greedy(pool, budget)
    for packet in batch:
        packet["scope_sha256"] = packet_digest(packet)
        packet["interpretation"] = "Candidate routing reach only; no proof, cost or speedup claim"
    dag = frontier(obligations)
    return {
        "protocol": "svyable.proof-exchange.v1",
        "evidence_boundary": "No engine transfer is proven by method membership; checker and scope audit required for each mathematical claim",
        "problem_count": len(ids), "method_count": len(methods),
        "available_units": len(pool), "budget_equal_slots": budget,
        "candidate_targets_touched": batch[-1]["cumulative_count"] if batch else 0,
        "selected_packets": batch,
        "obligation_frontier": dag,
        "frontier_counts": {name: sum(x["category"] == name for x in dag) for name in (
            "runnable", "externally_blocked", "waiting_on_dependencies", "discharged")},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget", type=int, default=5, help="Number of equal-sized *planning slots*, not a cost estimate")
    parser.add_argument("--unit-type", choices=("all", "shape", "engine"), default="all")
    parser.add_argument("--json", action="store_true", help="Machine-readable dispatch packets")
    parser.add_argument("--check", action="store_true", help="Validate sources and boundaries only")
    args = parser.parse_args()
    result = report(budget=args.budget, unit_type=args.unit_type)
    if args.check:
        print("Validated proof exchange for {} targets and {} obligations".format(
            result["problem_count"], len(result["obligation_frontier"])))
    elif args.json:
        print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))
    else:
        print("Candidate routing: {} / {} targets with {} equal planning slots".format(
            result["candidate_targets_touched"], result["problem_count"],
            len(result["selected_packets"])))
        for x in result["selected_packets"]:
            print("  {}: +{} candidate targets ({} existing verified anchors)".format(
                x["id"], x["marginal_count"], len(x["verified_anchors"])))
        print("Proof DAG: " + ", ".join("{}={}".format(k, v) for k, v in result["frontier_counts"].items()))
        print("These counts measure routing, not new mathematics or accelerated proofs.")


if __name__ == "__main__":
    main()
