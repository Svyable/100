"""Exact adversarial controls for the bounded M078 leaf-row inversion tool."""
import random
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from itertools import combinations, permutations, product

from m078_leaf_rows import (
    STAR, PATH, tree_matrix, row_signature, constructive_tree, exact_search,
    audit_tree_certificate,
)


def direct_quartet_classifier(D):
    """Separate all-quartets / split topology classifier, NOT the limb decoder."""
    for a,b,c,d in combinations(range(6),4):
        s=sorted((D[a][b]+D[c][d], D[a][c]+D[b][d], D[a][d]+D[b][c]))
        if s[-1] != s[-2]:
            return None
    if any(min(D[x][y]+D[x][z]-D[y][z]
               for y,z in combinations((v for v in range(6) if v!=x),2))<=0
           for x in range(6)):
        return None
    splits=[]
    for k in (2,3):
        for A in combinations(range(6),k):
            if k==3 and 0 not in A:
                continue
            B=[b for b in range(6) if b not in A]
            if all(D[i][j]+D[s][t] < D[i][s]+D[j][t] == D[i][t]+D[j][s]
                   for i,j in combinations(A,2) for s,t in combinations(B,2)):
                splits.append(k)
    if len(splits)!=3:
        return None
    return 'path' if splits.count(3)==1 else 'star' if splits.count(3)==0 else None


class SixLeafRowsTest(unittest.TestCase):
    def test_tied_symmetric_known(self):
        for shape,kind in ((STAR,'star'),(PATH,'path')):
            for lengths in ((1,)*9,(1,2,3,1,4,5,6,7,8)):
                D=tree_matrix(shape,lengths[:3],lengths[3:])
                self.assertEqual(constructive_tree(D)['topology'],kind)
                self.assertEqual(direct_quartet_classifier(D),kind)
                result=exact_search(row_signature(D),max_nodes=100000)
                self.assertTrue(result['complete'])
                self.assertTrue(result['trees'])
                for cert,matrix in result['trees']:
                    self.assertEqual(cert['topology'],kind)
                    self.assertTrue(audit_tree_certificate(matrix,cert,True))
                    self.assertEqual(row_signature(matrix),row_signature(D))

    def test_complete_small_integer_box(self):
        # Every edge is either 1 or 2: 2*2**9 = 1,024 source tuples.
        # This is a *finite negative check only*, not an all-orders theorem.
        total=0
        for shape,kind in ((STAR,'star'),(PATH,'path')):
            for lengths in product((1,2), repeat=9):
                D=tree_matrix(shape,lengths[:3],lengths[3:])
                cert=constructive_tree(D)
                self.assertIsNotNone(cert)
                self.assertEqual(cert['topology'],kind)
                self.assertEqual(direct_quartet_classifier(D),kind)
                r=exact_search(row_signature(D),max_nodes=25000)
                self.assertTrue(r['complete'],(kind,lengths,r['states']))
                self.assertTrue(r['trees'])
                self.assertEqual({c['topology'] for c,_ in r['trees']},{kind})
                total+=1
        self.assertEqual(total,1024)

    def test_permuted_leaf_labels(self):
        D=tree_matrix(PATH,(8,4,6),(2,9,3,10,5,7))
        rng=random.Random(553)
        sig=row_signature(D)
        for _ in range(40):
            order=list(range(6));rng.shuffle(order)
            E=[[D[order[i]][order[j]] for j in range(6)] for i in range(6)]
            self.assertEqual(row_signature(E),sig)
            c=constructive_tree(E)
            self.assertTrue(c and c['topology']=='path')
            self.assertTrue(audit_tree_certificate(E,c,True))

    def test_non_additive_metric_ambiguity(self):
        A=[[0]*6 for _ in range(6)]
        cycle=[(0,1),(1,2),(2,3),(3,0)]
        cycle_canonical={tuple(sorted(edge)) for edge in cycle}
        for i,(u,v) in enumerate(cycle):
            A[u][v]=A[v][u]=100+(i%2)
        other=(edge for edge in combinations(range(6),2) if edge not in cycle_canonical)
        for val,(u,v) in enumerate(other,102):
            A[u][v]=A[v][u]=val
        B=[row.copy() for row in A]
        for u,v in cycle:
            B[u][v]=B[v][u]=201-A[u][v]
        self.assertEqual(row_signature(A),row_signature(B))
        self.assertFalse(any(all(A[i][j]==B[p[i]][p[j]] for i,j in combinations(range(6),2))
                             for p in permutations(range(6))))
        for C in (A,B):
            self.assertTrue(all(C[i][j]<=C[i][k]+C[k][j]
                                for i,j,k in product(range(6),repeat=3)))
            self.assertIsNone(constructive_tree(C))
            self.assertIsNone(direct_quartet_classifier(C))

    def test_bad_inputs_and_tamper(self):
        D=tree_matrix(STAR,(2,4,6),(1,3,5,7,9,11))
        cert=constructive_tree(D)
        self.assertTrue(audit_tree_certificate(D,cert,True))
        bad=dict(cert);bad['pendant_lengths']=(cert['pendant_lengths'][0]+1,*cert['pendant_lengths'][1:])
        self.assertFalse(audit_tree_certificate(D,bad,True))
        bad=dict(cert);bad['attachments']=(0,*cert['attachments'][1:])
        self.assertFalse(audit_tree_certificate(D,bad,True))
        bad=dict(cert);bad['core_edges']=((0,1),(0,2),(1,3))
        self.assertFalse(audit_tree_certificate(D,bad,True))
        rows=list(row_signature(D))
        badrows=[list(row) for row in rows]
        badrows[0][0]+=100
        with self.assertRaises(ValueError):exact_search(badrows)
        with self.assertRaises(ValueError):exact_search(rows,0)

    def test_strict_cap_is_not_negative_certificate(self):
        D=tree_matrix(STAR,(1,1,1),(1,1,1,1,1,1))
        truncated=exact_search(row_signature(D),max_nodes=1)
        self.assertFalse(truncated['complete'])


if __name__=='__main__':
    unittest.main(verbosity=2)
