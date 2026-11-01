#!/usr/bin/env python3
"""Exact regression and adversarial controls for M073 antiferromagnetic stability.

The continuum proof is in research/M073_ANTIFERRO_STABILITY.md.
This program does not infer a continuum theorem from finite tests.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import product
import json

from m073_assortative2 import load_faces, histogram, exact_gap, graph_counts
from sidorenko_twoblock import numerator_by_faces

Q = Fraction
SAMPLE = (19, 32, 13)
EXPECTED = {"vertices": 35, "edges": 66, "wedges": 204, "c4": 33, "c6": 88}


def density(n, edges, u, b, delta):
    """Direct independent 2^n spin sum, with exact rational arithmetic."""
    if not (0 < u <= b and 0 <= delta <= u):
        raise ValueError("requires 0<u<=b and 0<=delta<=u")
    if any(i == j or i < 0 or j < 0 or i >= n or j >= n for i, j in edges):
        raise ValueError("invalid edge")
    if len({tuple(sorted(e)) for e in edges}) != len(edges):
        raise ValueError("duplicate edge")
    W = ((u + delta, b), (b, u - delta))
    return sum((product_of_edges(bits, edges, W)
                for bits in product((0, 1), repeat=n)), Q(0)) / (1 << n)


def product_of_edges(bits, edges, W):
    value = Q(1)
    for i, j in edges:
        value *= W[bits[i]][bits[j]]
    return value


def edge_spin_correlation(n, edges, u, b, edge):
    """Correlation of original antiferromagnetic spins at delta=0."""
    if edge not in edges and edge[::-1] not in edges:
        raise ValueError("edge absent")
    W = ((u, b), (b, u))
    total = Q(0)
    signed = Q(0)
    for bits in product((0, 1), repeat=n):
        weight = product_of_edges(bits, edges, W)
        total += weight
        signed += weight * (1 if bits[edge[0]] == bits[edge[1]] else -1)
    return signed / total


def exact_relative_bound(n, edges, u, b, delta):
    """Clear rational exponents by positive integer powers."""
    t = density(n, edges, u, b, delta)
    t0 = density(n, edges, u, b, Q(0))
    q = (b - u) / (b + u)
    exponent = Q(len(edges), 4) * (1 - q)
    base = 1 - (delta / u) ** 2
    # If exponent=N/D, (t/t0)^D >= base^N is equivalent.
    return (t / t0) ** exponent.denominator >= base ** exponent.numerator


def sample_certificate():
    faces = load_faces()
    counts = graph_counts(faces)
    if counts != EXPECTED:
        raise AssertionError(f"pinned M073 counts drifted: {counts}")
    profiles = histogram(faces)
    A, B, C = SAMPLE
    gap, _ = exact_gap(A, B, C, profiles)
    W = ((A, B), (B, C))
    direct = numerator_by_faces(faces, W)
    face = [A**k * B**(3-k) + B**k * C**(3-k) for k in range(4)]
    compressed = sum(mult * face[0]**h[0] * face[1]**h[1]
                     * face[2]**h[2] * face[3]**h[3]
                     for h, mult in profiles.items())
    if direct != compressed:
        raise AssertionError("independent exact density paths disagree")
    P = A + 2*B + C
    if gap != (1 << 97) * direct - P**66 or gap <= 0:
        raise AssertionError("exact rational sample failed")
    # u=1/2, b=1, delta=3/32, q=1/3, p=3/4.
    margin = Q(1114, 729)
    stability = Q(247, 256) ** 11
    if margin * stability <= 1:
        raise AssertionError("new disassortative cone sample is not certified")
    ratio = Q((1 << 97) * direct, P**66)
    if ratio < margin * stability:
        raise AssertionError("relative theorem bound failed at sample")
    return {
        "source_graph": counts,
        "source_assignments": sum(profiles.values()),
        "sample_weights": [f"{v}/32" for v in SAMPLE],
        "p": "3/4", "q": "1/3", "delta_over_u": "3/16",
        "margin": "1114/729", "stability": "(247/256)^11",
        "strict_sufficient_condition": True,
        "two_exact_density_paths_agree": True,
        "exact_gap_positive": True,
        "ratio_approx": round(float(ratio), 10),
        "certified_lower_ratio_approx": round(float(margin * stability), 10),
        "scope": "Two-block restricted inequality only; no finite Sidorenko host or independent review",
    }


def adversarial_audit():
    graphs = [
        (2, [(0, 1)]),
        (3, [(0, 1), (1, 2)]),
        (4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
        (6, [(i, j) for i in range(3) for j in range(3, 6)
             if (i, j) != (2, 5)]),
    ]
    cases = [(Q(1, 2), Q(1), Q(3, 32)),
             (Q(3, 4), Q(1), Q(1, 8))]
    for n, edges in graphs:
        for u, b, delta in cases:
            if not exact_relative_bound(n, edges, u, b, delta):
                raise AssertionError(f"relative bound failed on {n}-vertex graph")
            q = (b-u)/(b+u)
            for edge in edges:
                if edge_spin_correlation(n, edges, u, b, edge) > -q:
                    raise AssertionError("bipartite edge correlation gate failed")
    triangle = [(0, 1), (1, 2), (0, 2)]
    corr = edge_spin_correlation(3, triangle, Q(1, 2), Q(1), (0, 1))
    if corr != Q(-3, 13) or not corr > Q(-1, 3):
        raise AssertionError("nonbipartite negative control did not fail")
    return {"bipartite_graphs": len(graphs), "rational_parameter_sets": len(cases),
            "relative_checks": len(graphs) * len(cases),
            "nonbipartite_triangle_correlation": "-3/13",
            "triangle_violates_bipartite_edge_gate": True}


def audit():
    return {"certificate": sample_certificate(), "adversarial": adversarial_audit()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    print(json.dumps(audit(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
