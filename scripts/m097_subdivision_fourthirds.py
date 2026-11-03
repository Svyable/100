#!/usr/bin/env python3
"""Exact, independent finite falsifier for subdivided-core four-thirds theorem.

The all-orders proof relies on the established Edmonds--Johnson T-join
polyhedron and the M097 parity formula; finite tests are not a proof.
"""
import argparse
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
import json
import random


def component_count(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    seen, count = set(), 0
    for v in range(n):
        if v not in seen:
            count += 1
            stack = [v]
            while stack:
                u = stack.pop()
                if u in seen:
                    continue
                seen.add(u)
                stack.extend(adj[u] - seen)
    return count


def bridge_indices(n, edges):
    assert component_count(n, edges) == 1
    return frozenset(i for i in range(len(edges))
                     if component_count(n, edges[:i] + edges[i + 1:]) > 1)


def odd_vertices(n, edges):
    parity = [0] * n
    for a, b in edges:
        parity[a] ^= 1
        parity[b] ^= 1
    return tuple(parity)


def is_t_join(edges, target, mask):
    parity = [0] * len(target)
    for i, (a, b) in enumerate(edges):
        if mask & (1 << i):
            parity[a] ^= 1
            parity[b] ^= 1
    return tuple(parity) == target


def t_join_masks(n, edges):
    target = odd_vertices(n, edges)
    for mask in range(1 << len(edges)):
        if is_t_join(edges, target, mask):
            yield mask


def fractional_odd_cut_check(n, edges, bridges, override=None):
    """Check all T-odd cuts of the rational 1/3-on-nonbridges certificate."""
    target = odd_vertices(n, edges)
    weights = (override if override is not None else
               [Fraction(1) if i in bridges else Fraction(1, 3)
                for i in range(len(edges))])
    for shore in range(1, 1 << n):
        if sum(target[v] for v in range(n) if shore >> v & 1) % 2:
            capacity = sum(weights[i] for i, (a, b) in enumerate(edges)
                           if ((shore >> a) ^ (shore >> b)) & 1)
            if capacity < 1:
                return False
    return True


def check_instance(n, edges, lengths):
    assert all(0 <= a < n and 0 <= b < n and a != b for a, b in edges)
    assert all(isinstance(k, int) and k >= 2 for k in lengths)
    assert len(edges) == len(lengths) and component_count(n, edges) == 1
    bridges = bridge_indices(n, edges)
    m = sum(lengths)
    b = sum(lengths[i] for i in bridges)
    target_without_bridges = odd_vertices(
        n, [e for i, e in enumerate(edges) if i not in bridges])
    all_even = not any(target_without_bridges)
    assert fractional_odd_cut_check(n, edges, bridges)
    candidates = []
    for mask in t_join_masks(n, edges):
        removed = [i for i in range(len(edges)) if mask >> i & 1]
        assert bridges.issubset(removed)
        c = component_count(n, [e for i, e in enumerate(edges)
                                if not mask >> i & 1])
        cost = m + sum(lengths[i] - 2 for i in removed) + 2 * (c - 1)
        join_cost = sum(lengths[i] for i in removed)
        candidates.append((cost, join_cost, c, mask))
    tsp = min(row[0] for row in candidates)
    join = min(row[1] for row in candidates)
    sep = m + b
    fractional_cost = b + Fraction(m - b, 3)
    assert join <= fractional_cost
    assert tsp >= sep
    assert tsp <= Fraction(4 * m + 2 * b, 3)
    exactness = any(
        all(lengths[i] == 2 for i in range(len(edges))
            if mask >> i & 1 and i not in bridges)
        and c == len(bridges) + 1
        for _, _, c, mask in candidates
    )
    assert (tsp == sep) == exactness
    if all_even:
        assert tsp == sep
    else:
        assert tsp <= fractional_cost + m - 2
        assert tsp * 3 < 4 * sep
    return {'n': n, 'core_edges': len(edges), 'M': m, 'B': b,
            'SEP': sep, 'TSP': tsp, 't_join_opt': join,
            'even_bridgeless_core': all_even, 'LP_exact': exactness,
            'bridge_count': len(bridges)}


def falsifier_sweep():
    total = 0
    for n in (2, 3, 4):
        pairs = list(combinations(range(n), 2))
        for subset in range(1, 1 << len(pairs)):
            edges = [e for i, e in enumerate(pairs) if subset >> i & 1]
            if component_count(n, edges) != 1:
                continue
            for lengths in product((2, 3), repeat=len(edges)):
                check_instance(n, edges, lengths)
                total += 1
    # Exhaust every loopless labeled multigraph of at most five edges
    # on 2-4 vertices, with indexed repeated edges and lengths 2 or 3.
    for n in (2, 3, 4):
        pairs = list(combinations(range(n), 2))
        for edge_count in range(n - 1, min(6, len(pairs) + 3)):
            for edges in combinations_with_replacement(pairs, edge_count):
                if component_count(n, edges) != 1:
                    continue
                for lengths in product((2, 3), repeat=edge_count):
                    check_instance(n, edges, lengths)
                    total += 1
    for m in range(1, 6):
        edges = [(0, 1)] * m
        for lengths in product((2, 3, 4), repeat=m):
            check_instance(2, edges, lengths)
            total += 1
    rng = random.Random(970043)
    for _ in range(1500):
        n = rng.randrange(2, 6)
        edges = [(rng.randrange(n), rng.randrange(n))
                 for _ in range(rng.randrange(n - 1, 9))]
        edges = [(a, b) for a, b in edges if a != b]
        if not edges or component_count(n, edges) != 1:
            continue
        lengths = [rng.randrange(2, 9) for _ in edges]
        check_instance(n, edges, lengths)
        total += 1
    for L in (2, 3, 4, 10, 1000):
        theta = check_instance(2, [(0, 1)] * 3, [L] * 3)
        assert theta['TSP'] == 4 * L - 2
        assert theta['SEP'] == 3 * L
        pendant = check_instance(3, [(0, 1)] * 3 + [(0, 2)],
                                 [L] * 3 + [7])
        assert pendant['TSP'] == 4 * L - 2 + 14
        assert pendant['SEP'] == 3 * L + 14
        total += 2
    x = check_instance(2, [(0, 1)] * 3, [3, 3, 3])
    y = check_instance(2, [(0, 1)] * 3, [4, 3, 3])
    assert Fraction(x['TSP'], x['SEP']) == Fraction(10, 9)
    assert Fraction(y['TSP'], y['SEP']) == Fraction(11, 10)
    assert Fraction(x['TSP'], x['SEP']) > Fraction(y['TSP'], y['SEP'])
    total += 2
    # Negative controls: invalid fractional witness and false universal -2 slack.
    assert not fractional_odd_cut_check(
        2, [(0, 1)], frozenset(), override=[Fraction(1, 3)])
    tree = check_instance(2, [(0, 1)], [2])
    assert tree['TSP'] > Fraction(4 * tree['M'] + 2 * tree['B'], 3) - 2
    return {'checked_instances': total, 'theta_tight_at': [2, 3, 4, 10, 1000],
            'nonuniform_ratio_decrease': ['10/9', '11/10'],
            'negative_controls': 2, 'independent_review': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.parse_args()
    print(json.dumps(falsifier_sweep(), sort_keys=True))
