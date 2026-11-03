#!/usr/bin/env python3
"""M078: connected unicyclic S4 collisions for every order n >= 9.

No graph-isomorphism oracle or external package is used. The structural proof
is in research/M078_S4_NINE_UNICYCLIC.md. This code is a regression checker,
not an independent mathematical referee.
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
import json


A9 = ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0),
      (0, 6), (5, 7), (7, 8))
B9 = ((0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
      (0, 5), (5, 6), (5, 7), (7, 8))

BASE_PROFILES = Counter({
    (1, (2,)): 1, (1, (3,)): 1,
    (2, (1, 3)): 1, (2, (2, 2)): 2, (2, (2, 3)): 2,
    (3, (1, 2, 3)): 1, (3, (2, 2, 3)): 1,
})


def family(extra: int, cycle_subdivisions: int = 0
           ) -> tuple[tuple[int, tuple[tuple[int, int], ...]], ...]:
    """Subdivide cycle edge 1-2 equally, then grow a common tail from leaf 8."""
    if type(extra) is not int or extra < 0 or type(cycle_subdivisions) is not int or cycle_subdivisions < 0:
        raise ValueError("extra and cycle_subdivisions must be nonnegative integers")
    s = cycle_subdivisions
    cycle_path = ((1, 2),) if s == 0 else tuple(
        zip((1,) + tuple(range(9, 9 + s)),
            tuple(range(9, 9 + s)) + (2,)))
    tail_path = tuple(zip((8,) + tuple(range(9 + s, 9 + s + extra - 1)),
                          range(9 + s, 9 + s + extra)))
    n = 9 + s + extra
    return tuple((n, tuple(e for e in base if set(e) != {1, 2})
                  + cycle_path + tail_path) for base in (A9, B9))


def adjacency(n: int, edges: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    if n < 1:
        raise ValueError("empty graph")
    out = [0] * n
    for a, b in edges:
        if not (0 <= a < n and 0 <= b < n) or a == b or out[a] & (1 << b):
            raise ValueError("invalid, repeated or loop edge")
        out[a] |= 1 << b
        out[b] |= 1 << a
    return tuple(out)


def degree_neighborhood_profiles(n: int, edges: tuple[tuple[int, int], ...]) -> Counter:
    a = adjacency(n, edges)
    deg = [row.bit_count() for row in a]
    return Counter((deg[v], tuple(sorted(deg[u] for u in range(n) if a[v] >> u & 1)))
                   for v in range(n))


def cycle_core_length(n: int, edges: tuple[tuple[int, int], ...]) -> int:
    """For a connected unicyclic graph, its unique cycle length."""
    a = adjacency(n, edges)
    if len(edges) != n:
        raise ValueError("not unicyclic by edge count")
    visited = {0}
    stack = [0]
    while stack:
        v = stack.pop()
        for u in range(n):
            if a[v] >> u & 1 and u not in visited:
                visited.add(u)
                stack.append(u)
    if len(visited) != n:
        raise ValueError("not connected")
    active = set(range(n))
    while True:
        leaves = [v for v in active if (a[v] & sum(1 << u for u in active)).bit_count() <= 1]
        if not leaves:
            break
        active.difference_update(leaves)
    if not active or any((a[v] & sum(1 << u for u in active)).bit_count() != 2 for v in active):
        raise ValueError("not a single cycle")
    return len(active)


def card_signature_direct(n: int, edges: tuple[tuple[int, int], ...]) -> tuple:
    """Literal deletion, triangle triples and three cycles per four-set."""
    a = adjacency(n, edges)
    cards = []
    for deleted in range(n):
        vs = [v for v in range(n) if v != deleted]
        mask = ((1 << n) - 1) ^ (1 << deleted)
        degrees = tuple(sorted((a[v] & mask).bit_count() for v in vs))
        triangles = sum(bool(a[x] >> y & 1 and a[x] >> z & 1 and a[y] >> z & 1)
                        for x, y, z in combinations(vs, 3))
        four_cycles = 0
        for x, y, z, w in combinations(vs, 4):
            for p, q, r, s in ((x, y, z, w), (x, y, w, z), (x, z, y, w)):
                four_cycles += int(all(a[u] >> v & 1
                                       for u, v in ((p, q), (q, r), (r, s), (s, p))))
        cards.append((degrees, triangles, four_cycles))
    return tuple(sorted(cards))


def card_signature_bitset(n: int, edges: tuple[tuple[int, int], ...]) -> tuple:
    """Independent motif arithmetic: edge/common-neighbor and opposite-pair sums."""
    a = adjacency(n, edges)
    cards = []
    for deleted in range(n):
        mask = ((1 << n) - 1) ^ (1 << deleted)
        vs = [v for v in range(n) if v != deleted]
        degrees = tuple(sorted((a[v] & mask).bit_count() for v in vs))
        three_times_tri = 0
        twice_four = 0
        for x, y in combinations(vs, 2):
            common = (a[x] & a[y] & mask).bit_count()
            if a[x] >> y & 1:
                three_times_tri += common
            twice_four += common * (common - 1) // 2
        assert three_times_tri % 3 == 0 and twice_four % 2 == 0
        cards.append((degrees, three_times_tri // 3, twice_four // 2))
    return tuple(sorted(cards))


def check() -> dict:
    assert degree_neighborhood_profiles(9, A9) == BASE_PROFILES
    assert degree_neighborhood_profiles(9, B9) == BASE_PROFILES
    # The all-orders proof uses equality of local degree profiles and fixed
    # distinct cycle lengths; these larger tests are not an exhaustive proof.
    for t in (0, 1, 2, 3, 5, 8, 12, 20, 50):
        (n, a), (_, b) = family(t)
        assert degree_neighborhood_profiles(n, a) == degree_neighborhood_profiles(n, b)
        assert cycle_core_length(n, a) == 6
        assert cycle_core_length(n, b) == 5
        if t <= 12:
            left = card_signature_direct(n, a)
            right = card_signature_direct(n, b)
            assert left == right
            assert left == card_signature_bitset(n, a)
            assert right == card_signature_bitset(n, b)
            assert all(tri == four == 0 for _, tri, four in left)
    # Every fixed cycle-motif cutoff k>=4 has a connected counterexample
    # at n=k+5, with unique cycles of lengths k+2 and k+1.
    for k in range(4, 15):
        (n, a), (_, b) = family(0, cycle_subdivisions=k - 4)
        assert n == k + 5
        assert cycle_core_length(n, a) == k + 2
        assert cycle_core_length(n, b) == k + 1
        assert degree_neighborhood_profiles(n, a) == degree_neighborhood_profiles(n, b)
        if k <= 9:
            assert card_signature_direct(n, a) == card_signature_direct(n, b)
    n, a = family(0)[0]
    assert card_signature_direct(n, a) != card_signature_direct(n, a[:-1])
    return {"work_id": "X-M078-S4-NINE", "first_order": 9,
            "checked_orders": [9, 10, 11, 12, 14, 17, 21, 29, 59],
            "direct_card_orders": [9, 10, 11, 12, 14, 17, 21],
            "cycle_lengths": [6, 5], "status": "author_checked_not_independently_reviewed"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("use --check")
    result = check()
    print(json.dumps(result, indent=2) if args.json else "M078 S4 nine: checks passed")


if __name__ == "__main__":
    main()
