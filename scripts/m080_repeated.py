#!/usr/bin/env python3
"""M080: exact S4 orbit count and repeated-basis Rota grids over GF(2)^4.

Scope: first row fixed to E, other three rows an unordered multiset of
unlabelled four-vector bases.  This certifies *only* multisets with a
repeated basis; it does not settle the all-distinct 4,111,138 orbits.
"""
from collections import Counter
from itertools import combinations, permutations
from math import comb, factorial, prod
from hashlib import sha256
from pathlib import Path
import argparse
import json

PERMS = tuple(permutations(range(4)))
EXPECTED_CLASSES = {
    (1, 1, 1, 1): (840, 0, 0, 0, 99137080),
    (1, 1, 2): (48, 396, 0, 0, 38608),
    (2, 2): (12, 414, 0, 0, 5332),
    (1, 3): (6, 0, 278, 0, 334),
    (4,): (2, 5, 0, 207, 14),
}
DATA = Path(__file__).resolve().parents[1] / "data" / "m080_repeated_codes.bin"


def rank(vectors):
    """Independent rows over GF(2), by XOR elimination."""
    pivots = [0] * 4
    for vector in vectors:
        x = vector
        for k in range(3, -1, -1):
            if x & (1 << k):
                if pivots[k]:
                    x ^= pivots[k]
                else:
                    pivots[k] = x
                    break
        else:
            return False
    return True


def determinant(vectors):
    """Independent checker: Leibniz expansion modulo two, not elimination."""
    if len(vectors) != 4:
        raise ValueError("four rows required")
    return sum(all((vectors[i] >> p[i]) & 1 for i in range(4))
               for p in PERMS) % 2


def all_bases():
    result = tuple(b for b in combinations(range(1, 16), 4) if rank(b))
    assert len(result) == prod(16 - 2**k for k in range(4)) // factorial(4) == 840
    return result


def transform_vector(v, p):
    return sum(((v >> i) & 1) << p[i] for i in range(4))


def transform_basis(b, p):
    return tuple(sorted(transform_vector(v, p) for v in b))


def cycle_type(p):
    seen = set()
    lengths = []
    for i in range(4):
        if i in seen:
            continue
        j, length = i, 0
        while j not in seen:
            seen.add(j)
            j = p[j]
            length += 1
        lengths.append(length)
    return tuple(sorted(lengths))


def orbit_representatives(bases):
    seen = set()
    reps = []
    for b in bases:
        if b in seen:
            continue
        reps.append(b)
        seen.update(transform_basis(b, p) for p in PERMS)
    assert len(seen) == 840 and len(reps) == 51
    return tuple(reps)


def orbit_table(bases):
    """Burnside cycle index on the 840 unordered bases."""
    index = {b: i for i, b in enumerate(bases)}
    table = {}
    class_sizes = Counter()
    for p in PERMS:
        action = tuple(index[transform_basis(b, p)] for b in bases)
        assert len(set(action)) == len(bases)
        seen = set()
        cycles = Counter()
        for i in range(len(bases)):
            if i in seen:
                continue
            j, length = i, 0
            while j not in seen:
                seen.add(j)
                j = action[j]
                length += 1
            cycles[length] += 1
        c1, c2, c3 = (cycles[k] for k in (1, 2, 3))
        fixed = comb(c1 + 2, 3) + c1*c2 + c3
        key = cycle_type(p)
        value = (c1, c2, c3, cycles[4], fixed)
        if key in table:
            assert table[key] == value
        table[key] = value
        class_sizes[key] += 1
    assert table == EXPECTED_CLASSES
    assert sorted(class_sizes.values()) == [1, 3, 6, 6, 8]
    all_same = sum(class_sizes[k]*v[0] for k, v in table.items()) // 24
    two_same = sum(class_sizes[k]*v[0]*(v[0]-1) for k, v in table.items()) // 24
    all_distinct = sum(class_sizes[k]*(comb(v[0], 3) + v[0]*v[1] + v[2])
                       for k, v in table.items()) // 24
    total = sum(class_sizes[k]*v[4] for k, v in table.items()) // 24
    assert (all_same, two_same, all_distinct, total) == (51, 29956, 4111138, 4141145)
    assert total * 24 == sum(class_sizes[k]*v[4] for k, v in table.items())
    return table, class_sizes, (all_same, two_same, all_distinct, total)


def _has_matching(masks):
    """Four-element perfect matching; returns column-to-vector positions."""
    for p in PERMS:
        if all(masks[i] & (1 << p[i]) for i in range(4)):
            return p
    return None


def find_grid(repeated, other):
    """Construct row permutations for E, B, B, C by rank/matching search."""
    ordered = tuple(tuple(repeated[j] for j in p) for p in PERMS)
    for i, row1 in enumerate(ordered):
        for j, row2 in enumerate(ordered):
            if not all(rank((1 << k, row1[k], row2[k])) for k in range(4)):
                continue
            masks = tuple(sum((1 << h) for h, v in enumerate(other)
                              if rank((1 << k, row1[k], row2[k], v)))
                          for k in range(4))
            if any(m == 0 for m in masks):
                continue
            matching = _has_matching(masks)
            if matching is not None:
                return (i, j, PERMS.index(matching))
    raise AssertionError(f"no repeated-row grid: {repeated}, {other}")


def verify_grid(repeated, other, code):
    """Replay one certificate by independent Leibniz determinants."""
    if len(code) != 3 or any(not 0 <= v < 24 for v in code):
        raise ValueError("three row permutation indices in 0..23 required")
    row1 = tuple(repeated[j] for j in PERMS[code[0]])
    row2 = tuple(repeated[j] for j in PERMS[code[1]])
    row3 = tuple(other[j] for j in PERMS[code[2]])
    for k in range(4):
        if determinant((1 << k, row1[k], row2[k], row3[k])) != 1:
            raise AssertionError(f"dependent column {k}")
    return True


def build_certificate(bases, reps):
    output = bytearray()
    for repeated in reps:
        for other in bases:
            code = find_grid(repeated, other)
            verify_grid(repeated, other, code)
            output.extend(code)
    assert len(output) == 51 * 840 * 3
    return bytes(output)


def replay_certificate(data, bases, reps):
    if len(data) != 51 * 840 * 3:
        raise ValueError("wrong certificate length")
    # Independent of the generator's XOR search: check every base by determinant.
    if any(determinant(b) != 1 for b in bases):
        raise AssertionError("nonbasis in 840-basis list")
    for i, repeated in enumerate(reps):
        for j, other in enumerate(bases):
            start = (i*840 + j)*3
            verify_grid(repeated, other, data[start:start+3])
    return True


def report(data):
    bases = all_bases()
    reps = orbit_representatives(bases)
    table, classes, orbits = orbit_table(bases)
    replay_certificate(data, bases, reps)
    return {
        "bases": len(bases),
        "S4_basis_orbits": len(reps),
        "raw_three_multisets": comb(842, 3),
        "orbit_multiplicity": {"all_equal": orbits[0], "two_equal": orbits[1],
                               "all_distinct": orbits[2], "total": orbits[3]},
        "repeated_representative_pairs_checked": len(reps)*len(bases),
        "certificate_bytes": len(data),
        "certificate_sha256": sha256(data).hexdigest(),
        "class_table": {"".join(map(str, k)): {"size": classes[k], "cycles": list(v[:4]),
                                             "fixed_three_multisets": v[4]}
                        for k, v in sorted(table.items())},
        "boundary": "All repeated-base inputs GF(2)^4 only; no all-distinct grid result."
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="create binary witness archive")
    ap.add_argument("--check", action="store_true", help="replay witness archive")
    args = ap.parse_args()
    if args.write:
        DATA.write_bytes(build_certificate(all_bases(), orbit_representatives(all_bases())))
    if args.check or args.write:
        print(json.dumps(report(DATA.read_bytes()), indent=2, sort_keys=True))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
