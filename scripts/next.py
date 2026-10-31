#!/usr/bin/env python3
"""Validate and build the speculative Next 100 discovery reservoir.

This is NOT the authoritative open-problem registry. Candidate statements are
unvetted proposals; discovery ranks are editorial priorities, not evidence.
"""
import argparse
import json
import re
from urllib.parse import urlsplit
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "next_candidates.json"
BATCH_DIR = ROOT / "data" / "next_batches"
PROMOTIONS = ROOT / "data" / "next_promotions.json"
REVIEW_QUEUE = ROOT / "data" / "next_review_queue.json"
ACTIVE = ROOT / "data" / "problems.json"
OUTPUT = ROOT / "docs" / "data" / "next.json"
AS_OF = "2026-10-31"
FIELDS = ("impact", "tractability", "verifiability", "transfer")
STAGES = {"formalize", "prior_art_review"}
DOMAIN_MINIMUM = 2
SIMILARITY_STOPWORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "into", "is",
    "of", "on", "or", "the", "to", "under", "using", "with", "without",
    "across", "within", "bounded", "class", "classes", "selected",
    "specified", "certain", "nontrivial", "explicit", "provable",
    "guarantee", "guarantees", "model", "models", "family", "families"
}


def terms(text):
    return {word for word in re.findall(r"[a-z0-9]+", text.casefold())
            if len(word) > 2 and word not in SIMILARITY_STOPWORDS}


def similarity(a, b):
    return 2 * len(a & b) / (len(a) + len(b)) if a or b else 0.0


def similarity_pairs(entries, minimum=0.48):
    """Lexical triage only, not mathematical equivalence or a literature audit."""
    features = [(p["id"], terms(p["title"]), terms(p["statement"]))
                for p in entries]
    matches = []
    for i, (aid, at, ast) in enumerate(features):
        for bid, bt, bst in features[i + 1:]:
            title, statement = similarity(at, bt), similarity(ast, bst)
            strength = max(title * 0.65 + statement * 0.35,
                           statement, title * 0.88)
            if strength >= minimum:
                matches.append((strength, aid, bid, title, statement))
    return sorted(matches, key=lambda row: (-row[0], row[1], row[2]))


def validate_review_queue(queue, entries):
    if not isinstance(queue, list):
        raise ValueError("Review queue must be an array")
    ids = {p["id"] for p in entries}
    observed = set()
    expected_keys = {"priority", "candidate_id", "status", "review_question",
                     "smallest_test", "context_url", "review_gap"}
    for row in queue:
        if not isinstance(row, dict) or set(row) != expected_keys:
            raise ValueError("Review queue entry needs the seven required fields")
        uid = row["candidate_id"]
        if uid not in ids or uid in observed:
            raise ValueError(f"Unknown or repeated review candidate: {uid}")
        observed.add(uid)
        if row["status"] not in {"queued", "in_review"}:
            raise ValueError("Review queue cannot claim an unverified audit complete")
        for key in ("review_question", "smallest_test", "review_gap"):
            if not isinstance(row[key], str) or len(row[key].strip()) < 24:
                raise ValueError(f"{uid}: {key} must describe a substantive task")
        url = row["context_url"]
        if not isinstance(url, str) or urlsplit(url).scheme != "https" or not urlsplit(url).hostname:
            raise ValueError(f"{uid}: context_url must be absolute HTTPS")
    if [p["priority"] for p in queue] != list(range(1, len(queue) + 1)):
        raise ValueError("Review priorities must be contiguous in list order")
    return True



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
    close = [p for p in similarity_pairs(entries, minimum=0.0)
             if (p[3] >= 0.84 and p[4] >= 0.25)
             or (p[4] >= 0.83 and p[3] >= 0.25)
             or p[4] >= 0.92]
    if close:
        _, a, b, title_score, statement_score = close[0]
        raise ValueError(
            f"Near-duplicate candidate pair {a} / {b}: "
            f"title={title_score:.2f}, statement={statement_score:.2f}; "
            "resolve or explicitly differentiate before intake"
        )
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
    queue = read(REVIEW_QUEUE)
    validate_review_queue(queue, entries)
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
        "review_queue": queue,
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
    parser.add_argument("--similarity", type=int, default=0,
                        help="report N closest lexical pairs for manual screening")
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
    if opts.similarity > 0:
        for strength, first, second, title, statement in similarity_pairs(
                candidates(), minimum=0.0)[:opts.similarity]:
            print(f"{first} / {second}: combined={strength:.3f}, "
                  f"title={title:.3f}, statement={statement:.3f}")
    if opts.top > 0:
        for p in result["candidates"][:opts.top]:
            print(f"{p['discovery_rank']:>4} {p['id']} {p['score']:>3} {p['title']}")


if __name__ == "__main__":
    main()
