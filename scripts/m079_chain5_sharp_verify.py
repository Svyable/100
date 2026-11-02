#!/usr/bin/env python3
"""Two independent semantic representations for M079 chain-five instances.

A factorial gap-block DP and a sparse full-poset topological-order DP.
These are author-side algorithms, not independent human mathematical review.
"""
from __future__ import annotations
from functools import lru_cache
from math import factorial

def gapblock(intervals):
    lo = min(a for a, b in intervals)
    hi = max(b for a, b in intervals)
    size = hi - lo + 1
    k = len(intervals)
    full = (1 << k) - 1
    transitions = [[] for _ in range(size)]
    for q in range(size):
        g = lo + q
        for mask in range(1 << k):
            eligible = sum(1 << i for i, (a, b) in enumerate(intervals)
                           if a <= g <= b and not (mask >> i & 1))
            mandatory = sum(1 << i for i, (a, b) in enumerate(intervals)
                            if b == g and not (mask >> i & 1))
            sub = eligible
            while True:
                if (sub & mandatory) == mandatory:
                    transitions[q].append((mask, mask | sub, sub,
                                           factorial(sub.bit_count())))
                if sub == 0:
                    break
                sub = (sub - 1) & eligible
    f = [[0] * (1 << k) for _ in range(size + 1)]
    f[0][0] = 1
    for q in range(size):
        for a, b, sub, w in transitions[q]:
            f[q + 1][b] += f[q][a] * w
    bwd = [[0] * (1 << k) for _ in range(size + 1)]
    bwd[size][full] = 1
    for q in range(size - 1, -1, -1):
        for a, b, sub, w in transitions[q]:
            bwd[q][a] += w * bwd[q + 1][b]
    e = f[size][full]
    assert e > 0 and e == bwd[0][0]
    weights = [[0] * size for _ in range(k)]
    pair = [[0] * k for _ in range(k)]
    for q in range(size):
        for a, b, sub, w in transitions[q]:
            v = f[q][a] * bwd[q + 1][b]
            if not v:
                continue
            for i in range(k):
                if sub >> i & 1:
                    weights[i][q] += v * w
                    for j in range(k):
                        if j == i or a >> j & 1:
                            continue
                        if sub >> j & 1:
                            pair[i][j] += v * w // 2
                        else:
                            pair[i][j] += v * w
    best = 0
    for i in range(k):
        cum = 0
        for q in range(size - 1):
            cum += weights[i][q]
            best = max(best, min(cum, e - cum))
        for j in range(i + 1, k):
            assert pair[i][j] + pair[j][i] == e
            best = max(best, min(pair[i][j], e - pair[i][j]))
    return e, best

def literal_balance_sparse(intervals):
    lo = min(a for a, b in intervals)
    hi = max(b for a, b in intervals)
    m = hi - lo
    n = m + len(intervals)
    pred = [0] * n
    for j in range(m):
        if j:
            pred[j] |= 1 << (j - 1)
        for i, (a, b) in enumerate(intervals):
            if b - lo <= j:
                pred[j] |= 1 << (m + i)
    for i, (a, b) in enumerate(intervals):
        for j in range(a - lo):
            pred[m + i] |= 1 << j
    full = (1 << n) - 1

    @lru_cache(None)
    def choices(mask):
        return tuple(v for v in range(n) if not (mask >> v & 1)
                     and pred[v] & mask == pred[v])

    @lru_cache(None)
    def suffix(mask):
        if mask == full:
            return 1
        return sum(suffix(mask | (1 << v)) for v in choices(mask))

    e = suffix(0)
    f = {0: 1}
    pair = [[0] * n for _ in range(n)]
    for rank in range(n):
        for mask in tuple(mask for mask in f if mask.bit_count() == rank):
            count = f[mask]
            for v in choices(mask):
                nxt = mask | (1 << v)
                ways = count * suffix(nxt)
                for w in range(n):
                    if w != v and not (mask >> w & 1):
                        pair[v][w] += ways
                f[nxt] = f.get(nxt, 0) + count
    assert f[full] == e
    assert all(pair[i][j] + pair[j][i] == e
               for i in range(n) for j in range(i + 1, n))
    best = max(min(pair[i][j], pair[j][i])
               for i in range(n) for j in range(i + 1, n))
    return e, best
