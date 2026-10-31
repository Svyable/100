#!/usr/bin/env python3
"""Independently verify directed short-cycle witnesses and exhaustive tiny cases.

For a finite simple loopless digraph D, the Caccetta-Haggkvist assertion says
minimum outdegree >= r>0 forces a directed cycle of length <= ceil(n/r).
This tool verifies only finite inputs or exhaustive n<=4; it does NOT solve
the general conjecture.
"""
import argparse
from itertools import product
import json


def validate_digraph(n, edges):
    if type(n) is not int or not 2 <= n <= 128:
        raise ValueError("2 <= n <= 128 is required")
    if not isinstance(edges, list):
        raise ValueError("edges must be a list")
    adj = [0] * n
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError("edge must be [u,v]")
        u, v = edge
        if type(u) is not int or type(v) is not int or not (0 <= u < n and 0 <= v < n):
            raise ValueError("invalid vertex")
        if u == v or adj[u] & (1 << v):
            raise ValueError("loops and duplicate arcs are forbidden")
        adj[u] |= 1 << v
    return adj


def directed_girth(adj):
    """Exact directed girth by BFS from each vertex; return None if acyclic."""
    n = len(adj)
    best = n + 1
    for root in range(n):
        dist = [-1] * n
        dist[root] = 0
        queue = [root]
        for u in queue:
            if dist[u] + 1 >= best:
                continue
            neighbors = adj[u]
            while neighbors:
                bit = neighbors & -neighbors
                neighbors ^= bit
                v = bit.bit_length() - 1
                if v == root:
                    best = min(best, dist[u] + 1)
                elif dist[v] == -1:
                    dist[v] = dist[u] + 1
                    queue.append(v)
    return None if best == n + 1 else best


def check(n, edges, r):
    adj = validate_digraph(n, edges)
    if type(r) is not int or r < 1 or r >= n:
        raise ValueError("require 1 <= r < n")
    degrees = [row.bit_count() for row in adj]
    min_degree = min(degrees)
    bound = (n + r - 1) // r
    girth = directed_girth(adj)
    return {
        "min_outdegree": min_degree,
        "girth": girth,
        "bound": bound,
        "hypothesis_met": min_degree >= r,
        "counterexample": min_degree >= r and (girth is None or girth > bound),
    }


def exhaustive(n):
    if type(n) is not int or not 2 <= n <= 4:
        raise ValueError("exhaustive n restricted to 2..4")
    arcs = [(u,v) for u in range(n) for v in range(n) if u != v]
    valid = 0
    cases = 1 << len(arcs)
    for coloring in range(cases):
        edges = [list(arc) for i,arc in enumerate(arcs) if coloring & (1 << i)]
        adj = validate_digraph(n,edges)
        minimum = min(row.bit_count() for row in adj)
        if not minimum:
            continue
        girth = directed_girth(adj)
        valid += 1
        for r in range(1,minimum+1):
            if girth is None or girth > (n+r-1)//r:
                raise RuntimeError(f"potential counterexample n={n} r={r} arcs={edges}")
    return cases,valid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd",required=True)
    enum = sub.add_parser("exhaustive")
    enum.add_argument("--n",type=int,required=True)
    single = sub.add_parser("check")
    single.add_argument("certificate")
    single.add_argument("--r",type=int,required=True)
    args = parser.parse_args()
    try:
        if args.cmd == "exhaustive":
            total,eligible=exhaustive(args.n)
            print(f"PASS: checked {total} loopless digraphs, "
                  f"{eligible} with positive min outdegree, all r<=minimum")
        else:
            with open(args.certificate,encoding="utf-8") as stream:
                data=json.load(stream)
            if data.get("format")!="svyable.digraph.arcs.v1":
                raise ValueError("unrecognized digraph certificate")
            result=check(data["n"],data["arcs"],args.r)
            print(json.dumps(result,sort_keys=True))
            if result["counterexample"]:
                return 1
        return 0
    except (OSError,ValueError,TypeError,KeyError) as error:
        parser.error(str(error))


if __name__=="__main__":
    raise SystemExit(main())
