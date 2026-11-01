#!/usr/bin/env python3
"""Exact insertion-gap proof certificate for the M079 chain-plus-two class.

No external solver. The 27 residual cases are finite *algebraic* certificates;
a separate order-ideal DP checks actual linear-extension counts. This is not
independent specialist review or an unrestricted poset theorem.
"""
import argparse
import json
import random
from functools import lru_cache
from fractions import Fraction

BOUND = Fraction(4, 11)

# (length of x interval, length of y interval, y_start-x_start,
#  witnessing pair, exact probability for the first member preceding second).
# All 27 overlap-at-least-two cases with both lengths <= 4.
ROWS = (
    (2, 2, 0, "xy", "1/2"),
    (2, 3, -1, "xy", "3/8"),
    (2, 3, 0, "xy", "5/8"),
    (2, 4, -2, "y,c2", "2/5"),
    (2, 4, -1, "xy", "1/2"),
    (2, 4, 0, "x,c1", "1/2"),
    (3, 2, 0, "xy", "3/8"),
    (3, 2, 1, "xy", "5/8"),
    (3, 3, -1, "x,c2", "4/11"),
    (3, 3, 0, "xy", "1/2"),
    (3, 3, 1, "x,c2", "7/11"),
    (3, 4, -2, "y,c2", "3/7"),
    (3, 4, -1, "xy", "2/5"),
    (3, 4, 0, "xy", "3/5"),
    (3, 4, 1, "y,c3", "4/7"),
    (4, 2, 0, "y,c1", "1/2"),
    (4, 2, 1, "xy", "1/2"),
    (4, 2, 2, "x,c2", "2/5"),
    (4, 3, -1, "x,c3", "4/7"),
    (4, 3, 0, "xy", "2/5"),
    (4, 3, 1, "xy", "3/5"),
    (4, 3, 2, "x,c2", "3/7"),
    (4, 4, -2, "y,c2", "4/9"),
    (4, 4, -1, "y,c2", "9/19"),
    (4, 4, 0, "xy", "1/2"),
    (4, 4, 1, "x,c2", "9/19"),
    (4, 4, 2, "x,c2", "4/9"),
)


def canonical_intervals(lx, ly, delta):
    if lx < 1 or ly < 1:
        raise ValueError("interval lengths must be positive")
    ax, ay = max(0, -delta), max(0, delta)
    return (ax, ax + lx - 1), (ay, ay + ly - 1)


def overlap(ix, iy):
    return max(0, min(ix[1], iy[1]) - max(ix[0], iy[0]) + 1)


def probabilities(ix, iy):
    """First path: closed-form counts from gap insertion."""
    a, b = ix
    c, d = iy
    if min(a, c) < 0 or a > b or c > d:
        raise ValueError("invalid gaps")
    lx, ly = b - a + 1, d - c + 1
    r = overlap(ix, iy)
    if r < 1:
        raise ValueError("x and y would be comparable via the chain")
    n = lx * ly + r
    # In the same gap there are TWO linear extensions, one in each order.
    before_xy = sum((i < j) + (i == j)
                    for i in range(a, b + 1) for j in range(c, d + 1))
    result = {"xy": Fraction(before_xy, n)}
    for k in range(1, max(b, d) + 1):
        nx = sum(ly + (c <= i <= d) for i in range(a, b + 1) if i < k)
        ny = sum(lx + (a <= j <= b) for j in range(c, d + 1) if j < k)
        result[f"x,c{k}"] = Fraction(nx, n)
        result[f"y,c{k}"] = Fraction(ny, n)
    return n, result


def balance(probs):
    return max(min(p, 1 - p) for p in probs.values())


def order_ideal_count(ix, iy, pair=None):
    """Independent path: count topological sorts via predecessor bitmasks.

    Does not use the gap-counting formula, pairwise gap placements, or
    the ROWS certificate. Adds a precedence edge to count a pair event.
    """
    m = max(ix[1], iy[1])
    n = m + 2
    x, y = m, m + 1
    req = [0] * n
    for j in range(1, m):
        req[j] |= 1 << (j - 1)
    for v, (a, b) in ((x, ix), (y, iy)):
        if a:
            req[v] |= 1 << (a - 1)
        if b < m:
            req[b] |= 1 << v
    if pair is not None:
        left, right = pair
        req[right] |= 1 << left

    @lru_cache(None)
    def count(mask):
        if mask == (1 << n) - 1:
            return 1
        return sum(count(mask | (1 << v)) for v in range(n)
                   if not (mask & (1 << v)) and not (req[v] & ~mask))
    return count(0)


def pair_indices(name, m):
    if name == "xy":
        return (m, m + 1)
    left, right = name.split(",")
    return (m if left == "x" else m + 1, int(right[1:]) - 1)


def exact_dp_probabilities(ix, iy):
    """Check all incomparable-pair events, including x-y and x-chain."""
    total = order_ideal_count(ix, iy)
    if not total:
        raise AssertionError("unexpected cyclic poset")
    _, formula = probabilities(ix, iy)
    m = max(ix[1], iy[1])
    return total, {name: Fraction(order_ideal_count(ix, iy, pair_indices(name, m)), total)
                   for name in formula}


def verify_residual():
    found = set()
    for lx, ly, delta, name, expected in ROWS:
        key = (lx, ly, delta)
        if key in found:
            raise AssertionError("duplicate case")
        found.add(key)
        ix, iy = canonical_intervals(lx, ly, delta)
        if overlap(ix, iy) < 2:
            raise AssertionError("not a width-three overlap")
        n, formula = probabilities(ix, iy)
        if formula[name] != Fraction(expected):
            raise AssertionError((key, name, formula[name], expected))
        if not BOUND <= formula[name] <= 1 - BOUND:
            raise AssertionError((key, name))
        independent_total, dp = exact_dp_probabilities(ix, iy)
        if independent_total != n or dp != formula:
            raise AssertionError(("DP disagreement", key, n, independent_total))
    expected_keys = {(lx, ly, delta)
                     for lx in range(2, 5) for ly in range(2, 5)
                     for delta in range(-(ly - 1), lx)
                     if overlap(*canonical_intervals(lx, ly, delta)) >= 2}
    if found != expected_keys or len(found) != 27:
        raise AssertionError(("incomplete residual cases", expected_keys - found, found - expected_keys))
    return len(found)


def verify_large_atom_inequality():
    """Check finite boundary arithmetic; the all-L proof is in the dossier."""
    for lx in range(5, 20):
        for ly in range(2, 20):
            for r in range(2, min(lx, ly) + 1):
                max_mass = Fraction(ly + 1, lx * ly + r)
                if max_mass > Fraction(1, 4):
                    raise AssertionError((lx, ly, r, max_mass))
    # Boundary L=5, M=2, r=2 attains 1/4; 1/4 < 3/11.
    assert Fraction(3, 12) == Fraction(1, 4) < 1 - 2 * BOUND


def verify_adversarial():
    sharp_ix, sharp_iy = canonical_intervals(3, 3, -1)
    n, p = probabilities(sharp_ix, sharp_iy)
    if n != 11 or balance(p) != BOUND:
        raise AssertionError("sharp case failed")
    # Strictly stronger universal constants fail on this width-three poset.
    if not balance(p) < Fraction(5, 11):
        raise AssertionError("stronger false bound accepted")
    # Missing the two same-gap permutations changes the answer.
    wrong_n = 3 * 3
    if wrong_n == n:
        raise AssertionError("same-gap multiplicity mutation undetected")
    # Overlap one is NOT width three, and must be excluded.
    ix, iy = canonical_intervals(2, 2, 1)
    if overlap(ix, iy) != 1:
        raise AssertionError("invalid width-three negative control")


def verify_random(seed=7902, trials=320):
    rng = random.Random(seed)
    checked = 0
    for _ in range(trials):
        m = rng.randint(2, 10)
        a, b = sorted(rng.sample(range(m + 1), 2))
        c, d = sorted(rng.sample(range(m + 1), 2))
        ix, iy = (a, b), (c, d)
        if overlap(ix, iy) < 2:
            continue
        n, p = probabilities(ix, iy)
        dn, dp = exact_dp_probabilities(ix, iy)
        if n != dn or p != dp:
            raise AssertionError(("random mismatch", ix, iy))
        if balance(p) < BOUND:
            raise AssertionError(("counterexample", ix, iy, balance(p)))
        checked += 1
    return checked


def check():
    residual = verify_residual()
    verify_large_atom_inequality()
    verify_adversarial()
    random_checked = verify_random()
    return {"result": "self_checked_not_independently_reviewed",
            "restricted_class": "width-three posets with a chain after deleting two incomparable elements",
            "sharp_balance": "4/11", "residual_cases": residual,
            "random_dp_cases": random_checked, "seed": 7902,
            "exact_extremizer": {"x_gaps": [1, 3], "y_gaps": [0, 2],
                                 "chain_length": 3, "extensions": 11}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = check()
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print("M079 chain-plus-two exact check:", result)


if __name__ == "__main__":
    main()
