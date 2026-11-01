#!/usr/bin/env python3
"""M079 chain-plus-three sharp restricted balance: exact all-orders reduction.

The finite core is checked twice: a closed insertion-gap count and an
independent order-ideal state recurrence. No external dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction

BOUND = Fraction(11, 28)
MAX_RESIDUAL_LENGTH = 13
EXPECTED_CASES = 67392
EXPECTED_SHARP = 12


def intervals(max_length=MAX_RESIDUAL_LENGTH, min_length=2):
    """All intervals containing gap 0 with bounded length."""
    for length in range(min_length, max_length + 1):
        for left in range(1 - length, 1):
            yield (left, left + length - 1)


def in_gap(interval, gap):
    return interval[0] <= gap <= interval[1]


def valid_triple(triple, min_length=2):
    """Antichain outsiders, width exactly three, nontrivial chain overlap."""
    if len(triple) != 3:
        return False
    if any(b - a + 1 < min_length or a > b for a, b in triple):
        return False
    # Three pairwise-overlapping intervals have a common gap (Helly).
    # A second common gap would give a chain vertex incomparable to all 3.
    return max(a for a, _ in triple) == min(b for _, b in triple)


def formula(triple):
    """Return exact total extensions and pair-before numerators.

    Outsider pairs are keyed (i,j), i<j. Outsider-chain pairs are
    keyed (i,3+k), where chain c_k separates gaps k-1 and k.
    """
    if not valid_triple(triple):
        raise ValueError("outside width-three antichain-three scope")
    lo = min(a for a, _ in triple)
    hi = max(b for _, b in triple)
    S = [set(range(a, b + 1)) for a, b in triple]
    L = [len(s) for s in S]
    r = {(i, j): len(S[i] & S[j]) for i in range(3) for j in range(i + 1, 3)}
    t = len(S[0] & S[1] & S[2])
    E = L[0]*L[1]*L[2] + r[0,1]*L[2] + r[0,2]*L[1] + r[1,2]*L[0] + 2*t
    counts = {}
    for i in range(3):
        for j in range(i+1, 3):
            k = 3-i-j
            counts[i,j] = (
                sum(L[k] + (g in S[k]) + (h in S[k])
                    for g in S[i] for h in S[j] if g < h)
                + sum(L[k] + 2*(g in S[k]) for g in S[i] & S[j])
            )
    for i in range(3):
        j, k = [q for q in range(3) if q != i]
        base = L[j]*L[k] + len(S[j] & S[k])
        prefix = 0
        for gap in range(lo, hi):
            if gap in S[i]:
                prefix += base + L[k]*(gap in S[j]) + L[j]*(gap in S[k]) + 2*(gap in S[j] and gap in S[k])
            counts[i, 3+gap+1-lo] = prefix
    return E, counts


def independent_dp(triple):
    """Count actual extension paths, not insertion multiplicity formulas.

    The state (k,mask) is an order ideal: k chain vertices and mask of
    outsiders already placed. F/B count its prefixes/suffixes. Every
    legal transition placing outsider i contributes F*B to each pair
    that i precedes. This is an independent full-census checker.
    """
    if not valid_triple(triple):
        raise ValueError("outside scope")
    lo = min(a for a, _ in triple)
    hi = max(b for _, b in triple)
    shifted = [(a-lo,b-lo) for a,b in triple]
    m = hi-lo
    F = [[0]*8 for _ in range(m+1)]
    F[0][0] = 1
    def moves(k, mask):
        if k < m and all(mask & (1<<i) or b > k for i,(_,b) in enumerate(shifted)):
            yield k+1, mask, None
        for i,(a,b) in enumerate(shifted):
            if not mask & (1<<i) and a <= k <= b:
                yield k, mask | (1<<i), i
    for k in range(m+1):
        for mask in range(8):
            for nk,nmask,_ in moves(k,mask):
                F[nk][nmask] += F[k][mask]
    B = [[0]*8 for _ in range(m+1)]
    B[m][7] = 1
    for k in range(m,-1,-1):
        for mask in range(7,-1,-1):
            if k == m and mask == 7:
                continue
            B[k][mask] = sum(B[nk][nmask] for nk,nmask,_ in moves(k,mask))
    E = F[m][7]
    assert E == B[0][0] and E > 0
    counts = {(i,j):0 for i in range(3) for j in range(i+1,3)}
    counts.update({(i,3+t):0 for i in range(3) for t in range(1,m+1)})
    for k in range(m+1):
        for mask in range(8):
            for nk,nmask,added in moves(k,mask):
                if added is None:
                    continue
                ways = F[k][mask]*B[nk][nmask]
                i = added
                for j in range(i+1,3):
                    if not mask & (1<<j):
                        counts[i,j] += ways
                for t in range(k+1,m+1):
                    counts[i,3+t] += ways
    return E, counts


def best_balance(total, counts):
    return max(min(v,total-v) for v in counts.values())


def census(max_length=MAX_RESIDUAL_LENGTH, verify_dp=True):
    options = tuple(intervals(max_length))
    n = sharp = 0
    min_balance = Fraction(1,2)
    sharp_example = None
    digest = hashlib.sha256()
    for a in options:
        for b in options:
            for c in options:
                triple = (a,b,c)
                if max(a[0],b[0],c[0]) != min(a[1],b[1],c[1]):
                    continue
                # All intervals contain zero, so the unique common gap is zero.
                n += 1
                E, pairs = formula(triple)
                best = best_balance(E,pairs)
                if verify_dp:
                    E2, pairs2 = independent_dp(triple)
                    if (E,pairs) != (E2,pairs2):
                        raise AssertionError(("independent mismatch",triple,E,E2,pairs,pairs2))
                if 28*best < 11*E:
                    raise AssertionError(("bound falsified",triple,E,best))
                value = Fraction(best,E)
                if value < min_balance:
                    min_balance = value
                if 28*best == 11*E:
                    sharp += 1
                    if sharp_example is None:
                        sharp_example = triple
                digest.update(f"{triple}:{E}:{best}\n".encode())
    return {"max_length":max_length,"cases":n,"minimum":str(min_balance),
            "sharp_cases":sharp,"first_sharp":sharp_example,
            "sha256":digest.hexdigest(),"independent_dp":verify_dp}


def verify_large_interval_lemma(limit=200):
    # For two other intervals of lengths M,N with nonempty intersection,
    # B=MN+r>=MN+1, max atom <= B+M+N+2 <= 3B.
    for M in range(1,limit+1):
        for N in range(1,limit+1):
            assert M+N+2 <= 2*(M*N+1)
    assert Fraction(3,14) == 1-2*BOUND
    assert Fraction(3,14) < 1-BOUND


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--json",action="store_true")
    p.add_argument("--no-independent",action="store_true")
    args=p.parse_args()
    verify_large_interval_lemma()
    result=census(verify_dp=not args.no_independent)
    if args.check:
        assert result["cases"] == EXPECTED_CASES, result
        assert result["sharp_cases"] == EXPECTED_SHARP, result
        assert result["minimum"] == "11/28", result
        # The seven-vertex sharp witness is not chain-plus-two.
        witness=((-3,0),(-1,0),(0,1))
        E, pairs=formula(witness)
        assert E==28 and best_balance(E,pairs)==11
        assert independent_dp(witness)==(E,pairs)
        assert all(b-a+1>=2 for a,b in witness)
    print(json.dumps(result,sort_keys=True) if args.json else
          f"M079 chain3: {result['cases']} exact cases; minimum {result['minimum']}; "
          f"{result['sharp_cases']} sharp; independent DP {result['independent_dp']}; "
          f"SHA256 {result['sha256']}")

if __name__=="__main__":
    main()
