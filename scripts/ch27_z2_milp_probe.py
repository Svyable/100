"""Optional SciPy/HiGHS B-floor MILP exploration for M074 z=2.

Solver infeasibility is NOT an exact proof certificate. All feasible witnesses
are independently checked against literal arc, digon and triangle semantics.
Usage: OPENBLAS_NUM_THREADS=1 python3 -m scripts.ch27_z2_milp_probe --check
"""
import argparse
import json
from collections import Counter
from functools import lru_cache
from itertools import combinations

from .ch27_z2_root import alphas, ks, classify, b_floors

@lru_cache(None)
def model(n):
    import numpy as np
    from scipy.sparse import lil_matrix
    arcs=[(i,j) for i in range(n) for j in range(n) if i!=j]
    idx={a:t for t,a in enumerate(arcs)}
    rows=[];lo=[];hi=[]
    def add(d,lower=-np.inf,upper=np.inf):
        rows.append(d);lo.append(lower);hi.append(upper)
    for i,j in combinations(range(n),2):
        add({idx[i,j]:1,idx[j,i]:1},upper=1)
    for i,j,k in combinations(range(n),3):
        add({idx[i,j]:1,idx[j,k]:1,idx[k,i]:1},upper=2)
        add({idx[i,k]:1,idx[k,j]:1,idx[j,i]:1},upper=2)
    for i in range(n):
        add({idx[i,j]:1 for j in range(n) if i!=j},lower=0)
    mat=lil_matrix((len(rows),len(arcs)))
    for r,d in enumerate(rows):
        for c,v in d.items():mat[r,c]=v
    return arcs,mat.tocsr(),np.array(lo),np.array(hi)

def solve_floor(f,time_limit=2):
    import numpy as np
    from scipy.optimize import milp, Bounds, LinearConstraint
    n=len(f);arcs,mat,lo,hi=model(n)
    lo=lo.copy();lo[-n:]=f
    r=milp(np.zeros(len(arcs)),integrality=np.ones(len(arcs)),
           bounds=Bounds(np.zeros(len(arcs)),np.ones(len(arcs))),
           constraints=LinearConstraint(mat,lo,hi),
           options={"time_limit":time_limit})
    if r.status==0:
        edges={(i,j) for (i,j),v in zip(arcs,r.x) if v>.5}
        assert all(not ((i,j) in edges and (j,i) in edges)
                   for i,j in combinations(range(n),2))
        assert all(not ((i,j) in edges and (j,k) in edges and (k,i) in edges)
                   and not ((i,k) in edges and (k,j) in edges and (j,i) in edges)
                   for i,j,k in combinations(range(n),3))
        assert all(sum((i,j) in edges for j in range(n))>=f[i]
                   for i in range(n))
    return r.status

def run():
    candidates=[(a,k) for a in alphas() for k in ks()
                if classify(a,k)=="relaxed_survivor"]
    floors=Counter(b_floors(a,k) for a,k in candidates)
    statuses={f:solve_floor(f) for f in floors}
    if any(s not in (0,2) for s in statuses.values()):
        raise RuntimeError("Unresolved MILP status; no count can be asserted")
    feasible=sum(count for f,count in floors.items() if statuses[f]==0)
    return {"relaxed_profiles":len(candidates),"distinct_B_floors":len(floors),
            "B_MILP_feasible":feasible,
            "B_MILP_infeasible_unproved":len(candidates)-feasible,
            "warning":"Solver infeasibility statuses are not exact certificates"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    r=run()
    if args.check:
        assert (r["relaxed_profiles"],r["distinct_B_floors"],
                r["B_MILP_feasible"],r["B_MILP_infeasible_unproved"])==(475,292,72,403)
    print(json.dumps(r,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
