#!/usr/bin/env python3
"""Certified structural reduction for the CH (n=18, r=6) search.

Mathematical proof (not solver assumptions): research/M074_REGULARITY.md.
Every hypothetical counterexample has an exact-6-outdegree subgraph; a
six-vertex counting lemma then forces indegree exactly 6 at every vertex.
By relabeling the root, its outgoing, incoming, and nonadjacent sets can be
fixed to [1..6], [7..12], [13..17], respectively. All extra constraints are
therefore equisatisfiable with the base counterexample search, not with
individual arc assignments. No SAT or UNSAT result is implied.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from ch_compact import CompactCNF, neg


class RegularCNF(CompactCNF):
    """18-vertex exact indegree/outdegree-6 encoding with optional root pin."""

    def __init__(self, fix_root=True):
        if type(fix_root) is not bool:
            raise TypeError("fix_root must be boolean")
        self.fix_root = fix_root
        super().__init__(18, 6)
        self.by_category.update(exact_indegree=0, root_symmetry=0)
        self.in_prefixes = {}
        for v in range(self.n):
            self._in_degree(v)
        if fix_root:
            self._fix_root()

    def _in_degree(self, v):
        row = [self.arc[u, v] for u in range(self.n) if u != v]
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
                a, b = threshold(i - 1, j), threshold(i - 1, j - 1)
                # z <=> a OR (b AND x), identical sound cardinality gate.
                self.add("exact_indegree", neg(a), z)
                self.add("exact_indegree", neg(b), -x, z)
                self.add("exact_indegree", -z, a, b)
                self.add("exact_indegree", -z, a, x)
        self.add("exact_indegree", threshold(len(row), self.r))
        self.add("exact_indegree", neg(threshold(len(row), self.r + 1)))
        for (i, j), variable in prefix.items():
            self.in_prefixes[v, i, j] = variable

    def _fix_root(self):
        for v in range(1, 18):
            self.add("root_symmetry", self.arc[0, v] if v <= 6 else -self.arc[0, v])
            self.add("root_symmetry", self.arc[v, 0] if 7 <= v <= 12 else -self.arc[v, 0])

    def assigned(self, arcs):
        """Unique prefix-variable completion for *any* arc assignment."""
        assignment = super().assigned(arcs)
        on = {tuple(edge) for edge in arcs}
        for v in range(self.n):
            count = 0
            for i, u in enumerate((u for u in range(self.n) if u != v), 1):
                if (u, v) in on:
                    count += 1
                for j in range(1, min(i, self.r + 1) + 1):
                    assignment[self.in_prefixes[v, i, j]] = count >= j
        return assignment

    def output(self, stream):
        header = ("c CH n=18 r=6: exact in/out degree 6, no digons/triangles\n"
                  f"c root symmetry pinned={int(self.fix_root)}; see research/M074_REGULARITY.md\n"
                  f"p cnf {self.next_var - 1} {len(self.clauses)}\n")
        digest = sha256()
        size = 0

        def write(line):
            nonlocal size
            data = line.encode("ascii")
            stream.write(data)
            digest.update(data)
            size += len(data)

        write(header)
        for clause in self.clauses:
            write(" ".join(map(str, clause)) + " 0\n")
        return {
            "n": self.n, "r": self.r, "variables": self.next_var - 1,
            "arc_variables": self.n * (self.n - 1),
            "auxiliary_variables": self.next_var - 1 - self.n * (self.n - 1),
            "clauses": len(self.clauses), "bytes": size,
            "by_category": self.by_category, "root_pinned": self.fix_root,
            "sha256": digest.hexdigest(),
            "status": "CNF ONLY; NO SAT/UNSAT PROOF",
        }


def relabel_root(arcs, root=0):
    """Construct the canonical root labels for a 6-in/6-out vertex.

    This preserves orientations, 2/3-cycles and every vertex degree. It
    does not assert that the input is a CH counterexample.
    """
    edges = {tuple(edge) for edge in arcs}
    if not isinstance(root, int) or not 0 <= root < 18:
        raise ValueError("root must be a vertex in range(18)")
    if any(len(e) != 2 or e[0] == e[1] or not all(isinstance(x, int) and 0 <= x < 18 for x in e) for e in edges):
        raise ValueError("expected loopless arcs on vertices 0..17")
    outgoing = sorted(v for (u, v) in edges if u == root)
    incoming = sorted(u for (u, v) in edges if v == root)
    if len(outgoing) != 6 or len(incoming) != 6 or set(outgoing) & set(incoming):
        raise ValueError("root needs six disjoint outgoing and incoming neighbors")
    other = sorted(set(range(18)) - {root} - set(outgoing) - set(incoming))
    order = [root, *outgoing, *incoming, *other]
    mapping = {old: new for new, old in enumerate(order)}
    return sorted((mapping[u], mapping[v]) for (u, v) in edges), mapping


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--no-root-symmetry", action="store_true")
    args = parser.parse_args()
    formula = RegularCNF(fix_root=not args.no_root_symmetry)
    with args.output.open("wb") as stream:
        result = formula.output(stream)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
