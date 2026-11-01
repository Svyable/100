"""Explicit upper bound on the least Goldbach prime inside the growth mine.

For every even n with 4 <= n <= N, if p is the least prime with n-p prime, then
p <= floor(3 (ln n)^2). The bound is checked on every even n and, independently,
on the running-maximum record list (which dominates the intermediate values for
this increasing right-hand side). Known range only; not a new asymptotic theorem.
"""
import math

from probes.core import digest, require
from probes.primes import odd_sieve, sieve

MINE = {
    "id": "goldbach_bound",
    "problem_id": "M006",
    "title": "Explicit least-Goldbach-prime bound through 20,000",
    "engines": ["primes"],
    "frontier": (
        "Known through 4*10^18 (Oliveira e Silva, Herzog and Pardi, 2014). "
        "The inequality p <= floor(3 (ln n)^2) is certified only for 4 <= n <= 20000; "
        "it is not an asymptotic theorem and cannot enter Solved."
    ),
    "levels": {"smoke": {"limit": 20000}},
}

BOUND_FACTOR = 3


def scope(params):
    return (
        f"For every even n with 4 <= n <= {params['limit']}, the least prime p such that "
        f"n-p is prime satisfies p <= floor({BOUND_FACTOR} (ln n)^2)."
    )


def bound(n: int) -> int:
    return math.floor(BOUND_FACTOR * (math.log(n) ** 2))


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
        found = None
        for p in primes:
            if flags[n - p]:
                found = p
                break
            if 2 * p > n:
                break
        if found is None:
            return {
                "holds": False,
                "summary": {"limit": limit, "counterexample": n},
                "certificate": {"counterexample": n},
            }
        if found > bound(n):
            return {
                "holds": False,
                "summary": {"limit": limit, "bound_counterexample": [n, found, bound(n)]},
                "certificate": {"bound_counterexample": [n, found, bound(n)]},
            }
        least.append(found)
    records = _records(least)
    worst = max((p / (math.log(n) ** 2), n, p, bound(n)) for n, p in records)
    summary = {
        "limit": limit,
        "even_integers": len(least),
        "bound_factor": BOUND_FACTOR,
        "bound_formula": f"floor({BOUND_FACTOR}*(ln n)^2)",
        "record_count": len(records),
        "records": records,
        "worst_record_ratio": round(worst[0], 6),
        "worst_record_n": worst[1],
        "worst_record_prime": worst[2],
        "worst_record_bound": worst[3],
        "records_sha256": digest(records),
    }
    return {"holds": True, "summary": summary, "certificate": {"least": least, "records": records}}


def check(params, result):
    limit = params["limit"]
    require(result["holds"], "bound mine must hold inside the declared range")
    prime = odd_sieve(limit)
    least = result["certificate"]["least"]
    require(len(least) == (limit - 2) // 2, "one least prime per even n")
    records = []
    best = 0
    for k, p in enumerate(least):
        n = 4 + 2 * k
        require(prime(p) and prime(n - p), f"composite Goldbach part at n={n}")
        require(all(not prime(q) or not prime(n - q) for q in range(2, p)), f"not least at n={n}")
        require(p <= bound(n), f"bound fails at n={n}: p={p} > {bound(n)}")
        if p > best:
            best = p
            records.append([n, p])
    summary = result["summary"]
    require(records == summary["records"] == result["certificate"]["records"], "record list mismatch")
    require(summary["records_sha256"] == digest(records), "record hash mismatch")
    require(summary["bound_factor"] == BOUND_FACTOR, "bound factor mismatch")
    require(summary["record_count"] == len(records) == 12, "expected twelve records through 20000")
    require(summary["worst_record_n"] == 7426, "worst ratio should occur at the final record")
    require(summary["worst_record_prime"] == 173, "final record prime mismatch")
