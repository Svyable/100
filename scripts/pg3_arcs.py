#!/usr/bin/env python3
"""Exact PG(3,q) 4-arc frame-extension replay, q <= 9 (prime powers).

A 4-arc is a set of projective points for which every four vectors form a
basis. This is a known finite MDS reproduction, not a new theorem.
"""
from __future__ import annotations

import argparse
import itertools
import json
from functools import lru_cache

# Monic irreducible polynomials, constant coefficient first.
FIELDS = {
    2: (2, (0, 1)), 3: (3, (0, 1)), 4: (2, (1, 1, 1)),
    5: (5, (0, 1)), 7: (7, (0, 1)), 8: (2, (1, 1, 0, 1)),
    9: (3, (1, 0, 1)),
}


class Field:
    def __init__(self, q):
        if q not in FIELDS:
            raise ValueError("supported q: 2,3,4,5,7,8,9")
        self.q = q
        self.p, self.poly = FIELDS[q]
        self.m = len(self.poly) - 1
        self.add = [[self._add(a, b) for b in range(q)] for a in range(q)]
        self.neg = [next(b for b in range(q) if self.add[a][b] == 0)
                    for a in range(q)]
        self.mul = [[self._mul(a, b) for b in range(q)] for a in range(q)]
        self.inv = [0] + [
            next(b for b in range(1, q) if self.mul[a][b] == 1)
            for a in range(1, q)
        ]

    def digits(self, x):
        return [(x // self.p**i) % self.p for i in range(self.m)]

    def _add(self, a, b):
        return sum(((x + y) % self.p) * self.p**i
                   for i, (x, y) in enumerate(zip(self.digits(a), self.digits(b))))

    def _mul(self, a, b):
        ac, bc = self.digits(a), self.digits(b)
        cs = [0] * (2 * self.m - 1)
        for i, x in enumerate(ac):
            for j, y in enumerate(bc):
                cs[i+j] = (cs[i+j] + x*y) % self.p
        for k in range(len(cs)-1, self.m-1, -1):
            lead = cs[k]
            for j in range(self.m):
                cs[k-self.m+j] = (cs[k-self.m+j] - lead*self.poly[j]) % self.p
        return sum(cs[i]*self.p**i for i in range(self.m))

    def determinant(self, rows):
        if len(rows) != 4 or any(len(r) != 4 for r in rows):
            raise ValueError("expected 4x4")
        a = [list(r) for r in rows]
        result = 1
        for col in range(4):
            pivot = next((i for i in range(col, 4) if a[i][col]), None)
            if pivot is None:
                return 0
            if pivot != col:
                a[col], a[pivot] = a[pivot], a[col]
                result = self.mul[result][self.neg[1]]
            d = a[col][col]
            result = self.mul[result][d]
            inv = self.inv[d]
            for i in range(col+1, 4):
                factor = self.mul[a[i][col]][inv]
                for j in range(col, 4):
                    a[i][j] = self.add[a[i][j]][
                        self.neg[self.mul[factor][a[col][j]]]]
        return result

    def determinant_permutation(self, rows):
        """Independent Leibniz formula; no Gaussian elimination."""
        total = 0
        for perm in itertools.permutations(range(4)):
            term = 1
            for i, j in enumerate(perm):
                term = self.mul[term][rows[i][j]]
            parity = sum(perm[i] > perm[j] for i in range(4)
                         for j in range(i+1, 4)) % 2
            total = self.add[total][self.neg[term] if parity else term]
        return total


FRAME = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0),
         (0, 0, 0, 1), (1, 1, 1, 1))


def is_arc(field, points, checker="elimination"):
    det = (field.determinant if checker == "elimination"
           else field.determinant_permutation)
    return all(det(rows) != 0 for rows in itertools.combinations(points, 4))


def candidates(field):
    # Normalize first coordinate to 1. All four must be distinct and nonzero.
    return [(1, *t) for t in itertools.permutations(range(2, field.q), 3)]


def moment_curve(field):
    mul = field.mul
    return [(1, t, mul[t][t], mul[mul[t][t]][t])
            for t in range(field.q)] + [(0, 0, 0, 1)]


def search(field, target_extras, max_nodes=None):
    """Exhaust frame-normalized extensions; a resource cutoff returns UNKNOWN."""
    cs = candidates(field)
    nodes = 0
    witness = None
    cutoff = False
    assert is_arc(field, FRAME)
    assert all(is_arc(field, FRAME+(c,)) for c in cs)

    @lru_cache(None)
    def compatible(indices):
        k = len(indices)
        rows = tuple(cs[i] for i in indices)
        return all(field.determinant(fr + rows) != 0
                   for fr in itertools.combinations(FRAME, 4-k))

    def dfs(indices, start):
        nonlocal nodes, witness, cutoff
        if len(indices) == target_extras:
            witness = FRAME + tuple(cs[i] for i in indices)
            return True
        for i in range(start, len(cs)):
            nodes += 1
            if max_nodes is not None and nodes > max_nodes:
                cutoff = True
                return False
            if not compatible((i,)):
                continue
            if any(not compatible((j, i)) for j in indices):
                continue
            if any(not compatible((j, k, i))
                   for j, k in itertools.combinations(indices, 2)):
                continue
            if any(not compatible((j, k, l, i))
                   for j, k, l in itertools.combinations(indices, 3)):
                continue
            if dfs(indices+(i,), i+1):
                return True
            if cutoff:
                return False
        return False

    dfs((), 0)
    return {
        "q": field.q, "target_size": 5+target_extras,
        "status": "UNKNOWN" if cutoff else ("SAT" if witness else "UNSAT"),
        "visited_nodes": nodes, "candidate_count": len(cs),
        "witness": witness,
    }


def run(q, max_nodes=None):
    field = Field(q)
    curve = moment_curve(field)
    if q >= 4 and not is_arc(field, curve):
        raise AssertionError("normal rational curve fails determinant test")
    lower = max(5, len(curve))
    positive = search(field, lower-5, max_nodes)
    if positive["status"] != "SAT":
        raise AssertionError("lower-bound frame search did not find a witness")
    negative = search(field, lower-4, max_nodes)
    if positive["witness"] is None or not is_arc(
            field, positive["witness"], checker="permutation"):
        raise AssertionError("independent witness check failed")
    return {
        "q": q, "lower_bound": lower,
        "lower_search_nodes": positive["visited_nodes"],
        "upper_target": lower+1,
        "upper_status": negative["status"],
        "upper_search_nodes": negative["visited_nodes"],
        "candidate_count": negative["candidate_count"],
        "witness": positive["witness"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, nargs="+", default=sorted(FIELDS))
    parser.add_argument("--max-nodes", type=int)
    args = parser.parse_args()
    print(json.dumps([run(q, args.max_nodes) for q in args.q],
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
