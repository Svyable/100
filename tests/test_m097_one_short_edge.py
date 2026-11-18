"""Exact rational cut-cover certificates for two adversarial M097 controls.

These author-side checks are not independent mathematical review.  They audit
literal cut shores and rational dual coefficients without an LP solver.
"""
import itertools
import unittest
from fractions import Fraction


def expand(core_edges, lengths):
    n = max(max(a, b) for a, b in core_edges) + 1
    edges, paths = [], []
    for (a, b), length in zip(core_edges, lengths):
        previous, path = a, []
        for i in range(length):
            following = b if i == length - 1 else n
            if i != length - 1:
                n += 1
            path.append(len(edges))
            edges.append((previous, following))
            previous = following
        paths.append(path)
    return n, edges, paths


def cut_edges(n, edges, shore):
    return frozenset(i for i, (a, b) in enumerate(edges)
                     if ((shore >> a) & 1) != ((shore >> b) & 1))


def literal_shores(n, edges):
    return {cut_edges(n, edges, shore) for shore in range(1, (1 << n) - 1)}


def verify(core, lengths, expected):
    n, edges, paths = expand(core, lengths)
    assert lengths[0] == 1 and all(x >= 2 for x in lengths[1:])
    shores = literal_shores(n, edges)
    short = paths[0][0]
    dual = {}
    for path in paths[1:]:
        for i, j in itertools.combinations(path, 2):
            cut = frozenset((i, j))
            assert cut in shores, (n, cut)
            dual[cut] = dual.get(cut, Fraction(0)) + Fraction(1, len(path) - 1)
    if expected == len(edges):
        candidates = [p for p in paths[1:] if all(frozenset((short, i)) in shores for i in p)]
        assert candidates, 'No two-edge core cut'
        path = candidates[0]
        dual = {}
        for p in paths[1:]:
            weight = Fraction(1, len(p) if p is path else len(p) - 1)
            for i, j in itertools.combinations(p, 2):
                cut = frozenset((i, j))
                assert cut in shores
                dual[cut] = dual.get(cut, Fraction(0)) + weight
        for i in path:
            cut = frozenset((short, i))
            dual[cut] = dual.get(cut, Fraction(0)) + Fraction(1, len(path))
    else:
        assert expected == len(edges) - 1
        assert not any(all(frozenset((short, i)) in shores for i in p) for p in paths[1:])
    coefficients = [sum((weight for cut, weight in dual.items() if i in cut), Fraction(0))
                    for i in range(len(edges))]
    assert all(c <= 1 for c in coefficients)
    assert sum(2 * w for w in dual.values()) == expected
    primal = [0 if i == short and expected == len(edges) - 1 else 1
              for i in range(len(edges))]
    assert all(sum(primal[i] for i in cut) >= 2 for cut in shores)
    assert sum(primal) == expected
    return len(dual)


class OneShortEdgeCertificates(unittest.TestCase):
    def test_k4_no_two_edge_cut(self):
        self.assertGreater(verify([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
                                  [1, 2, 2, 2, 2, 2], 10), 0)

    def test_triangle_two_edge_cut(self):
        self.assertGreater(verify([(0, 1), (1, 2), (2, 0)], [1, 2, 2], 5), 0)

    def test_parallel_two_edge_cut(self):
        self.assertGreater(verify([(0, 1), (0, 1)], [1, 3], 4), 0)


if __name__ == '__main__':
    unittest.main()
