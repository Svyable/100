#!/usr/bin/env python3
"""Leverage dispatch: what to work on next.

Readiness still measures documented evidence only. The dispatch score chooses
the next hour of work. A method shape is an attack template shared by a cohort.
It is not a theorem, not a claim that the case is open, and not a score change.

    python3 scripts/approach.py           # write APPROACH.md
    python3 scripts/approach.py --check   # fail if the file or the rules drift
"""
import argparse
import json
from rank import ROOT, score
import research

SOURCE = ROOT / "data" / "methods.json"
CLAIMS = ROOT / "data" / "claim_reviews_2026.json"
OUTPUT = ROOT / "APPROACH.md"
ACTIONS = (
    "replay_claim_witness",
    "build_engine",
    "replay_published",
    "lock_restriction",
    "mine_structure",
    "scope_audit",
    "specify_shape",
    "stop_range",
)
CAMPAIGN_ACTIONS = {
    "replay_claim_witness", "replay_published", "lock_restriction",
    "mine_structure", "scope_audit", "stop_range",
}
GENERIC = "Specify a falsifiable restricted lemma and audit prior art"


class ApproachError(ValueError):
    pass


def _text(value, where, minimum):
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise ApproachError(f"{where} needs at least {minimum} characters")
    return value.strip()


def load_doc(doc=None):
    if doc is None:
        doc = json.loads(SOURCE.read_text(encoding="utf-8"))
    if doc.get("schema_version") != 1:
        raise ApproachError("methods schema_version must be 1")
    _text(doc.get("note"), "methods note", 40)
    actions = doc.get("actions")
    if not isinstance(actions, dict) or tuple(actions) != ACTIONS:
        raise ApproachError(f"actions must be exactly {ACTIONS}")
    for name, spec in actions.items():
        if type(spec.get("bonus")) is not int:
            raise ApproachError(f"{name}: bonus must be an int")
        _text(spec.get("label"), f"{name} label", 8)
        _text(spec.get("meaning"), f"{name} meaning", 40)
        if name == "stop_range" and spec["bonus"] >= 0:
            raise ApproachError("stop_range bonus must be negative")
        if name != "stop_range" and spec["bonus"] < 0:
            raise ApproachError(f"{name}: only stop_range may have a negative bonus")
    extra = actions["scope_audit"].get("mismatch_extra")
    if type(extra) is not int or extra <= 0:
        raise ApproachError("scope_audit needs a positive mismatch_extra")
    witness = doc.get("witness_replay")
    if not isinstance(witness, list) or len(witness) != len(set(witness)):
        raise ApproachError("witness_replay must be a list of unique ids")
    campaigns = doc.get("campaign_actions")
    if not isinstance(campaigns, dict):
        raise ApproachError("campaign_actions must be an object")
    methods = doc.get("methods")
    if not isinstance(methods, list) or not methods:
        raise ApproachError("methods must be a non-empty list")
    return doc


def _known_engines():
    import probes
    names = set(probes.ENGINES)
    road = json.loads((ROOT / "data" / "engine_roadmap.json").read_text(encoding="utf-8"))
    names.update(entry["engine"] for entry in road["entries"])
    return names


def _claims():
    payload = json.loads(CLAIMS.read_text(encoding="utf-8"))
    reviews = payload.get("reviews")
    if not isinstance(reviews, list):
        raise ApproachError("claim reviews missing")
    by_id = {}
    for review in reviews:
        pid = review.get("id")
        if pid in by_id:
            raise ApproachError(f"duplicate claim review {pid}")
        _text(review.get("next_review"), f"{pid} next_review", 40)
        by_id[pid] = review
    return by_id


def _methods(doc, ids, engines):
    seen, by_problem = set(), {}
    for method in doc["methods"]:
        mid = method.get("id")
        if not isinstance(mid, str) or not mid.replace("_", "").isalpha() or mid in seen:
            raise ApproachError(f"bad or duplicate method id {mid!r}")
        seen.add(mid)
        _text(method.get("title"), mid, 8)
        lead = _text(method.get("lead"), f"{mid} lead", 40)
        shape = _text(method.get("shape"), f"{mid} shape", 80)
        if not shape.startswith(lead):
            raise ApproachError(f"{mid}: shape must start with its lead sentence")
        _text(method.get("certificate"), f"{mid} certificate", 40)
        _text(method.get("falsifier"), f"{mid} falsifier", 40)
        listed = method.get("engines")
        if not isinstance(listed, list) or any(e not in engines for e in listed):
            raise ApproachError(f"{mid}: unknown engine")
        problems = method.get("problems")
        if not isinstance(problems, list) or problems != sorted(problems) or len(problems) != len(set(problems)):
            raise ApproachError(f"{mid}: problems must be unique and sorted")
        for pid in problems:
            if pid not in ids or pid in by_problem:
                raise ApproachError(f"{mid}: {pid} missing or repeated")
            by_problem[pid] = method
    missing = sorted(ids - set(by_problem))
    if missing:
        raise ApproachError("methods do not cover " + ", ".join(missing))
    return by_problem


def _bonus(doc, action, review):
    spec = doc["actions"][action]
    bonus = spec["bonus"]
    if action == "scope_audit" and review.get("scope_relation") == "different_statement":
        bonus += spec["mismatch_extra"]
    return bonus


def _shape_step(method):
    count = len(method["problems"])
    return (
        f"Shape {method['id']} ({count} problems, one write-up): {method['lead']} "
        "Full shape, certificate and falsifier are in APPROACH.md."
    )


def rows(items, program, doc=None):
    """One dispatch record per active problem, ranked."""
    doc = load_doc(doc)
    import lab
    indexed = {p["id"]: p for p in items}
    reviews = _claims()
    covered = lab.coverage(items, program)
    roadmap = {e["problem_id"]: e for e in lab.load_roadmap(items, covered)["entries"]}
    by_method = _methods(doc, set(indexed), _known_engines())
    campaigns = {c["problem_id"]: c for c in program["campaigns"]}
    actions = doc["campaign_actions"]
    if set(actions) != set(campaigns):
        raise ApproachError("campaign_actions must match the research-program campaigns exactly")
    witness = set(doc["witness_replay"])
    for pid in witness:
        if pid not in reviews or indexed[pid]["evidence_state"] != "claim_needs_review":
            raise ApproachError(f"{pid} is listed for witness replay without a claim review")
    claim_ids = {pid for pid, p in indexed.items() if p["evidence_state"] == "claim_needs_review"}
    if set(reviews) != claim_ids:
        raise ApproachError("claim reviews must match claim_needs_review exactly")

    built = []
    for pid, problem in indexed.items():
        method = by_method[pid]
        campaign = campaigns.get(pid)
        chosen = actions.get(pid)
        review = reviews.get(pid)
        if chosen is not None:
            if chosen.get("action") not in CAMPAIGN_ACTIONS:
                raise ApproachError(f"{pid}: campaign action not allowed")
            _text(chosen.get("why"), f"{pid} why", 40)
        if pid in witness:
            action = "replay_claim_witness"
            if campaign:
                if chosen is None or chosen["action"] != action or "next_step" in chosen:
                    raise ApproachError(
                        f"{pid}: witness replay must be the campaign action, with no next_step override")
                why = chosen["why"]
            else:
                if chosen is not None:
                    raise ApproachError(f"{pid}: witness replay without a campaign has no campaign action")
                why = "Listed for witness replay. The next step is the claim review's finite check."
            step = review["next_review"]
        elif problem["evidence_state"] == "claim_needs_review":
            action = "scope_audit"
            if chosen not in (None, {}) and (chosen.get("action") != action or "next_step" in chosen):
                raise ApproachError(f"{pid}: a non-witness claim stays on the review text")
            if campaign and chosen is None:
                raise ApproachError(f"{pid}: campaigned claim needs a scope_audit action")
            step = review["next_review"]
            if review.get("scope_relation") == "different_statement":
                why = "The claim review records a different statement. Close that watch before opening an attack."
            else:
                why = "A manuscript may already settle this entry. The next step is the review's own check, not a new lemma."
        elif pid in roadmap:
            action = "build_engine"
            if campaign or chosen:
                raise ApproachError(f"{pid}: an engine-roadmap problem has no campaign yet")
            entry = roadmap[pid]
            others = [p for p in method["problems"] if p != pid]
            step = f"Build engine {entry['engine']} once. {entry['first_probe']}"
            if others:
                step += " One build serves this shape, including " + ", ".join(others) + "."
            why = "Computable modality, no verifier, and the engine roadmap names the missing engine."
        elif campaign:
            if chosen is None:
                raise ApproachError(f"{pid}: campaign missing a dispatch action")
            action = chosen["action"]
            if action in {"replay_claim_witness", "scope_audit", "build_engine", "specify_shape"}:
                raise ApproachError(f"{pid}: {action} is assigned by a rule, not as a bare campaign action")
            if action in {"stop_range", "lock_restriction"}:
                step = _text(chosen.get("next_step"), f"{pid} next_step", 40)
            else:
                step = chosen.get("next_step") or campaign["next_experiment"]
                _text(step, f"{pid} next_step", 40)
            if action == "stop_range" and not step.startswith("Do not"):
                raise ApproachError(f"{pid}: a refused range must say what not to do")
            if action == "lock_restriction":
                if campaign.get("verifier"):
                    raise ApproachError(f"{pid}: lock the class before attaching a verifier")
                if not step.startswith("Lock"):
                    raise ApproachError(f"{pid}: lock_restriction starts by locking the class")
            if action == "stop_range" and pid not in covered:
                raise ApproachError(f"{pid}: refusing a range requires an existing verifier")
            why = chosen["why"]
        else:
            action = "specify_shape"
            step = _shape_step(method)
            why = "No campaign yet. Fill one restricted statement inside the shared shape."
        _text(step, f"{pid} next_step", 40)
        if GENERIC in step or GENERIC in why:
            raise ApproachError(f"{pid}: the generic next sentence is not a dispatch step")
        bonus = _bonus(doc, action, review or {})
        ready = research.readiness(pid, program)
        built.append({
            "problem_id": pid,
            "name": problem["name"],
            "field": problem["field"],
            "action": action,
            "action_label": doc["actions"][action]["label"],
            "action_bonus": bonus,
            "method_id": method["id"],
            "method_title": method["title"],
            "next_step": step,
            "why": why,
            "score": score(problem),
            "readiness": ready,
            "dispatch_score": score(problem) + ready + bonus,
        })
    if {r["problem_id"] for r in built if r["action"] == "build_engine"} != set(roadmap):
        raise ApproachError("build_engine drifted from the engine roadmap")
    built.sort(key=lambda r: (-r["dispatch_score"], r["problem_id"]))
    for index, row in enumerate(built, 1):
        row["dispatch_rank"] = index
    return built


def jobs(records):
    """One job per action on a shared shape. A job is the unit of work."""
    groups = {}
    for row in records:
        key = (row["action"], row["method_id"])
        groups.setdefault(key, []).append(row)
    built = []
    for (action, method_id), members in groups.items():
        members = sorted(members, key=lambda r: r["dispatch_rank"])
        distinct = list(dict.fromkeys(row["next_step"] for row in members))
        if len(distinct) == 1:
            summary = distinct[0]
        else:
            summary = " ".join(f"{row['problem_id']}: {row['next_step']}" for row in members)
        built.append({
            "action": action,
            "action_label": members[0]["action_label"],
            "method_id": method_id,
            "method_title": members[0]["method_title"],
            "problem_ids": [row["problem_id"] for row in members],
            "best_rank": members[0]["dispatch_rank"],
            "summary": summary,
            "why": members[0]["why"] if len({row["why"] for row in members}) == 1 else "",
        })
    built.sort(key=lambda job: (job["best_rank"], job["method_id"]))
    return built


def snapshot(items, program, doc=None):
    doc = load_doc(doc)
    records = rows(items, program, doc)
    return {
        "note": doc["note"],
        "actions": doc["actions"],
        "jobs": jobs(records),
        "methods": [
            {
                "id": method["id"],
                "title": method["title"],
                "lead": method["lead"],
                "problems": method["problems"],
                "engines": method["engines"],
            }
            for method in doc["methods"]
        ],
    }


def _cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def render(items=None, program=None, doc=None):
    if items is None:
        items, program, _ = research.load()
    doc = load_doc(doc)
    records = rows(items, program, doc)
    grouped = jobs(records)
    by_method = {m["id"]: m for m in doc["methods"]}
    counts = {}
    for row in records:
        counts[row["action"]] = counts.get(row["action"], 0) + 1
    no_campaign = len(records) - len(program["campaigns"])
    lines = [
        "# Approach — leverage dispatch", "",
        "Generated by `python3 scripts/approach.py` from "
        "[data/methods.json](data/methods.json); do not edit by hand.", "",
        doc["note"], "",
        "Dispatch score = editorial score + readiness + an action bonus. "
        "The bonus is a scheduling weight. It is not evidence, not a probability, "
        "and it does not change readiness. A known benchmark still earns no novelty.", "",
        f"**{len(by_method)} shapes** cover all {len(records)} problems. "
        f"**{len(grouped)} jobs** (one action on one shape) replace a per-problem queue. "
        f"**{no_campaign} problems have no campaign**; each of them points at a shared shape "
        "instead of a private method. "
        f"**{counts.get('stop_range', 0)} recorded experiment"
        f"{'s are' if counts.get('stop_range', 0) != 1 else ' is'} refused** "
        "because the campaign blocker already places that range inside known mathematics.", "",
        "## Action bonuses", "",
        "| Action | Bonus | What it schedules |",
        "|---|---:|---|",
    ]
    for name in ACTIONS:
        spec = doc["actions"][name]
        extra = ""
        if name == "scope_audit":
            extra = f" A review whose scope is a different statement adds +{spec['mismatch_extra']}."
        lines.append(
            f"| `{name}` | {spec['bonus']:+d} | {_cell(spec['meaning'] + extra)} |"
        )
    lines += [
        "",
        "## Jobs, in dispatch order", "",
        "A job is the unit of work. Problems in the same row share a shape and an action. "
        "Doing the write-up, the engine, or the witness check once covers the row.", "",
    ]
    for index, job in enumerate(grouped, 1):
        ids = ", ".join(job["problem_ids"])
        lines += [
            f"### {index}. {job['action_label']}", "",
            f"**Shape:** {job['method_title']} (`{job['method_id']}`). "
            f"**Problems:** {ids}. **Best dispatch rank:** {job['best_rank']}.", "",
            job["summary"], "",
        ]
        if job["why"]:
            lines += [f"_{job['why']}_", ""]
    lines += ["## Shapes", ""]
    lines.append(
        "Each shape is a template for a restricted attack. Filling it in does not "
        "assert that the restriction is open, new, or true."
    )
    lines.append("")
    for method in doc["methods"]:
        engines = ", ".join(f"`{e}`" for e in method["engines"]) or "none yet"
        lines += [
            f"### `{method['id']}` — {method['title']}", "",
            f"**Problems:** {', '.join(method['problems'])}. **Engines:** {engines}.", "",
            method["shape"], "",
            f"**Certificate.** {method['certificate']}", "",
            f"**Falsifier.** {method['falsifier']}", "",
        ]
    lines += [
        "## Every problem", "",
        "| Dispatch | ID | Action | Bonus | Score | Shape | Next step |",
        "|---:|---|---|---:|---:|---|---|",
    ]
    for row in records:
        lines.append(
            f"| {row['dispatch_rank']} | {row['problem_id']} | `{row['action']}` | "
            f"{row['action_bonus']:+d} | {row['dispatch_score']} | `{row['method_id']}` | "
            f"{_cell(row['next_step'])} |"
        )
    lines += [
        "",
        "Readiness and the editorial score are defined in "
        "[docs/RESEARCH_ENGINE.md](docs/RESEARCH_ENGINE.md). "
        "The attack queue is the same order, rendered per problem.", "",
    ]
    return "\n".join(lines)


def assert_roadmap(doc):
    """In-flight roadmap items may not recommend a refused range extension."""
    items, program, _ = research.load()
    by_id = {row["problem_id"]: row for row in rows(items, program)}
    for item in doc["items"]:
        if item["horizon"] not in {"now", "next"}:
            continue
        stopped = [pid for pid in item.get("problems", []) if by_id[pid]["action"] == "stop_range"]
        if not stopped:
            continue
        text = f"{item['title']} {item['outcome']}"
        if "do not" not in text.lower():
            raise ApproachError(
                f"{item['id']} lists refused problem(s) {', '.join(stopped)} "
                "without saying not to extend that range"
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    opts = parser.parse_args()
    items, program, _ = research.load()
    content = render(items, program)
    if GENERIC in content:
        raise SystemExit("generic next sentence leaked into APPROACH.md")
    if opts.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit("Stale approach: run python3 scripts/approach.py")
        print("OK: leverage dispatch covers 100 problems")
    else:
        OUTPUT.write_text(content, encoding="utf-8")
        print("Updated APPROACH.md")


if __name__ == "__main__":
    main()
