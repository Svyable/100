#!/usr/bin/env python3
"""Independent literal-poset checks and exact eight-gap census for M079.

This wrapper uses the existing C++ sequential and factorial-block algorithms
for the complete finite core, but constructs a separate predecessor-matrix
poset and counts its order ideals for adversarial examples. Neither replay is
an independent specialist mathematical review.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import json
import math
from pathlib import Path
from random import Random
import re
import subprocess
import tempfile

from m079_chain7_local import compile_cpp

K = 7
LIMIT = 8
EXPECTED_CASES = 12_610_738
# Filled only after the exhaustive census and literal witness replay.
EXPECTED_MINIMUM = (44873, 107157)
EXPECTED_DIGEST = "ddf479309a0661ab"
EXPECTED_WITNESS = "[-5,0][-2,0][-2,2][-1,0][0,1][0,2][0,5]"
SUMMARY = re.compile(
    r"cases=(\d+) dual=(\d+) negative=(\d+) minimum=(\d+)/(\d+) "
    r"multiplicity=(\d+) max_length=(\d+) intervals=(\d+) fnv64=([0-9a-f]{16}) witness=(.*)"
)


def valid(intervals, limit=LIMIT):
    return (len(intervals) == K
            and all(a <= 0 <= b and 2 <= b-a+1 <= limit for a,b in intervals)
            and max(a for a,b in intervals) == 0
            and min(b for a,b in intervals) == 0)


def canonical_count(limit=LIMIT):
    n = sum(range(2, limit+1))
    t = limit-1
    return math.comb(n+K-1,K) - 2*math.comb(n-t+K-1,K) + math.comb(n-2*t+K-1,K)


def literal_balance(intervals):
    """Independent full-poset predecessor masks, no gap-state recurrence."""
    assert valid(intervals)
    lo = min(a for a,b in intervals)
    hi = max(b for a,b in intervals)
    m = hi-lo
    n = m+K
    full = (1<<n)-1
    pred = [(1<<j)-1 for j in range(m)] + [0]*K
    for j in range(m):
        for i,(a,b) in enumerate(intervals):
            if b-lo <= j:
                pred[j] |= 1<<(m+i)
    for i,(a,b) in enumerate(intervals):
        pred[m+i] = (1<<(a-lo))-1

    @lru_cache(None)
    def suffix(mask):
        if mask == full:
            return 1
        ans = 0
        remain = full ^ mask
        while remain:
            bit = remain & -remain
            v = bit.bit_length()-1
            if not (pred[v] & ~mask):
                ans += suffix(mask|bit)
            remain ^= bit
        return ans

    levels = [[0]] + [[] for _ in range(n)]
    forward = {0:1}
    before = [[0]*n for _ in range(n)]
    E = suffix(0)
    for depth in range(n):
        for mask in levels[depth]:
            f = forward[mask]
            remain = full ^ mask
            available = remain
            while available:
                bit = available & -available
                v = bit.bit_length()-1
                if not (pred[v] & ~mask):
                    nextmask = mask|bit
                    if nextmask not in forward:
                        forward[nextmask] = 0
                        levels[depth+1].append(nextmask)
                    forward[nextmask] += f
                    weight = f*suffix(nextmask)
                    rest = remain ^ bit
                    while rest:
                        wbit = rest & -rest
                        w = wbit.bit_length()-1
                        before[v][w] += weight
                        rest ^= wbit
                available ^= bit
    assert forward[full] == E
    assert all(before[u][v]+before[v][u] == E for u in range(n) for v in range(u+1,n))
    best = max(min(before[u][v],before[v][u]) for u in range(n) for v in range(u+1,n))
    pair = [before[m+i][m+j] for i in range(K) for j in range(i+1,K)]
    gap = []
    for i in range(K):
        cumulative = 0
        row = []
        for j in range(m):
            upto = before[m+i][j]
            row.append(upto-cumulative)
            cumulative = upto
        row.append(E-cumulative)
        gap.append(row)
    return E,best,pair,gap


def cpp_instance(binary, intervals, mutation=False):
    arg = ",".join(f"{a}:{b}" for a,b in intervals)
    cmd = [str(binary), "--instance", arg]
    if mutation:
        cmd.append("--mutate-tie")
    p = subprocess.run(cmd, text=True, capture_output=True)
    if mutation:
        assert p.returncode == 3 and "mismatch" in p.stderr.lower()
        return None
    assert p.returncode == 0, (p.stderr,p.stdout)
    lines = p.stdout.splitlines()
    mat = re.fullmatch(r"E=(\d+) best=(\d+) delta=(\d+)/(\d+)",lines[0])
    assert mat
    E,best,delta,E2 = map(int,mat.groups())
    assert (E,best)==(E2,delta)
    pairs = [int(v) for v in lines[1].removeprefix("pairs=").split(",") if v]
    gaps = [[int(v) for v in row.split("=")[1].split(",") if v]
            for row in lines[2:]]
    return E,best,pairs,gaps


def replay_literal(binary, intervals):
    literal = literal_balance(intervals)
    cpp = cpp_instance(binary, intervals)
    assert literal == cpp, (intervals,literal,cpp)
    return literal


def sample_cases():
    choices = [(a,a+L-1) for L in range(2,LIMIT+1) for a in range(1-L,1)]
    rng = Random(79008)
    cases = []
    seen = set()
    while len(cases)<32:
        iv = tuple(sorted(rng.choices(choices,k=K)))
        if iv not in seen and valid(iv):
            seen.add(iv)
            cases.append(iv)
    return cases


def smoke(binary):
    assert canonical_count(6) == 436680
    assert canonical_count(7) == 2612268
    assert canonical_count(8) == EXPECTED_CASES
    # The previous six-gap sharp example remains in the larger class.
    old = ((-5,0),(-2,0),(-2,2),(-1,0),(0,1),(0,2),(0,5))
    assert replay_literal(binary,old)[:2] == (107157,44873)
    assert not valid(((-1,1),)*7)
    assert not valid(((0,0),)+((-1,0),)*6)
    assert not valid(((-7,1),)+((0,1),)*6)
    cpp_instance(binary,old,mutation=True)
    for iv in sample_cases():
        replay_literal(binary,iv)
    return {"literal_controls":33,"mutation_rejected":True,"count_formula":EXPECTED_CASES}


def check():
    with tempfile.TemporaryDirectory(prefix="m079_eightgap_") as d:
        binary = compile_cpp(Path(d))
        controls = smoke(binary)
        p = subprocess.run([str(binary),"--max-length","8","--dual"],
                           text=True,capture_output=True,check=True)
        mat = SUMMARY.search(p.stderr)
        assert mat, p.stderr
        cases,dual,negative,num,den,multiplicity,limit,options,digest,witness = mat.groups()
        assert (int(cases),int(dual),int(negative),int(limit),int(options)) == (EXPECTED_CASES,EXPECTED_CASES,0,8,35)
        assert EXPECTED_MINIMUM is not None and (int(num),int(den)) == EXPECTED_MINIMUM
        assert EXPECTED_DIGEST is not None and digest == EXPECTED_DIGEST
        assert EXPECTED_WITNESS is not None and witness == EXPECTED_WITNESS
        controls.update({"cases":int(cases),"dual":int(dual),"minimum":f"{num}/{den}",
                         "multiplicity":int(multiplicity),"fnv64":digest,"witness":witness})
        return controls


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--check",action="store_true")
    group.add_argument("--smoke",action="store_true")
    args=p.parse_args()
    if args.smoke:
        with tempfile.TemporaryDirectory(prefix="m079_eightgap_") as d:
            binary=compile_cpp(Path(d))
            print(json.dumps(smoke(binary),sort_keys=True))
    else:
        print(json.dumps(check(),sort_keys=True))
