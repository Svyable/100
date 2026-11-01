"""Independent matrix/histogram checks for the CH27 directed-girth deficit cut.

No program here enumerates a 27-vertex graph.
"""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ch27_girth_deficit as target


def compositions(total, bins):
    if bins == 1:
        yield (total,)
    else:
        for n in range(total + 1):
            for suffix in compositions(total-n, bins-1):
                yield (n,) + suffix


def independent_profiles():
    aa = []
    for h in compositions(9, 7):
        if sum(i*h[i] for i in range(7)) <= 11:
            aa.append(tuple(i+2 for i in range(7) for _ in range(h[i])))
    kk = []
    for h in compositions(6, 7):
        kk.append((0,)*4 + tuple(i+1 for i in range(7) for _ in range(h[i])))
    return sorted(aa), sorted(kk)


def independent_classifier(alpha, kk):
    total = sum(alpha)
    if sum(kk) < 92-2*total:
        return "prior"
    floors = sorted((max(0, 1+x-sum(1 for a in alpha if a >= x+2))
                    for x in kk), reverse=True)
    if any(sum(floors[:s]) > s*(19-s)//2 for s in range(1, 11)):
        return "prior"
    if floors[2] >= 8 or any(floors[s-1] >= 12-s for s in (4, 5, 6)):
        return "prior"
    for s in range(4,11):
        if floors[s-1] >= 11-s and sum(floors[:s]) > s*(19-s)//2-2:
            return f"girth_subset_{s}"
    if alpha.count(2) >= 7 and 81-sum(alpha)-sum(kk) > 16:
        return "seven_vertex_c_cut"
    for s in range(4,11):
        if floors[s-1] >= 11-s and sum(floors[:s]) == s*(19-s)//2-2:
            internal = tuple(v-(10-s) for v in floors[:s])
            expected = tuple(range(s-1,3,-1))+(1,1,1,1)
            if internal != expected:
                return f"equality_rigidity_{s}"
    return "unresolved"


def directed_cycle(shortest_out, length):
    vertices = range(len(shortest_out))
    for subset in combinations(vertices, length):
        for p in __import__("itertools").permutations(subset):
            if all(p[(i+1) % length] in shortest_out[p[i]]
                   for i in range(length)):
                return True
    return False


def exhaustive_oriented(n):
    """All 3^(n choose 2) partial orientations, independent matrix check."""
    pairs = tuple(combinations(range(n), 2))
    maxima = {4: -1, 5: -1}
    for assignments in product((0, 1, 2), repeat=len(pairs)):
        out = [set() for _ in range(n)]
        arcs = 0
        for flag, (u,v) in zip(assignments, pairs):
            if flag == 1:
                out[u].add(v); arcs += 1
            elif flag == 2:
                out[v].add(u); arcs += 1
        if any(not row for row in out):
            continue
        if directed_cycle(out,3):
            continue
        if arcs == n*(n-1)//2-2:
            rigid = tuple(range(n-1,3,-1))+(1,)*4
            actual = tuple(sorted((len(row) for row in out),reverse=True))
            if actual != rigid:
                raise AssertionError("sharp graph violates equality rigidity")
        maxima[4] = max(maxima[4], arcs)
        if not directed_cycle(out,4):
            maxima[5] = max(maxima[5], arcs)
    return maxima


def constructed_sharp(girth,n):
    out = [set() for _ in range(n)]
    for i in range(girth):
        out[i].add((i+1) % girth)
    for source in range(girth,n):
        out[source].update(range(source))
    return out


class GirthDeficitTests(unittest.TestCase):
    def test_general_girth_deficit_and_sharpness(self):
        for g in range(4,8):
            for n in range(g, g+3):
                out = constructed_sharp(g,n)
                arcs = sum(len(row) for row in out)
                self.assertEqual(arcs, n*(n-1)//2-g*(g-3)//2)
                self.assertTrue(all(out))
                for k in range(3,g):
                    self.assertFalse(directed_cycle(out,k))
                self.assertTrue(directed_cycle(out,g))
        for bad in (3, True, 4.5, "5"):
            with self.assertRaises(ValueError):
                target.required_missing_edges(bad)

    def test_all_partial_orientations_on_four_and_five_vertices(self):
        self.assertEqual(exhaustive_oriented(4)[4], 4)
        self.assertEqual(exhaustive_oriented(5), {4:8, 5:5})

    def test_histogram_profile_replay_independent_of_production_gates(self):
        alphas, ks = independent_profiles()
        self.assertEqual((len(alphas), len(ks)), (166,924))
        stages=Counter(independent_classifier(a,k) for a in alphas for k in ks)
        self.assertEqual(stages["girth_subset_4"],74)
        self.assertEqual(stages["girth_subset_5"],49)
        self.assertEqual(stages["girth_subset_6"],29)
        self.assertEqual(stages["seven_vertex_c_cut"],15)
        self.assertEqual(stages["equality_rigidity_6"],25)
        self.assertEqual(stages["unresolved"],103)
        self.assertEqual(stages["prior"], 153384-295)
        self.assertEqual(target.audit()["remaining"],103)

    def test_two_missing_edge_mutation_and_positive_boundary(self):
        self.assertEqual(target.first_girth_subset_violation(
            (7,7,7,7,0,0,0,0,0,0)),None)
        self.assertEqual(target.first_girth_subset_violation(
            (8,7,7,7,0,0,0,0,0,0)),4)
        self.assertIsNone(target.first_girth_subset_violation(
            (8,7,7,7,0,0,0,0,0,0), missing=1))
        self.assertEqual(target.audit(missing=1)["remaining"],191)
        self.assertEqual(target.audit(missing=0)["remaining"],275)
        self.assertEqual(target.audit(include_rigidity=False)["remaining"],128)
        self.assertEqual(target.audit(include_c=False,include_rigidity=False)["remaining"],143)
        self.assertEqual(target.first_rigidity_violation(
            (8,6,6,6,6,5,0,0,0,0)),6)
        self.assertIsNone(target.first_rigidity_violation(
            (9,8,5,5,5,5,0,0,0,0)))
        self.assertTrue(target.c_cut_violation(
            (2,)*7+(6,8), (0,)*4+(4,6,6,6,7,7)))
        self.assertFalse(target.c_cut_violation(
            (2,)*7+(7,8), (0,)*4+(5,5,6,6,7,7)))

    def test_fail_closed_inputs(self):
        for floors in ((8,7,7), (0,)*9+(1,), (-1,)*10, (1.2,)*10):
            with self.assertRaises(ValueError):
                target.first_girth_subset_violation(floors)


if __name__ == "__main__":
    unittest.main()
