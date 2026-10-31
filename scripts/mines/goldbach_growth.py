"""Record-setting least Goldbach primes. Known range only; not a new bound."""
from probes.core import digest, require
from probes.primes import odd_sieve, sieve

MINE = {
    "id": "goldbach_growth",
    "problem_id": "M006",
    "title": "Running-maximum least Goldbach prime",
    "engines": ["primes"],
    "frontier": ("Known through 4*10^18 (Oliveira e Silva, Herzog and Pardi, 2014). "
                 "This table only locates the record least primes inside a tiny initial segment."),
    "levels": {"smoke": {"limit": 20000}},
}


def scope(params):
    return (f"For every even n with 4 <= n <= {params['limit']}, the least prime p such that "
            "n-p is prime, and the pairs (n, p) where that least prime sets a new record.")


def _records(least):
    records, best = [], 0
    for k, p in enumerate(least):
        if p > best:
            best = p
            records.append([4 + 2 * k, p])
    return records


def search(params):
    limit = params["limit"]
    flags = sieve(limit)
    primes = [p for p in range(2, limit + 1) if flags[p]]
    least = []
    for n in range(4, limit + 1, 2):
        for p in primes:
            if flags[n - p]:
                least.append(p)
                break
            if 2 * p > n:
                return {"holds": False, "summary": {"limit": limit, "counterexample": n},
                        "certificate": {"counterexample": n}}
    records = _records(least)
    summary = {
        "limit": limit,
        "even_integers": len(least),
        "record_count": len(records),
        "largest_least_prime": records[-1][1],
        "attained_at": records[-1][0],
        "records": records,
        "records_sha256": digest(records),
    }
    return {"holds": True, "summary": summary, "certificate": {"records": records}}


def check(params, result):
    limit = params["limit"]
    if not result["holds"]:
        n = result["certificate"]["counterexample"]
        prime = odd_sieve(n)
        require(n % 2 == 0 and 4 <= n <= limit, "counterexample out of range")
        require(not any(prime(p) and prime(n - p) for p in range(2, n // 2 + 1)),
                "claimed Goldbach failure has a partition")
        return
    prime = odd_sieve(limit)
    least = []
    for n in range(4, limit + 1, 2):
        found = None
        for p in range(2, n // 2 + 1):
            if prime(p) and prime(n - p):
                found = p
                break
        require(found is not None, f"no Goldbach partition for {n}")
        least.append(found)
    records = _records(least)
    summary = result["summary"]
    require(summary["records"] == records, "record table does not match an independent sieve")
    require(summary["record_count"] == len(records)
            and summary["largest_least_prime"] == records[-1][1]
            and summary["attained_at"] == records[-1][0]
            and summary["even_integers"] == len(least)
            and summary["records_sha256"] == digest(records),
            "summary does not match the record table")
    require(result["certificate"]["records"] == records, "certificate records differ")
