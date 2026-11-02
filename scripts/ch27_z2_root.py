"""Exact relaxed integer-profile audit for CH(27,9) indegree-ten z=2 root.

This does not enumerate 27-vertex digraphs or certify MILP infeasibility.
See research/M074_Z2_ROOT.md for the elementary forbidden-profile proof.
"""
import argparse
import json
from collections import Counter
from itertools import combinations, combinations_with_replacement, product

P1=(2,2,2,3,4,4,4,4,4)
P2=(2,2,2,3,3,3,3,3,8)
P3=(2,2,2,2,4,4,4,4,5)
P4=(2,2,2,2,4,4,4,4,4)
FORBIDDEN=(P1,P2,P3,P4)
Q1=(2,2,2,2,3,3,3,4,8)
Q2=(2,2,2,3,3,3,3,4,7)
Q3=(2,2,2,2,3,3,3,3,8)
LAST_K=(0,0,3,4,5,6,6,6,6,6)

def alphas():
    return (a for a in combinations_with_replacement(range(2,9),9) if sum(a)<=29)

def ks():
    return ((0,0)+k for k in combinations_with_replacement(range(1,8),8))

def rank_deficit(a):
    return sum(max(0,d-sorted(a[:i]+a[i+1:],reverse=True)[d-1])
               for i,d in enumerate(a))

def b_floors(a,k):
    q=[sum(d>=j+2 for d in a) for j in range(8)]
    return tuple(sorted((max(0,1+j-q[j]) for j in k),reverse=True))

def classify(a,k):
    m,K=sum(a),sum(k)
    if K<92-2*m: return "root_cut"
    f=b_floors(a,k)
    if any(sum(f[:s])>s*(19-s)//2 for s in range(1,11)): return "B_capacity"
    if f[2]>=8 or f[4]>=7 or f[5]>=6: return "B_small_girth"
    if K<92-2*m+rank_deficit(a): return "A_C_rank_deficit"
    if any(f[s-1]>=11-s and sum(f[:s])>s*(19-s)//2-2 for s in range(4,11)):
        return "B_two_missing_pairs"
    return "relaxed_survivor"

def final_classify(a,k):
    """Additional exact necessary filters; imports pending nine-vertex three-low lemma."""
    f=b_floors(a,k)
    # Seven-vertex min-outdegree-two orientations have exactly 14 arcs.
    if f[6]>=5 and sum(f[:7])>35: return "seven_vertex_14_arc_cap"
    # Eight-vertex min-outdegree-two orientations have at most 21 arcs.
    if f[7]>=4 and sum(f[:8])>37: return "eight_vertex_21_arc_cap"
    if a.count(2)<3: return "conditional_three_low"
    if a in FORBIDDEN: return "four_forbidden_profiles"
    if a in (Q1,Q2): return "final_indegree_budget"
    if a==Q3 and k==LAST_K: return "eight_vertex_26_arc_extremal"
    return "unresolved"

def audit():
    counts=Counter();patterns=Counter();final=Counter()
    for a in alphas():
        for k in ks():
            stage=classify(a,k)
            counts[stage]+=1
            if stage=="relaxed_survivor":
                patterns[a]+=1
                final[final_classify(a,k)]+=1
    three={a:n for a,n in patterns.items() if a.count(2)>=3}
    forbidden={a:three.get(a,0) for a in FORBIDDEN}
    return counts,patterns,three,forbidden,final

def directed_four_cycle_control():
    pairs=list(combinations(range(4),2));good=0
    for values in product((-1,0,1),repeat=6):
        arcs=set()
        for (i,j),value in zip(pairs,values):
            if value==1:arcs.add((i,j))
            elif value==-1:arcs.add((j,i))
        if any(sum((i,j) in arcs for j in range(4))<1 for i in range(4)):continue
        if any((i,j) in arcs and (j,k) in arcs and (k,i) in arcs
               for i in range(4) for j in range(4) for k in range(4)
               if len({i,j,k})==3):continue
        good+=1
        if len(arcs)!=4 or any(sum((i,j) in arcs for j in range(4))!=1 for i in range(4)):
            raise AssertionError(("four-cycle lemma falsified",arcs))
    return good

def run():
    counts,patterns,three,forbidden,final=audit()
    return {
        "total_profiles":166*3003,
        "stages":dict(sorted(counts.items())),
        "relaxed_survivors":sum(patterns.values()),
        "after_conditional_three_low":sum(three.values()),
        "excluded_by_four_forbidden_profiles":sum(forbidden.values()),
        "after_both_gates":sum(three.values())-sum(forbidden.values()),
        "forbidden_multiplicities":{str(a):n for a,n in forbidden.items()},
        "four_cycle_labelled_controls":directed_four_cycle_control(),
        "final_stages":dict(sorted(final.items())),
        "boundary":"necessary integer profiles only; no 27-vertex graph census",
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check",action="store_true")
    p.add_argument("--json",action="store_true")
    args=p.parse_args()
    result=run()
    if args.check:
        assert result["stages"]=={
            "root_cut":373024,"B_capacity":82283,"B_small_girth":7959,
            "A_C_rank_deficit":33353,"B_two_missing_pairs":1404,
            "relaxed_survivor":475}
        assert result["after_conditional_three_low"]==287
        assert result["excluded_by_four_forbidden_profiles"]==226
        assert result["after_both_gates"]==61
        assert result["four_cycle_labelled_controls"]==6
        assert result["final_stages"]=={
            "seven_vertex_14_arc_cap":75,
            "eight_vertex_21_arc_cap":83,
            "conditional_three_low":144,
            "four_forbidden_profiles":156,
            "final_indegree_budget":16,
            "eight_vertex_26_arc_extremal":1}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
