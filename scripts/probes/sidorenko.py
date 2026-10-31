"""M073 - Sidorenko's conjecture: falsifier search over every small host graph.

For each pattern H and every graph G on at most N vertices, compare the
homomorphism density t(H,G) with t(K2,G)^e(H) exactly (integer arithmetic).
The pattern list contains K_{5,5} minus a Hamiltonian cycle, commonly cited
as the smallest open case, alongside proven controls (C4, C6, K_{3,3}, P4).
Check side recounts every homomorphism number from the other bipartition side.
"""
from fractions import Fraction

from .core import digest, fraction_text, require
from .graphs import census, to_adjacency
from .homomorphisms import bipartite, count_from_side, sidorenko_holds

PROBE = {
    "id": "sidorenko",
    "problem_id": "M073",
    "title": "Sidorenko inequality for K_{5,5} minus C_10 and controls on every small host graph",
    "engines": ["graph_homomorphisms", "graph_census"],
    "frontier": ("Known for trees, even cycles, complete bipartite graphs, hypercubes and many "
                 "families; K_{5,5} minus a Hamiltonian cycle is commonly cited as the smallest open "
                 "case (check current literature). Finite hosts this small are not expected to refute it."),
    "levels": {"smoke": {"max_host": 5}, "deep": {"max_host": 7}},
}


def patterns():
    k55_c10 = [(i, j) for i in range(5) for j in range(5) if j not in (i, (i - 1) % 5)]
    return {
        "K55_minus_C10": bipartite(5, 5, k55_c10),
        "C4": bipartite(2, 2, [(0, 0), (0, 1), (1, 0), (1, 1)]),
        "C6": bipartite(3, 3, [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (0, 2)]),
        "K33": bipartite(3, 3, [(i, j) for i in range(3) for j in range(3)]),
        "P4": bipartite(2, 2, [(0, 0), (1, 0), (1, 1)]),
    }


def scope(params):
    return (f"t(H,G) >= t(K2,G)^e(H) for every graph G on 1..{params['max_host']} vertices and "
            "H in {K_{5,5} minus C_10, C4, C6, K_{3,3}, P4}.")


def search(params):
    out, holds = {}, True
    for name, H in patterns().items():
        e_h, v_h = len(H["edges"]), H["A"] + H["B"]
        rows, worst = [], None
        for n in range(1, params["max_host"] + 1):
            for code in census(n):
                adj = to_adjacency(n, code)
                e_g = sum(bin(a).count("1") for a in adj) // 2
                hom = count_from_side(H, n, adj, "A")
                ok = sidorenko_holds(hom, n, e_g, e_h, v_h)
                holds &= ok
                rows.append([n, code, hom])
                if e_g:
                    ratio = Fraction(hom * n ** (2 * e_h - v_h), (2 * e_g) ** e_h)
                    if worst is None or ratio < worst[0]:
                        worst = (ratio, n, code)
        out[name] = {"edges": H["edges"], "a": H["A"], "b": H["B"], "hosts": rows,
                     "min_ratio": fraction_text(worst[0]), "min_at": [worst[1], worst[2]]}
    return {
        "holds": holds,
        "summary": {name: {"hosts": len(v["hosts"]), "min_ratio": v["min_ratio"]} for name, v in out.items()}
                   | {"certificate_sha256": digest(out)},
        "certificate": out,
    }


def check(params, result):
    cert = result["certificate"]
    pats = patterns()
    require(set(cert) == set(pats), "pattern list changed")
    expected_hosts = [(n, c) for n in range(1, params["max_host"] + 1) for c in census(n)]
    for name, H in pats.items():
        data = cert[name]
        require(data["edges"] == [list(e) for e in H["edges"]] or data["edges"] == H["edges"],
                f"{name}: pattern edges differ")
        require([(r[0], r[1]) for r in data["hosts"]] == expected_hosts, f"{name}: host list incomplete")
        e_h, v_h = len(H["edges"]), H["A"] + H["B"]
        worst = None
        for n, code, hom in data["hosts"]:
            adj = to_adjacency(n, code)
            require(count_from_side(H, n, adj, "B") == hom, f"{name}: hom count wrong for host {n}/{code}")
            e_g = sum(bin(a).count("1") for a in adj) // 2
            require(sidorenko_holds(hom, n, e_g, e_h, v_h) or not result["holds"],
                    f"{name}: inequality fails on host {n}/{code}")
            if e_g:
                ratio = Fraction(hom * n ** (2 * e_h - v_h), (2 * e_g) ** e_h)
                worst = ratio if worst is None or ratio < worst else worst
        require(fraction_text(worst) == data["min_ratio"], f"{name}: minimum ratio mismatch")
    require(result["summary"]["certificate_sha256"] == digest(cert), "certificate hash mismatch")
