"""M078 #381: exact and adversarial controls for single 4-cycle trades."""
import sys
import unittest
from collections import deque
from itertools import permutations
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from m078_four_cycle_trade import (STAR, PAIRS, path_forms, four_cycles,
                                   constraints, forced_zero_coordinates, verify_all)


def direct_distances(edges, lengths):
    adj = [[] for _ in range(10)]
    for (a, b), w in zip(edges, lengths):
        adj[a].append((b, w))
        adj[b].append((a, w))
    result = []
    for a, b in PAIRS:
        queue = deque([(a, -1, 0)])
        while queue:
            u, previous, distance = queue.popleft()
            if u == b:
                result.append(distance)
                break
            queue.extend((v, u, distance + w) for v, w in adj[u]
                         if v != previous)
    return tuple(result)


class FourCycleTradeTests(unittest.TestCase):
    def test_exhaustive_exact_obstruction(self):
        self.assertEqual(verify_all()["systems"], 4050)

    def test_independent_bfs_all_path_allocations(self):
        weights = (2, 3, 5, 7, 11, 13, 17, 19, 23)
        star_edges = ((0, 7), (1, 7), (2, 8), (3, 8),
                      (4, 9), (5, 9), (6, 7), (6, 8), (6, 9))
        self.assertEqual(direct_distances(star_edges, weights),
                         tuple(sum(x*y for x, y in zip(row, weights))
                               for row in STAR))
        independent = {}
        for a, b, c, d, e, f in permutations(range(6)):
            left, right = tuple(sorted((a, b))), tuple(sorted((e, f)))
            key = min((left, c, d, right), (right, d, c, left))
            independent.setdefault(key, ((a, 6), (b, 6), (c, 7), (d, 8),
                                         (e, 9), (f, 9), (6, 7), (7, 8), (8, 9)))
        self.assertEqual(len(independent), 90)
        for key, matrix in path_forms():
            self.assertEqual(direct_distances(independent[key], weights),
                             tuple(sum(x*y for x, y in zip(row, weights))
                                   for row in matrix))

    def test_cycle_degree_controls(self):
        cycles = four_cycles()
        self.assertEqual(len(cycles), 45)
        for cycle in cycles:
            self.assertEqual(len(cycle), 4)
            vertices = set(v for e in cycle for v in PAIRS[e])
            self.assertEqual(len(vertices), 4)
            self.assertEqual(sorted(sum(v in PAIRS[e] for e in cycle)
                                    for v in vertices), [2, 2, 2, 2])

    def test_elimination_positive_and_negative_controls(self):
        self.assertEqual(forced_zero_coordinates([]), ())
        self.assertEqual(forced_zero_coordinates([(1,) + (0,)*17]), (0,))
        self.assertEqual(forced_zero_coordinates([(1, -1) + (0,)*16]), ())
        self.assertEqual(forced_zero_coordinates([(1, 1) + (0,)*16,
                                                  (1, -1) + (0,)*16]), (0, 1))
        path = next(matrix for _, matrix in path_forms())
        eq = constraints(STAR, path, four_cycles()[0])
        self.assertTrue(forced_zero_coordinates(eq))
        self.assertEqual(forced_zero_coordinates([tuple(0 for _ in row)
                                                 for row in eq]), ())


if __name__ == "__main__":
    unittest.main()
