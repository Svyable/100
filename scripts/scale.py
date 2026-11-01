#!/usr/bin/env python3
"""Proof-exchange waves: evidence-bound parallel slots across the portfolio.

This is an *opportunity* and *coordination* layer, not a theorem prover,
performance forecast, or claim that N agents produce N theorems.

    python3 scripts/scale.py                     # short wave summary (budget 100)
    python3 scripts/scale.py --budget 5          # small coverage ablation
    python3 scripts/scale.py --budget 100 --json # machine-readable fleet packets
    python3 scripts/scale.py --write             # regenerate SCALE.md
    python3 scripts/scale.py --check             # validate sources + SCALE.md drift

`--unit-type shape|engine` keeps the original equal-slot coverage ablations.
Default mode schedules up to ``budget`` distinct claimable work items from the
derived work queue, refusing dominated range extensions and dependency-blocked
nodes, and attaches a recommended scout/adversary/checker role split.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import approach
import proof_obligations

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "SCALE.md"
PACKETS = ROOT / "docs" / "api" / "packets.json"
ROLES = ("scout", "adversary", "checker")
FAMILY_BASE = {
    "obligation": 1000,
    "lean": 800,
    "job": 600,
    "roadmap": 400,
    "comparator": 120,
    "status_audit": 80,
}
PROTOCOL = "svyable.proof-exchange.v2"


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
    scope = {k: packet[k] for k in (
        "id", "kind", "targets", "work", "certificate", "falsifier",
    ) if k in packet}
    if "deliverable" in packet:
        scope = {k: packet[k] for k in (
            "id", "kind", "problems", "deliverable", "acceptance", "boundary", "roles",
        )}
    return hashlib.sha256(json.dumps(scope, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _job_index(root=ROOT):
    from research import load
    items, program, _ = load()
    return {f"J-{j['method_id']}-{j['action']}": j for j in approach.snapshot(items, program)["jobs"]}


def leverage(item, dispatch_bonus, jobs):
    """Scheduling weight for wave fill. Not a probability or novelty score."""
    base = FAMILY_BASE[item["kind"]]
    bonus = 0
    job = jobs.get(item["id"])
    if job:
        bonus = dispatch_bonus.get(job["action"], 0)
    cohort = 10 * max(0, len(item["problems"]) - 1)
    rank_term = max(0, 200 - item["priority_rank"])
    return base + bonus + cohort + rank_term


def role_plan(item, jobs):
    """Recommended independent roles under one claim. Not three truth votes."""
    roles = {
        "scout": "Produce the exact artifact or restricted statement named in the deliverable.",
        "adversary": "Search for scope mismatches, missing hypotheses, counterexamples and contamination from known results.",
        "checker": "Replay on an independent path or proof kernel; report exactly what remains unproved.",
    }
    job = jobs.get(item["id"])
    action = job["action"] if job else None
    if item["kind"] == "status_audit":
        return {
            "scout": roles["scout"],
            "adversary": "Challenge each dated source against the registered quantifiers.",
        }
    if item["kind"] == "comparator":
        return {
            "scout": roles["scout"],
            "adversary": "Find a hand-checked instance where the encoding disagrees with the registry.",
            "checker": "Kernel-check the fidelity examples; confirm no escape hatches.",
        }
    if action == "stop_range":
        return {"scout": "Do not extend the refused range; record the replacement step that starts with 'Do not'."}
    if item["status"] != "runnable":
        return {"scout": "Unblock dependencies or external gates before constructive work."}
    return roles


def eligible_wave_items(work_items, jobs):
    kept, refused = [], []
    for item in work_items:
        job = jobs.get(item["id"])
        action = job["action"] if job else None
        if action == "stop_range":
            refused.append({
                "id": item["id"],
                "reason": "stop_range: campaign blocker places the range in known mathematics",
            })
            continue
        if item["status"] != "runnable":
            reason = (("waiting_on_dependencies: " + ",".join(item["depends_on"]))
                      if item["status"] == "waiting_on_dependencies"
                      else "externally_blocked: the obligation is not executable")
            refused.append({"id": item["id"], "reason": reason})
            continue
        kept.append(item)
    return kept, refused


def wave(budget=100, root=ROOT):
    """Fill up to ``budget`` distinct claimable slots from the derived work queue."""
    if not isinstance(budget, int) or budget < 0:
        raise ValueError("Budget must be a nonnegative integer")
    import work  # local import: work imports scale at module level

    doc = work.snapshot()
    jobs = _job_index(root)
    methods_doc = _read(root, "data/methods.json")
    dispatch_bonus = {name: spec["bonus"] for name, spec in methods_doc["actions"].items()}
    kept, refused = eligible_wave_items(doc["items"], jobs)
    ranked = sorted(
        kept,
        key=lambda w: (-leverage(w, dispatch_bonus, jobs), w["priority_rank"], w["id"]),
    )
    selected = ranked[:budget]
    packets = []
    problems = set()
    method_ids = set()
    for item in selected:
        problems.update(item["problems"])
        job = jobs.get(item["id"])
        if job:
            method_ids.add(job["method_id"])
        packet = {
            "id": item["id"],
            "kind": item["kind"],
            "status": item["status"],
            "problems": list(item["problems"]),
            "title": item["title"],
            "deliverable": item["deliverable"],
            "acceptance": list(item["acceptance"]),
            "boundary": item["boundary"],
            "falsifier": item.get("falsifier") or "",
            "depends_on": list(item.get("depends_on") or []),
            "priority_rank": item["priority_rank"],
            "leverage": leverage(item, dispatch_bonus, jobs),
            "roles": role_plan(item, jobs),
            "claim_title": item["claim_title"],
            "open_claim_url": item["open_claim_url"],
            "existing_claims_url": item["existing_claims_url"],
            "interpretation": "One claimable slot. Roles are a recommended split under that claim, not three independent truth votes.",
        }
        packet["scope_sha256"] = packet_digest(packet)
        packets.append(packet)
    by_kind = {k: sum(p["kind"] == k for p in packets) for k in FAMILY_BASE}
    return {
        "protocol": PROTOCOL,
        "evidence_boundary": (
            "A filled slot is a claimable work packet with a scope digest. "
            "It is not a solved theorem, a readiness change, or a measured speedup."
        ),
        "budget_slots": budget,
        "slots_filled": len(packets),
        "problems_touched": len(problems),
        "problem_ids": sorted(problems),
        "cohort_shapes_touched": len(method_ids),
        "refused_count": len(refused),
        "refused": refused,
        "by_kind": by_kind,
        "naive_one_agent_per_problem": 100,
        "shape_count": len(_read(root, "data/methods.json")["methods"]),
        "work_queue_size": doc["count"],
        "runnable_in_queue": doc["by_status"]["runnable"],
        "selected_packets": packets,
        "ambition_note": (
            "100 parallel evidence-bound slots is an operating capacity target. "
            "It is not a claim that the portfolio yields 100 new theorems."
        ),
    }


def coverage_report(root=ROOT, budget=5, unit_type="all"):
    """Original equal-slot coverage ablation over shapes/engines."""
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


def report(root=ROOT, budget=100, unit_type="all", mode="wave"):
    if mode == "coverage":
        return coverage_report(root=root, budget=budget, unit_type=unit_type)
    result = wave(budget=budget, root=root)
    # Always attach obligation frontier counts for the dashboard line.
    _, _, _, obligations = inputs(root)
    dag = frontier(obligations)
    result["obligation_frontier"] = dag
    result["frontier_counts"] = {name: sum(x["category"] == name for x in dag) for name in (
        "runnable", "externally_blocked", "waiting_on_dependencies", "discharged")}
    return result


def render(doc=None):
    doc = doc or report(budget=100, mode="wave")
    lines = [
        "# Scale — proof-exchange wave",
        "",
        f"Generated by `python3 scripts/scale.py --write` ({doc['protocol']}); do not edit by hand.",
        "",
        doc["ambition_note"],
        "",
        doc["evidence_boundary"],
        "",
        "## Operating readout",
        "",
        f"| Observable | Value | Boundary |",
        f"|---|---:|---|",
        f"| Claimable slots filled / budget | **{doc['slots_filled']}** / {doc['budget_slots']} | One agent claim per slot; not theorems |",
        f"| Active problems touched | **{doc['problems_touched']}** / 100 | Coverage of the registry, not resolutions |",
        f"| Cohort shapes touched (via jobs) | {doc['cohort_shapes_touched']} / {doc['shape_count']} | Shared attack templates |",
        f"| Derived work-queue size | {doc['work_queue_size']} ({doc['runnable_in_queue']} runnable) | Source: `scripts/work.py` |",
        f"| Refused this wave | {doc['refused_count']} | stop_range, externally blocked or dependency-blocked |",
        f"| Proof-obligation frontier | runnable={doc['frontier_counts']['runnable']}, "
        f"blocked={doc['frontier_counts']['externally_blocked']}, "
        f"waiting={doc['frontier_counts']['waiting_on_dependencies']}, "
        f"discharged={doc['frontier_counts']['discharged']} | Acceptance DAG only |",
        "",
        "Slot mix: " + ", ".join(f"{k}={v}" for k, v in doc["by_kind"].items() if v),
        "",
        "## How to take a slot",
        "",
        "1. Search open issues for the packet's claim title.",
        "2. If none is open, open `.github/ISSUE_TEMPLATE/claim.yml` with the scope digest.",
        "3. Do only the deliverable; keep the boundary.",
        "4. Prefer the scout / adversary / checker split inside the claim rather than three duplicate attempts.",
        "5. Regenerate with `python3 scripts/regen.py` before shipping.",
        "",
        "Full agent protocol: [AGENTS.md](AGENTS.md). Work queue: "
        "`python3 scripts/work.py --next 5`. Coverage ablation: "
        "`python3 scripts/scale.py --mode coverage --budget 5`.",
        "",
        "## Wave packets (dispatch order by leverage)",
        "",
    ]
    for index, packet in enumerate(doc["selected_packets"], 1):
        problems = ", ".join(packet["problems"]) or "—"
        lines.append(
            f"### {index}. `{packet['id']}` · {packet['kind']} · {packet['status']} · "
            f"leverage {packet['leverage']}"
        )
        lines.append("")
        lines.append(f"**{packet['title']}**")
        lines.append("")
        lines.append(f"- Problems: {problems}")
        lines.append(f"- Deliverable: {packet['deliverable']}")
        lines.append(f"- Boundary: {packet['boundary']}")
        if packet["falsifier"]:
            lines.append(f"- Falsifier: {packet['falsifier']}")
        lines.append(f"- Claim: `{packet['claim_title']}`")
        lines.append(f"- Digest: `{packet['scope_sha256'][:16]}…`")
        lines.append("- Roles:")
        for role, text in packet["roles"].items():
            lines.append(f"  - `{role}`: {text}")
        lines.append("")
    if doc["refused"]:
        lines += ["## Refused this wave", ""]
        for item in doc["refused"]:
            lines.append(f"- `{item['id']}` — {item['reason']}")
        lines.append("")
    lines += [
        "## Relationship to the rest of the stack",
        "",
        "This wave does not replace [APPROACH.md](APPROACH.md), the lab, the Lean gate, "
        "the proof-obligation DAG or the Solved archive. It schedules *claimable* work "
        "with source-bound digests so many agents can move at once without duplicating "
        "effort or inventing theorems.",
        "",
    ]
    return "\n".join(lines)


def packets_blob(wave_doc):
    """Stable JSON for docs/api/packets.json (fleet ingress)."""
    return json.dumps(wave_doc, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def write_outputs(wave_doc=None):
    wave_doc = wave_doc or report(budget=100, mode="wave")
    OUTPUT.write_text(render(wave_doc), encoding="utf-8")
    PACKETS.parent.mkdir(parents=True, exist_ok=True)
    PACKETS.write_text(packets_blob(wave_doc), encoding="utf-8")
    return wave_doc


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--budget", type=int, default=100,
                        help="Wave: claimable slots. Coverage mode: equal planning slots.")
    parser.add_argument("--unit-type", choices=("all", "shape", "engine"), default="all")
    parser.add_argument("--mode", choices=("wave", "coverage"), default="wave")
    parser.add_argument("--json", action="store_true", help="Machine-readable packets")
    parser.add_argument("--write", action="store_true", help="Regenerate SCALE.md and docs/api/packets.json")
    parser.add_argument("--check", action="store_true", help="Validate sources and SCALE.md / packets drift")
    args = parser.parse_args()
    if args.mode == "coverage":
        result = report(budget=args.budget, unit_type=args.unit_type, mode="coverage")
    else:
        result = report(budget=args.budget, mode="wave")
    if args.check:
        if args.mode != "wave" or args.budget != 100:
            # Still validate that wave sources parse.
            wave_doc = report(budget=100, mode="wave")
        else:
            wave_doc = result
        content = render(wave_doc)
        blob = packets_blob(wave_doc)
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit("Stale SCALE.md: run python3 scripts/scale.py --write")
        if not PACKETS.exists() or PACKETS.read_text(encoding="utf-8") != blob:
            raise SystemExit("Stale docs/api/packets.json: run python3 scripts/scale.py --write")
        print(
            "OK: scale wave fills {} / {} slots ({} problems, {} refused); "
            "obligation frontier runnable={}; packets={}".format(
                wave_doc["slots_filled"], wave_doc["budget_slots"],
                wave_doc["problems_touched"], wave_doc["refused_count"],
                wave_doc["frontier_counts"]["runnable"],
                PACKETS.relative_to(ROOT),
            )
        )
    elif args.write:
        wave_doc = write_outputs()
        print(f"Updated SCALE.md and {PACKETS.relative_to(ROOT)} ({wave_doc['slots_filled']} packets)")
    elif args.json:
        print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))
    elif args.mode == "coverage":
        print("Candidate routing: {} / {} targets with {} equal planning slots".format(
            result["candidate_targets_touched"], result["problem_count"],
            len(result["selected_packets"])))
        for x in result["selected_packets"]:
            print("  {}: +{} candidate targets ({} existing verified anchors)".format(
                x["id"], x["marginal_count"], len(x["verified_anchors"])))
        print("Proof DAG: " + ", ".join("{}={}".format(k, v) for k, v in result["frontier_counts"].items()))
        print("These counts measure routing, not new mathematics or accelerated proofs.")
    else:
        print("Wave: {} / {} claimable slots touching {} / 100 problems ({} refused)".format(
            result["slots_filled"], result["budget_slots"],
            result["problems_touched"], result["refused_count"]))
        print("Mix: " + ", ".join(f"{k}={v}" for k, v in result["by_kind"].items() if v))
        print("Proof DAG: " + ", ".join("{}={}".format(k, v) for k, v in result["frontier_counts"].items()))
        print(result["ambition_note"])


if __name__ == "__main__":
    main()
