#!/usr/bin/env python3
"""Validate and build the speculative Next 100 discovery reservoir.

This is NOT the authoritative open-problem registry. Candidate statements are
unvetted proposals; discovery ranks are editorial priorities, not evidence.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "next_candidates.json"
BATCH_DIR = ROOT / "data" / "next_batches"
PROMOTIONS = ROOT / "data" / "next_promotions.json"
ACTIVE = ROOT / "data" / "problems.json"
OUTPUT = ROOT / "docs" / "data" / "next.json"
AS_OF = "2026-10-31"
FIELDS = ("impact", "tractability", "verifiability", "transfer")
STAGES = {"formalize", "prior_art_review"}
DOMAIN_MINIMUM = 2


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def candidates():
    paths = [SEED] + sorted(BATCH_DIR.glob("*.json"))
    entries = []
    for path in paths:
        batch = read(path)
        if not isinstance(batch, list):
            raise ValueError(f"{path}: candidates must be a list")
        entries.extend(batch)
    return entries


def validate(entries, promotions, active):
    if not isinstance(entries, list) or not isinstance(promotions, list):
        raise ValueError("Candidates and promotions must be arrays")
    if len(active) != 100 or len({p["id"] for p in active}) != 100:
        raise ValueError("Active portfolio must retain exactly 100 distinct IDs")
    active_names = {p["name"].casefold().strip() for p in active}
    active_ids = {p["id"] for p in active}
    seen_ids, seen_titles = set(), set()
    for p in entries:
        if not isinstance(p, dict):
            raise ValueError("Every candidate must be an object")
        required = {"id", "title", "statement", "domain", "spillovers",
                    "consequence", "first_attack", "stage", "evidence_state", "scores"}
        if set(p) != required:
            raise ValueError(f"{p.get('id', '?')}: incorrect field set")
        uid = p["id"]
        if not isinstance(uid, str) or not re.fullmatch(r"N[0-9]{4,}", uid):
            raise ValueError(f"Invalid stable ID: {uid}")
        if uid in seen_ids:
            raise ValueError(f"Duplicate candidate ID: {uid}")
        seen_ids.add(uid)
        for name in ("title", "statement", "domain", "consequence", "first_attack"):
            if not isinstance(p[name], str) or len(p[name].strip()) < 12:
                raise ValueError(f"{uid}: {name} missing or too brief")
        title = p["title"].casefold().strip()
        if title in seen_titles or title in active_names:
            raise ValueError(f"{uid}: duplicated title or already in the active 100")
        seen_titles.add(title)
        if (not isinstance(p["spillovers"], list)
                or len(set(p["spillovers"])) < DOMAIN_MINIMUM
                or not all(isinstance(s, str) and len(s.strip()) >= 4 for s in p["spillovers"])):
            raise ValueError(f"{uid}: needs two distinct real-world/mathematical spillovers")
        if p["stage"] not in STAGES or p["evidence_state"] != "unvetted_hypothesis":
            raise ValueError(f"{uid}: hypotheses must not be presented as verified facts")
        scores = p["scores"]
        if (not isinstance(scores, dict) or set(scores) != set(FIELDS)
                or any(type(scores[k]) is not int or not 1 <= scores[k] <= 5
                       for k in FIELDS)):
            raise ValueError(f"{uid}: scores must be four editorial integers 1-5")
    promoted_ids, slots = set(), set()
    for link in promotions:
        if not isinstance(link, dict) or set(link) != {
            "next_id", "active_id", "promoted_on", "review_url", "reason"
        }:
            raise ValueError("Promotion requires next_id, active_id, promoted_on, review_url, reason")
        if (link["next_id"] not in seen_ids or link["next_id"] in promoted_ids
                or link["active_id"] not in active_ids or link["active_id"] in slots):
            raise ValueError("Promotion references invalid or repeated candidate/active slot")
        if not re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}", link["promoted_on"]):
            raise ValueError("Promotion requires ISO date")
        if (not isinstance(link["review_url"], str)
                or not link["review_url"].startswith("https://github.com/Svyable/100/pull/")):
            raise ValueError("Promotion requires an auditable GitHub PR")
        if not isinstance(link["reason"], str) or len(link["reason"].strip()) < 20:
            raise ValueError("Promotion requires substantive reasoning")
        promoted_ids.add(link["next_id"])
        slots.add(link["active_id"])
    return True


def editorial_score(candidate):
    s = candidate["scores"]
    return 6 * s["impact"] + 6 * s["tractability"] + 5 * s["verifiability"] + 3 * s["transfer"]


def build():
    entries, promotions, active = candidates(), read(PROMOTIONS), read(ACTIVE)
    validate(entries, promotions, active)
    promoted = {x["next_id"]: x["active_id"] for x in promotions}
    ordered = sorted(entries, key=lambda p: (-editorial_score(p), p["id"]))
    return {
        "title": "Next 100 — hypothesis reservoir",
        "source": "data/next_candidates.json + data/next_batches/*.json",
        "seeded_as_of": AS_OF,
        "count": len(entries),
        "available_count": len(entries) - len(promotions),
        "promoted_count": len(promotions),
        "score_description": "Editorial discovery priority, not a probability of truth or proof",
        "scoring": {"impact": 30, "tractability": 30, "verifiability": 25, "transfer": 15},
        "stages": {stage: sum(p["stage"] == stage for p in entries)
                   for stage in ("formalize", "prior_art_review")},
        "domains": sorted({p["domain"] for p in entries}),
        "promotions": promotions,
        "candidates": [
            {**p, "score": editorial_score(p), "discovery_rank": number,
             "promoted_to": promoted.get(p["id"])}
            for number, p in enumerate(ordered, 1)
        ],
    }


def render():
    return json.dumps(build(), indent=2, ensure_ascii=False) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail on stale Pages data")
    parser.add_argument("--top", type=int, default=0, help="show N leading hypotheses")
    opts = parser.parse_args()
    result = build()
    expected = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if opts.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit("Stale Next 100 snapshot: run python3 scripts/next.py")
        print(f"OK: {result['count']} hypotheses, {len(result['domains'])} domains; active 100 intact")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(expected, encoding="utf-8")
        print(f"Updated {OUTPUT.relative_to(ROOT)} ({result['count']} hypotheses)")
    if opts.top > 0:
        for p in result["candidates"][:opts.top]:
            print(f"{p['discovery_rank']:>4} {p['id']} {p['score']:>3} {p['title']}")


if __name__ == "__main__":
    main()
