#!/usr/bin/env python3
"""Exact one-vertex extension certificates for the publisher-pinned R(5,5,42) graphs.

This proves only nonextendibility of specified K42 colorings, not R(5,5)<=43.
The generator uses bitset K4 enumeration and DPLL with unit propagation.
The independent verifier uses four-subset enumeration and a separate propagation
implementation. A complete binary refutation tree is a replayable certificate.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from verify_mckay import CATALOG, SOURCE_SHA256, decode_graph6

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "data/ramsey_extension_certificate.json"
N = 42


def source_records():
    raw = CATALOG.read_bytes()
    if sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("source digest mismatch")
    records = raw.splitlines()
    if len(records) != 328 or len(set(records)) != 328:
        raise ValueError("source record count or uniqueness mismatch")
    return records


def bitset_k4(adj, red=True):
    n = len(adj)
    full = (1 << n) - 1
    rows = adj if red else [full ^ (1 << i) ^ adj[i] for i in range(n)]
    result = []
    for a in range(n):
        bs = rows[a] & (full ^ ((1 << (a + 1)) - 1))
        while bs:
            bbit = bs & -bs
            bs ^= bbit
            b = bbit.bit_length() - 1
            cs = rows[a] & rows[b] & (full ^ ((1 << (b + 1)) - 1))
            while cs:
                cbit = cs & -cs
                cs ^= cbit
                c = cbit.bit_length() - 1
                ds = rows[a] & rows[b] & rows[c] & (full ^ ((1 << (c + 1)) - 1))
                while ds:
                    dbit = ds & -ds
                    ds ^= dbit
                    result.append((a, b, c, dbit.bit_length() - 1))
    return result


def constraints_bitset(adj):
    red = bitset_k4(adj, True)
    blue = bitset_k4(adj, False)
    return [(0, sum(1 << j for j in c)) for c in red] + [
        (sum(1 << j for j in c), 0) for c in blue
    ], (len(red), len(blue))


def generate_tree(clauses, n=N, node_limit=1000000):
    nodes = 0

    def visit(pos, neg):
        nonlocal nodes
        nodes += 1
        if nodes > node_limit:
            raise RuntimeError("DPLL node limit reached; no conclusion")
        while True:
            score = [0] * n
            active = 0
            forced = False
            for p, q in clauses:
                if p & pos or q & neg:
                    continue
                rest = (p | q) & ~(pos | neg)
                if not rest:
                    return None
                if rest.bit_count() == 1:
                    if rest & p:
                        pos |= rest
                    else:
                        neg |= rest
                    forced = True
                    break
                active += 1
                weight = 1 << (5 - rest.bit_count())
                while rest:
                    bit = rest & -rest
                    rest ^= bit
                    score[bit.bit_length() - 1] += weight
            if not forced:
                break
        if not active:
            return {"sat": [pos, neg]}
        available = [j for j in range(n) if not ((pos | neg) >> j & 1)]
        j = max(available, key=lambda k: (score[k], -k))
        left = visit(pos | (1 << j), neg)
        if isinstance(left, dict):
            return left
        right = visit(pos, neg | (1 << j))
        if isinstance(right, dict):
            return right
        return [j, left, right]

    return visit(0, 0), nodes


def independent_k4_clauses(adj):
    """Different algorithm: all four-subsets and six direct edge checks."""
    n = len(adj)
    out = []
    for quad in combinations(range(n), 4):
        edges = [bool(adj[u] & (1 << v)) for u, v in combinations(quad, 2)]
        if all(edges):
            out.append((0, sum(1 << j for j in quad)))
        elif not any(edges):
            out.append((sum(1 << j for j in quad), 0))
    return out


def verify_tree(adj, tree):
    """Independently verify a complete branching proof, without DPLL search."""
    clauses = independent_k4_clauses(adj)
    n = len(adj)
    stats = [0, 0]

    def visit(node, assignments):
        # Literal-by-literal unit propagation, scanning clauses backwards.
        values = list(assignments)
        while True:
            changed = False
            for p, q in reversed(clauses):
                unresolved = []
                satisfied = False
                mask = p | q
                while mask:
                    bit = mask & -mask
                    mask ^= bit
                    j = bit.bit_length() - 1
                    want = 1 if p & bit else 0
                    if values[j] == want:
                        satisfied = True
                        break
                    if values[j] == -1:
                        unresolved.append((j, want))
                if satisfied:
                    continue
                if not unresolved:
                    if node is not None:
                        # Extra branching after a contradiction is not needed;
                        # reject to make the certificate canonical.
                        raise ValueError("branch after conflict")
                    stats[1] += 1
                    return
                if len(unresolved) == 1:
                    j, want = unresolved[0]
                    values[j] = want
                    changed = True
                    break
            if not changed:
                break
        if node is None:
            raise ValueError("false leaf without contradiction")
        if not isinstance(node, list) or len(node) != 3:
            raise ValueError("invalid branch node")
        j, left, right = node
        if type(j) is not int or not 0 <= j < n or values[j] != -1:
            raise ValueError("invalid or forced branch variable")
        stats[0] += 1
        l = list(values)
        l[j] = 1
        visit(left, l)
        r = list(values)
        r[j] = 0
        visit(right, r)

    visit(tree, [-1] * n)
    if stats[1] != stats[0] + 1:
        raise ValueError("incomplete binary proof")
    return {"branches": stats[0], "conflicts": stats[1], "clauses": len(clauses)}


def generate_first():
    """Generate the first proof afresh, for a reproducibility control."""
    adj = decode_graph6(source_records()[0])
    clauses, k4_counts = constraints_bitset(adj)
    tree, nodes = generate_tree(clauses)
    if isinstance(tree, dict):
        raise ValueError("K43 extension found: verify witness independently!")
    audit = verify_tree(adj, tree)
    if audit["clauses"] != len(clauses) or audit["branches"] * 2 + 1 != nodes:
        raise ValueError("independent checker disagrees")
    return {"record": 1, "red_k4": k4_counts[0], "blue_k4": k4_counts[1],
            "dpll_nodes": nodes, "tree": tree}


def generate_all():
    proofs = []
    for i, record in enumerate(source_records(), 1):
        adj = decode_graph6(record)
        if len(adj) != N:
            raise ValueError("wrong graph order")
        clauses, counts = constraints_bitset(adj)
        tree, nodes = generate_tree(clauses)
        if isinstance(tree, dict):
            raise ValueError(f"K43 extension candidate at source record {i}; independent verification required")
        proofs.append({"record": i, "red_k4": counts[0], "blue_k4": counts[1],
                       "dpll_nodes": nodes, "tree": tree})
    return {
        "scope": "Nonextendibility of exactly 328 publisher-pinned K42 colorings; no K43 nonexistence claim",
        "source_url": "https://users.cecs.anu.edu.au/~bdm/data/r55_42some.g6",
        "source_sha256": SOURCE_SHA256,
        "work_id": "X-M095-K42-EXTENSION",
        "scope_sha256": "d7ad170a225683e60d1fcaad99cf57638acffb2d293331aec72af84deda07660",
        "proofs": proofs,
    }


def tree_depth(tree):
    if tree is None:
        return 0
    if not isinstance(tree, list) or len(tree) != 3:
        raise ValueError("malformed proof tree")
    return 1 + max(tree_depth(tree[1]), tree_depth(tree[2]))


def verify_all(report):
    """Independent replay of all 328 *stored* trees, without DPLL search."""
    from collections import Counter
    records = source_records()
    if report.get("source_sha256") != SOURCE_SHA256 or report.get("work_id") != "X-M095-K42-EXTENSION":
        raise ValueError("source or work item mismatch")
    proofs = report.get("proofs")
    if not isinstance(proofs, list) or len(proofs) != len(records):
        raise ValueError("missing or extra proofs")
    distribution = Counter()
    depths = Counter()
    for i, (record, proof) in enumerate(zip(records, proofs), 1):
        if proof.get("record") != i:
            raise ValueError("missing, duplicated or out-of-order record")
        adj = decode_graph6(record)
        if len(adj) != N:
            raise ValueError("invalid graph order")
        stats = verify_tree(adj, proof["tree"])
        if stats["clauses"] != proof["red_k4"] + proof["blue_k4"]:
            raise ValueError(f"wrong K4 counts at record {i}")
        if stats["branches"] * 2 + 1 != proof["dpll_nodes"]:
            raise ValueError(f"wrong proof node count at record {i}")
        if proof["dpll_nodes"] > 51:
            raise ValueError("claimed 51-node upper bound false")
        depth = tree_depth(proof["tree"])
        if depth > 9:
            raise ValueError("claimed depth-nine bound false")
        depths[depth] += 1
        distribution[proof["dpll_nodes"]] += 1
    return {"records": len(records), "nonextendible": len(records),
            "max_nodes": max(distribution), "node_distribution": dict(sorted(distribution.items())),
            "max_depth": max(depths), "depth_distribution": dict(sorted(depths.items()))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--scan", type=int, default=0, help="optional bounded search of first N records")
    args = parser.parse_args()
    if args.scan:
        for i, record in enumerate(source_records()[:args.scan], 1):
            clauses, counts = constraints_bitset(decode_graph6(record))
            tree, nodes = generate_tree(clauses)
            print(json.dumps({"record": i, "nodes": nodes, "k4": counts,
                              "sat": isinstance(tree, dict)}))
        return
    if args.write:
        report = generate_all()
        CERT.write_text(json.dumps(report, separators=(",", ":"), sort_keys=True) + "\n")
    else:
        report = json.loads(CERT.read_text())
    if args.check or args.write:
        summary = verify_all(report)
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(json.dumps({"stored_records": len(report["proofs"])}, indent=2))


if __name__ == "__main__":
    main()
