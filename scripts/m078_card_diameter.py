"""Exact author-side audit for X-M078-CARD-DIAMETER, not independent review."""
import argparse
from collections import Counter, deque
from itertools import combinations, permutations
import json

def parameters(k,n):
    if not isinstance(k,int) or not isinstance(n,int) or k<3 or n<16*k:
        raise ValueError("require integers k>=3 and n>=16*k")
    L=2*k-3;h=L+4;A=2*h-1+(n-16*k)//3
    pairs=[((L,L+2),(L+1,L+1)),((L,L+3),(L+1,L+2)),
           ((L+1,L+3),(L+2,L+2))]
    return L,h,A,pairs[(n-16*k)%3]

def tree(k,n,variant):
    L,h,A,pairs=parameters(k,n)
    if variant not in (0,1):raise ValueError("variant")
    g=[set() for _ in range(n)];j=1;marks=[]
    for arm in range(3):
        p=0
        for d in range(1,A+1):
            g[p].add(j);g[j].add(p);p=j
            if arm<2 and d==h:marks.append(j)
            j+=1
    for mark,length in zip(marks,pairs[variant]):
        p=mark
        for _ in range(length):
            g[p].add(j);g[j].add(p);p=j;j+=1
    assert j==n
    return g

def validate(g):
    n=len(g)
    assert sum(map(len,g))==2*(n-1)
    assert Counter(map(len,g))==Counter({1:5,2:n-8,3:3})
    seen={0};todo=[0]
    while todo:
        for w in g[todo.pop()]:
            if w not in seen:seen.add(w);todo.append(w)
    assert len(seen)==n

def ball(g,v,r):
    def rec(u,p,depth):
        if depth==r:return ()
        return tuple(sorted(rec(w,u,depth+1) for w in g[u] if w!=p))
    return rec(v,-1,0)

def balls(g,r):
    return Counter(ball(g,v,r) for v in range(len(g)))

def diameter(g,omit):
    seen={omit};best=0
    def bfs(start):
        dist={start:0};q=deque([start]);far=start
        while q:
            u=q.popleft()
            if dist[u]>dist[far]:far=u
            for w in g[u]:
                if w!=omit and w not in dist:
                    dist[w]=dist[u]+1;q.append(w)
        return far,dist
    for v in range(len(g)):
        if v in seen:continue
        a,comp=bfs(v);b,ds=bfs(a);best=max(best,ds[b])
        seen.update(comp)
    return best

def degree_card(g,v):
    return tuple(sorted(len(g[u])-(v in g[u]) for u in range(len(g)) if u!=v))

def canonical(t):
    edges=list(combinations(range(t),2));index={e:i for i,e in enumerate(edges)}
    changes=[]
    for perm in permutations(range(t)):
        changes.append([index[tuple(sorted((perm[i],perm[j])))] for i,j in edges])
    return [min(sum(1<<change[i] for i in range(len(edges)) if mask>>i&1)
                for change in changes) for mask in range(1<<len(edges))]

def joint_signature(g,k):
    """Literal induced subsets in G; card counts via global minus incident."""
    n=len(g);tables={t:canonical(t) for t in range(1,k+1)}
    total=Counter();incident=[Counter() for _ in range(n)]
    for t in range(1,k+1):
        pairs=list(combinations(range(t),2))
        for vs in combinations(range(n),t):
            mask=sum(1<<i for i,(a,b) in enumerate(pairs) if vs[b] in g[vs[a]])
            key=(t,tables[t][mask]);total[key]+=1
            for v in vs:incident[v][key]+=1
    keys=sorted(total)
    return Counter((tuple(total[key]-incident[v][key] for key in keys),
                    degree_card(g,v),diameter(g,v)) for v in range(n))

def check(k,n,full=False):
    L,h,A,pairs=parameters(k,n);x,y=tree(k,n,0),tree(k,n,1)
    for g in (x,y):validate(g)
    r=k-1;bx,by=balls(x,r),balls(y,r)
    assert bx==by
    expected=sorted([3]+[9]*(r-1)+[5]*r+[n-(14*r-6)])
    assert sorted(bx.values())==expected
    for g in (x,y):
        assert Counter(diameter(g,v) for v in range(n))==Counter({A-1:1,2*A:n-1})
    assert Counter((degree_card(x,v),diameter(x,v)) for v in range(n))==Counter(
                   (degree_card(y,v),diameter(y,v)) for v in range(n))
    if full:assert joint_signature(x,k)==joint_signature(y,k)
    return {"k":k,"n":n,"A":A,"spur_pairs":pairs,"rooted_types":len(bx),
            "literal_motifs":full,"card_diameter_histogram":{str(A-1):1,str(2*A):n-1}}

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    p.add_argument("--json",action="store_true");args=p.parse_args()
    if not args.check:p.error("use --check")
    rows=[check(3,n,True) for n in range(48,52)]
    rows += [check(4,64,True),check(5,80,False)]
    if args.json:print(json.dumps(rows,sort_keys=True))
    else:
        for row in rows:print("PASS",row)

if __name__=="__main__":main()
