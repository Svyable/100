#!/usr/bin/env python3
"""Validate the Lean formal-statement catalogue and replay its finite certificates.

    python3 scripts/formal.py            # summary
    python3 scripts/formal.py --check    # fail on any catalogue / source problem

Lean itself runs in CI through the Lean proof gate (``scripts/lean_verify.py``:
``lake build``, warnings as errors, axiom audit of every declaration registered in
``data/lean_targets.json``). This script is the dependency-free half of the
comparator-statement contract:

* every catalogue entry names an existing module, imported by ``Hundred.lean``,
  that defines the named statement and kernel-checked theorems;
* no escape hatch (``sorry``, ``admit``, ``axiom``, ``native_decide``,
  ``implemented_by``, ``extern``, ``unsafe``) appears anywhere under ``lean/``;
* the witness tables embedded in the Lean sources are replayed independently
  here, so a bad table fails fast even before the Lean kernel sees it.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "data" / "formalization.json"
LEAN = ROOT / "lean"
FORBIDDEN = re.compile(r"\b(sorry|admit|axiom|native_decide|implemented_by|extern|unsafe)\b")
LEVELS = {"author_checked", "independently_reviewed"}


class FormalError(Exception):
    pass


def strip_comments(src):
    src = re.sub(r"/-.*?-/", "", src, flags=re.S)
    return re.sub(r"--[^\n]*", "", src)


def load():
    return json.loads(CATALOGUE.read_text(encoding="utf-8"))


def declared(src, name):
    return re.search(rf"^(?:abbrev|def|theorem|lemma)\s+{re.escape(name)}\b", src, re.M) is not None


def validate(doc=None, problem_ids=None):
    doc = load() if doc is None else doc
    if problem_ids is None:
        problem_ids = {p["id"] for p in json.loads((ROOT / "data" / "problems.json").read_text(encoding="utf-8"))}
    toolchain = (LEAN / "lean-toolchain").read_text(encoding="utf-8").strip()
    if doc["toolchain"] != toolchain:
        raise FormalError(f"catalogue toolchain {doc['toolchain']} != lean/lean-toolchain {toolchain}")
    root_src = (ROOT / doc["library"]).read_text(encoding="utf-8")
    for path in sorted(LEAN.rglob("*.lean")):
        if ".lake" in path.parts or path.name == "Audit.lean":
            continue
        hit = FORBIDDEN.search(strip_comments(path.read_text(encoding="utf-8")))
        if hit:
            raise FormalError(f"{path.relative_to(ROOT)}: forbidden escape hatch '{hit.group(1)}'")
    audited = {name for row in json.loads((ROOT / "data" / "lean_targets.json").read_text(encoding="utf-8"))
               for name in row.get("declarations", [])}
    seen = set()
    for e in doc["entries"]:
        pid = e["problem_id"]
        if pid not in problem_ids or pid in seen:
            raise FormalError(f"unknown or duplicate problem {pid}")
        seen.add(pid)
        if e.get("fidelity") not in LEVELS:
            raise FormalError(f"{pid}: fidelity must be one of {sorted(LEVELS)}")
        for key in ("encodes", "statement", "namespace", "module"):
            if not isinstance(e.get(key), str) or not e[key].strip():
                raise FormalError(f"{pid}: missing {key}")
        path = ROOT / e["module"]
        if not path.is_file():
            raise FormalError(f"{pid}: missing module {e['module']}")
        module = e["module"].removeprefix("lean/").removesuffix(".lean").replace("/", ".")
        if f"import {module}" not in root_src:
            raise FormalError(f"{pid}: {module} is not imported by {doc['library']}")
        src = strip_comments(path.read_text(encoding="utf-8"))
        if f"namespace {e['namespace']}" not in src:
            raise FormalError(f"{pid}: namespace {e['namespace']} not found")
        if not declared(src, e["statement"]):
            raise FormalError(f"{pid}: statement {e['statement']} not declared")
        if pid not in path.read_text(encoding="utf-8").split("\n", 5)[3]:
            raise FormalError(f"{pid}: module header must name the problem id")
        for k in e["kernel_checked"]:
            if not declared(src, k["decl"]):
                raise FormalError(f"{pid}: kernel-checked theorem {k['decl']} not declared")
            full = f"{e['namespace']}.{k['decl']}"
            if full not in audited:
                raise FormalError(f"{pid}: {full} is not registered in data/lean_targets.json, "
                                  "so the Lean proof gate would not audit its axioms")
    return doc


# ---------------------------------------------------------------- independent replay

def _list_literal(src, name):
    m = re.search(rf"def {name}\s*:[^=]*:=\s*\[(.*?)\]\s*\n\n", src, re.S)
    if not m:
        raise FormalError(f"table {name} not found")
    return m.group(1)


def _is_prime(n):
    return n >= 2 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def replay():
    """Re-check the finite certificates embedded in the Lean sources. Returns claims checked."""
    checked = []
    src = (LEAN / "Hundred" / "Statements" / "Goldbach.lean").read_text(encoding="utf-8")
    least = [int(x) for x in re.findall(r"\d+", _list_literal(src, "leastPrime"))]
    for n in range(4, 101, 2):
        p = least[n]
        if not (p <= n and _is_prime(p) and _is_prime(n - p)):
            raise FormalError(f"Goldbach witness for {n} is invalid")
    checked.append("M006 Goldbach witnesses 4..100")
    src = (LEAN / "Hundred" / "Statements" / "ErdosStraus.lean").read_text(encoding="utf-8")
    triples = [tuple(map(int, t)) for t in re.findall(r"\((\d+),\s*(\d+),\s*(\d+)\)", _list_literal(src, "table"))]
    for n in range(2, 101):
        x, y, z = triples[n - 2]
        if not (x > 0 and y > 0 and z > 0 and 4 * x * y * z == n * (x * y + y * z + z * x)):
            raise FormalError(f"Erdős–Straus triple for {n} is invalid")
    checked.append("M019 Erdős–Straus triples 2..100")
    src = (LEAN / "Hundred" / "Statements" / "Hadamard.lean").read_text(encoding="utf-8")
    rows = [[int(v) for v in re.findall(r"-?\d+", r)] for r in re.findall(r"\[([-\d,\s]+)\]", _list_literal(src, "paley12Rows"))]
    syl = lambda k: [[-1 if bin(i & j).count("1") % 2 else 1 for j in range(2 ** k)] for i in range(2 ** k)]
    for H in (syl(2), syl(3), rows):
        n = len(H)
        if any(v not in (1, -1) for r in H for v in r) or any(
                sum(H[i][k] * H[j][k] for k in range(n)) != 0 for i in range(n) for j in range(n) if i != j):
            raise FormalError(f"Hadamard matrix of order {n} is invalid")
    checked.append("M094 Hadamard orders 4, 8, 12")
    for k in (1, 2, 3):
        for F in range(2 ** (2 ** k)):
            mem = [s for s in range(2 ** k) if F >> s & 1]
            if not mem or all(s == 0 for s in mem):
                continue
            if any(not (F >> (s | t) & 1) for s in mem for t in mem):
                continue
            if not any(2 * sum(s >> x & 1 for s in mem) >= len(mem) for x in range(k)):
                raise FormalError(f"Frankl fails for family {F} on {k} elements")
    checked.append("M075 Frankl ground sets 1..3")
    pent = lambda i, j: (j - i) % 5 in (1, 4)
    from itertools import combinations
    for a, b, c in combinations(range(5), 3):
        if pent(a, b) == pent(a, c) == pent(b, c):
            raise FormalError("pentagon has a monochromatic triangle")
    checked.append("M095 pentagon colouring")
    for q, ds in ((2, {0, 1, 3}), (3, {0, 1, 3, 9})):
        N = q * q + q + 1
        inc = lambda p, l: (p - l) % N in ds
        ok = all(sum(inc(p, l) for p in range(N)) == q + 1 for l in range(N)) and \
            all(sum(inc(p, l) and inc(r, l) for l in range(N)) == 1 for p in range(N) for r in range(N) if p != r) and \
            all(sum(inc(p, l) and inc(p, m) for p in range(N)) == 1 for l in range(N) for m in range(N) if l != m)
        if not ok:
            raise FormalError(f"difference-set plane of order {q} is invalid")
    checked.append("M096 planes of order 2 and 3")
    return checked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    opts = parser.parse_args()
    try:
        doc = validate()
        checked = replay()
    except FormalError as exc:
        print(f"FORMAL CATALOGUE ERROR: {exc}", file=sys.stderr)
        return 1
    n = len(doc["entries"])
    k = sum(len(e["kernel_checked"]) for e in doc["entries"])
    print(f"OK: {n} Lean statements, {k} kernel-checked finite results, "
          f"{len(checked)} certificate families replayed independently; no escape hatches")
    if not opts.check:
        for e in doc["entries"]:
            print(f"  {e['problem_id']}  {e['namespace']}.{e['statement']}  ({len(e['kernel_checked'])} kernel-checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
