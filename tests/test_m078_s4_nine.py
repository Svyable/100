"""M078 nine-vertex connected unicyclic S4 counterexample controls."""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from m078_s4_nine import (
    A9, B9, BASE_PROFILES, adjacency, card_signature_bitset,
    card_signature_direct, check, cycle_core_length,
    degree_neighborhood_profiles, family,
)


def independently_bipartite(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    colors = {}
    for root in range(n):
        if root in colors:
            continue
        colors[root] = 0
        stack = [root]
        while stack:
            v = stack.pop()
            for w in adj[v]:
                if w in colors:
                    if colors[w] == colors[v]:
                        return False
                else:
                    colors[w] = 1 - colors[v]
                    stack.append(w)
    return True


class M078S4NineTests(unittest.TestCase):
    def test_base_profiles_and_two_cycle_lengths(self):
        self.assertEqual(degree_neighborhood_profiles(9, A9), BASE_PROFILES)
        self.assertEqual(degree_neighborhood_profiles(9, B9), BASE_PROFILES)
        self.assertEqual(cycle_core_length(9, A9), 6)
        self.assertEqual(cycle_core_length(9, B9), 5)

    def test_literal_card_multisets_agree_and_are_paired(self):
        a = card_signature_direct(9, A9)
        b = card_signature_direct(9, B9)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 9)
        self.assertTrue(all(tri == 0 and four == 0 for _, tri, four in a))
        self.assertEqual(a, card_signature_bitset(9, A9))
        self.assertEqual(b, card_signature_bitset(9, B9))

    def test_connected_family_not_just_isolate_padding(self):
        for t in (0, 1, 2, 5, 10, 30, 100):
            (n, a), (_, b) = family(t)
            self.assertEqual(len(a), n)
            self.assertEqual(len(b), n)
            self.assertEqual(cycle_core_length(n, a), 6)
            self.assertEqual(cycle_core_length(n, b), 5)
            self.assertEqual(degree_neighborhood_profiles(n, a),
                             degree_neighborhood_profiles(n, b))
            if t <= 10:
                self.assertEqual(card_signature_direct(n, a),
                                 card_signature_direct(n, b))

    def test_all_fixed_cycle_cutoffs_and_tail_extensions(self):
        for k in range(4, 13):
            for t in (0, 1, 4):
                (n, a), (_, b) = family(t, cycle_subdivisions=k - 4)
                self.assertEqual(n, k + 5 + t)
                self.assertEqual(cycle_core_length(n, a), k + 2)
                self.assertEqual(cycle_core_length(n, b), k + 1)
                self.assertNotEqual(independently_bipartite(n, a),
                                    independently_bipartite(n, b))
                self.assertEqual(degree_neighborhood_profiles(n, a),
                                 degree_neighborhood_profiles(n, b))
                if k <= 7 and t <= 1:
                    self.assertEqual(card_signature_direct(n, a),
                                     card_signature_direct(n, b))

    def test_independent_motif_engines_randomized(self):
        rng = random.Random(10078)
        for n in (5, 7, 9):
            for _ in range(25):
                edges = tuple((i, j) for i in range(n) for j in range(i + 1, n)
                              if rng.randrange(100) < 39)
                self.assertEqual(card_signature_direct(n, edges),
                                 card_signature_bitset(n, edges))

    def test_triangle_and_four_cycle_positive_controls(self):
        # C4 has exactly one 4-cycle; K4 has three.
        square = ((0, 1), (1, 2), (2, 3), (3, 0))
        complete = tuple((i, j) for i in range(4) for j in range(i + 1, 4))
        for edges, expected in ((square, 1), (complete, 3)):
            n = 5
            # The card deleting isolated vertex 4 is exactly C4 or K4.
            direct = card_signature_direct(n, edges)
            self.assertIn((tuple(sorted(sum(1 for a, b in edges if v in (a, b))
                                        for v in range(4))),
                           4 if edges == complete else 0, expected), direct)
            self.assertEqual(direct, card_signature_bitset(n, edges))

    def test_mutation_rejected(self):
        self.assertNotEqual(card_signature_direct(9, A9),
                            card_signature_direct(9, A9[:-1]))
        with self.assertRaises(ValueError):
            adjacency(9, A9 + (A9[0],))
        with self.assertRaises(ValueError):
            adjacency(9, ((0, 0),))
        with self.assertRaises(ValueError):
            family(-1)
        with self.assertRaises(ValueError):
            cycle_core_length(9, A9[:-1])

    def test_full_checker(self):
        result = check()
        self.assertEqual(result["first_order"], 9)
        self.assertEqual(result["cycle_lengths"], [6, 5])


if __name__ == "__main__":
    unittest.main()
