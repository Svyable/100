#!/usr/bin/env python3
"""Validate the structural finite-analogue ledger.

    python3 scripts/analogues.py           # summary
    python3 scripts/analogues.py --check   # fail on schema / registry drift
    python3 scripts/analogues.py --json

Analogues are restricted finite stand-ins for structural problems. They do not
change Solved, readiness, or lab coverage.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "structural_analogues.json"
FIELDS = {
    "problem_id", "analogue", "certificate", "proposed_engine", "status",
}
STATUSES = {
    "campaign_specified", "depends_on_M044", "class_locked", "aspirational",
}


def load(path=SOURCE):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate(doc=None):
    doc = load() if doc is None else doc
    if not isinstance(doc, dict) or "entries" not in doc or "interpretation" not in doc:
        raise ValueError("structural_analogues.json missing required top-level keys")
    problems = {
        p["id"]: p
        for p in json.loads((ROOT / "data" / "problems.json").read_text(encoding="utf-8"))
    }
    seen = set()
    for entry in doc["entries"]:
        if not isinstance(entry, dict) or set(entry) != FIELDS:
            raise ValueError(f"Bad analogue entry fields: {entry!r}")
        pid = entry["problem_id"]
        if pid not in problems or pid in seen:
            raise ValueError(f"Unknown or duplicate analogue problem: {pid}")
        seen.add(pid)
        if problems[pid].get("modality") != "structural":
            raise ValueError(f"{pid}: analogue ledger is for structural modality only")
        for key in ("analogue", "certificate", "proposed_engine"):
            if not isinstance(entry[key], str) or len(entry[key].strip()) < 8:
                raise ValueError(f"{pid}: {key} too short")
        if entry["status"] not in STATUSES:
            raise ValueError(f"{pid}: unknown status {entry['status']}")
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    doc = validate()
    if args.json:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        return 0
    print(
        f"OK: {len(doc['entries'])} structural analogues "
        f"({sum(e['status'] == 'aspirational' for e in doc['entries'])} aspirational)"
    )
    if args.check:
        return 0
    for entry in doc["entries"]:
        print(f"  {entry['problem_id']}: {entry['status']} → {entry['proposed_engine']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
