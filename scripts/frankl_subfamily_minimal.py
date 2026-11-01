#!/usr/bin/env python3
"""Exact inclusion-minimality test for a particular triple-local Frankl falsifier.

Searches EVERY proper subfamily of the supplied union-closed family that
retains a designated triple, remains union-closed, and has all three triple
frequencies strictly below one half. DPLL explores the full Boolean space,
with sound closure and cardinality propagation. The claim is relative to the
given example, never a global minimum or a proof of Frankl's conjecture.
"""
import argparse
import json
from pathlib import Path


def check_family(sets, triple):
    if len(triple) != 3 or len(set(triple)) != 3:
        raise ValueError("Three distinct elements required")
    family = [frozenset(s) for s in sets]
    if len(set(family)) != len(family):
        raise ValueError("Duplicate family members")
    lookup = {s: i for i, s in enumerate(family)}
    if frozenset(triple) not in lookup:
        raise ValueError("Exact triple missing")
    if any(a | b not in lookup for a in family for b in family):
        raise ValueError("Source family not union-closed")
    if any(2 * sum(t in s for s in family) >= len(family) for t in triple):
        raise ValueError("Source does not violate triple-local abundance")
    return family, lookup


def search_proper(sets, triple):
    family, index = check_family(sets, triple)
    n = len(family)
    if n > 34:
        raise ValueError("Cost guard: at most 34 family members")
    clauses = sorted({
        (i, j, index[a | b])
        for i, a in enumerate(family) for j, b in enumerate(family)
        if i <= j and index[a | b] not in (i, j)
    })
    weights = [[2 * int(t in s) - 1 for s in family] for t in triple]
    degrees = [sum(i in c for c in clauses) for i in range(n)]
    counts = dict(nodes=0, failed_propagations=0, forced_absences=0)

    def propagate(a):
        changed = True
        while changed:
            changed = False
            for i, j, k in clauses:
                vi, vj, vk = a[i], a[j], a[k]
                requirements = []
                if vi == 1 and vj == 1:
                    requirements.append((k, 1))
                if vk == 0 and vi == 1:
                    requirements.append((j, 0))
                if vk == 0 and vj == 1:
                    requirements.append((i, 0))
                for p, val in requirements:
                    if a[p] == -1:
                        a[p] = val
                        changed = True
                    elif a[p] != val:
                        return False
            for co in weights:
                # For every member indicator x_i in {0,1}, enforce
                # sum_i (2*[t in F_i]-1)*x_i <= -1 for each triple element t.
                best = sum(c if v == 1 else (min(0, c) if v == -1 else 0)
                           for c, v in zip(co, a))
                if best > -1:
                    return False
                if best == -1:
                    for p, (c, v) in enumerate(zip(co, a)):
                        if v == -1:
                            a[p] = 0 if c > 0 else 1
                            changed = True
        return True

    def dfs(a):
        counts["nodes"] += 1
        if not propagate(a):
            counts["failed_propagations"] += 1
            return None
        undecided = [i for i, val in enumerate(a) if val == -1]
        if not undecided:
            selected = [family[i] for i, val in enumerate(a) if val == 1]
            if (all(s | t in selected for s in selected for t in selected)
                    and all(2 * sum(t in s for s in selected) < len(selected)
                            for t in triple)):
                return [i for i, val in enumerate(a) if val == 1]
            raise AssertionError("Propagated solution is not valid")
        idx = max(undecided, key=lambda i: (degrees[i], -i))
        for val in (0, 1):
            b = a.copy()
            b[idx] = val
            result = dfs(b)
            if result is not None:
                return result
        return None

    triple_index = index[frozenset(triple)]
    for absent in range(n):
        if absent == triple_index:
            continue
        counts["forced_absences"] += 1
        a = [-1] * n
        a[triple_index] = 1
        a[absent] = 0
        answer = dfs(a)
        if answer is not None:
            return {"family_size": n, "triple": list(triple),
                    "inclusion_minimal": False, "proper_subfamily_indices": answer,
                    "closure_clauses": len(clauses), **counts}
    return {"family_size": n, "triple": list(triple),
            "inclusion_minimal": True, "proper_subfamily_indices": None,
            "closure_clauses": len(clauses), **counts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--assert-minimal", action="store_true")
    args = parser.parse_args()
    try:
        obj = json.loads(args.certificate.read_text(encoding="utf-8"))
        result = search_proper(obj["sets"], obj["triple"])
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if args.assert_minimal and not result["inclusion_minimal"] else 0
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
