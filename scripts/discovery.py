#!/usr/bin/env python3
"""Validate motivated discovery trails without changing mathematical evidence states."""
import argparse
import json
import re
from pathlib import Path

from rank import ROOT

PATH = ROOT / "data" / "discovery_trails.json"
KINDS = {"observation", "strategy", "reproduction", "blocker", "next_step"}
STATES = {"documented", "reproduced_known", "proposed", "blocked"}
ID = re.compile(r"[a-z][a-z0-9_-]*\Z")


def validate(doc, root=ROOT):
    """Fail closed on unsupported references, drift, and malformed dependency graphs."""
    if doc.get("version") != 1 or not re.fullmatch(r"20\d\d-\d\d-\d\d", doc.get("as_of", "")):
        raise ValueError("Discovery version/date invalid")
    if not doc.get("purpose"):
        raise ValueError("Missing disclaimer")
    problems = {x["id"] for x in json.loads((root / "data/problems.json").read_text(encoding="utf-8"))}
    obligations = {o["id"]: o["problem_id"] for o in
                   json.loads((root / "data/proof_obligations.json").read_text(encoding="utf-8"))["obligations"]}
    moves = {}
    for m in doc.get("moves", []):
        mid = m.get("id", "")
        if not ID.fullmatch(mid) or mid in moves or not all(m.get(k) for k in ("name", "description")):
            raise ValueError("Invalid/duplicate discovery move: " + mid)
        moves[mid] = m
    if not moves:
        raise ValueError("No discovery moves")
    trails = {}
    for t in doc.get("trails", []):
        pid = t.get("problem_id")
        if pid not in problems or pid in trails or not t.get("question"):
            raise ValueError("Invalid/duplicate discovery problem: " + str(pid))
        trails[pid] = t
        seen = set()
        nodes = t.get("nodes", [])
        if not nodes:
            raise ValueError("Empty discovery trail: " + pid)
        for n in nodes:
            nid = n.get("id", "")
            if not ID.fullmatch(nid) or nid in seen:
                raise ValueError("Invalid/duplicate discovery node: " + str(nid))
            if n.get("kind") not in KINDS or n.get("status") not in STATES or not n.get("title") or not n.get("detail"):
                raise ValueError("Incomplete discovery node: " + pid + "/" + nid)
            if n["status"] == "reproduced_known" and n["kind"] != "reproduction":
                raise ValueError("Known reproduction label requires a reproduction node")
            deps = n.get("motivated_by")
            if not isinstance(deps, list) or len(deps) != len(set(deps)) or any(d not in seen for d in deps):
                raise ValueError("Discovery dependency must point to an earlier node: " + nid)
            if n.get("move_id") is not None and n["move_id"] not in moves:
                raise ValueError("Unknown discovery move: " + nid)
            if n.get("obligation_id") and obligations.get(n["obligation_id"]) != pid:
                raise ValueError("Obligation does not match problem: " + nid)
            sources = n.get("sources")
            if not isinstance(sources, list) or not sources:
                raise ValueError("Unsourced discovery node: " + nid)
            for source in sources:
                if not isinstance(source, str) or source.startswith("/") or ".." in source.split("/") or not re.fullmatch(r"[A-Za-z0-9_./-]+", source):
                    raise ValueError("Unsafe discovery source path: " + str(source))
                if not (root / source).is_file():
                    raise ValueError("Missing discovery source: " + source)
            seen.add(nid)
    if not trails:
        raise ValueError("No discovery trails")
    return doc


def load():
    return validate(json.loads(PATH.read_text(encoding="utf-8")))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    doc = load()
    print(f"OK: {len(doc['trails'])} discovery trails, "
          f"{sum(len(t['nodes']) for t in doc['trails'])} sourced nodes, "
          f"{len(doc['moves'])} reusable moves")


if __name__ == "__main__":
    main()
