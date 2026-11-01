#!/usr/bin/env python3
"""The outcomes ledger: what claimed work actually produced, and what it cost.

    python3 scripts/outcomes.py            # rewrite YIELD.md
    python3 scripts/outcomes.py --check    # validate the ledger; fail if YIELD.md is stale
    python3 scripts/outcomes.py --json     # metrics, machine-readable

Filled slots measure capacity. This ledger measures yield: **independently accepted
work items** per 10 recorded agent-hours. Each record describes one claimed work item
(see scripts/work.py) after the claim closes. Only ``accepted_independent`` counts, and
it requires a named reviewer who is not the author, a public review link and an
``accepted_on`` date.

An accepted work item is not a new theorem. A comparator, status audit or reproduction
can be accepted. A record counts as a *new restricted mathematical result* only with a
separately audited ``novelty`` classification (``new_restricted_result``, with its own
named novelty reviewer and link), which is reported as a separate number.

Independence is checked structurally (reviewer differs from author, public link); the
validator does not authenticate identity or expertise. Nothing here changes an evidence
state; the proof, novelty and Solved gates of docs/RESEARCH_PROTOCOL.md stay separate.
"""
import argparse
import json
import math
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "outcomes.json"
REPORT = ROOT / "YIELD.md"

OUTCOMES = {
    "accepted_independent": "Delivered and accepted by a named reviewer who is not the author.",
    "merged_pending_review": "Artifact merged; independent review not yet recorded.",
    "gap_reported": "A precise gap, obstruction or negative result was recorded instead of the deliverable.",
    "falsified": "The deliverable's claim was refuted, or its falsifier was found.",
    "abandoned": "Claim closed without a usable artifact.",
}
NOVELTY = {
    "not_assessed": "No novelty or scope audit recorded (the default).",
    "known_or_reproduction": "Audited as known mathematics, a reproduction or infrastructure.",
    "new_restricted_result": "Audited by a named novelty reviewer as a new restricted result.",
}
STRUCTURAL_NOTE = ("Independence is structural: the validator checks that the named reviewer is not the author "
                   "and that a public review link exists. It does not authenticate identity or expertise, and the "
                   "proof, novelty and Solved gates remain separate.")
FAMILY_PREFIX = (("X-", "infrastructure"), ("V-", "review"), ("O-", "obligation"), ("F-", "comparator"), ("S-", "status_audit"),
                 ("J-", "job"), ("L", "lean"), ("R", "roadmap"))
WORK_ID = re.compile(r"^(X-[A-Z0-9-]+|V-[A-Z0-9-]+|O-M\d{3}-\d{2}|F-M\d{3}|S-M\d{3}|J-[a-z0-9_]+-[a-z_]+|L\d{3}|R\d{2,3})$")
HEX = re.compile(r"^[0-9a-f]{16,64}$")


class OutcomeError(ValueError):
    pass


def family(work_id):
    for prefix, name in FAMILY_PREFIX:
        if work_id.startswith(prefix):
            return name
    return "other"


def _date(value, where):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise OutcomeError(f"{where}: invalid ISO date {value!r}") from None


def _amount(value):
    """A finite, nonnegative int or float. bool is rejected (it is an int subclass)."""
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def validate(doc):
    if doc.get("version") != 1 or doc.get("resource_unit") != "agent_hour":
        raise OutcomeError("outcomes ledger must be version 1 with resource_unit agent_hour")
    seen = set()
    for i, rec in enumerate(doc.get("outcomes", [])):
        where = f"outcome {i} ({rec.get('work_id')})"
        if not WORK_ID.match(str(rec.get("work_id", ""))):
            raise OutcomeError(f"{where}: work_id does not match a work-queue id pattern")
        if not HEX.match(str(rec.get("scope_sha256", ""))):
            raise OutcomeError(f"{where}: scope_sha256 must be 16-64 lowercase hex characters")
        key = (rec["work_id"], rec["scope_sha256"][:16])
        if key in seen:
            raise OutcomeError(f"{where}: duplicate record for the same claimed scope")
        seen.add(key)
        if rec.get("outcome") not in OUTCOMES:
            raise OutcomeError(f"{where}: outcome must be one of {sorted(OUTCOMES)}")
        if not str(rec.get("author", "")).strip():
            raise OutcomeError(f"{where}: author required")
        for key_url in ("claim_url", "pr_url", "review_url"):
            url = rec.get(key_url)
            if url is not None and not str(url).startswith("https://"):
                raise OutcomeError(f"{where}: {key_url} must be an https URL")
        claimed = _date(rec.get("claimed_on"), where)
        closed = _date(rec.get("closed_on"), where)
        if closed < claimed:
            raise OutcomeError(f"{where}: closed before claimed")
        res = rec.get("resources")
        if not isinstance(res, dict):
            raise OutcomeError(f"{where}: resources must be an object")
        if not _amount(res.get("agent_hours")):
            raise OutcomeError(f"{where}: resources.agent_hours must be a finite nonnegative int or float")
        if not _amount(res.get("ci_minutes", 0)):
            raise OutcomeError(f"{where}: resources.ci_minutes must be a finite nonnegative int or float")
        if rec["outcome"] == "accepted_independent":
            reviewer = str(rec.get("reviewer", "")).strip()
            if not reviewer:
                raise OutcomeError(f"{where}: accepted_independent requires a named reviewer")
            if reviewer.casefold() == str(rec["author"]).strip().casefold():
                raise OutcomeError(f"{where}: the reviewer must not be the author")
            if not rec.get("review_url"):
                raise OutcomeError(f"{where}: accepted_independent requires a public review_url")
            if _date(rec.get("accepted_on"), where) < claimed:
                raise OutcomeError(f"{where}: accepted before claimed")
        else:
            for key_only in ("reviewer", "accepted_on"):
                if rec.get(key_only):
                    raise OutcomeError(f"{where}: {key_only} is only recorded for accepted_independent outcomes")
        novelty = rec.get("novelty", "not_assessed")
        if novelty not in NOVELTY:
            raise OutcomeError(f"{where}: novelty must be one of {sorted(NOVELTY)}")
        if novelty == "new_restricted_result":
            if rec["outcome"] != "accepted_independent":
                raise OutcomeError(f"{where}: a new restricted result must first be an accepted work item")
            nreviewer = str(rec.get("novelty_reviewer", "")).strip()
            if not nreviewer or nreviewer.casefold() == str(rec["author"]).strip().casefold():
                raise OutcomeError(f"{where}: novelty needs a named novelty_reviewer who is not the author")
            if not str(rec.get("novelty_review_url", "")).startswith("https://"):
                raise OutcomeError(f"{where}: novelty needs a public https novelty_review_url")
        elif rec.get("novelty_reviewer") or rec.get("novelty_review_url"):
            raise OutcomeError(f"{where}: novelty reviewer fields only accompany new_restricted_result")
    return doc


def load(path=LEDGER):
    return validate(json.loads(Path(path).read_text(encoding="utf-8")))


def accepted_ids(doc=None):
    """Work ids with an independent acceptance on record (used by the work queue)."""
    doc = load() if doc is None else doc
    return {r["work_id"] for r in doc["outcomes"] if r["outcome"] == "accepted_independent"}


def metrics(doc=None, review_backlog=None):
    doc = load() if doc is None else doc
    recs = doc["outcomes"]
    hours = sum(r["resources"]["agent_hours"] for r in recs)
    ci = sum(r["resources"].get("ci_minutes", 0) for r in recs)
    accepted = [r for r in recs if r["outcome"] == "accepted_independent"]
    by_family = {}
    for fam in sorted({family(r["work_id"]) for r in recs}):
        fr = [r for r in recs if family(r["work_id"]) == fam]
        fh = sum(r["resources"]["agent_hours"] for r in fr)
        fa = sum(r["outcome"] == "accepted_independent" for r in fr)
        by_family[fam] = {"records": len(fr), "accepted_work_items": fa, "agent_hours": round(fh, 2),
                          "accepted_work_items_per_10_agent_hours": round(10 * fa / fh, 3) if fh else None}
    days = sorted((date.fromisoformat(r["accepted_on"]) - date.fromisoformat(r["claimed_on"])).days for r in accepted)
    close_days = sorted((date.fromisoformat(r["closed_on"]) - date.fromisoformat(r["claimed_on"])).days for r in recs)
    novel = [r for r in accepted if r.get("novelty") == "new_restricted_result"]
    if review_backlog is None:
        import work  # local: work imports this module
        review_backlog = sum(w["kind"] == "review" for w in work.snapshot()["items"])
    return {
        "definition": "Yield = independently accepted work items per 10 recorded agent-hours. An accepted work "
                      "item is not a new theorem; new restricted results with an audited novelty classification "
                      "are counted separately. Capacity (filled slots) is reported by scripts/scale.py.",
        "independence_note": STRUCTURAL_NOTE,
        "records": len(recs),
        "by_outcome": {k: sum(r["outcome"] == k for r in recs) for k in OUTCOMES},
        "accepted_work_items": len(accepted),
        "new_restricted_results_audited": len(novel),
        "agent_hours": round(hours, 2),
        "ci_minutes": round(ci, 1),
        "accepted_work_items_per_10_agent_hours": round(10 * len(accepted) / hours, 3) if hours else None,
        "median_days_claim_to_acceptance": days[len(days) // 2] if days else None,
        "median_days_claim_to_close": close_days[len(close_days) // 2] if close_days else None,
        "pending_review_share": round(sum(r["outcome"] == "merged_pending_review" for r in recs) / len(recs), 3) if recs else None,
        "review_backlog_items": review_backlog,
        "by_family": by_family,
        "distinct_reviewers": len({r["reviewer"] for r in accepted}),
        "authors": dict(Counter(r["author"] for r in recs)),
    }


def render(m=None):
    m = metrics() if m is None else m
    fmt = lambda v: "—" if v is None else str(v)
    lines = [
        "# Yield — independently accepted work items per unit of resource",
        "",
        "Generated by `python3 scripts/outcomes.py` from [data/outcomes.json](data/outcomes.json). "
        "Do not edit by hand.",
        "",
        "Capacity is how many claimable slots exist ([SCALE.md](SCALE.md)). **Yield** is how many claimed "
        "work items a named reviewer, who is not the author, accepted, per 10 recorded agent-hours. A merged "
        "artifact without independent review is *pending*.",
        "",
        "**An accepted work item is not a new theorem.** Comparators, status audits and reproductions can be "
        "accepted. A record counts as a *new restricted mathematical result* only with a separately audited "
        "`novelty: new_restricted_result` classification (its own named novelty reviewer and public link); that "
        "number is reported on its own line and is the only one comparable to the numerator of the preregistered "
        "benchmark ([benchmarks/PROTOCOL.md](benchmarks/PROTOCOL.md)).",
        "",
        f"> {STRUCTURAL_NOTE}",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Outcome records | {m['records']} |",
        f"| Independently accepted work items | {m['accepted_work_items']} |",
        f"| New restricted results with audited novelty | {m['new_restricted_results_audited']} |",
        f"| Recorded agent-hours | {m['agent_hours']} |",
        f"| **Yield** (independently accepted work items per 10 recorded agent-hours) | {fmt(m['accepted_work_items_per_10_agent_hours'])} |",
        f"| Median days, claim to independent acceptance (`accepted_on`) | {fmt(m['median_days_claim_to_acceptance'])} |",
        f"| Median days, claim to close (`closed_on`) | {fmt(m['median_days_claim_to_close'])} |",
        f"| Share of records merged but pending review | {fmt(m['pending_review_share'])} |",
        f"| Distinct independent reviewers | {m['distinct_reviewers']} |",
        f"| **Review backlog** (`review` items in the work queue) | {m['review_backlog_items']} |",
        "",
        "## Outcomes",
        "",
        "| Outcome | Count | Meaning |",
        "|---|---:|---|",
    ]
    lines += [f"| `{k}` | {m['by_outcome'][k]} | {v} |" for k, v in OUTCOMES.items()]
    lines += ["", "## Novelty classification", "", "| `novelty` | Meaning |", "|---|---|"]
    lines += [f"| `{k}` | {v} |" for k, v in NOVELTY.items()]
    lines += ["", "## By work family", ""]
    if m["by_family"]:
        lines += ["| Family | Records | Accepted work items | Agent-hours | Accepted per 10 h |", "|---|---:|---:|---:|---:|"]
        lines += [f"| {k} | {v['records']} | {v['accepted_work_items']} | {v['agent_hours']} | {fmt(v['accepted_work_items_per_10_agent_hours'])} |"
                  for k, v in m["by_family"].items()]
    else:
        lines.append("No outcomes recorded yet. The baseline is zero accepted results; the first records "
                     "establish the denominator.")
    lines += [
        "",
        "## Recording an outcome",
        "",
        "When a claim closes, append one record to `data/outcomes.json` in the PR that closes it:",
        "",
        "```json",
        '{"work_id": "F-M079", "scope_sha256": "<first 16+ hex of the claimed digest>",',
        ' "author": "<who did the work>", "outcome": "merged_pending_review",',
        ' "claim_url": "https://github.com/Svyable/100/issues/<n>", "pr_url": "https://github.com/Svyable/100/pull/<n>",',
        ' "claimed_on": "2026-11-01", "closed_on": "2026-11-02",',
        ' "resources": {"agent_hours": 1.5, "ci_minutes": 6}}',
        "```",
        "",
        "Only a reviewer who is not the author may later change it to `accepted_independent`, adding "
        "`reviewer`, a public `review_url` and `accepted_on`. A separate novelty audit may then add "
        "`novelty`, `novelty_reviewer` and `novelty_review_url`. Report agent-hours honestly, as finite "
        "numbers, including failed attempts; a `gap_reported` or `falsified` record is useful evidence and "
        "keeps the denominator truthful.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    opts = parser.parse_args()
    try:
        m = metrics()
    except OutcomeError as exc:
        print(f"OUTCOMES LEDGER ERROR: {exc}", file=sys.stderr)
        return 1
    text = render(m)
    if opts.json:
        json.dump(m, sys.stdout, indent=2)
        print()
    elif opts.check:
        if not REPORT.is_file() or REPORT.read_text(encoding="utf-8") != text:
            print("Stale YIELD.md: run python3 scripts/outcomes.py", file=sys.stderr)
            return 1
        print(f"OK: {m['records']} outcome records, {m['accepted_work_items']} independently accepted work items, "
              f"review backlog {m['review_backlog_items']}")
    else:
        REPORT.write_text(text, encoding="utf-8")
        print(f"Updated YIELD.md ({m['records']} records, review backlog {m['review_backlog_items']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
