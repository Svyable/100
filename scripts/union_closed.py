#!/usr/bin/env python3
"""Exact finite certificate checker for Frankl's union-closed sets conjecture.

This can verify finite examples and exhaust small universes; it does NOT
establish the conjecture for arbitrary finite set systems.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys

FORMAT = "svyable.unionclosed.family.v1"


def parse_family(n, sets):
    if type(n) is not int or n < 1:
        raise ValueError("n must be a positive integer")
    if not isinstance(sets, list) or not sets:
        raise ValueError("sets must be a nonempty list")
    masks = set()
    for subset in sets:
        if not isinstance(subset, list):
            raise ValueError("each subset must be a list")
        mask = 0
        for e in subset:
            if type(e) is not int or not 0 <= e < n:
                raise ValueError("element outside 0..n-1 or not an integer")
            if mask & (1 << e):
                raise ValueError("duplicate element within subset")
            mask |= 1 << e
        if mask in masks:
            raise ValueError("duplicate set in family")
        masks.add(mask)
    if all(x == 0 for x in masks):
        raise ValueError("family must contain a nonempty set")
    return masks


def is_union_closed(members):
    return all((a | b) in members for a in members for b in members)


def frequencies(members, n):
    return [sum(bool(m & (1 << i)) for m in members) for i in range(n)]


def verify(n, sets):
    members = parse_family(n, sets)
    if not is_union_closed(members):
        raise ValueError("not union-closed")
    counts = frequencies(members, n)
    largest = max(counts)
    return {
        "family_size": len(members),
        "frequencies": counts,
        "most_frequent": largest,
        "abundance": Fraction(largest, len(members)),
        "frankl_holds": 2 * largest >= len(members)
    }


def exhaustive(n):
    """Enumerate EVERY distinct family of subsets of [n], for n <= 4 only."""
    if type(n) is not int or not 1 <= n <= 4:
        raise ValueError("exhaustive search is restricted to 1 <= n <= 4")
    total = 1 << (1 << n)
    closed_nontrivial = 0
    sharp = None
    for encoded in range(total):
        members = {i for i in range(1 << n) if encoded & (1 << i)}
        if not members or max(members) == 0 or not is_union_closed(members):
            continue
        closed_nontrivial += 1
        f = max(frequencies(members, n))
        if 2 * f < len(members):
            raise RuntimeError(f"possible counterexample at n={n}: {sorted(members)}")
        abundance = Fraction(f, len(members))
        if sharp is None or abundance < sharp:
            sharp = abundance
    return total, closed_nontrivial, sharp


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    check.add_argument("certificate", type=Path)
    enum = sub.add_parser("exhaustive")
    enum.add_argument("--n", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "exhaustive":
            total, valid, sharp = exhaustive(args.n)
            print(f"PASS: {total} candidate families checked; "
                  f"{valid} nontrivial union-closed; minimum maximal frequency {sharp}")
            return 0
        item = json.loads(args.certificate.read_text(encoding="utf-8"))
        if not isinstance(item, dict) or item.get("format") != FORMAT:
            raise ValueError("unsupported certificate format")
        v = verify(item["n"], item["sets"])
        print("PASS" if v["frankl_holds"] else "POTENTIAL COUNTEREXAMPLE")
        print(f"|F|={v['family_size']} counts={v['frequencies']} "
              f"maximum fraction={v['abundance']}")
        return 0 if v["frankl_holds"] else 1
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
        print(f"INVALID: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
