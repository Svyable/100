"""How the unit-fraction search solves primes n = 1 (mod 24). Reproduction only."""
from collections import Counter

from probes.core import digest, require
from probes.erdos_straus import solve
from probes.primes import odd_sieve

MINE = {
    "id": "straus_patterns",
    "problem_id": "M019",
    "title": "Erdos-Straus residue patterns for primes 1 mod 24",
    "engines": ["primes"],
    "frontier": ("Classical identities leave n = 1 (mod 24) uncovered. "
                 "The table clusters one explicit solution per such prime in a finite range. "
                 "It is not an identity and not a proof."),
    "levels": {"smoke": {"limit": 8000}},
}


def scope(params):
    return (f"Every prime n <= {params['limit']} with n = 1 (mod 24) has an explicit positive "
            "solution of 4/n = 1/x + 1/y + 1/z, grouped by the residue 4x - n.")


def _primes(limit):
    prime = odd_sieve(limit)
    return [n for n in range(2, limit + 1) if n % 24 == 1 and prime(n)]


def search(params):
    limit = params["limit"]
    rows = []
    for n in _primes(limit):
        found = solve(n)
        if found is None:
            return {"holds": False, "summary": {"limit": limit, "counterexample": n},
                    "certificate": {"counterexample": n}}
        x, y, z = sorted(found)
        rows.append({"n": n, "x": x, "y": y, "z": z, "residue": 4 * x - n})
    counts = Counter(row["residue"] for row in rows)
    summary = {
        "limit": limit,
        "primes": len(rows),
        "residues": sorted(counts),
        "by_residue": {str(k): counts[k] for k in sorted(counts)},
        "rows_sha256": digest(rows),
    }
    return {"holds": True, "summary": summary, "certificate": {"rows": rows}}


def check(params, result):
    limit = params["limit"]
    if not result["holds"]:
        n = result["certificate"]["counterexample"]
        require(n in _primes(limit), "counterexample is not a prime 1 mod 24 in range")
        return
    rows = result["certificate"]["rows"]
    require([row["n"] for row in rows] == _primes(limit), "the prime list is not exactly n = 1 (mod 24)")
    counts = Counter()
    for row in rows:
        n, x, y, z = row["n"], row["x"], row["y"], row["z"]
        require(1 <= x <= y <= z, f"unordered triple at n={n}")
        require(4 * x * y * z == n * (x * y + y * z + z * x), f"equation fails at n={n}")
        require(row["residue"] == 4 * x - n, f"residue mismatch at n={n}")
        counts[row["residue"]] += 1
    summary = result["summary"]
    require(summary["primes"] == len(rows), "prime count mismatch")
    require(summary["residues"] == sorted(counts), "residue set mismatch")
    require(summary["by_residue"] == {str(k): counts[k] for k in sorted(counts)}, "residue counts mismatch")
    require(summary["rows_sha256"] == digest(rows), "row hash mismatch")
