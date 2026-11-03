"""Independent controls for the eight-vertex source-chain theorem and CH27 cuts.

The finite tests confirm necessary arithmetic and positive/falsifying fixtures.
The mathematical universal implication is proved in the associated note.
"""
from collections import Counter
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch27_rigidity as target
import ch27_b_internal as baseline


def graph_stats(rows):
    """Independent adjacency-matrix checker; no calls to target graph code."""
    n = len(rows)
    mat = [[int(j in rows[i]) for j in range(n)] for i in range(n)]
    if any(mat[i][i] for i in range(n)):
        raise ValueError("loop")
    if any(mat[i][j] and mat[j][i] for i in range(n) for j in range(n)):
        raise ValueError("digon")
    if any(mat[i][j] and mat[j][k] and mat[k][i]
           for i in range(n) for j in range(n) for k in range(n)):
        raise ValueError("directed triangle")
    outgoing = [sum(x) for x in mat]
    incoming = [sum(mat[i][j] for i in range(n)) for j in range(n)]
    return outgoing, incoming


class TestRigidity(unittest.TestCase):
    def test_four_vertex_cycle_forced(self):
        """Every C3-free oriented four-vertex min-out-1 graph is an exact C4."""
        pairs = tuple(combinations(range(4), 2))
        number = 0
        for choices in product(range(3), repeat=len(pairs)):
            out = [set() for _ in range(4)]
            for (u, v), choice in zip(pairs, choices):
                if choice == 1:
                    out[u].add(v)
                elif choice == 2:
                    out[v].add(u)
            if min(map(len, out)) < 1:
                continue
            try:
                graph_stats(out)
            except ValueError:
                continue
            number += 1
            self.assertEqual(sorted(map(len, out)), [1] * 4)
            self.assertEqual(sum(map(len, out)), 4)
            self.assertEqual(sorted(sum(v in row for row in out) for v in range(4)), [1] * 4)
        self.assertEqual(number, 6)  # directed C4s on four labeled vertices

    def test_source_chain_positive_witness_and_mutation(self):
        seven = [{(i + 1) % 7, (i + 2) % 7} for i in range(7)]
        eight = seven + [set(range(7))]
        outgoing, incoming = graph_stats(eight)
        self.assertEqual(sum(outgoing), 21)
        self.assertEqual(sorted(outgoing), [2] * 7 + [7])
        self.assertEqual(sorted(incoming), [0] + [3] * 7)
        nine = eight + [set(range(8))]
        outgoing, incoming = graph_stats(nine)
        self.assertEqual(sum(outgoing), 29)
        self.assertEqual(sorted(outgoing), [2] * 7 + [7, 8])
        self.assertEqual(sorted(incoming), [0, 1] + [4] * 7)
        # A one-edge mutation introduces a digon, correctly rejected.
        changed = [set(x) for x in nine]
        changed[0].add(8)
        with self.assertRaises(ValueError):
            graph_stats(changed)

    def test_deficiency_partitions_need_the_stronger_local_bound(self):
        expected = [
            ((0,) + (3,) * 7, 21),
            ((1, 2) + (3,) * 6, 20),
            ((2,) * 3 + (3,) * 5, 19),
        ]
        got = []
        # Construct indegree partitions *without* using the production function.
        for degrees in combinations_with_replacement(range(4), 8):
            if sum(degrees) == 21:
                upper = sum((7, 5, 3, 2)[d] for d in degrees)
                got.append((degrees, upper))
        self.assertEqual(got, expected)
        weaker = sum((7, 5, 4, 2)[d] for d in expected[1][0])
        self.assertEqual(weaker, 21)  # without the new b=2 cap, no contradiction

    def test_relaxed_profile_filter_second_path(self):
        counts = Counter()
        sample = None
        for a in combinations_with_replacement(range(2, 9), 9):
            m = sum(a)
            if m > 29:
                continue
            for positive in combinations_with_replacement(range(1, 8), 6):
                k = (0,) * 4 + positive
                if sum(k) < 92 - 2 * m:
                    continue
                floors = baseline.internal_B_floors(a, k)
                if not baseline.subset_capacity_ok(floors) or baseline.forbidden_small_set(floors) is not None:
                    continue
                counts["previously_unexcluded"] += 1
                if m == 29 and max(a) == 8 and a != (2,) * 7 + (7, 8):
                    counts["removed_by_new_rigidity"] += 1
                elif a.count(2) >= 7 and sum(k) < 65 - m:
                    counts["removed_by_existing_c_cap"] += 1
                else:
                    counts["remaining"] += 1
                    if sample is None:
                        sample = (a, k)
        self.assertEqual(dict(counts), {
            "previously_unexcluded": 295,
            "removed_by_new_rigidity": 120,
            "removed_by_existing_c_cap": 20,
            "remaining": 155,
        })
        self.assertIsNotNone(sample)
        self.assertEqual(target.profile_audit()["counts"], dict(counts))

    def test_reject_only_inside_proved_hypothesis(self):
        exceptional = (2,) * 7 + (7, 8)
        self.assertFalse(target.rigidity_falsifier(exceptional))
        self.assertTrue(target.rigidity_falsifier((2,) * 6 + (3, 6, 8)))
        self.assertFalse(target.rigidity_falsifier((2,) * 7 + (6, 8)))  # m=28
        self.assertFalse(target.c_cut_falsifier((2,) * 6 + (3, 6, 8),
                                                (0,) * 4 + (5, 6, 6, 6, 7, 7)))
        with self.assertRaises(ValueError):
            target.rigidity_falsifier((8, 7) + (2,) * 7)


if __name__ == "__main__":
    unittest.main()
