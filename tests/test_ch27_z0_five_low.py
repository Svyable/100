"""Independent histogram and literal digraph checks for M074 z=0."""
import hashlib
import unittest
from collections import Counter
from scripts import ch27_z0_five_low as subject

FOUR_LOW_ARCS = (
    (0,3),(0,5),(1,2),(1,6),(2,0),(2,4),(3,1),(3,7),
    (4,0),(4,3),(4,5),(5,1),(5,3),(5,7),(6,0),(6,2),
    (6,4),(7,1),(7,2),(7,6),(8,0),(8,1),(8,2),(8,3),
)
FIVE_LOW_ARCS = (
    (0,4),(0,5),(1,0),(1,8),(2,1),(2,3),(3,1),(3,7),
    (4,2),(4,3),(5,2),(5,3),(5,4),(6,0),(6,1),(6,2),
    (6,3),(6,4),(7,0),(7,1),(7,8),(8,0),(8,4),(8,5),
)


def compositions(n, slots):
    if slots == 1:
        yield (n,)
    else:
        for j in range(n + 1):
            for rest in compositions(n-j, slots-1):
                yield (j,) + rest


def independent_audit():
    # Histogram construction is independent of the subject's sorted tuple
    # enumeration and never calls its reject_reason.
    aa = []
    for counts in compositions(4, 6):
        a = (2,)*5 + tuple(d for d,c in zip(range(3,9),counts) for _ in range(c))
        if sum(a) <= 29:
            aa.append(a)
    kk = [tuple(d for d,c in zip(range(1,8),counts) for _ in range(c))
          for counts in compositions(10, 7)]
    stages = Counter()
    for a in aa:
        second = a[-2]
        need = 9 if second == 6 else 8
        for k in kk:
            if sum(k) < 73-sum(a):
                stages['missing_pair_lower_cut'] += 1
            elif sum(x <= second-2 for x in k) < need:
                stages['high_B_eligibility'] += 1
            else:
                stages['unresolved'] += 1
    return len(aa), len(kk), stages


def triangle_free(arcs):
    E = set(arcs)
    if len(E) != len(arcs) or any(x == y or (y,x) in E for x,y in E):
        return False
    return not any((y,z) in E and (z,x) in E for x,y in E for z in range(16))


class TestFiveLow(unittest.TestCase):
    def test_scope_digest(self):
        self.assertEqual(hashlib.sha256(subject.SCOPE.encode()).hexdigest(),
                         subject.SCOPE_SHA256)

    def test_independent_histogram_counts(self):
        a,k,stages = independent_audit()
        self.assertEqual((a,k),(35,8008))
        self.assertEqual(stages,Counter({
            'missing_pair_lower_cut':200489,
            'high_B_eligibility':79791,
        }))
        self.assertEqual(subject.audit()['unresolved'],0)

    def test_literal_nine_vertex_boundaries(self):
        for E,t,degree in [
            (FOUR_LOW_ARCS,4,[2,2,2,2,3,3,3,3,4]),
            (FIVE_LOW_ARCS,5,[2,2,2,2,2,3,3,3,5]),
        ]:
            self.assertTrue(triangle_free(E))
            out=[sum(i==x for i,j in E) for x in range(9)]
            self.assertEqual(sorted(out),degree)
            self.assertEqual(out.count(2),t)
            self.assertEqual(len(E),24)
        self.assertFalse(triangle_free(FIVE_LOW_ARCS+((4,0),)))  # digon
        self.assertFalse(triangle_free(FIVE_LOW_ARCS+((1,4),)))  # triangle

    def test_literal_missing_pair_propagation(self):
        # A literal 9-vertex graph, with 7 added C points. Add each A->C
        # arc needed for outdegree 9, then all triangle-safe C->A arcs.
        E=set(FIVE_LOW_ARCS)
        alpha=[sum(i==x for i,j in E) for x in range(9)]
        for a in range(9):
            for offset in range(9-alpha[a]):
                E.add((a,9+(a+offset)%7))
        for c in range(9,16):
            for a in range(9):
                if (a,c) in E:
                    continue
                trial=E|{(c,a)}
                if triangle_free(tuple(trial)):
                    E=trial
        self.assertTrue(triangle_free(tuple(E)))
        M=sum((a,c) not in E and (c,a) not in E
              for a in range(9) for c in range(9,16))
        self.assertGreaterEqual(M,len(FIVE_LOW_ARCS)-19)
        low={a for a in range(9) if alpha[a]==2}
        for a in range(9):
            if alpha[a]<=2 or not any((a,l) in E for l in low):
                continue
            for c in range(9,16):
                if (a,c) not in E:
                    self.assertNotIn((c,a),E)

    def test_z_zero_hypothesis_cannot_be_dropped(self):
        a=(2,2,2,2,2,3,3,6,6)
        with self.assertRaises(AssertionError):
            subject.reject_reason(a,(0,3,4,4,4,4,5,6,7,7))

    def test_small_graph_is_not_full_counterexample(self):
        self.assertEqual(len({v for edge in FIVE_LOW_ARCS for v in edge}),9)
        self.assertNotEqual(len(FIVE_LOW_ARCS),27*9)


if __name__ == '__main__':
    unittest.main()
