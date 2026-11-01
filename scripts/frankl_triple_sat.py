#!/usr/bin/env python3
"""Exact fixed-universe SAT encoding of a *triple-local* Frankl strengthening.

Only the finite seven-element optimization of issue #95 is investigated here.
A SAT model is independently checked as a concrete counterexample to the
triple-local strengthening. An UNSAT solver verdict is NOT a proof; a checked
proof trace covering EVERY cardinality k=2..18 is required for a lower bound.

    python3 scripts/frankl_triple_sat.py --size 18 --out /tmp/triple18.cnf
    python3 scripts/frankl_triple_sat.py --check-witness examples/FRANKL_VAN_DER_HOUT_ROOS_19.json
    python3 scripts/frankl_triple_sat.py --size 18 --verify-model /tmp/solver-model.txt
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys


def neg(lit):
    if type(lit) is bool:
        return not lit
    return -lit


def require(condition, message):
    if not condition:
        raise ValueError(message)


def set_mask(elements, n):
    require(isinstance(elements, list), "Set must be a list")
    out = 0
    for e in elements:
        require(type(e) is int and 0 <= e < n, "Element outside universe")
        require(not out & (1 << e), "Repeated set element")
        out |= 1 << e
    return out


def independent_check(members, n=7, triple=(0, 1, 2), size=None):
    """An independent definition-level checker: no CNF auxiliary state is used."""
    require(type(n) is int and 3 <= n <= 8, "Universe must have 3..8 elements")
    require(len(triple) == 3 and len(set(triple)) == 3
            and all(type(t) is int and 0 <= t < n for t in triple),
            "Three distinct in-universe elements required")
    require(isinstance(members, (list, set, tuple)), "Members must be a collection")
    require(all(type(s) is int and 0 <= s < 1 << n for s in members),
            "Out-of-range or non-integer member")
    chosen = set(members)
    require(len(chosen) == len(members), "Duplicate family member")
    require(size is None or len(chosen) == size, "Family size does not match")
    tmask = sum(1 << i for i in triple)
    require(0 in chosen and tmask in chosen, "Empty set and exact triple are mandatory")
    for a in chosen:
        for b in chosen:
            require((a | b) in chosen, f"Not union-closed: {a} | {b} = {a|b}")
    frequencies = {t: sum(bool(s & (1 << t)) for s in chosen) for t in triple}
    require(all(2 * f < len(chosen) for f in frequencies.values()),
            "Triple does not fail the strict half-bound")
    return {"members": len(chosen), "frequencies": frequencies, "triple": list(triple),
            "universe": n, "scope": "triple-local failure, NOT a Frankl counterexample"}


class CNF:
    """Definitional prefix count encodings with an exact canonical extension."""
    def __init__(self, base_vars):
        self.base_vars = base_vars
        self.var_count = base_vars
        self.clauses = []
        self.definitions = []  # (aux, a, x, b): aux <=> a OR (x AND b)

    def new(self):
        self.var_count += 1
        return self.var_count

    def clause(self, *lits):
        seen = set()
        for lit in lits:
            if lit is True:
                return
            if lit is False:
                continue
            require(type(lit) is int and lit != 0 and abs(lit) <= self.var_count,
                    "Invalid literal")
            if -lit in seen:
                return
            seen.add(lit)
        self.clauses.append(sorted(seen, key=lambda v: (abs(v), v < 0)))

    def or_and(self, a, x, b):
        """z iff (a or (x and b)); four standard Tseitin implications."""
        z = self.new()
        self.clause(neg(a), z)
        self.clause(neg(x), neg(b), z)
        self.clause(neg(z), a, x)
        self.clause(neg(z), a, b)
        self.definitions.append((z, a, x, b))
        return z

    def prefix_ge(self, literals, limit):
        """Threshold booleans for total selected >= j, 1 <= j <= limit.

        State recurrence on prefix i:
          ge(i,j) <=> ge(i-1,j) OR (x_i AND ge(i-1,j-1)).
        Boundary ge(0,0)=true, ge(0,j>0)=false.
        """
        require(0 <= limit <= len(literals) + 1, "Invalid counter limit")
        prev = {}
        for i, x in enumerate(literals, 1):
            curr = {}
            for j in range(1, min(i, limit) + 1):
                a = prev.get(j, False)
                b = True if j == 1 else prev.get(j - 1, False)
                curr[j] = self.or_and(a, x, b)
            prev = curr
        return prev

    def extend(self, selected_masks):
        """Unique constructive assignment of all auxiliary counter variables."""
        values = [False] * (self.var_count + 1)
        selected = set(selected_masks)
        for i in range(self.base_vars):
            values[i + 1] = i in selected

        def value(lit):
            return lit if type(lit) is bool else values[lit]

        for z, a, x, b in self.definitions:
            values[z] = value(a) or (value(x) and value(b))
        return values

    def satisfies(self, values):
        require(len(values) == self.var_count + 1, "Model length mismatch")
        return all(any(values[abs(l)] if l > 0 else not values[-l]
                       for l in clause) for clause in self.clauses)

    def dimacs(self):
        return (f"c triple-local n encoded as subset variables 1..{self.base_vars}\n"
                f"c literal s+1 means subset bitmask s is in the family\n"
                f"p cnf {self.var_count} {len(self.clauses)}\n"
                + "".join(" ".join(map(str, c)) + " 0\n" for c in self.clauses))


def build(n=7, size=18, triple=(0, 1, 2)):
    """One EXACT-size decision instance. Need all sizes 2..18 for optimality."""
    require(type(n) is int and 3 <= n <= 8, "Universe must have 3..8 elements")
    require(type(size) is int and 2 <= size <= (1 << n),
            "Invalid exact family size")
    require(len(triple) == 3 and len(set(triple)) == 3
            and all(type(t) is int and 0 <= t < n for t in triple),
            "Invalid triple")
    total = 1 << n
    cnf = CNF(total)
    triple_mask = sum(1 << t for t in triple)
    cnf.clause(1)  # include empty set
    cnf.clause(triple_mask + 1)  # include exactly the designated triple
    for a in range(total):
        for b in range(a + 1, total):
            u = a | b
            if u not in (a, b):
                cnf.clause(-(a + 1), -(b + 1), u + 1)
    counts = cnf.prefix_ge(range(1, total + 1), size + 1)
    cnf.clause(counts.get(size, False))
    cnf.clause(neg(counts.get(size + 1, False)))
    max_freq = (size - 1) // 2
    for t in triple:
        chosen_with_t = [m + 1 for m in range(total) if m & (1 << t)]
        c = cnf.prefix_ge(chosen_with_t, max_freq + 1)
        cnf.clause(neg(c.get(max_freq + 1, False)))
    return cnf


def parse_solver_model(text, cnf):
    """Validate SAT-model syntax and then reject any invalid actual family."""
    status = [line.split(maxsplit=1)[1].strip().upper()
              for line in text.splitlines() if line.startswith("s ")]
    require(status and all(x in ("SATISFIABLE", "SAT") for x in status),
            "Need an explicit SATISFIABLE line; UNSAT is not proof")
    literals = []
    for line in text.splitlines():
        if line.startswith("v "):
            for word in line.split()[1:]:
                v = int(word)
                if v:
                    require(abs(v) <= cnf.var_count, "Model literal out of range")
                    literals.append(v)
    require(bool(literals), "No signed model literals supplied")
    observations = {}
    for lit in literals:
        var, val = abs(lit), lit > 0
        require(var not in observations or observations[var] == val,
                "Contradictory model literals")
        observations[var] = val
    require(all(i in observations for i in range(1, cnf.base_vars + 1)),
            "SAT output omits a subset membership variable")
    selected = [i - 1 for i in range(1, cnf.base_vars + 1) if observations[i]]
    canonical = cnf.extend(selected)
    require(cnf.satisfies(canonical), "SAT output does not satisfy generated CNF")
    require(all(canonical[i] == truth for i, truth in observations.items()),
            "Reported auxiliary literals contradict the cardinality definitions")
    return selected


def run(args):
    if args.check_witness:
        obj = json.loads(Path(args.check_witness).read_text(encoding="utf-8"))
        n = obj["n"]
        members = [set_mask(s, n) for s in obj["sets"]]
        print(json.dumps(independent_check(members, n=n, triple=tuple(obj["triple"])),
                         indent=2, sort_keys=True))
        return 0

    cnf = build(n=args.universe, size=args.size)
    if args.verify_model:
        selected = parse_solver_model(Path(args.verify_model).read_text(), cnf)
        verdict = independent_check(selected, n=args.universe, size=args.size)
        verdict["selected_bitmasks"] = sorted(selected)
        print(json.dumps(verdict, indent=2, sort_keys=True))
    elif args.out:
        data = cnf.dimacs().encode("ascii")
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        print(json.dumps({"cnf": str(target), "sha256": sha256(data).hexdigest(),
                          "variables": cnf.var_count, "clauses": len(cnf.clauses),
                          "size": args.size, "universe": args.universe,
                          "note": "Only one exact size; UNSAT needs independent proof trace"}))
    else:
        print(json.dumps({"size": args.size, "variables": cnf.var_count,
                          "clauses": len(cnf.clauses), "universe": args.universe,
                          "note": "No solver run; no mathematical conclusion"}))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--universe", type=int, default=7)
    parser.add_argument("--size", type=int, default=18)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--verify-model", type=Path)
    parser.add_argument("--check-witness", type=Path)
    args = parser.parse_args()
    require(not (args.check_witness and (args.out or args.verify_model))
            and not (args.out and args.verify_model), "Choose one operation")
    return run(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
