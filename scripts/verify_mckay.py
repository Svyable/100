#!/usr/bin/env python3
"""Replay McKay's 328 known Ramsey(5,5,42) graph6 records without a solver.

The red/blue K5 exclusion is independently checked by:
  1. scripts/ramsey.py's bitset recursive clique search; and
  2. a separate triangle + common-neighbor pair enumerator.

This proves the *specific finite witnesses* are valid when the pinned source
bytes match, not that the catalog is complete or that R(5,5)=43.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys

from ramsey import verify as bitset_verify

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/reference/r55_42some.g6"
REPORT = ROOT / "data/ramsey_mckay_replay.json"
SOURCE_URL = "https://users.cecs.anu.edu.au/~bdm/data/r55_42some.g6"
# Confirmed against an independently published mirror manifest; don't silently
# refresh this digest if McKay's source ever changes.
SOURCE_SHA256 = "067902e853d87b49bcef0d1d4c0e3bbadd238ee18bc65341b079a3ca4780eccb"
EXPECTED_RECORDS = 328
ORDER = 42


def decode_graph6(line):
    """Decode graph6 for simple graphs of order 2..62; reject malformed bits."""
    if not isinstance(line, (str, bytes)):
        raise ValueError("graph6 record must be ASCII")
    if isinstance(line, str):
        try:
            line = line.encode("ascii")
        except UnicodeEncodeError as exc:
            raise ValueError("graph6 record must be ASCII") from exc
    if not line or not 63 <= line[0] <= 125:
        raise ValueError("unsupported graph6 order prefix")
    n = line[0] - 63
    if n < 2 or n > 62:
        raise ValueError("unsupported graph6 order")
    bit_count = n * (n - 1) // 2
    expected_chars = (bit_count + 5) // 6
    if len(line) != expected_chars + 1:
        raise ValueError("wrong graph6 record length")
    payload = [x - 63 for x in line[1:]]
    if any(not 0 <= x < 64 for x in payload):
        raise ValueError("graph6 payload has invalid character")
    spare = expected_chars * 6 - bit_count
    if spare and payload[-1] & ((1 << spare) - 1):
        raise ValueError("nonzero graph6 padding")
    adjacency = [0] * n
    for index, (u, v) in enumerate((u, v) for v in range(1, n) for u in range(v)):
        if payload[index // 6] & (1 << (5 - index % 6)):
            adjacency[u] |= 1 << v
            adjacency[v] |= 1 << u
    return adjacency


def to_red_edges(adjacency):
    """Convert the decoded bit matrix into the existing checker input schema."""
    return [
        [u, v] for u in range(len(adjacency))
        for v in range(u + 1, len(adjacency))
        if adjacency[u] & (1 << v)
    ]


def triangle_checker(adjacency):
    """Independent finite K5 finder using monochromatic triangles + one edge.

    If there is a monochromatic five-clique, its smallest three vertices form
    a monochromatic triangle whose two larger vertices lie in the same-color
    common neighborhood. Checking an edge there is necessary and sufficient.
    Returns (color, vertices) for a failure, else None.
    """
    n = len(adjacency)
    full = (1 << n) - 1
    for color in ("red", "blue"):
        neighbors = (adjacency if color == "red" else [
            full ^ (1 << v) ^ adjacency[v] for v in range(n)
        ])
        for a in range(n - 2):
            for b in range(a + 1, n - 1):
                if not (neighbors[a] & (1 << b)):
                    continue
                for c in range(b + 1, n):
                    if not (neighbors[a] & neighbors[b] & (1 << c)):
                        continue
                    # Any other member of the K5 must be larger than c.
                    common = (neighbors[a] & neighbors[b] & neighbors[c])
                    common &= full ^ ((1 << (c + 1)) - 1)
                    while common:
                        d_bit = common & -common
                        d = d_bit.bit_length() - 1
                        common ^= d_bit
                        second = common & neighbors[d]
                        if second:
                            e = (second & -second).bit_length() - 1
                            return color, (a, b, c, d, e)
    return None


def independently_check(adjacency):
    n = len(adjacency)
    if n < 5:
        raise ValueError("witness order too small")
    for u, row in enumerate(adjacency):
        if row >> n or row & (1 << u):
            raise ValueError("malformed simple graph adjacency")
        for v in range(u + 1, n):
            if bool(row & (1 << v)) != bool(adjacency[v] & (1 << u)):
                raise ValueError("asymmetric graph adjacency")
    # Two algorithms sharing only the decoded finite mathematical object.
    bitset_ok, red_hit, blue_hit = bitset_verify(n, to_red_edges(adjacency), 5, 5)
    triangle_hit = triangle_checker(adjacency)
    if not bitset_ok or triangle_hit is not None:
        raise ValueError(
            "monochromatic K5 detected; bitset red=%r blue=%r triangle=%r"
            % (red_hit, blue_hit, triangle_hit)
        )
    return True


def replay(catalog=CATALOG):
    raw = Path(catalog).read_bytes()
    if sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("McKay catalog SHA-256 mismatch; source not pinned")
    if not raw.endswith(b"\n") or b"\r" in raw:
        raise ValueError("catalog requires LF-terminated ASCII records")
    lines = raw.splitlines()
    if len(lines) != EXPECTED_RECORDS or len(set(lines)) != EXPECTED_RECORDS:
        raise ValueError("unexpected or duplicate graph6 source records")
    for i, record in enumerate(lines, 1):
        try:
            graph = decode_graph6(record)
            if len(graph) != ORDER:
                raise ValueError("unexpected graph order")
            independently_check(graph)
        except ValueError as exc:
            raise ValueError("graph6 record %d: %s" % (i, exc)) from exc
    return {
        "source_url": SOURCE_URL,
        "source_sha256": SOURCE_SHA256,
        "source_records_checked": EXPECTED_RECORDS,
        "vertices_per_graph": ORDER,
        "witnesses_including_color_swaps": EXPECTED_RECORDS * 2,
        "checkers": ["recursive_bitset_K5", "triangle_common_neighborhood_K5"],
        "known_lower_bound": "R(5,5) >= 43",
        "scope": ("Reproduced known valid K42 graph colorings only. "
                  "No completeness proof for all K42 colorings, "
                  "no K43 nonexistence proof, no resolution of R(5,5)."),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="replay and match frozen JSON")
    parser.add_argument("--catalog", type=Path, default=CATALOG,
                        help="alternative data source (still must match SHA-256)")
    args = parser.parse_args(argv)
    try:
        report = replay(args.catalog)
        if args.check:
            expected = json.loads(REPORT.read_text(encoding="utf-8"))
            if report != expected:
                raise ValueError("McKay replay report drift")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("INVALID: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
