#!/usr/bin/env python3
"""Exact all-length subdivision formula; author checks, not external review.

Only standard-library dependencies. Parallel core edges have distinct indices.
Every core edge must have integer length >= 2; expanded graphs are simple.
"""
import argparse
from collections import deque
from fractions import Fraction as Q
from itertools import combinations, product
import json


def edge(u, v):
    return min(u, v), max(u, v)


def components(vertices, edges):
    adj = {v: set() for v in vertices}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    unseen, result = set(vertices), []
    while unseen:
        seen, todo = set(), [min(unseen)]
        while todo:
            v = todo.pop()
            if v not in seen:
                seen.add(v)
                todo.extend(adj[v] - seen)
        result.append(seen)
        unseen -= seen
    return result


def validate(n, edges, lengths):
    if type(n) is not int or n < 2 or len(edges) != len(lengths):
        raise ValueError("n>=2 and one length per core edge required")
    if any(len(e) != 2 or any(type(v) is not int or not 0 <= v < n for v in e)
           or e[0] == e[1] for e in edges):
        raise ValueError("invalid loopless core")
    if any(type(k) is not int or k < 2 for k in lengths):
        raise ValueError("integer path lengths >=2 required")
    if len(components(range(n), edges)) != 1:
        raise ValueError("core must be connected")


def expand(n, edges, lengths):
    validate(n, edges, lengths)
    paths, out, nxt = [], set(), n
    for (u, v), length in zip(edges, lengths):
        path = [u] + list(range(nxt, nxt + length - 1)) + [v]
        nxt += length - 1
        paths.append(path)
        out.update(edge(a, b) for a, b in zip(path, path[1:]))
    return nxt, out, paths


def even_masks(n, edges):
    """Fundamental-cycle basis: exactly 2^(m-n+1) even edge subsets."""
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    parent = {0: (None, None)}
    paths = {0: 0}
    queue = deque([0])
    tree = set()
    while queue:
        v = queue.popleft()
        for w, i in adj[v]:
            if w not in parent:
                parent[w] = (v, i)
                paths[w] = paths[v] ^ (1 << i)
                tree.add(i)
                queue.append(w)
    if len(parent) != n:
        raise ValueError("disconnected core")
    basis = [paths[u] ^ paths[v] ^ (1 << i)
             for i, (u, v) in enumerate(edges) if i not in tree]
    mask, previous = 0, 0
    yield mask
    for value in range(1, 1 << len(basis)):
        gray = value ^ (value >> 1)
        changed = gray ^ previous
        mask ^= basis[changed.bit_length() - 1]
        previous = gray
        yield mask


def states(n, edges):
    for mask in even_masks(n, edges):
        count = len(components(range(n), [e for i, e in enumerate(edges)
                                          if mask >> i & 1]))
        yield mask, len(edges) - mask.bit_count(), count


def optimum(n, edges, lengths):
    validate(n, edges, lengths)
    total = sum(lengths)
    return min((total + sum(lengths[i] - 2 for i in range(len(edges))
                            if not mask >> i & 1) + 2 * (count - 1), mask)
               for mask, _, count in states(n, edges))


def uniform_profile(n, edges):
    validate(n, edges, [2] * len(edges))
    by_d = {}
    for _, d, c in states(n, edges):
        by_d[d] = min(by_d.get(d, n), c)
    q = min(by_d)
    c0 = by_d[q]
    threshold = max([Q(2)] + [Q(2) + Q(2 * (c0 - c), d - q)
                             for d, c in by_d.items() if d > q])
    integer_threshold = -(-threshold.numerator // threshold.denominator)
    return {"edges": len(edges), "minimum_join_size": q,
            "minimum_join_complement_components": c0,
            "stabilization_length": integer_threshold,
            "eventual_slope": len(edges) + q,
            "eventual_intercept": -2 * (q - c0 + 1),
            "minimum_components_by_join_size": by_d}


def walk_certificate(n, edges, lengths, mask):
    N, expanded, paths = expand(n, edges, lengths)
    odd = [e for i, e in enumerate(edges) if mask >> i & 1]
    parity = [0] * n
    for a, b in odd:
        parity[a] ^= 1
        parity[b] ^= 1
    if any(parity) or not 0 <= mask < 1 << len(edges):
        raise ValueError("mask must be an even edge subset")
    parent = list(range(n))
    def root(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    def join(a, b):
        a, b = root(a), root(b)
        if a == b:
            return False
        parent[a] = b
        return True
    for a, b in odd:
        join(a, b)
    through = {i for i, (a, b) in enumerate(edges)
               if not mask >> i & 1 and join(a, b)}
    mult = {}
    for i, path in enumerate(paths):
        for j, (a, b) in enumerate(zip(path, path[1:])):
            mult[edge(a, b)] = 1 if mask >> i & 1 else (
                0 if i not in through and j == 0 else 2)
    check_walk(N, expanded, mult)
    return mult


def check_walk(n, edges, mult):
    if set(mult) - set(edges) or any(type(z) is not int or z < 0 for z in mult.values()):
        raise AssertionError("invalid multiplicities")
    degree = [0] * n
    for (a, b), z in mult.items():
        degree[a] += z
        degree[b] += z
    if any(d == 0 or d % 2 for d in degree):
        raise AssertionError("not spanning/even")
    if len(components(range(n), [e for e, z in mult.items() if z])) != 1:
        raise AssertionError("disconnected walk")
    return sum(mult.values())


def glue_points(x, y, v):
    """Exact degree-two articulation gluing; labels already share only v."""
    a = {b if a == v else a: z for (a, b), z in x.items() if v in (a, b)}
    b = {b if a == v else a: z for (a, b), z in y.items() if v in (a, b)}
    if sum(a.values(), Q(0)) != 2 or sum(b.values(), Q(0)) != 2:
        raise AssertionError("bad articulation degree")
    out = dict(x)
    for e, z in y.items():
        out[e] = out.get(e, Q(0)) + z
    for u, z in a.items():
        out[edge(u, v)] -= z / 2
    for w, z in b.items():
        out[edge(w, v)] -= z / 2
    for u, zu in a.items():
        for w, zw in b.items():
            e = edge(u, w)
            out[e] = out.get(e, Q(0)) + zu * zw / 4
    return {e: z for e, z in out.items() if z}


def star_point(vertices, edges):
    """Valid on a 2-connected fully subdivided block, not across articulations."""
    out = {e: Q(1) for e in edges}
    for v in sorted(vertices):
        near = sorted(b if a == v else a for a, b in edges if v in (a, b))
        d = len(near)
        if d <= 2:
            continue
        for w in near:
            out[edge(v, w)] = Q(2, d)
        gamma = Q(d - 2, d * (d - 1))
        for a, b in combinations(near, 2):
            e = edge(a, b)
            out[e] = out.get(e, Q(0)) + gamma
    return out


def primal(vertices, edges):
    """Recursive block decomposition uses literal expanded graph only."""
    vertices, edges = set(vertices), set(edges)
    if len(vertices) == 2:
        return {next(iter(edges)): Q(2)}
    for v in sorted(vertices):
        parts = components(vertices - {v}, [e for e in edges if v not in e])
        if len(parts) > 1:
            points = []
            for part in parts:
                vs = part | {v}
                es = {e for e in edges if set(e) <= vs}
                points.append(primal(vs, es))
            x = points[0]
            for y in points[1:]:
                x = glue_points(x, y, v)
            return x
    return star_point(vertices, edges)


def metric(n, edges):
    """Independent literal-graph Floyd-Warshall distances."""
    dist = [[0 if i == j else n + 1 for j in range(n)] for i in range(n)]
    for a, b in edges:
        dist[a][b] = dist[b][a] = 1
    for k in range(n):
        for i in range(n):
            for j in range(n):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    return dist


def mincut(n, point):
    """Exact rational Stoer-Wagner global minimum cut, with a witness shore."""
    adj = {v: {} for v in range(n)}
    for (a, b), z in point.items():
        adj[a][b] = adj[b][a] = z
    groups = {v: {v} for v in range(n)}
    best, shore = None, None
    while len(adj) > 1:
        used, weights, prev = set(), {v: Q(0) for v in adj}, None
        for i in range(len(adj)):
            v = max((v for v in adj if v not in used), key=lambda v: (weights[v], -v))
            used.add(v)
            if i == len(adj) - 1:
                if best is None or weights[v] < best:
                    best, shore = weights[v], set(groups[v])
                for w in list(adj):
                    if w not in (prev, v):
                        z = adj[prev].get(w, Q(0)) + adj[v].get(w, Q(0))
                        adj[prev][w] = adj[w][prev] = z
                        adj[w].pop(v, None)
                adj[prev].pop(v, None)
                groups[prev] |= groups.pop(v)
                del adj[v]
                break
            prev = v
            for w, z in adj[v].items():
                if w not in used:
                    weights[w] += z
    return best, shore


def check_primal(n, edges, point, exhaustive=False):
    if any(not 0 <= a < b < n or not isinstance(z, Q) or z < 0
           for (a, b), z in point.items()):
        raise AssertionError("invalid LP variables")
    for v in range(n):
        if sum((z for e, z in point.items() if v in e), Q(0)) != 2:
            raise AssertionError("degree equation")
    cut, shore = mincut(n, point)
    literal = sum((z for (a, b), z in point.items()
                   if (a in shore) != (b in shore)), Q(0))
    if literal != cut or cut < 2:
        raise AssertionError(("cut", cut, sorted(shore)))
    if exhaustive:
        direct = min(sum((z for (a, b), z in point.items()
                          if bool(mask >> a & 1) != bool(mask >> b & 1)), Q(0))
                     for mask in range(1, (1 << n) - 1) if mask & 1)
        if direct != cut:
            raise AssertionError("mincut disagrees with literal subset enumeration")
    dist = metric(n, edges)
    return sum((z * dist[a][b] for (a, b), z in point.items()), Q(0))


def dual(n, edges, lengths):
    """Weighted literal cuts cover each expanded graph edge exactly once."""
    N, expanded, paths = expand(n, edges, lengths)
    cuts, bridge_length = [], 0
    for i, path in enumerate(paths):
        pe = [edge(a, b) for a, b in zip(path, path[1:])]
        is_bridge = len(components(range(n), edges[:i] + edges[i+1:])) > 1
        if is_bridge:
            bridge_length += lengths[i]
            for e in pe:
                parts = components(range(N), expanded - {e})
                cuts.append((parts[0], Q(1)))
        else:
            for a, b in combinations(range(lengths[i]), 2):
                cuts.append((set(path[a + 1:b + 1]), Q(1, lengths[i] - 1)))
    return cuts, sum(lengths) + bridge_length


def check_dual(n, expanded, cuts):
    cover = {e: Q(0) for e in expanded}
    for shore, weight in cuts:
        if not shore or not shore < set(range(n)) or weight < 0:
            raise AssertionError("invalid dual cut")
        for a, b in expanded:
            if (a in shore) != (b in shore):
                cover[a, b] += weight
    if any(z != 1 for z in cover.values()):
        raise AssertionError("dual edge cover")
    return 2 * sum((z for _, z in cuts), Q(0))


def tour_dp(dist):
    """Literal expanded-metric Held-Karp DP; knows no core/length formula."""
    n = len(dist)
    dp = {(1, 0): 0}
    for _ in range(n - 1):
        nxt = {}
        for (mask, v), cost in dp.items():
            for w in range(1, n):
                if not mask >> w & 1:
                    key = mask | (1 << w), w
                    value = cost + dist[v][w]
                    nxt[key] = min(nxt.get(key, value), value)
        dp = nxt
    return min(cost + dist[v][0] for (_, v), cost in dp.items())


def check_instance(n, edges, lengths, use_dp=True):
    edges, lengths = list(edges), list(lengths)
    N, expanded, _ = expand(n, edges, lengths)
    value, mask = optimum(n, edges, lengths)
    walk = walk_certificate(n, edges, lengths, mask)
    assert check_walk(N, expanded, walk) == value
    cuts, expected_lp = dual(n, edges, lengths)
    assert check_dual(N, expanded, cuts) == expected_lp
    lp = check_primal(N, expanded, primal(range(N), expanded), exhaustive=N <= 10)
    assert lp == expected_lp
    if use_dp:
        actual = tour_dp(metric(N, expanded))
        assert actual == value, (n, edges, lengths, actual, value)
    return {"vertices": N, "tsp": value, "sep": int(lp)}


def double_octahedron():
    """Two K_(2,2,2)'s, opposite terminals 0,1 and 6,7; two cross edges."""
    edges = []
    for shift in (0, 6):
        edges += [(a + shift, b + shift) for a, b in combinations(range(6), 2)
                  if a // 2 != b // 2]
    return 12, edges + [(0, 6), (1, 7)]


def sweep():
    count = 0
    # All connected labeled simple cores through order 4, lengths independently 2/3.
    for n in range(2, 5):
        pairs = list(combinations(range(n), 2))
        for mask in range(1, 1 << len(pairs)):
            edges = [e for i, e in enumerate(pairs) if mask >> i & 1]
            if len(components(range(n), edges)) != 1:
                continue
            for lengths in product((2, 3), repeat=len(edges)):
                if n + sum(k - 1 for k in lengths) <= 11:
                    check_instance(n, edges, lengths)
                    count += 1
    # Parallel-edge cores, articulation and bridge compositions.
    extra = [(2, [(0, 1)] * k, [3] * k) for k in range(2, 5)]
    extra += [(5, [(0,1),(1,2),(2,0),(0,3),(3,4),(4,0)], [2]*6),
              (4, [(0,1),(0,1),(1,2),(2,3),(2,3)], [2,3,2,2,3])]
    for n, edges, lengths in extra:
        check_instance(n, edges, lengths)
        count += 1
    n, edges = double_octahedron()
    profile = uniform_profile(n, edges)
    large = []
    for length in (2, 3, 4):
        row = check_instance(n, edges, [length]*len(edges), use_dp=False)
        assert row["tsp"] == min(28*length-2, 30*length-8)
        large.append({"length": length, **row})
    return {"literal_metric_dp_cases": count,
            "double_octahedron": large, "uniform_profile": profile}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("specify --check")
    print(json.dumps(sweep(), sort_keys=True))
