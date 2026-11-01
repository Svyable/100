#!/usr/bin/env python3
"""Exact audit of the *type/parity input* to the M044 construction.

This does NOT build the manuscript's random matching graphs, group presentation,
or group-ring elements. In particular it does not verify ab=1 or ba != 1.
Source: openai/math at 4eaee87548250b2682affda7d05d947c05554bae,
2026-10-04 manuscript, sections/algebra.tex, random.tex, assembly.tex.
"""
from __future__ import annotations

import argparse
import json

Q = 128
MOD = 0x83  # x^7 + x + 1, used only to implement F_128 arithmetic
V = Q * Q + Q + 1


def gf_mul(a: int, b: int, mod: int = MOD) -> int:
    if not 0 <= a < Q or not 0 <= b < Q:
        raise ValueError("field element outside F_128")
    value = 0
    while b:
        if b & 1:
            value ^= a
        b >>= 1
        a <<= 1
        if a & Q:
            a ^= mod
    return value


def field_tables(mod: int = MOD):
    table = tuple(tuple(gf_mul(a, b, mod) for b in range(Q)) for a in range(Q))
    inv = [0] * Q
    for a in range(1, Q):
        candidates = [b for b in range(1, Q) if table[a][b] == 1]
        if len(candidates) != 1:
            raise ValueError("specified polynomial does not define a field")
        inv[a] = candidates[0]
    return table, inv


def normalize(vec, table, inv):
    first = next((x for x in vec if x), None)
    if first is None:
        raise ValueError("zero projective vector")
    return tuple(table[inv[first]][x] for x in vec)


def projective_vectors():
    # Each projective class has exactly one representative with leading 1.
    return ([(1, a, b) for a in range(Q) for b in range(Q)]
            + [(0, 1, a) for a in range(Q)] + [(0, 0, 1)])


def dot(a, b, table):
    return table[a[0]][b[0]] ^ table[a[1]][b[1]] ^ table[a[2]][b[2]]


def cross(a, b, table):
    return (
        table[a[1]][b[2]] ^ table[a[2]][b[1]],
        table[a[2]][b[0]] ^ table[a[0]][b[2]],
        table[a[0]][b[1]] ^ table[a[1]][b[0]],
    )


def projective_audit(mod: int = MOD):
    """Enumerate all 2,130,177 point-line incidences independently of paper."""
    table, inv = field_tables(mod)
    vectors = projective_vectors()
    assert len(vectors) == V == len(set(vectors))
    incidences = dict.fromkeys(vectors, 0)
    for line in vectors:
        pivot = next(i for i, x in enumerate(line) if x)
        free = [i for i in range(3) if i != pivot]
        # The 129 projective points of the two-dimensional kernel:
        # free coordinates (1,t) for t in F_128, plus (0,1).
        seen = set()
        for u, v in [(1, t) for t in range(Q)] + [(0, 1)]:
            coords = [0, 0, 0]
            coords[free[0]], coords[free[1]] = u, v
            rhs = table[line[free[0]]][u] ^ table[line[free[1]]][v]
            coords[pivot] = table[inv[line[pivot]]][rhs]
            point = normalize(coords, table, inv)
            if dot(line, point, table):
                raise AssertionError("invalid line incidence")
            seen.add(point)
            incidences[point] += 1
        if len(seen) != Q + 1:
            raise AssertionError("a line does not have 129 distinct points")
    if set(incidences.values()) != {Q + 1}:
        raise AssertionError("a point does not lie on 129 lines")
    # Distinct linear forms have rank two over a field, hence a unique
    # projective intersection. Verify deterministic adversarial pairs too.
    for i in range(0, V, 53):
        for j in (0, 1, 128, 129, 1000, V - 1):
            if i == j:
                continue
            x = cross(vectors[i], vectors[j], table)
            point = normalize(x, table, inv)
            if dot(vectors[i], point, table) or dot(vectors[j], point, table):
                raise AssertionError("pair of lines lacks common point")
    return {"field_order": Q, "projective_points": V,
            "projective_lines": V, "incidences": V * (Q + 1),
            "incidences_per_line": Q + 1, "lines_per_point": Q + 1}


def fano_complements():
    # The cyclic (7,3,1) difference set {0,1,3}.
    lines = [{i % 7, (i + 1) % 7, (i + 3) % 7} for i in range(7)]
    return [set(range(7)) - line for line in lines]


def verify_extra_parity(complements=None):
    ds = fano_complements() if complements is None else complements
    if len(ds) != 7 or any(len(d) != 4 for d in ds):
        raise ValueError("Fano complements must be seven 4-subsets")
    if len({frozenset(d) for d in ds}) != 7:
        raise ValueError("duplicate Fano complements")
    if any(len(a & b) != 2 for i, a in enumerate(ds)
           for b in ds[i + 1:]):
        raise ValueError("Fano complements have incorrect pair intersections")
    if any(sum(x in d for d in ds) != 4 for x in range(7)):
        raise ValueError("extra-letter frequency is not four")
    root = set(range(7))
    empty = set()
    ordinary_intersections = (1, Q + 1)
    # The manuscript's ordinary intersections are always odd. Extra
    # intersections must be even, except the unique root-root pair.
    for left in [empty, *ds, root]:
        for right in [empty, *ds, root]:
            if left is root and right is root:
                if any((ordinary + len(left & right)) % 2 != 0
                       for ordinary in ordinary_intersections):
                    raise AssertionError("root diagonal is not even")
            elif any((ordinary + len(left & right)) % 2 != 1
                     for ordinary in ordinary_intersections):
                raise AssertionError("off-root intersection not odd")
    return ds


def type_audit(m: int = 5, complements=None):
    if m < 5 or m % 4 != 1:
        raise ValueError("finite type check requires m>=5 and m=1 (mod 4)")
    ds = verify_extra_parity(complements)
    a = ((Q + 1) * m - 1) // 4
    b = ((Q + 1) * (m - 1)) // 4
    # A concrete disjoint allocation of one D-type vertex per line
    # class exists at m=5. Larger m need not use this allocation.
    if 7 * a + 1 > V or 7 * b > V:
        raise ValueError("this simple disjoint-class allocation is too small")
    a_counts = [a] * 7
    b_counts = [b] * 7
    for letter in range(7):
        if 1 + sum(a_counts[i] for i, d in enumerate(ds) if letter in d) != (Q + 1) * m:
            raise AssertionError("A extra-letter imbalance")
        if sum(b_counts[i] for i, d in enumerate(ds) if letter in d) != (Q + 1) * (m - 1):
            raise AssertionError("B extra-letter imbalance")
    return {"m": m, "A_vertices": V * m, "B_vertices": V * (m - 1),
            "A_D_vertices_per_type": a, "B_D_vertices_per_type": b,
            "A_root_extra_degree": 7, "ordinary_incidence_per_line": Q + 1,
            "type_intersection_parity": "pass",
            "matching_edges_constructed": False,
            "group_ring_products_checked": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = {"scope": "type-parity-only",
              "projective_plane": projective_audit(),
              "type_allocation": type_audit(),
              "witness_replayed": False}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
