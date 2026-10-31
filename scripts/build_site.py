#!/usr/bin/env python3
"""Generate the GitHub Pages JSON snapshot deterministically from the registry.

The source of truth is data/problems.json, NOT docs/data/portfolio.json.
No network, timestamps generated at runtime, or external dependencies.
"""
import argparse
import json
from pathlib import Path
from rank import validate, score, REGISTRY, ROOT

OUTPUT = ROOT / "docs" / "data" / "portfolio.json"


def build():
    items = validate(json.loads(REGISTRY.read_text(encoding="utf-8")))
    sorted_items = sorted(items, key=lambda item: (-score(item), item["id"]))
    states = sorted({p["evidence_state"] for p in items})
    return {
        "title": "100 — A living mathematical research portfolio",
        "source": "data/problems.json",
        "source_review_as_of": max((p["checked_on"] or "" for p in items), default=""),
        "scoring": {
            "impact": 30,
            "attackability": 30,
            "verifiability": 25,
            "spillover": 15,
            "interpretation": "Editorial priority score, not an estimated proof probability",
        },
        "status_counts": {
            status: sum(p["evidence_state"] == status for p in items)
            for status in states
        },
        "problems": [
            {**item, "rank": number, "score": score(item)}
            for number, item in enumerate(sorted_items, start=1)
        ],
    }


def render():
    return json.dumps(build(), indent=2, ensure_ascii=False) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="fail if the committed site snapshot is stale")
    options = parser.parse_args()
    expected = render()
    if options.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit("Stale GitHub Pages data: run python3 scripts/build_site.py")
        print("OK: Pages snapshot matches all 100 ranked registry records")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(expected, encoding="utf-8")
        print("Updated docs/data/portfolio.json")


if __name__ == "__main__":
    main()
