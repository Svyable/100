"""Independent integer min-cut replay for the chorded-multitheta LP witness.

This uses no functions from m097_chorded_multitheta. It checks the
fractional degree equations, exact objective and all cuts via a separate
Stoer-Wagner global-min-cut algorithm. It is author-side cross-checking,
not an independent mathematical review. Claim #228.
"""
from itertools import combinations
import random


def witness(lengths):
    if len(lengths) < 2 or any(type(x) is not int or x < 2 for x in lengths):
        raise ValueError("need at least two paths of integer length >= 2")
    k = len(lengths)
    scale = k * (k - 1)
    graph = {0: {}, 1: {}}
    next_vertex = 2
    paths = []

    def add(a, b, capacity):
        if not capacity:
            return
        if a == b or capacity < 0:
            raise AssertionError("invalid weighted edge")
        graph[a][b] = graph[a].get(b, 0) + capacity
        graph[b][a] = graph[b].get(a, 0) + capacity

    for length in lengths:
        interior = list(range(next_vertex, next_vertex + length - 1))
        next_vertex += length - 1
        for vertex in interior:
            graph[vertex] = {}
        path = [0, *interior, 1]
        paths.append(path)
        for i, (a, b) in enumerate(zip(path, path[1:])):
            add(a, b, 2 * (k - 1) if i in (0, length - 1) else scale)

    for i, j in combinations(range(k), 2):
        add(paths[i][1], paths[j][1], k - 2)
        add(paths[i][-2], paths[j][-2], k - 2)
    return graph, scale, paths


def global_min_cut(graph):
    """Integer Stoer-Wagner algorithm; input is not modified."""
    weights = {v: dict(adj) for v, adj in graph.items()}
    active = list(weights)
    if len(active) < 2:
        raise ValueError("at least two vertices required")
    best = None
    while len(active) > 1:
        chosen_set = set()
        score = {v: 0 for v in active}
        previous = None
        for i in range(len(active)):
            chosen = max((v for v in active if v not in chosen_set),
                         key=lambda v: (score[v], -v))
            chosen_set.add(chosen)
            if i == len(active) - 1:
                best = score[chosen] if best is None else min(best, score[chosen])
                for neighbor, capacity in list(weights[chosen].items()):
                    if neighbor == previous:
                        continue
                    weights[previous][neighbor] = weights[previous].get(neighbor, 0) + capacity
                    weights[neighbor][previous] = weights[previous][neighbor]
                    del weights[neighbor][chosen]
                weights[previous].pop(chosen, None)
                del weights[chosen]
                active.remove(chosen)
                break
            previous = chosen
            for neighbor, capacity in weights[chosen].items():
                if neighbor not in chosen_set:
                    score[neighbor] += capacity
    return best


def brute_min_cut(graph):
    vertices = sorted(graph)
    root, others = vertices[0], vertices[1:]
    best = None
    for mask in range(1 << len(others)):
        left = {root} | {v for i, v in enumerate(others) if mask & (1 << i)}
        if len(left) == len(vertices):
            continue
        value = sum(w for u in left for v, w in graph[u].items() if v not in left)
        best = value if best is None else min(best, value)
    return best


def audit(lengths):
    graph, scale, paths = witness(lengths)
    assert all(sum(adj.values()) == 2 * scale for adj in graph.values())
    long_edges = {tuple(sorted((a, b))) for path in paths
                  for a, b in zip(path, path[1:])}
    cost = sum(w * (1 if (u, v) in long_edges else 2)
               for u, adj in graph.items() for v, w in adj.items() if u < v)
    assert cost == sum(lengths) * scale
    assert global_min_cut(graph) == 2 * scale
    return len(graph), scale


def self_test():
    rng = random.Random(9718)
    for n in range(2, 9):
        for _ in range(30):
            graph = {v: {} for v in range(n)}
            for u in range(n):
                for v in range(u + 1, n):
                    weight = rng.randrange(7)
                    if weight:
                        graph[u][v] = weight
                        graph[v][u] = weight
            assert global_min_cut(graph) == brute_min_cut(graph)
    cases = [(2, 2), (3, 3, 3), (2, 3, 3, 3, 3),
             (5, 7, 9, 11), (2,) * 12, (3,) * 13, (2,) * 20]
    return [audit(case) for case in cases]


if __name__ == "__main__":
    print(self_test())
