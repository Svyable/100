#!/usr/bin/env python3
"""M078: finite six-vertex separator by induced four-vertex paths.

This is an exact finite census certificate, NOT a reconstruction theorem and
NOT an independently reviewed mathematical novelty claim.

  python3 scripts/m078_p4_separator.py --write
  python3 scripts/m078_p4_separator.py --check
  python3 scripts/m078_p4_separator.py --check --json

Search: generate the 156 unlabeled n=6 graphs, count induced P4 directly.
Checker: certify census separately (Burnside + degree-canonical forms), recover
degrees and triangles from the vertex-deleted cards, recover P4 from card P4
counts divided by n-4=2, using a different predicate (BFS connectivity).
"""
import argparse
import hashlib
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from mines.deck_invariants import (_adjacency_degrees, _card_triangles,
                                   _cards, _direct_triangles, _kelly_degrees)
from probes.graphs import (KNOWN_GRAPH_COUNTS, brute_canonical, census, certify_census,
                           edge_set, pair_order, to_adjacency)
from rank import ROOT

CERTIFICATE = ROOT / "data/reference/m078_p4_pairs.json"


def induced_path4_by_degrees(adjacency, vertices):
    """Four distinct vertices induce P4 iff induced degrees are 1,1,2,2."""
    ds = [sum((adjacency[v] >> w) & 1 for w in vertices if w != v)
          for v in vertices]
    return sorted(ds) == [1, 1, 2, 2]


def induced_path4_by_connectivity(adjacency, vertices):
    """Independent definition: a connected 3-edge tree with no degree-three centre."""
    vset = set(vertices)
    edges = sum((adjacency[a] >> b) & 1 for a, b in combinations(vertices, 2))
    if edges != 3 or any(sum((adjacency[v] >> w) & 1 for w in vertices if w != v) > 2 for v in vertices):
        return False
    visited, pending = {vertices[0]}, [vertices[0]]
    while pending:
        v = pending.pop()
        for w in vertices:
            if w not in visited and w in vset and ((adjacency[v] >> w) & 1):
                visited.add(w)
                pending.append(w)
    return len(visited) == 4


def direct_path4_count(n, code):
    adjacency = to_adjacency(n, code)
    return sum(induced_path4_by_degrees(adjacency, vs)
               for vs in combinations(range(n), 4))


def card_path4_count(n, code):
    """Kelly's identity: sum_v p4(G-v) = (n-4)*p4(G), for n>4."""
    if n <= 4:
        raise ValueError("the vertex-deleted cards must be larger than four vertices")
    count = sum(
        induced_path4_by_connectivity(card, vs)
        for card in _cards(n, code)
        for vs in combinations(range(n - 1), 4)
    )
    if count % (n - 4):
        raise ValueError("card count not divisible by n-4")
    return count // (n - 4)


# Explicit P4-free, nonisomorphic seven-vertex witnesses.
# The paw is a triangle with a fourth (pendant) vertex.
SHARP_G_EDGES = ((0, 1), (0, 2), (0, 3), (4, 5), (4, 6), (5, 6))
SHARP_H_EDGES = ((0, 1), (1, 2), (3, 4), (3, 5), (4, 5), (3, 6))


def code_from_edges(n, edges):
    all_pairs = pair_order(n)
    positions = {edge: bit for bit, edge in enumerate(all_pairs)}
    if any(edge not in positions for edge in edges):
        raise ValueError("bad edge in sharpness witness")
    return sum(1 << positions[edge] for edge in edges)


def sharpness_witness(extra_isolates=0):
    """Pair showing failure for every n=7+t, t>=0, by isolate padding."""
    if type(extra_isolates) is not int or extra_isolates < 0:
        raise ValueError("isolate count must be a nonnegative integer")
    n = 7 + extra_isolates
    codes = (code_from_edges(n, SHARP_G_EDGES), code_from_edges(n, SHARP_H_EDGES))
    values = [(_adjacency_degrees(n, code), _direct_triangles(n, code),
               direct_path4_count(n, code)) for code in codes]
    if values[0] != values[1]:
        raise ValueError("seven-vertex witness signatures differ")
    return {
        "order": n,
        "first": {"name": "K1,3 disjoint K3",
                  "edges": [list(p) for p in SHARP_G_EDGES], "edge_code": codes[0]},
        "second": {"name": "P3 disjoint paw",
                   "edges": [list(p) for p in SHARP_H_EDGES], "edge_code": codes[1]},
        "common_sorted_degrees": list(values[0][0]),
        "common_triangles": values[0][1],
        "common_induced_p4": values[0][2],
        "isolate_padding": extra_isolates,
    }


def _records(codes, invariant):
    by_key = defaultdict(list)
    for code in codes:
        by_key[invariant(code)[:2]].append(code)
    records = []
    for (degrees, triangles), group in sorted(by_key.items()):
        for a, b in combinations(sorted(group), 2):
            pa, pb = invariant(a)[2], invariant(b)[2]
            records.append({
                "graph_a": a, "graph_b": b,
                "degree_sequence": list(degrees),
                "triangles": triangles,
                "induced_p4_a": pa, "induced_p4_b": pb,
            })
    return sorted(records, key=lambda x: (x["graph_a"], x["graph_b"]))


def _fingerprint(records):
    raw = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def derive():
    codes = census(6)
    if len(codes) != KNOWN_GRAPH_COUNTS[6]:
        raise ValueError("unexpected n=6 graph census")
    direct = lambda code: (_adjacency_degrees(6, code),
                           _direct_triangles(6, code), direct_path4_count(6, code))
    records = _records(codes, direct)
    if len(records) != 20 or any(r["induced_p4_a"] == r["induced_p4_b"] for r in records):
        raise ValueError("the candidate invariant does not separate all 20 collisions")
    return {
        "schema_version": 1,
        "problem_id": "M078",
        "scope": "All 156 nonisomorphic simple undirected graphs with six vertices",
        "invariant": "number of induced P4 subgraphs",
        "definition": "Four vertices inducing precisely a connected three-edge path",
        "base_key": "sorted degree sequence plus total triangle count",
        "graph_code": "Edge-bit integer using (0,1),(0,2),...,(4,5) in lexicographic order",
        "graph_count": len(codes),
        "base_key_collision_pairs": len(records),
        "residual_collision_pairs": 0,
        "records_sha256": _fingerprint(records),
        "collision_pairs": records,
        "sharpness_witness_n7": sharpness_witness(),
        "extension": "Appending t isolated vertices to both witnesses yields nonisomorphic graphs with the same signature for every t>=0.",
        "interpretation": "Finite six-vertex separator only; no claim of global reconstruction or literature novelty.",
    }


def verify(certificate):
    codes = census(6)
    if len(codes) != KNOWN_GRAPH_COUNTS[6]:
        raise ValueError("incorrect six-vertex count")
    certify_census(6, codes)  # independent Burnside count and canonicalization
    for code in codes:
        if direct_path4_count(6, code) != card_path4_count(6, code):
            raise ValueError(f"Kelly P4 count disagrees for graph {code}")
        if _adjacency_degrees(6, code) != _kelly_degrees(6, code):
            raise ValueError(f"Kelly degree sequence disagrees for graph {code}")
        if _direct_triangles(6, code) != _card_triangles(6, code):
            raise ValueError(f"Kelly triangle count disagrees for graph {code}")
    independent = lambda code: (_kelly_degrees(6, code),
                                _card_triangles(6, code), card_path4_count(6, code))
    records = _records(codes, independent)
    expected = dict(certificate)
    if expected.get("collision_pairs") != records:
        raise ValueError("collision pairs differ from independent card reconstruction")
    if expected.get("records_sha256") != _fingerprint(records):
        raise ValueError("collision pair digest differs")
    if len(records) != 20 or any(r["induced_p4_a"] == r["induced_p4_b"] for r in records):
        raise ValueError("the six-vertex P4 separation failed")
    witness = sharpness_witness()
    if expected.get("sharpness_witness_n7") != witness:
        raise ValueError("sharpness witness differs from pinned seven-vertex pair")
    c1, c2 = witness["first"]["edge_code"], witness["second"]["edge_code"]
    if brute_canonical(7, edge_set(7, c1)) == brute_canonical(7, edge_set(7, c2)):
        raise ValueError("sharpness witnesses are isomorphic")
    for code in (c1, c2):
        if (_kelly_degrees(7, code), _card_triangles(7, code), card_path4_count(7, code)) != (
            tuple(witness["common_sorted_degrees"]), witness["common_triangles"],
            witness["common_induced_p4"]):
            raise ValueError("seven-vertex witness fails independent card test")
    if expected != derive():
        raise ValueError("certificate fields do not match regenerated data")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        expected = derive()
        verify(expected)
        body = json.dumps(expected, ensure_ascii=False, indent=2) + "\n"
        if args.check and (not CERTIFICATE.is_file() or CERTIFICATE.read_text() != body):
            raise ValueError("stale P4 certificate: run --write and inspect diff")
        if args.write:
            CERTIFICATE.write_text(body, encoding="utf-8")
        if args.json:
            print(json.dumps({k: v for k, v in expected.items() if k != "collision_pairs"},
                             indent=2))
        else:
            print(f"OK: {expected['graph_count']} graph classes; "
                  f"{expected['base_key_collision_pairs']} original collisions; "
                  f"{expected['residual_collision_pairs']} after induced P4; "
                  f"certificate {expected['records_sha256'][:16]}")
    except ValueError as exc:
        print(f"M078 P4 verification failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
