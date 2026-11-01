#!/usr/bin/env python3
"""Independent K42 checker calibration, NOT one of the 36 agent trials.

Only --record writes evidence; --check replays all 328 graph6 witnesses and
the deliberate single-edge negative control against both exact checkers.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys
import tempfile
from time import perf_counter_ns

import benchmark
import verify_mckay as vm
from ramsey import verify as bitset_verify

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "benchmarks" / "calibrations" / "k42_checker.json"
SOURCE_FILES = ("scripts/verify_mckay.py", "scripts/ramsey.py",
                "scripts/k42_calibration.py")
VERSION = "svyable.k42-checker-calibration.v1"


def sha_file(path):
    return sha256(path.read_bytes()).hexdigest()


def assert_condition(holds, reason):
    if not holds:
        raise ValueError(reason)


def observe():
    """Return actual measured checker outcomes without treating them as agent output."""
    manifest = benchmark.load_manifest()
    task = next(t for t in manifest["tasks"] if t["id"] == "K42-REPLAY")
    assert_condition(task["class"] == "replay" and not task["eligible_for_novelty"],
                     "The K42 calibration requires a frozen known-replay contract")
    raw = vm.CATALOG.read_bytes()
    assert_condition(sha256(raw).hexdigest() == vm.SOURCE_SHA256,
                     "McKay source mismatch")
    assert_condition(raw.endswith(b"\n") and b"\r" not in raw,
                     "Catalog line ending mismatch")
    lines = raw.splitlines()
    assert_condition(len(lines) == vm.EXPECTED_RECORDS and
                     len(set(lines)) == vm.EXPECTED_RECORDS,
                     "Unexpected or duplicate catalog records")
    start = perf_counter_ns()
    bit_ns, triangle_ns = 0, 0
    first = None
    for idx, line in enumerate(lines):
        graph = vm.decode_graph6(line)
        assert_condition(len(graph) == vm.ORDER, "Wrong graph order")
        if idx == 0:
            first = graph
        t = perf_counter_ns()
        result = bitset_verify(vm.ORDER, vm.to_red_edges(graph), 5, 5)
        bit_ns += perf_counter_ns() - t
        assert_condition(result[0] is True, "Bitset K5 failure at record " + str(idx))
        t = perf_counter_ns()
        hit = vm.triangle_checker(graph)
        triangle_ns += perf_counter_ns() - t
        assert_condition(hit is None, "Triangle K5 failure at record " + str(idx))
    elapsed_ns = perf_counter_ns() - start

    # Deliberately flip a single edge on the FIRST certified original witness.
    changed = first.copy()
    a, b = 0, 2
    changed[a] ^= 1 << b
    changed[b] ^= 1 << a
    mutant_bit = bitset_verify(vm.ORDER, vm.to_red_edges(changed), 5, 5)
    mutant_triangle = vm.triangle_checker(changed)
    assert_condition(mutant_bit[0] is False and mutant_triangle is not None,
                     "Single-edge negative control escaped a checker")
    assert_condition(mutant_triangle[0] == ("red" if mutant_bit[1] else "blue"),
                     "Checker colors disagree on negative control")
    with tempfile.TemporaryDirectory() as temp:
        tampered = Path(temp) / "tampered.g6"
        tampered.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
        try:
            vm.replay(tampered)
        except ValueError as exc:
            assert_condition("SHA-256 mismatch" in str(exc),
                             "Tamper rejected for the wrong reason")
        else:
            raise ValueError("Tampered catalog escaped the real replay guard")
    return {
        "schema": VERSION,
        "kind": "known_certificate_checker_calibration",
        "trial_credit": False,
        "manifest_sha256": benchmark.digest(manifest),
        "frozen_source_commit": manifest["source_commit"],
        "catalog_sha256": vm.SOURCE_SHA256,
        "source_file_sha256": {path: sha_file(ROOT / path)
                               for path in SOURCE_FILES},
        "records_checked": len(lines),
        "vertices_per_record": vm.ORDER,
        "independent_checker_passes": {
            "bitset_K5": len(lines),
            "triangle_common_neighbor_K5": len(lines),
        },
        "single_edge_negative_control": {
            "record_index": 0,
            "edge_flipped": [a, b],
            "detected_by": ["bitset_K5", "triangle_common_neighbor_K5"],
            "monochromatic_color": mutant_triangle[0],
            "witness_vertices": list(mutant_triangle[1]),
        },
        "catalog_hash_tamper_detected": True,
        "wall_ns": elapsed_ns,
        "bitset_checker_ns": bit_ns,
        "triangle_checker_ns": triangle_ns,
        "observed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "runtime": {"python": platform.python_version(),
                    "system": platform.system(), "architecture": platform.machine()},
        "interpretation": ("Reproduction of the known R(5,5)>=43 lower bound "
                           "and checker negative control; NO agent-arm trial "
                           "and NO measured research speedup."),
    }


def verify_evidence(observed, frozen):
    assert_condition(set(observed) == set(frozen), "Calibration schema drift")
    volatile = {"wall_ns", "bitset_checker_ns", "triangle_checker_ns",
                "observed_at_utc", "runtime"}
    for key in sorted(set(observed) - volatile):
        assert_condition(observed[key] == frozen[key],
                         "Calibration evidence drift: " + key)
    for key in ("wall_ns", "bitset_checker_ns", "triangle_checker_ns"):
        value = frozen[key]
        assert_condition(type(value) is int and value > 0 and value < 3_600_000_000_000,
                         "Invalid recorded duration: " + key)
    assert_condition(frozen["bitset_checker_ns"] + frozen["triangle_checker_ns"] <= frozen["wall_ns"],
                     "Checker time exceeds measured overall wall time")
    assert_condition(type(frozen["observed_at_utc"]) is str
                     and "+00:00" in frozen["observed_at_utc"],
                     "Calibration must record UTC clock time")
    assert_condition(isinstance(frozen["runtime"], dict) and
                     set(frozen["runtime"]) == {"python", "system", "architecture"},
                     "Runtime metadata missing")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--record", action="store_true",
                       help="Write first measured checker calibration if absent")
    group.add_argument("--check", action="store_true",
                       help="Replay all 328 and validate frozen calibration")
    args = p.parse_args(argv)
    observed = observe()
    if args.record:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        if REPORT.exists():
            raise SystemExit("Existing calibration evidence; refusing overwrite")
        REPORT.write_text(json.dumps(observed, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")
        print("Recorded " + str(REPORT))
    else:
        recorded = json.loads(REPORT.read_text(encoding="utf-8"))
        verify_evidence(observed, recorded)
        print("OK: 328 K42 graph6 witnesses independently checked twice; "
              "single-edge and hash tamper controls detected; "
              "not an agent-arm trial")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
