"""Second histogram-based necessary-profile sweep; no main checker calls."""
import unittest
from collections import Counter

def compositions(total,bins):
    if bins==1:
        yield (total,)
        return
    for x in range(total+1):
        for tail in compositions(total-x,bins-1):
            yield (x,)+tail

def expand(hist,start):
    return tuple(v for j,c in enumerate(hist) for v in [j+start]*c)

def independent_stage(a,k):
    m=sum(a);K=sum(k)
    if K<92-2*m:return "root"
    q=[sum(v>=j+2 for v in a) for j in range(8)]
    f=sorted((max(0,1+j-q[j]) for j in k),reverse=True)
    if any(sum(f[:s])>s*(19-s)//2 for s in range(1,11)):return "cap"
    if f[2]>7 or f[4]>6 or f[5]>5:return "small"
    missing=0
    for i,d in enumerate(a):
        peers=Counter(a[:i]+a[i+1:])
        rank=next(v for v in range(8,1,-1)
                  if sum(c for val,c in peers.items() if val>=v)>=d)
        missing+=max(0,d-rank)
    if K<92-2*m+missing:return "rank"
    if any(f[s-1]>=11-s and sum(f[:s])>s*(19-s)//2-2
           for s in range(4,11)):return "girth"
    if f[6]>=5 and sum(f[:7])>35:return "seven"
    if f[7]>=4 and sum(f[:8])>37:return "eight"
    if a.count(2)<3:return "three_low"
    if a in ((2,2,2,3,4,4,4,4,4),(2,2,2,3,3,3,3,3,8),
             (2,2,2,2,4,4,4,4,5),(2,2,2,2,4,4,4,4,4)):
        return "four"
    if a in ((2,2,2,2,3,3,3,4,8),(2,2,2,3,3,3,3,4,7)):
        return "budget"
    if a==(2,2,2,2,3,3,3,3,8) and k==(0,0,3,4,5,6,6,6,6,6):
        return "extremal"
    return "unresolved"

class TestIndependentSweep(unittest.TestCase):
    def test_full_histogram_sweep(self):
        aa=[expand(h,2) for h in compositions(9,7)
            if sum((i+2)*c for i,c in enumerate(h))<=29]
        kk=[(0,0)+expand(h,1) for h in compositions(8,7)]
        self.assertEqual((len(aa),len(kk)),(166,3003))
        count=Counter(independent_stage(a,k) for a in aa for k in kk)
        self.assertEqual((count["root"],count["cap"],count["small"],
                          count["rank"],count["girth"]),
                         (373024,82283,7959,33353,1404))
        self.assertEqual((count["seven"],count["eight"],count["three_low"],
                          count["four"],count["budget"],count["extremal"]),
                         (75,83,144,156,16,1))
        self.assertEqual(count["unresolved"],0)
        self.assertEqual(sum(count.values()),498498)

if __name__=="__main__":unittest.main()
