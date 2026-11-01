"""Structurally distinct adjacency-matrix check for 17-edge obstructions."""
import sys
import unittest
from itertools import combinations, permutations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch27_seventeen as seven


def cover_number(edges):
    vertices = range(7)
    for size in range(8):
        if any(all(a in cover or b in cover for a, b in edges)
               for cover in combinations(vertices, size)):
            return size
    raise AssertionError("No vertex cover")


def independent_orientation_count(missing):
    edges = tuple(p for p in combinations(range(7), 2) if p not in missing)
    counted = good = 0
    for decision in range(1 << 17):
        matrix = [[False] * 7 for _ in range(7)]
        for i, (a, b) in enumerate(edges):
            if decision & (1 << i):
                a, b = b, a
            matrix[a][b] = True
        if max(sum(matrix[i][j] for i in range(7)) for j in range(7)) > 3:
            continue
        counted += 1
        if not any(matrix[i][j] and matrix[j][k] and matrix[k][i]
                   for i in range(7) for j in range(7) for k in range(7)):
            good += 1
    return counted, good


class SeventeenEdgeExhaustivityTests(unittest.TestCase):
    def test_classification_is_complete_under_relabeling(self):
        # Enumerates all 5985 four-edge missing graphs without relying on
        # the production orientation generator or on external graph libraries.
        reps = [frozenset(m) for m in seven.MISSING_TYPES.values()]
        perms = tuple(permutations(range(7)))
        generated = set()
        for rep in reps:
            self.assertEqual(cover_number(rep), 3)
            for p in perms:
                generated.add(frozenset(tuple(sorted((p[a], p[b])))
                                        for a, b in rep))
        for missing in combinations(seven.PAIRS, 4):
            condition = cover_number(missing) >= 3
            self.assertEqual(frozenset(missing) in generated, condition)
        self.assertEqual(len(generated), 1785)

    def test_independent_orientation_replay(self):
        expected = {
            "triangle_plus_edge": 17192,
            "path4_plus_edge": 18460,
            "path3_plus_two_edges": 20004,
        }
        for name, missing in seven.MISSING_TYPES.items():
            self.assertEqual(independent_orientation_count(set(missing)),
                             (expected[name], 0))
            self.assertEqual(seven.enumerate_orientation_class(missing), {
                "orientations": 131072,
                "indegree_cap_survivors": expected[name],
                "triangle_free_and_cap": 0,
            })

    def test_mutations_detect_bad_missing_edge_sets(self):
        rep = seven.MISSING_TYPES["triangle_plus_edge"]
        for bad in (rep[:-1], rep + (rep[0],)):
            with self.assertRaises(ValueError):
                seven.enumerate_orientation_class(bad)


if __name__ == "__main__":
    unittest.main()
