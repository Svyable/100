#!/usr/bin/env python3
"""Exact bounded induced-motif card-profile counterexamples for trees (M078).

No external dependencies. Graphs are tuples of neighbor sets; motifs are
canonicalized by exhaustive relabeling, not by a heuristic graph hash.
"""
from collections import Counter
from itertools import combinations, permutations
import argparse
import json


def spider(legs):
    assert len(legs) == 3 and all(x >= 1 for x in legs)
    n = 1 + sum(legs)
    g = [set() for _ in range(n)]
    j = 1
    for length in legs:
        prev = 0
        for _ in range(length):
            g[prev].add(j)
            g[j].add(prev)
            prev, j = j, j + 1
    return tuple(frozenset(x) for x in g)


def pair(k, extra=0):
    assert k >= 2 and extra >= 0
    L = max(3, 2*k-3)
    return spider((L, L, L+2+extra)), spider((L, L+1, L+1+extra))


def rooted_ball(g, root, radius):
    distance = {root: 0}
    frontier = [root]
    for depth in range(radius):
        following = []
        for v in frontier:
            for w in g[v]:
                if w not in distance:
                    distance[w] = depth+1
                    following.append(w)
        frontier = following
    def encode(v, parent):
        return '(' + ''.join(sorted(encode(w, v) for w in g[v]
                                   if w != parent and w in distance)) + ')'
    return encode(root, -1)


def ball_histogram(g, radius):
    return Counter(rooted_ball(g, v, radius) for v in range(len(g)))


def card_degree_signature(g):
    return Counter(tuple(sorted(len(g[w])-int(v in g[w])
                 for w in range(len(g)) if w != v)) for v in range(len(g)))


def canonical_maps(t):
    edges = list(combinations(range(t), 2))
    index = {e: i for i, e in enumerate(edges)}
    maps = []
    for p in permutations(range(t)):
        maps.append(tuple(index[tuple(sorted((p[a], p[b])))] for a,b in edges))
    return [min(sum(((mask>>i)&1)<<p[i] for i in range(len(edges)))
                for p in maps) for mask in range(1<<len(edges))]


def card_motif_signature(g, k):
    # Direct enumeration of disconnected as well as connected induced motifs.
    n = len(g)
    tables = {t: canonical_maps(t) for t in range(1,k+1)}
    out = Counter()
    for omitted in range(n):
        remaining = [v for v in range(n) if v != omitted]
        card = []
        for t in range(1,k+1):
            motifs = Counter()
            for subset in combinations(remaining,t):
                mask = 0
                for i,(a,b) in enumerate(combinations(subset,2)):
                    if b in g[a]: mask |= 1<<i
                motifs[tables[t][mask]] += 1
            card.append(tuple(sorted(motifs.items())))
        out[tuple(card)] += 1
    return out


def run_check(max_k=4):
    assert max_k in (2,3,4), 'larger k needs a separate computational budget'
    summary = []
    for k in range(2,max_k+1):
        g,h=pair(k)
        assert len(g)==3*max(3,2*k-3)+3
        assert ball_histogram(g,k-1)==ball_histogram(h,k-1)
        assert card_degree_signature(g)==card_degree_signature(h)
        a,b=card_motif_signature(g,k),card_motif_signature(h,k)
        assert a==b
        assert sum(a.values())==len(g)
        L=max(3,2*k-3)
        assert sorted((L,L,L+2))!=sorted((L,L+1,L+1))
        summary.append({'k':k,'n':len(g),'card_types':len(a),
                        'motif_card_equal':True,'rooted_ball_equal':True})
    small1=spider((1,3,5)); small2=spider((1,4,4))
    assert card_degree_signature(small1)==card_degree_signature(small2)
    assert ball_histogram(small1,1)==ball_histogram(small2,1)
    assert card_degree_signature(small1)!=card_degree_signature(spider((1,2,6)))
    return summary


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--check',action='store_true')
    p.add_argument('--max-k',type=int,default=4)
    a=p.parse_args()
    print(json.dumps(run_check(a.max_k),sort_keys=True))
