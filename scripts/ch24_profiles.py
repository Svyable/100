#!/usr/bin/env python3
"""M074 (24,8) irregular-branch arithmetic: exact *necessary* indegree profiles.

This validates an elementary degree-profile consequence of a hypothetical
triangle-free, 8-outregular oriented graph. It is NOT a digraph existence
solver, an exhaustive 24-vertex search, or a new resolution of CH.
"""
import argparse
from collections import Counter
from functools import lru_cache

N, R, MAX_IN = 24, 8, 9

# Sharp local example: a triangle-free oriented 8-vertex graph with exactly
# four vertices of outdegree 2; the other four have outdegree 3.
LOCAL_EDGES = (
    (2, 0), (4, 0), (0, 5), (6, 0), (0, 7),
    (3, 1), (1, 4), (5, 1), (1, 6), (7, 1),
    (4, 2), (2, 5), (6, 2), (2, 7), (3, 4),
    (5, 3), (3, 6), (7, 3), (6, 4), (7, 5),
)


def local_witness_check(edges=LOCAL_EDGES):
    """Check the local 8-vertex *sharpness example*, not the 24-vertex claim."""
    if len(edges) != 20 or len(set(edges)) != len(edges):
        raise ValueError("Local sharpness witness must have 20 distinct directed arcs")
    out = [set() for _ in range(8)]
    inc = [set() for _ in range(8)]
    pairs = set()
    for u, v in edges:
        if not isinstance(u, int) or not isinstance(v, int) or not (
            0 <= u < 8 and 0 <= v < 8 and u != v
        ):
            raise ValueError("Invalid witness arc")
        pair = frozenset((u, v))
        if pair in pairs:
            raise ValueError("Local witness has a digon")
        pairs.add(pair)
        out[u].add(v)
        inc[v].add(u)
    for u in range(8):
        if not 2 <= len(out[u]) <= 3 or len(inc[u]) > 3:
            raise ValueError("Invalid local degree profile")
        for v in out[u]:
            if out[v] & inc[u]:
                raise ValueError("Local witness contains a directed triangle")
    if sum(len(out[u]) == 2 for u in range(8)) != 4:
        raise ValueError("Local witness does not attain four degree-two vertices")
    return {"arcs": len(edges),
            "outdegrees": [len(s) for s in out],
            "indegrees": [len(s) for s in inc],
            "outdegree_two_count": 4}


def local_degree_lower_bound():
    """Independent, finite *arithmetic* check of the inequality used in proof.

    For m arcs in H, t=#vertices with outdegree 2:
      m >= 24-t (all other outdegrees >=3);
      m <= 16+t (indegrees <=3 and indegree=3 forces outdegree=2).
    Hence t >= max(24-m,m-16) >=4. Both premises come from the
    hand-proved eight-vertex lemma; this function does not prove them.
    """
    out = {}
    for m in range(16, 22):
        out[m] = max(24 - m, m - 16)
    if min(out.values()) != 4:
        raise AssertionError("Local four-neighbor arithmetic drift")
    return out


def histograms_from_indegrees():
    """Enumerator A: bounded multisets of indegrees 0..9 summing to 24*8."""
    result = set()

    def go(degree, remaining_vertices, remaining_sum, counts):
        if degree == MAX_IN:
            if remaining_sum == MAX_IN * remaining_vertices:
                result.add(tuple(counts + [remaining_vertices]))
            return
        if degree:
            maximum = min(remaining_vertices, remaining_sum // degree)
        else:
            maximum = remaining_vertices
        for count in range(maximum + 1):
            go(degree + 1, remaining_vertices - count,
               remaining_sum - degree * count, counts + [count])

    go(0, N, N * R, [])
    return result


def histograms_from_deficit_partitions():
    """Enumerator B: partitions of 24 units of deficit from indegree 9."""
    result = set()

    def parts(remainder, upper, current):
        if remainder == 0:
            if len(current) <= N:
                counts = [0] * (MAX_IN + 1)
                for deficit in current:
                    counts[MAX_IN - deficit] += 1
                counts[MAX_IN] = N - len(current)
                result.add(tuple(counts))
            return
        for deficit in range(min(remainder, upper, MAX_IN), 0, -1):
            parts(remainder - deficit, deficit, current + (deficit,))

    parts(N * (MAX_IN - R), MAX_IN, ())
    return result


def admissible_histogram(hist):
    """Necessary global condition; certainly not a sufficiency predicate."""
    high = hist[MAX_IN]  # indegree 9
    low = sum(hist[:R])  # indegree <=7
    return high > 0 and low > 0 and 5 * high <= 8 * low


def profile_summary():
    a, b = histograms_from_indegrees(), histograms_from_deficit_partitions()
    if a != b:
        raise AssertionError("Independent indegree-histogram enumerators disagree")
    with_high = {hist for hist in a if hist[MAX_IN] > 0}
    survivors = {hist for hist in a if admissible_histogram(hist)}
    return {
        "all_numeric_indegree_histograms": len(a),
        "histograms_with_indegree_nine": len(with_high),
        "histograms_surviving_necessary_5h_le_8l": len(survivors),
        "numeric_histograms_excluded_after_irregular_branch": len(with_high) - len(survivors),
        "max_indegree": MAX_IN,
        "note": "Only arithmetic indegree multisets; no 24-vertex graph existence or novelty claim",
    }


def check():
    local_witness_check()
    local_degree_lower_bound()
    results = profile_summary()
    if (results["all_numeric_indegree_histograms"],
        results["histograms_with_indegree_nine"],
        results["histograms_surviving_necessary_5h_le_8l"]) != (1076, 1075, 83):
        raise AssertionError("Frozen numeric profile census changed")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = check()
    print("M074 (24,8): {} numeric indegree histograms -> {} survivors after "
          "conditional 5h <= 8l; 4 low-degree neighbors per indegree-9 root".format(
              result["all_numeric_indegree_histograms"],
              result["histograms_surviving_necessary_5h_le_8l"]))
    print("Finite necessary condition only; does not construct or eliminate a 24-vertex graph.")


if __name__ == "__main__":
    main()
