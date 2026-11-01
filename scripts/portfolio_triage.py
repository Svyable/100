#!/usr/bin/env python3
"""Check a conservative admission/retirement screening without inferring open status."""
import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/problems.json"
TRIAGE = ROOT / "data/portfolio_triage.json"
ACTIONS = {"scope": "respecify", "overlap": "consolidation_review",
           "portfolio_tradeoff": "compare_candidates", "resolution_claim": "audit_claim"}

def valid_day(value):
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False

def https(url):
    if not isinstance(url, str):
        return False
    parsed = urlparse(url)
    return parsed.scheme == "https" and bool(parsed.netloc)

def substantial(value, minimum=30):
    return isinstance(value, str) and len(value.strip()) >= minimum

def validate(triage, active):
    if not isinstance(triage, dict) or set(triage) != {
            "as_of", "purpose", "entries", "admission_candidates"}:
        raise ValueError("Triage schema missing or has unknown fields")
    if not valid_day(triage["as_of"]) or triage["purpose"] != "screening_only_not_status_verification":
        raise ValueError("Triage must be dated, explicitly nonauthoritative")
    if not isinstance(active, list) or len(active) != 100 or len({p["id"] for p in active}) != 100:
        raise ValueError("Expected 100 distinct active entries")
    entries, admissions = triage["entries"], triage["admission_candidates"]
    if not isinstance(entries, list) or not isinstance(admissions, list):
        raise ValueError("Entries and admissions must be arrays")
    active_ids = {p["id"] for p in active}
    active_names = {p["name"].casefold().strip() for p in active}
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {
                "id", "concern", "proposed_action", "rationale", "evidence_needed", "lead_urls"}:
            raise ValueError("Invalid screening entry fields")
        pid = entry["id"]
        if pid not in active_ids or pid in seen:
            raise ValueError("Unknown or duplicate screening ID")
        seen.add(pid)
        if entry["concern"] not in ACTIONS or entry["proposed_action"] != ACTIONS[entry["concern"]]:
            raise ValueError("Concern and action inconsistent")
        if not substantial(entry["rationale"]) or not substantial(entry["evidence_needed"]):
            raise ValueError("Rationale and evidence gate required")
        leads = entry["lead_urls"]
        if not isinstance(leads, list) or not all(https(u) for u in leads):
            raise ValueError("Lead sources must be HTTPS list")
        if entry["concern"] == "resolution_claim" and not leads:
            raise ValueError("Proof claim requires an actual source lead")
    keys, names = set(), set()
    for entry in admissions:
        if not isinstance(entry, dict) or set(entry) != {
                "key", "name", "proposed_statement", "rationale", "source_urls",
                "admission_state", "next_gate"}:
            raise ValueError("Invalid candidate fields")
        key = entry["key"]
        if not isinstance(key, str) or len(key) != 4 or key[0] != "A" or not key[1:].isdigit() or key in keys:
            raise ValueError("Invalid or repeated admission key")
        keys.add(key)
        name = entry["name"]
        if not substantial(name, 8):
            raise ValueError("Candidate name missing")
        normalized = name.strip().casefold()
        if normalized in names or normalized in active_names:
            raise ValueError("Duplicate candidate name or active question")
        names.add(normalized)
        if any(not substantial(entry[k]) for k in ("proposed_statement", "rationale", "next_gate")):
            raise ValueError("Admission requires precise statement, rationale and gate")
        if entry["admission_state"] != "unvetted_candidate":
            raise ValueError("A screening record must not assert verified or solved status")
        sources = entry["source_urls"]
        if not isinstance(sources, list) or not sources or not all(https(u) for u in sources):
            raise ValueError("Candidate needs HTTPS source leads")
    return Counter(entry["concern"] for entry in entries)


SCOPE = ROOT / "data" / "statement_scope_reviews.json"

def validate_scope(scope, triage):
    """Draft statements are context only, never an open-status upgrade."""
    if not isinstance(scope, dict) or set(scope) != {"as_of", "purpose", "reviews"}:
        raise ValueError("Scope-review schema invalid")
    if (not valid_day(scope["as_of"])
            or scope["purpose"] != "statement_scope_drafts_not_verified_open_status"):
        raise ValueError("Scope review must be a dated, explicitly provisional record")
    entries = {p["id"] for p in triage["entries"] if p["concern"] == "scope"}
    reviews = scope["reviews"]
    if not isinstance(reviews, list) or {p["id"] for p in reviews} != entries or len(reviews) != len(entries):
        raise ValueError("Every and only scope-flagged target must have one draft review")
    for r in reviews:
        if not isinstance(r, dict) or set(r) != {
                "id", "current_ambiguity", "draft_scope", "open_questions",
                "source_urls", "evidence_level", "promotion_barrier"}:
            raise ValueError("Scope-review entry schema invalid")
        if r["evidence_level"] != "background_only":
            raise ValueError("Scope draft cannot be marked verified, solved or current-status audited")
        for key in ("current_ambiguity", "draft_scope", "promotion_barrier"):
            if not substantial(r[key], 70):
                raise ValueError("Scope review lacks a substantive qualification")
        if (not isinstance(r["open_questions"], list) or len(r["open_questions"]) < 2
                or any(not substantial(q, 20) for q in r["open_questions"])):
            raise ValueError("Scope review needs open verification questions")
        if (not isinstance(r["source_urls"], list) or not r["source_urls"]
                or any(not https(url) for url in r["source_urls"])):
            raise ValueError("Scope review needs starting citations")
    return len(reviews)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    active = json.loads(REGISTRY.read_text(encoding="utf-8"))
    triage = json.loads(TRIAGE.read_text(encoding="utf-8"))
    counts = validate(triage, active)
    scope_count = validate_scope(json.loads(SCOPE.read_text(encoding="utf-8")), triage)
    print(f"OK: 100 active unchanged; {len(triage['entries'])} targeted flags; "
          f"{len(triage['admission_candidates'])} unvetted candidates; "
          f"{100-len(triage['entries'])} not screened in this pass")
    for concern in sorted(counts):
        print(f"{concern}: {counts[concern]}")
    print(f"{scope_count} provisional statement reviews linked; no current-status certification.")
    print("No resolution, independent open status or replacement certified.")

if __name__ == "__main__":
    main()
