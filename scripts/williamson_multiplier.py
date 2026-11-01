"""Exact row-sum obstruction to over-restricting Williamson n=29 multipliers.

This is a *necessary-condition* screen, not a Williamson construction or a
proof of Hadamard nonexistence. See research/M094_MULTIPLIER_GATE.md.
"""
import argparse
import itertools
import json
from math import gcd, isqrt

N = 29
TARGET = 4 * N


def multiplier_orbits(n, multiplier):
    """Orbits on Z/n under reversal and multiplication by a unit."""
    if n < 3 or n % 2 != 1 or gcd(n, multiplier) != 1:
        raise ValueError("odd n>=3 and an invertible multiplier required")
    seen, orbits = set(), []
    for x in range(n):
        if x in seen:
            continue
        orbit, todo = {x}, [x]
        while todo:
            y = todo.pop()
            for z in ((-y) % n, (multiplier * y) % n):
                if z not in orbit:
                    orbit.add(z)
                    todo.append(z)
        seen.update(orbit)
        orbits.append(tuple(sorted(orbit)))
    return tuple(orbits)


def row_sums_from_orbits(orbits):
    """All row sums of +/-1 sequences constant on each given orbit."""
    sizes = [len(orbit) for orbit in orbits]
    return tuple(sorted({
        sum(sign * size for sign, size in zip(signs, sizes))
        for signs in itertools.product((-1, 1), repeat=len(sizes))
    }))


def row_sum_screen(n, multiplier):
    """Reject only when the necessary four-square identity is impossible."""
    orbits = multiplier_orbits(n, multiplier)
    sums = row_sums_from_orbits(orbits)
    small = tuple(s for s in sums if s * s <= 4 * n)
    witness = next((
        four for four in itertools.product(small, repeat=4)
        if sum(s * s for s in four) == 4 * n
    ), None)
    return {
        "n": n, "multiplier": multiplier,
        "orbit_sizes": [len(o) for o in orbits],
        "eligible_row_sums": list(small),
        "four_square_witness": list(witness) if witness else None,
        "row_sum_obstructed": witness is None,
    }


def independent_n29_gate(multiplier):
    """Independent arithmetic derivation; does not call orbit enumeration.

    For 12, 12^2=-1 mod 29 and its order is four: 0 plus seven
    four-element orbits. For 7, order seven and -1 independent:
    0 plus two fourteen-element orbits.
    """
    if multiplier == 12:
        assert 12 * 12 % 29 == 28 and pow(12, 4, 29) == 1
        sums = {
            e + 4 * (2 * k - 7)
            for e in (-1, 1) for k in range(8)
        }
        assert {abs(s) for s in sums if s * s <= TARGET} == {3, 5}
        # Four squares are at most 4*25=100, strictly below 116.
        return True
    if multiplier == 7:
        assert pow(7, 7, 29) == 1
        assert all(pow(7, k, 29) != 1 for k in range(1, 7))
        sums = {e + 14 * a + 14 * b
                for e, a, b in itertools.product((-1, 1), repeat=3)}
        assert {abs(s) for s in sums if s * s <= TARGET} == {1}
        # Four squares are exactly 4, not 116.
        return True
    raise ValueError("independent derivation only covers 12 and 7")


def audit():
    restricted = [row_sum_screen(N, g) for g in (12, 7)]
    control = row_sum_screen(N, 28)  # reversal alone: no extra restriction
    assert all(r["row_sum_obstructed"] for r in restricted)
    assert all(independent_n29_gate(g) for g in (12, 7))
    assert control["four_square_witness"] is not None
    assert sorted(control["orbit_sizes"]) == [1] + [2] * 14
    return {"scope": "common multiplier symmetry, Williamson n=29 only",
            "restricted": restricted, "reversal_only_control": control,
            "full_williamson_n29_search": "NOT PERFORMED",
            "hadamard_116_nonexistence": "NOT CLAIMED"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = audit()
    if args.check:
        print("M094 n29 multiplier row-sum gate: PASS (restricted obstruction only)")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
