#!/usr/bin/env python3
"""Proof-carrying capped Frankl triple-local search, fixed ground set.

One CNF covers EVERY family cardinality 2..cap, unlike independent size
pilots. When cap=18, n=7 and T=(0,1,2), a refutation plus the published
19-member witness would establish a sharp restricted *finite* theorem.
The CNF includes six sound implied clauses: no proper nonempty subset
of a strictly rare triple can be present (singleton/pair injection).

    python3 scripts/frankl_triple_capped.py --cap 18 --out /tmp/capped18.cnf
    python3 scripts/frankl_triple_capped.py --cap 19 --positive-control
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

from frankl_triple_sat import CNF, independent_check, neg, require, set_mask

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/FRANKL_VAN_DER_HOUT_ROOS_19.json"


class CappedCNF(CNF):
    """Selectors are uniquely determined by the family size."""

    def __init__(self, base_vars):
        super().__init__(base_vars)
        self.selectors = {}

    def extend(self, selected_masks):
        values = super().extend(selected_masks)
        k = len(selected_masks)
        for size, selector in self.selectors.items():
            values[selector] = k == size
        return values


def build_capped(n=7, cap=18, triple=(0, 1, 2)):
    """Exact union-closed rare-triple families, size between 2 and cap."""
    require(type(n) is int and 3 <= n <= 8, "Universe must have 3..8 elements")
    require(type(cap) is int and 2 <= cap <= (1 << n),
            "Cap must be in 2..2**n")
    require(isinstance(triple, (tuple, list)) and len(triple) == 3
            and len(set(triple)) == 3
            and all(type(t) is int and 0 <= t < n for t in triple),
            "Invalid triple")
    total = 1 << n
    cnf = CappedCNF(total)
    tmask = sum(1 << t for t in triple)

    cnf.clause(1)  # include the empty set
    cnf.clause(tmask + 1)
    for a in range(total):
        for b in range(a + 1, total):
            u = a | b
            if u not in (a, b):
                cnf.clause(-(a + 1), -(b + 1), u + 1)

    # SOUND derived clauses. If a singleton {t} is in F, t is abundant:
    # S without t -> S union {t} is an injective map to sets with t.
    # If {a,b} is in F, D (neither) injects into B (both) by union:
    # f(a)+f(b)-|F| = |B|-|D| >= 0. This contradicts both rare.
    for mask in range(1, 1 << len(triple)):
        if mask == (1 << len(triple)) - 1:
            continue
        subset = sum(1 << triple[i] for i in range(3) if mask & (1 << i))
        cnf.clause(-(subset + 1))

    counts = cnf.prefix_ge(range(1, total + 1), cap + 1)
    per_element = {
        t: cnf.prefix_ge(
            [s + 1 for s in range(total) if s & (1 << t)],
            (cap + 1) // 2
        )
        for t in triple
    }

    for size in range(2, cap + 1):
        selector = cnf.new()
        cnf.selectors[size] = selector
        cnf.clause(-selector, counts[size])
        cnf.clause(-selector, neg(counts.get(size + 1, False)))
        for t in triple:
            cutoff = (size - 1) // 2 + 1
            cnf.clause(-selector, neg(per_element[t][cutoff]))
    cnf.clause(*cnf.selectors.values())
    return cnf


def verify_positive_control(cap=19):
    obj = json.loads(FIXTURE.read_text(encoding="utf-8"))
    members = [set_mask(elements, obj["n"]) for elements in obj["sets"]]
    result = independent_check(members, n=7, triple=(0, 1, 2), size=19)
    cnf = build_capped(7, cap, (0, 1, 2))
    satisfies = cnf.satisfies(cnf.extend(members))
    require(satisfies == (cap >= 19), "Published witness failed capped encoding")
    return {"fixture_members": result["members"], "frequencies": result["frequencies"],
            "cap": cap, "satisfies": satisfies,
            "interpretation": "Published triple-local witness; not Frankl counterexample"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--universe", type=int, default=7)
    parser.add_argument("--cap", type=int, default=18)
    parser.add_argument("--out", type=Path, help="write an exact, deterministic DIMACS input")
    parser.add_argument("--positive-control", action="store_true")
    args = parser.parse_args()
    if args.positive_control:
        require(args.out is None and args.universe == 7,
                "Positive control requires n=7, no output path")
        print(json.dumps(verify_positive_control(args.cap), indent=2, sort_keys=True))
        return
    cnf = build_capped(n=args.universe, cap=args.cap)
    data = cnf.dimacs().encode("ascii")
    result = {
        "scope": f"n={args.universe}, T=0,1,2, exact cardinalities 2..{args.cap}",
        "variables": cnf.var_count,
        "clauses": len(cnf.clauses),
        "sha256": sha256(data).hexdigest(),
        "math_claim": "Unsolved by generating this input; needs independently checked UNSAT certificate",
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(data)
        result["file"] = str(args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
