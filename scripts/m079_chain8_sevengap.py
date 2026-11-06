#!/usr/bin/env python3
"""Exact width-eight chain+antichain local balance certificate.

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
CPP = ROOT / "m079_chain8_sevengap.cpp"
K = 8
EXPECTED_CASES = 1_819_530
EXPECTED_MINIMUM = (418779, 939501)
EXPECTED_HASH = "df3b1c32cf646fb7"
WITNESS = ((-6, 0), (-3, 0), (-2, 0), (-1, 0), (0, 1), (0, 2), (0, 3), (0, 6))
BOUNDARY6 = ((-5, 0), (-3, 0), (-2, 2), (-2, 3), (-1, 0), (-1, 3), (0, 3), (0, 4))
BOUNDARY6_COUNTS = (3193368, 1425408)
SUMMARY = re.compile(
    r"cases=(\d+) dual=(\d+) negative=(\d+) minimum=(\d+)/(\d+) "
    r"multiplicity=(\d+) max_length=(\d+) intervals=(\d+) distinct=(\d+) fnv64=([0-9a-f]{16}) witness=(.*)"
)
INSTANCE = re.compile(r"E=(\d+) best=(\d+) delta=(\d+)/(\d+)")


def canonical_count(limit: int, distinct: bool = False) -> int:
    """Inclusion-exclusion over multisets containing a left-zero and right-zero interval."""
    n = sum(range(2, limit + 1))
    edge = limit - 1
    offset = 0 if distinct else K - 1
    return (math.comb(n + offset, K)
            - 2 * math.comb(n - edge + offset, K)
            + math.comb(n - 2 * edge + offset, K))


def valid(intervals: tuple[tuple[int, int], ...], limit: int = 7) -> bool:
    return (len(intervals) == K
            and all(a <= 0 <= b and 2 <= b - a + 1 <= limit
                    for a, b in intervals)
            and max(a for a, _ in intervals) == 0
            and min(b for _, b in intervals) == 0)


def literal_poset(intervals: tuple[tuple[int, int], ...]) -> list[int]:
    """Predecessor bitmasks from a chain and explicit transitive relations."""
    assert valid(intervals, limit=7)
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
    binary = destination / "m079_chain8_sevengap"
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


def check(full: bool = False) -> dict:
    """Check a literal-poset witness and controls; --full runs the exhaustive dual core."""
    assert canonical_count(7, distinct=True) == EXPECTED_CASES
    assert canonical_count(7) == 12_259_764
    assert canonical_count(6, distinct=True) == 113_145
    assert valid(WITNESS)
    with tempfile.TemporaryDirectory(prefix="m079_chain8_sevengap_") as tmp:
        binary = compile_cpp(Path(tmp))
        witness = literal_balance(WITNESS)
        assert witness[:2] == cpp_instance(binary, WITNESS)
        assert witness[:2] == (939501, 418779)
        assert valid(BOUNDARY6, limit=6)
        assert literal_balance(BOUNDARY6)[:2] == cpp_instance(binary, BOUNDARY6) == BOUNDARY6_COUNTS
        assert EXPECTED_MINIMUM[0] * BOUNDARY6_COUNTS[0] < BOUNDARY6_COUNTS[1] * EXPECTED_MINIMUM[1]
        # Different state representation, including seven-gap and repeated intervals.
        choices = [(a, a + length - 1)
                   for length in range(2, 8) for a in range(1 - length, 1)]
        left = [v for v in choices if v[0] == 0]
        right = [v for v in choices if v[1] == 0]
        rng = Random(79027)
        checked = 0
        with_seven = 0
        for _ in range(25):
            sample = tuple(sorted((rng.choice(left), rng.choice(right), *rng.sample(choices, 6))))
            assert valid(sample)
            assert literal_balance(sample)[:2] == cpp_instance(binary, sample)
            checked += 1
            with_seven += any(b - a + 1 == 7 for a, b in sample)
        assert with_seven >= 20
        repeated = ((-1, 0),) * 4 + ((0, 1),) * 4
        E, B, _ = literal_balance(repeated)
        assert 2 * B == E
        assert not valid(((-1, 1),) * K)  # width nine
        assert not valid(((-1, 0),) * 7 + ((0, 0),))  # forbidden singleton
        assert not valid(((-7, 0),) + ((0, 1),) * 7)  # eight gaps
        arg = ",".join(f"{a}:{b}" for a, b in WITNESS)
        tamper = subprocess.run([str(binary), "--instance", arg, "--mutate-tie"],
                                capture_output=True, text=True)
        assert tamper.returncode == 3 and "mismatch" in tamper.stderr.lower()
        result = {"full": full, "distinct_cases": EXPECTED_CASES,
                  "repeated_cases_discharged": 12_259_764 - EXPECTED_CASES,
                  "minimum": f"{EXPECTED_MINIMUM[0]}/{EXPECTED_MINIMUM[1]}",
                  "witness_extensions": witness[0], "witness_best": witness[1],
                  "literal_controls": checked, "seven_gap_controls": with_seven,
                  "mutation_rejected": True}
        if full:
            proc = subprocess.run([str(binary), "--max-length", "7", "--dual"],
                                  check=True, capture_output=True, text=True)
            match = SUMMARY.search(proc.stderr)
            if not match:
                raise AssertionError(proc.stderr)
            cases, dual, negative, numerator, denominator, multiplicity, limit, options, distinct, digest, iv = match.groups()
            assert (int(cases), int(dual), int(negative)) == (EXPECTED_CASES, EXPECTED_CASES, 0)
            assert (int(numerator), int(denominator)) == EXPECTED_MINIMUM
            assert (int(multiplicity), int(limit), int(options), int(distinct)) == (1, 7, 27, 1)
            assert digest == EXPECTED_HASH
            assert iv == "".join(f"[{a},{b}]" for a, b in WITNESS)
            result.update({"dual_checked": int(dual), "hash": digest, "multiplicity": 1})
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    if not (args.check or args.full):
        parser.error("Use --check for the independent witness or --full for the dual census")
    print(json.dumps(check(full=args.full), sort_keys=True))
