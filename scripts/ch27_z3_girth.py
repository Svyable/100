#!/usr/bin/env python3
"""Necessary integer z=3 CH27 audit, NOT a 27-vertex digraph census."""
import argparse
import json
from collections import Counter
from itertools import combinations_with_replacement

def alpha_profiles():
    return tuple(a for a in combinations_with_replacement(range(2,9),9)
                 if sum(a)<=29)

def k_profiles():
    return tuple((0,0,0)+k for k in combinations_with_replacement(range(1,8),7))

def forced_missing_pairs(alpha):
    """Each A-source hits a target no larger than its d-th-ranked peer."""
    if len(alpha)!=9 or any(type(x) is not int or x<2 or x>8 for x in alpha):
        raise ValueError("invalid nine-vertex A degree profile")
    return sum(max(0,d-sorted(alpha[:i]+alpha[i+1:],reverse=True)[d-1])
               for i,d in enumerate(alpha))

def c_to_a_capacity(alpha):
    low=alpha.count(2); high=9-low; universal=8 in alpha
    return sum(d-2 for d in alpha if d>2
               and not(low and universal and d==8)
               and d<=high-1-int(bool(low and universal)))

def floors(alpha,k):
    q={j:sum(a>=j+2 for a in alpha) for j in range(8)}
    return tuple(sorted((max(0,1+j-q[j]) for j in k),reverse=True))

def subset_capacity(f):
    return all(sum(f[:s])<=s*(19-s)//2 for s in range(1,11))

def old_local_girth(f):
    return f[2]<8 and f[4]<7 and f[5]<6

def new_subset_girth(f,missing_edges=2):
    return all(f[s-1]<11-s or sum(f[:s])<=s*(19-s)//2-missing_edges
               for s in range(4,11))

FIRST=((2,2,2,3,3,3,3,3,8),(0,0,0,5,5,6,6,6,6,6))
SECOND=((2,2,2,3,4,4,4,4,4),(0,0,0,2,3,4,5,6,7,7))

def classify(alpha,k,girth_missing=2,endpoints=True):
    m=sum(alpha);K=sum(k)
    if K<92-2*m:return "root_cut"
    f=floors(alpha,k)
    if not subset_capacity(f):return "B_capacity"
    if not old_local_girth(f):return "B_small_girth"
    if K<92-2*m+forced_missing_pairs(alpha):return "A_C_missing_cut"
    if not new_subset_girth(f,girth_missing):return "new_B_girth_deficit"
    if endpoints and (alpha,k)==FIRST:return "dominated_five_overflow"
    if endpoints and (alpha,k)==SECOND:return "five_high_sources_deficit"
    return "unresolved"

def audit(girth_missing=2,endpoints=True):
    counts=Counter();survivors=[]
    for a in alpha_profiles():
        for k in k_profiles():
            result=classify(a,k,girth_missing,endpoints)
            counts[result]+=1
            if result=="unresolved":survivors.append((a,k))
    return {"total_profiles":len(alpha_profiles())*len(k_profiles()),
            "alpha_profiles":len(alpha_profiles()),"k_profiles":len(k_profiles()),
            "stages":dict(sorted(counts.items())),"survivors":survivors,
            "scope":"Relaxed necessary sorted integer profiles; no graph census"}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    exact=audit()
    weak=audit(girth_missing=0,endpoints=False)
    no_endpoints=audit(endpoints=False)
    report={"exact":exact,"no_girth_survivors":len(weak["survivors"]),
            "two_structural_endpoints":no_endpoints["survivors"]}
    print(json.dumps(report,indent=2))
    if args.check:
        expected={"root_cut":253556,"B_capacity":22498,
                  "B_small_girth":2255,"A_C_missing_cut":6448,
                  "new_B_girth_deficit":97,"dominated_five_overflow":1,
                  "five_high_sources_deficit":1}
        if (exact["total_profiles"]!=284856 or exact["stages"]!=expected
            or exact["survivors"] or len(weak["survivors"])!=99
            or no_endpoints["survivors"]!=[FIRST,SECOND]):
            raise SystemExit("CH27 z=3 certificate drift")
if __name__=="__main__":main()
