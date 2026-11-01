#!/usr/bin/env python3
"""Count full-support union-closed families modulo S_n by Burnside's lemma.

Instead of canonicalizing millions of labeled n=5 families one at a time,
enumerate families invariant under one representative per permutation cycle
type. Each invariant family includes or excludes an entire orbit of subsets;
closure-invalid branches are pruned. The identity case reuses the independent
full-support labeled enumerator.

This reproduces published n<=5 results, NOT Frankl's universal conjecture.
See research/M075_BURNSIDE.md for the precise proof obligations.
"""
import argparse
from collections import defaultdict
from itertools import permutations
import json
from math import factorial
from pathlib import Path

from frankl_canonical import full_support_families, relabel_family, subset_actions

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/frankl_burnside_n5.json"
EXPECTED_ORBITS = {4: 330, 5: 28960}


def checked_permutation(perm):
    if not isinstance(perm, tuple) or not 1 <= len(perm) <= 5:
        raise ValueError("Expected permutation tuple on 1..5 elements")
    if any(type(x) is not int for x in perm) or sorted(perm) != list(range(len(perm))):
        raise ValueError("Not a ground-set permutation")
    return len(perm)


def cycle_type(perm):
    n = checked_permutation(perm)
    used = set()
    lengths = []
    for start in range(n):
        if start in used:
            continue
        at, length = start, 0
        while at not in used:
            used.add(at)
            at = perm[at]
            length += 1
        lengths.append(length)
    return tuple(sorted(lengths, reverse=True))


def subset_orbits(perm):
    """Exact partition of P([n]) under the cyclic action of a permutation."""
    n = checked_permutation(perm)
    action = tuple(
        sum(1 << perm[i] for i in range(n) if subset >> i & 1)
        for subset in range(1 << n)
    )
    visited = set()
    orbits = []
    for subset in range(1 << n):
        if subset in visited:
            continue
        orbit, at = [], subset
        while at not in visited:
            visited.add(at)
            orbit.append(at)
            at = action[at]
        orbits.append(tuple(sorted(orbit)))
    return sorted(orbits, key=lambda orbit: (-orbit[0].bit_count(), -max(orbit)))


def can_add_orbit(family, orbit):
    """All unions involving a newly added orbit must lie in the new family."""
    addition = sum(1 << s for s in orbit)
    present = family | addition
    members = []
    remaining = present
    while remaining:
        bit = remaining & -remaining
        members.append(bit.bit_length() - 1)
        remaining ^= bit
    for a in orbit:
        for b in members:
            if not (present >> (a | b)) & 1:
                return False
    return True


def fixed_family_count(perm):
    """Count union-closed full-support families fixed by this permutation."""
    n = checked_permutation(perm)
    if perm == tuple(range(n)):
        return sum(1 for _ in full_support_families(n))
    top = (1 << n) - 1
    orbits = subset_orbits(perm)
    if not orbits or orbits[0] != (top,):
        raise ValueError("full-set singleton orbit missing")
    blocks = orbits[1:]
    additions = [sum(1 << s for s in block) for block in blocks]

    def enumerate_fixed(index, family):
        if index == len(blocks):
            return 1
        count = enumerate_fixed(index + 1, family)  # exclude entire block
        orbit = blocks[index]
        if can_add_orbit(family, orbit):
            count += enumerate_fixed(index + 1, family | additions[index])
        return count

    return enumerate_fixed(0, 1 << top)


def burnside(n):
    if type(n) is not int or n not in (4, 5):
        raise ValueError("Burnside audit covers ground sizes 4 and 5")
    classes = defaultdict(list)
    for perm in permutations(range(n)):
        classes[cycle_type(perm)].append(perm)
    records = []
    numerator = 0
    for signature in sorted(classes, reverse=True):
        class_members = classes[signature]
        fixed = fixed_family_count(class_members[0])
        weight = len(class_members)
        numerator += weight * fixed
        records.append({
            "cycle_type": list(signature),
            "permutations": weight,
            "fixed_full_support_families": fixed,
        })
    if sum(r["permutations"] for r in records) != factorial(n):
        raise ValueError("incomplete S_n partition")
    if numerator % factorial(n):
        raise ValueError("Burnside orbit count is not integral")
    orbit_count = numerator // factorial(n)
    if orbit_count != EXPECTED_ORBITS[n]:
        raise ValueError("orbit count disagrees with independently published sequence")
    return {
        "n": n, "classes": records, "fixed_points_weighted_sum": numerator,
        "group_order": factorial(n), "orbit_count": orbit_count,
    }


def report():
    return {
        "n4": burnside(4),
        "n5": burnside(5),
        "sources": {
            "labeled_full_support": "https://oeis.org/A326906",
            "unlabeled_full_support": "https://oeis.org/A326907",
        },
        "scope": (
            "Known exact finite counts only: group-action orbit counting of "
            "full-support union-closed families through n=5. Not Frankl's conjecture."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="reproduce the pinned exact n4/n5 Burnside report")
    args = parser.parse_args(argv)
    try:
        calculated = report()
        if args.check:
            frozen = json.loads(REPORT.read_text(encoding="utf-8"))
            if calculated != frozen:
                raise ValueError("Burnside certificate drift")
        print(json.dumps(calculated, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
