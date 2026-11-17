"""M078 #381: exact positive-length obstruction to a single alternating four-cycle trade.

Six leaves, four degree-three hubs. The star's three peripheral hubs have
leaf pairs 01, 23, 45. The path's endpoints have two leaves each and its
two internal hubs one leaf each. Every hub edge has positive length.

Only one two-value alternating 4-cycle trade is excluded, NOT arbitrary
unlabeled row-profile collisions. Pure integer arithmetic; no LP dependency.
"""
from itertools import combinations, permutations
from math import gcd

PAIRS = tuple(combinations(range(6), 2))
INDEX = {p: i for i, p in enumerate(PAIRS)}


def forms(edges):
    assert len(edges) == 9
    adj = [[] for _ in range(10)]
    for k, (u, v) in enumerate(edges):
        adj[u].append((v, k))
        adj[v].append((u, k))
    out = []
    for a, b in PAIRS:
        stack = [(a, -1, ())]
        while stack:
            u, prev, path = stack.pop()
            if u == b:
                out.append(tuple(int(k in path) for k in range(9)))
                break
            stack.extend((v, u, path + (k,)) for v, k in adj[u] if v != prev)
        else:
            raise ValueError("disconnected")
    return tuple(out)


STAR = forms(((0, 7), (1, 7), (2, 8), (3, 8), (4, 9), (5, 9),
              (6, 7), (6, 8), (6, 9)))


def path_forms():
    seen = set()
    for a, b, c, d, e, f in permutations(range(6)):
        left, right = tuple(sorted((a, b))), tuple(sorted((e, f)))
        key = min((left, c, d, right), (right, d, c, left))
        if key in seen:
            continue
        seen.add(key)
        yield key, forms(((a, 6), (b, 6), (c, 7), (d, 8),
                          (e, 9), (f, 9), (6, 7), (7, 8), (8, 9)))


def four_cycles():
    out = set()
    for vertices in combinations(range(6), 4):
        for order in permutations(vertices):
            out.add(tuple(sorted(INDEX[tuple(sorted((order[i], order[(i+1) % 4])))]
                                 for i in range(4))))
    return tuple(sorted(out))


def constraints(star, path, cycle):
    opposite = [(i, j) for i, j in combinations(cycle, 2)
                if set(PAIRS[i]).isdisjoint(PAIRS[j])]
    assert len(opposite) == 2
    (a, c), (b, d) = opposite
    z = (0,) * 9
    rows = [star[i] + tuple(-v for v in path[i])
            for i in range(15) if i not in cycle]
    rows += [tuple(star[a][k] - star[c][k] for k in range(9)) + z,
             tuple(star[b][k] - star[d][k] for k in range(9)) + z,
             z + tuple(path[a][k] - path[c][k] for k in range(9)),
             z + tuple(path[b][k] - path[d][k] for k in range(9))]
    rows += [star[i] + tuple(-v for v in path[j])
             for i, j in ((a, b), (b, a), (c, d), (d, c))]
    return rows


def forced_zero_coordinates(equations, width=18):
    """Integer row-equivalent elimination, returning variables forced to zero.

    For a homogeneous system, a pivot variable vanishes for every rational
    solution iff its reduced row has no nonzero free-variable coefficient.
    GCD division is exact and preserves the rational nullspace.
    """
    rows = [list(map(int, row)) for row in equations if any(row)]
    pivots = []
    r = 0
    for c in range(width):
        pivot = next((k for k in range(r, len(rows)) if rows[k][c]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        p = rows[r][c]
        for k in range(len(rows)):
            if k == r or not rows[k][c]:
                continue
            q = rows[k][c]
            rows[k] = [p*x-q*y for x, y in zip(rows[k], rows[r])]
            common = 0
            for v in rows[k]:
                common = gcd(common, v)
            if common > 1:
                rows[k] = [v//common for v in rows[k]]
        common = 0
        for v in rows[r]:
            common = gcd(common, v)
        if common > 1:
            rows[r] = [v//common for v in rows[r]]
        pivots.append(c)
        r += 1
        if r == len(rows):
            break
    free = set(range(width)) - set(pivots)
    return tuple(c for row, c in zip(rows, pivots)
                 if all(row[f] == 0 for f in free))


def verify_all():
    paths, cycles = list(path_forms()), four_cycles()
    assert len(paths) == 90 and len(cycles) == 45
    count = 0
    for _, path in paths:
        for cycle in cycles:
            zero = forced_zero_coordinates(constraints(STAR, path, cycle))
            if not zero:
                raise AssertionError(("unexcluded case", count))
            count += 1
    return {"path_allocations": len(paths), "four_cycles": len(cycles),
            "systems": count, "forced_zero_in_every_system": True}


if __name__ == "__main__":
    import json
    print(json.dumps(verify_all(), sort_keys=True))
