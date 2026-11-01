"""Finite permutation groups, quotients, conjugacy classes and modular character degrees.

Groups are given by permutation generators (tuples) and enumerated completely, so
this engine is meant for groups of order up to a few thousand. A quotient N/Q (Q
normal in N) is represented by canonical coset representatives. Character degrees
come from Dixon's method: the class-multiplication matrices are reduced mod a prime
r = 1 (mod exponent) with r > 2 sqrt(|G|), their common eigenvectors are the central
characters mod r, and chi(1)^2 = |G| / sum_j w_j w_j* / |C_j| determines each degree
uniquely in [1, sqrt|G|]. A different prime gives an independent recomputation.
"""
from math import gcd, isqrt


def compose(a, b):
    """(a o b)(i) = a[b[i]]."""
    return tuple(a[i] for i in b)


def inverse(a):
    out = [0] * len(a)
    for i, ai in enumerate(a):
        out[ai] = i
    return tuple(out)


def cycle(n, *cycles):
    perm = list(range(n))
    for c in cycles:
        for i, x in enumerate(c):
            perm[x] = c[(i + 1) % len(c)]
    return tuple(perm)


def closure(gens, identity):
    """All products of the generators (finite group), identity first, deterministic order."""
    seen = {identity}
    order = [identity]
    frontier = [identity]
    while frontier:
        nxt = []
        for x in frontier:
            for g in gens:
                y = compose(x, g)
                if y not in seen:
                    seen.add(y)
                    order.append(y)
                    nxt.append(y)
        frontier = nxt
    return order


def element_order(x):
    e = tuple(range(len(x)))
    k, y = 1, x
    while y != e:
        y = compose(y, x)
        k += 1
    return k


def p_part(n, p):
    out = 1
    while n % p == 0:
        n //= p
        out *= p
    return out


def prime_factors(n):
    out, f = [], 2
    while f * f <= n:
        if n % f == 0:
            out.append(f)
            while n % f == 0:
                n //= f
        f += 1
    if n > 1:
        out.append(n)
    return out


def is_prime(n):
    return n > 1 and all(n % f for f in range(2, isqrt(n) + 1))


class FiniteGroup:
    """Abstract finite group: elements, multiplication, inverse, identity, generators."""

    def __init__(self, elements, mul, inv, identity, gens):
        self.elements = list(elements)
        self.mul, self.inv, self.identity, self.gens = mul, inv, identity, list(gens)
        self.order = len(self.elements)

    @classmethod
    def from_permutations(cls, gens):
        n = len(gens[0])
        e = tuple(range(n))
        return cls(closure(gens, e), compose, inverse, e, gens)

    @classmethod
    def quotient(cls, N, Q, n_gens):
        """N/Q for a list N of permutations and a normal subgroup Q (set) of N."""
        rep = {}
        for x in N:
            if x not in rep:
                coset = [compose(x, q) for q in Q]
                r = min(coset)
                for y in coset:
                    rep[y] = r
        reps = sorted(set(rep.values()))
        mul = lambda a, b: rep[compose(a, b)]
        inv = lambda a: rep[inverse(a)]
        identity = rep[tuple(range(len(N[0])))]
        gens = sorted({rep[g] for g in n_gens})
        return cls(reps, mul, inv, identity, gens)

    def elt_order(self, x):
        k, y = 1, x
        while y != self.identity:
            y = self.mul(y, x)
            k += 1
        return k

    def classes(self):
        """Conjugacy classes (identity class first), via orbits under conjugation by generators."""
        cls_of, out = {}, []
        ordered = [self.identity] + [x for x in sorted(self.elements) if x != self.identity]
        inv_gens = [(g, self.inv(g)) for g in self.gens]
        for x in ordered:
            if x in cls_of:
                continue
            idx = len(out)
            cls_of[x] = idx
            members, frontier = [x], [x]
            while frontier:
                nxt = []
                for y in frontier:
                    for g, gi in inv_gens:
                        z = self.mul(self.mul(g, y), gi)
                        if z not in cls_of:
                            cls_of[z] = idx
                            members.append(z)
                            nxt.append(z)
                frontier = nxt
            out.append(members)
        return out, cls_of


def generating_set(elements, mul, identity):
    """Greedy generating set of the group formed by `elements` (deterministic)."""
    gens, sub = [], {identity}
    for x in sorted(elements):
        if x in sub:
            continue
        gens.append(x)
        frontier = list(sub)
        while frontier:
            nxt = []
            for y in frontier:
                for g in gens:
                    z = mul(y, g)
                    if z not in sub:
                        sub.add(z)
                        nxt.append(z)
            frontier = nxt
        if len(sub) == len(elements):
            break
    return gens


# =============================================================== Dixon mod r

def dixon_prime(order, exponent, skip=0):
    """The (skip+1)-th prime r = 1 (mod exponent) with r > 2 sqrt(order)."""
    k, found = 1, -1
    while True:
        r = 1 + k * exponent
        if r * r > 4 * order and is_prime(r):
            found += 1
            if found == skip:
                return r
        k += 1


def _rref(rows, r):
    rows = [list(v) for v in rows]
    pivots, out = [], []
    width = len(rows[0]) if rows else 0
    for col in range(width):
        piv = next((i for i, v in enumerate(rows) if v[col] % r), None)
        if piv is None:
            continue
        v = rows.pop(piv)
        inv = pow(v[col], r - 2, r)
        v = [x * inv % r for x in v]
        rows = [[(a - w[col] * b) % r for a, b in zip(w, v)] for w in rows]
        out = [[(a - w[col] * b) % r for a, b in zip(w, v)] for w in out]
        out.append(v)
        pivots.append(col)
    return out, pivots


def _nullspace(A, r):
    """Basis of {x : A x = 0} over F_r (A: list of rows)."""
    n = len(A[0])
    R, piv = _rref(A, r)
    free = [j for j in range(n) if j not in piv]
    basis = []
    for f in free:
        x = [0] * n
        x[f] = 1
        for row, pc in zip(R, piv):
            x[pc] = (-row[f]) % r
        basis.append(x)
    return basis


def _charpoly(A, r):
    """Coefficients c[0..d] (c[d] = 1) of det(xI - A) over F_r by Faddeev-LeVerrier (d < r)."""
    d = len(A)
    c = [0] * (d + 1)
    c[d] = 1
    M = [[0] * d for _ in range(d)]
    for k in range(1, d + 1):
        # M <- A M + c[d-k+1] I
        AM = [[sum(A[i][t] * M[t][j] for t in range(d)) % r for j in range(d)] for i in range(d)]
        for i in range(d):
            AM[i][i] = (AM[i][i] + c[d - k + 1]) % r
        M = AM
        tr = sum(sum(A[i][t] * M[t][i] for t in range(d)) for i in range(d)) % r
        c[d - k] = (-tr * pow(k, r - 2, r)) % r
    return c


def central_characters(group, classes, cls_of, r, order_of_matrices=None):
    """Common eigenvectors (normalised, w[0] = 1) of the class matrices mod r."""
    k = len(classes)
    reps = [c[0] for c in classes]
    # C[i][j][kk] = #{x in C_i : x^-1 z_kk in C_j}
    C = [[[0] * k for _ in range(k)] for _ in range(k)]
    for kk, z in enumerate(reps):
        for x in group.elements:
            C[cls_of[x]][cls_of[group.mul(group.inv(x), z)]][kk] += 1
    spaces = [[[1 if i == j else 0 for j in range(k)] for i in range(k)]]  # rows, RREF
    seq = order_of_matrices or list(range(1, k))
    for i in seq:
        if all(len(sp) == 1 for sp in spaces):
            break
        Mi = C[i]
        new = []
        for basis in spaces:
            if len(basis) == 1:
                new.append(basis)
                continue
            basis, piv = _rref(basis, r)
            d = len(basis)
            images = [[sum(Mi[a][b] * v[b] for b in range(k)) % r for a in range(k)] for v in basis]
            A = [[images[col][piv[row]] for col in range(d)] for row in range(d)]  # column = image coords
            cp = _charpoly(A, r)
            roots = [lam for lam in range(r) if _horner(cp, lam, r) == 0]
            for lam in roots:
                null = _nullspace([[(A[a][b] - (lam if a == b else 0)) % r for b in range(d)]
                                   for a in range(d)], r)
                vecs = [[sum(cf * basis[t][j] for t, cf in enumerate(nv)) % r for j in range(k)] for nv in null]
                new.append(vecs)
        spaces = new
    if any(len(sp) != 1 for sp in spaces) or len(spaces) != k:
        raise ValueError("class matrices did not split into one-dimensional eigenspaces")
    out = []
    for (v,) in spaces:
        inv0 = pow(v[0], r - 2, r)
        out.append([x * inv0 % r for x in v])
    return out


def _horner(c, x, r):
    acc = 0
    for coef in reversed(c):
        acc = (acc * x + coef) % r
    return acc


def character_degrees(group, skip=0, reverse=False):
    """Sorted irreducible character degrees of a finite group (Dixon's method mod a prime)."""
    classes, cls_of = group.classes()
    exponent = 1
    for c in classes:
        o = group.elt_order(c[0])
        exponent = exponent * o // gcd(exponent, o)
    r = dixon_prime(group.order, exponent, skip)
    k = len(classes)
    seq = list(range(k - 1, 0, -1)) if reverse else None
    ws = central_characters(group, classes, cls_of, r, seq)
    inv_class = [cls_of[group.inv(c[0])] for c in classes]
    degrees = []
    for w in ws:
        S = sum(w[j] * w[inv_class[j]] * pow(len(classes[j]), r - 2, r) for j in range(k)) % r
        target = group.order * pow(S, r - 2, r) % r
        ds = [d for d in range(1, isqrt(group.order) + 1) if d * d % r == target]
        if len(ds) != 1:
            raise ValueError("degree not determined uniquely")
        degrees.append(ds[0])
    return sorted(degrees), r
