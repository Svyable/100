"""M093 - MDS conjecture, dimension 3: maximum arcs in PG(2,q).

A [n,3] linear MDS code over GF(q) is the same as an n-arc in PG(2,q)
(n points, no three collinear). The MDS conjecture predicts n <= q+1 for odd q
and n <= q+2 for even q (Segre 1955 / Bose 1947 for k = 3: known).

Search: exhaustive extension of the standard frame (PGL(3,q) is transitive on
ordered quadrangles, so every arc of size >= 4 is equivalent to one containing
it). Check: an independent implementation with its own field arithmetic
(re-derived from the certified irreducible modulus) re-verifies the witness,
recounts complete extensions, and, for q <= 4, brute-forces all subsets
without any symmetry assumption.
"""
from itertools import combinations

from .core import require
from .fields import field, is_irreducible, prime_power, projective_points

PROBE = {
    "id": "mds_arcs",
    "problem_id": "M093",
    "title": "Maximum arcs in PG(2,q) = longest 3-dimensional linear MDS codes",
    "engines": ["finite_fields", "symmetry_reduction"],
    "frontier": ("Known for k = 3 by Segre (q odd) and Bose (q even); the MDS conjecture is "
                 "proved for prime q (Ball 2012) and open for general prime powers."),
    "levels": {"smoke": {"qs": [2, 3, 4, 5, 7]}, "deep": {"qs": [2, 3, 4, 5, 7, 8, 9]}},
}


def scope(params):
    return ("For q in {" + ", ".join(map(str, params["qs"])) + "}: an explicit maximum arc and "
            "exhaustive exclusion of larger arcs (MDS length bound for k = 3).")


def _det(F, a, b, c):
    t1 = F.mul(a[0], F.sub(F.mul(b[1], c[2]), F.mul(b[2], c[1])))
    t2 = F.mul(a[1], F.sub(F.mul(b[0], c[2]), F.mul(b[2], c[0])))
    t3 = F.mul(a[2], F.sub(F.mul(b[0], c[1]), F.mul(b[1], c[0])))
    return F.add(F.sub(t1, t2), t3)


def max_arcs(q):
    F = field(q)
    pts = projective_points(F)
    idx = {p: i for i, p in enumerate(pts)}
    frame = [idx[(1, 0, 0)], idx[(0, 1, 0)], idx[(0, 0, 1)], idx[(1, 1, 1)]]
    n = len(pts)
    # explicit backtracking over candidates outside the frame
    best, complete = [], []
    def free(arc, cand):
        return [c for c in cand if all(_det(F, pts[a], pts[b], pts[c]) != 0
                                       for a, b in combinations(arc, 2))]
    def extend(arc, cand):
        nonlocal best
        if len(arc) > len(best):
            best = list(arc)
            complete.clear()
        if len(arc) == len(best):
            complete.append(sorted(arc))
        for i, c in enumerate(cand):
            nxt = [d for d in cand[i + 1:] if all(_det(F, pts[c], pts[a], pts[d]) != 0 for a in arc)]
            extend(arc + [c], nxt)
    start = free(frame, [i for i in range(n) if i not in frame])
    extend(list(frame), start)
    return F, pts, best, complete


def search(params):
    results = {}
    for q in params["qs"]:
        F, pts, best, complete = max_arcs(q)
        results[str(q)] = {
            "modulus": F.modulus,
            "max_arc_size": len(best),
            "witness": [list(pts[i]) for i in best],
            "maximum_arcs_through_frame": len(complete),
        }
    holds = all(r["max_arc_size"] == (int(q) + 2 if int(q) % 2 == 0 else int(q) + 1)
                for q, r in results.items())
    return {
        "holds": holds,
        "summary": {q: {"max_arc_size": r["max_arc_size"],
                        "maximum_arcs_through_frame": r["maximum_arcs_through_frame"]}
                    for q, r in results.items()},
        "certificate": results,
    }


class _Field:
    """Independent GF(p^k) arithmetic from an explicit modulus (lowest degree first)."""
    def __init__(self, q, modulus):
        p, k = prime_power(q)
        require(len(modulus) == k + 1 and is_irreducible(list(modulus), p),
                f"GF({q}) modulus is not monic irreducible of degree {k}")
        self.p, self.k, self.m = p, k, modulus
    def vec(self, a):
        return [(a // self.p ** i) % self.p for i in range(self.k)]
    def mul(self, a, b):
        x, y, p, k = self.vec(a), self.vec(b), self.p, self.k
        prod = [0] * (2 * k)
        for i in range(k):
            for j in range(k):
                prod[i + j] += x[i] * y[j]
        for d in range(2 * k - 1, k - 1, -1):
            c = prod[d] % p
            for i in range(k + 1):
                prod[d - k + i] -= c * self.m[i]
        return sum((prod[i] % p) * p ** i for i in range(k))
    def add(self, a, b):
        x, y = self.vec(a), self.vec(b)
        return sum(((x[i] + y[i]) % self.p) * self.p ** i for i in range(self.k))
    def neg(self, a):
        return sum(((-c) % self.p) * self.p ** i for i, c in enumerate(self.vec(a)))


def _collinear(G, a, b, c):
    terms = [(0, 1, 2, 1), (1, 0, 2, -1), (2, 0, 1, 1)]
    total = 0
    for i, j, k, sign in terms:
        minor = G.add(G.mul(b[j], c[k]), G.neg(G.mul(b[k], c[j])))
        t = G.mul(a[i], minor)
        total = G.add(total, t if sign == 1 else G.neg(t))
    return total == 0


def check(params, result):
    cert = result["certificate"]
    require(sorted(map(int, cert)) == sorted(params["qs"]), "missing field sizes")
    for key, r in cert.items():
        q = int(key)
        G = _Field(q, r["modulus"])
        pts = []
        for lead in range(3):
            for code in range(q ** (2 - lead)):
                tail = [(code // q ** i) % q for i in range(2 - lead)]
                pts.append(tuple([0] * lead + [1] + tail))
        w = [tuple(p) for p in r["witness"]]
        require(len(set(w)) == len(w) == r["max_arc_size"] and all(p in pts for p in w),
                f"q={q}: witness points invalid")
        require(not any(_collinear(G, a, b, c) for a, b, c in combinations(w, 3)),
                f"q={q}: witness has three collinear points")
        expected = q + 2 if q % 2 == 0 else q + 1
        require(r["max_arc_size"] == expected or not result["holds"], f"q={q}: unexpected bound")
        # independent recount with collinearity masks derived from the certified field
        n = len(pts)
        third = {}
        for a, b, c in combinations(range(n), 3):
            if _collinear(G, pts[a], pts[b], pts[c]):
                for x, y, z in ((a, b, c), (a, c, b), (b, c, a)):
                    third[(x, y)] = third.get((x, y), 0) | (1 << z)
        def blocked(arc):
            m = 0
            for x, y in combinations(sorted(arc), 2):
                m |= third.get((x, y), 0)
            return m
        frame = [pts.index(p) for p in [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)]]
        sizes = {}
        def grow(arc, avoid, last):
            sizes[len(arc)] = sizes.get(len(arc), 0) + 1
            for c in range(last + 1, n):
                if c not in arc and not avoid >> c & 1:
                    extra = 0
                    for a in arc:
                        x, y = min(a, c), max(a, c)
                        extra |= third.get((x, y), 0)
                    grow(arc + [c], avoid | extra, c)
        grow(frame, blocked(frame), -1)
        top = max(sizes)
        require(top == r["max_arc_size"], f"q={q}: independent search found arcs of size {top}")
        require(sizes[top] == r["maximum_arcs_through_frame"], f"q={q}: extension count mismatch")
        if q <= 4:  # no symmetry assumption at all
            def is_arc(s):
                return not any(third.get((x, y), 0) >> z & 1 for x, y, z in combinations(s, 3))
            require(not any(is_arc(s) for s in combinations(range(n), top + 1)),
                    f"q={q}: brute force found a larger arc")
