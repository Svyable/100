#!/usr/bin/env python3
"""An exact boundary checker for a CH(27,9) *local* irregular-root lemma.

This excludes the z=4 degree-profile subfamily alpha=(2^7,a,8), 2<=a<=6,
assuming the prior sharp seven-vertex 16-arc theorem. It does not prove the
full finite CH(27,9) statement, or an unrestricted theorem.
"""
from collections import Counter
from itertools import combinations, combinations_with_replacement
import json

SIX_SHARP = (
    (1, 2, 3, 4, 5), (2, 3, 4, 5), (3,), (5,), (2,), (4,)
)


def graph_facts(out):
    """Direct adjacency-matrix oracle, independent of the bitmask search."""
    n = len(out)
    if any(type(v) is not int or not 0 <= v < n or v == u
           for u, row in enumerate(out) for v in row):
        raise ValueError("invalid vertex or loop")
    if any(len(set(row)) != len(row) for row in out):
        raise ValueError("repeated arc")
    adj = [[int(v in out[u]) for v in range(n)] for u in range(n)]
    if any(adj[u][v] and adj[v][u] for u in range(n) for v in range(n)):
        raise ValueError("digon")
    if any(adj[u][v] and adj[v][w] and adj[w][u]
           for u in range(n) for v in range(n) for w in range(n)):
        raise ValueError("directed triangle")
    indegrees = tuple(sum(adj[u][v] for u in range(n)) for v in range(n))
    return {"arcs": sum(map(len, out)), "indegrees": indegrees,
            "max_indegree": max(indegrees)}


def dense_six_orientation_audit():
    """All orientations of K6 minus one pair, the only 14-arc support up to labels.

    A 15-arc oriented graph has a 14-arc subgraph obtained by deleting an arc;
    deletion cannot create a triangle or increase indegree. Thus this covers
    every hypothetical >=14-arc counterexample up to relabeling.
    """
    edges = tuple((u, v) for u, v in combinations(range(6), 2)
                  if (u, v) != (0, 1))
    assert len(edges) == 14
    count_cap = count_good = 0
    for flags in range(1 << 14):
        out = [0] * 6
        indeg = [0] * 6
        for bit, (u, v) in enumerate(edges):
            if flags & (1 << bit):
                u, v = v, u
            out[u] |= 1 << v
            indeg[v] += 1
        if max(indeg) > 3:
            continue
        count_cap += 1
        # A triangle exists precisely when u -> v and v -> w and w -> u.
        if not any(out[v] & (1 << w) and out[w] & (1 << u)
                   for u in range(6) for v in range(6)
                   if out[u] & (1 << v) for w in range(6)):
            count_good += 1
    return {"orientations": 1 << 14,
            "indegree_cap_survivors": count_cap,
            "triangle_free_and_cap": count_good}


def target_profile(alpha, k):
    return (len(alpha) == 9 and len(k) == 10 and k.count(0) == 4
            and tuple(sorted(alpha)) in {
                tuple(sorted((2,)*7 + (a, 8))) for a in range(2, 7)
            })


def eligible_a(alpha, k):
    return sum(a >= k + 2 for a in alpha)


def b_six_cut(alpha, k):
    """Necessary six-positive-B-vertex cut for a profile with exactly four zeros."""
    if (len(alpha) != 9 or tuple(sorted(alpha)) != tuple(alpha)
            or len(k) != 10 or tuple(sorted(k)) != tuple(k)
            or k.count(0) != 4 or any(type(x) is not int or not 0 <= x <= 7 for x in k)):
        raise ValueError("expected sorted A profile and a sorted z=4 B profile")
    positives = [v for v in k if v]
    q = [eligible_a(alpha, v) for v in positives]
    floors = [1 + v - qi for v, qi in zip(positives, q)]
    return {"sum_k": sum(k), "q": q, "B_outgoing_floor": sum(floors),
            "six_subset_capacity": 39,
            "surplus": sum(alpha) - 18,
            "C_internal_lower": 63 - sum(k) - (sum(alpha) - 18)}


def eligible_profile(alpha, k):
    """Necessary relaxed cut and all B subset capacities, not graph feasibility."""
    m = sum(alpha)
    if sum(k) < 92 - 2*m:
        return False
    floors = sorted((max(0, 1 + v - eligible_a(alpha, v)) for v in k),
                    reverse=True)
    return all(sum(floors[:s]) <= s * (19 - s) // 2 for s in range(1, 11))


def report():
    sharp = graph_facts(SIX_SHARP)
    if sharp["arcs"] != 13 or sharp["max_indegree"] != 3:
        raise AssertionError("13-arc positive graph changed")
    dense = dense_six_orientation_audit()
    if dense["triangle_free_and_cap"]:
        raise AssertionError("14-arc counterexample: six-vertex lemma is false")
    by_a = {}
    for a in range(2, 7):
        alpha = tuple(sorted((2,)*7 + (a, 8)))
        # The arithmetic argument is universal in k. Enumerations below are
        # independent negative controls for the bounded interpretation.
        assert all(eligible_a(alpha, k) <= 7-k for k in range(1, 8))
        admissible = []
        for positive in combinations_with_replacement(range(1, 8), 6):
            k = (0,)*4 + positive
            if eligible_profile(alpha, k):
                cut = b_six_cut(alpha, k)
                if cut["B_outgoing_floor"] > 39:
                    raise AssertionError("bad necessary B capacity")
                if cut["sum_k"] > 37 or cut["C_internal_lower"] < 22-a:
                    raise AssertionError("cut lemma failed")
                admissible.append(k)
        by_a[str(a)] = {"relaxed_profiles_after_B_cuts": len(admissible),
                        "k_sum_values": dict(sorted(Counter(map(sum, admissible)).items())),
                        "first_relaxed_profile": admissible[0] if admissible else None}
    return {"six_vertex_sharp_example": sharp,
            "six_vertex_dense_audit": dense, "by_remaining_A_degree": by_a,
            "claim": "z=4 with alpha=(2^7,a,8), 2<=a<=6 impossible, conditional on prior seven-vertex cap",
            "boundary": "No graph on 27 vertices constructed; no CH(27,9) resolution or novelty verdict"}


def main():
    result = report()
    print(json.dumps(result, indent=2, sort_keys=True))
    assert result["by_remaining_A_degree"]["6"]["relaxed_profiles_after_B_cuts"] == 8
    assert all(result["by_remaining_A_degree"][str(a)]["relaxed_profiles_after_B_cuts"] == 0
               for a in range(2, 6))


if __name__ == "__main__":
    main()
