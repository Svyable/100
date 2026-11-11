"""Independent exact PG(3,2) 4-arc census (known finite reproduction).

Run: python3 scripts/pg32_arc_census.py
Only stdlib; no external mathematical claims are inferred.
"""
from itertools import combinations, permutations

POINTS = tuple(range(1, 16))  # GF(2)^4 nonzero vectors, unique projective reps


def rank4(vectors):
    pivots = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def det4(vectors):
    """Leibniz determinant mod 2, independent of Gaussian elimination."""
    rows = [[(v >> j) & 1 for j in range(4)] for v in vectors]
    return sum(
        rows[0][p[0]] * rows[1][p[1]] * rows[2][p[2]] * rows[3][p[3]]
        for p in permutations(range(4))
    ) % 2


def is_arc(points, checker):
    return all(checker(quad) == 4 if checker is rank4 else checker(quad) == 1
               for quad in combinations(points, 4))


def census():
    result = {}
    for size in (4, 5, 6):
        count = 0
        for subset in combinations(POINTS, size):
            a = is_arc(subset, rank4)
            b = is_arc(subset, det4)
            assert a == b, (size, subset, a, b)
            count += a
        result[size] = count
    return result


def test_controls():
    basis = (1, 2, 4, 8)
    dependent = (1, 2, 4, 7)  # 7 = 1 xor 2 xor 4
    assert rank4(basis) == 4 and det4(basis) == 1
    assert rank4(dependent) == 3 and det4(dependent) == 0
    assert is_arc((1, 2, 4, 8, 15), rank4)
    assert is_arc((1, 2, 4, 8, 15), det4)
    assert not is_arc((1, 2, 4, 7, 8), rank4)
    assert not is_arc((1, 2, 4, 7, 8), det4)


if __name__ == '__main__':
    test_controls()
    counts = census()
    assert counts == {4: 840, 5: 168, 6: 0}, counts
    print('PG(3,2) 4-arc census:', counts)
    print('Two exact checkers agree on every subset; controls passed.')
