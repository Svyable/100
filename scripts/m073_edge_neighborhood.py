#!/usr/bin/env python3
"""M073: source-bound two-square Ising edge-correlation certificate.

Finite source incidence verification + independent parity/spin calculations.
The continuum argument and its limitations are in research/M073_EDGE_NEIGHBORHOOD.md.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from itertools import product
from math import prod
import json

from m073_assortative2 import load_faces, histogram
from m073_information_alignment import coefficients_by_spins, coefficients_by_parity
from sidorenko_twoblock import numerator_by_faces

Q = Fraction
# Abstract vertices: 0=i, 1=f, 2=j, 3=k; 4=g_ij, 5=g_ik, 6=g_jk.
RUNG = ((0, 1), (0, 4), (4, 2), (2, 1),
        (0, 5), (5, 3), (3, 1), (2, 6), (6, 3))
FIRST_SQUARE = ((4, 7), (7, 8), (8, 0))
SECOND_A = ((5, 9), (9, 10), (10, 0))
SECOND_B = ((6, 9), (9, 10), (10, 2))
EDGES_A = RUNG + FIRST_SQUARE + SECOND_A
EDGES_B = RUNG + FIRST_SQUARE + SECOND_B

DEN = {0: 1, 4: 5, 6: 6, 8: 11, 10: 6, 12: 3}
NUM_A = {1: 1, 3: 2, 5: 7, 7: 6, 9: 11, 11: 4, 13: 1}
NUM_B = {1: 1, 3: 2, 5: 6, 7: 9, 9: 8, 11: 5, 13: 1}
RUNG_DEN = {0: 1, 4: 3, 6: 4}
RUNG_NUM = {1: 1, 3: 2, 5: 3, 7: 2}


def source_motifs(faces):
    """Construct every rooted 11-vertex 15-edge subgraph in the pinned H."""
    if len(faces) != 22 or len(set(map(frozenset, faces))) != 22:
        raise ValueError("source must contain 22 distinct faces")
    pair_faces = {}
    for fi, face in enumerate(faces):
        if len(face) != 3 or len(set(face)) != 3 or not all(0 <= x < 13 for x in face):
            raise ValueError("malformed triple")
        for a in range(3):
            for b in range(a + 1, 3):
                pair_faces.setdefault(frozenset((face[a], face[b])), []).append(fi)
    if len(pair_faces) != 33 or any(len(v) != 2 for v in pair_faces.values()):
        raise ValueError("pinned pair-twice property fails")
    witnesses = []
    for fi, face in enumerate(faces):
        for i in face:
            j, k = sorted(x for x in face if x != i)
            g = [next(t for t in pair_faces[frozenset(pair)] if t != fi)
                 for pair in ((i, j), (i, k), (j, k))]
            x = [next(p for p in faces[t] if p not in face) for t in g]
            if len(set(x)) != 3:
                raise ValueError("third-point collision")
            h = [next(t for t in pair_faces[frozenset((v, p))] if t != gt)
                 for v, p, gt in zip((i, i, j), x, g)]
            if h[0] == h[2]:
                raise ValueError("two-square uniform motif obstruction")
            kind = "A" if h[0] != h[1] else "B"
            z = 1 if kind == "A" else 2
            vertices = (i, 13 + fi, j, k, 13 + g[0], 13 + g[1],
                        13 + g[2], x[0], 13 + h[0], x[z], 13 + h[z])
            edges = EDGES_A if kind == "A" else EDGES_B
            if len(set(vertices)) != 11 or len(set(map(frozenset, edges))) != 15:
                raise ValueError("degenerate local motif")
            for a, b in edges:
                u, v = vertices[a], vertices[b]
                if not ((u < 13 <= v and u in faces[v - 13]) or
                        (v < 13 <= u and v in faces[u - 13])):
                    raise ValueError("invented incidence edge")
            witnesses.append((fi, i, kind, vertices))
    if len(witnesses) != 66:
        raise ValueError("incorrect incidence edge count")
    return witnesses


def independent_source_counts(faces):
    """Different incidence-neighbor search, no pair_faces map or abstract graph."""
    face_sets = [set(f) for f in faces]
    kinds = Counter()
    for fi, face in enumerate(face_sets):
        for i in face:
            j, k = sorted(face - {i})
            other = []
            for pair in ({i, j}, {i, k}, {j, k}):
                candidates = [t for t, g in enumerate(face_sets)
                              if t != fi and pair <= g]
                if len(candidates) != 1:
                    raise ValueError("nonunique alternate face")
                other.append(candidates[0])
            extra = [next(iter(face_sets[t] - face)) for t in other]
            bridges = []
            for v, x, g in zip((i, i, j), extra, other):
                candidates = [t for t, f in enumerate(face_sets)
                              if t != g and {v, x} <= f]
                if len(candidates) != 1:
                    raise ValueError("nonunique square completion")
                bridges.append(candidates[0])
            if bridges[0] == bridges[2]:
                raise ValueError("square bridge collision")
            kinds["A" if bridges[0] != bridges[1] else "B"] += 1
    return dict(kinds)


def surface_link_certificate(faces, points):
    """Link-cycle theorem premise for a closed simplicial triangulated surface.

    Returns the degree-four count and predicted A/B incidence counts.
    Uses only triangle links, not the square-completion search above.
    """
    if points < 1 or len(set(map(frozenset, faces))) != len(faces):
        raise ValueError("invalid simplicial complex")
    links = [dict() for _ in range(points)]
    pair_count = Counter()
    for face in faces:
        if len(face) != 3 or len(set(face)) != 3 or any(
                not isinstance(v, int) or not 0 <= v < points for v in face):
            raise ValueError("invalid face")
        for i in face:
            j, k = (v for v in face if v != i)
            links[i].setdefault(j, set()).add(k)
            links[i].setdefault(k, set()).add(j)
            pair_count[frozenset((j, k))] += 1
    if any(n != 2 for n in pair_count.values()):
        raise ValueError("surface has a boundary or nonmanifold edge")
    degrees = []
    for neighbors in links:
        if len(neighbors) < 4 or any(len(adj) != 2 for adj in neighbors.values()):
            raise ValueError("vertex link is not a cycle of length at least four")
        seen = {next(iter(neighbors))}
        frontier = list(seen)
        while frontier:
            for x in neighbors[frontier.pop()]:
                if x not in seen:
                    seen.add(x)
                    frontier.append(x)
        if len(seen) != len(neighbors):
            raise ValueError("vertex link has disconnected cycles")
        degrees.append(len(neighbors))
    b = 4 * sum(d == 4 for d in degrees)
    a = 3 * len(faces) - b
    return {"A": a, "B": b}, Counter(degrees)


def boundary_polynomial(edges, odd=()):
    """Direct high-temperature parity enumeration, all 2^15 edge subsets."""
    masks = [(1 << a) ^ (1 << b) for a, b in edges]
    target = sum(1 << v for v in odd)
    out = Counter()
    for subset in range(1 << len(edges)):
        parity = 0
        for e, mask in enumerate(masks):
            if (subset >> e) & 1:
                parity ^= mask
        if parity == target:
            out[subset.bit_count()] += 1
    return dict(sorted(out.items()))


def spin_correlation(edges, q):
    """Independent full 2^11 spin partition function (no parity enumeration)."""
    if not 0 <= q < 1:
        raise ValueError("requires 0 <= q < 1")
    total = signed = Q(0)
    for spins in product((-1, 1), repeat=11):
        weight = prod(1 + q * spins[a] * spins[b] for a, b in edges)
        total += weight
        signed += weight * spins[0] * spins[1]
    return signed / total


def poly_mul(a, b):
    out = Counter()
    for i, x in a.items():
        for j, y in b.items():
            out[i + j] += x * y
    return {k: v for k, v in out.items() if v}


def poly_sub(a, b):
    out = Counter(a)
    out.subtract(b)
    return {k: v for k, v in out.items() if v}


def evaluate(poly, q):
    return sum((v * q**k for k, v in poly.items()), Q(0))


def improvement_polynomial():
    # q^5(1-q^2)^3(1+q^2)(2q^6+2q^4+3q^2+1)
    return poly_mul({5: 1},
                    poly_mul({0: 1, 2: -3, 4: 3, 6: -1},
                             poly_mul({0: 1, 2: 1},
                                      {0: 1, 2: 3, 4: 2, 6: 2})))


def source_sample(faces):
    q, h = Q(1, 3), Q(2443, 10000)
    # Full 23-coefficient even-subgraph polynomial, not just the 4/6-cycle truncation.
    coefficients = coefficients_by_spins(faces, 13)
    if coefficients != coefficients_by_parity(faces, 13):
        raise AssertionError("full source spectrum disagrees across independent recurrences")
    margin = sum(c * q**(2*k) for k, c in enumerate(coefficients))
    R = 1 - h * h
    ka = evaluate(NUM_A, q) / evaluate(DEN, q)
    kb = evaluate(NUM_B, q) / evaluate(DEN, q)
    k0 = evaluate(RUNG_NUM, q) / evaluate(RUNG_DEN, q)
    exponent = (Q(66) - 54 * ka - 12 * kb) / 4
    old_exponent = Q(66, 4) * (1 - k0)
    uniform_exponent = Q(66, 4) * (1 - kb)
    if (ka, kb, exponent, old_exponent, uniform_exponent) != (
            Q(21899, 53397), Q(21755, 53397), Q(10199, 1047),
            Q(187, 19), Q(174031, 17799)):
        raise AssertionError("exact exponent drift")
    # Exact integer-power comparisons; no floating-point proof.
    old = margin**old_exponent.denominator * R**old_exponent.numerator
    # The large uniform-B comparison uses direct integer powers to avoid
    # expensive repeated Fraction gcds on million-bit numerators.
    uniform_below = (margin.numerator**uniform_exponent.denominator *
                     R.numerator**uniform_exponent.numerator <
                     margin.denominator**uniform_exponent.denominator *
                     R.denominator**uniform_exponent.numerator)
    new = margin**exponent.denominator * R**exponent.numerator
    if not old < 1 or not uniform_below or not new > 1:
        raise AssertionError("strict weighted-only certificate failed")
    weights = ((12443, 20000), (20000, 7557))
    direct = numerator_by_faces(faces, weights)
    factors = [12443**z * 20000**(3 - z) +
               20000**z * 7557**(3 - z) for z in range(4)]
    compressed = sum(m * prod(factors[z]**n for z, n in enumerate(profile))
                     for profile, m in histogram(faces).items())
    if direct != compressed:
        raise AssertionError("independent point-histogram density disagrees")
    actual_ratio = Q((1 << 97) * direct, 60000**66)
    if actual_ratio <= 1 or actual_ratio**exponent.denominator < new:
        raise AssertionError("full H violates certified two-square lower bound")
    return {
        "weights": ["12443/20000", "1", "7557/20000"],
        "full_even_subgraph_coefficients": len(coefficients),
        "full_even_subgraph_factor_at_q": str(margin),
        "q": str(q), "h": str(h), "R": str(R),
        "K_A": str(ka), "K_B": str(kb),
        "old_exponent": str(old_exponent), "uniform_exponent": str(uniform_exponent),
        "new_exponent": str(exponent),
        "rung_plus_full_spectrum_below_one": old < 1,
        "uniform_two_square_plus_full_spectrum_below_one": uniform_below,
        "weighted_two_square_plus_full_spectrum_above_one": new > 1,
        "density_paths_agree": direct == compressed,
        "old_lower_ratio_approx": round(float(margin) * float(R)**float(old_exponent), 9),
        "uniform_lower_ratio_approx": round(float(margin) * float(R)**float(uniform_exponent), 9),
        "new_lower_ratio_approx": round(float(margin) * float(R)**float(exponent), 9),
        "actual_ratio_approx": round(float(actual_ratio), 9),
    }


def audit():
    faces = load_faces()
    witnesses = source_motifs(faces)
    counts = dict(Counter(kind for _, _, kind, _ in witnesses))
    surface_counts, degree_hist = surface_link_certificate(faces, 13)
    if (counts != {"A": 54, "B": 12} or
            independent_source_counts(faces) != counts or
            surface_counts != counts or degree_hist != {4: 3, 5: 6, 6: 4}):
        raise AssertionError("source incidence or surface-link census drift")
    for edges, expected_num in ((EDGES_A, NUM_A), (EDGES_B, NUM_B)):
        if boundary_polynomial(edges) != DEN:
            raise AssertionError("even boundary polynomial drift")
        if boundary_polynomial(edges, (0, 1)) != expected_num:
            raise AssertionError("odd boundary polynomial drift")
        for q in (Q(0), Q(1, 3), Q(3, 4)):
            if spin_correlation(edges, q) != evaluate(expected_num, q) / evaluate(DEN, q):
                raise AssertionError("independent spin and parity disagree")
    if poly_sub(NUM_A, NUM_B) != {5: 1, 7: -3, 9: 3, 11: -1}:
        raise AssertionError("A/B strict ordering drift")
    if poly_sub(poly_mul(NUM_B, RUNG_DEN),
                poly_mul(RUNG_NUM, DEN)) != improvement_polynomial():
        raise AssertionError("B/rung strict improvement factorization drift")
    return {
        "rooted_incidence_edges": len(witnesses),
        "class_counts": counts,
        "surface_link_degrees": dict(degree_hist),
        "motif_vertices": 11, "motif_edges": 15,
        "even_boundary": DEN, "odd_boundary_A": NUM_A, "odd_boundary_B": NUM_B,
        "strict_A_over_B": "q^5(1-q^2)^3/D(q)",
        "strict_B_over_rung": "q^5(1-q^2)^3(1+q^2)(1+3q^2+2q^4+2q^6)/(D(q)D0(q))",
        "sample": source_sample(faces),
        "scope": "source-pinned two-block bound; author-checked, no independent mathematical review",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    print(json.dumps(audit(), sort_keys=True, indent=2))
