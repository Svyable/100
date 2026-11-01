#!/usr/bin/env python3
"""Build the GitHub Pages site from the canonical registry, campaigns, lab and archives.

Writes ``docs/data/portfolio.json`` (the full legacy snapshot) plus the whole
static multi-page site rendered by ``sitegen`` (a page per problem, field,
campaign index, lab, claims, ledger, library document, JSON/CSV API, Atom feed
and sitemap). Nothing under the generated paths may be edited by hand:
``--check`` byte-compares every file and fails on stale leftovers.
"""
import argparse
import json
from rank import score, ROOT
from research import load, execution_order
import approach
import lab
import mine
import roadmap
import sitegen

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


def site_files():
    """Every generated file under docs/ as {relative path: text}."""
    portfolio = build()
    files = sitegen.build_files(portfolio)
    files["data/portfolio.json"] = json.dumps(portfolio, indent=2, ensure_ascii=False) + "\n"
    return files


def check(files):
    """Paths that differ from the committed tree, plus stale generated leftovers."""
    drift = [path for path, text in sorted(files.items())
             if not (sitegen.DOCS / path).is_file()
             or (sitegen.DOCS / path).read_text(encoding="utf-8") != text]
    return drift, sitegen.stale_files(files)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="fail if any generated Pages file is stale or missing")
    opts = parser.parse_args()
    files = site_files()
    if opts.check:
        drift, stale = check(files)
        if drift or stale:
            for path in drift[:20]:
                print(f"stale or missing: docs/{path}")
            for path in stale[:20]:
                print(f"no longer generated: docs/{path}")
            raise SystemExit("Stale GitHub Pages site: run python3 scripts/build_site.py")
        pages = sum(p.endswith(".html") for p in files)
        print(f"OK: {len(files)} generated Pages files ({pages} HTML pages) match the validated ledgers")
    else:
        for path in sitegen.stale_files(files):
            (sitegen.DOCS / path).unlink()
        for d in sitegen.GENERATED_DIRS:
            for folder in sorted((sitegen.DOCS / d).glob("**/"), key=lambda q: -len(q.parts)):
                if folder.is_dir() and not any(folder.iterdir()):
                    folder.rmdir()
        for path, text in files.items():
            target = sitegen.DOCS / path
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.is_file() or target.read_text(encoding="utf-8") != text:
                target.write_text(text, encoding="utf-8")
        pages = sum(p.endswith(".html") for p in files)
        print(f"Updated docs/: {len(files)} generated files, {pages} HTML pages")


if __name__ == "__main__":
    main()
