"""Exact author-side certificate for a deep interior cross-edge in chorded multitheta.

Usage: python3 -m scripts.m097_interior_cross --check
No independent mathematical or historical-novelty review is implied.
"""
import argparse
from collections import deque
from fractions import Fraction
from itertools import combinations, product


def instance(lengths, a, b):
    lengths = tuple(lengths)
    if len(lengths) < 3 or min(lengths) < 2:
        raise ValueError("need at least three paths of length >=2")
    if not (2 <= a <= lengths[0]-2 and 2 <= b <= lengths[1]-2):
        raise ValueError("cross endpoints must be >=2 edges from each hub")
    n = 2 + sum(L-1 for L in lengths)
    adj = [set() for _ in range(n)]
    def edge(i, j):
        if i == j:
            raise ValueError("loop")
        adj[i].add(j)
        adj[j].add(i)
    edge(0, 1)
    paths = []
    nxt = 2
    for L in lengths:
        p = [0] + list(range(nxt, nxt+L-1)) + [1]
        nxt += L-1
        paths.append(p)
        for i, j in zip(p, p[1:]):
            edge(i, j)
    edge(paths[0][a], paths[1][b])
    return adj, paths


def metric(adj):
    n = len(adj)
    dist = []
    for root in range(n):
        row = [n+1]*n
        row[root] = 0
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if row[v] > row[u]+1:
                    row[v] = row[u]+1
                    queue.append(v)
        if max(row) > n:
            raise AssertionError("disconnected graph")
        dist.append(row)
    return dist


def rational_witness(paths):
    k = len(paths)
    alpha = Fraction(2, k)
    gamma = Fraction(k-2, k*(k-1))
    x = {}
    def add(i, j, z):
        key = tuple(sorted((i, j)))
        x[key] = x.get(key, Fraction(0)) + z
    for p in paths:
        L = len(p)-1
        for i in range(L):
            add(p[i], p[i+1], alpha if i in (0, L-1) else Fraction(1))
    for i, j in combinations(range(k), 2):
        add(paths[i][1], paths[j][1], gamma)
        add(paths[i][-2], paths[j][-2], gamma)
    return x


def verify_witness(adj, paths, x):
    n = len(adj)
    d = metric(adj)
    deg = [Fraction(0)]*n
    for (i, j), v in x.items():
        if v < 0 or i == j:
            raise AssertionError("invalid LP variable")
        deg[i] += v
        deg[j] += v
    if any(z != 2 for z in deg):
        raise AssertionError("degree failure")
    # Every nontrivial cut, modulo complementation; node 0 is outside.
    for mask in range(1, 1 << (n-1)):
        side = mask << 1
        cut = sum(v for (i, j), v in x.items()
                  if bool(side >> i & 1) != bool(side >> j & 1))
        if cut < 2:
            raise AssertionError(("subtour cut failure", mask, cut))
    cost = sum(v*d[i][j] for (i, j), v in x.items())
    if cost != sum(len(p)-1 for p in paths):
        raise AssertionError(("wrong objective", cost))
    return cost


def exact_tour(d):
    n = len(d)
    if n > 16:
        raise ValueError("DP limited to 16 vertices")
    # Independent Held-Karp recurrence, not using the parity proof.
    dp = {(1 << j, j): d[0][j] for j in range(1, n)}
    for size in range(2, n):
        new = {}
        for (mask, last), cost in dp.items():
            for nxt in range(1, n):
                if mask >> nxt & 1:
                    continue
                key = (mask | 1 << nxt, nxt)
                z = cost + d[last][nxt]
                if z < new.get(key, 10**9):
                    new[key] = z
        dp = new
    full = (1 << n)-2
    return min(cost+d[last][0] for (mask, last), cost in dp.items()
               if mask == full)


def check_instance(lengths, a, b):
    adj, paths = instance(lengths, a, b)
    m = sum(lengths)
    cost = verify_witness(adj, paths, rational_witness(paths))
    tour = exact_tour(metric(adj))
    expected = m + (len(lengths) % 2)*int(min(lengths) >= 3)
    if cost != m or tour != expected:
        raise AssertionError((lengths, a, b, cost, tour, expected))
    return cost, tour


def run():
    count = 0
    for k in range(3, 6):
        for L1 in range(4, 7):
            for L2 in range(4, 7):
                for rest in product(range(2, 5), repeat=k-2):
                    L = (L1, L2) + rest
                    if 2 + sum(v-1 for v in L) > 12:
                        continue
                    for a in range(2, L1-1):
                        for b in range(2, L2-1):
                            check_instance(L, a, b)
                            count += 1
    # Deep-to-shallow mutation falsifies unrestricted tour invariance.
    adj, paths = instance((4, 4, 3), 2, 2)
    assert exact_tour(metric(adj)) == 12
    adj[paths[0][2]].remove(paths[1][2])
    adj[paths[1][2]].remove(paths[0][2])
    adj[paths[0][2]].add(paths[1][3])
    adj[paths[1][3]].add(paths[0][2])
    assert exact_tour(metric(adj)) == 11
    # Adversarial LP mutation: degree constraints must reject chord mass.
    adj, paths = instance((4, 4, 2), 2, 2)
    x = rational_witness(paths)
    x[(0, 1)] = Fraction(1)
    try:
        verify_witness(adj, paths, x)
    except AssertionError:
        pass
    else:
        raise AssertionError("tampered LP witness accepted")
    print(f"PASS: {count} exact rational all-cut witnesses and tour DPs; boundary/tamper controls")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    run()
