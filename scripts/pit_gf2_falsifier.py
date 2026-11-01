#!/usr/bin/env python3
"""Exact, fail-closed falsifier for the *locked* M088 GF(2) circuit class.

Two deliberately separate paths:
  * formal_polynomial: expands gates in GF(2)[x_0,...,x_(n-1)]
  * evaluate: interprets gates directly on bits, without symbolic expansion

This is a falsifier for supplied hitting sets, not a hitting-set construction.
A nonzero formal polynomial need not be a nonzero GF(2)-valued function.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

MAX_GATES = 20
MAX_DEGREE = 3
MAX_VARIABLES = 8


def _is_int(x):
    return type(x) is int


def _ref_degree(ref, n, degrees):
    if ref in ("0", "1"):
        return 0
    if not isinstance(ref, str):
        raise ValueError("operand must be a string")
    if ref.startswith("x") and ref[1:].isdigit():
        i = int(ref[1:])
        if ref != f"x{i}" or i >= n:
            raise ValueError("invalid input reference")
        return 1
    if ref.startswith("g") and ref[1:].isdigit():
        i = int(ref[1:])
        if ref != f"g{i}" or i >= len(degrees):
            raise ValueError("forward or invalid gate reference")
        return degrees[i]
    raise ValueError("unknown operand reference")


def validate(circuit):
    if not isinstance(circuit, dict) or set(circuit) != {"n", "gates"}:
        raise ValueError("circuit must contain exactly n and gates")
    n, gates = circuit["n"], circuit["gates"]
    if not _is_int(n) or not 0 <= n <= MAX_VARIABLES:
        raise ValueError("n must be an integer from 0 through 8")
    if not isinstance(gates, list) or not 1 <= len(gates) <= MAX_GATES:
        raise ValueError("circuit needs 1..20 binary gates; last is output")
    degrees = []
    for gate in gates:
        if not isinstance(gate, dict) or set(gate) != {"op", "a", "b"}:
            raise ValueError("each gate must have exactly op, a, b")
        if gate["op"] not in ("xor", "mul"):
            raise ValueError("only XOR and multiplication are permitted")
        da = _ref_degree(gate["a"], n, degrees)
        db = _ref_degree(gate["b"], n, degrees)
        d = max(da, db) if gate["op"] == "xor" else da + db
        if d > MAX_DEGREE:
            raise ValueError("syntactic degree exceeds 3")
        degrees.append(d)
    return n, gates, degrees[-1]


def _formal_ref(ref, n, gates):
    if ref == "0":
        return set()
    if ref == "1":
        return {()}
    if ref[0] == "x":
        return {(int(ref[1:]),)}
    return gates[int(ref[1:])]


def formal_polynomial(circuit):
    """Set of sorted monomial tuples with coefficient 1 in GF(2)."""
    n, instructions, _ = validate(circuit)
    computed = []
    for gate in instructions:
        a = _formal_ref(gate["a"], n, computed)
        b = _formal_ref(gate["b"], n, computed)
        if gate["op"] == "xor":
            out = a.symmetric_difference(b)
        else:
            out = set()
            for u in a:
                for v in b:
                    term = tuple(sorted(u + v))
                    if term in out:
                        out.remove(term)
                    else:
                        out.add(term)
        computed.append(out)
    return computed[-1]


def _bit_ref(ref, bits, gates):
    if ref == "0":
        return 0
    if ref == "1":
        return 1
    if ref[0] == "x":
        return bits[int(ref[1:])]
    return gates[int(ref[1:])]


def evaluate(circuit, bits):
    """Direct gate replay, not evaluation of formal_polynomial."""
    n, instructions, _ = validate(circuit)
    if (not isinstance(bits, (tuple, list)) or len(bits) != n
            or any(not _is_int(v) or v not in (0, 1) for v in bits)):
        raise ValueError("point must be a length-n list of 0/1 integers")
    values = []
    for gate in instructions:
        a = _bit_ref(gate["a"], bits, values)
        b = _bit_ref(gate["b"], bits, values)
        values.append(a ^ b if gate["op"] == "xor" else a & b)
    return values[-1]


def analyze(circuit, hitting_set):
    n, gates, degree = validate(circuit)
    if not isinstance(hitting_set, list):
        raise ValueError("hitting_set must be a list of points")
    points = []
    for point in hitting_set:
        if (not isinstance(point, list) or len(point) != n
                or any(not _is_int(x) or x not in (0, 1) for x in point)):
            raise ValueError("invalid GF(2) point")
        points.append(tuple(point))
    if len(set(points)) != len(points):
        raise ValueError("duplicate hitting-set point")
    monomials = formal_polynomial(circuit)
    full_nonzero_points = [
        list(p) for p in itertools.product((0, 1), repeat=n)
        if evaluate(circuit, p) == 1
    ]
    missed = all(evaluate(circuit, p) == 0 for p in points)
    return {
        "n": n,
        "gate_count": len(gates),
        "syntactic_degree": degree,
        "formal_nonzero": bool(monomials),
        "formal_monomials": [list(m) for m in sorted(monomials)],
        "function_nonzero": bool(full_nonzero_points),
        "first_nonzero_boolean_point": full_nonzero_points[0] if full_nonzero_points else None,
        "vanishes_on_supplied_set": missed,
        "formal_falsifier": bool(monomials) and missed,
        "functional_falsifier": bool(full_nonzero_points) and missed,
        "full_cube_checked": 1 << n,
    }


def formal_obstruction():
    # x0*x0 + x0: nonzero formal polynomial, zero function on all GF(2).
    return {"n": 1, "gates": [
        {"op": "mul", "a": "x0", "b": "x0"},
        {"op": "xor", "a": "g0", "b": "x0"},
    ]}


def functional_obstruction():
    # x0*x1 misses the zero and unit vectors but is 1 at (1,1).
    return {"n": 2, "gates": [
        {"op": "mul", "a": "x0", "b": "x1"},
    ]}


def check():
    formal = analyze(formal_obstruction(), [[0], [1]])
    assert formal["formal_monomials"] == [[0], [0, 0]]
    assert formal["formal_falsifier"] and not formal["function_nonzero"]
    assert formal["full_cube_checked"] == 2
    functional = analyze(functional_obstruction(), [[0, 0], [0, 1], [1, 0]])
    assert functional["formal_falsifier"] and functional["functional_falsifier"]
    assert functional["first_nonzero_boolean_point"] == [1, 1]
    full = analyze(functional_obstruction(), [[0, 0], [0, 1], [1, 0], [1, 1]])
    assert not full["vanishes_on_supplied_set"]
    return {"formal_vs_function_obstruction": formal, "missed_function_control": functional}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--input", type=Path, help="JSON object with circuit and hitting_set")
    args = ap.parse_args()
    if args.input:
        obj = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(obj, dict) or set(obj) != {"circuit", "hitting_set"}:
            raise ValueError("input must contain exactly circuit and hitting_set")
        report = analyze(obj["circuit"], obj["hitting_set"])
    else:
        report = check()
    if args.check:
        check()
    if args.json or args.input:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("PASS: M088 exact symbolic and independent Boolean falsifier controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
