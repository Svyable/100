"""M006 - Strong Goldbach: every even 4 <= n <= N is a sum of two primes."""
from .core import digest, require
from .primes import is_prime, odd_sieve, sieve

PROBE = {
    "id": "goldbach",
    "problem_id": "M006",
    "title": "Goldbach partitions for every even integer up to N",
    "engines": ["primes"],
    "frontier": ("Known: verified for every even n <= 4*10^18 (Oliveira e Silva, Herzog & Pardi, "
                 "Math. Comp. 83 (2014)). This range reproduces known mathematics only."),
    "levels": {"smoke": {"limit": 200000}, "deep": {"limit": 4000000}},
}


def scope(params):
    return f"Every even integer 4 <= n <= {params['limit']:,} is p + q with p, q prime."


def search(params):
    limit = params["limit"]
    flags = sieve(limit)
    primes = [p for p in range(2, limit + 1) if flags[p]]
    least = []
    record = (0, 0)
    for n in range(4, limit + 1, 2):
        for p in primes:
            if flags[n - p]:
                break
            if 2 * p > n:
                return {"holds": False, "summary": {"limit": limit},
                        "certificate": {"counterexample": {"n": n}}}
        least.append(p)
        if p > record[0]:
            record = (p, n)
    return {
        "holds": True,
        "summary": {
            "limit": limit,
            "even_integers_checked": len(least),
            "largest_least_prime": record[0],
            "attained_at": record[1],
            "partitions_sha256": digest(least),
        },
        "certificate": {"least_prime": least},
    }


def check(params, result):
    limit = params["limit"]
    if not result["holds"]:
        n = result["certificate"]["counterexample"]["n"]
        prime = odd_sieve(n)
        require(n % 2 == 0 and n >= 4, "counterexample must be an even integer >= 4")
        require(not any(prime(p) and prime(n - p) for p in range(2, n // 2 + 1)),
                "claimed counterexample actually has a Goldbach partition")
        return
    least = result["certificate"]["least_prime"]
    require(len(least) == (limit - 2) // 2, "one partition per even n required")
    # Independent primality oracles: an odd-only sieve (different code from the search's sieve)
    # for every n, plus deterministic Miller-Rabin on each partition for runs up to 300,000.
    sieve_prime = odd_sieve(limit)
    for k, p in enumerate(least):
        n = 4 + 2 * k
        require(2 <= p <= n - 2 and sieve_prime(p) and sieve_prime(n - p),
                f"invalid Goldbach partition for n={n}: {p} + {n - p}")
        require(not any(sieve_prime(r) and sieve_prime(n - r) for r in range(2, p)),
                f"partition for n={n} is not the least")
    if limit <= 300000:
        require(all(is_prime(p) and is_prime(4 + 2 * k - p) for k, p in enumerate(least)),
                "Miller-Rabin rejects a partition")
    record = max(range(len(least)), key=lambda k: (least[k], -k))
    summary = result["summary"]
    require(summary["largest_least_prime"] == least[record]
            and summary["attained_at"] == 4 + 2 * record
            and summary["partitions_sha256"] == digest(least),
            "summary does not match certificate")
