#!/usr/bin/env python3
"""A closure-pruned, symmetry-canonical generator for union-closed families.

Every finite nonempty union-closed family with nonempty support contains the
union U of its members. Generate full-support families on [n] from {U},
deciding subsets in decreasing cardinality. The include branch is taken only
when all unions with existing members are already present. Relabel by S_n and
emit only the least bitmask in each orbit.

Proved construction logic in research/M075_CANONICAL.md. This is a classical
finite enumeration method, NOT a new proof of Frankl's conjecture.
"""
import argparse
from functools import lru_cache
from itertools import islice, permutations
import json
from math import comb

EXHAUSTIVE_COUNTS = {1: 2, 2: 8, 3: 90, 4: 4542, 5: 2747402}
# Independent n<=4 totals also reproduced by the existing frankl_orbits mine.
ORBIT_COUNTS = {1: 2, 2: 6, 3: 28, 4: 330}


def _n(n):
    if type(n) is not int or not 1 <= n <= 5:
        raise ValueError("n must be in 1..5; this engine is deliberately finite")
    return n


@lru_cache(None)
def subset_actions(n):
    """All S_n actions on 2^[n], including the identity."""
    _n(n)
    return tuple(
        tuple(sum(1 << perm[i] for i in range(n) if subset >> i & 1)
              for subset in range(1 << n))
        for perm in permutations(range(n))
    )


def relabel_family(encoded, subset_action):
    """A set family is a bitset indexed by its constituent subset masks."""
    out = 0
    while encoded:
        bit = encoded & -encoded
        out |= 1 << subset_action[bit.bit_length() - 1]
        encoded ^= bit
    return out


def canonical(encoded, n):
    _n(n)
    _check_encoding(encoded, n)
    return min(relabel_family(encoded, action) for action in subset_actions(n))


def is_canonical(encoded, n):
    """Short-circuit as soon as a smaller relabeling is found."""
    _n(n)
    _check_encoding(encoded, n)
    return all(relabel_family(encoded, action) >= encoded
               for action in subset_actions(n))


def _check_encoding(encoded, n):
    if type(encoded) is not int or not 0 <= encoded < (1 << (1 << n)):
        raise ValueError("family encoding out of range")


def includes_unions(encoded, subset):
    """A member may be added iff its unions with old members are present."""
    existing = encoded
    while existing:
        bit = existing & -existing
        old = bit.bit_length() - 1
        joined = old | subset
        if joined != subset and not (encoded >> joined & 1):
            return False
        existing ^= bit
    return True


def full_support_families(n):
    """Yield every full-support union-closed family exactly once, without 2^(2^n) scanning.

    The union U of all members is required to be present. Every subset except
    U is decided once, larger subsets first. An invalid include is omitted,
    since no later smaller subset can supply the missing union.
    """
    _n(n)
    top = (1 << n) - 1
    candidates = sorted(range(top), key=lambda s: (-s.bit_count(), -s))

    def walk(index, family):
        if index == len(candidates):
            yield family
            return
        subset = candidates[index]
        yield from walk(index + 1, family)  # exclusion
        if includes_unions(family, subset):
            yield from walk(index + 1, family | (1 << subset))

    yield from walk(0, 1 << top)


def canonical_representatives(n):
    """Each S_n orbit of full-support union-closed families occurs exactly once."""
    for family in full_support_families(n):
        if is_canonical(family, n):
            yield family


def summary():
    labeled = {str(n): sum(1 for _ in full_support_families(n)) for n in range(1, 6)}
    orbits = {str(n): sum(1 for _ in canonical_representatives(n)) for n in range(1, 5)}
    # Families on a fixed n-element universe can have unused ground elements.
    # Partition by the exact support subset to reconstruct the old n=4 census.
    fixed_n4 = sum(comb(4, k) * labeled[str(k)] for k in range(1, 5))
    all_orbits_n4 = sum(orbits.values())
    if labeled != {str(k): v for k, v in EXHAUSTIVE_COUNTS.items()}:
        raise ValueError("full-support family count disagrees with published sequence")
    if orbits != {str(k): v for k, v in ORBIT_COUNTS.items()}:
        raise ValueError("canonical orbit count disagrees with known finite census")
    if fixed_n4 != 4958 or all_orbits_n4 != 366:
        raise ValueError("n=4 independent census decomposition failed")
    return {
        "full_support_labeled": labeled,
        "full_support_orbits": orbits,
        "all_supports_labeled_n4": fixed_n4,
        "all_supports_orbits_n4": all_orbits_n4,
        "n5_orbits": "not computed by this check",
        "scope": "Known finite enumeration and exact orbit canonicalization only; not a proof of Frankl.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="recompute known n<=5 labeled / n<=4 orbit baselines")
    parser.add_argument("--n", type=int, default=4)
    parser.add_argument("--limit", type=int, default=10,
                        help="max canonical representatives to print, n=5 capped")
    args = parser.parse_args(argv)
    try:
        if args.check:
            print(json.dumps(summary(), sort_keys=True, indent=2))
            return 0
        _n(args.n)
        if type(args.limit) is not int or args.limit < 1 or args.limit > 1000:
            raise ValueError("limit must be 1..1000; use --check for audited counts")
        examples = list(islice(canonical_representatives(args.n), args.limit))
        print(json.dumps({
            "ground_set": args.n, "representatives_shown": len(examples),
            "prefix_only": True, "families": examples,
        }, indent=2))
        return 0
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
