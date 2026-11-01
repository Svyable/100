#!/usr/bin/env python3
"""Optional, bounded CaDiCaL pilot; NO UNSAT proof certificates are produced.

Requires an external, unvendored python-sat installation.
  python3 scripts/frankl_triple_experiment.py --sizes 18,17 --conflicts 200000
  python3 scripts/frankl_triple_experiment.py --sizes 18 --conflicts 200000 --out /tmp/run.json
An UNSAT answer is explicitly *uncertified*; use independently checked proof
traces for every size to establish a global >=19 lower bound.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys
from time import monotonic

import frankl_triple_sat as core

PROTOCOL = "svyable.frankl.triple-seven-pilot.v1"


def classification(answer):
    if answer is True:
        return "sat_verified_witness"
    if answer is False:
        return "unsat_solver_report_only"
    if answer is None:
        return "unknown_budget_exhausted"
    raise ValueError("Unexpected SAT solver result")


def pilot(sizes, conflicts):
    if not sizes or any(type(k) is not int or not 2 <= k <= 18 for k in sizes):
        raise ValueError("Sizes must be in 2..18")
    if len(set(sizes)) != len(sizes):
        raise ValueError("No duplicate sizes")
    if type(conflicts) is not int or not 1 <= conflicts <= 10_000_000:
        raise ValueError("Conflict limit must be an integer in 1..10,000,000")

    try:
        from pysat.solvers import Solver
        distribution = version("python-sat")
    except (ImportError, ModuleNotFoundError):
        raise RuntimeError("This optional experiment requires python-sat (not a repo dependency)")

    records = []
    for k in sizes:
        cnf = core.build(n=7, size=k)
        encoded = cnf.dimacs().encode("ascii")
        started = monotonic()
        with Solver(name="cadical195", bootstrap_with=cnf.clauses) as solver:
            solver.conf_budget(conflicts)
            answer = solver.solve_limited(expect_interrupt=True)
            stats = {key: int(value) for key, value in solver.accum_stats().items()}
            witness = None
            if answer is True:
                model = solver.get_model()
                if not model:
                    raise ValueError("SAT result without a model")
                text = "s SATISFIABLE\nv " + " ".join(map(str, model)) + " 0\n"
                chosen = core.parse_solver_model(text, cnf)
                core.independent_check(chosen, n=7, size=k)
                witness = [{"set": [e for e in range(7) if mask & (1 << e)],
                            "mask": mask} for mask in sorted(chosen)]
        records.append({
            "size": k,
            "status": classification(answer),
            "cnf_sha256": sha256(encoded).hexdigest(),
            "variables": cnf.var_count,
            "clauses": len(cnf.clauses),
            "resource_cap_conflicts": conflicts,
            "observed_conflicts": stats.get("conflicts"),
            "solver_stats": stats,
            "elapsed_seconds": round(monotonic() - started, 3),
            "witness": witness,
        })
    return {
        "protocol": PROTOCOL,
        "scope": ("n=7, exact triple {0,1,2} and empty member required, "
                  "union-closed, strict triple-local failure; sizes 2..18 independent"),
        "solver": "cadical195",
        "python_sat_version": distribution,
        "python_version": platform.python_version(),
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_boundary": ("A SAT model is a candidate verified by independent direct set operations. "
                              "An UNSAT return is ONLY a solver report and needs an independent checked "
                              "proof trace. Unknown proves nothing. This is not Frankl's conjecture."),
        "records": records,
    }



def validate_record(doc):
    """Validate instance hashes and claims; never authenticate UNSAT mathematics."""
    core.require(isinstance(doc, dict) and
                 set(doc) == {"protocol", "scope", "solver", "python_sat_version",
                              "python_version", "observed_at_utc", "evidence_boundary", "records"},
                 "Malformed pilot record")
    core.require(doc["protocol"] == PROTOCOL and doc["solver"] == "cadical195",
                 "Unknown experiment protocol or solver")
    core.require(isinstance(doc["python_sat_version"], str) and doc["python_sat_version"]
                 and isinstance(doc["python_version"], str) and doc["python_version"],
                 "Missing solver version data")
    core.require(isinstance(doc["scope"], str) and "triple" in doc["scope"]
                 and isinstance(doc["evidence_boundary"], str)
                 and "UNSAT" in doc["evidence_boundary"], "Missing scientific boundary")
    dt = datetime.fromisoformat(doc["observed_at_utc"])
    core.require(dt.tzinfo is not None, "UTC timestamp requires offset")
    records = doc["records"]
    core.require(isinstance(records, list) and bool(records), "No pilot attempts")
    seen = set()
    for record in records:
        core.require(isinstance(record, dict) and
                     set(record) == {"size", "status", "cnf_sha256", "variables",
                                     "clauses", "resource_cap_conflicts",
                                     "observed_conflicts", "solver_stats",
                                     "elapsed_seconds", "witness"},
                     "Malformed run record")
        k = record["size"]
        core.require(type(k) is int and 2 <= k <= 18 and k not in seen,
                     "Invalid or duplicate attempt size")
        seen.add(k)
        cnf = core.build(7, k)
        core.require(record["cnf_sha256"] == sha256(cnf.dimacs().encode("ascii")).hexdigest()
                     and record["variables"] == cnf.var_count
                     and record["clauses"] == len(cnf.clauses),
                     "CNF drift or tampering")
        cap = record["resource_cap_conflicts"]
        used = record["observed_conflicts"]
        core.require(type(cap) is int and cap > 0 and
                     type(used) is int and used >= 0 and
                     type(record["elapsed_seconds"]) in (float, int) and
                     record["elapsed_seconds"] >= 0, "Invalid recorded resources")
        stats = record["solver_stats"]
        core.require(isinstance(stats, dict) and stats.get("conflicts") == used
                     and all(type(v) is int and v >= 0 for v in stats.values()),
                     "Inconsistent solver counters")
        status = record["status"]
        core.require(status in {"sat_verified_witness", "unsat_solver_report_only",
                                "unknown_budget_exhausted"}, "Unsupported result class")
        if status == "unknown_budget_exhausted":
            core.require(used >= cap, "Unknown claimed before budget was exhausted")
        if status == "sat_verified_witness":
            witness = record["witness"]
            core.require(isinstance(witness, list) and witness, "SAT witness absent")
            members = []
            for item in witness:
                core.require(isinstance(item, dict) and set(item) == {"mask", "set"},
                             "Malformed witness member")
                core.require(item["mask"] == core.set_mask(item["set"], 7),
                             "Witness set/mask mismatch")
                members.append(item["mask"])
            core.independent_check(members, n=7, size=k)
            core.require(cnf.satisfies(cnf.extend(members)), "Witness fails encoded constraints")
        else:
            core.require(record["witness"] is None,
                         "Uncertified result cannot carry a validated witness")
    return {"checked_records": len(seen),
            "unknown": sum(r["status"] == "unknown_budget_exhausted" for r in records),
            "sat": sum(r["status"] == "sat_verified_witness" for r in records),
            "unsat_solver_only": sum(r["status"] == "unsat_solver_report_only" for r in records),
            "independent_unsat_proofs": 0}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sizes", default="18,17", help="comma-delimited exact family sizes 2..18")
    p.add_argument("--conflicts", type=int, default=200000)
    p.add_argument("--out", type=Path, help="optional local JSON report path")
    p.add_argument("--check-record", type=Path, help="offline verification of a recorded attempt")
    args = p.parse_args()
    if args.check_record:
        core.require(args.out is None, "Cannot mix --out and --check-record")
        verdict = validate_record(json.loads(args.check_record.read_text(encoding="utf-8")))
        print(json.dumps(verdict, sort_keys=True))
        return 0
    sizes = [int(k) for k in args.sizes.split(",")]
    result = pilot(sizes, args.conflicts)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print("Recorded " + str(args.out))
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
