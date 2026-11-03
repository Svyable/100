#!/usr/bin/env python3
"""A sound orbit-by-orbit augmentation for union-closed families (M075).

The *naive* rule 'canonical child must have a canonical deletion-parent'
is false, already on three ground elements. We preserve complete orbits by
canonicalizing each valid augmentation of canonical *parent orbits* instead.

General proofs and prior-art boundaries: research/M075_AUGMENTATION.md.
Counts through n=4 reproduce known mathematics; not a Frankl proof.
"""
import argparse
import json

from frankl_canonical import (
    canonical, canonical_representatives, includes_unions, is_canonical,
    relabel_family, subset_actions,
)

EXPECTED_LEVELS = {
    1: [1, 1],
    2: [1, 2, 2, 1],
    3: [1, 3, 5, 7, 6, 3, 2, 1],
    4: [1, 4, 10, 20, 34, 45, 49, 49, 42, 30, 21, 13, 6, 3, 2, 1],
}
NAIVE_LEVELS = {
    3: [1, 3, 4, 2],
    4: [1, 4, 8, 10, 7, 2],
}


def checked_n(n):
    if type(n) is not int or n not in (1, 2, 3, 4):
        raise ValueError("Exact orbit census restricted to 1 <= n <= 4")
    return n


def members(family, n):
    return tuple(s for s in range(1 << n) if family & (1 << s))


def is_union_closed(family, n):
    sets = members(family, n)
    return all(family & (1 << (a | b)) for a in sets for b in sets)


def deletion_parent(family, n):
    """Delete a smallest-cardinality member (tie: smallest subset mask).

    With at least two members, this is a union-closed full-support parent.
    Not equivariant as a *labeled integer* or necessarily canonical.
    """
    top = (1 << n) - 1
    sets = members(family, n)
    if len(sets) <= 1 or top not in sets:
        raise ValueError("A nonroot full-support family is required")
    deleted = min((s for s in sets if s != top),
                  key=lambda s: (s.bit_count(), s))
    return family ^ (1 << deleted), deleted


def orbit_layers(n, naive_parent_test=False):
    """Return size-graded sets of all *canonical* full-support orbit reps.

    For valid, safe enumeration, do not require that deleting the chosen
    member from the canonicalized child gives the canonical parent.
    The naive_parent_test option deliberately performs that unsound test
    only to record its finite failure, never to prove completeness.
    """
    checked_n(n)
    top = (1 << n) - 1
    layers = [{1 << top}]
    for size in range(1, 1 << n):
        following = set()
        for parent in layers[-1]:
            smallest = min(s.bit_count() for s in members(parent, n))
            for candidate in range(top):
                if parent & (1 << candidate):
                    continue
                # A minimum-cardinality deletion in some relabeling of
                # any target family gives an augmentation in this range.
                if candidate.bit_count() > smallest:
                    continue
                if not includes_unions(parent, candidate):
                    continue
                child = canonical(parent | (1 << candidate), n)
                if naive_parent_test:
                    deleted_parent, _ = deletion_parent(child, n)
                    if deleted_parent != parent:
                        continue
                following.add(child)
        if not following:
            break
        layers.append(following)
    return layers


def obstruction(n):
    """One explicit counterexample to strict canonical-parent inheritance.

    F_n = {{0},{1},{0,1},[n]}, n >= 3; n <= 5 checked here.
    """
    if type(n) is not int or n not in (3, 4, 5):
        raise ValueError("Explicit obstruction is checked at n=3,4,5")
    top = (1 << n) - 1
    family = sum(1 << s for s in (1, 2, 3, top))
    parent, removed = deletion_parent(family, n)
    reparent = canonical(parent, n)
    if (not is_union_closed(family, n)
            or not is_union_closed(parent, n)
            or canonical(family, n) != family
            or not reparent < parent
            or removed != 1):
        raise AssertionError("Explicit canonical-parent obstruction failed")
    return {
        "n": n, "canonical_child": family,
        "deleted_subset": removed,
        "deletion_parent": parent,
        "canonical_parent": reparent,
        "child_sets": list(members(family, n)),
        "parent_sets": list(members(parent, n)),
    }



def stronger_obstruction(n):
    """All minimum-cardinality deletion-parents are noncanonical.

    F_n = {{1,2},{0,3},{0,1,2,3},[n]}, n >= 4;
    the four-set union is duplicated with [n] when n=4.
    Under relabeling, the quadruple mask is at least 15; once it is
    minimized, the least disjoint-doubleton pair has masks {6,9}.
    After deleting either doubleton, its mate can be relabeled to mask 3.
    """
    if type(n) is not int or n not in (4, 5):
        raise ValueError("Explicit stronger witness is checked at n=4,5")
    top = (1 << n) - 1
    family = (1 << 6) | (1 << 9) | (1 << 15) | (1 << top)
    parents = [family ^ (1 << s) for s in (6, 9)]
    canonical_parents = [canonical(p, n) for p in parents]
    if (not is_union_closed(family, n)
            or canonical(family, n) != family
            or not all(is_union_closed(p, n) for p in parents)
            or canonical_parents != [(1 << 3) | (1 << 15) | (1 << top)] * 2
            or not all(q < p for p, q in zip(parents, canonical_parents))):
        raise AssertionError("Strong all-minimum-deletions obstruction failed")
    return {
        "n": n, "canonical_child": family,
        "child_sets": sorted({6, 9, 15, top}),
        "minimum_cardinality_members": [6, 9],
        "deletion_parent_bitmasks": parents,
        "canonical_parent_bitmasks": canonical_parents,
    }


def lacks_canonical_min_parent(family, n):
    """Exact finite diagnostic; n<=4 validation, not an all-n count."""
    sets = members(family, n)
    if len(sets) <= 1:
        return False
    min_size = min(s.bit_count() for s in sets)
    removable = [s for s in sets if s.bit_count() == min_size
                 and s != (1 << n) - 1]
    return bool(removable) and all(
        canonical(family ^ (1 << s), n) != family ^ (1 << s)
        for s in removable
    )


def independent_census(n):
    """Independent exhaustive truth table, valid only for n <= 3.

    Enumerates all bitmask families directly, without any augmentation or
    closure-pruning logic. Canonical classes use distinct S_n actions.
    """
    if n not in (1, 2, 3):
        raise ValueError("Independent full Boolean census capped at n=3")
    top = (1 << n) - 1
    unique = set()
    for family in range(1 << (1 << n)):
        if not (family >> top & 1) or not is_union_closed(family, n):
            continue
        unique.add(min(relabel_family(family, action)
                       for action in subset_actions(n)))
    return unique


def verify():
    records = {}
    for n in range(1, 5):
        layers = orbit_layers(n)
        sizes = [len(layer) for layer in layers]
        if sizes != EXPECTED_LEVELS[n]:
            raise AssertionError("Incorrect orbit-level census at n=" + str(n))
        observed = set().union(*layers)
        if len(observed) != sum(sizes):
            raise AssertionError("A family appears at two different sizes")
        if any((not is_canonical(f, n) or not is_union_closed(f, n)
                or not (f & (1 << ((1 << n) - 1))))
               for f in observed):
            raise AssertionError("Generated invalid or noncanonical family")
        # Independent generation logic: old descending-size construction.
        old = set(canonical_representatives(n))
        if observed != old:
            raise AssertionError("Augmentation and descending generator disagree")
        if n <= 3 and observed != independent_census(n):
            raise AssertionError("Augmentation disagrees with raw Boolean truth table")
        record = {"n": n, "per_family_size": sizes, "orbit_count": len(observed)}
        if n >= 3:
            naive = [len(x) for x in orbit_layers(n, naive_parent_test=True)]
            if naive != NAIVE_LEVELS[n]:
                raise AssertionError("Naive parent-test negative-control drift")
            record.update(
                naive_parent_test_level_counts=naive,
                naive_parent_test_orbits=sum(naive),
                explicit_obstruction=obstruction(n),
                canonical_families_without_any_canonical_min_parent=sum(
                    lacks_canonical_min_parent(f, n) for f in observed
                ),
            )
            if n == 4 and record[
                "canonical_families_without_any_canonical_min_parent"
            ] != 5:
                raise AssertionError("Strong-deletion obstruction census drift")
            if n == 4:
                record["stronger_obstruction"] = stronger_obstruction(n)
        records[str(n)] = record
    obstruction(5)  # n>=3 algebraic pattern; one additional finite check.
    stronger_obstruction(5)  # n>=4 stronger pattern.
    return {
        "schema": "svyable.frankl-orbit-augmentation.v1",
        "records": records,
        "interpretation": "Known finite orbit counts; all-n augmentation completeness "
                          "is a written combinatorial argument. Not a Frankl theorem, "
                          "not an audited novelty claim.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="cross-check orbit layers with distinct generators")
    parser.add_argument("--n", type=int, choices=(1, 2, 3, 4),
                        help="show orbit layer counts (n <= 4)")
    args = parser.parse_args(argv)
    try:
        if args.check:
            print(json.dumps(verify(), indent=2, sort_keys=True))
        elif args.n is not None:
            layers = orbit_layers(args.n)
            print(json.dumps({
                "n": args.n, "orbit_count": sum(map(len, layers)),
                "per_family_size": [len(s) for s in layers],
                "scope": "finite known census only",
            }, indent=2))
        else:
            parser.error("Select --check or --n")
    except (ValueError, AssertionError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
