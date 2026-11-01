#!/usr/bin/env python3
"""Evidence-separated, breadth-first scheduling across the active 100.

    python3 scripts/coverage.py                  # headline; 200 claimable slots
    python3 scripts/coverage.py --json           # exact packet assignments + matrix
    python3 scripts/coverage.py --write          # generate COVERAGE.md
    python3 scripts/coverage.py --check          # check ledger invariants / drift

This allocates existing eligible work, not compute workers or real reviews.
Two distinct *work kinds* are two routes to investigate, not independent proof.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import scale

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "COVERAGE.md"
DEFAULT_BUDGET = 200


def choose_breadth_first(packets, budget):
    """Maximize new problem coverage, then a second distinct work kind.

    Both stages are deterministic equal-*slot* greedy heuristics, not optimal
    schedules under heterogeneous time costs. High existing leverage breaks
    equal marginal-coverage ties; it never overrides a new target or kind.
    """
    if type(budget) is not int or budget < 0:
        raise ValueError("budget must be a nonnegative integer")
    ids = [p["id"] for p in packets]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate work ID in wave inputs")
    for p in packets:
        if p["status"] != "runnable" or not p["problems"]:
            raise ValueError("cannot dispatch blocked or unscoped packet " + p["id"])
        if len(p["problems"]) != len(set(p["problems"])):
            raise ValueError("duplicate problem in packet " + p["id"])
        if scale.packet_digest(p) != p.get("packet_sha256"):
            raise ValueError("packet digest mismatch for " + p["id"])

    remaining = {p["id"]: p for p in packets}
    used = defaultdict(set)
    chosen = []
    while remaining and len(chosen) < budget:
        def key(p):
            first = sum(not used[t] for t in p["problems"])
            second = sum(len(used[t]) == 1 and p["kind"] not in used[t]
                         for t in p["problems"])
            return (-first, -second, -p["leverage"], p["priority_rank"], p["id"])
        best = min(remaining.values(), key=key)
        del remaining[best["id"]]
        chosen.append(best)
        for target in best["problems"]:
            used[target].add(best["kind"])
    return chosen


def _source_evidence(root):
    def read(relative):
        return json.loads((root / relative).read_text(encoding="utf-8"))
    problems = read("data/problems.json")
    ids = [p["id"] for p in problems]
    if len(ids) != 100 or len(set(ids)) != 100:
        raise ValueError("expected 100 unique active problems")
    campaigns = {c["problem_id"] for c in read("data/research_program.json")["campaigns"]}
    formal = {f["problem_id"] for f in read("data/formalization.json")["entries"]}
    exact = {v["problem_id"] for v in read("data/lab_results.json")["levels"]["deep"].values()
             if v["holds"] is True}
    for label, items in (("campaigns", campaigns), ("formal", formal), ("probes", exact)):
        if not items <= set(ids):
            raise ValueError("unknown problem in " + label)
    return problems, campaigns, formal, exact


def coverage_matrix(packets, problems, campaigns, formal, exact):
    kinds = defaultdict(set)
    assignments = defaultdict(list)
    for p in packets:
        for pid in p["problems"]:
            kinds[pid].add(p["kind"])
            assignments[pid].append(p["id"])
    if set(assignments) - {p["id"] for p in problems}:
        raise ValueError("packet targets missing from active registry")
    rows = []
    for p in problems:
        pid = p["id"]
        rows.append({
            "problem_id": pid,
            "field": p["field"],
            "evidence_state": p["evidence_state"],
            "registry_source_recorded": bool(p.get("source_url") and p.get("checked_on")),
            "campaign_documented": pid in campaigns,
            "exact_probe_recorded": pid in exact,
            "formal_statement_recorded": pid in formal,
            "planned_work_kinds": sorted(kinds[pid]),
            "planned_work_ids": assignments[pid],
        })
    return rows


def summary(rows):
    return {
        "problems_touched": sum(bool(p["planned_work_ids"]) for p in rows),
        "two_distinct_work_kinds": sum(len(p["planned_work_kinds"]) >= 2 for p in rows),
        "recorded_source_anchors": sum(p["registry_source_recorded"] for p in rows),
        "documented_campaigns": sum(p["campaign_documented"] for p in rows),
        "exact_probe_targets": sum(p["exact_probe_recorded"] for p in rows),
        "formal_statement_targets": sum(p["formal_statement_recorded"] for p in rows),
    }


def build(root=ROOT, budget=DEFAULT_BUDGET, candidates=None, registry=None):
    # The existing work queue is the authority for refusals, dependencies,
    # role plans and scope digests. No new mathematical tasks are fabricated.
    source = scale.wave(budget=100000) if candidates is None else candidates
    eligible = source["selected_packets"]
    selected = choose_breadth_first(eligible, budget)
    problems, campaigns, formal, exact = _source_evidence(root) if registry is None else registry
    breadth_rows = coverage_matrix(selected, problems, campaigns, formal, exact)
    baseline_packets = eligible[:min(budget, len(eligible))]
    baseline_rows = coverage_matrix(baseline_packets, problems, campaigns, formal, exact)
    source_summary = summary(breadth_rows)
    baseline_summary = summary(baseline_rows)
    if any(p["id"] in {r["id"] for r in source["refused"]} for p in selected):
        raise ValueError("refused work accidentally selected")
    return {
        "schema": "svyable.coverage-depth.v1",
        "budget_slots": budget,
        "selected_count": len(selected),
        "eligible_count": len(eligible),
        "refused_count": len(source["refused"]),
        "source_note": "Read-only report of source ledger fields; recorded URLs are not authenticated reviews.",
        "evidence_boundary": (
            "Planned work types are not independently verified proofs, experiments, accepted reviews or speedup. "
            "Existing exact probes reproduce known finite results only."
        ),
        "breadth_first": source_summary,
        "existing_ranked_at_same_budget": baseline_summary,
        "by_kind": dict(sorted(Counter(p["kind"] for p in selected).items())),
        "problem_matrix": breadth_rows,
        "selected_packets": selected,
    }


def render(doc):
    a, b = doc["breadth_first"], doc["existing_ranked_at_same_budget"]
    lines = [
        "# Coverage — breadth-first research deployment plan",
        "",
        "Generated by `python3 scripts/coverage.py --write`; do not edit by hand.",
        "",
        "**Planning only.** " + doc["evidence_boundary"],
        "",
        "## Coverage versus existing leverage-only allocation",
        "",
        "| Dimension | Breadth-first | Existing ranking at equal budget |",
        "|---|---:|---:|",
        f"| Claimable selected work slots | {doc['selected_count']} | {min(doc['budget_slots'],doc['eligible_count'])} |",
        f"| Problem IDs with at least one slot | {a['problems_touched']} | {b['problems_touched']} |",
        f"| Problem IDs with at least two distinct work kinds | **{a['two_distinct_work_kinds']}** | {b['two_distinct_work_kinds']} |",
        f"| Recorded source anchors (not verified by this report) | {a['recorded_source_anchors']} | {b['recorded_source_anchors']} |",
        f"| Documented research campaigns | {a['documented_campaigns']} | {b['documented_campaigns']} |",
        f"| Problem IDs with exact lab probes | {a['exact_probe_targets']} | {b['exact_probe_targets']} |",
        f"| Problem IDs with formal statements | {a['formal_statement_targets']} | {b['formal_statement_targets']} |",
        "",
        f"Planning budget: **{doc['budget_slots']}**; currently eligible distinct work packets: "
        f"**{doc['eligible_count']}**; refused by existing gate: **{doc['refused_count']}**.",
        "",
        "The optimizer first chooses packets covering yet-untouched problem IDs, then packets "
        "adding a second *different work kind* to a problem. Existing leverage and rank break ties. "
        "The greedy assignment does not prove optimality or equivalence of effort per task. "
        "When the two-kind minimum is achieved, remaining slots are chosen by existing leverage. "
        "Tasks overlapping several problems count for all their stated targets, but still correspond "
        "to **one** claim and **one** deliverable—not multiple verified findings.",
        "",
        "Run `python3 scripts/coverage.py --json` for full source-bound work packets and existing-claim "
        "links. Before execution search GitHub for an existing `[Claim] <id>` and do not duplicate it. "
        "No agents are launched by generating this report.",
        "",
        "## Source evidence and planned work by problem",
        "",
        "`Src` means source URL **and** date are populated in the registry, not that an independent "
        "status audit occurred. `Campaign` means an authored plan. `Probe` means an exact finite "
        "lab check (not a new theorem). `Formal` means a registered formal statement, "
        "not a scope-audited unrestricted proof. Missing entries are not necessarily computable tasks.",
        "",
        "| ID | Field | Src | Campaign | Probe | Formal | Planned distinct work kinds |",
        "|---|---|:---:|:---:|:---:|:---:|---|",
    ]
    for r in doc["problem_matrix"]:
        yes = lambda key: "✓" if r[key] else "—"
        lines.append(f"| `{r['problem_id']}` | {r['field']} | {yes('registry_source_recorded')} | "
                     f"{yes('campaign_documented')} | {yes('exact_probe_recorded')} | "
                     f"{yes('formal_statement_recorded')} | "
                     f"{', '.join('`'+x+'`' for x in r['planned_work_kinds']) or '—'} |")
    lines += [
        "", "## Guardrails", "",
        "All candidate packets come from the existing dependency-gated work queue, including prior-art "
        "refusals and scope hashes. The planner does not invent claim IDs, change scores or solved states, "
        "declare a paper independently reviewed, or reclassify open problems. "
        "Actual progress is accounted for by `data/outcomes.json` and independently reviewed claims, not "
        "by these planned coverage counts.", "",
        "For observed yield see [YIELD.md](YIELD.md); for the original leverage-first 100-slot "
        "baseline see [SCALE.md](SCALE.md); for preregistered causal comparison "
        "see [benchmarks/PROTOCOL.md](benchmarks/PROTOCOL.md).", "",
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--budget", type=int, default=DEFAULT_BUDGET)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    doc = build(budget=args.budget)
    content = render(doc)
    if args.check:
        if args.budget != DEFAULT_BUDGET:
            raise SystemExit("--check requires the committed default 200-slot plan")
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit("Stale COVERAGE.md: run python3 scripts/coverage.py --write")
        print("OK: breadth-first coverage depth {}/100, source evidence separated".format(
            doc["breadth_first"]["two_distinct_work_kinds"]))
    elif args.write:
        OUTPUT.write_text(content, encoding="utf-8")
        print("Updated COVERAGE.md")
    elif args.json:
        print(json.dumps(doc, sort_keys=True, indent=2, ensure_ascii=False))
    else:
        print("Coverage: {} / 100 problems with >=2 distinct planned work kinds in {} slots "
              "(existing ranked allocation at same budget: {} / 100).".format(
                  doc["breadth_first"]["two_distinct_work_kinds"], doc["selected_count"],
                  doc["existing_ranked_at_same_budget"]["two_distinct_work_kinds"]))
        print(doc["evidence_boundary"])


if __name__ == "__main__":
    main()
