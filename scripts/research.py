#!/usr/bin/env python3
"""Conservative research-program validation, progress accounting and attack queue.

The editorial score and execution-readiness score are deliberately separate.
Neither measures probability of solving a conjecture. No status can be inferred
from unreviewed claims, solver output, or the existence of a campaign.
"""
import argparse
from datetime import date
import json
from pathlib import Path
from urllib.parse import urlparse
from rank import ROOT, REGISTRY, score, validate

PROGRAM = ROOT / "data" / "research_program.json"
SOLVED = ROOT / "data" / "solved.json"
QUEUE = ROOT / "ATTACK_QUEUE.md"
STAGES = {"specified", "benchmark_reproduced", "restricted_verified", "claim_under_review"}
MILESTONE_CLASSES = {"reproduced_known", "restricted_verified"}
RUNNABLE = {
    "python3 scripts/ramsey.py demo": "scripts/ramsey.py",
    "python3 scripts/union_closed.py exhaustive --n 4": "scripts/union_closed.py",
}


def https(value):
    return isinstance(value, str) and (
        lambda u: u.scheme == "https" and bool(u.netloc)
    )(urlparse(value))


def valid_date(value):
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def required(obj, keys, where):
    for key in keys:
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            raise ValueError(f"{where}: required nonempty string {key}")


def validate_solved(solved, active):
    """Archive is intentionally empty until full resolutions pass strict gates."""
    if not isinstance(solved, list):
        raise ValueError("Solved archive must be an array")
    seen = set()
    for record in solved:
        required(record, (
            "original_problem_id", "name", "full_statement", "resolution",
            "proof_url", "accepted_on", "verification_notes", "replacement_id",
        ), "solved entry")
        old_id = record["original_problem_id"]
        if old_id in seen or old_id in active:
            raise ValueError(f"Solved ID must be unique and absent from active 100: {old_id}")
        seen.add(old_id)
        if record["resolution"] not in {"proved", "refuted"}:
            raise ValueError("Only fully proved or refuted statements enter Solved")
        if record["replacement_id"] not in active:
            raise ValueError("Solved entry needs an active replacement ID")
        if not valid_date(record["accepted_on"]) or not https(record["proof_url"]):
            raise ValueError("Solved entry needs accepted date and HTTPS proof")
        sources = record.get("independent_review_urls")
        if not isinstance(sources, list) or len(sources) < 2 or not all(map(https, sources)):
            raise ValueError("Solved entry requires at least two independent HTTPS reviews")
        hosts = {urlparse(u).netloc.lower() for u in sources}
        if len(hosts) < 2:
            raise ValueError("Reviews must come from two distinct domains")
        if len(record["verification_notes"].strip()) < 60:
            raise ValueError("Explain exact scope and independent review in detail")
    return solved


def load():
    items = validate(json.loads(REGISTRY.read_text(encoding="utf-8")))
    indexed = {p["id"]: p for p in items}
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    solved = validate_solved(json.loads(SOLVED.read_text(encoding="utf-8")), indexed)
    if type(program.get("version")) is not int or not valid_date(program.get("as_of")):
        raise ValueError("Program version/as_of invalid")
    campaigns = program.get("campaigns")
    milestones = program.get("milestones")
    if not isinstance(campaigns, list) or not isinstance(milestones, list):
        raise ValueError("Campaigns and milestones must be arrays")
    seen_campaigns, seen_milestones = set(), set()
    campaigns_by_id = {}
    for c in campaigns:
        required(c, ["problem_id", "stage", "method", "hypothesis", "first_proof_obligation",
                     "next_experiment", "falsification", "blocker", "dossier"], "campaign")
        pid = c["problem_id"]
        if pid not in indexed or pid in seen_campaigns or c["stage"] not in STAGES:
            raise ValueError(f"Invalid/duplicate campaign: {pid}")
        if c["dossier"].startswith("/") or ".." in Path(c["dossier"]).parts:
            raise ValueError("Invalid dossier path")
        if not (ROOT / c["dossier"]).is_file():
            raise ValueError(f"Missing dossier: {c['dossier']}")
        verifier = c.get("verifier")
        if verifier is not None and verifier not in RUNNABLE:
            raise ValueError(f"Unallowlisted verifier: {verifier}")
        if verifier and c["stage"] == "specified":
            raise ValueError("Runnable campaign must declare benchmark stage")
        if c["stage"] == "benchmark_reproduced" and not verifier:
            raise ValueError("Benchmark stage requires actual verifier")
        seen_campaigns.add(pid)
        campaigns_by_id[pid] = c
    for m in milestones:
        required(m, ["id", "problem_id", "classification", "title", "scope",
                     "description", "verifier", "artifact", "verified_on"], "milestone")
        pid = m["problem_id"]
        if pid not in campaigns_by_id or m["id"] in seen_milestones:
            raise ValueError(f"Invalid/duplicate milestone: {m['id']}")
        seen_milestones.add(m["id"])
        if m["classification"] not in MILESTONE_CLASSES:
            raise ValueError("Unverified/ambiguous milestone class")
        if m["verifier"] not in RUNNABLE or m["verifier"] != campaigns_by_id[pid]["verifier"]:
            raise ValueError("Milestone verifier must be approved and match campaign")
        if m["artifact"] != RUNNABLE[m["verifier"]] or not (ROOT / m["artifact"]).is_file():
            raise ValueError("Missing or mismatched exact verification artifact")
        if not valid_date(m["verified_on"]):
            raise ValueError("Invalid milestone verification date")
        if m["classification"] == "restricted_verified":
            sources = m.get("independent_review_urls")
            if not isinstance(sources, list) or len(sources) < 2 or not all(map(https, sources)):
                raise ValueError("New restricted theorem requires two independent reviews")
            if len({urlparse(u).netloc for u in sources}) < 2:
                raise ValueError("New restricted-theorem reviews must be independent")
        elif m.get("independent_review_urls"):
            raise ValueError("Known theorem reproduction is not independently new")
    for c in campaigns:
        m = [x for x in milestones if x["problem_id"] == c["problem_id"]]
        if c["stage"] == "benchmark_reproduced" and not any(
            x["classification"] == "reproduced_known" for x in m
        ):
            raise ValueError("Benchmark stage lacks actual reproduced-known milestone")
        if c["stage"] == "restricted_verified" and not any(
            x["classification"] == "restricted_verified" for x in m
        ):
            raise ValueError("Restricted verified stage lacks independently reviewed theorem")
    return items, program, solved


def readiness(problem_id, program):
    campaigns = {c["problem_id"]: c for c in program["campaigns"]}
    campaign = campaigns.get(problem_id)
    if not campaign:
        return 0
    marks = [m for m in program["milestones"] if m["problem_id"] == problem_id]
    return min(10,
        2 +  # formal campaign brief
        (3 if campaign["verifier"] else 0) +  # runnable independent baseline checker
        (2 if any(m["classification"] == "reproduced_known" for m in marks) else 0) +
        (3 if any(m["classification"] == "restricted_verified" for m in marks) else 0))


def execution_order(items, program):
    order = sorted(items, key=lambda p: (-(score(p) + readiness(p["id"], program)), p["id"]))
    return {
        p["id"]: {"execution_rank": i, "execution_score": score(p) + readiness(p["id"], program),
                  "readiness": readiness(p["id"], program)}
        for i, p in enumerate(order, 1)
    }


def render_queue(items, program, solved):
    ranked = execution_order(items, program)
    by_id = {c["problem_id"]: c for c in program["campaigns"]}
    ordered = sorted(items, key=lambda p: ranked[p["id"]]["execution_rank"])
    lines = [
        "# Execution queue — evidence-aware research priorities", "",
        f"Program intake: {program['as_of']}. **{len(solved)} independently reviewed full solutions** archived.",
        "These ranks measure *where to deploy proof effort*, not the likelihood of proving a conjecture.", "",
        "Execution index = editorial 20–100 score + readiness (0–10). Readiness counts a specific",
        "campaign brief (+2), an allowlisted exact verifier (+3), a reproduced **known** benchmark",
        "(+2), and an independently reviewed new restricted result (+3). A known benchmark never",
        "counts as a new theorem, and unreviewed claims receive no bonus.", "",
        "| Attack rank | ID | Problem | Base | Readiness | Index | Next step |",
        "|---:|---|---|---:|---:|---:|---|",
    ]
    for p in ordered:
        mark = ranked[p["id"]]
        c = by_id.get(p["id"])
        next_step = c["next_experiment"] if c else "Specify a falsifiable restricted lemma and audit prior art"
        next_step = next_step.replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {mark['execution_rank']} | {p['id']} | {p['name']} | {score(p)} "
            f"| +{mark['readiness']} | {mark['execution_score']} | {next_step} |"
        )
    lines += ["", "## Active proof campaigns", ""]
    for p in ordered:
        c = by_id.get(p["id"])
        if not c:
            continue
        lines += [
            f"### {p['id']} — {p['name']}", "",
            f"**Proof obligation:** {c['first_proof_obligation']}", "",
            f"**Falsifier:** {c['falsification']}", "",
            f"**Next experiment:** {c['next_experiment']}", "",
            f"**Current blocker:** {c['blocker']}", "",
            f"**Stage:** `{c['stage']}` · [Dossier]({c['dossier']})", "",
        ]
    lines += [
        "## What counts as solved?", "",
        "Only an independently confirmed *full* proof or counterexample with exact theorem scope,",
        "two distinct independent reviews, dated acceptance, and a replacement active candidate",
        "can enter [data/solved.json](data/solved.json). Existing known small-case reproductions",
        "remain research milestones, never Solved entries.", "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    opts = parser.parse_args()
    items, program, solved = load()
    content = render_queue(items, program, solved)
    if opts.check:
        if not QUEUE.exists() or QUEUE.read_text(encoding="utf-8") != content:
            raise SystemExit("Stale attack queue: run python3 scripts/research.py")
        print("OK: execution queue and research evidence are consistent")
    else:
        QUEUE.write_text(content, encoding="utf-8")
        print("Updated ATTACK_QUEUE.md")


if __name__ == "__main__":
    main()
