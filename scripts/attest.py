#!/usr/bin/env python3
"""Mechanical pre-review attestations for the exact probe lab.

Independent review is the throughput bottleneck of this repository (YIELD.md).
Most of a ``V-P-<problem>`` review is mechanical: rerun the verifier, pin the
certificate, deliberately corrupt it and confirm the checker rejects every
corruption. This tool does that part for every allowlisted probe so that a
human reviewer only has to (a) triage the mutants that *survived* and
(b) compare the finite scope against the cited source.

    python3 scripts/attest.py                     # all probes, writes data/attestations.json
    python3 scripts/attest.py --probe sic         # one probe (repeatable)
    python3 scripts/attest.py --mutants 200       # more random certificate mutants per probe
    python3 scripts/attest.py --probe dirichlet_l --mutants 4   # smaller budget for a slow checker
    python3 scripts/attest.py --check             # rerun and fail on drift from the ledger
    python3 scripts/attest.py --render            # Markdown table from the committed ledger
    python3 scripts/attest.py --json              # print, do not write

For each probe and level it records:

* **replay** - ``search`` reproduces the certificate digest committed in
  data/lab_results.json, and ``check`` accepts it;
* **controls** - mandatory negative controls (flip ``holds``, empty the
  certificate) must be rejected;
* **summary binding** - every published ``summary`` leaf is mutated once; a
  surviving mutant means the checker does not bind that published number;
* **certificate mutants** - seeded, structure-aware corruptions (integer and
  fraction nudges, boolean flips, list drop/duplicate/swap) of the certificate.

Status per probe: ``clean`` (nothing survived), ``triage`` (summary or
certificate survivors for a person to classify), ``weak`` (a mandatory control
survived: the checker accepts a flipped verdict or an empty certificate) and
``broken`` (the certificate no longer replays). Exit codes: 0 ok, 1 ledger drift
or malformed ledger, 2 a probe is ``broken``. A ``weak`` probe is a recorded
finding for a follow-up work item, not a run failure.

An attestation is **not** an independent review, an acceptance, or evidence
about any untested range. A surviving certificate mutant may be an equivalent
valid certificate; only a person can decide. Nothing here edits outcomes,
fidelity, evidence states or Solved.
"""
import argparse
import copy
import hashlib
import json
import random
import re
import signal
import sys
import time
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import probes  # noqa: E402
from probes.core import ProbeFailure, canonical, digest  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "attestations.json"
LAB = ROOT / "data" / "lab_results.json"
FORMAT = "svyable.attest.v1"
SEED_VERSION = 1
DEFAULT_MUTANTS = 24
SUMMARY_CAP = 48
FRACTION = re.compile(r"^(-?\d+)/(\d+)$")
INTEGER = re.compile(r"^-?\d+$")


class Timeout(BaseException):
    """Raised by the alarm; BaseException so a broad ``except Exception`` cannot swallow it."""


def _alarm(_signum, _frame):
    raise Timeout()


# ------------------------------------------------------------------ mutation

def walk(obj, path=()):
    """Yield (path, value) for every leaf and every non-empty sequence below obj."""
    if isinstance(obj, dict):
        for key in sorted(obj, key=str):
            yield from walk(obj[key], path + (key,))
    elif isinstance(obj, (list, tuple)):
        if obj:
            yield path, obj
        for i, value in enumerate(obj):
            yield from walk(value, path + (i,))
    else:
        yield path, obj


def put(obj, path, value):
    """Return obj with path replaced; tuples on the path are rebuilt, not mutated."""
    if not path:
        return value
    child = put(obj[path[0]], path[1:], value)
    if isinstance(obj, tuple):
        rebuilt = list(obj)
        rebuilt[path[0]] = child
        return tuple(rebuilt)
    obj[path[0]] = child
    return obj


def mutate(value, rng):
    """One deterministic structure-aware corruption of value, or None if none applies."""
    if isinstance(value, bool):
        return "bool_flip", (not value)
    if isinstance(value, int):
        if value == 0:
            return "int_one", 1
        step = rng.choice((1, -1))
        return ("int_inc" if step > 0 else "int_dec"), value + step
    if isinstance(value, float):
        return "float_nudge", value * (1 + 1e-6) + 1e-9
    if isinstance(value, Fraction):
        return "fraction_nudge", value + Fraction(1, 7)
    if isinstance(value, str):
        m = FRACTION.match(value)
        if m:
            return "fraction_text_nudge", f"{int(m.group(1)) + 1}/{m.group(2)}"
        if INTEGER.match(value):
            return "int_text_inc", str(int(value) + 1)
        return "text_append", value + "x"
    if isinstance(value, (list, tuple)):
        items = list(value)
        ops = ["list_drop", "list_dup"] + (["list_swap"] if len(items) > 1 else [])
        op = rng.choice(ops)
        i = rng.randrange(len(items))
        if op == "list_drop":
            del items[i]
        elif op == "list_dup":
            items.insert(i, copy.deepcopy(items[i]))
        else:
            j = rng.randrange(len(items))
            if items[i] == items[j]:
                return None
            items[i], items[j] = items[j], items[i]
        return op, (tuple(items) if isinstance(value, tuple) else items)
    return None


def seed_for(probe_id, level):
    text = f"{probe_id}:{level}:{SEED_VERSION}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(text).digest()[:8], "big")


def mutants(result, count, rng):
    """Mandatory controls, every summary leaf (capped), then `count` certificate mutants."""
    yield "control", ("holds",), "holds_flip", put(copy.deepcopy(result), ("holds",), not result["holds"])
    empty = {} if isinstance(result["certificate"], dict) else []
    yield "control", ("certificate",), "certificate_empty", put(copy.deepcopy(result), ("certificate",), empty)
    summary = [(p, v) for p, v in walk(result.get("summary", {}), ("summary",)) if len(p) > 1]
    if len(summary) > SUMMARY_CAP:
        summary = rng.sample(summary, SUMMARY_CAP)
    for path, value in summary:
        change = mutate(value, rng)
        if change:
            yield "summary", path, change[0], put(copy.deepcopy(result), path, change[1])
    pool = [(p, v) for p, v in walk(result["certificate"], ("certificate",)) if len(p) > 1]
    made, tries = 0, 0
    while pool and made < count and tries < count * 20:
        tries += 1
        path, value = rng.choice(pool)
        change = mutate(value, rng)
        if change:
            made += 1
            yield "certificate", path, change[0], put(copy.deepcopy(result), path, change[1])


def verdict(module, params, candidate, limit):
    """killed | crashed | timeout | survived for one candidate result."""
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, limit)
    try:
        module.check(params, candidate)
        return "survived"
    except ProbeFailure:
        return "killed"
    except Timeout:
        return "timeout"
    except Exception:  # noqa: BLE001 - any other rejection is fail-closed but untyped
        return "crashed"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


# ------------------------------------------------------------------ attestation

def code_digest(probe_id):
    paths = [ROOT / probes.artifact(probe_id), ROOT / "scripts" / "probes" / "core.py"]
    h = hashlib.sha256()
    for path in paths:
        h.update(path.relative_to(ROOT).as_posix().encode("utf-8") + b"\0")
        h.update(path.read_bytes())
    return h.hexdigest()


def lab_digest(probe_id, level):
    doc = json.loads(LAB.read_text(encoding="utf-8"))
    rec = doc.get("levels", {}).get(level, {}).get(probe_id)
    return rec["certificate_sha256"] if rec else None


def attest(probe_id, level="smoke", count=DEFAULT_MUTANTS):
    module = probes.load(probe_id)
    params = module.PROBE["levels"][level]
    result = module.search(params)
    cert_sha = digest(result["certificate"])
    pinned = lab_digest(probe_id, level)
    started = time.perf_counter()
    baseline = verdict(module, params, copy.deepcopy(result), 3600)
    check_seconds = time.perf_counter() - started
    limit = max(10.0, 25 * check_seconds)
    rng = random.Random(seed_for(probe_id, level))
    base = canonical(result)
    tally = {"killed": 0, "crashed": 0, "timeout": 0, "survived": 0}
    regions = {}
    survivors, failed_controls, seen = [], [], set()
    for region, path, op, candidate in mutants(result, count, rng):
        text = canonical(candidate)
        if text == base or text in seen:
            continue  # an identity or repeated mutation tests nothing
        seen.add(text)
        outcome = verdict(module, params, candidate, limit)
        tally[outcome] += 1
        r = regions.setdefault(region, {"tried": 0, "rejected": 0})
        r["tried"] += 1
        r["rejected"] += outcome in ("killed", "crashed")
        if outcome == "survived":
            entry = {"region": region, "path": "/".join(map(str, path)), "op": op}
            survivors.append(entry)
            if region == "control":
                failed_controls.append(entry["op"])
    replay = ("match" if pinned == cert_sha and baseline == "survived"
              else "unpinned" if pinned is None and baseline == "survived" else "drift")
    flags = []
    if replay != "match":
        flags.append(f"replay_{replay}")
    flags += [f"control_survived:{op}" for op in failed_controls]
    if any(s["region"] == "summary" for s in survivors):
        flags.append("unbound_summary")
    if any(s["region"] == "certificate" for s in survivors):
        flags.append("certificate_survivors_need_triage")
    if tally["timeout"]:
        flags.append("checker_timeouts")
    status = ("broken" if replay == "drift" else "weak" if failed_controls
              else "triage" if flags else "clean")
    return {
        "probe": probe_id,
        "problem_id": module.PROBE["problem_id"],
        "level": level,
        "command": probes.command(probe_id),
        "code_sha256": code_digest(probe_id),
        "certificate_sha256": cert_sha,
        "replay": replay,
        "seed": seed_for(probe_id, level),
        "certificate_mutants_requested": count,
        "tally": tally,
        "regions": dict(sorted(regions.items())),
        "survivors": survivors,
        "flags": flags,
        "status": status,
    }


def empty_ledger():
    return {
        "format": FORMAT,
        "note": ("Mechanical pre-review evidence only: replay, negative controls and seeded "
                 "mutation of each lab certificate. Not an independent review or acceptance; "
                 "surviving certificate mutants may be equivalent valid certificates."),
        "seed_version": SEED_VERSION,
        "probes": {},
    }


def load_ledger():
    if not LEDGER.exists():
        return empty_ledger()
    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    if doc.get("format") != FORMAT or not isinstance(doc.get("probes"), dict):
        raise SystemExit("attest: malformed data/attestations.json")
    for key, rec in doc["probes"].items():
        if rec.get("probe") not in probes.PROBES or key != f"{rec['probe']}@{rec.get('level')}":
            raise SystemExit(f"attest: ledger key {key} does not match the probe registry")
    return doc


def dump(doc):
    return json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render(doc):
    lines = [
        "| Probe | Problem | Replay | Controls | Summary rejected | Certificate rejected | Survivors | Status |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for key in sorted(doc["probes"]):
        r = doc["probes"][key]
        reg = r["regions"]

        def frac(name):
            x = reg.get(name)
            return f"{x['rejected']}/{x['tried']}" if x else "—"
        controls = "fail" if any(f.startswith("control_survived") for f in r["flags"]) else "pass"
        stale = " (stale: probe code changed)" if r["code_sha256"] != code_digest(r["probe"]) else ""
        lines.append(f"| `{r['probe']}` | {r['problem_id']} | {r['replay']} | {controls} | "
                     f"{frac('summary')} | {frac('certificate')} | {len(r['survivors'])} | {r['status']}{stale} |")
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--probe", action="append", choices=sorted(probes.PROBES))
    p.add_argument("--skip", action="append", default=[], choices=sorted(probes.PROBES))
    p.add_argument("--level", default="smoke", choices=("smoke", "deep"))
    p.add_argument("--mutants", type=int, default=DEFAULT_MUTANTS)
    p.add_argument("--check", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--render", action="store_true")
    args = p.parse_args()
    if not 0 <= args.mutants <= 10000:
        p.error("--mutants must be between 0 and 10000")
    doc = load_ledger()
    if args.render:
        sys.stdout.write(render(doc))
        return 0
    ids = [i for i in (args.probe or list(probes.PROBES)) if i not in args.skip]
    fresh = {}
    for pid in ids:
        t0 = time.perf_counter()
        count = args.mutants
        if args.check and f"{pid}@{args.level}" in doc["probes"]:
            # Replay exactly what was attested, including a smaller budget for slow probes.
            count = doc["probes"][f"{pid}@{args.level}"]["certificate_mutants_requested"]
        rec = attest(pid, args.level, count)
        fresh[f"{pid}@{args.level}"] = rec
        print(f"{pid:18s} {rec['status']:6s} replay={rec['replay']:5s} "
              f"tally={rec['tally']} flags={rec['flags']} ({time.perf_counter() - t0:.1f}s)",
              file=sys.stderr)
    if args.check:
        drift = []
        for key, rec in fresh.items():
            old = doc["probes"].get(key)
            if old is None:
                drift.append(f"{key}: missing from ledger")
            elif dump(old) != dump(rec):
                drift.append(f"{key}: attestation drifted (rerun scripts/attest.py and review the diff)")
        for line in drift:
            print(line, file=sys.stderr)
        if any(r["status"] == "broken" for r in fresh.values()):
            return 2
        return 1 if drift else 0
    doc["probes"].update(fresh)
    if args.json:
        sys.stdout.write(dump({**doc, "probes": fresh}))
    else:
        LEDGER.write_text(dump(doc), encoding="utf-8")
        print(f"wrote {LEDGER.relative_to(ROOT)} ({len(fresh)} probe(s))", file=sys.stderr)
    return 2 if any(r["status"] == "broken" for r in fresh.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
