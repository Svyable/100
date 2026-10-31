#!/usr/bin/env python3
"""Deterministic score/rank generator; no external dependencies."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/problems.json"
RANKED = ROOT / "RANKED.md"
STATES = {"official_open", "needs_review", "claim_needs_review", "verified_open", "resolved", "retired"}
# How finite exact computation can bear on the statement (editorial, see docs/RESEARCH_PROTOCOL.md).
MODALITIES = {"finite_refutable", "finite_parameter", "existence_family", "asymptotic", "structural"}
COMPUTABLE = {"finite_refutable", "finite_parameter", "existence_family"}

def score(p):
    return 6*p["impact"] + 6*p["attackability"] + 5*p["verifiability"] + 3*p["spillover"]

def validate(items):
    if len(items) != 100 or len({p["id"] for p in items}) != 100:
        raise ValueError("Registry must have 100 unique candidates")
    for p in items:
        if not p["id"].startswith("M") or len(p["id"]) != 4:
            raise ValueError("Bad stable ID")
        if p["evidence_state"] not in STATES or p["evidence_state"] in {"resolved", "retired"}:
            raise ValueError("Nonactive or invalid evidence state: " + p["id"])
        for key in ("impact","attackability","verifiability","spillover"):
            if type(p[key]) is not int or not 1 <= p[key] <= 5:
                raise ValueError("Invalid score field: " + p["id"])
        if p.get("modality") not in MODALITIES:
            raise ValueError("Missing or unknown computational modality: " + p["id"])
        for key in ("name","field","question","first_attack"):
            if not isinstance(p[key],str) or not p[key].strip():
                raise ValueError("Missing text field: " + p["id"])
        if p["evidence_state"] in {"official_open","verified_open"} and not (p["source_url"] and p["checked_on"]):
            raise ValueError("Open status requires source and checked date: " + p["id"])
    return items

def render(items):
    lines = ["# Ranked candidate portfolio", "",
        "**Provisional rankings (2026-10-30).** Only `official_open` entries have been checked against an official authority here. Most candidates require an independent status audit. A proof claim is not an accepted solution.", "",
        "Score: impact 30% + attackability 30% + verifiability 25% + spillover 15%. Each factor is 1–5; score is out of 100. Scores are editorial, not proof probabilities. Stable ID breaks ties.", "",
        "| Rank | ID | Question | Field | Score | Evidence |",
        "|---:|---|---|---|---:|---|"]
    for i,p in enumerate(sorted(items,key=lambda p: (-score(p),p["id"])), 1):
        lines.append(f"| {i} | {p['id']} | {p['name']} | {p['field']} | {score(p)} | {p['evidence_state']} |")
    lines += ["", "For all top candidates: verify the full theorem and current status from primary literature, formulate a first lemma, try counterexample search, and independently check any proof. See [protocol](docs/RESEARCH_PROTOCOL.md).", ""]
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args = parser.parse_args()
    items = validate(json.loads(REGISTRY.read_text(encoding="utf-8")))
    content = render(items)
    if args.check:
        if not RANKED.exists() or RANKED.read_text(encoding="utf-8") != content:
            raise SystemExit("Stale ranking: run python3 scripts/rank.py")
        print("OK: 100 candidates, ranking reproducible")
    else:
        RANKED.write_text(content,encoding="utf-8")
        print("Updated RANKED.md")

if __name__ == "__main__":
    main()
