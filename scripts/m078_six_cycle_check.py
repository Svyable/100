#!/usr/bin/env python3
"""X-M078-SIX-CYCLE-TRADE #385: standalone *exact certificate checker*.

Input: a compact JSON certificate with one dual vector per orbit representative.
Output: a single JSON summary, or nonzero exit and descriptive failure.

Uses only Python's standard library; independently reconstructs graph paths by
BFS, symmetries by leaf permutations, and checks EVERY rational identity.
The certificate generator (SymPy) and the solver (integer elimination) are
separate author-controlled methods, NOT independent human mathematical review.
"""
import argparse
from collections import deque
from fractions import Fraction
from itertools import combinations, permutations, product
import json
import sys

N = 6
PAIRS = list(combinations(range(N), 2))
INDEX = {p: k for k, p in enumerate(PAIRS)}
STAR_EDGES = [(0, 7), (1, 7), (2, 8), (3, 8),
              (4, 9), (5, 9), (6, 7), (6, 8), (6, 9)]


def validate(cond, message):
    if not cond:
        raise ValueError(message)


def canonical_path(left, inner1, inner2, right):
    a = (tuple(sorted(left)), int(inner1), int(inner2), tuple(sorted(right)))
    return min(a, (a[3], a[2], a[1], a[0]))


def enumerate_paths():
    # Distinct construction from generator: choose endpoint pair and
    # ordered middle singletons, quotient by path reversal.
    out = set()
    leaves = set(range(N))
    for left in combinations(range(N), 2):
        for c in leaves - set(left):
            for d in leaves - set(left) - {c}:
                out.add(canonical_path(left, c, d, leaves - set(left) - {c, d}))
    validate(len(out) == 90, 'path allocation census is not 90')
    return out


def enumerate_cycles():
    # Fix first vertex 0; break reversal by second vertex < last.
    out = set()
    for tail in permutations(range(1, N)):
        if tail[0] > tail[-1]:
            continue
        vertices = (0,) + tail
        edges = frozenset(INDEX[tuple(sorted((vertices[i], vertices[(i + 1) % N])))]
                          for i in range(N))
        out.add(edges)
    validate(len(out) == 60, 'undirected Hamilton cycle census is not 60')
    return out


def incidence_rows(edges):
    validate(len(edges) == 9, 'binary six-leaf tree needs 9 edges')
    neighbor = [[] for _ in range(10)]
    for k, (a, b) in enumerate(edges):
        neighbor[a].append((b, k))
        neighbor[b].append((a, k))
    forms = []
    for source, dest in PAIRS:
        todo = deque([(source, -1, frozenset())])
        found = None
        while todo:
            v, parent, used = todo.popleft()
            if v == dest:
                found = used
                break
            for w, i in neighbor[v]:
                if w != parent:
                    todo.append((w, v, used | {i}))
        validate(found is not None, 'not a tree')
        forms.append(tuple(int(i in found) for i in range(9)))
    return forms


def path_edges(key):
    l, c, d, r = key
    return [(l[0], 6), (l[1], 6), (c, 7), (d, 8),
            (r[0], 9), (r[1], 9), (6, 7), (7, 8), (8, 9)]


def equations(star, path, reds, blues):
    zeros = (0,) * 9
    changed = set(reds) | set(blues)
    rows = [star[i] + tuple(-v for v in path[i])
            for i in range(15) if i not in changed]
    for F, is_path in ((star, False), (path, True)):
        for color in (reds, blues):
            for i in color[1:]:
                diff = tuple(a - b for a, b in zip(F[color[0]], F[i]))
                rows.append((zeros + diff) if is_path else (diff + zeros))
    rows.append(star[reds[0]] + tuple(-v for v in path[blues[0]]))
    rows.append(star[blues[0]] + tuple(-v for v in path[reds[0]]))
    validate(len(rows) == 19, 'unexpected number of constraints')
    return rows


def check_coloring(reds, blues, cycles):
    validate(len(reds) == len(blues) == 3, 'each color should have 3 edges')
    validate(len(set(reds) | set(blues)) == 6, 'repeat edge in cycle colors')
    cyc = frozenset(reds) | frozenset(blues)
    validate(cyc in cycles, 'colored edges not a Hamilton six-cycle')
    for color in (reds, blues):
        counts = [0] * N
        for i in color:
            validate(0 <= i < 15, 'invalid pair index')
            for v in PAIRS[i]:
                counts[v] += 1
        validate(counts == [1] * N, 'color class is not a perfect matching')
    return cyc


def automorphisms():
    out = set()
    for block_perm in permutations(range(3)):
        for switches in product((0, 1), repeat=3):
            p = tuple(2 * block_perm[v // 2] + ((v % 2) ^ switches[v // 2])
                      for v in range(N))
            out.add(p)
    validate(len(out) == 48, 'star automorphism group has wrong size')
    return out


def action(p, path, cycle):
    l, c, d, r = path
    dest_path = canonical_path((p[i] for i in l), p[c], p[d], (p[i] for i in r))
    dest_cycle = frozenset(INDEX[tuple(sorted((p[a], p[b])))]
                           for edge in cycle for a, b in [PAIRS[edge]])
    return (dest_path, dest_cycle)


def verify_object(cert):
    validate(cert.get('scope') == 'X-M078-SIX-CYCLE-TRADE-v1', 'wrong scope')
    validate(cert.get('target_coordinate') == 16, 'wrong target coordinate')
    validate(cert.get('total_systems') == 5400, 'wrong system count')
    validate(cert.get('star_automorphisms') == 48, 'wrong symmetry count')
    rows = cert.get('representatives')
    validate(isinstance(rows, list) and len(rows) == 142, 'wrong representative count')
    paths, cycles = enumerate_paths(), enumerate_cycles()
    group, star = automorphisms(), incidence_rows(STAR_EDGES)
    covered = set()
    nterms = 0
    for k, rec in enumerate(rows):
        raw = rec['path_key']
        path = canonical_path(raw[0], raw[1], raw[2], raw[3])
        validate(path in paths and tuple(raw[0]) == path[0] and raw[1] == path[1]
                 and raw[2] == path[2] and tuple(raw[3]) == path[3],
                 f'invalid path representative #{k}')
        reds, blues = tuple(rec['red']), tuple(rec['blue'])
        cycle = check_coloring(reds, blues, cycles)
        orbit = {action(p, path, cycle) for p in group}
        validate(len(orbit) == rec['orbit'], f'orbit size mismatch #{k}')
        validate(not orbit & covered, f'redundant orbit #{k}')
        covered.update(orbit)
        E = equations(star, incidence_rows(path_edges(path)), reds, blues)
        vector = [Fraction(0)] * 18
        validate(rec['terms'] and len(rec['terms']) <= 19, f'wrong terms #{k}')
        seen_idx = set()
        for idx, a, b in rec['terms']:
            validate(idx not in seen_idx and 0 <= idx < 19 and b > 0 and a != 0,
                     f'invalid rational coefficient #{k}')
            seen_idx.add(idx)
            coeff = Fraction(a, b)
            nterms += 1
            for j in range(18):
                vector[j] += coeff * E[idx][j]
        target = [Fraction(int(j == 16)) for j in range(18)]
        validate(vector == target, f'rational identity fails for rep #{k}')
    validate(len(covered) == len(paths) * len(cycles) == 5400,
             f'incomplete orbit coverage: {len(covered)} of 5400')
    return {'target':'path_middle_edge_is_zero', 'exact_certs':len(rows),
            'linear_combination_terms':nterms, 'star_automorphisms':len(group),
            'path_allocations':len(paths),'hamilton_cycles':len(cycles),
            'systems_proved':len(covered),'certificate_verified':True}


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('certificate', help='path to JSON proof packet')
    args = a.parse_args()
    try:
        with open(args.certificate, 'r', encoding='utf-8') as f:
            cert = json.load(f)
        summary = verify_object(cert)
    except (ValueError, TypeError, KeyError, OSError) as e:
        print('FAIL:', e, file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
