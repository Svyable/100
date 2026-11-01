#!/usr/bin/env python3
"""Independent histogram audit of the enumeration-free CH (24,8) proof.

Checks only relaxed integer profiles, NOT the existence of a 24-vertex graph.
The mathematical proof is research/M074_WEIGHTED_DEFICIT.md.
"""
from collections import Counter
import json


def compositions(total, bins):
    """Enumerate count vectors, avoiding the original sorted-tuple generator."""
    if bins == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for rest in compositions(total - first, bins - 1):
                yield (first,) + rest


def alpha_histograms():
    return tuple(h for h in compositions(8, 6)
                 if sum(j * h[j] for j in range(6)) <= 5)


def k_histograms():
    return tuple(compositions(9, 7))


def capacity_violation(alpha_hist, k_hist):
    """Exact B-outdegree subset obstruction; no use of e(B,A) lower bound."""
    q = [sum(alpha_hist[d - 2] for d in range(k + 2, 8))
         for k in range(7)]
    floors = sorted((max(0, 1 + k - q[k])
                     for k, count in enumerate(k_hist)
                     for _ in range(count)), reverse=True)
    prefix = 0
    for s, value in enumerate(floors, 1):
        prefix += value
        if prefix > s * (17 - s) // 2:
            return True
    return False


def audit(cut_slack=0):
    """Classify every necessary relaxed profile by deficit or B capacity."""
    if type(cut_slack) is not int or cut_slack < 0:
        raise ValueError("cut_slack must be a nonnegative integer")
    stages = Counter()
    survivors = []
    alphas = alpha_histograms()
    ks = k_histograms()
    for a in alphas:
        m = sum((d + 2) * count for d, count in enumerate(a))
        t = a[0]
        for k in ks:
            incoming = sum(degree * count for degree, count in enumerate(k))
            if incoming < 74 - 2 * m - cut_slack:
                continue
            stages["cut"] += 1
            z = k[0]
            if t * (4 - z) >= 8:
                stages["weighted"] += 1
            elif capacity_violation(a, k):
                stages["capacity"] += 1
            else:
                stages["unresolved"] += 1
                survivors.append((a, k))
    return {
        "alpha_histograms": len(alphas),
        "k_histograms": len(ks),
        "cut_slack": cut_slack,
        "cut_profiles": stages["cut"],
        "weighted_excluded": stages["weighted"],
        "capacity_excluded": stages["capacity"],
        "unresolved": stages["unresolved"],
        "unresolved_histograms": survivors,
    }


def main():
    baseline = audit()
    weakened = audit(cut_slack=1)
    print(json.dumps({"exact_cut": baseline, "one_unit_weakened_cut": weakened},
                     indent=2, sort_keys=True))
    if (baseline["alpha_histograms"] != 19
            or baseline["k_histograms"] != 5005
            or (baseline["cut_profiles"], baseline["weighted_excluded"],
                baseline["capacity_excluded"], baseline["unresolved"])
            != (20500, 20287, 213, 0)
            or weakened["unresolved"] != 2):
        raise SystemExit("INVALID: weighted-deficit profile audit drift")


if __name__ == "__main__":
    main()
