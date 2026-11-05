#!/usr/bin/env python3
"""Exact width-seven chain+antichain local balance certificate.

The C++ sequential and factorial-block recurrences check every normalized
interval multiset; the Python witness checker uses the literal relation
matrix and a full-poset order-ideal recurrence (no gap-state transitions).
Author-side algorithmic agreement is not independent mathematical review.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parent
CPP = ROOT / "m079_chain7_local.cpp"
K = 7
EXPECTED_CASES = 436_680
EXPECTED_MINIMUM = (44873, 107157)
EXPECTED_HASH = "1779f630db5c21b2"
WITNESS = ((-5, 0), (-2, 0), (-2, 2), (-1, 0), (0, 1), (0, 2), (0, 5))
SUMMARY = re.compile(
    r"cases=(\d+) dual=(\d+) negative=(\d+) minimum=(\d+)/(\d+) "
    r"multiplicity=(\d+) max_length=(\d+) intervals=(\d+) fnv64=([0-9a-f]{16}) witness=(.*)"
)
INSTANCE = re.compile(r"E=(\d+) best=(\d+) delta=(\d+)/(\d+)")


def canonical_count(limit: int) -> int:
    """Inclusion-exclusion over multisets containing a left-zero and right-zero interval."""
    n = sum(range(2, limit + 1))
    edge = limit - 1
    return (math.comb(n + K - 1, K)
            - 2 * math.comb(n - edge + K - 1, K)
            + math.comb(n - 2 * edge + K - 1, K))


def valid(intervals: tuple[tuple[int, int], ...], limit: int = 6) -> bool:
    return (len(intervals) == K
            and all(a <= 0 <= b and 2 <= b - a + 1 <= limit
                    for a, b in intervals)
            and max(a for a, _ in intervals) == 0
            and min(b for _, b in intervals) == 0)


def literal_poset(intervals: tuple[tuple[int, int], ...]) -> list[int]:
    """Predecessor bitmasks from a chain and explicit transitive relations."""
    assert valid(intervals)
    lo = min(a for a, _ in intervals)
    hi = max(b for _, b in intervals)
    m = hi - lo
    n = m + K
    pred = [0] * n
    for j in range(m):
        pred[j] = (1 << j) - 1
        for i, (_, b) in enumerate(intervals):
            if b - lo <= j:
                pred[j] |= 1 << (m + i)
    for i, (a, _) in enumerate(intervals):
        pred[m + i] = (1 << (a - lo)) - 1
    return pred


def literal_balance(intervals: tuple[tuple[int, int], ...]) -> tuple[int, int, list[list[int]]]:
    """One independent full-poset bitmask recurrence, all pair-order numerators."""
    pred = literal_poset(intervals)
    n = len(pred)
    full = (1 << n) - 1
    F = [0] * (full + 1)
    B = [0] * (full + 1)
    F[0] = 1
    B[full] = 1
    for mask in range(full + 1):
        if not F[mask]:
            continue
        remaining = full ^ mask
        while remaining:
            bit = remaining & -remaining
            v = bit.bit_length() - 1
            if not (pred[v] & ~mask):
                F[mask | bit] += F[mask]
            remaining -= bit
    for mask in range(full - 1, -1, -1):
        remaining = full ^ mask
        while remaining:
            bit = remaining & -remaining
            v = bit.bit_length() - 1
            if not (pred[v] & ~mask):
                B[mask] += B[mask | bit]
            remaining -= bit
    E = F[full]
    assert E and E == B[0]
    before = [[0] * n for _ in range(n)]
    for mask in range(full):
        if not F[mask]:
            continue
        remaining = full ^ mask
        avail = remaining
        while avail:
            bit = avail & -avail
            v = bit.bit_length() - 1
            if not (pred[v] & ~mask):
                weight = F[mask] * B[mask | bit]
                rest = remaining ^ bit
                while rest:
                    wbit = rest & -rest
                    w = wbit.bit_length() - 1
                    before[v][w] += weight
                    rest -= wbit
            avail -= bit
    assert all(before[i][j] + before[j][i] == E
               for i in range(n) for j in range(i + 1, n))
    best = max(min(before[i][j], before[j][i])
               for i in range(n) for j in range(i + 1, n))
    return E, best, before


def compile_cpp(destination: Path) -> Path:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if compiler is None:
        raise RuntimeError("C++17 compiler required")
    binary = destination / "m079_chain7_local"
    subprocess.run([compiler, "-std=c++17", "-O3", "-Wall", "-Wextra",
                    "-Werror", str(CPP), "-o", str(binary)],
                   check=True, capture_output=True, text=True)
    return binary


def cpp_instance(binary: Path, intervals: tuple[tuple[int, int], ...]) -> tuple[int, int]:
    arg = ",".join(f"{a}:{b}" for a, b in intervals)
    proc = subprocess.run([str(binary), "--instance", arg], check=True,
                          capture_output=True, text=True)
    match = INSTANCE.search(proc.stdout)
    if not match:
        raise AssertionError(proc.stdout)
    E, best, a, b = map(int, match.groups())
    assert (E, best) == (b, a)
    return E, best


def check() -> dict:
    assert canonical_count(4) == 4887
    assert canonical_count(5) == 55432
    assert canonical_count(6) == EXPECTED_CASES
    assert valid(WITNESS)
    with tempfile.TemporaryDirectory(prefix="m079_chain7_") as tmp:
        binary = compile_cpp(Path(tmp))
        proc = subprocess.run([str(binary), "--max-length", "6", "--dual"],
                              check=True, capture_output=True, text=True)
        match = SUMMARY.search(proc.stderr)
        if not match:
            raise AssertionError(proc.stderr)
        cases, dual, negative, numerator, denominator, multiplicity, limit, options, digest, witness = match.groups()
        assert (int(cases), int(dual), int(negative)) == (EXPECTED_CASES, EXPECTED_CASES, 0)
        assert (int(numerator), int(denominator)) == EXPECTED_MINIMUM
        assert (int(multiplicity), int(limit), int(options)) == (1, 6, 20)
        assert digest == EXPECTED_HASH
        assert witness == "".join(f"[{a},{b}]" for a, b in WITNESS)
        literal = literal_balance(WITNESS)
        assert literal[:2] == cpp_instance(binary, WITNESS)
        assert literal[:2] == (107157, 44873)
        # Independent-representation seeded controls, including duplicates.
        choices = [(a, a + length - 1)
                   for length in range(2, 7)
                   for a in range(1 - length, 1)]
        rng = Random(79007)
        checked = 0
        while checked < 30:
            sample = tuple(sorted(rng.choices(choices, k=K)))
            if not valid(sample):
                continue
            assert literal_balance(sample)[:2] == cpp_instance(binary, sample)
            checked += 1
        # Negative controls for invalid width, forbidden singleton, and length.
        assert not valid(((-1, 1),) * K)  # common two or more gaps: width eight
        assert not valid(((-1, 0),) * 6 + ((0, 0),))
        assert not valid(((-6, 0),) + ((0, 1),) * 6)
        # Tamper with same-gap order: the second counter must disagree.
        arg = ",".join(f"{a}:{b}" for a, b in WITNESS)
        tamper = subprocess.run([str(binary), "--instance", arg, "--mutate-tie"],
                                capture_output=True, text=True)
        assert tamper.returncode == 3 and "mismatch" in tamper.stderr.lower()
        return {"cases": int(cases), "dual_checked": int(dual),
                "minimum": f"{numerator}/{denominator}",
                "multiplicity": int(multiplicity), "hash": digest,
                "witness_extensions": literal[0], "witness_best": literal[1],
                "literal_controls": checked, "mutation_rejected": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("Use --check for the complete certificate")
    print(json.dumps(check(), sort_keys=True))
