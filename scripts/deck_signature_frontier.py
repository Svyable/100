#!/usr/bin/env python3
"""Exact finite deck-motif signature frontier for graph reconstruction M078.

A card signature consists of paired (degree multiset, #K3, optionally #C4).
The 8-vertex generation extends *every* 7-vertex graph isomorphism class by
every subset of neighbours, a complete covering with repeated isomorphism
classes. Distinct signature counts are compared to independent Burnside
isomorphism-class counts. This is not a proof of general graph reconstruction.
"""
import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

from probes.graphs import burnside_count, census, to_adjacency
from rank import ROOT

OUTPUT = ROOT / "data" / "card_motif_signatures.json"
WITNESS = (
    [[0, 4], [0, 7], [1, 4], [1, 5], [1, 7], [2, 5], [2, 6],
     [3, 5], [3, 6], [4, 6]],
    [[0, 4], [0, 7], [1, 4], [1, 5], [2, 5], [2, 6], [2, 7],
     [3, 5], [3, 6], [4, 6]],
)


def adjacency(n, edges):
    rows = [0] * n
    for u, v in edges:
        if not (isinstance(u, int) and isinstance(v, int) and 0 <= u < v < n):
            raise ValueError("Edges must be distinct ordered pairs within 0..n-1")
        if (rows[u] >> v) & 1:
            raise ValueError("Duplicate edge")
        rows[u] |= 1 << v
        rows[v] |= 1 << u
    return rows


def four_cycles(rows):
    """Direct C4 count: every cycle contributes to two opposite-vertex pairs."""
    n = len(rows)
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            common = (rows[i] & rows[j]).bit_count()
            count += common * (common - 1) // 2
    assert count % 2 == 0
    return count // 2


def fast_signature(rows, with_squares=False):
    """Search path: bitset neighborhoods and vertex-incidence identities."""
    n = len(rows)
    deg = [r.bit_count() for r in rows]
    tri = [0] * n
    for a, b, c in combinations(range(n), 3):
        if rows[a] >> b & 1 and rows[a] >> c & 1 and rows[b] >> c & 1:
            tri[a] += 1
            tri[b] += 1
            tri[c] += 1
    triangles = sum(tri) // 3
    out = []
    for v in range(n):
        card_deg = tuple(sorted(deg[i] - (rows[i] >> v & 1) for i in range(n) if i != v))
        entry = [card_deg, triangles - tri[v]]
        if with_squares:
            # Count 4-cycles in each deleted card with masked common neighbors.
            mask = ((1 << n) - 1) ^ (1 << v)
            twice = 0
            for a in range(n):
                if a == v:
                    continue
                for b in range(a + 1, n):
                    if b == v:
                        continue
                    common = (rows[a] & rows[b] & mask).bit_count()
                    twice += common * (common - 1) // 2
            assert twice % 2 == 0
            entry.append(twice // 2)
        out.append(tuple(entry))
    return tuple(sorted(out))


def independent_signature(rows, with_squares=False):
    """Checker: physically rebuild every card as an edge set and count motifs."""
    n = len(rows)
    result = []
    for v in range(n):
        keep = tuple(i for i in range(n) if i != v)
        edges = {(i, j) for i, j in combinations(keep, 2) if rows[i] >> j & 1}
        d = {i: 0 for i in keep}
        for i, j in edges:
            d[i] += 1
            d[j] += 1
        deg = tuple(sorted(d.values()))
        t = sum(all((min(i, j), max(i, j)) in edges
                    for i, j in combinations(verts, 2))
                for verts in combinations(keep, 3))
        entry = [deg, t]
        if with_squares:
            squares = 0
            for a, b, c, d in combinations(keep, 4):
                for cyc in ((a, b, c, d), (a, b, d, c), (a, c, b, d)):
                    if all((min(cyc[k], cyc[(k + 1) % 4]), max(cyc[k], cyc[(k + 1) % 4])) in edges
                           for k in range(4)):
                        squares += 1
            entry.append(squares)
        result.append(tuple(entry))
    return tuple(sorted(result))


def instances(n):
    """Cover all n-vertex graphs, up to isomorphism (with duplicates at n=8)."""
    if n < 8:
        for code in census(n):
            yield to_adjacency(n, code)
        return
    if n != 8:
        raise ValueError("Exact frontier supports n=3..8")
    for code in census(7):
        base = to_adjacency(7, code)
        for neighbors in range(1 << 7):
            yield [row | (((neighbors >> i) & 1) << 7) for i, row in enumerate(base)] + [neighbors]


def signature_digest(keys):
    return hashlib.sha256("\n".join(repr(k) for k in sorted(keys)).encode("utf-8")).hexdigest()


def census_report(verify_cards=False, sample_only=False):
    summary = {}
    for n in range(3, 9):
        keys3, keys4 = set(), set()
        count = 0
        for rows in instances(n):
            key3 = fast_signature(rows)
            key4 = fast_signature(rows, with_squares=True)
            keys3.add(key3)
            keys4.add(key4)
            # Independent code path checks all cards except in explicit quick mode.
            if verify_cards and (not sample_only or n < 8 or count % 197 == 0):
                if independent_signature(rows) != key3 or independent_signature(rows, True) != key4:
                    raise ValueError(f"Card-motif check disagrees at n={n}, input={count}")
            count += 1
        classes = burnside_count(n)  # independent orbit-counting theorem
        if len(keys3) > classes or len(keys4) > classes:
            raise ValueError("An invariant cannot distinguish more than the isomorphism classes")
        if n < 8 and count != classes:
            raise ValueError(f"Incomplete {n}-graph enumeration")
        if n == 8 and count != 1044 * 128:
            raise ValueError("Incomplete one-vertex extension")
        summary[str(n)] = {
            "tested_graphs": count,
            "isomorphism_classes_burnside": classes,
            "degree_triangle_card_signatures": len(keys3),
            "degree_triangle_square_card_signatures": len(keys4),
            "degree_triangle_excess": classes - len(keys3),
            "degree_triangle_square_excess": classes - len(keys4),
            "degree_triangle_digest": signature_digest(keys3),
            "degree_triangle_square_digest": signature_digest(keys4),
        }
    a, b = (adjacency(8, edges) for edges in WITNESS)
    if independent_signature(a) != independent_signature(b) or fast_signature(a) != fast_signature(b):
        raise ValueError("The two witnesses do not share the S3 signature")
    if independent_signature(a, True) == independent_signature(b, True):
        raise ValueError("S4 does not distinguish the witnesses")
    if four_cycles(a) == four_cycles(b):
        raise ValueError("Witnesses are not distinguishable by a graph invariant")
    if summary["7"]["degree_triangle_excess"] or summary["8"]["degree_triangle_square_excess"]:
        raise ValueError("The expected sharp finite boundary fails")
    if summary["8"]["degree_triangle_excess"] <= 0:
        raise ValueError("The S3 boundary has no collision")
    return {
        "schema": "svyable.deck-motif-signatures.v1",
        "as_of": "2026-11-01",
        "claim": "The deck-computable S3 is complete for 3<=n<=7, not n=8. S4 is complete for 3<=n<=8.",
        "mathematical_novelty": "unconfirmed; finite computation inside previously verified full reconstruction range",
        "method": "all unlabeled 7-vertex parents extended in every one-vertex neighborhood; independent Burnside class count",
        "table": summary,
        "counterexample_S3_n8": {
            "edges": WITNESS,
            "degree_sequence": tuple(sorted(x.bit_count() for x in a)),
            "triangles": 0,
            "S3": fast_signature(a),
            "four_cycles": [four_cycles(a), four_cycles(b)],
            "note": "Both are triangle-free, share S3, and differ in C4. They are NOT a same-deck pair.",
        },
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--write", action="store_true")
    p.add_argument("--check", action="store_true")
    p.add_argument("--quick", action="store_true", help="Sample the independent card recheck; exhaustive signature search stays complete")
    opts = p.parse_args()
    data = census_report(verify_cards=opts.check, sample_only=opts.quick)
    serialized = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if opts.write:
        OUTPUT.write_text(serialized, encoding="utf-8")
    if opts.check and OUTPUT.read_text(encoding="utf-8") != serialized:
        raise SystemExit("Stale deck signature ledger: run python3 scripts/deck_signature_frontier.py --write")
    print("OK: " + ", ".join(
        f"n={n} S3={row['degree_triangle_card_signatures']} S4={row['degree_triangle_square_card_signatures']}"
        for n, row in data["table"].items()))


if __name__ == "__main__":
    main()
