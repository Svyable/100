#!/usr/bin/env python3
"""Check the five LRAT certificates for the nine-vertex three-low lemma.

The checker uses only the Python standard library. Proof generation requires
python-sat/CaDiCaL and drat-trim; neither is trusted by this checker. The
mathematical statement is local to nine vertices and remains unreviewed.
"""

import argparse
import gzip
import hashlib
import json
from itertools import combinations
from pathlib import Path

ROOT = (Path(__file__).resolve().parents[1] / "data" / "certificates"
        / "m074_nine_three")

# (outneighbors of vertex 0, outneighbors of vertex 1).
CASES = {
    "edge_overlap": ((1, 2), (2, 3)),
    "edge_disjoint": ((1, 2), (3, 4)),
    "nonedge_overlap2": ((2, 3), (2, 3)),
    "nonedge_overlap1": ((2, 3), (2, 4)),
    "nonedge_overlap0": ((2, 3), (4, 5)),
}

CERT_SHA256 = {
    "zero_low": "28d50503d132c35ba3fb9838b59878e71608cd8cabe3dab297401432dc185297",
    "one_low": "3ca89fb64b7d7c58db0ad880974bbcd37ec147eae85ce0901aa6089f5ee59266",
    "edge_overlap": "afe58e66898367ec50ccfac5b92809f7a2a1dfdb8e8c755c0806ba9f8a212253",
    "edge_disjoint": "247e9291579e3c2fee0c57a407e84c44c85672e6a4a6e586ca6c3f12a646ceab",
    "nonedge_overlap2": "8c48d66c220a017857949fe87b43bffdc8466967352bac2c154b2b4b9338ae00",
    "nonedge_overlap1": "50bacf62c68f66220264ed125cff6d1d43ea4f04d7959e88fb21cb2093846fae",
    "nonedge_overlap0": "abb1b30a23e2a9377c20bdfdfbe4a85d8826bf435b0fb4601c119ace602c398e",
}

WITNESS = (
    (6, 7), (0, 3), (1, 8), (0, 6, 7), (1, 5, 8),
    (1, 2, 8), (2, 4, 5), (2, 4, 5), (0, 1, 3),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def var(i, j):
    """Map one of the 72 ordered nonloop arcs to a 1-based DIMACS variable."""
    require(0 <= i < 9 and 0 <= j < 9 and i != j, "invalid arc")
    return 8 * i + (j if j < i else j - 1) + 1


def formula(case):
    """Direct, auxiliary-free CNF for a normalized zero/one/two-low case."""
    if case in ("zero_low", "one_low"):
        return formula_fewer_low(case)
    a, b = CASES[case]
    clauses = []
    for i, j in combinations(range(9), 2):
        clauses.append((-var(i, j), -var(j, i)))
    for i, j, k in combinations(range(9), 3):
        clauses.append((-var(i, j), -var(j, k), -var(k, i)))
        clauses.append((-var(i, k), -var(k, j), -var(j, i)))
    for i in range(9):
        outgoing = [var(i, j) for j in range(9) if i != j]
        # At least two (i=0,1) or three (i>=2) of eight outgoing arcs.
        clauses.extend(combinations(outgoing, 7 if i < 2 else 6))
        if i < 2:
            # At most two outgoing arcs: no three may all be selected.
            clauses.extend(tuple(-x for x in subset)
                           for subset in combinations(outgoing, 3))
    for i, neighbors in ((0, a), (1, b)):
        for j in range(9):
            if i != j:
                clauses.append((var(i, j) if j in neighbors else -var(i, j),))
    return clauses


def formula_fewer_low(case):
    """Exclude zero or one degree-two vertex, with vertex-0 normalization.

    For zero lows, a minimum-outdegree-three graph can have vertex 0
    trimmed to exactly three arcs without introducing a triangle.
    For one low, vertex 0 has exactly two arcs by hypothesis.
    """
    low = case == "one_low"
    clauses = []
    for i, j in combinations(range(9), 2):
        clauses.append((-var(i, j), -var(j, i)))
    for i, j, k in combinations(range(9), 3):
        clauses.append((-var(i, j), -var(j, k), -var(k, i)))
        clauses.append((-var(i, k), -var(k, j), -var(j, i)))
    for i in range(9):
        outgoing = [var(i, j) for j in range(9) if i != j]
        clauses.extend(combinations(outgoing, 7 if low and i == 0 else 6))
        if low and i == 0:
            clauses.extend(tuple(-x for x in subset)
                           for subset in combinations(outgoing, 3))
    neighbors = (1, 2) if low else (1, 2, 3)
    for j in range(1, 9):
        clauses.append((var(0, j) if j in neighbors else -var(0, j),))
    return clauses


def dimacs(clauses):
    return (f"p cnf 72 {len(clauses)}\n"
            + "\n".join(" ".join(map(str, c)) + " 0" for c in clauses)
            + "\n")


def check_lrat(clauses, path):
    """Replay each LRAT RUP addition with the specified unit-propagation hints.

    No RAT steps occur in these five trimmed traces. Deletion steps update
    the live clause database. An empty derived clause certifies UNSAT.
    """
    active = {i + 1: tuple(c) for i, c in enumerate(clauses)}
    added = deleted = 0
    last = len(clauses)
    final = False
    with gzip.open(path, "rt", encoding="ascii") as stream:
        for line in stream:
            words = line.split()
            require(len(words) >= 3, "short LRAT line")
            cid = int(words[0])
            if words[1] == "d":
                ids = list(map(int, words[2:]))
                require(ids[-1] == 0, "unterminated deletion")
                for old in ids[:-1]:
                    require(old in active, f"unknown deleted clause {old}")
                    del active[old]
                    deleted += 1
                continue
            require(cid > last and not final, "out-of-order LRAT addition")
            last = cid
            parts = list(map(int, words))
            cut = parts.index(0, 1)
            new = tuple(parts[1:cut])
            require(parts[-1] == 0, "unterminated LRAT hints")
            hints = parts[cut + 1:-1]
            require(bool(hints) and all(h > 0 for h in hints),
                    "non-RUP or empty hint sequence")
            # Assume the negation of the proposed lemma, then follow hints.
            assignment = {}
            for lit in new:
                variable, value = abs(lit), lit < 0
                require(variable not in assignment or assignment[variable] == value,
                        "tautological lemma")
                assignment[variable] = value
            conflict = False
            for hint in hints:
                require(hint in active, f"unknown hint {hint}")
                unassigned = []
                satisfied = False
                for lit in active[hint]:
                    value = assignment.get(abs(lit))
                    if value is None:
                        unassigned.append(lit)
                    elif value == (lit > 0):
                        satisfied = True
                        break
                require(not satisfied, "hint already satisfied")
                if not unassigned:
                    conflict = True
                    break
                require(len(unassigned) == 1, "hint is not unit")
                lit = unassigned[0]
                assignment[abs(lit)] = lit > 0
            require(conflict, "lemma lacks a unit-propagation contradiction")
            active[cid] = new
            added += 1
            if not new:
                final = True
    require(final, "no empty clause derived")
    return added, deleted, last


def verify_witness(rows=WITNESS):
    if len(rows) != 9 or [len(r) for r in rows].count(2) != 3:
        return False
    out = [set(r) for r in rows]
    if any(len(out[i]) != len(rows[i]) or i in out[i]
           or any(j not in range(9) for j in out[i]) for i in range(9)):
        return False
    if any(i in out[j] for i in range(9) for j in out[i]):
        return False
    if any(i in out[k] for i in range(9)
           for j in out[i] for k in out[j]):
        return False
    return min(map(len, rows)) >= 2


def run_check():
    results = {}
    for case in CERT_SHA256:
        clauses = formula(case)
        expected = 464 if case == "zero_low" else 500 if case == "one_low" else 544
        require(len(clauses) == expected and
                max(abs(x) for c in clauses for x in c) == 72,
                "CNF dimensions drifted")
        path = ROOT / (case + ".lrat.gz")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == CERT_SHA256[case], f"certificate digest mismatch: {case}")
        added, deleted, last = check_lrat(clauses, path)
        results[case] = {
            "clauses": len(clauses),
            "lrat_added": added,
            "lrat_deleted": deleted,
            "final_clause_id": last,
            "cnf_sha256": hashlib.sha256(dimacs(clauses).encode()).hexdigest(),
            "certificate_sha256": digest,
        }
    require(verify_witness(), "sharpness witness invalid")
    return {
        "scope": "nine-vertex oriented C3-free min-outdegree-two; zero/one/two-low cases UNSAT",
        "cases": results,
        "sharp_witness_arcs": sum(map(len, WITNESS)),
        "independent_mathematical_review": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--emit-dimacs", choices=tuple(CERT_SHA256))
    args = parser.parse_args()
    if args.emit_dimacs:
        print(dimacs(formula(args.emit_dimacs)), end="")
        return
    result = run_check()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("M074 nine-vertex three-low: seven LRAT cases and sharp witness verified")


if __name__ == "__main__":
    main()
