"""M096 - Finite projective planes: PG(2,q) certificates and the Bruck-Ryser sieve.

Search side builds PG(2,q) over GF(q) for every prime power q <= Q.
Check side verifies the incidence axioms *combinatorially* from the line
lists alone (no field arithmetic), and recomputes Bruck-Ryser exclusions by
brute-force sums of two squares.
"""
from .core import digest, require
from .fields import field, prime_power, projective_points

PROBE = {
    "id": "projective_planes",
    "problem_id": "M096",
    "title": "Projective planes of prime-power order and the Bruck-Ryser order sieve",
    "engines": ["finite_fields"],
    "frontier": ("Known: order 10 excluded by computer search (Lam, Thiel & Swiercz 1989); "
                 "12 is the smallest order whose existence is open. Every known plane has "
                 "prime-power order."),
    "levels": {"smoke": {"max_q": 9, "table_limit": 50}, "deep": {"max_q": 27, "table_limit": 200}},
}

EXTERNAL_EXCLUSIONS = {10: "Lam, Thiel & Swiercz (1989) exhaustive computer search"}


def scope(params):
    return (f"PG(2,q) satisfies the projective-plane axioms for every prime power q <= {params['max_q']}; "
            f"Bruck-Ryser classification of every order n <= {params['table_limit']}.")


def plane(q):
    F = field(q)
    pts = projective_points(F)
    index = {p: i for i, p in enumerate(pts)}
    lines = []
    for L in pts:
        on = [index[p] for p in pts
              if F.add(F.add(F.mul(L[0], p[0]), F.mul(L[1], p[1])), F.mul(L[2], p[2])) == 0]
        lines.append(sorted(on))
    return lines


def _two_squares_by_factoring(n):
    """Fermat: n is a sum of two squares iff primes = 3 mod 4 occur to even powers."""
    m, p = n, 2
    while p * p <= m:
        e = 0
        while m % p == 0:
            m //= p
            e += 1
        if p % 4 == 3 and e % 2:
            return False
        p += 1
    return not (m > 1 and m % 4 == 3)


def classify(n):
    if prime_power(n):
        return "exists (prime power)"
    if n % 4 in (1, 2) and not _two_squares_by_factoring(n):
        return "excluded (Bruck-Ryser)"
    if n in EXTERNAL_EXCLUSIONS:
        return "excluded (external computer proof)"
    return "open"


def search(params):
    qs = [q for q in range(2, params["max_q"] + 1) if prime_power(q)]
    planes = {str(q): plane(q) for q in qs}
    table = {str(n): classify(n) for n in range(2, params["table_limit"] + 1)}
    return {
        "holds": True,
        "summary": {
            "orders_constructed": qs,
            "bruck_ryser_excluded": [int(n) for n, s in table.items() if s.startswith("excluded (B")],
            "open_orders": [int(n) for n, s in table.items() if s == "open"],
            "smallest_open_order": min(int(n) for n, s in table.items() if s == "open"),
            "planes_sha256": digest(planes),
        },
        "certificate": {"planes": planes, "table": table},
    }


def check(params, result):
    planes = result["certificate"]["planes"]
    for key, lines in planes.items():
        q = int(key)
        v = q * q + q + 1
        require(len(lines) == v, f"PG(2,{q}): need {v} lines")
        masks = []
        for line in lines:
            require(len(line) == q + 1 and len(set(line)) == q + 1
                    and all(0 <= x < v for x in line), f"PG(2,{q}): bad line {line}")
            masks.append(sum(1 << x for x in line))
        require(len(set(masks)) == v, f"PG(2,{q}): repeated line")
        for i in range(v):
            for j in range(i + 1, v):
                require(bin(masks[i] & masks[j]).count("1") == 1,
                        f"PG(2,{q}): lines {i},{j} do not meet in exactly one point")
        through = [0] * v
        for k, m in enumerate(masks):
            for x in range(v):
                if m >> x & 1:
                    through[x] |= 1 << k
        for x in range(v):
            for y in range(x + 1, v):
                require(bin(through[x] & through[y]).count("1") == 1,
                        f"PG(2,{q}): points {x},{y} are not joined by exactly one line")
    table = result["certificate"]["table"]
    for key, status in table.items():
        n = int(key)
        sum2 = any(a * a + b * b == n for a in range(int(n ** 0.5) + 1) for b in range(a, int(n ** 0.5) + 1))
        if status == "excluded (Bruck-Ryser)":
            require(n % 4 in (1, 2) and not sum2, f"order {n} wrongly excluded")
        else:
            require(not (n % 4 in (1, 2) and not sum2), f"order {n} should be Bruck-Ryser excluded")
        if status.startswith("exists"):
            require(key in planes or n > params["max_q"], f"order {n} claimed constructed")
    require(result["summary"]["planes_sha256"] == digest(planes), "summary hash mismatch")
