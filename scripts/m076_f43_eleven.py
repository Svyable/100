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


def fixed_drop_candidates():
    """All individually admissible new sets after the explicit eleven deletions."""
    family = base_family()
    dropped = TEN_DROP | {19}
    kept = [a for j, a in enumerate(family) if j not in dropped]
    edges = [(a, b, a & b) for i, a in enumerate(kept)
             for b in kept[:i]]
    return tuple(p for p in combinations(range(23), 4)
                 if mask(p) not in family and
                 all((a & mask(p)) != core or (b & mask(p)) != core
                     for a, b, core in edges))


def fixed_drop_structural_bound(candidates):
    """Seven outsider supports, one inside, and a seven-insertion cap.

    Every outsider triple is contained in a retained old set, preventing
    two distinct completions of that triple. The unique inside candidate
    clashes with five of the seven outsider supports.
    """
    family = base_family()
    old = [a for j, a in enumerate(family) if j not in TEN_DROP | {19}]
    inside = tuple(p for p in candidates if all(x < 18 for x in p))
    triples = tuple(sorted({tuple(x for x in p if x < 18)
                            for p in candidates if sum(x >= 18 for x in p) == 1}))
    if inside != ((0, 1, 2, 3),) or len(triples) != 7:
        raise AssertionError((inside, triples))
    if set(candidates) != set(inside) | {
        t + (x,) for t in triples for x in range(18, 23)
    }:
        raise AssertionError('candidate support catalog is incomplete')
    old_supersets = {t: [j for j, a in enumerate(family)
                         if j not in TEN_DROP | {19} and a & mask(t) == mask(t)]
                     for t in triples}
    expected_supersets = {
        (0, 1, 3): [1], (0, 2, 3): [4], (1, 2, 3): [7],
        (3, 6, 7): [21], (3, 6, 8): [22],
        (5, 6, 7): [21], (5, 6, 8): [22],
    }
    if old_supersets != expected_supersets:
        raise AssertionError(('retained old supersets changed', old_supersets))
    conflicts = tuple(t for t in triples if any(
        sunflower(mask(inside[0]), mask(t + (18,)), a) for a in old))
    if conflicts != ((0, 1, 3), (0, 2, 3), (1, 2, 3),
                     (5, 6, 7), (5, 6, 8)):
        raise AssertionError(('inside conflict pattern changed', conflicts))
    return {'inside': inside[0], 'outside_triples': triples,
            'old_supersets': old_supersets, 'inside_conflicts': conflicts,
            'max_simultaneous_insertions': max(len(triples),
                                                1 + len(triples) - len(conflicts))}


def literal_verify_seven():
    """All-triples check using sets, independently of integer-mask sunflowers."""
    family = base_family()
    dropped = TEN_DROP | {19}
    old = [frozenset(i for i in range(18) if a & (1 << i))
           for j, a in enumerate(family) if j not in dropped]
    added = [frozenset(p) for p in TEN_INSERT]
    added.extend((frozenset((3, 6, 8, 18)),
                  frozenset((5, 6, 8, 18))))
    all_sets = old + added
    return (len(all_sets) == 50 and len(set(all_sets)) == 50 and
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
    assert output[23] == 'allowed 36', output[23:24]
    result = tuple(sorted((int(line.split()[0]),
                           tuple(map(int, line.split()[1:])))
                          for line in output[1:23]))
    allowed = tuple(sorted(tuple(map(int, line.split()[1:]))
                           for line in output[24:]))
    return result, allowed


def check():
    first, candidates = pair_intersection_scan()
    if first != EXPECTED:
        raise AssertionError(('Python classification mismatch', first))
    second, allowed_cpp = independent_cpp_scan()
    if second != first:
        raise AssertionError(('independent C++ mismatch', second))
    allowed = fixed_drop_candidates()
    if allowed != allowed_cpp or len(allowed) != 36:
        raise AssertionError('independent fixed-deletion candidate mismatch')
    structure = fixed_drop_structural_bound(allowed)
    if structure['max_simultaneous_insertions'] != 7:
        raise AssertionError('fixed-deletion structural upper bound failed')
    if not all(literal_verify(j, c) for j, c in first):
        raise AssertionError('literal witness replay failed')
    if literal_verify(21, (3, 6, 8, 18)):
        raise AssertionError('forged extra deletion accepted')
    if not literal_verify(19, (3, 6, 8, 1000)):
        raise AssertionError('arbitrary ambient outsider not supported')
    if literal_verify(19, (3, 6, 8, 3)):
        raise AssertionError('repeated point accepted')
    seven = [a for j, a in enumerate(base_family())
             if j not in TEN_DROP | {19}]
    seven += [mask(p) for p in TEN_INSERT]
    seven += [mask((3, 6, 8, 18)), mask((5, 6, 8, 18))]
    if len(seven) != 50 or not verify_family(seven) or not literal_verify_seven():
        raise AssertionError('seven-insertion witness failed')
    return {'candidates_per_old_deletion': candidates,
            'retained_old_choices': 44,
            'candidate_deletion_pairs_tested': 44 * candidates,
            'admissible_labeled_pairs_on_23_points': len(first),
            'outside_representatives': [18, 19, 20, 21, 22],
            'witness_drop': sorted(TEN_DROP | {19}),
            'witness_insert': [list(p) for p in TEN_INSERT] +
                              [[3, 6, 8, 18], [5, 6, 8, 18]],
            'family_size': 50,
            'triples_checked_per_witness': 19600,
            'individually_allowed_candidates': len(allowed),
            'outside_support_triples': [list(t) for t in structure['outside_triples']],
            'inside_conflicts': [list(t) for t in structure['inside_conflicts']],
            'fixed_drop_sharp_max_insertions': 7,
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
