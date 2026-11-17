"""Independent weighted-skeleton census for M078 three-hub leaf profiles.

Usage: python3 research/m078_three_hub_independent.py 5
Scope: five leaves, three degree-three hubs, all seven lengths in [1, bound].
No graph reconstruction theorem or independent mathematical review is claimed.
"""
from itertools import combinations_with_replacement, product
from collections import defaultdict
import sys

def canonical(a,b,c,e,f,d,g):
    left=(a,b,d)
    right=(e,f,g)
    if right<left:
        left,right=right,left
    return left+(c,)+right

def signature(p):
    a,b,d,c,e,f,g=p
    edges=((0,5,a),(1,5,b),(5,6,d),(2,6,c),(6,7,g),(3,7,e),(4,7,f))
    adj=[[] for _ in range(8)]
    for u,v,w in edges:
        adj[u].append((v,w))
        adj[v].append((u,w))
    profiles=[]
    for leaf in range(5):
        distances={leaf:0}
        stack=[leaf]
        while stack:
            u=stack.pop()
            for v,w in adj[u]:
                if v not in distances:
                    distances[v]=distances[u]+w
                    stack.append(v)
        counts=defaultdict(int)
        for v,dd in distances.items():
            if v!=leaf:
                counts[dd]+=1
        for u,v,w in edges:
            du,dv=distances[u],distances[v]
            for j in range(1,w):
                counts[min(du+j,dv+w-j)]+=1
        profiles.append(tuple(counts[k] for k in range(1,max(counts)+1)))
    return tuple(sorted(profiles))

def census(bound):
    if bound<1:
        raise ValueError("bound must be positive")
    seen={}
    canonical_seen=set()
    classes=0
    for a,b in combinations_with_replacement(range(1,bound+1),2):
        for e,f in combinations_with_replacement(range(1,bound+1),2):
            for c,d,g in product(range(1,bound+1),repeat=3):
                p=canonical(a,b,c,e,f,d,g)
                if p in canonical_seen:
                    continue
                canonical_seen.add(p)
                s=signature(p)
                if s in seen and seen[s]!=p:
                    return dict(bound=bound,classes=classes+1,collision=(seen[s],p))
                seen[s]=p
                classes+=1
    return dict(bound=bound,classes=classes,distinct_signatures=len(seen),collision=None)

if __name__=="__main__":
    print(census(int(sys.argv[1]) if len(sys.argv)>1 else 5))
