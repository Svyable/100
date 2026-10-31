"""M019 - Erdos-Straus: 4/n = 1/x + 1/y + 1/z in positive integers for 2 <= n <= N."""
from math import gcd

from .core import digest, require

PROBE = {
    "id": "erdos_straus",
    "problem_id": "M019",
    "title": "Erdos-Straus unit-fraction certificates for every n up to N",
    "engines": ["primes"],
    "frontier": ("Known: computational verification is reported far beyond this range "
                 "(at least 10^14 in the literature). Reproduction only."),
    "levels": {"smoke": {"limit": 20000}, "deep": {"limit": 1000000}},
}


def scope(params):
    return (f"For every integer 2 <= n <= {params['limit']:,}, explicit positive integers x <= y <= z "
            "with 4xyz = n(xy + yz + zx).")


def _factor(n, out=None):
    out = {} if out is None else out
    p = 2
    while p * p <= n:
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
        p += 1 if p == 2 else 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def _two_terms(a, b, factors_b):
    """Some y <= z with 1/y + 1/z = a/b, via (ay - b)(az - b) = b^2 and d = ay - b <= b."""
    divs = [1]
    for p, e in factors_b.items():
        divs = [d * p ** k for d in divs for k in range(2 * e + 1) if d * p ** k <= b]
    for d in sorted(divs, reverse=True):          # large d first gives small z
        if (d + b) % a == 0 and (b * b // d + b) % a == 0:
            return (d + b) // a, (b * b // d + b) // a
    return None


def solve(n):
    if n % 2 == 0:
        return (n // 2, n, n) if n > 2 else (1, 2, 2)
    if n % 4 == 3:
        return ((n + 1) // 4, n * (n + 1) // 2, n * (n + 1) // 2)
    for x in range(n // 4 + 1, n + 1):
        a, b = 4 * x - n, n * x
        g = gcd(a, b)
        a, b = a // g, b // g
        found = _two_terms(a, b, _factor(b // n, _factor(n)) if b % n == 0 else _factor(b))
        if found:
            return (x,) + found
    return None


def search(params):
    limit = params["limit"]
    triples = []
    for n in range(2, limit + 1):
        t = solve(n)
        if t is None:
            return {"holds": False, "summary": {"limit": limit},
                    "certificate": {"counterexample": {"n": n}}}
        triples.append(sorted(t))
    return {
        "holds": True,
        "summary": {
            "limit": limit,
            "integers_certified": len(triples),
            "searched_n_equiv_1_mod_4": sum(1 for n in range(2, limit + 1) if n % 4 == 1),
            "triples_sha256": digest(triples),
        },
        "certificate": {"triples": triples},
    }


def check(params, result):
    require(result["holds"], "a finite search failure is not a counterexample; "
            "nonexistence of a triple would need a separate proof")
    triples = result["certificate"]["triples"]
    require(len(triples) == params["limit"] - 1, "one triple per n required")
    for k, (x, y, z) in enumerate(triples):
        n = k + 2
        require(0 < x <= y <= z and 4 * x * y * z == n * (x * y + y * z + z * x),
                f"invalid Erdos-Straus certificate for n={n}: {(x, y, z)}")
    require(result["summary"]["triples_sha256"] == digest(triples), "summary hash mismatch")
