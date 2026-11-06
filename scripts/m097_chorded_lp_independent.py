"""Optional independent full-subtour LP cross-check (requires SciPy).

Graph construction and LP formulation are intentionally separate from
scripts.m097_chorded_multitheta. Not required for repository CI.
"""
from itertools import combinations, combinations_with_replacement
from scipy.optimize import linprog


def solve(lengths):
    k = len(lengths)
    n = 2 + sum(t - 1 for t in lengths)
    adj = [set() for _ in range(n)]

    def connect(u, v):
        adj[u].add(v)
        adj[v].add(u)

    connect(0, 1)
    next_v = 2
    for L in lengths:
        u = 0
        for _ in range(L - 1):
            connect(u, next_v)
            u = next_v
            next_v += 1
        connect(u, 1)
    d = []
    for u in range(n):
        seen = {u: 0}
        todo = [u]
        for v in todo:
            for w in adj[v]:
                if w not in seen:
                    seen[w] = seen[v] + 1
                    todo.append(w)
        d.append(seen)
    pairs = list(combinations(range(n), 2))
    c = [d[u][v] for u, v in pairs]
    Aeq = [[int(u == w or v == w) for u, v in pairs] for w in range(n)]
    Aub = []
    for mask in range(1, 1 << (n - 1)):
        Aub.append([-int(bool(mask & (1 << u)) != bool(mask & (1 << v))) for u, v in pairs])
    r = linprog(c, A_eq=Aeq, b_eq=[2] * n, A_ub=Aub,
                b_ub=[-2] * len(Aub), bounds=(0, None), method='highs')
    assert r.success, (lengths, r.message)
    assert abs(r.fun - sum(lengths)) < 1e-7, (lengths, r.fun)
    return r.fun


if __name__ == '__main__':
    count = 0
    for k in range(2, 5):
        for L in combinations_with_replacement(range(2, 7), k):
            if 2 + sum(t - 1 for t in L) > 8:
                continue
            solve(L)
            count += 1
    print('independent LP instances', count)
