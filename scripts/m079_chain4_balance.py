#!/usr/bin/env python3
"""M079 chain-plus-four: reproduce the sharp restricted 25/61 candidate.

--check compiles a C++17 two-path exact census over 3,456,151 normalized
unlabelled interval multisets and SHA-256 hashes its complete transcript.
--smoke runs the same check through length 8; --witness uses literal
permutation enumeration only. Neither is an independent human review.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CPP = ROOT / "scripts" / "m079_chain4_balance.cpp"
WITNESS = ((-1, 0), (0, 1), (-1, 1), (-4, 0))
FULL_SHA256 = "79017e785d0fd236d5aa87fb1c2869fcf039c1e2a36fb75be667d3236a04be88"
SMOKE_SHA256 = "db1bd1e54f06f56ffd9babc082ac2f1cb16693d7ee226f8fcd0e66bcfa2634cb"
EXPECTED = {8: (21511, SMOKE_SHA256), 18: (3456151, FULL_SHA256)}


def valid(intervals):
    return (len(intervals) == 4
            and all(a <= 0 <= b and b - a + 1 >= 2 for a, b in intervals)
            and max(a for a, _ in intervals) == min(b for _, b in intervals) == 0)


def literal_permutations(intervals):
    """Third path for small instances: check all permutations against poset relations."""
    if not valid(intervals):
        raise ValueError("not a width-four chain-plus-four normalized instance")
    lo = min(a for a, _ in intervals)
    hi = max(b for _, b in intervals)
    m = hi - lo
    n = m + 4
    if n > 10:
        raise ValueError("literal factorial checker limited to 10 elements")
    shifted = [(a - lo, b - lo) for a, b in intervals]
    counts = {(i, j): 0 for i in range(4) for j in range(i + 1, 4)}
    counts.update({(i, 4 + q): 0 for i in range(4) for q in range(m)})
    total = 0
    for p in itertools.permutations(range(n)):
        positions = [0] * n
        for rank, v in enumerate(p):
            positions[v] = rank
        if any(positions[q] >= positions[q + 1] for q in range(m - 1)):
            continue
        if any((a > 0 and positions[a - 1] >= positions[m + i])
               or (b < m and positions[m + i] >= positions[b])
               for i, (a, b) in enumerate(shifted)):
            continue
        total += 1
        for i in range(4):
            for j in range(i + 1, 4):
                counts[i, j] += positions[m + i] < positions[m + j]
            for q in range(m):
                counts[i, 4 + q] += positions[m + i] < positions[q]
    best = max(min(c, total - c) for c in counts.values())
    return {"extensions": total, "best_numerator": best,
            "balance": f"{best}/{total}", "pair_counts": counts}


def census(max_length=18):
    if max_length not in EXPECTED:
        raise ValueError("only the pinned 8-gap smoke or 18-gap full run is accepted")
    with tempfile.TemporaryDirectory(prefix="m079_chain4_") as tmp:
        binary = Path(tmp) / "m079_chain4"
        subprocess.run(["c++", "-O3", "-std=c++17", str(CPP), "-o", str(binary)],
                       check=True, cwd=ROOT)
        p = subprocess.Popen([str(binary), str(max_length), "--transcript"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT)
        digest = hashlib.sha256()
        for line in p.stdout:
            digest.update(line)
        stderr = p.stderr.read().decode("utf-8")
        p.stdout.close()
        p.stderr.close()
        if p.wait() != 0:
            raise AssertionError(f"census failed: {stderr}")
    match = re.search(r"length=(\d+) cases=(\d+) min=(\d+)/(\d+) sharp=(\d+)", stderr)
    if not match:
        raise AssertionError(f"unparseable census summary: {stderr}")
    length, cases, numerator, denominator, sharp = map(int, match.groups())
    expected_cases, expected_hash = EXPECTED[max_length]
    if (length != max_length or cases != expected_cases or
            numerator * 61 != denominator * 25 or sharp != 2):
        raise AssertionError(f"unexpected census: {stderr}")
    if digest.hexdigest() != expected_hash:
        raise AssertionError(f"transcript SHA-256 mismatch: {digest.hexdigest()}")
    return {"length_cap": length, "cases": cases, "minimum": "25/61",
            "sharp_interval_multisets": sharp, "sha256": digest.hexdigest(),
            "two_integer_counters_agree": True}


def check_witness():
    r = literal_permutations(WITNESS)
    if (r["extensions"], r["best_numerator"]) != (183, 75):
        raise AssertionError(f"sharp witness failed literal enumeration: {r}")
    if 61 * r["best_numerator"] != 25 * r["extensions"]:
        raise AssertionError("witness is not exactly 25/61")
    return r


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true")
    group.add_argument("--smoke", action="store_true")
    group.add_argument("--witness", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    witness = check_witness()
    result = {"witness": {"intervals": WITNESS, "extensions": witness["extensions"],
                          "balance": "25/61", "literal_permutations_checked": 362880}}
    if not args.witness:
        result["census"] = census(8 if args.smoke else 18)
    print(json.dumps(result, sort_keys=True, indent=2) if args.json else
          f"M079 chain4 verified: {result}")


if __name__ == "__main__":
    main()
