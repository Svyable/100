"""M048 - Alperin's weight conjecture (global form) on small groups, every prime.

For a finite group G and a prime p the conjecture states l(G) = w(G), where
l(G) is the number of irreducible p-Brauer characters, which equals the number of
p-regular conjugacy classes (Brauer), and w(G) is the number of G-classes of
p-weights (Q, phi): Q is a p-radical subgroup (Q = O_p(N_G(Q))) and phi is an
irreducible character of N_G(Q)/Q of p-defect zero. So w(G) is the sum over radical
Q up to conjugacy of the number of degrees d of N_G(Q)/Q with d_p = |N_G(Q)/Q|_p.

Search side: Sylow subgroup by Cauchy steps, all its subgroups, G-conjugacy classes,
radical test as Q = core of a Sylow subgroup of N_G(Q), character degrees by Dixon's
method. Check side: re-verifies the p-regular classes (pairwise non-conjugate,
centraliser-orbit sizes summing to the number of p-regular elements), re-enumerates
the Sylow subgroup's subgroups from all small generating sets, decides radicality by
a different criterion (no N-class of x with x^p in Q generates a larger normal
p-subgroup), and recomputes every degree list with a different prime.
"""
from itertools import combinations

from . import fields
from .core import digest, require
from .groups_cert import (FiniteGroup, character_degrees, closure, compose, cycle, element_order, generating_set,
                     inverse, p_part, prime_factors)

PROBE = {
    "id": "alperin_weights",
    "problem_id": "M048",
    "title": "Alperin's weight conjecture l(G) = w(G) for small groups and every prime dividing |G|",
    "engines": ["group_characters"],
    "frontier": ("Known: proved for p-solvable groups (Okuyama; Isaacs-Navarro), symmetric groups and GL(n,q) "
                 "(Alperin-Fong 1990), many sporadic and Lie-type groups, and reduced to an inductive "
                 "condition on simple groups (Navarro-Tiep 2011). Every group here is a known case."),
    "levels": {
        "smoke": {"groups": ["S3", "A4", "S4", "A5", "S5", "PSL(2,7)"]},
        "deep": {"groups": ["S3", "A4", "S4", "A5", "S5", "PSL(2,7)", "GL(2,3)", "A6", "S6", "PSL(2,8)",
                            "PSL(2,11)", "PSL(2,13)", "A7", "S7", "M11"]},
    },
}


def _sym(n):
    return [cycle(n, (0, 1)), cycle(n, tuple(range(n)))]


def _alt(n):
    return [cycle(n, (0, 1, 2)), cycle(n, tuple(range(n))) if n % 2 else cycle(n, tuple(range(1, n)))]


def _psl2_prime(q):
    """PSL(2,q) on the projective line {0..q-1, inf=q}: x -> x+1 and x -> -1/x."""
    t = tuple([(x + 1) % q for x in range(q)] + [q])
    s = tuple([q] + [(-pow(x, q - 2, q)) % q for x in range(1, q)] + [0])
    return [t, s]


def _psl2_8():
    """SL(2,8) on the projective line over GF(8): all translations and x -> 1/x generate it."""
    F = fields.GF(8)
    inf = 8
    gens = [tuple([F.add(x, a) for x in range(8)] + [inf]) for a in (1, 2, 4)]
    gens.append(tuple([inf] + [F.inv(x) for x in range(1, 8)] + [0]))
    return gens


def _gl2_3():
    """GL(2,3) acting on the 8 nonzero vectors of GF(3)^2."""
    vecs = [(a, b) for a in range(3) for b in range(3) if (a, b) != (0, 0)]
    idx = {v: i for i, v in enumerate(vecs)}

    def act(m):
        return tuple(idx[((m[0][0] * a + m[0][1] * b) % 3, (m[1][0] * a + m[1][1] * b) % 3)] for a, b in vecs)
    return [act(((1, 1), (0, 1))), act(((1, 0), (1, 1))), act(((2, 0), (0, 1)))]


GROUPS = {
    "S3": (_sym(3), 6), "A4": (_alt(4), 12), "S4": (_sym(4), 24), "A5": (_alt(5), 60), "S5": (_sym(5), 120),
    "PSL(2,7)": (_psl2_prime(7), 168), "GL(2,3)": (_gl2_3(), 48), "A6": (_alt(6), 360), "S6": (_sym(6), 720),
    "PSL(2,8)": (_psl2_8(), 504), "PSL(2,11)": (_psl2_prime(11), 660), "PSL(2,13)": (_psl2_prime(13), 1092),
    "A7": (_alt(7), 2520), "S7": (_sym(7), 5040),
    # Mathieu group M11 on 11 points (ATLAS generators, shifted to 0-based points)
    "M11": ([cycle(11, tuple(range(11))), cycle(11, (2, 6, 10, 7), (3, 9, 4, 5))], 7920),
}


def scope(params):
    return ("l(G) = w(G) (p-regular classes = conjugacy classes of p-weights) for G in {"
            + ", ".join(params["groups"]) + "} and every prime p dividing |G|.")


# ------------------------------------------------------------------ helpers

def _gen_closure(gens, e):
    return frozenset(closure(list(gens), e))


def normaliser(G_elems, H, gens_H):
    return [g for g in G_elems if all(compose(compose(g, h), inverse(g)) in H for h in gens_H)]


def sylow(elems, p, e):
    """A Sylow p-subgroup of the group with element list `elems`, by repeated Cauchy steps."""
    target = p_part(len(elems), p)
    R, gens = frozenset([e]), []
    while len(R) < target:
        N = normaliser(elems, R, gens or [e])
        for g in N:
            if g in R:
                continue
            y = g
            for _ in range(p - 1):
                y = compose(y, g)
            if y in R:
                gens = gens + [g]
                R = _gen_closure(gens, e)
                break
        else:
            raise ValueError("no Cauchy step available")
    return R, gens


def subgroups_by_extension(P, e):
    """All subgroups of the p-group P: close {H, x} for every known H and x in P."""
    found = {frozenset([e])}
    frontier = [frozenset([e])]
    while frontier:
        nxt = []
        for H in frontier:
            for x in sorted(P):
                if x in H:
                    continue
                K = _gen_closure(list(H) + [x], e)
                if K not in found:
                    found.add(K)
                    nxt.append(K)
        frontier = nxt
    return sorted(found, key=lambda H: (len(H), sorted(H)))


def o_p_by_core(N, p, e):
    S, _ = sylow(N, p, e)
    core = set(S)
    for n in N:
        ni = inverse(n)
        core &= {compose(compose(n, s), ni) for s in S}
    return frozenset(core)


def defect_zero(degrees, order, p):
    full = p_part(order, p)
    return sum(1 for d in degrees if p_part(d, p) == full)


def _min_gens(H, e):
    out, sub = [], frozenset([e])
    for x in sorted(H):
        if x not in sub:
            out.append(x)
            sub = _gen_closure(out, e)
            if len(sub) == len(H):
                break
    return out


def analyse(name, p):
    gens, order = GROUPS[name]
    G = FiniteGroup.from_permutations(gens)
    if G.order != order:
        raise ValueError(f"{name}: generated order {G.order} != {order}")
    e = G.identity
    classes, _ = G.classes()
    regular = [c for c in classes if element_order(c[0]) % p]
    P, _ = sylow(G.elements, p, e)
    radicals, seen = [], set()
    for H in subgroups_by_extension(P, e):
        if H in seen:
            continue
        for g in G.elements:
            gi = inverse(g)
            seen.add(frozenset(compose(compose(g, h), gi) for h in H))
        hg = _min_gens(H, e)
        N = normaliser(G.elements, H, hg or [e])
        if o_p_by_core(N, p, e) != H:
            continue
        quotient = FiniteGroup.quotient(N, H, _min_gens(N, e))
        degrees, r = character_degrees(quotient)
        radicals.append({
            "generators": [list(x) for x in hg], "order": len(H), "normaliser_order": len(N),
            "quotient_degrees": degrees, "defect_zero": defect_zero(degrees, quotient.order, p), "prime_r": r,
        })
    w = sum(rad["defect_zero"] for rad in radicals)
    return {
        "group": name, "order": G.order, "p": p,
        "regular_classes": [{"rep": list(c[0]), "size": len(c)} for c in regular],
        "l": len(regular), "w": w,
        "sylow_generators": [list(x) for x in _min_gens(P, e)],
        "radicals": radicals,
    }


def search(params):
    rows = [analyse(name, p) for name in params["groups"] for p in prime_factors(GROUPS[name][1])]
    bad = [(r["group"], r["p"]) for r in rows if r["l"] != r["w"]]
    return {
        "holds": not bad,
        "summary": {
            "cases": len(rows), "groups": len(params["groups"]),
            "table": {f"{r['group']} p={r['p']}": [r["l"], r["w"]] for r in rows},
            "radical_classes": sum(len(r["radicals"]) for r in rows),
            "counterexample": bad or None,
            "certificate_sha256": digest(rows),
        },
        "certificate": rows,
    }


# ------------------------------------------------------------------- checker

def _is_p_group_order(n, p):
    return n == p_part(n, p)


def _radical_by_closures(G_elems, Q, p, e):
    """Q is p-radical iff no N_G(Q)-class of x in N \\ Q with x^p in Q generates, with Q, a p-group."""
    N = [g for g in G_elems if all(compose(compose(g, q), inverse(g)) in Q for q in Q)]
    limit = p_part(len(N), p)
    done = set()
    for x in N:
        if x in Q or x in done:
            continue
        y = x
        for _ in range(p - 1):
            y = compose(y, x)
        if y not in Q:
            continue
        cls = {compose(compose(n, x), inverse(n)) for n in N}
        done |= cls
        K = set(Q)
        frontier = list(K)
        gens = list(cls) + list(Q)
        too_big = False
        while frontier and not too_big:
            nxt = []
            for a in frontier:
                for g in gens:
                    b = compose(a, g)
                    if b not in K:
                        K.add(b)
                        nxt.append(b)
                        if len(K) > limit:
                            too_big = True
                            break
                if too_big:
                    break
            frontier = nxt
        if not too_big and _is_p_group_order(len(K), p):
            return False, N
    return True, N


def _subgroups_by_generating_sets(P, p, e):
    k = 0
    while p ** k < len(P):
        k += 1
    elems = sorted(x for x in P if x != e)
    found = {frozenset([e])}
    for size in range(1, k + 1):
        for combo in combinations(elems, size):
            found.add(_gen_closure(combo, e))
    return found


def _conjugate(G_elems, A, B):
    if len(A) != len(B) or sorted(map(element_order, A)) != sorted(map(element_order, B)):
        return False
    for g in G_elems:
        gi = inverse(g)
        if all(compose(compose(g, a), gi) in B for a in A):
            return True
    return False


def check_case(row):
    name, p = row["group"], row["p"]
    gens, order = GROUPS[name]
    G = FiniteGroup.from_permutations(gens)
    require(G.order == order == row["order"], f"{name}: group order mismatch")
    e = G.identity
    elems = G.elements
    # l(G): listed reps are p-regular, pairwise non-conjugate, and their classes exhaust the p-regular elements
    reps = [tuple(c["rep"]) for c in row["regular_classes"]]
    sizes = []
    for x, c in zip(reps, row["regular_classes"]):
        require(element_order(x) % p != 0, f"{name}: class rep is not p-regular")
        cent = sum(1 for g in elems if compose(g, x) == compose(x, g))
        require(order % cent == 0 and order // cent == c["size"], f"{name}: class size wrong")
        sizes.append(c["size"])
    for i in range(len(reps)):
        for j in range(i + 1, len(reps)):
            require(not _conjugate(elems, [reps[i]], {reps[j]}), f"{name}: class reps are conjugate")
    regular_total = sum(1 for g in elems if element_order(g) % p)
    require(sum(sizes) == regular_total, f"{name} p={p}: p-regular classes incomplete")
    require(row["l"] == len(reps), f"{name}: l(G) mismatch")
    # Sylow subgroup and its subgroups, re-enumerated from small generating sets
    P = _gen_closure([tuple(x) for x in row["sylow_generators"]] or [e], e)
    require(len(P) == p_part(order, p), f"{name}: not a Sylow {p}-subgroup")
    listed = [_gen_closure([tuple(x) for x in rad["generators"]] or [e], e) for rad in row["radicals"]]
    for i in range(len(listed)):
        for j in range(i + 1, len(listed)):
            require(not _conjugate(elems, listed[i], listed[j]), f"{name}: listed radicals are conjugate")
    norms = []
    for Q, rad in zip(listed, row["radicals"]):
        require(len(Q) == rad["order"] and _is_p_group_order(len(Q), p), f"{name}: radical is not a p-group")
        ok, N = _radical_by_closures(elems, Q, p, e)
        require(ok, f"{name} p={p}: listed subgroup of order {len(Q)} is not radical")
        require(len(N) == rad["normaliser_order"], f"{name}: normaliser order mismatch")
        norms.append(N)
    for R in _subgroups_by_generating_sets(P, p, e):
        if any(_conjugate(elems, R, Q) for Q in listed):
            continue
        ok, _ = _radical_by_closures(elems, R, p, e)
        require(not ok, f"{name} p={p}: radical subgroup of order {len(R)} missing from the list")
    # defect-zero counts of N/Q with a different Dixon prime and splitting order
    w = 0
    for Q, N, rad in zip(listed, norms, row["radicals"]):
        quotient = FiniteGroup.quotient(N, Q, generating_set(N, compose, e))
        degrees, r = character_degrees(quotient, skip=1, reverse=True)
        require(r != rad["prime_r"], "checker must use a different prime")
        require(degrees == rad["quotient_degrees"], f"{name}: degrees of N/Q differ")
        require(sum(d * d for d in degrees) == quotient.order, f"{name}: degrees do not square-sum to |N/Q|")
        require(len(degrees) == len(quotient.classes()[0]), f"{name}: one degree per class required")
        z = defect_zero(degrees, quotient.order, p)
        require(z == rad["defect_zero"], f"{name}: defect-zero count mismatch")
        w += z
    require(w == row["w"], f"{name} p={p}: weight count mismatch")
    return row["l"] == w


def check(params, result):
    rows = result["certificate"]
    expected = [(n, p) for n in params["groups"] for p in prime_factors(GROUPS[n][1])]
    require([(r["group"], r["p"]) for r in rows] == expected, "case list differs from the parameters")
    holds = all(check_case(r) for r in rows)
    require(holds == result["holds"], "holds flag differs from the recomputed comparison")
    s = result["summary"]
    require(s["table"] == {f"{r['group']} p={r['p']}": [r["l"], r["w"]] for r in rows}, "summary table mismatch")
    require(s["certificate_sha256"] == digest(rows), "certificate hash mismatch")
