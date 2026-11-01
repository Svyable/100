#!/usr/bin/env python3
"""The work queue: every bounded, claimable unit of work in the repository.

    python3 scripts/work.py --next 5            # the five highest-priority runnable items
    python3 scripts/work.py --next 5 --kind comparator
    python3 scripts/work.py --id F-M074         # one item in full
    python3 scripts/work.py --json              # the whole queue, machine-readable
    python3 scripts/work.py --check             # validate the derived queue

The queue is *derived*, never edited: each family is read from the ledger that
already defines it, and an item disappears as soon as its ledger records the
result. Nothing here changes a ledger, a rank or an evidence state.

Families (in priority order):

* ``obligation``   — nodes of ``data/proof_obligations.json`` (dependency-aware frontier)
* ``review``       — independent review of an artifact that exists but is not yet accepted
                     (implemented Lean targets, author-checked comparators, status drafts)
* ``lean``         — next deliverable of each ``data/lean_targets.json`` target
* ``job``          — cohort jobs from the dispatcher (``scripts/approach.py``)
* ``roadmap``      — roadmap items in the ``now`` and ``next`` horizons
* ``comparator``   — a Lean comparator statement for a problem that has none
* ``status_audit`` — a dated exact-status audit draft for a problem without one

Coordination: before starting an item, search open issues for its claim title
(``[Claim] <id>``); if none is open, open one (``.github/ISSUE_TEMPLATE/claim.yml``).
The scope digest pins what was claimed: if the item's text changes, so does the digest.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import quote

import approach
import benchmark
import outcomes
import proof_obligations
import scale
from research import load

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/Svyable/100"
FAMILIES = ("obligation", "review", "benchmark", "lean", "job", "roadmap", "comparator", "status_audit")
STATUS_ORDER = {"runnable": 0, "externally_blocked": 1, "waiting_on_dependencies": 2}
REGEN = "python3 scripts/regen.py && python3 scripts/regen.py --check"
TESTS = "python3 -m unittest discover -s tests"


def _json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(item):
    scope = {k: item[k] for k in ("id", "kind", "problems", "deliverable", "acceptance", "boundary")}
    # A review accepts the precise statement in context, not just a generic task title.
    # Leave existing non-review claim hashes stable for in-flight contributor claims.
    if item["kind"] == "review":
        scope["context"] = item.get("context", "")
    return hashlib.sha256(json.dumps(scope, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def claim_title(item):
    return f"[Claim] {item['id']} — {item['title']}"


def claim_links(item):
    title = claim_title(item)
    query = 'is:issue is:open in:title "[Claim] ' + item["id"] + '"'
    return {
        "claim_title": title,
        "open_claim_url": f"{REPO}/issues/new?template=claim.yml&title={quote(title)}",
        "existing_claims_url": f"{REPO}/issues?q={quote(query)}",
    }


def build():
    items, program, _ = load()
    by_id = {p["id"]: p for p in items}
    dispatch = {r["problem_id"]: r for r in approach.rows(items, program)}
    rank = lambda pids: min((dispatch[p]["dispatch_rank"] for p in pids if p in dispatch), default=999)
    work = []

    def add(**item):
        item.setdefault("depends_on", [])
        item["priority_rank"] = rank(item["problems"])
        work.append(item)

    # 1. Proof obligations: the acceptance frontier, with dependencies.
    frontier = {x["id"]: x for x in scale.frontier(proof_obligations.load(ROOT / "data/proof_obligations.json", ROOT))}
    for node in proof_obligations.load(ROOT / "data/proof_obligations.json", ROOT):
        f = frontier[node["id"]]
        if f["category"] == "discharged":
            continue
        add(id=node["id"], kind="obligation", status=f["category"], problems=[node["problem_id"]],
            title=f"{node['kind'].capitalize()} obligation for {node['problem_id']}",
            deliverable=node["next_action"], context=node["statement"],
            acceptance=[f"Discharge evidence recorded on {node['id']} in data/proof_obligations.json, "
                        "passing python3 scripts/proof_obligations.py --check",
                        "Independent review recorded before the node is marked discharged", REGEN],
            boundary=node["prior_art_boundary"], falsifier=node["falsifier"],
            depends_on=list(node["depends_on"]), source="data/proof_obligations.json")

    # 1b. Independent review: the acceptance bottleneck, made claimable. An item clears
    # when data/outcomes.json records an accepted_independent outcome for it.
    accepted = outcomes.accepted_review_scopes()
    independence = ("The reviewer is not an author of the artifact (check git log of its files) and records "
                    "the review in data/outcomes.json as accepted_independent or gap_reported, with a public review_url")
    problems_by_id = {p["id"]: p for p in items}
    for t in _json("data/lean_targets.json"):
        if t["stage"] != "implemented":
            continue
        add(id=f"V-{t['id']}", kind="review", status="runnable", problems=[t["problem_id"]],
            title=f"Independent scope review of Lean target {t['id']} ({t['problem_id']})",
            deliverable=("Compare every registered declaration of " + t["id"] + " with the registry statement and its "
                         "primary source: domains, quantifiers, nonemptiness and distinctness conditions, strict versus "
                         "weak inequalities, encodings. State exactly what is and is not established."),
            context=t["statement"],
            acceptance=[independence, "Any mismatch is filed as a gap on the target's scope_gap, not silently fixed", REGEN],
            boundary="A scope review checks that the encoded statement matches the claim; it does not add mathematics. "
                     + t["scope_gap"],
            falsifier="A quantifier, domain or convention in the Lean statement that differs from the registered claim.",
            source="data/lean_targets.json")
    for e in _json("data/formalization.json")["entries"]:
        wid = f"V-F-{e['problem_id']}"
        if e.get("fidelity") != "author_checked":
            continue
        add(id=wid, kind="review", status="runnable", problems=[e["problem_id"]],
            title=f"Independent fidelity review of the {problems_by_id[e['problem_id']]['name']} comparator",
            deliverable=(f"Check {e['namespace']}.{e['statement']} in {e['module']} against the registry statement and a "
                         "primary source; confirm the 'not encoded' list is complete; try to break each fidelity example."),
            context=e["encodes"],
            acceptance=[independence, "On acceptance, set fidelity to independently_reviewed in data/formalization.json "
                        "in the same PR", REGEN],
            boundary="Fidelity review certifies the encoding, never the conjecture.",
            falsifier="A hand-checked instance on which the comparator and the registry statement disagree.",
            source="data/formalization.json")
    for r in _json("data/statement_scope_reviews.json")["reviews"]:
        wid = f"V-S-{r['id']}"
        if r["id"] not in problems_by_id:
            continue
        add(id=wid, kind="review", status="runnable", problems=[r["id"]],
            title=f"Independent review of the status draft for {problems_by_id[r['id']]['name']}",
            deliverable=("Check the draft scope and open questions in data/statement_scope_reviews.json against dated "
                         "specialist sources; record agreement, corrections or the source that settles the status."),
            context=r.get("draft_scope", ""),
            acceptance=[independence, "Evidence state changes only through docs/PORTFOLIO_SELECTION.md", REGEN],
            boundary="Reviewing a draft is not an open-status certification by itself.",
            falsifier="A dated source showing the drafted statement is already resolved or misstated.",
            source="data/statement_scope_reviews.json")

    # 1b(ii). Independent audit of the existing runnable verifier for each
    # campaign. Replaying its checker is not a new theorem, but a distinct
    # reviewable artifact from Lean fidelity or status-source audits.
    verified = set()
    for campaign in program["campaigns"]:
        cmd = campaign.get("verifier")
        pid = campaign["problem_id"]
        if not cmd or pid in verified:
            continue
        verified.add(pid)
        add(id=f"V-P-{pid}", kind="review", status="runnable", problems=[pid],
            title=f"Independent certificate and scope audit for {pid}",
            deliverable=(f"Reproduce the campaign verifier ({cmd}); inspect the independent "
                         "checker, deliberately corrupt its input/certificate, and compare "
                         "every computational claim against the registered finite scope "
                         "and its cited published boundary."),
            context=(f"Command: {cmd}; project: {by_id[pid]['question']}. "
                     f"Evidence: data/research_program.json, LAB.md and verifier source."),
            acceptance=[independence,
                        "Publish exact command, pinned input SHA and output, negative "
                        "control, numerical range and scope-vs-source assessment; "
                        "record any discrepancy as a gap, never as a solved result",
                        REGEN, TESTS],
            boundary=("Reproduction and fidelity only. Even an independently accepted "
                      "finite checker is not a new restricted result, a universal proof, "
                      "or a claim to have established untested ranges."),
            falsifier="A tampered certificate passes, checker and search share an "
                      "unjustified assumption, or a claimed scope exceeds the exact run.",
            source="data/research_program.json")

    # 1c. Frozen matched-budget experiment cells. A cell disappears only
    # after its exact task/arm/seed has a validated real run record.
    manifest = benchmark.load_manifest()
    recorded = benchmark.load_runs()
    benchmark.validate_runs(manifest, recorded)
    done = {(r["task_id"], r["arm"], r["seed"]) for r in recorded}
    stamp = benchmark.digest(manifest)
    for task in manifest["tasks"]:
        for arm in manifest["arms"]:
            for seed in manifest["seeds"]:
                if (task["id"], arm, seed) in done:
                    continue
                contaminated = benchmark.NOVELTY_CONTAMINATED.get(task["id"])
                boundary = ("Experimental work, not a theorem or speedup. No reuse between "
                            "arms or seeds; record source snapshot, prompts, tool/model versions, "
                            "checker, token accounting, all failed attempts. "
                            + (f"POST-FREEZE PRIOR ART: {contaminated}. No novelty credit or clean "
                               "holdout comparison for this task." if contaminated else
                               "Known prior art and the frozen source baseline must be disclosed."))
                add(id=f"B-{task['id']}-{arm}-{seed}", kind="benchmark", status="runnable",
                    problems=[task["problem_id"]],
                    title=f"Preregistered {task['id']} / {arm} / seed {seed}",
                    deliverable=(f"Run the {arm} agent architecture on {task['id']} with seed {seed}, "
                                 f"under the frozen scope: {task['scope']}"),
                    context=(f"Protocol SHA-256 {stamp}; source commit {manifest['source_commit']}. "
                             f"Acceptance: {task['acceptance']}"),
                    acceptance=[
                        "Claim exact task/arm/seed. Capture model version, prompts, source snapshot, "
                        "raw agent/tool transcript and measured aggregate usage across all workers, "
                        "checker and coordinator",
                        f"Caps: {manifest['resource_caps']['model_tokens']} model tokens, "
                        f"{manifest['resource_caps']['tool_calls']} tool calls, "
                        f"{manifest['resource_caps']['elapsed_seconds']} wall seconds",
                        "Append exactly one observed record to data/benchmark_runs.jsonl; "
                        "include failures/timeouts, not fixtures or estimated costs",
                        "A result needs artifact, independent checker log, scope/prior-art audit; "
                        "a no-result trial must have null evidence",
                        "python3 scripts/benchmark.py --check", REGEN],
                    boundary=boundary, falsifier="Contaminated source, missing logs, failed "
                    "independent replay or scope mismatch.",
                    source="data/benchmark_prereg.json")

    # 2. Lean targets: the next formal deliverable of each target.
    for t in _json("data/lean_targets.json"):
        add(id=t["id"], kind="lean", status="runnable", problems=[t["problem_id"]],
            title=("Implement" if t["stage"] == "planned" else "Extend") + f" Lean target {t['id']} ({t['problem_id']})",
            deliverable=t["next_step"], context=t["statement"],
            acceptance=["New theorems registered in data/lean_targets.json (stable names, no escape hatches)",
                        "python3 scripts/lean_verify.py passes in CI: warnings as errors, only propext / "
                        "Classical.choice / Quot.sound, per-module time well under the 300 s build budget",
                        "A negative case in lean/Negative.lean that a weakened statement would fail", REGEN],
            boundary=t["scope_gap"], falsifier="", source="data/lean_targets.json")

    # 3. Cohort jobs from the dispatcher. Dominated range extensions stay visible
    # but are externally blocked so agents do not claim them as constructive work.
    for job in approach.snapshot(items, program)["jobs"]:
        status = "externally_blocked" if job["action"] == "stop_range" else "runnable"
        boundary = (
            "Refused range extension: the campaign blocker already places this range inside known mathematics. "
            "Do not claim this job; follow the replacement step that starts with 'Do not'."
            if job["action"] == "stop_range"
            else "A cohort job is a scheduling unit, not a claim that the shape works for every listed problem."
        )
        add(id=f"J-{job['method_id']}-{job['action']}", kind="job", status=status,
            problems=list(job["problem_ids"]), title=f"{job['action_label']}: {job['method_title']}",
            deliverable=job["summary"], context=job.get("why") or "",
            acceptance=["Every problem on the job moves by the same action, or a precise gap is recorded per problem",
                        "Evidence lands in the ledger the action names (lab, claim review, campaign or obligation)", REGEN, TESTS],
            boundary=boundary,
            falsifier="", source="scripts/approach.py")

    # 4. Roadmap items that are current or next.
    for it in _json("data/roadmap.json")["items"]:
        if it["horizon"] not in ("now", "next"):
            continue
        add(id=it["id"], kind="roadmap", status="runnable", problems=list(it.get("problems") or []),
            title=it["title"], deliverable=it["outcome"], context="",
            acceptance=[f"Exit criterion met: {it.get('exit') or 'see data/roadmap.json'}",
                        "data/roadmap.json horizon moved to shipped with the evidence path", REGEN],
            boundary="Shipped roadmap work is infrastructure, reproduction or audit unless independently reviewed.",
            falsifier="", source="data/roadmap.json")

    # 5. Comparator statements for problems with none.
    formal = {e["problem_id"] for e in _json("data/formalization.json")["entries"]}
    for p in items:
        if p["id"] in formal:
            continue
        add(id=f"F-{p['id']}", kind="comparator", status="runnable", problems=[p["id"]],
            title=f"Lean comparator statement for {p['name']}",
            deliverable=(f"Encode the registry statement of {p['id']} as a Prop in "
                         f"lean/Hundred/Statements/ (header: what is encoded, what is not, frontier), "
                         f"with kernel-checked fidelity examples."),
            context=p["question"],
            acceptance=[f"Entry for {p['id']} in data/formalization.json; module imported by lean/Hundred.lean",
                        "python3 scripts/formal.py --check (no escape hatches; every kernel-checked theorem "
                        "registered in data/lean_targets.json)",
                        "Lean proof gate green in CI; each kernel certificate small (a few seconds, not minutes)", REGEN],
            boundary=("A comparator is a precise target, never a proof. Statements needing analysis or "
                      "topology may require Mathlib; record that as a blocker instead of encoding a weaker statement."),
            falsifier="A hand-checked instance on which the encoding disagrees with the registry statement.",
            source="data/formalization.json")

    # 6. Exact-status audit drafts.
    drafts = {r["id"] for r in _json("data/statement_scope_reviews.json")["reviews"]}
    for p in items:
        if p["evidence_state"] in ("official_open", "verified_open") or p["id"] in drafts:
            continue
        add(id=f"S-{p['id']}", kind="status_audit", status="runnable", problems=[p["id"]],
            title=f"Exact-status audit draft for {p['name']}",
            deliverable=(f"Draft the precise statement of {p['id']} and its current status from dated primary "
                         "specialist sources (survey, problem list or recent paper), in "
                         "data/statement_scope_reviews.json."),
            context=p["question"],
            acceptance=["Draft entry with current ambiguity, draft scope and open questions; every source dated",
                        "Evidence state unchanged unless a separate reviewed PR follows docs/PORTFOLIO_SELECTION.md", REGEN, TESTS],
            boundary="A draft is not an independent open-status confirmation and cannot move a problem to verified_open by itself.",
            falsifier="A dated source showing the exact registered statement is already resolved.",
            source="data/statement_scope_reviews.json")

    for item in work:
        item["scope_sha256"] = digest(item)
        item.update(claim_links(item))
        unknown = [p for p in item["problems"] if p not in by_id]
        if unknown:
            raise ValueError(f"{item['id']}: unknown problems {unknown}")
    # Only a review accepted for the *current* scope can leave the queue.
    # Changed statement contexts and acceptance requirements re-open the review.
    work = [item for item in work if item["kind"] != "review"
            or item["scope_sha256"][:16] not in accepted.get(item["id"], set())]
    order = {k: i for i, k in enumerate(FAMILIES)}
    work.sort(key=lambda x: (STATUS_ORDER[x["status"]], order[x["kind"]], x["priority_rank"], x["id"]))
    return work


def validate(work):
    ids = [w["id"] for w in work]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate work ids")
    known = set(ids)
    for w in work:
        if w["kind"] not in FAMILIES or w["status"] not in STATUS_ORDER:
            raise ValueError(f"{w['id']}: bad kind or status")
        for key in ("title", "deliverable", "boundary"):
            if not w[key].strip():
                raise ValueError(f"{w['id']}: empty {key}")
        if not w["acceptance"]:
            raise ValueError(f"{w['id']}: no acceptance criteria")
        for dep in w["depends_on"]:
            if dep not in known and not dep.startswith("O-"):
                raise ValueError(f"{w['id']}: unknown dependency {dep}")
    return work


def snapshot():
    work = validate(build())
    counts = {k: sum(w["kind"] == k for w in work) for k in FAMILIES}
    status = {k: sum(w["status"] == k for w in work) for k in STATUS_ORDER}
    return {"protocol": "svyable.work.v1", "count": len(work), "by_kind": counts, "by_status": status,
            "claim_protocol": "Search open issues for the claim title; if none is open, open one with "
                              ".github/ISSUE_TEMPLATE/claim.yml before starting. Close it with the PR.",
            "items": work}


def show(w):
    print(f"{w['id']}  [{w['kind']} · {w['status']} · dispatch #{w['priority_rank']}]  {w['title']}")
    print(f"  problems:    {', '.join(w['problems']) or '—'}")
    print(f"  deliverable: {w['deliverable']}")
    for a in w["acceptance"]:
        print(f"  accept:      {a}")
    print(f"  boundary:    {w['boundary']}")
    if w["depends_on"]:
        print(f"  depends on:  {', '.join(w['depends_on'])}")
    print(f"  claim:       {w['claim_title']}")
    print(f"  digest:      {w['scope_sha256'][:16]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--next", type=int, metavar="N", help="show the N highest-priority runnable items")
    parser.add_argument("--kind", choices=FAMILIES)
    parser.add_argument("--id")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true")
    opts = parser.parse_args()
    doc = snapshot()
    work = [w for w in doc["items"] if not opts.kind or w["kind"] == opts.kind]
    if opts.check:
        print(f"OK: {doc['count']} work items ({', '.join(f'{v} {k}' for k, v in doc['by_kind'].items())}); "
              f"{doc['by_status']['runnable']} runnable")
    elif opts.json:
        json.dump({**doc, "items": work}, sys.stdout, indent=2, ensure_ascii=False)
        print()
    elif opts.id:
        match = [w for w in doc["items"] if w["id"] == opts.id]
        if not match:
            raise SystemExit(f"No work item {opts.id}")
        show(match[0])
    else:
        runnable = [w for w in work if w["status"] == "runnable"]
        for w in runnable[: opts.next or 10]:
            show(w)
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
