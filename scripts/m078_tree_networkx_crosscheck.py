#!/usr/bin/env python3
"""Optional independent-representation M078 cross-check (requires networkx>=3).

Unlike m078_tree_local_motifs.py, this uses NetworkX's graph-isomorphism
algorithm and graph atlas; it does not canonicalize adjacency bitmasks.
"""
from collections import Counter
from itertools import combinations
import networkx as nx
from m078_tree_local_motifs import pair


def signature(g, k=4):
    n=len(g)
    graph=nx.Graph()
    graph.add_nodes_from(range(n))
    graph.add_edges_from((u,v) for u in range(n) for v in g[u] if u<v)
    atlas=nx.graph_atlas_g()
    patterns={t:[h for h in atlas if h.number_of_nodes()==t] for t in range(1,k+1)}
    result=Counter()
    for omitted in range(n):
        card=[]
        for t in range(1,k+1):
            counts=[0]*len(patterns[t])
            for vertices in combinations((v for v in range(n) if v!=omitted),t):
                sub=graph.subgraph(vertices)
                for j,pat in enumerate(patterns[t]):
                    if nx.is_isomorphic(sub,pat):
                        counts[j]+=1
                        break
                else:
                    raise AssertionError('missing atlas isomorphism type')
            card.append(tuple(counts))
        result[tuple(card)]+=1
    return result


if __name__=='__main__':
    a,b=pair(4)
    assert signature(a)==signature(b)
    print('M078 NetworkX graph-isomorphism cross-check: k=4 n=18 match')
