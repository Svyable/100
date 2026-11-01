"""Exact finite-group engine: conjugacy, abelianization, radical p-subgroups.

Groups are concrete subgroups of a symmetric group, stored as a frozenset of
permutations. A permutation on {0..n-1} is an n-tuple ``p`` with ``p[i]`` the
image of ``i``. All counts are exact. Character *degrees* of a group of order
at most 60 are recovered from the triple (|G|, number of conjugacy classes,
|G:G'|): for every such triple that arises, the multiset of ordinary degrees
is unique among tuples of positive divisors of |G| that square-sum to |G| and
contain exactly |G:G'| ones. That is enough for Alperin's weight count, which
only needs how many degrees are divisible by the full p-part of |G|.

This module never claims an open modular-representation conjecture.
"""
from functools import lru_cache
from math import gcd


def compose(a, b):
    """Return a ∘ b (apply b, then a)."""
    return tuple(a[b[i]] for i in range(len(a)))


def invert(a):
    out = [0] * len(a)
    for i, j in enumerate(a):
        out[j] = i
    return tuple(out)


def identity(n):
    return tuple(range(n))


def order_of(a):
    n, p, k = len(a), a, 1
    idn = identity(n)
    while p != idn:
        p = compose(a, p)
        k += 1
        if k > n * n:
            raise ValueError("permutation order overflow")
    return k


def generated(seed, n):
    """Cayley closure of a set of permutations on n letters."""
    idn = identity(n)
    gens = [g for g in seed if g != idn]
    elts = {idn}
    frontier = [idn]
    while frontier:
        g = frontier.pop()
        for s in gens:
            for h in (compose(g, s), compose(s, g)):
                if h not in elts:
                    elts.add(h)
                    frontier.append(h)
    return frozenset(elts)


def is_group(elements):
    if not elements:
        return False
    n = len(next(iter(elements)))
    idn = identity(n)
    if idn not in elements:
        return False
    if any(len(g) != n for g in elements):
        return False
    for g in elements:
        if invert(g) not in elements:
            return False
        for h in elements:
            if compose(g, h) not in elements:
                return False
    return True


def conjugacy_classes(elements):
    """Partition ``elements`` into conjugacy classes; each class sorted."""
    remaining = set(elements)
    classes = []
    while remaining:
        g = min(remaining)  # stable representative
        cls = {compose(compose(x, g), invert(x)) for x in elements}
        classes.append(tuple(sorted(cls)))
        remaining -= cls
    classes.sort(key=lambda c: (len(c), c[0]))
    return classes


def p_regular_classes(elements, p):
    """Conjugacy classes whose representatives have order coprime to p."""
    return [c for c in conjugacy_classes(elements) if order_of(c[0]) % p != 0]


def derived_subgroup(elements):
    gens = []
    for g in elements:
        ig = invert(g)
        for h in elements:
            # [g,h] = g^{-1} h^{-1} g h
            gens.append(compose(compose(compose(ig, invert(h)), g), h))
    n = len(next(iter(elements)))
    return generated(gens, n)


def abelianization_order(elements):
    return len(elements) // len(derived_subgroup(elements))


def centre(elements):
    out = []
    for z in elements:
        if all(compose(z, g) == compose(g, z) for g in elements):
            out.append(z)
    return frozenset(out)


def _p_part(n, p):
    part = 1
    while n % p == 0:
        n //= p
        part *= p
    return part


def character_degrees(elements):
    """Unique ordinary character-degree multiset for |G| <= 60 (when unique)."""
    order = len(elements)
    if order > 60:
        raise ValueError("character_degrees only covers groups of order <= 60")
    classes = conjugacy_classes(elements)
    n_classes = len(classes)
    n_linear = abelianization_order(elements)
    if n_linear < 1 or n_linear > n_classes or order % n_linear != 0:
        raise ValueError("abelianization incompatible with class count")
    divs = [d for d in range(2, order + 1) if order % d == 0]
    # Ito: each degree divides |G:Z(G)|
    index_z = order // len(centre(elements))
    divs = [d for d in divs if index_z % d == 0]
    n_nonlin = n_classes - n_linear
    remaining = order - n_linear
    found = []

    def rec(start, left, rem, acc):
        if left == 0:
            if rem == 0:
                found.append(tuple(sorted([1] * n_linear + acc)))
            return
        for i in range(start, len(divs)):
            d = divs[i]
            if d * d > rem:
                break
            rec(i, left - 1, rem - d * d, acc + [d])

    rec(0, n_nonlin, remaining, [])
    uniq = sorted(set(found))
    if len(uniq) != 1:
        raise ValueError(
            f"character degrees not unique for |G|={order}, k={n_classes}, "
            f"|G:G'|={n_linear}: {uniq}"
        )
    return list(uniq[0])


def defect_zero_count(elements, p):
    """Number of ordinary irreps of p-defect zero."""
    if len(elements) % p != 0:
        # p' group: every irrep has defect zero
        return len(conjugacy_classes(elements))
    p_part = _p_part(len(elements), p)
    return sum(1 for d in character_degrees(elements) if d % p_part == 0)


def subgroups(elements):
    """All subgroups, each as a frozenset (exponential; for |G| <= 24)."""
    if len(elements) > 24:
        raise ValueError("full subgroup lattice only for |G| <= 24")
    n = len(next(iter(elements)))
    elts = sorted(elements)
    found = {frozenset({identity(n)})}
    changed = True
    while changed:
        changed = False
        current = list(found)
        for H in current:
            for g in elts:
                if g in H:
                    continue
                K = generated(list(H) + [g], n)
                if K not in found and K <= elements:
                    found.add(K)
                    changed = True
    return found


def is_p_group(elements, p):
    return all(order_of(g) == 1 or order_of(g) % p == 0 for g in elements) and (
        len(elements) == 1 or len(elements) % p == 0
    )


def p_subgroups(elements, p):
    """Every p-subgroup, generated from p-elements (works for |G| <= 60)."""
    if len(elements) > 60:
        raise ValueError("p-subgroup census only for |G| <= 60")
    n = len(next(iter(elements)))
    idn = identity(n)
    p_elts = [g for g in elements if g != idn and order_of(g) % p == 0]
    found = {frozenset({idn})}
    changed = True
    while changed:
        changed = False
        current = list(found)
        for H in current:
            for g in p_elts:
                if g in H:
                    continue
                K = generated(list(H) + [g], n)
                if K <= elements and is_p_group(K, p) and K not in found:
                    found.add(K)
                    changed = True
    return found


def normalizer(elements, subgroup):
    n = len(next(iter(elements)))
    out = []
    for g in elements:
        ig = invert(g)
        conjugated = frozenset(compose(compose(g, h), ig) for h in subgroup)
        if conjugated == subgroup:
            out.append(g)
    return frozenset(out)


def is_normal(elements, subgroup):
    return normalizer(elements, subgroup) == elements


def o_p(elements, p):
    """Largest normal p-subgroup O_p(G)."""
    normals = [H for H in p_subgroups(elements, p) if is_normal(elements, H)]
    return max(normals, key=len)


def is_radical(elements, subgroup, p):
    """Q is radical iff Q = O_p(N_G(Q))."""
    return subgroup == o_p(normalizer(elements, subgroup), p)


def conjugate_subgroup(g, subgroup):
    ig = invert(g)
    return frozenset(compose(compose(g, h), ig) for h in subgroup)


def radical_p_subgroup_reps(elements, p):
    """One representative per G-conjugacy class of radical p-subgroups."""
    radicals = [H for H in p_subgroups(elements, p) if is_radical(elements, H, p)]
    reps = []
    seen = []
    for H in sorted(radicals, key=lambda X: (len(X), sorted(X))):
        if any(any(conjugate_subgroup(g, H) == S for g in elements) for S in seen):
            continue
        seen.append(H)
        reps.append(H)
    return reps


def quotient(elements, normal):
    """Left cosets of a normal subgroup as a concrete permutation group.

    Cosets are labeled 0..index-1 in sorted order of their minimal element.
    Multiplication of cosets is the quotient group law.
    """
    if not is_normal(elements, normal):
        raise ValueError("quotient requires a normal subgroup")
    n = len(next(iter(elements)))
    # build cosets
    remaining = set(elements)
    cosets = []
    while remaining:
        g = min(remaining)
        coset = frozenset(compose(g, h) for h in normal)
        cosets.append(coset)
        remaining -= coset
    cosets.sort(key=lambda c: min(c))
    index = {min(c): i for i, c in enumerate(cosets)}
    # map every element to its coset index
    elt_to_coset = {}
    for i, c in enumerate(cosets):
        for g in c:
            elt_to_coset[g] = i
    # permutation representation on cosets by left multiplication
    perms = []
    for g in elements:
        images = []
        for c in cosets:
            rep = min(c)
            images.append(elt_to_coset[compose(g, rep)])
        perms.append(tuple(images))
    return frozenset(perms)


def alperin_weight_count(elements, p):
    """Global Alperin count: #weights via radical subgroups and defect-0 degrees."""
    total = 0
    details = []
    for Q in radical_p_subgroup_reps(elements, p):
        N = normalizer(elements, Q)
        H = quotient(N, Q)
        dz = defect_zero_count(H, p)
        total += dz
        details.append({
            "q_order": len(Q),
            "n_order": len(N),
            "h_order": len(H),
            "h_classes": len(conjugacy_classes(H)),
            "h_linear": abelianization_order(H),
            "h_degrees": character_degrees(H) if len(H) <= 60 else None,
            "defect_zero": dz,
        })
    return total, details


def simple_module_count(elements, p):
    """Number of simple modules over an algebraically closed field of char p."""
    return len(p_regular_classes(elements, p))


# ------------------------------------------------------------------ named groups


def cyclic(n):
    if n < 1:
        raise ValueError("n >= 1")
    # act on n points by rotation; for n=1 use a dummy 1-point group
    deg = max(n, 1)
    rot = tuple((i + 1) % deg for i in range(deg)) if n > 1 else identity(1)
    return generated([rot], deg) if n > 1 else frozenset({identity(1)})


def symmetric(n):
    if n < 1 or n > 5:
        raise ValueError("symmetric(n) supported for 1 <= n <= 5")
    if n == 1:
        return frozenset({identity(1)})
    # adjacent transpositions
    gens = []
    for i in range(n - 1):
        p = list(range(n))
        p[i], p[i + 1] = p[i + 1], p[i]
        gens.append(tuple(p))
    return generated(gens, n)


def alternating(n):
    s = symmetric(n)
    # sign: count inversions
    def even(p):
        inv = 0
        for i in range(len(p)):
            for j in range(i + 1, len(p)):
                if p[i] > p[j]:
                    inv += 1
        return inv % 2 == 0
    return frozenset(g for g in s if even(g))


def dihedral(n):
    """Dihedral group of order 2n acting on n vertices (n >= 3)."""
    if n < 3:
        raise ValueError("dihedral(n) needs n >= 3")
    rot = tuple((i + 1) % n for i in range(n))
    ref = tuple((n - i) % n for i in range(n))
    return generated([rot, ref], n)


def quaternion():
    """Q8 as a regular permutation representation on 8 elements.

    Label elements as 0..7 corresponding to {1,-1,i,-i,j,-j,k,-k} in that
    order. Left multiplication gives an injective homomorphism Q8 -> S8.
    """
    # multiplication table for (1,-1,i,-i,j,-j,k,-k)
    # indices: 0=1, 1=-1, 2=i, 3=-i, 4=j, 5=-j, 6=k, 7=-k
    mul = [
        [0, 1, 2, 3, 4, 5, 6, 7],  # 1 *
        [1, 0, 3, 2, 5, 4, 7, 6],  # -1 *
        [2, 3, 1, 0, 6, 7, 5, 4],  # i *
        [3, 2, 0, 1, 7, 6, 4, 5],  # -i *
        [4, 5, 7, 6, 1, 0, 2, 3],  # j *
        [5, 4, 6, 7, 0, 1, 3, 2],  # -j *
        [6, 7, 4, 5, 3, 2, 1, 0],  # k *
        [7, 6, 5, 4, 2, 3, 0, 1],  # -k *
    ]
    gens = [tuple(mul[2]), tuple(mul[4])]  # i and j
    return generated(gens, 8)


def direct_product(a, b):
    """Direct product as permutations on deg(a)+deg(b) letters."""
    na = len(next(iter(a)))
    nb = len(next(iter(b)))
    elts = []
    for g in a:
        for h in b:
            elts.append(tuple(list(g) + [na + x for x in h]))
    return frozenset(elts)


NAMED = {
    "C1": lambda: cyclic(1),
    "C2": lambda: cyclic(2),
    "C3": lambda: cyclic(3),
    "C4": lambda: cyclic(4),
    "C5": lambda: cyclic(5),
    "C6": lambda: cyclic(6),
    "C2xC2": lambda: direct_product(cyclic(2), cyclic(2)),
    "S3": lambda: symmetric(3),
    "D8": lambda: dihedral(4),
    "Q8": quaternion,
    "A4": lambda: alternating(4),
    "D10": lambda: dihedral(5),
    "S4": lambda: symmetric(4),
    "A5": lambda: alternating(5),
    "D12": lambda: dihedral(6),
}


@lru_cache(maxsize=None)
def named(name):
    if name not in NAMED:
        raise KeyError(name)
    G = NAMED[name]()
    if not is_group(G):
        raise RuntimeError(f"{name} failed the group axioms")
    return G


def catalog():
    return {name: named(name) for name in NAMED}
