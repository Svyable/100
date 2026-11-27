#!/usr/bin/env python3
"""Exact residual certificate for research/M079_UNIFORM_SPLIT_BALANCE.md.

Run: python3 scripts/m079_uniform_split.py
Standard library only; all arithmetic is exact. No unrestricted M079 claim.
"""
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import factorial

EXPECTED = {2: 9, 3: 32, 4: 65, 5: 49, 6: 49}
MINIMA = {2: Fraction(2, 5), 3: Fraction(28, 69),
          4: Fraction(671, 1537), 5: Fraction(6529, 15414),
          6: Fraction(40423, 88060)}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def residual(k):
    for left in combinations(range(1, 2*k), k-1):
        a = tuple(-x for x in reversed(left)) + (0,)
        for right in combinations(range(1, 2*k), k-1):
            b = (0,) + right
            I = tuple(zip(a, b))
            if any(y-x+1 > 2*k for x, y in I):
                continue
            r = {g: sum(not x <= g <= y for x, y in I)
                 for g in range(a[0], b[-1]+1)}
            if any(sum((Fraction(1, r[g]+1) for g in range(x, y+1)
                        if g != 0), Fraction(0)) >= 2 for x, y in I):
                continue
            yield I


def counts(I):
    """Sequential one-element order-ideal recurrence; all gap marginals."""
    k = len(I)
    full = (1 << k)-1
    lo, hi = min(a for a, b in I), max(b for a, b in I)

    @lru_cache(None)
    def B(g, S):
        if g > hi:
            return int(S == full)
        n = 0
        if all(S >> i & 1 or g < b for i, (a, b) in enumerate(I)):
            n += B(g+1, S)
        for i, (a, b) in enumerate(I):
            if not S >> i & 1 and a <= g <= b:
                n += B(g, S | 1 << i)
        return n

    E = B(lo, 0)
    F = {(lo, 0): 1}
    W = [[0]*(hi-lo+1) for _ in I]
    for g in range(lo, hi+1):
        for S in range(full+1):
            f = F.get((g, S), 0)
            if not f:
                continue
            if all(S >> i & 1 or g < b for i, (a, b) in enumerate(I)):
                F[g+1, S] = F.get((g+1, S), 0)+f
            for i, (a, b) in enumerate(I):
                if not S >> i & 1 and a <= g <= b:
                    T = S | 1 << i
                    F[g, T] = F.get((g, T), 0)+f
                    W[i][g-lo] += f*B(g, T)
    require(E > 0 and all(sum(w) == E for w in W), ('bad marginal', I))
    return E, lo, W


def blocks(I, lo, hi):
    """Separate factorial gap-block recurrence; exact extension count."""
    full = (1 << len(I))-1
    D = {0: 1}
    for g in range(lo, hi+1):
        A = sum(1 << i for i, (a, b) in enumerate(I) if a <= g <= b)
        M = sum(1 << i for i, (a, b) in enumerate(I) if b == g)
        N = {}
        for S, v in D.items():
            T = A & ~S
            U = T
            while True:
                if M & ~(S | U) == 0:
                    V = S | U
                    N[V] = N.get(V, 0)+v*factorial(U.bit_count())
                if U == 0:
                    break
                U = (U-1) & T
        D = N
    return D.get(full, 0)


def verify_witness(I, E, i, g, n, lo, hi):
    require(blocks(I, lo, hi) == E, ('total mismatch', I))
    J = list(I)
    J[i] = (J[i][0], min(J[i][1], g))
    require(blocks(J, lo, hi) == n, ('witness mismatch', I))
    require(3*min(n, E-n) >= E, ('unbalanced witness', I))


def main():
    # Adversarial control: equal modal gaps need not balance the outsider pair.
    # For [-1,0], [0,1], E=5, both common-gap counts=3, but x<y in 4/5.
    I = ((-1, 0), (0, 1))
    E, lo, W = counts(I)
    require((E, lo, W) == (5, -1, [[2, 3, 0], [0, 3, 2]]), 'anchor')
    verify_witness(I, 5, 0, -1, 2, -1, 1)
    try:
        verify_witness(I, 5, 0, -1, 3, -1, 1)
    except RuntimeError:
        pass
    else:
        raise RuntimeError('tampered witness accepted')

    for k in range(2, 7):
        seen = set()
        minimum = Fraction(1)
        for I in residual(k):
            require(I not in seen, ('duplicate', I))
            seen.add(I)
            E, lo, W = counts(I)
            hi = lo+len(W[0])-1
            candidates = []
            for i, row in enumerate(W):
                n = 0
                for g, v in enumerate(row[:-1], lo):
                    n += v
                    candidates.append((min(n, E-n), i, g, n))
            d, i, g, n = max(candidates)
            verify_witness(I, E, i, g, n, lo, hi)
            minimum = min(minimum, Fraction(d, E))
            for i, (a, b) in enumerate(I):
                for g in range(a, b+1):
                    r = sum(not c <= g <= d for c, d in I)
                    require(W[i][g-lo] <= W[i][-lo] <= (r+1)*W[i][g-lo],
                            ('occupancy inequality fails', I, i, g))
        require(len(seen) == EXPECTED[k], ('coverage count', k, len(seen)))
        require(minimum == MINIMA[k], ('minimum', k, minimum))
        print(f'k={k}: {len(seen)} cases; min chain-pair balance={minimum}')
    print('PASS: 204 residuals, exact witness replay and tamper rejection')


if __name__ == '__main__':
    main()
