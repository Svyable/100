#!/usr/bin/env python3
"""Exact rational, equal-mass two-block graphon audit for M073.

Fixed domain: symmetric W with two classes of mass 1/2, and matrix
    [[a/D, b/D], [b/D, c/D]]  for 0<=a,b,c<=D.
This is *not* an explicit finite host graph nor a proof about all graphons.
Two independent combinatorial algorithms compute the integer homomorphism
numerator; equality/violation uses exact integers, no rounding.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACES_PATH = ROOT / "data/reference/sidorenko_faces.json"
FACES_SHA256 = "653fd38252aa4034512303dd71d738a42cc3685666b982d41f21c76c336c4b02"


def read_faces(path=FACES_PATH):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if (data.get("problem_id"), data.get("point_count"),
            data.get("face_count"), data.get("expected_edges")) != ("M073", 13, 22, 66):
        raise ValueError("M073 source dimensions do not match pinned statement")
    faces = data["faces"]
    if (len(faces) != 22
            or any(not isinstance(f, list) or len(f) != 3 or
                   any(type(v) is not int or not 0 <= v < 13 for v in f) or
                   len(set(f)) != 3 for f in faces)
            or len({tuple(f) for f in faces}) != 22):
        raise ValueError("M073 incidence triples malformed")
    actual = hashlib.sha256(json.dumps(faces, separators=(",", ":")).encode()).hexdigest()
    if actual != FACES_SHA256:
        raise ValueError("M073 faces differ from pinned source table")
    # Preserve the upstream zero-based triple table ordering.
    if any(f != sorted(f) for f in faces):
        raise ValueError("M073 source triples not in canonical order")
    return tuple(tuple(f) for f in faces)


def weights(a, b, c):
    if any(type(v) is not int or v < 0 for v in (a, b, c)):
        raise ValueError("integer nonnegative weight numerators required")
    return ((a, b), (b, c))


def numerator_by_faces(faces, W, points=13):
    """Sum over assignments of points; integrate out each face independently."""
    if any(len(face) != 3 for face in faces):
        raise ValueError("incidence face must have three points")
    tables = []
    for face in faces:
        vals = []
        for code in range(8):
            point_bits = [(code >> i) & 1 for i in range(3)]
            vals.append(sum(W[point_bits[0]][j] * W[point_bits[1]][j] *
                            W[point_bits[2]][j] for j in (0, 1)))
        tables.append(vals)
    total = 0
    for mask in range(1 << points):
        term = 1
        for (u, v, z), tbl in zip(faces, tables):
            index = ((mask >> u) & 1) | (((mask >> v) & 1) << 1) | (((mask >> z) & 1) << 2)
            term *= tbl[index]
            if not term:
                break
        total += term
    return total


def numerator_by_edges(nodes, edges, W):
    """Independent exact factor elimination over an arbitrary simple graph.

    Every edge contributes its original pairwise interaction. Explicit unary
    factors count isolated vertices correctly (a constant factor of 2 each).
    """
    if type(nodes) is not int or nodes < 0:
        raise ValueError("nonnegative vertex count required")
    factors = [((v,), (1, 1)) for v in range(nodes)]
    seen = set()
    for u, v in edges:
        if (type(u) is not int or type(v) is not int or u == v or
                not 0 <= u < nodes or not 0 <= v < nodes):
            raise ValueError("simple loopless graph with in-range vertices required")
        key = (min(u, v), max(u, v))
        if key in seen:
            raise ValueError("duplicate edge")
        seen.add(key)
        factors.append((key, tuple(W[x][y] for x in (0, 1) for y in (0, 1))))
    for vertex in range(nodes):
        active = [f for f in factors if vertex in f[0]]
        factors = [f for f in factors if vertex not in f[0]]
        other_vars = sorted({v for scope, _ in active for v in scope if v != vertex})
        scope = tuple(other_vars)
        output = []
        # First scoped variable is the most significant bit.
        for values in product((0, 1), repeat=len(scope)):
            assignment = dict(zip(scope, values))
            subtotal = 0
            for bit in (0, 1):
                assignment[vertex] = bit
                val = 1
                for factor_scope, table in active:
                    idx = 0
                    for node in factor_scope:
                        idx = (idx << 1) | assignment[node]
                    val *= table[idx]
                    if val == 0:
                        break
                subtotal += val
            output.append(subtotal)
        factors.append((scope, tuple(output)))
    if any(scope or len(vals) != 1 for scope, vals in factors):
        raise AssertionError("failed to eliminate every graphon variable")
    result = 1
    for _, vals in factors:
        result *= vals[0]
    return result


def numerator_by_elimination(faces, W, points=13):
    """Check the whole incidence graph using general pairwise-edge factors."""
    edges = [(i, points + j) for j, face in enumerate(faces) for i in face]
    return numerator_by_edges(points + len(faces), edges, W)


def compare(faces, a, b, c, denominator=2, independent=True):
    if type(denominator) is not int or denominator <= 0:
        raise ValueError("positive integer denominator required")
    if any(t > denominator for t in (a, b, c)):
        raise ValueError("graphon weight > 1")
    W = weights(a, b, c)
    numer = numerator_by_faces(faces, W)
    if independent:
        replay = numerator_by_elimination(faces, W)
        if replay != numer:
            raise AssertionError("independent incidence-edge computation disagrees")
    e = 3 * len(faces)
    v = 13 + len(faces)
    if v > 2 * e:
        raise ValueError("comparison normalization needs v<=2e")
    # t(H,W) = numer / (2**v * D**e)
    # p(W) = (a+2*b+c)/(4*D)
    # Hence comparing numer*2**(2*e-v) to (a+2*b+c)**e is exact.
    lhs = numer * (1 << (2 * e - v))
    rhs = (a + 2 * b + c) ** e
    return {"a": a, "b": b, "c": c, "denominator": denominator,
            "hom_numerator": numer, "gap_sign": (lhs > rhs) - (lhs < rhs),
            "strict_counterexample": lhs < rhs,
            "equality": lhs == rhs}


def audit_grid(faces, numerator_values=(0, 1, 2), denominator=2):
    if tuple(numerator_values) != (0, 1, 2) or denominator != 2:
        raise ValueError("preregistered grid is exactly {0,1/2,1}^3")
    rows = [compare(faces, *v, denominator, independent=True)
            for v in product(numerator_values, repeat=3)]
    negatives = [r for r in rows if r["strict_counterexample"]]
    equals = [r for r in rows if r["equality"]]
    positives = [r for r in rows if r["gap_sign"] > 0]
    return {
        "certificate_schema": "svyable.m073.twoblock.v1",
        "source": str(FACES_PATH.relative_to(ROOT)),
        "source_faces_sha256": FACES_SHA256,
        "pattern_vertices": 13 + len(faces),
        "pattern_edges": 3 * len(faces),
        "mass_vector": ["1/2", "1/2"],
        "weight_values": ["0", "1/2", "1"],
        "grid_size": len(rows),
        "strict_violations": len(negatives),
        "positive_gap_cases": len(positives),
        "equality_cases": len(equals),
        "violations": negatives,
        "equality_weights": [[r[k] for k in ("a", "b", "c")] for r in equals],
        "interpretation": ("Finite coarse two-step *graphon* grid only; a failed "
                           "search does not establish Sidorenko and does not replay "
                           "the claimed finite host G."),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true")
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    doc = audit_grid(read_faces())
    print(json.dumps(doc, indent=2, sort_keys=True) if args.json or args.check else
          f"M073 two-block coarse grid: {doc['grid_size']} exact cells, "
          f"{doc['strict_violations']} violating, {doc['equality_cases']} equal, "
          f"{doc['positive_gap_cases']} strict positive")
    if args.check and (doc["grid_size"] != 27
                       or doc["strict_violations"] != 0
                       or doc["pattern_edges"] != 66):
        raise SystemExit("M073 two-block grid drift or strict witness: inspect data before claiming!")


if __name__ == "__main__":
    main()
