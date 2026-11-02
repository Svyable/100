#!/usr/bin/env python3
"""Exact one-step extensions of a pinned ten-deletion M076 witness.

A restricted computational theorem candidate, not a global sunflower bound.
The C++ literal checker independently reconstructs the family and scans every
old-deletion/new-insertion pair; it does not call this Python enumerator.
"""
from __future__ import annotations

import argparse
import json
import os
from itertools import combinations
from pathlib import Path
import subprocess
import tempfile

from scripts.m076_f43_stability import base_family, mask, sunflower, verify_family

TEN_DROP = frozenset((0, 2, 3, 5, 6, 8, 18, 24, 25, 26))
TEN_INSERT = ((0, 1, 3, 18), (0, 2, 3, 18), (1, 2, 3, 18),
              (3, 6, 7, 18), (5, 6, 7, 18))
# The complete answer over the 23-point representative universe.
EXPECTED = tuple(sorted(
    [(j, (3, 6, 8, x)) for j in (19, 22) for x in range(18, 23)] +
    [(j, (3, 7, 8, x)) for j in (20, 23) for x in range(18, 23)] +
    [(19, (5, 6, 8, 18)), (20, (5, 7, 8, 18))]
))


def baseline():
    family = base_family()
    kept = [(i, a) for i, a in enumerate(family) if i not in TEN_DROP]
    inserted = tuple(mask(points) for points in TEN_INSERT)
    return family, kept, inserted


def pair_intersection_scan():
    """Each new sunflower must involve the candidate and an old pair.

    For each candidate, intersect the possible extra-deletion endpoints of
    every forbidden pair. Empty intersection means no one-step extension.
    """
    family, kept, inserted = baseline()
    present = tuple(a for _, a in kept) + inserted
    old_count = len(kept)
    assert old_count == 44 and verify_family(present)
    forbidden = set(family) | set(inserted)
    edges = [(i, j, a & b) for i, a in enumerate(present)
             for j, b in enumerate(present[:i])]
    answer = []
    candidates = 0
    for points in combinations(range(23), 4):
        c = mask(points)
        if c in forbidden:
            continue
        candidates += 1
        removable = set(range(old_count))
        for i, j, core in edges:
            if (present[i] & c) == core == (present[j] & c):
                removable.intersection_update(
                    k for k in (i, j) if k < old_count)
                if not removable:
                    break
        for k in sorted(removable):
            answer.append((kept[k][0], points))
    assert candidates == 8796
    return tuple(sorted(answer)), candidates


def literal_verify(drop, candidate):
    """Separate frozenset representation and all-triples replay."""
    family, _, _ = baseline()
    if drop in TEN_DROP or not 0 <= drop < 54:
        return False
    if len(set(candidate)) != 4:
        return False
    old = [frozenset(i for i in range(18) if a & (1 << i))
           for j, a in enumerate(family) if j not in TEN_DROP | {drop}]
    inserted = [frozenset(p) for p in TEN_INSERT]
    new = frozenset(candidate)
    if new in set(old) | set(inserted) | {
        frozenset(i for i in range(18) if a & (1 << i)) for a in family
    }:
        return False
    all_sets = old + inserted + [new]
    return (len(all_sets) == len(set(all_sets)) and
            all(not (a & b == a & c == b & c)
                for a, b, c in combinations(all_sets, 3)))


def independent_cpp_scan():
    """Compile a standalone direct enumerator, independently built from blocks."""
    src = Path(__file__).with_name('m076_f43_eleven_direct.cpp')
    with tempfile.TemporaryDirectory(prefix='m076-eleven-') as tmp:
        binary = Path(tmp) / 'direct'
        subprocess.run([os.environ.get('CXX', 'c++'), '-std=c++17', '-O2',
                        '-Wall', '-Wextra', str(src), '-o', str(binary)],
                       check=True, capture_output=True, text=True)
        output = subprocess.run([str(binary)], check=True, capture_output=True,
                                text=True).stdout.splitlines()
    assert output[0] == 'tested 387024 solutions 22', output[:1]
    result = tuple(sorted((int(line.split()[0]),
                           tuple(map(int, line.split()[1:])))
                          for line in output[1:]))
    return result


def check():
    first, candidates = pair_intersection_scan()
    if first != EXPECTED:
        raise AssertionError(('Python classification mismatch', first))
    second = independent_cpp_scan()
    if second != first:
        raise AssertionError(('independent C++ mismatch', second))
    if not all(literal_verify(j, c) for j, c in first):
        raise AssertionError('literal witness replay failed')
    if literal_verify(21, (3, 6, 8, 18)):
        raise AssertionError('forged extra deletion accepted')
    if not literal_verify(19, (3, 6, 8, 1000)):
        raise AssertionError('arbitrary ambient outsider not supported')
    if literal_verify(19, (3, 6, 8, 3)):
        raise AssertionError('repeated point accepted')
    return {'candidates_per_old_deletion': candidates,
            'retained_old_choices': 44,
            'candidate_deletion_pairs_tested': 44 * candidates,
            'admissible_labeled_pairs_on_23_points': len(first),
            'outside_representatives': [18, 19, 20, 21, 22],
            'witness_drop': sorted(TEN_DROP | {19}),
            'witness_insert': [list(p) for p in TEN_INSERT] +
                              [[3, 6, 8, 18]],
            'family_size': 49,
            'triples_checked_per_witness': 18424,
            'independent_cpp_agrees': True}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    p.add_argument('--json', action='store_true')
    args = p.parse_args()
    result = check()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)


if __name__ == '__main__':
    main()
