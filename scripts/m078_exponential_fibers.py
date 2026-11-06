#!/usr/bin/env python3
"""M078: exact finite falsifiers for a proven all-orders local-deck fiber.

A check is not the proof. The research note proves the unbounded claim from
locality; this script independently enumerates small literal card motifs.
"""
from collections import Counter
from itertools import combinations
from math import comb
import argparse
import json


def fiber_tree(k, m, extras):
    """Subcubic path of m degree-three hubs with m+2 pendant legs.

    The first/last two slots attach to each endpoint hub, while the
    middle m-2 slots attach to the m-2 interior hubs. Every leg has
    length L+extra, L=2k-3; extra must be a nonnegative integer.
    """
    if k < 3 or m < 4 or len(extras) != m+2 or any(type(x) is not int or x < 0 for x in extras):
        raise ValueError("require k>=3, m>=4, and m+2 nonnegative integer extras")
    g = [set() for _ in range(m)]
    for i in range(m-1):
        g[i].add(i+1)
        g[i+1].add(i)
    L = 2*k-3
    def add_leg(hub, length):
        previous = hub
        for _ in range(length):
            node = len(g)
            g.append({previous})
            g[previous].add(node)
            previous = node
    add_leg(0, L + extras[0])
    add_leg(0, L + extras[1])
    for i in range(1, m-1):
        add_leg(i, L + extras[i+1])
    add_leg(m-1, L + extras[m])
    add_leg(m-1, L + extras[m+1])
    expected_n = m + (m+2)*L + sum(extras)
    assert len(g) == expected_n
    assert sum(len(a) for a in g) == 2*(len(g)-1)
    assert max(map(len,g)) == 3
    return tuple(frozenset(a) for a in g)


def family_tree(k, m, long_indices=(), endpoint_padding=0):
    """Binary-extra subfamily; internal hubs are indexed 1..m-2."""
    indices = tuple(long_indices)
    chosen = set(indices)
    if len(chosen) != len(indices) or any(i not in range(1, m-1) for i in chosen) or endpoint_padding < 0:
        raise ValueError("extras must attach to distinct internal hubs")
    extras = [0] * (m+2)
    extras[0] = endpoint_padding
    for i in chosen:
        extras[i+1] = 1
    return fiber_tree(k,m,extras)


def weak_compositions(total, slots):
    """All m+2 nonnegative integer tuples summing to total."""
    if slots == 1:
        yield (total,)
    else:
        for x in range(total+1):
            for suffix in weak_compositions(total-x,slots-1):
                yield (x,)+suffix


def rooted_ball(g, start, radius):
    distance = {start:0}
    frontier = [start]
    for d in range(radius):
        following=[]
        for v in frontier:
            for w in g[v]:
                if w not in distance:
                    distance[w] = d+1
                    following.append(w)
        frontier=following
    def encode(v, parent):
        return '(' + ''.join(sorted(encode(w,v) for w in g[v]
                    if w in distance and w != parent)) + ')'
    return encode(start,-1)


def balls(g, k):
    return Counter(rooted_ball(g, v, k-1) for v in range(len(g)))


def degree_cards(g):
    return Counter(tuple(sorted(len(g[v])-int(omitted in g[v])
               for v in range(len(g)) if v != omitted)) for omitted in range(len(g)))


def class_of_small_induced(g, nodes):
    """All unlabeled simple graphs on at most four vertices have distinct
    sorted degree sequences; this classification includes disconnected graphs.
    """
    return tuple(sorted(sum(w in g[v] for w in nodes if w != v) for v in nodes))


def direct_joint_cards(g, k):
    if not 1 <= k <= 4:
        raise ValueError("direct exhaustive enumeration supports only k<=4")
    hist = Counter()
    n = len(g)
    for omitted in range(n):
        rest = [v for v in range(n) if v != omitted]
        motifs=[]
        for t in range(1,k+1):
            counts = Counter(class_of_small_induced(g, nodes)
                             for nodes in combinations(rest, t))
            motifs.append(tuple(sorted(counts.items())))
        degree_card = tuple(sorted(len(g[v])-int(omitted in g[v]) for v in rest))
        hist[(tuple(motifs), degree_card)] += 1
    return hist


def spine_code(g):
    """Recover the multiset of pendant lengths from the graph itself, not
    from its construction labels; reverse the hub path to canonicalize.
    """
    hubs = [v for v in range(len(g)) if len(g[v]) == 3]
    hset = set(hubs)
    ends = [v for v in hubs if len(hset & g[v]) == 1]
    assert len(ends) == 2 and len(hubs) >= 4
    ordered, previous, current = [], None, ends[0]
    while current is not None:
        ordered.append(current)
        next_hubs = [w for w in g[current] if w in hset and w != previous]
        assert len(next_hubs) <= 1
        previous, current = current, (next_hubs[0] if next_hubs else None)
    assert len(ordered) == len(hubs)
    lengths=[]
    for hub in ordered:
        legs=[]
        for v in g[hub] - hset:
            prev, cur, length = hub, v, 1
            while len(g[cur]) == 2:
                nxt = next(w for w in g[cur] if w != prev)
                prev, cur, length = cur, nxt, length+1
            assert len(g[cur]) == 1
            legs.append(length)
        lengths.append(tuple(sorted(legs)))
    key=tuple(lengths)
    return min(key,key[::-1])


def check_small(k=3,m=6,t=2,deep=False):
    patterns=list(combinations(range(1,m-1),t))
    examples=[family_tree(k,m,p) for p in patterns]
    signatures=[balls(g,k) for g in examples]
    assert all(s==signatures[0] for s in signatures)
    assert all(degree_cards(g)==degree_cards(examples[0]) for g in examples)
    codes={spine_code(g) for g in examples}
    assert len(codes)>=comb(m-2,t)/2
    for g in examples:
        assert len(g)==m+(m+2)*(2*k-3)+t
    if deep:
        card_signatures=[direct_joint_cards(g,k) for g in examples]
        assert all(s==card_signatures[0] for s in card_signatures)
    return {'k':k,'m':m,'t':t,'n':len(examples[0]),
            'choices':len(patterns),'nonisomorphic':len(codes),
            'bound':f'{comb(m-2,t)}/2',
            'joint_direct_card_checked':deep,
            'rooted_balls_checked':True}


def quantitative_fiber(k=3, m=4, extra_total=4, direct=False):
    """Count literal isomorphism classes; does not assume the 8-to-1 bound."""
    codes=set()
    first_ball=None
    first_card=None
    choices=0
    for xs in weak_compositions(extra_total, m+2):
        g=fiber_tree(k,m,xs)
        current=balls(g,k)
        if first_ball is None:
            first_ball=current
        else:
            assert current==first_ball
        if direct:
            fingerprint=direct_joint_cards(g,k)
            if first_card is None:
                first_card=fingerprint
            else:
                assert fingerprint==first_card
        codes.add(spine_code(g))
        choices += 1
    assert choices==comb(extra_total+m+1,m+1)
    assert len(codes)*8 >= choices
    return {'k':k,'m':m,'extra_total':extra_total,
            'n':m+(m+2)*(2*k-3)+extra_total,
            'compositions':choices,'nonisomorphic':len(codes),
            'eight_to_one_lower_bound':f'{choices}/8',
            'all_direct_joint_checked':direct}


def run_checks(deep=False):
    # Three nonisomorphic witnesses from six configurations, compared
    # card-by-card including all disconnected 1-, 2- and 3-vertex motifs.
    first=check_small(3,6,2,True)
    # Radius-three result; check locality and (optionally) every 4-motif.
    second=check_small(4,5,1,deep)
    # Every target order can be extended without changing local profiles.
    x=family_tree(3,6,(1,3),endpoint_padding=7)
    y=family_tree(3,6,(2,3),endpoint_padding=7)
    assert balls(x,3)==balls(y,3)
    assert direct_joint_cards(x,3)==direct_joint_cards(y,3)
    assert spine_code(x)!=spine_code(y)
    # All on four vertices have unique sorted degree-sequence types;
    # an exact 64-graph crosscheck below verifies the classification.
    assert check_four_vertex_degree_classification()
    many=quantitative_fiber(3,4,4,False)
    return [first, second, many, {'padded_pair_n':len(x),'joint_cards':True,
                            'small_four_vertex_classes':11}]


def check_four_vertex_degree_classification():
    from itertools import permutations
    vertices=range(4)
    edges=list(combinations(vertices,2))
    seen={}
    for bits in range(64):
        deg=tuple(sorted(sum(bool(bits & (1<<i))
                  for i,e in enumerate(edges) if v in e) for v in vertices))
        adjacency=frozenset(edges[i] for i in range(6) if bits&(1<<i))
        code=min(tuple(sorted(tuple(sorted((p[a],p[b]))) for a,b in adjacency))
                 for p in permutations(vertices))
        if deg in seen and seen[deg]!=code:
            return False
        seen[deg]=code
    return len(seen)==11


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--deep',action='store_true',help='also enumerate every four-vertex card motif')
    args=parser.parse_args()
    print(json.dumps(run_checks(args.deep),sort_keys=True,indent=2))
