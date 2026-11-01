"""Independent exact controls for nine-vertex lemma / regular (27,9) cut."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch27_crosscut as ch


def histogram_profiles():
    """Separate composition-based generator: counts of outdegrees 2,...,8."""
    def compositions(total, bins):
        if bins == 1:
            yield (total,)
        else:
            for first in range(total + 1):
                for rest in compositions(total - first, bins - 1):
                    yield (first,) + rest
    result = []
    for counts in compositions(9, 7):
        if sum(degree * count for degree, count in enumerate(counts)) > 11:
            continue
        result.append(tuple(degree + 2 for degree, count in enumerate(counts)
                            for _ in range(count)))
    return tuple(sorted(result))


def independent_audit(profiles):
    # Build seven-bin frequency vectors; count eligible pairs by convolution.
    frequencies = []
    for p in profiles:
        counts = tuple(p.count(d) for d in range(2, 9))
        frequencies.append((sum(p), counts))
    max_allowed = -1
    min_required = 100
    max_margin = -100
    unexcluded = 0
    for sa, a in frequencies:
        for sb, b in frequencies:
            demand = max(81 - 2 * sa, 81 - 2 * sb)
            allowed = sum(a[i] * b[j] for i in range(7) for j in range(7)
                          if i + j >= 6)
            max_allowed = max(max_allowed, allowed)
            min_required = min(min_required, demand)
            max_margin = max(max_margin, allowed - demand)
            unexcluded += allowed >= demand
    return max_allowed, min_required, max_margin, unexcluded


def graph_valid(graph):
    vertices = set(graph)
    if any(a not in vertices or x in outgoing
           for x, outgoing in graph.items() for a in outgoing):
        return False
    if any(x in graph[y] for x in graph for y in graph[x]):
        return False
    return not any(x in graph[z] for x in graph
                   for y in graph[x] for z in graph[y])


class NineVertexAnd27RegularTests(unittest.TestCase):
    def test_profile_count_with_independent_generator(self):
        generated = histogram_profiles()
        self.assertEqual(len(generated), 166)
        self.assertEqual(generated, ch.profiles())

    def test_crosscut_independent_convolution(self):
        self.assertEqual(independent_audit(histogram_profiles()),
                         (22, 23, -1, 0))
        report = ch.audit()
        self.assertEqual((report["profiles"], report["profile_pairs"],
                          report["not_excluded_pairs"]), (166, 27556, 0))
        alpha, beta, demand, allowed = report["max_margin_witness"]
        self.assertEqual((demand, allowed), (23, 22))
        self.assertEqual((sum(alpha), sum(beta)), (29, 29))

    def test_one_arc_local_bound_mutation_destroys_exclusion(self):
        weak = ch.audit(local_arc_cap=30)
        self.assertEqual(weak["not_excluded_pairs"], 60)
        self.assertGreaterEqual(weak["maximum_eligible_minus_required"], 0)

    def test_local_sharp_witness_and_corruptions(self):
        graph = ch.sharp_local_witness()
        self.assertEqual(len(graph), 9)
        self.assertEqual(sum(len(v) for v in graph.values()), 29)
        self.assertEqual(min(map(len, graph.values())), 2)
        self.assertTrue(graph_valid(graph))
        loop = {i: set(nbrs) for i, nbrs in graph.items()}
        loop[0].add(0)
        self.assertFalse(graph_valid(loop))
        digon = {i: set(nbrs) for i, nbrs in graph.items()}
        digon[0].add(7)
        self.assertFalse(graph_valid(digon))
        triangle = {i: set(nbrs) for i, nbrs in graph.items()}
        triangle[3].add(0)  # 0 -> 1 -> 3 -> 0; no added digon
        self.assertFalse(any(x in triangle[y] for x in triangle
                             for y in triangle[x]))
        self.assertFalse(graph_valid(triangle))

    def test_irregular_branch_negative_control(self):
        x = ch.irregular_relaxed_obstruction()
        self.assertEqual((x["m"], x["cut_required"], x["cut_observed"],
                          x["zero_k_vertices"]), (29, 34, 34, 4))
        self.assertEqual(x["B_outdegree_floors"],
                         [8, 8, 4, 4, 4, 4, 0, 0, 0, 0])
        self.assertTrue(x["B_subset_caps_pass"])
        # This is not a graph; it prevents false promotion of the irregular case.

    def test_invalid_local_cap(self):
        for x in (17, 29.5, True):
            with self.assertRaises(ValueError):
                ch.profiles(x)


if __name__ == "__main__":
    unittest.main()
