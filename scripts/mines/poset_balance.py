"""Posets whose best balance is exactly 1/3, with width and height.

Balance in the search uses the maximal-element extension count. The checker
recounts every witness with the minimal-element recurrence. Width-2 posets are
already settled by Linial (1984); this is a census table, not a new bound.
"""
from collections import Counter
from fractions import Fraction

from probes.core import fraction_text, require
from probes.posets import (KNOWN_UNLABELLED, _count_by_minimal, best_pair, census)

MINE = {
    "id": "poset_balance",
    "problem_id": "M079",
    "title": "Posets attaining balance exactly 1/3",
    "engines": ["poset_census"],
    "frontier": ("The conjecture is verified through 11 elements (Peczarski) and proved for width 2 "
                 "(Linial 1984). The table names the extremal posets inside this census."),
    "levels": {"smoke": {"max_n": 6}},
}


def scope(params):
    return (f"Every non-chain poset on at most {params['max_n']} elements has best balance at least 1/3, "
            "and the width-height profile of those whose best balance is exactly 1/3 is the recorded multiset.")


def width(below):
    n = len(below)
    for size in range(n, 0, -1):
        # An antichain is a subset with no strict relation. n <= 6, so subsets are immediate.
        for mask in range(1 << n):
            if bin(mask).count("1") != size:
                continue
            members = [v for v in range(n) if mask >> v & 1]
            if all(not below[b] >> a & 1 for i, a in enumerate(members) for b in members[i + 1:]):
                return size
    return 1


def height(below):
    n = len(below)
    order = sorted(range(n), key=lambda v: bin(below[v]).count("1"))
    chain = [1] * n
    for v in order:
        mask = below[v]
        while mask:
            bit = mask & -mask
            chain[v] = max(chain[v], chain[bit.bit_length() - 1] + 1)
            mask -= bit
    return max(chain) if n else 0


def _profile(max_n, balance_of):
    """balance_of(below) -> Fraction or None for a chain."""
    counts = Counter()
    least = None
    one_third = 0
    for n in range(1, max_n + 1):
        posets = census(n)
        require(len(posets) == KNOWN_UNLABELLED[n], f"n={n}: poset count is not OEIS A000112")
        for below in posets:
            bal = balance_of(below)
            if bal is None:
                continue
            least = bal if least is None or bal < least else least
            if bal == Fraction(1, 3):
                one_third += 1
                counts[(width(below), height(below))] += 1
    return {
        "max_n": max_n,
        "least_balance": fraction_text(least),
        "one_third_posets": one_third,
        "width_height": {f"{w}x{h}": counts[(w, h)] for w, h in sorted(counts)},
    }


def _from_maximal(below):
    found = best_pair(below)
    if found is None:
        return None
    bal, _x, _y, _a, _e = found
    return bal


def _from_minimal(below):
    n = len(below)
    comparable = sum(1 for y in range(n) for x in range(y) if below[y] >> x & 1 or below[x] >> y & 1)
    if comparable == n * (n - 1) // 2:
        return None
    total = _count_by_minimal(below)
    best = None
    for x in range(n):
        for y in range(x + 1, n):
            if below[y] >> x & 1 or below[x] >> y & 1:
                continue
            closed = list(below)
            closed[y] |= 1 << x | closed[x]
            for _ in range(n):
                nxt = []
                for mask in closed:
                    for u in range(n):
                        if mask >> u & 1:
                            mask |= closed[u]
                    nxt.append(mask)
                closed = nxt
            a = _count_by_minimal(tuple(closed))
            bal = min(Fraction(a, total), 1 - Fraction(a, total))
            if best is None or bal > best:
                best = bal
    return best


def search(params):
    summary = _profile(params["max_n"], _from_maximal)
    return {"holds": summary["least_balance"] == "1/3" or Fraction(summary["least_balance"]) >= Fraction(1, 3),
            "summary": summary, "certificate": summary}


def check(params, result):
    summary = _profile(params["max_n"], _from_minimal)
    require(Fraction(summary["least_balance"]) >= Fraction(1, 3), "a poset in the census falls below 1/3")
    require(result["summary"] == summary, "balance profile does not match the minimal-element recount")
    require(result["certificate"] == summary, "certificate is not the checked profile")
