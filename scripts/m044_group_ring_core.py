"""Exact F2 group-algebra arithmetic for *finite* groups only.

Elements are bit masks of basis group elements; this cannot reduce words in
an arbitrary finitely presented (in particular torsion-free) group.
"""
from itertools import permutations


def validate(table):
    n = len(table)
    if not n or any(len(row) != n or set(row) != set(range(n)) for row in table):
        raise ValueError('not a Latin multiplication table')
    identities = [e for e in range(n) if all(table[e][a] == a == table[a][e] for a in range(n))]
    if len(identities) != 1:
        raise ValueError('missing unique identity')
    for a in range(n):
        for b in range(n):
            for c in range(n):
                if table[table[a][b]][c] != table[a][table[b][c]]:
                    raise ValueError('nonassociative table')
    return identities[0]


def multiply(a, b, table):
    n = len(table)
    if a < 0 or b < 0 or a >= (1 << n) or b >= (1 << n):
        raise ValueError('element outside F2[G]')
    out = 0
    while a:
        low = a & -a
        i = low.bit_length() - 1
        a ^= low
        bb = b
        while bb:
            low_b = bb & -bb
            j = low_b.bit_length() - 1
            bb ^= low_b
            out ^= 1 << table[i][j]
    return out


def reference_multiply(a, b, table):
    """Separate dense coefficient-sum implementation."""
    n = len(table)
    return sum((sum(((a >> i) & 1) * ((b >> j) & 1)
                    for i in range(n) for j in range(n) if table[i][j] == k) % 2) << k
               for k in range(n))


def cyclic(n):
    return [[(i + j) % n for j in range(n)] for i in range(n)]


def symmetric_three():
    elems = list(permutations(range(3)))
    index = {p: i for i, p in enumerate(elems)}
    return [[index[tuple(p[q[x]] for x in range(3))] for q in elems] for p in elems]


def check():
    for table in (cyclic(3), symmetric_three()):
        e = validate(table)
        one = 1 << e
        n = len(table)
        for a in range(1 << n):
            assert multiply(one, a, table) == multiply(a, one, table) == a
            for b in range(1 << n):
                ab = multiply(a, b, table)
                assert ab == reference_multiply(a, b, table)
                if ab == one:
                    assert multiply(b, a, table) == one
    # (1+g)(1+g+g^2)=0 in F2[C3].
    t = cyclic(3)
    assert multiply(0b011, 0b111, t) == 0
    for bad in ([], [[0, 0], [1, 1]], [[0, 1], [0, 1]]):
        try:
            validate(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid table accepted')
    # A nonassociative Latin loop of order five is not needed: mutate S3
    # by swapping two outputs in a row, which must fail validation.
    t = symmetric_three()
    t[0][0], t[0][1] = t[0][1], t[0][0]
    try:
        validate(t)
    except ValueError:
        pass
    else:
        raise AssertionError('corrupted table accepted')
    return 'C3 and S3: 4160 exhaustive product comparisons, inverse and zero-divisor controls passed'


if __name__ == '__main__':
    print(check())
