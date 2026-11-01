#!/usr/bin/env python3
"""Build Pages data from canonical registry, proof campaigns, milestones and archive.

The snapshot cannot be edited independently. Both portfolio prestige rank and
execution-ready attack rank are deterministic and their meanings are distinct.
"""
import argparse
import json
from rank import score, ROOT
from research import load, execution_order
import approach
import lab
import mine
import roadmap

OUTPUT = ROOT / "docs" / "data" / "portfolio.json"


def build():
    items, program, solved = load()
    baseline = sorted(items, key=lambda p: (-score(p), p["id"]))
    execution = execution_order(items, program)
    dispatched = {row["problem_id"]: row for row in approach.rows(items, program)}
    campaign_by_id = {c["problem_id"]: c for c in program["campaigns"]}
    active_ids = {p["id"] for p in items}
    milestones_by_id = {
        p["id"]: [m for m in program["milestones"] if m["problem_id"] == p["id"]]
        for p in items
    }
    active_rank = {p["id"]: i for i, p in enumerate(baseline, 1)}
    return {
        "title": "100 — A living mathematical research portfolio",
        "source": "data/problems.json",
        "source_review_as_of": max((p["checked_on"] or "" for p in items), default=""),
        "scoring": {
            "impact": 30,
            "attackability": 30,
            "verifiability": 25,
            "spillover": 15,
            "interpretation": "Editorial priority score, not an estimated proof probability",
        },
        "status_counts": {
            status: sum(p["evidence_state"] == status for p in items)
            for status in sorted({p["evidence_state"] for p in items})
        },
        "program_as_of": program["as_of"],
        "summary": {
            "campaigns": sum(c["problem_id"] in active_ids for c in program["campaigns"]),
            "reproduced_known": sum(
                m["classification"] == "reproduced_known" for m in program["milestones"]),
            "restricted_verified": sum(
                m["classification"] == "restricted_verified" for m in program["milestones"]),
            "fully_solved": len(solved),
            "problems_with_exact_verifier": len(lab.coverage(items, program)),
            "exact_probes": len(lab.probes.PROBES),
            "engines": len(lab.probes.ENGINES),
        },
        "execution_scoring": {
            "brief": 2,
            "runnable_verifier": 3,
            "known_reproduction": 2,
            "independently_verified_restricted_theorem": 3,
            "interpretation": "Operational readiness bonus (0–10), not mathematical proof progress",
        },
        "problems": [
            {
                **item, "rank": number, "score": score(item),
                **execution[item["id"]],
                "dispatch_rank": dispatched[item["id"]]["dispatch_rank"],
                "dispatch_score": dispatched[item["id"]]["dispatch_score"],
                "action": dispatched[item["id"]]["action"],
                "action_label": dispatched[item["id"]]["action_label"],
                "action_bonus": dispatched[item["id"]]["action_bonus"],
                "method_id": dispatched[item["id"]]["method_id"],
                "method_title": dispatched[item["id"]]["method_title"],
                "dispatch_next": dispatched[item["id"]]["next_step"],
                "dispatch_why": dispatched[item["id"]]["why"],
                "campaign_stage": campaign_by_id.get(item["id"], {}).get("stage"),
                "milestone_count": len(milestones_by_id[item["id"]]),
            }
            for number, item in enumerate(baseline, start=1)
        ],
        "lab": lab.snapshot(),
        "mines": mine.snapshot(),
        "roadmap": roadmap.snapshot(),
        "campaigns": program["campaigns"],
        "milestones": program["milestones"],
        "solved": solved,
        "approach": approach.snapshot(items, program),
        "execution_queue": [
            {
                "problem_id": c["problem_id"],
                "name": next(p["name"] for p in items if p["id"] == c["problem_id"]),
                "execution_rank": execution[c["problem_id"]]["execution_rank"],
                "execution_score": execution[c["problem_id"]]["execution_score"],
                "dispatch_rank": dispatched[c["problem_id"]]["dispatch_rank"],
                "dispatch_score": dispatched[c["problem_id"]]["dispatch_score"],
                "action": dispatched[c["problem_id"]]["action"],
                "action_label": dispatched[c["problem_id"]]["action_label"],
                "baseline_rank": active_rank[c["problem_id"]],
                "stage": c["stage"],
                "first_proof_obligation": c["first_proof_obligation"],
                "next_experiment": dispatched[c["problem_id"]]["next_step"],
                "recorded_experiment": c["next_experiment"],
                "blocker": c["blocker"],
                "dossier": c["dossier"],
            }
            for c in sorted((c for c in program["campaigns"] if c["problem_id"] in active_ids),
                            key=lambda c: dispatched[c["problem_id"]]["dispatch_rank"])
        ],
    }


def render():
    return json.dumps(build(), indent=2, ensure_ascii=False) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="fail if the committed snapshot is stale")
    opts = parser.parse_args()
    expected = render()
    if opts.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit("Stale GitHub Pages snapshot: run python3 scripts/build_site.py")
        print("OK: Pages snapshot includes 100 problems, evidence, execution ranks, and solved archive")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(expected, encoding="utf-8")
        print("Updated docs/data/portfolio.json")


if __name__ == "__main__":
    main()
