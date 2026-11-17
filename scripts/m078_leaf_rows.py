"""Exact six-leaf tree-row inverse search (exploratory M078 #375).

A leaf-row signature retains the multiset of the five leaf-to-leaf
path distances from each leaf, but forgets both vertex labels and column
labels. This module is complete for a fixed signature if complete=True.
Neither successful tests nor a completed bounded search imply novelty.
"""

from collections import Counter
from fractions import Fraction
from itertools import combinations

STAR = (((0, 1), (0, 2), (0, 3)), (1, 1, 2, 2, 3, 3))
PATH = (((0, 1), (1, 2), (2, 3)), (0, 0, 1, 2, 3, 3))


def tree_matrix(shape, core_lengths, pendant_lengths):
    """Construct the 6x6 leaf metric from a positive 9-edge tree."""
    edges, attachments = shape
    if len(core_lengths) != 3 or len(pendant_lengths) != 6:
        raise ValueError('expect 3 core and 6 pendant lengths')
    if not all(x > 0 for x in (*core_lengths, *pendant_lengths)):
        raise ValueError('tree edges must be strictly positive')
    adj = [[] for _ in range(10)]
    for (u, v), w in zip(edges, core_lengths):
        adj[u].append((v, w))
        adj[v].append((u, w))
    for i, (u, w) in enumerate(zip(attachments, pendant_lengths), 4):
        adj[u].append((i, w))
        adj[i].append((u, w))
    result = [[0] * 6 for _ in range(6)]
    for s in range(4, 10):
        stack = [(s, -1, 0)]
        dist = {}
        while stack:
            u, parent, depth = stack.pop()
            dist[u] = depth
            stack.extend((v, u, depth + w) for v, w in adj[u] if v != parent)
        for t in range(4, 10):
            result[s - 4][t - 4] = dist[t]
    return result


def row_signature(matrix):
    n = len(matrix)
    return tuple(sorted(tuple(sorted(matrix[i][j] for j in range(n) if j != i))
                        for i in range(n)))


def _valid_matrix(D):
    n = len(D)
    return n == 6 and all(len(r) == n for r in D) and all(
        D[i][j] == D[j][i] and (D[i][j] == 0 if i == j else D[i][j] > 0)
        for i in range(n) for j in range(n))


def constructive_tree(D):
    """Independent constructive certificate or None for a nonbinary/non-tree matrix.

    Recovers leaf limbs by the Buneman additive limb formula and tests the
    complete four-hub realization by direct 10-node path distances. Uses
    exact rational arithmetic; returns a dict of positive edge lengths.
    """
    if not _valid_matrix(D):
        return None
    leaves = range(6)
    limb = []
    for i in leaves:
        other = [j for j in leaves if j != i]
        limb.append(min(Fraction(D[i][j] + D[i][k] - D[j][k], 2)
                        for j, k in combinations(other, 2)))
    if min(limb) <= 0:
        return None
    # d(i,j)-limb_i-limb_j is distance between leaf-attachment hubs.
    hubdist = [[Fraction(D[i][j]) - limb[i] - limb[j] if i != j else Fraction(0)
                for j in leaves] for i in leaves]
    if any(hubdist[i][j] < 0 for i, j in combinations(leaves, 2)):
        return None
    groups = []
    for i in leaves:
        if any(i in g for g in groups):
            continue
        group = tuple(j for j in leaves if i == j or hubdist[i][j] == 0)
        groups.append(group)
    groups.sort()
    if any((hubdist[i][j] == 0) != any(i in g and j in g for g in groups)
           for i, j in combinations(leaves, 2)):
        return None
    if sum(map(len, groups)) != 6:
        return None

    def hub(a, b):
        return hubdist[a[0]][b[0]]

    if len(groups) == 3 and all(len(g) == 2 for g in groups):
        # The 3 cherry hubs form a 3-leaf star about a fourth hub.
        A, B, C = groups
        ab, ac, bc = hub(A, B), hub(A, C), hub(B, C)
        core = ((ab + ac - bc) / 2, (ab + bc - ac) / 2,
                (ac + bc - ab) / 2)
        attachment = [None] * 6
        for j, group in enumerate(groups, 1):
            for leaf in group:
                attachment[leaf] = j
        shape = STAR
        kind = 'star'
    elif len(groups) == 4 and sorted(map(len, groups)) == [1, 1, 2, 2]:
        ends = sorted([g for g in groups if len(g) == 2])
        mid = sorted([g for g in groups if len(g) == 1])
        E1, E2 = ends
        possible = []
        for M1, M2 in (mid, mid[::-1]):
            core_try = (hub(E1, M1), hub(M1, M2), hub(M2, E2))
            if min(core_try) > 0 and sum(core_try) == hub(E1, E2):
                possible.append((core_try, (E1, M1, M2, E2)))
        if not possible:
            return None
        core, ordered_groups = possible[0]
        attachment = [None] * 6
        for j, group in enumerate(ordered_groups):
            for leaf in group:
                attachment[leaf] = j
        shape = PATH
        kind = 'path'
    else:
        return None

    if min(core) <= 0:
        return None
    # Independent witness: the explicit weighted 10-vertex tree reproduces
    # *all* 15 pair distances, not merely the cherry or quartet structure.
    reconstructed = tree_matrix((shape[0], tuple(attachment)), core, limb)
    if any(reconstructed[i][j] != D[i][j] for i, j in combinations(leaves, 2)):
        return None
    return {
        'topology': kind,
        'core_edges': shape[0],
        'core_lengths': tuple(core),
        'pendant_lengths': tuple(limb),
        'attachments': tuple(attachment),
    }


def _validate_rows(rows):
    if len(rows) != 6 or any(len(row) != 5 for row in rows):
        raise ValueError('expected exactly six five-entry rows')
    if any(not isinstance(x, int) or isinstance(x, bool) or x <= 0
           for row in rows for x in row):
        raise ValueError('requires strictly positive integer distances')
    counted = Counter(x for row in rows for x in row)
    if any(k % 2 for k in counted.values()):
        raise ValueError('each pair distance must appear an even number of times')


def exact_search(rows, max_nodes=100000):
    """Enumerate all compatible positive-integer symmetric matrices (six leaves).

    Search results: `trees` is a list of (certificate, matrix) pairs;
    `complete` means the entire row-compatible matrix space was searched.
    Unlike a statistical sampler, no negative claim is valid if `complete=False`.
    The cap bounds recursive states, not the number of found solutions.
    """
    _validate_rows(rows)
    if not isinstance(max_nodes, int) or max_nodes < 1:
        raise ValueError('max_nodes must be a positive integer')
    n = 6
    residual = [Counter(row) for row in rows]
    D = [[0] * n for _ in range(n)]
    unknown = set(combinations(range(n), 2))
    hits = Counter()
    found = []
    nodes = 0
    complete = True
    rejected_partial = 0

    def place(pair, value):
        i, j = pair
        if pair not in unknown or residual[i][value] <= 0 or residual[j][value] <= 0:
            raise ValueError('inconsistent pair assignment')
        residual[i][value] -= 1
        residual[j][value] -= 1
        D[i][j] = D[j][i] = value
        unknown.remove(pair)

    def unplace(pair, value):
        i, j = pair
        unknown.add(pair)
        D[i][j] = D[j][i] = 0
        residual[i][value] += 1
        residual[j][value] += 1

    # Singleton pair colors are necessarily a particular edge.
    total = Counter(x for row in rows for x in row)
    try:
        for value, c in total.items():
            if c != 2:
                continue
            ends = [i for i in range(n) if residual[i][value] != 0]
            if len(ends) != 2:
                return {'trees': [], 'complete': True, 'states': 0, 'matrix_count': 0,
                        'partial_rejects': 0, 'residual_edges': 0}
            place(tuple(sorted(ends)), value)
    except ValueError:
        return {'trees': [], 'complete': True, 'states': 0, 'matrix_count': 0,
                'partial_rejects': 0, 'residual_edges': 0}

    # For every connected forest component, the degree-one vertex fixes the
    # last incident edge, regardless of the count of distinct repeated values.
    while True:
        deg = Counter(i for pair in unknown for i in pair)
        leaves = [i for i in range(n) if deg[i] == 1]
        if not leaves:
            break
        i = leaves[0]
        pair = next(e for e in sorted(unknown) if i in e)
        values = [x for x, c in residual[i].items() if c > 0]
        if len(values) != 1:
            return {'trees': [], 'complete': True, 'states': 0, 'matrix_count': 0,
                    'partial_rejects': 0, 'residual_edges': len(unknown)}
        try:
            place(pair, values[0])
        except ValueError:
            return {'trees': [], 'complete': True, 'states': 0, 'matrix_count': 0,
                    'partial_rejects': 0, 'residual_edges': len(unknown)}
    residual_edges = len(unknown)

    def partial_consistent(pair, val):
        u, v = pair
        # Triangle inequalities on any completely exposed triangle.
        for w in range(n):
            if w in pair or not (D[u][w] and D[v][w]):
                continue
            if not (abs(D[u][w] - D[v][w]) <= val <= D[u][w] + D[v][w]):
                return False
        # All quartet inequalities for which the last missing edge is pair.
        # A tree metric has two equal maximal opposing-pair sums.
        for others in combinations((x for x in range(n) if x not in pair), 2):
            a, b = others
            if not all(D[x][y] > 0 for x, y in
                       ((u, a), (u, b), (v, a), (v, b))):
                continue
            s = sorted((val + D[a][b], D[u][a] + D[v][b], D[u][b] + D[v][a]))
            if D[a][b] and s[-1] != s[-2]:
                return False
        return True

    def walk():
        nonlocal nodes, complete, rejected_partial
        if nodes >= max_nodes:
            complete = False
            return
        nodes += 1
        if not unknown:
            if any(c != 0 for row in residual for c in row.values()):
                raise AssertionError('missing residual bookkeeping')
            if row_signature(D) != tuple(sorted(tuple(sorted(r)) for r in rows)):
                raise AssertionError('row signature mismatch')
            hits['matrix_count'] += 1
            cert = constructive_tree(D)
            if cert is not None:
                found.append((cert, tuple(tuple(r) for r in D)))
            return
        options = []
        for edge in sorted(unknown):
            u, v = edge
            common = [x for x in sorted(residual[u])
                      if residual[u][x] > 0 and residual[v][x] > 0]
            if not common:
                return
            options.append((len(common), edge, common))
        _, edge, common = min(options)
        for val in common:
            if not partial_consistent(edge, val):
                rejected_partial += 1
                continue
            place(edge, val)
            walk()
            unplace(edge, val)
            if not complete:
                return

    walk()
    return {'trees': found, 'complete': complete, 'states': nodes,
            'matrix_count': hits['matrix_count'],
            'partial_rejects': rejected_partial, 'residual_edges': residual_edges}


def audit_tree_certificate(matrix, cert, require_integer_edges=False):
    """Check a proposed certificate *without* trusting the inverse solver."""
    core = cert['core_lengths']
    pendant = cert['pendant_lengths']
    attachment = cert['attachments']
    kind = cert['topology']
    if kind not in {'star', 'path'}:
        return False
    if len(core) != 3 or len(pendant) != 6 or len(attachment) != 6:
        return False
    if min((*core, *pendant)) <= 0:
        return False
    if require_integer_edges and any(Fraction(a).denominator != 1
                                     for a in (*core, *pendant)):
        return False
    edges = STAR[0] if kind == 'star' else PATH[0]
    required = sorted(STAR[1]) if kind == 'star' else sorted(PATH[1])
    if list(sorted(attachment)) != required:
        return False
    if tuple(map(tuple, cert['core_edges'])) != edges:
        return False
    return tree_matrix((edges, attachment), core, pendant) == [list(x) for x in matrix]


def main(argv=None):
    """Machine-readable, falsification-oriented CLI for an exact row signature."""
    import argparse
    import json
    import sys
    from time import perf_counter
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rows-json', help='file containing six five-entry rows; use - for stdin')
    parser.add_argument('--example', choices=('star', 'path'),
                        help='generate a fixed example instead of supplying a file')
    parser.add_argument('--max-nodes', type=int, default=100000,
                        help='maximum recursion states (cap exhaustion is INCONCLUSIVE)')
    args = parser.parse_args(argv)
    if (args.rows_json is None) == (args.example is None):
        parser.error('choose exactly one of --rows-json or --example')
    if args.rows_json is not None:
        if args.rows_json == '-':
            payload = json.load(sys.stdin)
        else:
            with open(args.rows_json, encoding='utf-8') as handle:
                payload = json.load(handle)
        rows = payload['rows'] if isinstance(payload, dict) else payload
    else:
        shape = STAR if args.example == 'star' else PATH
        rows = row_signature(tree_matrix(shape, (1,2,3), (1,4,5,6,7,8)))
    start = perf_counter()
    results = exact_search(rows, max_nodes=args.max_nodes)
    elapsed = perf_counter() - start
    classes = {}
    for cert, matrix in results['trees']:
        if cert['topology'] in classes:
            continue
        if not audit_tree_certificate(matrix, cert, require_integer_edges=True):
            continue
        classes[cert['topology']] = {
            'leaf_matrix': [list(row) for row in matrix],
            'core_edges': cert['core_edges'],
            'core_lengths': [str(v) for v in cert['core_lengths']],
            'attachments': cert['attachments'],
            'pendant_lengths': [str(v) for v in cert['pendant_lengths']],
        }
    payload = {'result': 'INCONCLUSIVE' if not results['complete'] else
               'CROSS_TOPOLOGY_COLLISION' if len(classes) == 2 else 'NO_CROSS_TOPOLOGY_COLLISION',
               'complete': results['complete'],
               'topologies_found_integer_edges': sorted(classes),
               'certificates': classes,
               'states': results['states'],
               'matrix_count': results['matrix_count'],
               'tree_metric_count_including_noninteger': len(results['trees']),
               'partial_rejects': results['partial_rejects'],
               'residual_edges_after_peeling': results['residual_edges'],
               'elapsed_seconds': round(elapsed, 6)}
    json.dump(payload, sys.stdout, indent=2)
    print()
    return 0 if results['complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
