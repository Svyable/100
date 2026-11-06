"""Adversarial tests for the independent M097 integer min-cut replay."""
import unittest
from scripts.m097_chorded_mincut import (
    audit, brute_min_cut, global_min_cut, self_test, witness,
)


class ChordedMinCutTests(unittest.TestCase):
    def test_large_and_random(self):
        self.assertEqual(len(self_test()), 7)

    def test_exact_gap_instance(self):
        self.assertEqual(audit((3, 3, 3)), (8, 6))

    def test_all_length_two_large(self):
        self.assertEqual(audit((2,) * 20), (22, 380))

    def test_tampered_edge_fails_cut(self):
        graph, scale, _ = witness((3, 3, 3))
        a, b = 0, next(iter(graph[0]))
        graph[a][b] -= 1
        graph[b][a] -= 1
        self.assertLess(global_min_cut(graph), 2 * scale)

    def test_disconnected_negative_control(self):
        graph = {0: {1: 3}, 1: {0: 3}, 2: {}}
        self.assertEqual(global_min_cut(graph), 0)
        self.assertEqual(global_min_cut(graph), brute_min_cut(graph))

    def test_reject_invalid_lengths(self):
        for lengths in ((), (2,), (1, 2), (2, 0), (2, 2.0)):
            with self.assertRaises(ValueError):
                witness(lengths)


if __name__ == "__main__":
    unittest.main()
