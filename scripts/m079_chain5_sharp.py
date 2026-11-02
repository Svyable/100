#!/usr/bin/env python3
"""Compile and replay the sharp 2/5 chain-five certificate (two exact DPs)."""
from __future__ import annotations
import argparse
import json
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

SOURCE = Path(__file__).with_suffix(".cpp")
FULL_CASES = 40_355_371
FULL_PRUNED = 36_703_596
FULL_RESIDUAL = 3_651_775
FULL_EXTRA = 512
FULL_DIGEST = "4638243d10a8ccff"
SMOKE_DIGEST = "67349aa7cfbaa376"

def count_formula(max_length: int) -> int:
    n = sum(range(2, max_length + 1))
    edge = max_length - 1
    return (math.comb(n + 4, 5) - 2 * math.comb(n - edge + 4, 5)
            + math.comb(n - 2 * edge + 4, 5))

def compile_checker(path: Path) -> None:
    compiler = shutil.which("clang++") or shutil.which("g++") or shutil.which("c++")
    if compiler is None:
        raise RuntimeError("C++17 compiler required")
    subprocess.run([compiler, "-std=c++17", "-O3", "-Wall", "-Wextra",
                    "-Werror", str(SOURCE), "-o", str(path)], check=True)

def run_census(binary: Path, max_length: int) -> dict:
    proc = subprocess.run([str(binary), str(max_length)], check=True,
                          text=True, capture_output=True)
    pat = (r"max_length=(\d+) checked=(\d+) pruned=(\d+) residual=(\d+) "
           r"bad=(\d+) equality_residual=(\d+) residual_min=(\d+/\d+) "
           r"extra=(\d+) extra_bad=(\d+) extra_min=(\d+/\d+) "
           r"digest=([0-9a-f]+)")
    m = re.search(pat, proc.stdout)
    if m is None:
        raise AssertionError("missing exact certificate summary: " + proc.stdout)
    keys = ["max_length", "cases", "symbolically_dispatched", "exact_base",
            "bad", "sharp_base", "minimum_base", "exact_boundary16",
            "bad_boundary16", "minimum_boundary16", "fnv64"]
    result = dict(zip(keys, m.groups()))
    for key in ["max_length", "cases", "symbolically_dispatched", "exact_base",
                "bad", "sharp_base", "exact_boundary16", "bad_boundary16"]:
        result[key] = int(result[key])
    assert result["cases"] == count_formula(max_length), result
    assert result["symbolically_dispatched"] + result["exact_base"] == result["cases"], result
    assert result["bad"] == result["bad_boundary16"] == 0, result
    assert result["minimum_base"] == "562/1405" and result["sharp_base"] == 1, result
    return result

def main() -> None:
    p = argparse.ArgumentParser()
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="full dual-DP 3.65m+512 core")
    mode.add_argument("--smoke", action="store_true", help="148421-case dual-DP smoke")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    with tempfile.TemporaryDirectory(prefix="m079_chain5_sharp_") as td:
        binary = Path(td) / "checker"
        compile_checker(binary)
        r = run_census(binary, 15 if args.check else 8)
    if args.check:
        assert (r["cases"], r["symbolically_dispatched"], r["exact_base"],
                r["exact_boundary16"], r["minimum_boundary16"], r["fnv64"]) == (
                FULL_CASES, FULL_PRUNED, FULL_RESIDUAL, FULL_EXTRA,
                "1589/3500", FULL_DIGEST), r
    else:
        assert r["cases"] == 226_135 and r["exact_base"] == 148_421, r
        assert r["fnv64"] == SMOKE_DIGEST, r
    print(json.dumps(r, sort_keys=True) if args.json else str(r))

if __name__ == "__main__":
    main()
