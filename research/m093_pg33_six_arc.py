"""Exact, bounded PG(3,3) 4-arc obstruction; known finite mathematics.

Run: python3 research/m093_pg33_six_arc.py
"""
from itertools import combinations, product

P = 3

def det(matrix):
    a = [list(row) for row in matrix]
    ans = 1
    for j in range(len(a)):
        pivot = next((i for i in range(j, len(a)) if a[i][j] % P), None)
        if pivot is None:
            return 0
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            ans = -ans
        v = a[j][j] % P
        ans = ans * v % P
        inv = pow(v, -1, P)
        for i in range(j + 1, len(a)):
            factor = a[i][j] * inv % P
            for k in range(j, len(a)):
                a[i][k] = (a[i][k] - factor * a[j][k]) % P
    return ans % P

def independent4(points):
    return det([list(row) for row in zip(*points)]) != 0

def is_arc(points):
    return all(independent4(s) for s in combinations(points, 4))

basis = [tuple(int(i == j) for i in range(4)) for j in range(4)]
candidates = [(1, *signs) for signs in product((1, 2), repeat=3)]
assert len(candidates) == 8
assert all(is_arc(basis + [u]) for u in candidates)
assert not is_arc(basis + [(1, 0, 1, 1)])  # missing coordinate
assert not is_arc(basis + [candidates[0], candidates[0]])  # duplicate
pairs = list(combinations(candidates, 2))
valid = [pair for pair in pairs if is_arc(basis + list(pair))]
assert len(pairs) == 28 and len(valid) == 0
# Independent pair obstruction: every coordinate ratio u_i/v_i must be distinct;
# but there are four coordinates and only two nonzero field elements.
assert all(len({u[i] * pow(v[i], -1, 3) % 3 for i in range(4)}) < 4 for u,v in pairs)
print('PG(3,3): 8 normalized fifth points, 28 candidate sixth-point pairs, 0 six-arcs; five-arc witness verified')
