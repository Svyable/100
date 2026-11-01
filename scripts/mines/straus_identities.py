"""Parametric Erdős–Straus identities read off the residue-3/7 mine clusters.

The search path proves each family as a polynomial identity and counts how many
primes n <= N with n = 1 (mod 24) fall into one of them. The checker rebuilds
the triples from the closed forms and re-verifies the cleared equation without
calling the search. These identities are classical in style; they are not a
proof of the full conjecture and cannot enter Solved.
"""
from straus_identities import FAMILIES, coverage_report, first_cover, prove_all

from probes.core import digest, require

MINE = {
    "id": "straus_identities",
    "problem_id": "M019",
    "title": "Parametric identities for primes 1 mod 24",
    "engines": ["primes"],
    "frontier": (
        "Classical Mordell-type identities already cover many arithmetic progressions "
        "inside n = 1 (mod 24). The families here are extracted from the residue mine "
        "and proved as polynomial identities; they do not finish the uncovered progressions "
        "n = 1 or 49 (mod 120), and a finite list of polynomial identities cannot cover "
        "every such n."
    ),
    "levels": {"smoke": {"limit": 8000}},
}


def scope(params):
    return (
        f"Nine polynomial identities give explicit 4/n = 1/x+1/y+1/z solutions on "
        f"named arithmetic progressions inside n = 1 (mod 24); prime coverage is "
        f"reported through {params['limit']}."
    )


def search(params):
    limit = params["limit"]
    prove_all()
    report = coverage_report(limit)
    families = []
    for family in FAMILIES:
        samples = []
        for t in range(0, 5):
            n, x, y, z = family.triple(t)
            samples.append({"t": t, "n": n, "x": x, "y": y, "z": z})
        families.append(
            {
                "id": family.id,
                "modulus": family.modulus,
                "offset": family.offset,
                "residue": family.residue,
                "title": family.title,
                "prime_hits": report["by_family"][family.id],
                "samples": samples,
            }
        )
    summary = {
        "limit": limit,
        "families": len(FAMILIES),
        "primes_1_mod_24": report["primes_1_mod_24"],
        "covered_primes": report["covered"],
        "uncovered_primes": len(report["uncovered"]),
        "uncovered_mod_120": report["uncovered_mod_120"],
        "by_family": report["by_family"],
        "family_ids": report["family_ids"],
        "families_sha256": digest(families),
    }
    return {
        "holds": True,
        "summary": summary,
        "certificate": {
            "families": families,
            "uncovered": report["uncovered"],
        },
    }


def check(params, result):
    require(result["holds"], "identity mine must hold")
    limit = params["limit"]
    prove_all()
    report = coverage_report(limit)
    summary = result["summary"]
    cert = result["certificate"]
    require(summary["families"] == len(FAMILIES), "family count mismatch")
    require(summary["primes_1_mod_24"] == report["primes_1_mod_24"], "prime count mismatch")
    require(summary["covered_primes"] == report["covered"], "coverage mismatch")
    require(summary["uncovered_primes"] == len(report["uncovered"]), "uncovered count mismatch")
    require(summary["uncovered_mod_120"] == report["uncovered_mod_120"], "uncovered moduli mismatch")
    require(summary["by_family"] == report["by_family"], "per-family counts mismatch")
    require(cert["uncovered"] == report["uncovered"], "uncovered list mismatch")
    rebuilt = []
    for family in FAMILIES:
        samples = []
        for t in range(0, 5):
            n, x, y, z = family.triple(t)
            require(4 * x - n == family.residue, f"{family.id}: residue at t={t}")
            require(
                4 * x * y * z == n * (x * y + y * z + z * x),
                f"{family.id}: equation at t={t}",
            )
            samples.append({"t": t, "n": n, "x": x, "y": y, "z": z})
        rebuilt.append(
            {
                "id": family.id,
                "modulus": family.modulus,
                "offset": family.offset,
                "residue": family.residue,
                "title": family.title,
                "prime_hits": report["by_family"][family.id],
                "samples": samples,
            }
        )
    require(cert["families"] == rebuilt, "family certificate mismatch")
    require(summary["families_sha256"] == digest(rebuilt), "family hash mismatch")
    # Every covered prime in the report is hit by the closed form, not by a search.
    flags_limit = limit
    from straus_identities import odd_prime_flags

    flags = odd_prime_flags(flags_limit)
    for n in range(2, flags_limit + 1):
        if n % 24 != 1 or not flags[n]:
            continue
        family = first_cover(n)
        if n in report["uncovered"]:
            require(family is None, f"listed uncovered prime {n} is covered")
        else:
            require(family is not None, f"prime {n} has no closed form")
            _n, x, y, z = family.triple((n - family.offset) // family.modulus)
            require(_n == n and 4 * x * y * z == n * (x * y + y * z + z * x), f"bad cover at {n}")
