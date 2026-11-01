#!/usr/bin/env python3
"""A general degree-defect transfer check for finite outregular digraphs.

No triangle-free, oriented, or CH-specific assumption is needed. This script
does not prove the associated graph theory by itself: see
proofs/DEGREE_DEFECT_TRANSFER.md for the independent double-counting proof.
"""
import argparse
from itertools import combinations, product
import json


def inspect(out):
    """Return exact integer facts, or refuse graphs outside the theorem.

    out[u] is the complete list of destinations of outgoing arcs from u.
    The graph is simple and loopless; two-cycles are allowed.
    """
    if not isinstance(out, (tuple, list)) or len(out) < 2:
        raise ValueError("need at least two vertices")
    n = len(out)
    if not isinstance(out[0], (tuple, list)):
        raise ValueError("adjacency lists required")
    r = len(out[0])
    if not 1 <= r < n:
        raise ValueError("outdegree must lie between 1 and n-1")
    indegrees = [0] * n
    for u, targets in enumerate(out):
        if not isinstance(targets, (tuple, list)) or len(targets) != r:
            raise ValueError("outdegrees are not constant")
        if (any(type(v) is not int or not 0 <= v < n or v == u
                for v in targets) or len(set(targets)) != r):
            raise ValueError("invalid, repeated or looped directed edge")
        for v in targets:
            indegrees[v] += 1
    if max(indegrees) > r + 1:
        raise ValueError("maximum indegree exceeds r+1")

    high = tuple(u for u, d in enumerate(indegrees) if d == r + 1)
    low = tuple(u for u, d in enumerate(indegrees) if d < r)
    high_set = set(high)
    low_set = set(low)
    h, ell = len(high), len(low)
    high_to_low = sum(v in low_set for u in high for v in out[u])
    nonhigh_to_low = sum(v in low_set for u in range(n) if u not in high_set
                         for v in out[u])
    low_to_low = sum(v in low_set for u in low for v in out[u])
    q = min((sum(v in low_set for v in out[u]) for u in high), default=0)
    deficit = sum(r - indegrees[u] for u in low)
    low_indegree_sum = sum(indegrees[u] for u in low)
    if (deficit != h or low_indegree_sum != r*ell-h
            or h < ell or (q+1)*h > r*ell):
        raise AssertionError("degree-defect invariant broken")
    saturated = bool(high) and q >= r-1
    if saturated and (h != ell or nonhigh_to_low
                      or low_to_low
                      or any(indegrees[u] != r-1 for u in low)
                      or high_to_low != (r-1)*h):
        raise AssertionError("defect-transfer saturation failed")
    return {
        "n": n, "r": r, "indegrees": indegrees,
        "high": list(high), "low": list(low), "high_count": h,
        "low_count": ell, "q_min": q,
        "high_to_low": high_to_low,
        "nonhigh_to_low": nonhigh_to_low,
        "low_to_low": low_to_low,
        "deficit": deficit, "saturated": saturated,
    }


def audit(n, r):
    """Exhaust *all loopless outregular digraphs*, allowing two-cycles."""
    if (n, r) not in ((4, 1), (5, 2)):
        raise ValueError("cost-bounded audit supports only (4,1) and (5,2)")
    options = [list(combinations((v for v in range(n) if v != u), r))
               for u in range(n)]
    result = dict(total=0, cap=0, high=0, saturated=0,
                  nonsaturated_with_low_arcs=0, regular=0)
    for out in product(*options):
        result["total"] += 1
        try:
            rec = inspect(out)
        except ValueError as exc:
            if str(exc) != "maximum indegree exceeds r+1":
                raise
            continue
        result["cap"] += 1
        if not rec["high_count"]:
            result["regular"] += 1
            continue
        result["high"] += 1
        if rec["saturated"]:
            result["saturated"] += 1
        elif rec["low_to_low"]:
            result["nonsaturated_with_low_arcs"] += 1
    return result


EXPECTED = {
    "4,1": {"total": 81, "cap": 69, "high": 60, "saturated": 60,
            "nonsaturated_with_low_arcs": 0, "regular": 9},
    "5,2": {"total": 7776, "cap": 5436, "high": 5220, "saturated": 1080,
            "nonsaturated_with_low_arcs": 720, "regular": 216},
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="freeze exact finite audit counts")
    args = parser.parse_args(argv)
    result = {f"{n},{r}": audit(n, r) for n, r in ((4, 1), (5, 2))}
    if args.check and result != EXPECTED:
        raise SystemExit("INVALID: degree-defect audit changed")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
