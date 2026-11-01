#!/usr/bin/env python3
"""Replay adversarial controls for proposed mathematical lemmas.

Each record targets an EXACT auxiliary statement, not the parent conjecture.
Only allowlisted evaluators are available. The independent oracles here check
specific finite witnesses, not universal correctness or novelty.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

import ch27_local
import degree_defect
import frankl_pair_boundary

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "lemma_adversaries.json"
CATEGORIES = {"refuted_auxiliary_only", "known_theorem_positive_control"}
EVALUATORS = {
    "frankl_triple_local": "A-M075-TRIPLE",
    "frankl_doubleton": "A-M075-DOUBLET",
    "degree_defect_unsaturated": "A-M074-DEFECT",
    "ch_nine_sharp": "A-M074-NINE-28",
}
ALLOWED_FIXTURES = {
    "frankl_triple_local": "examples/FRANKL_SARVATE_RENAUD.json",
    "frankl_doubleton": "examples/FRANKL_DOUBLETON.json",
    "degree_defect_unsaturated": None,
    "ch_nine_sharp": None,
}


def validate(data):
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("Expected version-1 adversarial-control ledger")
    if not isinstance(data.get("cases"), list) or not data["cases"]:
        raise ValueError("Nonempty adversarial cases required")
    seen = set()
    for c in data["cases"]:
        if not isinstance(c, dict):
            raise ValueError("Each control must be a record")
        for k in ("id", "problem_id", "classification", "statement",
                  "evaluator", "source", "warning"):
            if not isinstance(c.get(k), str) or not c[k].strip():
                raise ValueError(f"Missing {k}")
        key = c["evaluator"]
        if (key not in EVALUATORS or c["id"] != EVALUATORS[key] or
                c["id"] in seen):
            raise ValueError("Unknown, repeated or mismatched evaluator ID")
        seen.add(c["id"])
        if c["classification"] not in CATEGORIES:
            raise ValueError("Unsupported result classification")
        if (key in ("frankl_doubleton",) and
                c["classification"] != "known_theorem_positive_control"):
            raise ValueError("Doubleton is a positive, not negative, control")
        if (key != "frankl_doubleton" and
                c["classification"] != "refuted_auxiliary_only"):
            raise ValueError("A counterexample is not a positive theorem")
        if (key.startswith("frankl") and c["problem_id"] != "M075") or (
                not key.startswith("frankl") and c["problem_id"] != "M074"):
            raise ValueError("Evaluator belongs to a different target")
        source = urlparse(c["source"])
        if source.scheme != "https" or not source.netloc:
            raise ValueError("Source must be an HTTPS URL")
        if c.get("fixture") != ALLOWED_FIXTURES[key]:
            raise ValueError("Unexpected fixture path")
        if not isinstance(c.get("expected"), dict):
            raise ValueError("Exact expected certificate data required")
        if key == "degree_defect_unsaturated":
            out = c.get("out")
            if not isinstance(out, list) or len(out) != 6:
                raise ValueError("Expected six-vertex adjacency witness")
        elif "out" in c:
            raise ValueError("Unexpected embedded adjacency")
    if seen != set(EVALUATORS.values()):
        raise ValueError("A baseline adversarial control was dropped")
    return data


def _fixture(c):
    path = ROOT / c["fixture"]
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Invalid family fixture")
    return raw


def _independent_family(n, sets):
    if type(n) is not int or n < 1 or not isinstance(sets, list):
        raise ValueError("Bad family")
    family = set()
    for subset in sets:
        if not isinstance(subset, list) or any(
                type(x) is not int or x < 0 or x >= n for x in subset):
            raise ValueError("Bad set indices")
        item = frozenset(subset)
        if len(item) != len(subset) or item in family:
            raise ValueError("Duplicated set or element")
        family.add(item)
    if not family or any(a | b not in family for a in family for b in family):
        raise ValueError("Family fails independent union-closure")
    return family


def _independent_graph(out, oriented):
    n = len(out)
    if n < 2:
        raise ValueError("Graph too small")
    matrix = [[0] * n for _ in range(n)]
    for u, row in enumerate(out):
        if not isinstance(row, (list, tuple)):
            raise ValueError("Bad graph adjacency")
        for v in row:
            if type(v) is not int or not 0 <= v < n or v == u or matrix[u][v]:
                raise ValueError("Bad directed arc")
            matrix[u][v] = 1
    if oriented and any(matrix[u][v] and matrix[v][u] for u in range(n) for v in range(n)):
        raise ValueError("Graph has a digon")
    if oriented and any(matrix[u][v] and matrix[v][w] and matrix[w][u]
                        for u in range(n) for v in range(n) for w in range(n)):
        raise ValueError("Graph has a directed triangle")
    indeg = [sum(matrix[u][v] for u in range(n)) for v in range(n)]
    return matrix, indeg


def run_case(c):
    k = c["evaluator"]
    if k == "frankl_triple_local":
        f = _fixture(c)
        got = frankl_pair_boundary.triple_local_falsifier(
            f["n"], f["sets"], f["triple"])
        independent = _independent_family(f["n"], f["sets"])
        freq = [sum(i in s for s in independent) for i in f["triple"]]
        if freq != got["triple_frequencies"] or len(independent) != got["family_size"]:
            raise AssertionError("Independent Frankl frequency disagreement")
        report = {a: got[a] for a in c["expected"]}
    elif k == "frankl_doubleton":
        f = _fixture(c)
        got = frankl_pair_boundary.doubleton_certificate(
            f["n"], f["sets"], 0, 1)
        independent = _independent_family(f["n"], f["sets"])
        if (sum(0 in s for s in independent) != got["frequency_a"] or
                sum(1 in s for s in independent) != got["frequency_b"]):
            raise AssertionError("Independent pair frequency disagreement")
        report = {a: got[a] for a in c["expected"]}
    elif k == "degree_defect_unsaturated":
        got = degree_defect.inspect(c["out"])
        matrix, indeg = _independent_graph(c["out"], False)
        low = {i for i, d in enumerate(indeg) if d < got["r"]}
        low_low = sum(matrix[u][v] for u in low for v in low)
        if indeg != got["indegrees"] or low_low != got["low_to_low"]:
            raise AssertionError("Independent degree-defect disagreement")
        report = {a: got[a] for a in c["expected"]}
    elif k == "ch_nine_sharp":
        out = ch27_local.sharp_nine()
        got = ch27_local.check_oriented_triangle_free(out)
        _, indeg = _independent_graph(out, True)
        if max(indeg) != max(got["indegrees"]):
            raise AssertionError("Independent CH graph disagreement")
        report = {
            "n":got["n"],"arcs":got["arcs"],
            "minimum_outdegree":got["minimum_outdegree"],
            "maximum_indegree":max(got["indegrees"])
        }
    else:
        raise ValueError("Unknown evaluator")
    if report != c["expected"]:
        raise AssertionError(f"{c['id']}: expected certificate mismatch: {report}")
    return {"id":c["id"], "problem_id":c["problem_id"],
            "classification":c["classification"], "result":"replayed",
            "facts":report, "full_conjecture_resolved":False}


def report(data):
    validate(data)
    items = [run_case(c) for c in data["cases"]]
    return {"controls":len(items),
            "false_auxiliary":sum(x["classification"]=="refuted_auxiliary_only" for x in items),
            "known_positive":sum(x["classification"]=="known_theorem_positive_control" for x in items),
            "open_conjectures_resolved":0, "results":items}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="replay all pinned adversarial controls")
    args = parser.parse_args()
    try:
        data = json.loads(LEDGER.read_text(encoding="utf-8"))
        result = report(data)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ValueError, OSError, TypeError, KeyError, AssertionError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
