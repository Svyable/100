#!/usr/bin/env python3
"""Proof-aware SAT encoding for fixed Caccetta-Haggkvist challenges.

Arc variable x(u,v) means u -> v. SAT assignments correspond EXACTLY to
loopless oriented digraphs with minimum outdegree >= r and no directed
cycle of length <= ceil(n/r), for supported k<=3. A 2-cycle always already
satisfies the CH bound, so forbidding them loses no counterexamples.
UNSAT solver output is not a proof without independent certificate checking.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path

from digraph import check as independent_check


def parameters(n, r):
    if type(n) is not int or type(r) is not int or not (
        3 <= n <= 30 and 1 <= r < n
    ):
        raise ValueError("require integers 3<=n<=30 and 1<=r<n")
    k = (n + r - 1) // r
    if k > 3:
        raise ValueError("exact encoder currently supports ceil(n/r)<=3")
    return k


def variables(n):
    return {
        (u, v): 1 + u*(n-1) + (v if v < u else v-1)
        for u in range(n) for v in range(n) if u != v
    }


def clauses(n, r):
    k = parameters(n, r)
    x = variables(n)
    for u, v in combinations(range(n), 2):
        yield (-x[u, v], -x[v, u])
    if k >= 3:
        for u, v, w in combinations(range(n), 3):
            yield (-x[u, v], -x[v, w], -x[w, u])
            yield (-x[u, w], -x[w, v], -x[v, u])
    # Outdegree >= r iff every (n-r)-subset of the other vertices
    # contains at least one outgoing neighbor.
    for u in range(n):
        adjacent = [v for v in range(n) if v != u]
        for subset in combinations(adjacent, n-r):
            yield tuple(x[u, v] for v in subset)


def formula_counts(n, r):
    k = parameters(n, r)
    return {
        "variables": n*(n-1),
        "no_2cycles": comb(n, 2),
        "no_3cycles": 2*comb(n, 3) if k >= 3 else 0,
        "min_degree": n*comb(n-1, n-r),
        "max_forbidden_girth": k,
    }


def encode(n, r, output):
    counts = formula_counts(n, r)
    nclauses = sum(counts[key] for key in
                   ("no_2cycles", "no_3cycles", "min_degree"))
    if nclauses > 500_000:
        raise ValueError("CNF exceeds 500000 clauses; narrow the instance")
    hasher = sha256()
    written = 0

    def write(line):
        nonlocal written
        data = line.encode("ascii")
        output.write(data)
        hasher.update(data)
        written += len(data)

    write("c Svyable/100 fixed-parameter CH counterexample search\n")
    write("c directed arc x_uv is true iff u -> v; all pairs forbid 2-cycles\n")
    write(f"c n={n} r={r} forbid cycles length <= {counts['max_forbidden_girth']}\n")
    write(f"p cnf {counts['variables']} {nclauses}\n")
    actual = 0
    for clause in clauses(n, r):
        write(" ".join(map(str, clause)) + " 0\n")
        actual += 1
    if actual != nclauses:
        raise AssertionError("Clause-count mismatch")
    return {
        "n": n, "r": r, "clauses": actual, "bytes": written,
        "sha256": hasher.hexdigest(), **counts,
        "meaning": "SAT = fixed CH counterexample; UNSAT needs certified proof"
    }


def verify_arcs(n, r, arcs):
    parameters(n, r)
    result = independent_check(n, arcs, r)
    arc_set = {tuple(arc) for arc in arcs}
    two_cycle = any((v, u) in arc_set for u, v in arc_set)
    return {
        **result, "oriented": not two_cycle,
        "is_valid_sat_witness": bool(result["counterexample"] and not two_cycle)
    }


def assignment_satisfies(n, r, arcs):
    """Slow reference clause evaluator for exhaustive small-case testing."""
    x = variables(n)
    on = {x[u, v] for u, v in arcs}
    return all(any((lit > 0 and lit in on) or
                   (lit < 0 and -lit not in on) for lit in clause)
               for clause in clauses(n, r))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    cnf = sub.add_parser("cnf")
    cnf.add_argument("--n", type=int, required=True)
    cnf.add_argument("--r", type=int, required=True)
    cnf.add_argument("--output", type=Path, required=True)
    check = sub.add_parser("check")
    check.add_argument("--n", type=int, required=True)
    check.add_argument("--r", type=int, required=True)
    check.add_argument("--arcs", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "cnf":
            parameters(args.n, args.r)
            with args.output.open("wb") as output:
                result = encode(args.n, args.r, output)
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            arcs = json.loads(args.arcs.read_text(encoding="utf-8"))["arcs"]
            result = verify_arcs(args.n, args.r, arcs)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["is_valid_sat_witness"] else 1
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
