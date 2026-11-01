#!/usr/bin/env python3
"""Necessary integer-profile certificate for CH (24,8), indegree-nine root.

Searches small *relaxed* degree profiles, not 24-vertex digraphs.
A surviving row need not be realizable. See proofs/M074_IRREGULAR_24.md.
"""
from collections import Counter
from itertools import combinations_with_replacement
import json

N_A, N_B, N_C = 8, 9, 6


def alpha_profiles():
    return tuple(a for a in combinations_with_replacement(range(2, 8), N_A)
                 if sum(a) <= 21)


def incoming_profiles():
    return tuple(combinations_with_replacement(range(N_C + 1), N_B))


def requirements(alpha, incoming):
    if (len(alpha) != N_A or any(type(x) is not int or not 2 <= x <= 7 for x in alpha)
            or tuple(sorted(alpha)) != tuple(alpha) or sum(alpha) > 21):
        raise ValueError("invalid A profile")
    if (len(incoming) != N_B
            or any(type(x) is not int or not 0 <= x <= N_C for x in incoming)
            or tuple(sorted(incoming)) != tuple(incoming)):
        raise ValueError("invalid C->B profile")
    m = sum(alpha)
    eligible = tuple(sum(a >= k + 2 for a in alpha) for k in incoming)
    floors = tuple(sorted((max(0, 1 + k - q)
                           for k, q in zip(incoming, eligible)), reverse=True))
    return {
        "m": m,
        "cut_ok": sum(incoming) >= 74 - 2*m,
        "eligible_ok": sum(eligible) >= 37 - m,
        "subset_ok": all(sum(floors[:s]) <= s*(17-s)//2 for s in range(1, 10)),
        "internal_B_outdegree_floors": floors,
    }


def certificate():
    alphas = alpha_profiles()
    incoming = incoming_profiles()
    stages = Counter()
    surviving = Counter()
    witness = {}
    for a in alphas:
        for k in incoming:
            v = requirements(a, k)
            if not v["cut_ok"]:
                continue
            stages["cut"] += 1
            if not v["eligible_ok"]:
                continue
            stages["eligible"] += 1
            if not v["subset_ok"]:
                continue
            stages["subset"] += 1
            surviving[a] += 1
            witness.setdefault(a, k)
    return {
        "alpha_profile_count": len(alphas),
        "incoming_profile_count": len(incoming),
        "pairs_meeting_C_to_B_cut": stages["cut"],
        "pairs_meeting_cross_edge_eligibility": stages["eligible"],
        "pairs_meeting_all_B_subset_caps": stages["subset"],
        "surviving_alpha_profiles": [
            {"internal_outdegrees_A": list(a),
             "possible_C_to_B_profiles": surviving[a],
             "sample_C_to_B_profile": list(witness[a])}
            for a in sorted(surviving)
        ],
        "interpretation": ("These are necessary integer profiles, not valid "
                           "24-vertex graph certificates. See the proof and scope audit."),
    }


def main():
    result = certificate()
    print(json.dumps(result, sort_keys=True, indent=2))
    if (result["alpha_profile_count"] != 19
            or result["incoming_profile_count"] != 5005
            or result["pairs_meeting_C_to_B_cut"] != 20500
            or result["pairs_meeting_cross_edge_eligibility"] != 1116
            or result["pairs_meeting_all_B_subset_caps"] != 83
            or [(tuple(x["internal_outdegrees_A"]), x["possible_C_to_B_profiles"])
                for x in result["surviving_alpha_profiles"]] != [
                    ((2, 2, 2, 2, 2, 2, 2, 7), 77),
                    ((2, 2, 2, 2, 2, 2, 3, 6), 6),
                ]):
        raise SystemExit("INVALID: CH24 necessary-profile certificate drift")


if __name__ == "__main__":
    main()
