#!/usr/bin/env python3
"""Compact exact-outdegree CNF encoding for fixed Caccetta-Haggkvist cases.

A counterexample with minimum outdegree >=r has a spanning exact-r-outdegree
subgraph: delete surplus outgoing arcs. Deletion cannot create short cycles.
The exact-r formulation is therefore equisatisfiable with the min-r
counterexample formulation, though their raw satisfying assignments differ.

Prefix threshold gates impose exactly r outgoing arcs with linear-size CNF.
This script produces an encoding, not a SAT/UNSAT result or a proof.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


def parameters(n, r):
    if type(n) is not int or type(r) is not int or not (3 <= n <= 30 and 1 <= r < n):
        raise ValueError("require integers 3<=n<=30 and 1<=r<n")
    k = (n + r - 1) // r
    if k > 3:
        raise ValueError("exact encoder supports ceil(n/r)<=3")
    return k


def arc_variables(n):
    return {(u, v): 1 + u * (n - 1) + (v if v < u else v - 1)
            for u in range(n) for v in range(n) if v != u}


def neg(lit):
    return not lit if type(lit) is bool else -lit


class CompactCNF:
    def __init__(self, n, r):
        self.n, self.r = n, r
        self.bound = parameters(n, r)
        self.arc = arc_variables(n)
        self.next_var = n * (n - 1) + 1
        self.clauses = []
        self.prefixes = {}
        self.by_category = {"no_digons": 0, "no_triangles": 0, "exact_outdegree": 0}
        self._build()

    def add(self, category, *lits):
        cleaned, seen = [], set()
        for lit in lits:
            if lit is True:
                return
            if lit is False:
                continue
            if not isinstance(lit, int) or not lit:
                raise TypeError("nonzero integer or boolean literal required")
            if -lit in seen:
                return
            if lit not in seen:
                cleaned.append(lit)
                seen.add(lit)
        if not cleaned:
            raise ValueError("CNF contains an empty clause")
        self.clauses.append(tuple(cleaned))
        self.by_category[category] += 1

    def _degree(self, u):
        row = [self.arc[u, v] for v in range(self.n) if v != u]
        prefix = {}

        def threshold(i, j):
            if j == 0:
                return True
            if j > i:
                return False
            return prefix[i, j]

        for i, x in enumerate(row, 1):
            for j in range(1, min(i, self.r + 1) + 1):
                z = self.next_var
                self.next_var += 1
                prefix[i, j] = z
                a, b = threshold(i-1, j), threshold(i-1, j-1)
                # z <=> a OR (b AND x): four equivalence clauses.
                self.add("exact_outdegree", neg(a), z)
                self.add("exact_outdegree", neg(b), -x, z)
                self.add("exact_outdegree", -z, a, b)
                self.add("exact_outdegree", -z, a, x)
        self.add("exact_outdegree", threshold(len(row), self.r))
        self.add("exact_outdegree", neg(threshold(len(row), self.r + 1)))
        for (i, j), variable in prefix.items():
            self.prefixes[u, i, j] = variable

    def _build(self):
        n, x = self.n, self.arc
        for u, v in combinations(range(n), 2):
            self.add("no_digons", -x[u, v], -x[v, u])
        if self.bound >= 3:
            for u, v, w in combinations(range(n), 3):
                self.add("no_triangles", -x[u, v], -x[v, w], -x[w, u])
                self.add("no_triangles", -x[u, w], -x[w, v], -x[v, u])
        for u in range(n):
            self._degree(u)

    def assigned(self, arcs):
        """Unique threshold-variable completion for an arc assignment."""
        on = {tuple(e) for e in arcs}
        assignment = {v: (edge in on) for edge, v in self.arc.items()}
        for u in range(self.n):
            count = 0
            for i, v in enumerate((v for v in range(self.n) if v != u), 1):
                if (u, v) in on:
                    count += 1
                for j in range(1, min(i, self.r + 1) + 1):
                    assignment[self.prefixes[u, i, j]] = count >= j
        return assignment

    def holds(self, assignment):
        return all(any(assignment[abs(lit)] == (lit > 0) for lit in clause)
                   for clause in self.clauses)

    def output(self, stream):
        header = (f"c Svyable/100 independently generated exact-r CH encoding\n"
                  f"c n={self.n} r={self.r} forbidden_girth<={self.bound}\n"
                  f"p cnf {self.next_var-1} {len(self.clauses)}\n")
        digest = sha256()

        def write(data):
            b = data.encode("ascii")
            stream.write(b)
            digest.update(b)

        write(header)
        for clause in self.clauses:
            write(" ".join(map(str, clause)) + " 0\n")
        return {"n": self.n, "r": self.r, "variables": self.next_var - 1,
                "arc_variables": self.n*(self.n-1),
                "auxiliary_variables": self.next_var-1-self.n*(self.n-1),
                "clauses": len(self.clauses), "by_category": self.by_category,
                "sha256": digest.hexdigest(),
                "status": "CNF ONLY; NO SAT/UNSAT PROOF"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--r", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        cnf = CompactCNF(args.n, args.r)
        with args.output.open("wb") as stream:
            meta = cnf.output(stream)
        meta["bytes"] = args.output.stat().st_size
        print(json.dumps(meta, indent=2, sort_keys=True))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
