#!/usr/bin/env python3
"""Integer audit for CH(27,9) z<=3. Proof: proofs/M074_ZERO_K_THREE.md."""
import json
from collections import Counter
from itertools import combinations_with_replacement

def alpha_profiles():
    return tuple(a for a in combinations_with_replacement(range(2, 9), 9)
                 if sum(a) <= 29)

def z4_profiles():
    return tuple((0,)*4 + k for k in combinations_with_replacement(range(1, 8), 6))

def missing_pair_floor(alpha):
    if len(alpha) != 9 or any(type(a) is not int or not 2 <= a <= 8 for a in alpha):
        raise ValueError("invalid A profile")
    m = sum(alpha)
    if m > 29: raise ValueError("exceeds local arc cap")
    p = max(alpha)
    if p == 8: return 6
    if p == 7: return 5
    if p in (5, 6) or (p == 4 and m == 29): return 2
    return 0

def maximum_C_to_B(alpha):
    p = max(alpha)
    return 37 if p == 8 else 36 if p == 7 else 35

def new_cut_gap(alpha, k):
    if len(k) != 10 or any(type(x) is not int or not 0 <= x <= 7 for x in k):
        raise ValueError("invalid B profile")
    if k.count(0) != 4:
        raise ValueError("expected z=4")
    needed = 92-2*sum(alpha) + missing_pair_floor(alpha)
    return needed - min(sum(k), maximum_C_to_B(alpha))

def old_B_conditions(alpha, k):
    q = [sum(a >= x+2 for a in alpha) for x in k]
    f = sorted((max(0, 1+x-y) for x,y in zip(k,q)), reverse=True)
    return (all(sum(f[:s]) <= s*(19-s)//2 for s in range(1,11))
            and f[2]<8 and f[4]<7 and f[5]<6)

def audit():
    stage=Counter()
    by_degree=Counter()
    for a in alpha_profiles():
        m=sum(a)
        for k in z4_profiles():
            if sum(k)<92-2*m: stage["old_cut"]+=1
            elif not old_B_conditions(a,k): stage["old_B_capacity_or_girth"]+=1
            else:
                stage["formerly_unexcluded"]+=1
                if new_cut_gap(a,k)>0:
                    stage["newly_excluded"]+=1
                    by_degree[max(a)]+=1
                else: stage["still_unexcluded"]+=1
    return {"pairs":len(alpha_profiles())*len(z4_profiles()),
            "stages":dict(sorted(stage.items())),
            "new_exclusions_by_max_alpha":dict(sorted(by_degree.items())),
            "scope":"Relaxed integer profiles, not graphs"}

def main():
    r=audit()
    print(json.dumps(r,indent=2,sort_keys=True))
    assert r["pairs"]==153384
    assert r["stages"]=={"old_cut":149396,"old_B_capacity_or_girth":3693,
                         "formerly_unexcluded":295,"newly_excluded":295}
    assert r["new_exclusions_by_max_alpha"]=={6:33,7:102,8:160}

if __name__=="__main__": main()
