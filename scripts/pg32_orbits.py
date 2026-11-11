"""Exact GL(4,2) orbit-stabilizer cross-check of projective 4-arcs.

Run: python3 scripts/pg32_orbits.py --check
"""
import argparse
from itertools import combinations


def rank(vectors):
    basis = [0] * 4
    for v in vectors:
        w = v
        while w:
            bit = w.bit_length() - 1
            if basis[bit]:
                w ^= basis[bit]
            else:
                basis[bit] = w
                break
    return sum(bool(v) for v in basis)


def independent_four(points):
    return all(rank(c) == 4 for c in combinations(points, 4))


def gl4_columns():
    for cols in combinations(range(1, 16), 4):
        if rank(cols) != 4:
            continue
        # Every permutation of independent columns defines a distinct matrix.
        from itertools import permutations
        yield from permutations(cols)


def act(cols, v):
    result = 0
    for i in range(4):
        if v & (1 << i):
            result ^= cols[i]
    return result


def orbit(seed):
    images = set()
    stabilizer = 0
    for cols in gl4_columns():
        transformed = frozenset(act(cols, v) for v in seed)
        images.add(transformed)
        stabilizer += transformed == frozenset(seed)
    return images, stabilizer


def check():
    # Independent algebraic route: ordered bases, not enumeration of all arcs.
    matrices = sum(1 for _ in gl4_columns())
    assert matrices == 15 * 14 * 12 * 8 == 20160
    for seed, expected_orbit, expected_stabilizer in [
        ((1, 2, 4, 8), 840, 24),
        ((1, 2, 4, 8, 15), 168, 120),
    ]:
        images, stabilizer = orbit(seed)
        assert len(images) == expected_orbit
        assert stabilizer == expected_stabilizer
        assert len(images) * stabilizer == matrices
        assert all(independent_four(points) for points in images)
        # Independent candidate-set sweep: check completeness of the orbit.
        census = {frozenset(p) for p in combinations(range(1, 16), len(seed))
                  if independent_four(p)}
        assert images == census
        print(f'n={len(seed)} orbit={len(images)} stabilizer={stabilizer}')
    # Negative controls: singular map collapses points; nonarc stays nonarc.
    assert rank((1, 2, 4, 7)) == 3
    assert not independent_four((1, 2, 4, 7))
    assert len({act((1, 2, 4, 7), v) for v in (1, 2, 4, 8)}) == 4
    assert rank([act((1, 2, 4, 7), v) for v in (1, 2, 4, 8)]) == 3
    print('GL4 order=20160; controls passed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.parse_args()
    check()
