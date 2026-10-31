"""Exact sparse polynomials in two variables over Z (dict {(i, j): coeff})."""


def monomials(k):
    """All exponent pairs of total degree k, in a fixed order."""
    return [(i, k - i) for i in range(k, -1, -1)]


def pdeg(p):
    return max((i + j for i, j in p), default=0)


def padd(p, q, sign=1):
    out = dict(p)
    for m, c in q.items():
        out[m] = out.get(m, 0) + sign * c
    return {m: c for m, c in out.items() if c}


def pmul(p, q):
    out = {}
    for (a, b), c in p.items():
        for (e, f), k in q.items():
            key = (a + e, b + f)
            out[key] = out.get(key, 0) + c * k
    return {m: c for m, c in out.items() if c}


def _power(p, n, cache):
    if n == 0:
        return {(0, 0): 1}
    if n not in cache:
        cache[n] = pmul(_power(p, n - 1, cache), p)
    return cache[n]


def pdiff(p, var):
    out = {}
    for (i, j), c in p.items():
        e = (i, j)[var]
        if e:
            key = (i - 1, j) if var == 0 else (i, j - 1)
            out[key] = out.get(key, 0) + c * e
    return out


def compose(p, a, b):
    """p(a, b) for polynomials a, b."""
    out = {}
    pa, pb = {}, {}
    for (i, j), c in p.items():
        term = pmul(_power(a, i, pa), _power(b, j, pb))
        for m, k in term.items():
            out[m] = out.get(m, 0) + c * k
    return {m: c for m, c in out.items() if c}


def jacobian_minus_one(f, g):
    """det d(x+f, y+g)/d(x,y) - 1 = f_x + g_y + f_x g_y - f_y g_x."""
    fx, fy, gx, gy = pdiff(f, 0), pdiff(f, 1), pdiff(g, 0), pdiff(g, 1)
    return padd(padd(padd(fx, gy), pmul(fx, gy)), pmul(fy, gx), -1)


def peval(p, x, y):
    return sum(c * x ** i * y ** j for (i, j), c in p.items())


def grid(degree):
    """Unisolvent lattice points for polynomials of total degree <= degree."""
    return [(u, v) for u in range(degree + 1) for v in range(degree + 1 - u)]
