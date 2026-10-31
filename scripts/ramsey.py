#!/usr/bin/env python3
"""Independent finite Ramsey coloring verifier and a transparent SAT encoding.

A missing pair in a red-edge certificate is BLUE. Only a verified
counterexample on n vertices proves R(s,t) > n. UNSAT solver logs alone
are not accepted as proofs without independently checked certificates.
"""
import argparse
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys

FORMAT = "svyable.ramsey.red-edges.v1"


def parameters(n, red, blue):
    if any(type(x) is not int for x in (n, red, blue)):
        raise ValueError("n, red and blue must be integers")
    if n < 2 or red < 2 or blue < 2:
        raise ValueError("require n >= 2 and clique sizes >= 2")


def build_red(n, edges):
    if not isinstance(edges, list):
        raise ValueError("red_edges must be a list of [u, v] pairs")
    adj = [0] * n
    seen = set()
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError("each edge must be [u, v]")
        u, v = edge
        if type(u) is not int or type(v) is not int or not (0 <= u < v < n):
            raise ValueError("edges require integer endpoints 0 <= u < v < n")
        if (u, v) in seen:
            raise ValueError("duplicate red edge")
        seen.add((u, v))
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def find_clique(adj, size):
    """Return one clique as a tuple, or None, via exact bitset backtracking."""
    n = len(adj)
    def visit(candidates, remaining, chosen):
        if remaining == 0:
            return chosen
        while candidates.bit_count() >= remaining:
            bit = candidates & -candidates
            v = bit.bit_length() - 1
            candidates ^= bit
            result = visit(candidates & adj[v], remaining - 1, chosen + (v,))
            if result is not None:
                return result
        return None
    return visit((1 << n) - 1, size, ())


def verify(n, red_edges, red_size, blue_size):
    """Return (acceptable, red witness, blue witness)."""
    parameters(n, red_size, blue_size)
    red = build_red(n, red_edges)
    mask = (1 << n) - 1
    blue = [mask ^ (1 << v) ^ red[v] for v in range(n)]
    red_hit = find_clique(red, red_size)
    blue_hit = find_clique(blue, blue_size)
    return red_hit is None and blue_hit is None, red_hit, blue_hit


def clauses(n, red_size, blue_size):
    """DIMACS clauses: x_uv=True denotes a RED edge."""
    parameters(n, red_size, blue_size)
    edge_vars = {(u, v): i + 1 for i, (u, v) in
                 enumerate(combinations(range(n), 2))}
    for vertices in combinations(range(n), red_size):
        yield tuple(-edge_vars[e] for e in combinations(vertices, 2))
    for vertices in combinations(range(n), blue_size):
        yield tuple(edge_vars[e] for e in combinations(vertices, 2))


def dimacs(n, red_size, blue_size, destination, force=False):
    parameters(n, red_size, blue_size)
    count = comb(n, red_size) + comb(n, blue_size) if n >= max(red_size, blue_size) else (
        (comb(n, red_size) if n >= red_size else 0)
        + (comb(n, blue_size) if n >= blue_size else 0))
    if count > 100_000 and not force:
        raise ValueError(f"{count} clauses: pass --force to write a large CNF")
    destination.write(f"c x_(u,v) is red; all absent red edges are blue\n")
    destination.write(f"p cnf {comb(n, 2)} {count}\n")
    for clause in clauses(n, red_size, blue_size):
        destination.write(" ".join(map(str, clause)) + " 0\n")


def demo():
    """Independently enumerate all 2^15 labeled graphs for R(3,3)=6."""
    cycle = [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4]]
    if not verify(5, cycle, 3, 3)[0]:
        raise RuntimeError("C5 lower-bound witness failed")
    edges = list(combinations(range(6), 2))
    checked = 0
    for bits in range(1 << len(edges)):
        coloring = [list(e) for i, e in enumerate(edges) if bits & (1 << i)]
        if verify(6, coloring, 3, 3)[0]:
            raise RuntimeError("unexpected (3,3)-free coloring of K6")
        checked += 1
    return checked


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="verify a red-edge JSON certificate")
    check.add_argument("certificate", type=Path)
    check.add_argument("--red", type=int, required=True)
    check.add_argument("--blue", type=int, required=True)
    cnf = sub.add_parser("cnf", help="emit no-monochromatic-clique SAT encoding")
    cnf.add_argument("--n", type=int, required=True)
    cnf.add_argument("--red", type=int, required=True)
    cnf.add_argument("--blue", type=int, required=True)
    cnf.add_argument("--force", action="store_true")
    sub.add_parser("demo", help="exactly check R(3,3)=6 by finite enumeration")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            print(f"PASS: C5 witness and {demo()} exhaustively checked K6 colorings")
            return 0
        if args.command == "cnf":
            dimacs(args.n, args.red, args.blue, sys.stdout, args.force)
            return 0
        data = json.loads(args.certificate.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("format") != FORMAT:
            raise ValueError("unsupported certificate format")
        ok, red_hit, blue_hit = verify(data["n"], data["red_edges"],
                                        args.red, args.blue)
        if ok:
            print(f"PASS: K{data['n']} has no red K{args.red} or blue K{args.blue}")
            return 0
        print(f"FAIL: red clique={red_hit}; blue clique={blue_hit}")
        return 1
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
