#!/usr/bin/env python3
"""Exact probe lab: run every probe, re-check it independently, record results.

    python3 scripts/lab.py                    # all probes, smoke level; updates ledger + LAB.md
    python3 scripts/lab.py --level deep       # larger finite ranges (minutes)
    python3 scripts/lab.py --probe hadamard   # one probe (repeatable flag)
    python3 scripts/lab.py --check            # rerun and fail on any drift from the ledger
    python3 scripts/lab.py --list             # engines and probes
    python3 scripts/lab.py --emit DIR         # also write full certificates for outside replay
    python3 scripts/lab.py --replay FILE      # independently re-check an emitted certificate
    python3 scripts/lab.py --render           # rebuild LAB.md from the committed ledger only

Exit codes: 0 ok, 1 stale ledger/report, 2 independent check failed,
3 counterexample candidate (the search found a violation that the checker
confirmed). Inside the ranges shipped here every statement is already known,
so exit 3 almost certainly means a bug; it never promotes anything to Solved.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import probes
from probes.core import ProbeFailure, digest
from rank import COMPUTABLE, ROOT
import research

RESULTS = ROOT / "data" / "lab_results.json"
REPORT = ROOT / "LAB.md"
ROADMAP = ROOT / "data" / "engine_roadmap.json"
FORMAT = "svyable.lab.v1"
LEVELS = ("smoke", "deep")

MODALITY_TEXT = {
    "finite_refutable": "One finite, checkable object would refute it; computation can search and certify ranges.",
    "finite_parameter": "Asks for one specific finite value or object; exhaustive search or a certificate can settle it.",
    "existence_family": "Existence for infinitely many finite parameters; constructions certify cases, one certified nonexistence refutes.",
    "asymptotic": "Limiting or infinitary statement; computation gives data and certified bounds, never a refutation.",
    "structural": "About infinite or continuous objects; computation helps only through restricted finite analogues.",
}


class LabError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def empty_ledger():
    return {"format": FORMAT, "levels": {level: {} for level in LEVELS}}


def load_ledger():
    if not RESULTS.exists():
        return empty_ledger()
    doc = json.loads(RESULTS.read_text(encoding="utf-8"))
    if doc.get("format") != FORMAT or set(doc.get("levels", {})) != set(LEVELS):
        raise LabError(1, "Malformed lab ledger")
    for level, records in doc["levels"].items():
        for pid, rec in records.items():
            if pid not in probes.PROBES or rec.get("probe") != pid or rec.get("level") != level:
                raise LabError(1, f"Ledger entry {level}/{pid} does not match the probe registry")
    return doc


def dump(doc):
    return json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def run_probe(module, level):
    params = module.PROBE["levels"][level]
    t0 = time.perf_counter()
    result = module.search(params)
    t1 = time.perf_counter()
    try:
        module.check(params, result)
    except ProbeFailure as exc:
        raise LabError(2, f"{module.PROBE['id']} ({level}): independent check FAILED: {exc}") from exc
    t2 = time.perf_counter()
    record = {
        "probe": module.PROBE["id"],
        "problem_id": module.PROBE["problem_id"],
        "level": level,
        "engines": module.PROBE["engines"],
        "params": params,
        "holds": bool(result["holds"]),
        "scope": module.scope(params),
        "summary": result["summary"],
        "certificate_sha256": digest(result["certificate"]),
    }
    return record, result, (t1 - t0, t2 - t1)


# ------------------------------------------------------------------ report

def coverage(items, program):
    """Problem ids with at least one allowlisted exact verifier (probe or standalone)."""
    covered = {m.PROBE["problem_id"] for m in probes.all_probes()}
    for c in program["campaigns"]:
        if c.get("verifier") or c.get("additional_verifiers"):
            covered.add(c["problem_id"])
    active = {p["id"] for p in items}
    return covered & active


def load_roadmap(items, covered):
    doc = json.loads(ROADMAP.read_text(encoding="utf-8"))
    by_id = {p["id"]: p for p in items}
    seen = set()
    for e in doc["entries"]:
        pid = e["problem_id"]
        if pid not in by_id or pid in seen:
            raise LabError(1, f"Roadmap: unknown or duplicate problem {pid}")
        if by_id[pid]["modality"] not in COMPUTABLE:
            raise LabError(1, f"Roadmap: {pid} is not in a computable modality")
        if pid in covered:
            raise LabError(1, f"Roadmap: {pid} already has an exact verifier; remove it from the roadmap")
        if not all(isinstance(e.get(k), str) and e[k].strip() for k in ("engine", "first_probe")):
            raise LabError(1, f"Roadmap: {pid} needs engine and first_probe")
        seen.add(pid)
    missing = sorted(p["id"] for p in items
                     if p["modality"] in COMPUTABLE and p["id"] not in covered and p["id"] not in seen)
    if missing:
        raise LabError(1, "Roadmap must list every computable problem without a verifier: " + ", ".join(missing))
    return doc


def _cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def render_report(ledger):
    items, program, _ = research.load()
    by_id = {p["id"]: p for p in items}
    mods = probes.all_probes()
    covered = coverage(items, program)
    roadmap = load_roadmap(items, covered)
    computable = [p for p in items if p["modality"] in COMPUTABLE]
    lines = [
        "# Exact probe lab — computational reach of the 100", "",
        f"Generated by `python3 scripts/lab.py` from [the ledger](data/lab_results.json); do not edit by hand. "
        f"Program as of {program['as_of']}.", "",
        "> Every result below is a **finite computation that a second, independent checker re-verified**.",
        "> Each range is either covered by known results or is a small exploratory falsifier check flagged in",
        "> its probe's frontier. Nothing here is a new theorem, nothing resolves an open conjecture, and nothing",
        "> can enter the [Solved archive](data/solved.json). The lab exists so that a new finite",
        "> case, counterexample or certificate can be checked as soon as someone produces one, and so that each",
        "> engine built for one problem is reused on the next.", "",
        "## Reach at a glance", "",
        "| Metric | Value |", "|---|---:|",
        f"| Problems with an exact, independently checked verifier | {len(covered)} / {len(items)} |",
        f"| Computable-modality problems covered | {sum(p['id'] in covered for p in computable)} / {len(computable)} |",
        f"| Exact probes in the lab | {len(mods)} |",
        f"| Reusable engines | {len(probes.ENGINES)} |",
        f"| Engines serving two or more problems | "
        f"{sum(len({m.PROBE['problem_id'] for m in mods if e in m.PROBE['engines']}) >= 2 for e in probes.ENGINES)} |",
        f"| Probe runs recorded (smoke / deep) | {len(ledger['levels']['smoke'])} / {len(ledger['levels']['deep'])} |",
        "",
        "## Coverage by computational modality", "",
        "Each of the 100 problems carries an editorial `modality` in [data/problems.json](data/problems.json):",
        "how, if at all, finite exact computation can bear on the statement.", "",
        "| Modality | What computation can do | Problems | With exact verifier |", "|---|---|---:|---:|",
    ]
    for modality, text in MODALITY_TEXT.items():
        group = [p for p in items if p["modality"] == modality]
        lines.append(f"| `{modality}` | {text} | {len(group)} | {sum(p['id'] in covered for p in group)} |")
    lines += ["", "## Engines and the problems they serve", "",
              "| Engine | What it is | Problems served by probes | Source |", "|---|---|---|---|"]
    for eid, e in probes.ENGINES.items():
        served = sorted({m.PROBE["problem_id"] for m in mods if eid in m.PROBE["engines"]})
        names = ", ".join(f"{pid} {by_id[pid]['name']}" for pid in served) or "—"
        src = ", ".join(f"[{Path(x).name}]({x})" for x in e["modules"])
        lines.append(f"| `{eid}` | {_cell(e['name'])} | {_cell(names)} | {src} |")
    lines += ["", "## Probe results", "",
              "| Problem | Probe | Verified here (smoke · deep) | Literature frontier | Certificate SHA-256 |",
              "|---|---|---|---|---|"]
    for m in mods:
        pid, probe_id = m.PROBE["problem_id"], m.PROBE["id"]
        cells = []
        for level in LEVELS:
            rec = ledger["levels"][level].get(probe_id)
            if rec:
                status = "" if rec["holds"] else " **COUNTEREXAMPLE CANDIDATE**"
                cells.append(f"*{level}:* {rec['scope']}{status}")
            else:
                cells.append(f"*{level}:* not yet run")
        shas = " · ".join(f"`{ledger['levels'][lv][probe_id]['certificate_sha256'][:12]}`"
                          for lv in LEVELS if probe_id in ledger["levels"][lv])
        lines.append(f"| {pid} {_cell(by_id[pid]['name'])} | [`{probe_id}`]({probes.artifact(probe_id)}) "
                     f"| {_cell('<br>'.join(cells))} | {_cell(m.PROBE['frontier'])} | {shas or '—'} |")
    standalone = [c for c in program["campaigns"] if c.get("verifier") and
                  not c["verifier"].startswith("python3 scripts/lab.py")]
    lines += ["", "## Standalone verifiers", "",
              "Verifiers that predate the lab and run on their own:", "",
              "| Problem | Command | Checker |", "|---|---|---|"]
    for c in standalone:
        art = research.RUNNABLE[c["verifier"]]
        lines.append(f"| {c['problem_id']} {_cell(by_id[c['problem_id']]['name'])} | `{c['verifier']}` | [{art}]({art}) |")
    lines += ["", "## Engine roadmap — computable problems without a probe yet", "",
              roadmap["note"], "",
              "| Problem | Modality | Engine to build | First probe |", "|---|---|---|---|"]
    for e in roadmap["entries"]:
        p = by_id[e["problem_id"]]
        lines.append(f"| {p['id']} {_cell(p['name'])} | `{p['modality']}` | `{e['engine']}` | {_cell(e['first_probe'])} |")
    lines += ["", "## Add a probe", "",
              "1. Write `scripts/probes/<name>.py` with `PROBE` metadata, `search(params)`, an **independent**",
              "   `check(params, result)` that raises `ProbeFailure`, and `scope(params)`. Reuse an engine if one fits.",
              "2. Register it in `PROBES` in [scripts/probes/\\_\\_init\\_\\_.py](scripts/probes/__init__.py).",
              "3. Add tamper tests in [tests/test_lab.py](tests/test_lab.py): the checker must reject a corrupted certificate.",
              "4. Add or extend the problem's campaign and a `reproduced_known` milestone in",
              "   [data/research_program.json](data/research_program.json) (verifier `python3 scripts/lab.py --probe <id>`).",
              "5. Run `python3 scripts/lab.py`, `python3 scripts/lab.py --level deep`, then the full rebuild in the README.", ""]
    return "\n".join(lines)


def snapshot(ledger=None):
    """Compact, deterministic lab summary for the Pages portfolio."""
    ledger = load_ledger() if ledger is None else ledger
    items, program, _ = research.load()
    by_id = {p["id"]: p for p in items}
    covered = coverage(items, program)
    roadmap = load_roadmap(items, covered)
    mods = probes.all_probes()
    return {
        "covered_problems": sorted(covered),
        "computable_problems": sorted(p["id"] for p in items if p["modality"] in COMPUTABLE),
        "modalities": [
            {"modality": m, "description": text,
             "problems": sum(p["modality"] == m for p in items),
             "with_verifier": sum(p["modality"] == m and p["id"] in covered for p in items)}
            for m, text in MODALITY_TEXT.items()
        ],
        "engines": [
            {"id": eid, "name": e["name"], "use": e["use"], "modules": e["modules"],
             "problems": sorted({m.PROBE["problem_id"] for m in mods if eid in m.PROBE["engines"]})}
            for eid, e in probes.ENGINES.items()
        ],
        "probes": [
            {"id": m.PROBE["id"], "problem_id": m.PROBE["problem_id"],
             "name": by_id[m.PROBE["problem_id"]]["name"], "title": m.PROBE["title"],
             "engines": m.PROBE["engines"], "frontier": m.PROBE["frontier"],
             "artifact": probes.artifact(m.PROBE["id"]), "command": probes.command(m.PROBE["id"]),
             "runs": {level: {"holds": rec["holds"], "scope": rec["scope"],
                              "certificate_sha256": rec["certificate_sha256"]}
                      for level in LEVELS
                      for rec in [ledger["levels"][level].get(m.PROBE["id"])] if rec}}
            for m in mods
        ],
        "roadmap": [dict(e, name=by_id[e["problem_id"]]["name"]) for e in roadmap["entries"]],
    }


# --------------------------------------------------------------------- CLI

def list_lab():
    print("Engines:")
    for eid, e in probes.ENGINES.items():
        print(f"  {eid:20s} {e['name']}")
    print("Probes:")
    for m in probes.all_probes():
        p = m.PROBE
        print(f"  {p['id']:18s} {p['problem_id']}  [{', '.join(p['engines'])}]  {p['title']}")


def replay(path):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    module = probes.load(doc["probe"])
    if doc.get("params") != module.PROBE["levels"].get(doc.get("level")):
        print("note: params differ from the registered level; checking the supplied params as given")
    try:
        module.check(doc["params"], doc["result"])
    except ProbeFailure as exc:
        raise LabError(2, f"Replay of {path} FAILED: {exc}") from exc
    if digest(doc["result"]["certificate"]) != doc.get("certificate_sha256"):
        raise LabError(2, "Replay: certificate hash does not match the recorded SHA-256")
    print(f"OK: {doc['probe']} certificate independently re-verified ({doc['certificate_sha256'][:16]}…)")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--level", choices=LEVELS, default="smoke")
    parser.add_argument("--probe", action="append", choices=sorted(probes.PROBES))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--emit", metavar="DIR")
    parser.add_argument("--replay", metavar="FILE")
    parser.add_argument("--render", action="store_true")
    opts = parser.parse_args(argv)
    try:
        if opts.list:
            return list_lab()
        if opts.replay:
            return replay(opts.replay)
        ledger = load_ledger()
        if opts.render:
            REPORT.write_text(render_report(ledger), encoding="utf-8")
            print("Updated LAB.md from the committed ledger")
            return 0
        selected = opts.probe or list(probes.PROBES)
        candidates = []
        for pid in selected:
            module = probes.load(pid)
            record, result, (ts, tc) = run_probe(module, opts.level)
            flag = "HOLDS" if record["holds"] else "COUNTEREXAMPLE CANDIDATE"
            print(f"{pid:18s} {module.PROBE['problem_id']} {opts.level:5s} {flag:8s} "
                  f"search {ts:6.2f}s  check {tc:6.2f}s  {record['certificate_sha256'][:12]}")
            if not record["holds"]:
                candidates.append(record)
            if opts.emit:
                out = Path(opts.emit)
                out.mkdir(parents=True, exist_ok=True)
                (out / f"{pid}.{opts.level}.json").write_text(json.dumps(
                    {**record, "result": result}, sort_keys=True, default=list), encoding="utf-8")
            if opts.check:
                committed = ledger["levels"][opts.level].get(pid)
                if committed != json.loads(json.dumps(record)):
                    raise LabError(1, f"Stale lab ledger for {pid} ({opts.level}): run python3 scripts/lab.py"
                                      + (" --level deep" if opts.level == "deep" else ""))
            else:
                ledger["levels"][opts.level][pid] = json.loads(json.dumps(record))
        if candidates:
            for rec in candidates:
                print(f"!!! COUNTEREXAMPLE CANDIDATE for {rec['problem_id']} via {rec['probe']} — the independent "
                      "checker confirmed the violating object. This range is inside known verified mathematics, "
                      "so first suspect a bug. Never promote to Solved without full external review.",
                      file=sys.stderr)
        report = render_report(ledger)
        if opts.check:
            if not REPORT.exists() or REPORT.read_text(encoding="utf-8") != report:
                raise LabError(1, "Stale LAB.md: run python3 scripts/lab.py --render")
            print(f"OK: {len(selected)} probe(s) reproduced the committed {opts.level} ledger exactly")
        else:
            RESULTS.write_text(dump(ledger), encoding="utf-8")
            REPORT.write_text(report, encoding="utf-8")
            print("Updated data/lab_results.json and LAB.md")
        return 3 if candidates else 0
    except LabError as exc:
        print(exc, file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    sys.exit(main())
