#!/usr/bin/env python3
"""M075: exact six-point triple-local witness and exhaustive five-point boundary.

This is NOT a counterexample to Frankl's original existential conjecture.
A five-point enumeration is a *finite* argument, not a global 19-set bound.
No SAT/MILP solver is needed for the reproducible certificates.

    python3 scripts/frankl_triple_support.py --check
    python3 scripts/frankl_triple_support.py --json
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = ROOT / "examples" / "FRANKL_VAN_DER_HOUT_ROOS_19.json"
SIX = ROOT / "examples" / "FRANKL_TRIPLE_SIX_19.json"
TRIPLE = (0, 1, 2)
PAIRS = ((3, 4), (3, 5), (4, 5))


def mask(els):
    if any(type(i) is not int or i < 0 for i in els) or len(set(els)) != len(els):
        raise ValueError("Invalid set")
    return sum(1 << i for i in els)


def six_family():
    """A compressed version of the published seven-point 19-set example."""
    triple = set(TRIPLE)
    outside = {3, 4, 5}
    members = [set(), triple]
    for i, pair in enumerate(PAIRS):
        p = set(pair)
        members.extend((p, p | {i}, p | triple))
    members.extend(outside | {i for i in TRIPLE if bits & (1 << i)}
                   for bits in range(8))
    return sorted(mask(s) for s in members)


def lifted_family(k):
    """Replace triple element 2 with a nonempty block; union commutes with lift."""
    if type(k) is not int or k < 3:
        raise ValueError("Target size k must be >=3")
    blocks = ({0}, {1}, set(range(2, k)), {k}, {k + 1}, {k + 2})
    return sorted(mask(set().union(*(blocks[j] for j in range(6) if s & (1 << j))))
                  for s in six_family())


def check_family(family, n, target):
    """Definition-level checker independent of the construction and enumeration."""
    if len(family) != len(set(family)) or not family or any(
        type(x) is not int or x < 0 or x >= 1 << n for x in family
    ):
        raise ValueError("Invalid or duplicated subsets")
    chosen = set(family)
    tmask = sum(1 << i for i in target)
    if 0 not in chosen or tmask not in chosen:
        raise ValueError("Empty set or exact target missing")
    if any((x | y) not in chosen for x in chosen for y in chosen):
        raise ValueError("Not union-closed")
    frequencies = tuple(sum(bool(s & (1 << i)) for s in chosen) for i in range(n))
    if any(2 * frequencies[i] >= len(chosen) for i in target):
        raise ValueError("Target not strictly rare")
    if any(s not in (0, tmask) and s & tmask == s for s in chosen):
        raise ValueError("Target not inclusion-minimal among nonempty members")
    return {"members": len(chosen), "universe": n, "target": list(target),
            "frequencies": list(frequencies), "inclusion_minimal_target": True}


def direct_count(n):
    """Independent brute force for n<=4 (all 2^(2^n) membership vectors)."""
    if not 3 <= n <= 4:
        raise ValueError("Direct negative control limited to n<=4")
    total = 0
    rare = 0
    for bits in range(1 << (1 << n)):
        if not(bits & 1) or not(bits & (1 << 7)):
            continue
        chosen = [s for s in range(1 << n) if bits & (1 << s)]
        membership = set(chosen)
        if any((a | b) not in membership for a in chosen for b in chosen):
            continue
        total += 1
        if all(2 * sum(bool(s & (1 << t)) for s in chosen) < len(chosen)
               for t in TRIPLE):
            rare += 1
    return total, rare


def closure_descending_count(n):
    """Enumerate ALL union-closed families with empty and exact {0,1,2}.

    Proof of completeness: visit potential members in decreasing cardinality.
    On including S, every union S|A with an already chosen A is either
    S, A or a STRICT SUPERSET of S. In the last case it has already been
    decided, and must have been included. Every valid union-closed family
    has exactly one compatible include/exclude path. Excluding S never
    invalidates closure of the currently selected members.

    No full-support assumption; the run n=5 also covers smaller supports.
    """
    if type(n) is not int or not 3 <= n <= 5:
        raise ValueError("Supported exact enumeration range n=3..5")
    N = 1 << n
    order = sorted(range(N), key=lambda s: (-s.bit_count(), -s))
    unions = [[a | b for b in range(N)] for a in range(N)]
    total = 0
    rare = 0
    nodes = 0

    def visit(pos, selection, size, f0, f1, f2):
        nonlocal total, rare, nodes
        nodes += 1
        if pos == N:
            total += 1
            if 2 * f0 < size and 2 * f1 < size and 2 * f2 < size:
                rare += 1
            return
        s = order[pos]
        if s not in (0, 7):
            visit(pos + 1, selection, size, f0, f1, f2)
        remaining = selection
        while remaining:
            low = remaining & -remaining
            t = low.bit_length() - 1
            remaining ^= low
            u = unions[s][t]
            if u != s and u != t and not (selection & (1 << u)):
                break
        else:
            visit(pos + 1, selection | (1 << s), size + 1,
                  f0 + bool(s & 1), f1 + bool(s & 2), f2 + bool(s & 4))

    visit(0, 0, 0, 0, 0, 0)
    return {"n": n, "families_with_empty_and_triple": total,
            "triple_rare": rare, "search_nodes": nodes}


def published_projection():
    """Drop redundant point 6; exact image must be collision-free."""
    data = json.loads(PUBLISHED.read_text(encoding="utf-8"))
    if data["n"] != 7 or data["triple"] != list(TRIPLE):
        raise ValueError("Published fixture scope changed")
    original = [mask(s) for s in data["sets"]]
    image = [s & ((1 << 6) - 1) for s in original]
    if len(original) != len(set(original)) or len(image) != len(set(image)):
        raise ValueError("Coordinate deletion was not injective")
    if sorted(image) != six_family():
        raise ValueError("Six-point family is not the published image")
    return image


def verify():
    six = check_family(six_family(), 6, TRIPLE)
    if six["members"] != 19 or six["frequencies"] != [9, 9, 9, 14, 14, 14]:
        raise ValueError("Six-point witness drift")
    if sorted(mask(s) for s in json.loads(SIX.read_text(encoding="utf-8"))["sets"]) != six_family():
        raise ValueError("Committed six-point witness drift")
    published_projection()
    checks = []
    for n, target in ((3, 45), (4, 1575), (5, 710830)):
        result = closure_descending_count(n)
        if result["families_with_empty_and_triple"] != target or result["triple_rare"] != 0:
            raise ValueError(f"Five-point boundary drift at n={n}")
        if n <= 4 and direct_count(n) != (result["families_with_empty_and_triple"], 0):
            raise ValueError(f"Independent brute-force count disagrees at n={n}")
        checks.append(result)
    lifts = []
    for k in (3, 4, 5, 8):
        witness = check_family(lifted_family(k), k + 3, range(k))
        if witness["members"] != 19 or witness["frequencies"] != [9] * k + [14] * 3:
            raise ValueError("Lifted witness drift")
        lifts.append({"k": k, "members": witness["members"], "ground_points": k + 3})
    return {"scope": "triple-local only, not Frankl's conjecture",
            "six_point_witness": six,
            "published_projection_injective": True,
            "exhaustive_counts": checks,
            "lifting_checks": lifts,
            "independent_specialist_review": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("OK: six-point 19-set exact triple-local witness, target frequencies 9/19")
        print("OK: published seven-point example projects injectively to the six-point witness")
        print("OK: n<=5 exhaustively excludes triple-local failures; "
              "n=5 checked {} families".format(result["exhaustive_counts"][-1]["families_with_empty_and_triple"]))
        print("OK: 19-member cloned-target construction at k=3,4,5,8")
        print("No global minimum-size, novelty or independently reviewed theorem claimed")


if __name__ == "__main__":
    main()
