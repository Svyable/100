"""Union-closed families up to ground-set size 4, one per ground-set symmetry.

Search canonises by the minimum bitmask over S_n. The checker canonises by the
minimum sorted subset-tuple and recomputes the minimum abundance. n = 4 is the
exhaustive limit of the existing verifier. This is not a proof of Frankl.
"""
from fractions import Fraction
from itertools import permutations

from probes.core import fraction_text, require

MINE = {
    "id": "frankl_orbits",
    "problem_id": "M075",
    "title": "Orbits of union-closed families under ground-set permutation",
    "engines": ["symmetry_reduction"],
    "frontier": ("Exhaustive verification for ground sets of size at most 4 is already in this repository. "
                 "The orbit count is the symmetry reduction the n = 5 enumeration still needs. Not a theorem."),
    "levels": {"smoke": {"max_n": 4}},
}


def scope(params):
    return (f"Every nontrivial union-closed family on a ground set of size at most {params['max_n']} "
            "satisfies Frankl's abundance bound, and the number of families up to relabelling is the recorded orbit count.")


def _image_subset(subset, perm):
    out = 0
    bit = 0
    while subset:
        if subset & 1:
            out |= 1 << perm[bit]
        subset >>= 1
        bit += 1
    return out


def _members(encoded, n):
    return [s for s in range(1 << n) if encoded >> s & 1]


def _valid(encoded, n):
    members = _members(encoded, n)
    if not members or max(members) == 0:
        return False
    present = set(members)
    return all((a | b) in present for a in present for b in present)


def _abundance(encoded, n):
    members = _members(encoded, n)
    present = set(members)
    largest = max(sum(bool(mask & (1 << i)) for mask in present) for i in range(n))
    return Fraction(largest, len(present))


def _bit_canon(encoded, n, group):
    universe = 1 << n

    def permute(perm):
        out = 0
        for subset in range(universe):
            if encoded >> subset & 1:
                out |= 1 << _image_subset(subset, perm)
        return out

    return min(permute(perm) for perm in group)


def _tuple_canon(encoded, n, group):
    members = _members(encoded, n)
    best = None
    for perm in group:
        image = tuple(sorted(_image_subset(subset, perm) for subset in members))
        if best is None or image < best:
            best = image
    return best


def _summarise(max_n, canon):
    orbits = {}
    families = {}
    least = None
    for n in range(1, max_n + 1):
        group = list(permutations(range(n)))
        seen = set()
        count = 0
        for encoded in range(1 << (1 << n)):
            if not _valid(encoded, n):
                continue
            count += 1
            seen.add(canon(encoded, n, group))
            abundance = _abundance(encoded, n)
            require(abundance >= Fraction(1, 2), f"n={n}: abundance {abundance} is below 1/2")
            least = abundance if least is None or abundance < least else least
        orbits[str(n)] = len(seen)
        families[str(n)] = count
    return {
        "max_n": max_n,
        "orbits": orbits,
        "families": families,
        "minimum_abundance": fraction_text(least),
    }


def search(params):
    summary = _summarise(params["max_n"], _bit_canon)
    return {"holds": True, "summary": summary, "certificate": summary}


def check(params, result):
    summary = _summarise(params["max_n"], _tuple_canon)
    require(result["summary"] == summary, "orbit table does not match the subset-tuple canonisation")
    require(result["certificate"] == summary, "certificate is not the checked orbit table")
    require(Fraction(summary["minimum_abundance"]) >= Fraction(1, 2), "minimum abundance is below 1/2")
