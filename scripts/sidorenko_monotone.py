#!/usr/bin/env python3
"""Certified wedge-pair bound for unequal-mass ordered two-block M073 graphons.

Mathematics: Harris product-measure association (known), plus a concrete
pairing of the 66 pinned H edges into 33 adjacent edge-pairs. This is a
restricted quantitative result, not a general Sidorenko theorem.
"""
from __future__ import annotations
import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import sidorenko_twoblock as old

ROOT = Path(__file__).resolve().parents[1]
WITNESS = ROOT / "data/reference/m073_wedge_cover.json"


def source_edges(faces=None):
    if faces is None:
        faces = old.read_faces()
    return tuple(sorted((p, 13 + i) for i, face in enumerate(faces) for p in face))


def construct_pairing(n, edges):
    """Independent construction: pair free edges in postorder of BFS tree.

    Parent edges are reserved until the vertex has an odd number of other
    unpaired edges. At the root parity is necessarily even if |E| is even.
    """
    es = tuple(sorted(tuple(sorted(e)) for e in edges))
    if len(set(es)) != len(es) or any(
            len(e) != 2 or e[0] == e[1] or e[0] < 0 or e[1] >= n for e in es):
        raise ValueError("simple graph with in-range edges needed")
    if n < 1 or len(es) % 2:
        raise ValueError("even edge count and nonempty graph needed")
    adj = [set() for _ in range(n)]
    for u, v in es:
        adj[u].add(v)
        adj[v].add(u)
    parent = {0: None}
    order = [0]
    for v in order:
        for x in sorted(adj[v]):
            if x not in parent:
                parent[x] = v
                order.append(x)
    if len(order) != n:
        raise ValueError("graph must be connected")
    used = set()
    pairs = []
    for v in reversed(order):
        pe = tuple(sorted((v, parent[v]))) if parent[v] is not None else None
        free = sorted(e for e in es if v in e and e not in used and e != pe)
        if len(free) % 2:
            if pe is None or pe in used:
                raise AssertionError("root odd or reserved edge already paired")
            free.append(pe)
        for i in range(0, len(free), 2):
            e1, e2 = free[i:i+2]
            if len({e1, e2}) != 2 or e1 in used or e2 in used:
                raise AssertionError("double assignment")
            used.update((e1, e2))
            pairs.append([v, [list(e1), list(e2)]])
    if used != set(es) or len(pairs)*2 != len(es):
        raise AssertionError("unpaired edges")
    return sorted(pairs, key=lambda t: (t[0], t[1]))


def verify_pairing(data, edges=None, n=35):
    """Independent witness validation, not relying on the pairing algorithm."""
    es = source_edges() if edges is None else tuple(edges)
    if (data.get("problem_id") != "M073" or data.get("vertices") != n
            or data.get("edges") != len(es) or
            data.get("source_faces_sha256") != old.FACES_SHA256):
        raise ValueError("witness metadata or source digest mismatch")
    seen = Counter()
    pairs = data.get("wedges")
    if not isinstance(pairs, list) or len(pairs)*2 != len(es):
        raise ValueError("wrong number of wedges")
    for item in pairs:
        if (not isinstance(item,list) or len(item)!=2 or type(item[0]) is not int
                or not 0<=item[0]<n or not isinstance(item[1], list)
                or len(item[1])!=2):
            raise ValueError("invalid wedge record")
        center, pair = item
        adjacent = []
        for e in pair:
            if (not isinstance(e,list) or len(e)!=2 or
                    any(type(v) is not int or not 0<=v<n for v in e)
                    or e[0]>=e[1] or center not in e):
                raise ValueError("edge does not meet wedge center")
            adjacent.append(tuple(e))
        if adjacent[0] == adjacent[1]:
            raise ValueError("duplicate edges in a wedge")
        seen.update(adjacent)
    if seen != Counter(es):
        raise ValueError("wedge multiset != source incidence edge multiset")
    return len(pairs)


def read_witness(path=WITNESS):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    verify_pairing(data)
    return data


def validate_weights(a, b, c, d, mass0, mass_d):
    if any(type(v) is not int for v in (a,b,c,d,mass0,mass_d)):
        raise ValueError("weights/masses must have exact integer numerators")
    if d <= 0 or mass_d <= 0 or not 0<=mass0<=mass_d:
        raise ValueError("probabilities outside the permitted range")
    if not all(0<=v<=d for v in (a,b,c)):
        raise ValueError("graphon entries outside [0,1]")
    if not (a>=b>=c or c>=b>=a):
        raise ValueError("ordered (monotone) block weights required")


def face_numerator(faces, a, b, c, mass0, mass_d, points=13):
    """Integer numerator of t(H,W), denominator mass_d^35*d^66.

    This method sums over point labels first and integrates each face
    separately. It does not use the 33-wedge certificate.
    """
    P, Q = mass0, mass_d
    mu = (P, Q-P)
    W = ((a,b),(b,c))
    tables = []
    for face in faces:
        table = []
        for x0,x1,x2 in product(range(2),repeat=3):
            table.append(sum(mu[y]*W[x0][y]*W[x1][y]*W[x2][y]
                             for y in (0,1)))
        tables.append(table)
    result = 0
    for mask in range(1 << points):
        term = 1
        for i in range(points):
            term *= mu[(mask >> i)&1]
        if not term:
            continue
        for (u,v,w),table in zip(faces,tables):
            ind = (((mask >> u)&1)*4 + ((mask>>v)&1)*2 + ((mask>>w)&1))
            term *= table[ind]
            if not term:
                break
        result += term
    return result


def edge_numerator(n, edges, a,b,c,mass0,mass_d):
    """Independent 35-variable factor elimination, edges and unary masses."""
    mu=(mass0,mass_d-mass0)
    W=((a,b),(b,c))
    factors=[((v,),mu) for v in range(n)]
    for u,v in edges:
        factors.append(((u,v),tuple(W[x][y] for x in (0,1) for y in (0,1))))
    for vertex in range(n):
        selected=[f for f in factors if vertex in f[0]]
        factors=[f for f in factors if vertex not in f[0]]
        other=tuple(sorted({x for scope,_ in selected for x in scope if x!=vertex}))
        out=[]
        for values in product((0,1),repeat=len(other)):
            assignment=dict(zip(other,values))
            total=0
            for choice in (0,1):
                assignment[vertex]=choice
                prod_value=1
                for scope,table in selected:
                    ix=0
                    for var in scope:
                        ix=2*ix+assignment[var]
                    prod_value*=table[ix]
                    if not prod_value:
                        break
                total+=prod_value
            out.append(total)
        factors.append((other,tuple(out)))
    if any(scope for scope,_ in factors):
        raise AssertionError("failed to eliminate all variables")
    value=1
    for scope,table in factors:
        value*=table[0]
    return value


def compare(a,b,c,d=4,mass0=1,mass_d=2,independent=False):
    """Exact inequality after clearing graphon probability denominators."""
    validate_weights(a,b,c,d,mass0,mass_d)
    faces=old.read_faces()
    edges=source_edges(faces)
    T=face_numerator(faces,a,b,c,mass0,mass_d)
    if independent and T!=edge_numerator(35,edges,a,b,c,mass0,mass_d):
        raise AssertionError("independent face-vs-edge hom numerator mismatch")
    P,Q=mass0,mass_d
    # wedge density: E d(X)^2
    B=P*(P*a+(Q-P)*b)**2+(Q-P)*(P*b+(Q-P)*c)**2
    # t(H,W) = T/(Q^35 d^66)
    # (E d(X)^2)^33 = B^33/(Q^99 d^66)
    L=T*Q**64
    R=B**33
    if L<R:
        raise AssertionError("33-wedge quantitative bound violated")
    p_n=P*P*a+2*P*(Q-P)*b+(Q-P)*(Q-P)*c
    degree_diff=P*(a-b)+(Q-P)*(b-c)
    var_n=P*(Q-P)*degree_diff**2
    # p= p_n/(Q^2 d), V=var_n/(Q^4 d^2):
    # p^2+V = (p_n^2+var_n)/(Q^4 d^2);
    # B/(Q^3 d^2) => B*Q = p_n^2+var_n.
    if B*Q!=p_n*p_n+var_n:
        raise AssertionError("covariance normalization drift")
    # strict if nondegenerate class masses and nonconstant monotone matrix
    strict=(0<P<Q and a!=c)
    if (L>R) != strict:
        raise AssertionError("strictness claim failed for rational test")
    return {"a":a,"b":b,"c":c,"denominator":d,"mass0":P,"mass_denominator":Q,
            "hom_numerator":T,"density_gap_numerator":L-R,
            "strict":strict}


def audit():
    wedges=read_witness()
    if construct_pairing(35,source_edges())!=wedges["wedges"]:
        raise AssertionError("witness does not reproduce independently")
    cases=[]
    # Four distinct masses and two separate monotone cones; include
    # degenerate q endpoints, sparse 0 and maximal 1 weights.
    for P,Q in ((0,2),(1,2),(2,2),(1,3),(2,3)):
        for a,b,c in product((0,1,2),repeat=3):
            if a>=b>=c or c>=b>=a:
                cases.append(compare(a,b,c,2,P,Q, independent=(a,b,c,P,Q) in {
                    (2,1,0,1,2),(0,1,2,1,3),(1,1,1,2,3),(2,1,0,0,2)
                }))
    return {
        "schema":"svyable.m073.monotone2-wedge.v1",
        "vertices":35,"edges":66,"wedges":33,
        "source_faces_sha256":old.FACES_SHA256,
        "grid_cases":len(cases),
        "grid_strict":sum(r["strict"] for r in cases),
        "grid_zero_gap":sum(r["density_gap_numerator"]==0 for r in cases),
        "independent_full_graph_recounts":4,
        "strictness_witness": [read_witness()["wedges"][0], read_witness()["wedges"][1]],
        "statement":"t(H,W) >= (p^2 + q(1-q)*(q*(a-b)+(1-q)*(b-c))^2)^33",
        "domain":"q,a,b,c in [0,1], W=[[a,b],[b,c]], a>=b>=c or c>=b>=a",
        "boundary":"Harris product-association and wedge pairing; not all 2x2 graphons or full Sidorenko, no external novelty or independent reviewer",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check",action="store_true")
    p.add_argument("--json",action="store_true")
    args=p.parse_args()
    report=audit()
    if args.check and (report["grid_cases"] != 85 or report["wedges"] !=33):
        raise SystemExit("M073 monotone regression count drift")
    if args.json or args.check:
        print(json.dumps(report,indent=2,sort_keys=True))
    else:
        print(f"M073 monotone two-block bound: {report['wedges']} wedges, {report['grid_cases']} exact cases")


if __name__=="__main__":
    main()
