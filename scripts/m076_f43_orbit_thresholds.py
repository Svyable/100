#!/usr/bin/env python3
"""Exact single-insertion deletion spectrum around the 54-set 4-uniform family.

An author-derived restricted certificate. Independent specialist review and
historical novelty are NOT established. Pure Python 3 standard library.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict, deque
from itertools import combinations

WORK_ID = "X-M076-F43-ORBIT-THRESHOLDS"
SCOPE_SHA256 = "09dc1a6fcd21524f108dcd72ad20e7582ce3f3c25a3847fef201fc469e4d59e9"


def base_family():
    """Two disjoint nine-point components, three blocks of size three each."""
    return tuple(frozenset(a + b)
                 for offset in (0, 9)
                 for p, q in combinations(range(3), 2)
                 for a in combinations(range(offset + 3*p, offset + 3*p + 3), 2)
                 for b in combinations(range(offset + 3*q, offset + 3*q + 3), 2))


def orbit_key(c):
    """Complete orbit invariant under the block/component/outside action."""
    blocks = tuple(sorted((tuple(sorted((sum(x in c for x in range(offset + 3*j,
                                                                    offset + 3*j + 3))
                                         for j in range(3)), reverse=True))
                           for offset in (0, 9)), reverse=True))
    return (len(c - frozenset(range(18))), blocks)


def representatives(family):
    reps, sizes = {}, Counter()
    for c in combinations(range(22), 4):
        c = frozenset(c)
        if c in family:
            continue
        k = orbit_key(c)
        reps.setdefault(k, c)
        sizes[k] += 1
    assert len(reps) == 18 and sum(sizes.values()) == 7261
    assert dict(Counter(k[0] for k in reps)) == {0: 8, 1: 5, 2: 3, 3: 1, 4: 1}
    return reps, sizes


def conflict_edges(family, c):
    """Literal old-old-new sunflower edges, including the empty core."""
    return tuple((i, j) for i in range(len(family)) for j in range(i)
                 if family[i] & family[j] == family[i] & c == family[j] & c)


def block_id(x):
    return x // 3


def structural_colors(family, c):
    """Explicit two-coloring by common trace T = F_i intersect C.

    T=empty: color by component. T singleton or same-block pair: color
    by the other occupied block. T in two blocks: color by the extra
    point in the lower block. T triple: at most two old sets have T.
    """
    by_trace = defaultdict(list)
    for i, a in enumerate(family):
        by_trace[a & c].append(i)
    colors = {}
    for t, ids in by_trace.items():
        if not t:
            for i in ids:
                colors[i] = i // 27
        elif len(t) == 1 or (len(t) == 2 and len({block_id(x) for x in t}) == 1):
            anchor = block_id(min(t))
            others = sorted(set(range((anchor // 3)*3, (anchor // 3)*3 + 3)) - {anchor})
            for i in ids:
                occupied = {block_id(x) for x in family[i]}
                other = next(iter(occupied - {anchor}))
                colors[i] = others.index(other)
        elif len(t) == 2:
            anchor = min(block_id(x) for x in t)
            p = next(x for x in t if block_id(x) == anchor)
            alternatives = sorted(set(range(anchor*3, anchor*3 + 3)) - {p})
            for i in ids:
                other = next(x for x in family[i] if block_id(x) == anchor and x != p)
                colors[i] = alternatives.index(other)
        else:
            assert len(ids) <= 2, (t, ids)
            for j, i in enumerate(ids):
                colors[i] = j
    assert len(colors) == len(family)
    return colors


def matching_and_cover(edges, colors, n):
    """Construct matching and same-size vertex cover (Koenig certificate)."""
    left = sorted(i for i in range(n) if colors[i] == 0)
    neighbors = {i: [] for i in left}
    for i, j in edges:
        assert colors[i] != colors[j], (i, j)
        u, v = (i, j) if colors[i] == 0 else (j, i)
        neighbors[u].append(v)
    for u in left:
        neighbors[u].sort()
    mate = {}  # right -> left

    def augment(u, seen):
        for v in neighbors[u]:
            if v in seen:
                continue
            seen.add(v)
            if v not in mate or augment(mate[v], seen):
                mate[v] = u
                return True
        return False

    for u in left:
        augment(u, set())
    matching = tuple(sorted((u, v) for v, u in mate.items()))
    matched_left = set(mate.values())
    reached_left = set(left) - matched_left
    reached_right = set()
    q = deque(sorted(reached_left))
    while q:
        u = q.popleft()
        for v in neighbors[u]:
            if (u, v) in matching or v in reached_right:
                continue
            reached_right.add(v)
            if v in mate and mate[v] not in reached_left:
                reached_left.add(mate[v])
                q.append(mate[v])
    cover = (set(left) - reached_left) | reached_right
    assert len(matching) == len(cover)
    assert len({x for pair in matching for x in pair}) == 2*len(matching)
    assert all(i in cover or j in cover for i, j in edges)
    return matching, tuple(sorted(cover))


def literal_sunflower(a, b, c):
    return a & b == a & c == b & c


def verify_witness(family, c, cover):
    """Directly verify deletion + insertion and each essential deletion."""
    kept = [a for i, a in enumerate(family) if i not in cover]
    assert c not in family and len(set(kept + [c])) == len(kept) + 1
    assert all(not literal_sunflower(a, b, c) for a, b in combinations(kept, 2))
    for i in cover:
        assert any(literal_sunflower(a, family[i], c) for a in kept)
    return len(kept) + 1


def independent_bitmask_sweep(family, expected):
    """Orbit-free 7,261-candidate replay with integer masks and BFS colors.

    This path does not use trace coloring or the representative graph.
    """
    masks = [sum(1 << x for x in a) for a in family]
    old = set(masks)
    checked = 0
    for c in combinations(range(22), 4):
        cm = sum(1 << x for x in c)
        if cm in old:
            continue
        edges = [(i, j) for i in range(54) for j in range(i)
                 if masks[i] & masks[j] == masks[i] & cm == masks[j] & cm]
        adj = [[] for _ in range(54)]
        for i, j in edges:
            adj[i].append(j)
            adj[j].append(i)
        color = {}
        for root in range(54):
            if root in color:
                continue
            color[root] = 0
            q = deque([root])
            while q:
                u = q.popleft()
                for v in adj[u]:
                    if v not in color:
                        color[v] = 1 - color[u]
                        q.append(v)
                    else:
                        assert color[v] != color[u], (c, u, v)
        matching, cover = matching_and_cover(edges, color, 54)
        key = orbit_key(frozenset(c))
        assert len(matching) == expected[key], (c, key, len(matching), expected[key])
        checked += 1
    assert checked == 7261
    return checked


def check(full_sweep=True):
    family = base_family()
    assert len(family) == len(set(family)) == 54
    assert all(not literal_sunflower(a, b, c) for a, b, c in combinations(family, 3))
    reps, sizes = representatives(set(family))
    table = []
    thresholds = {}
    for key, c in sorted(reps.items()):
        edges = conflict_edges(family, c)
        colors = structural_colors(family, c)
        matching, cover = matching_and_cover(edges, colors, len(family))
        assert verify_witness(family, c, cover) == 55 - len(cover)
        thresholds[key] = len(cover)
        table.append({"outsiders": key[0], "blocks": [list(v) for v in key[1]],
                      "representative": sorted(c), "orbit_size_on_22": sizes[key],
                      "edges": len(edges), "minimum_deletions": len(cover),
                      "matching": [list(pair) for pair in matching],
                      "cover": list(cover)})
    expected = (5, 6, 9, 11, 12, 13, 15, 15, 16, 18, 18, 19, 19, 21, 21, 24, 27, 27)
    assert tuple(sorted(thresholds.values())) == expected
    swept = independent_bitmask_sweep(family, thresholds) if full_sweep else 0
    digest = hashlib.sha256(("\n".join(
        str((r["outsiders"], r["blocks"], r["minimum_deletions"])) for r in table)
        + "\n").encode()).hexdigest()
    return {"work_id": WORK_ID, "scope_sha256": SCOPE_SHA256,
            "family_size": len(family), "orbit_types": len(reps),
            "candidates_on_22": sum(sizes.values()),
            "orbit_free_candidates_checked": swept,
            "bipartite_conflict_graphs": len(reps),
            "threshold_multiset": list(expected), "table_sha256": digest,
            "independent_mathematical_review": False, "table": table}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fast", action="store_true", help="Skip independent 7,261-candidate sweep")
    args = parser.parse_args()
    result = check(full_sweep=not args.fast)
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print("M076 exact single-insertion thresholds:", result["threshold_multiset"])
        print("18 bipartite conflict graphs; independent sweep:", result["orbit_free_candidates_checked"])
        print("certificate SHA-256:", result["table_sha256"])


if __name__ == "__main__":
    main()
