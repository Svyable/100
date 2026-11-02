#!/usr/bin/env python3
"""Exact all-orders chain-plus-five balance kernel: compile and replay C++.

The finite census uses two different integer DPs; Python independently checks
the combinatorial number of interval multisets. This is not human review.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "m079_chain5_kernel.cpp"
EXPECTED_FULL_CASES = 40_355_371
EXPECTED_MINIMUM = "562/1405"
EXPECTED_SHARP = 1
EXPECTED_FNV64 = "b1671adf73c7eb56"  # full 40,355,371-case dual replay

SUMMARY = re.compile(
    r"cases=(\d+) dual=(\d+) negative=(\d+) minimum=(\d+/\d+) "
    r"multiplicity=(\d+) max_length=(\d+) intervals=(\d+) fnv64=([0-9a-f]{16}) "
    r"witness=(.*)"
)


def number_of_multisets(max_length: int) -> int:
    """Inclusion-exclusion: at least one left=0 and one right=0.

    Intervals have length >=2, so these two sets are disjoint. The count is
    independent of the C++ enumeration and its width/Helly validity filter.
    """
    n = sum(range(2, max_length + 1))
    edge = max_length - 1
    return (
        math.comb(n + 4, 5)
        - 2 * math.comb(n - edge + 4, 5)
        + math.comb(n - 2 * edge + 4, 5)
    )


def compile_checker(directory: str | Path) -> Path:
    compiler = shutil.which("clang++") or shutil.which("g++") or shutil.which("c++")
    if compiler is None:
        raise RuntimeError("C++17 compiler required (clang++ or g++)")
    binary = Path(directory) / "m079_chain5_kernel"
    subprocess.run(
        [compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-Werror",
         str(SOURCE), "-o", str(binary)],
        check=True, capture_output=True, text=True,
    )
    return binary


def run_census(binary: Path, max_length: int = 15, dual: bool = True) -> dict:
    command = [str(binary), "--max-length", str(max_length)]
    if dual:
        command.append("--dual")
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    match = SUMMARY.search(result.stderr)
    if not match:
        raise AssertionError("C++ census omitted its exact summary: " + result.stderr)
    cases, dual_cases, negative, minimum, sharp, limit, n, fnv, witness = match.groups()
    output = {
        "cases": int(cases),
        "dual_checked": int(dual_cases),
        "negative": int(negative),
        "minimum": minimum,
        "sharp_multisets": int(sharp),
        "max_length": int(limit),
        "interval_options": int(n),
        "fnv64": fnv,
        "first_minimum_witness": witness,
    }
    assert output["cases"] == number_of_multisets(max_length), output
    assert output["negative"] == 0, output
    if dual:
        assert output["dual_checked"] == output["cases"], output
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="full 40m-case two-path certificate")
    parser.add_argument("--smoke", action="store_true", help="21,250-case fast dual certificate")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--max-length", type=int, default=15)
    parser.add_argument("--no-dual", action="store_true", help="exploratory only")
    args = parser.parse_args()
    if args.check and (args.smoke or args.no_dual or args.max_length != 15):
        parser.error("--check requires the full max-length=15 dual certificate")
    if args.smoke:
        args.max_length = 6
    if not 2 <= args.max_length <= 15:
        parser.error("length must be between 2 and 15")
    with tempfile.TemporaryDirectory(prefix="m079_chain5_") as temp:
        binary = compile_checker(temp)
        data = run_census(binary, args.max_length, dual=not args.no_dual)
        if args.check:
            assert data["cases"] == EXPECTED_FULL_CASES, data
            assert data["minimum"] == EXPECTED_MINIMUM, data
            assert data["sharp_multisets"] == EXPECTED_SHARP, data
            if EXPECTED_FNV64 is not None:
                assert data["fnv64"] == EXPECTED_FNV64, data
        if args.smoke:
            assert data["cases"] == 21_250, data
            assert data["minimum"] == EXPECTED_MINIMUM, data
        if args.json:
            print(json.dumps(data, sort_keys=True))
        else:
            print(
                f"M079 chain5: {data['cases']} normalized interval multisets; "
                f"minimum {data['minimum']}; two-path {data['dual_checked']}; "
                f"FNV64 {data['fnv64']}"
            )


if __name__ == "__main__":
    main()
