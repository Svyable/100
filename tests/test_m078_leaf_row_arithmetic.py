"""Independent exact arithmetic cross-topology check for M078 #375.

This verifier does not import the leaf-row inverse engine. It enumerates every
positive integer edge assignment in a stated box and builds row signatures
directly from the hub attachment formulas. No unbounded claim is implied.
"""
from itertools import product
import unittest


def arithmetic_signature(topology, lengths):
    edges, arms = lengths[:3], lengths[3:]
    if topology == "star":
        hubs = (1, 1, 2, 2, 3, 3)

        def between(i, j):
            u, v = hubs[i], hubs[j]
            return 0 if u == v else edges[u - 1] + edges[v - 1]
    elif topology == "path":
        hubs = (0, 0, 1, 2, 3, 3)

        def between(i, j):
            u, v = sorted((hubs[i], hubs[j]))
            return sum(edges[u:v])
    else:
        raise ValueError("unknown topology")

    return tuple(sorted(tuple(sorted(
        arms[i] + arms[j] + between(i, j)
        for j in range(6) if j != i
    )) for i in range(6)))


class IndependentArithmeticBox(unittest.TestCase):
    def test_full_positive_box_through_three(self):
        # 2 * 3**9 = 39,366 parameter tuples, with repeated signatures.
        # Independent of the graph-walk generator and inverse search.
        star = {arithmetic_signature("star", p)
                for p in product((1, 2, 3), repeat=9)}
        path = {arithmetic_signature("path", p)
                for p in product((1, 2, 3), repeat=9)}
        self.assertEqual(len(star), 1140)
        self.assertEqual(len(path), 4455)
        self.assertTrue(star.isdisjoint(path))


if __name__ == "__main__":
    unittest.main()
