#!/usr/bin/env python3
"""Exact digraph isomorphism-orbit enumerator for n<=5.

Enumerates all 2^(n(n-1)) loopless labeled digraphs via vertex-relabelling
orbits. Independent Burnside counting certifies the number of orbits.
Two independent cycle-detection methods check every relevant representative.
This reproduces known small cases, NOT the full Caccetta-Haggkvist conjecture.
"""
import argparse
import hashlib
from itertools import permutations
import json

from digraph import directed_girth

KNOWN_ALL = {2: 3, 3: 16, 4: 218, 5: 9608}  # OEIS A000273
KNOWN_ORIENTED = {2: 2, 3: 7, 4: 42, 5: 582}  # OEIS A001174


def arc_index(n):
    arcs = tuple((u, v) for u in range(n) for v in range(n) if u != v)
    return arcs, {edge: i for i, edge in enumerate(arcs)}


def permutations_of_arcs(n, arcs, lookup):
    return tuple(tuple(1 << lookup[perm[u], perm[v]] for u, v in arcs)
                 for perm in permutations(range(n)))


def image_of(mask, mapping):
    result = 0
    while mask:
        bit = mask & -mask
        result |= mapping[bit.bit_length() - 1]
        mask ^= bit
    return result


def burnside_orbits(maps):
    total = 0
    for mapping in maps:
        seen = 0
        cycles = 0
        for i in range(len(mapping)):
            bit = 1 << i
            if seen & bit:
                continue
            cycles += 1
            j = i
            while not seen & (1 << j):
                seen |= 1 << j
                j = mapping[j].bit_length() - 1
        total += 1 << cycles
    if total % len(maps):
        raise AssertionError("Burnside sum not divisible by group size")
    return total // len(maps)


def adjacency(mask, arcs, n):
    result = [0] * n
    while mask:
        bit = mask & -mask
        u, v = arcs[bit.bit_length() - 1]
        result[u] |= 1 << v
        mask ^= bit
    return result


def has_short_cycle(adj, max_length):
    """Independent DFS over vertex-distinct directed cycles."""
    for root in range(len(adj)):
        def walk(u, seen, length):
            if length >= max_length:
                return False
            row = adj[u]
            while row:
                bit = row & -row
                row ^= bit
                v = bit.bit_length() - 1
                if v == root and length + 1 >= 2:
                    return True
                if not (seen & bit) and walk(v, seen | bit, length + 1):
                    return True
            return False
        if walk(root, 1 << root, 0):
            return True
    return False


def oriented(adj):
    return not any(adj[u] & (1 << v) and adj[v] & (1 << u)
                   for u in range(len(adj)) for v in range(u + 1, len(adj)))


def enumerate_orbits(n):
    if type(n) is not int or not 2 <= n <= 5:
        raise ValueError("Exact orbit enumeration supported for 2<=n<=5")
    arcs, lookup = arc_index(n)
    maps = permutations_of_arcs(n, arcs, lookup)
    expected_orbits = burnside_orbits(maps)
    visited = bytearray(1 << len(arcs))
    classes = oriented_classes = count_labeled = 0
    eligible_labeled = eligible_classes = 0
    eligible_by_r = {
        str(r): {"labeled": 0, "unlabeled": 0} for r in range(1, n)
    }
    sha = hashlib.sha256()
    width = (len(arcs) + 7) // 8
    for representative in range(len(visited)):
        if visited[representative]:
            continue
        orbit = {image_of(representative, mapping) for mapping in maps}
        if any(visited[image] for image in orbit):
            raise AssertionError("Distinct orbits intersect")
        for image in orbit:
            visited[image] = 1
        classes += 1
        count_labeled += len(orbit)
        sha.update(representative.to_bytes(width, "little"))
        adj = adjacency(representative, arcs, n)
        if oriented(adj):
            oriented_classes += 1
        minimum = min(row.bit_count() for row in adj)
        if minimum < 1:
            continue
        eligible_classes += 1
        eligible_labeled += len(orbit)
        girth = directed_girth(adj)
        for k in range(2, n + 1):
            if has_short_cycle(adj, k) != (girth is not None and girth <= k):
                raise AssertionError(
                    f"Independent cycle algorithms disagree: n={n} mask={representative} k={k}"
                )
        for r in range(1, minimum + 1):
            bound = (n + r - 1) // r
            if girth is None or girth > bound:
                raise AssertionError(
                    f"Possible counterexample n={n} r={r} mask={representative}"
                )
            eligible_by_r[str(r)]["labeled"] += len(orbit)
            eligible_by_r[str(r)]["unlabeled"] += 1
    assert all(visited) and count_labeled == len(visited)
    assert classes == expected_orbits == KNOWN_ALL[n]
    assert oriented_classes == KNOWN_ORIENTED[n]
    return {
        "n": n, "labeled_graphs": len(visited),
        "unlabeled_orbits": classes, "burnside_orbits": expected_orbits,
        "oriented_unlabeled": oriented_classes,
        "eligible_min_degree_classes": eligible_classes,
        "eligible_min_degree_labeled": eligible_labeled,
        "by_minimum_r": eligible_by_r,
        "representative_sha256": sha.hexdigest(),
        "status": "PASS: known finite cases only; unrestricted conjecture remains open"
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=5)
    args = parser.parse_args()
    try:
        print(json.dumps(enumerate_orbits(args.n), indent=2, sort_keys=True))
    except (ValueError, AssertionError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
