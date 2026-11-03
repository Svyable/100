#!/usr/bin/env python3
"""M080: the all-ranks one-exceptional-row matching/Latin theorem.

Paper proof: research/M080_ONE_EXCEPTIONAL.md
Lean combinatorial completion: lean/Hundred/OneExceptional.lean

An n x n Rota grid has n-1 IDENTICAL input basis rows B, one arbitrary
exceptional row C (its n labeled occurrences held fixed in column order),
and n transversal bases as columns. Such a grid exists iff the exchange
support graph has a perfect matching; the exact number of grids is the
support permanent times the number of Latin squares with first row fixed.
This is a classical-style restricted theorem, NOT the full Rota conjecture.

Stdlib-only arithmetic uses prime fields GF(p). The mathematical theorem is
stated for arbitrary matroids, with an elementary Hall proof on paper.
"""
import argparse
import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "data/reference/m080_one_exceptional.json"


def prime(p):
    return type(p) is int and p >= 2 and all(p % d for d in range(2, math.isqrt(p) + 1))


def validate(basis, exceptional, p):
    if not prime(p):
        raise ValueError("the modulus must be a prime (a field, not a ring)")
    n = len(basis)
    if not n or len(exceptional) != n:
        raise ValueError("both rows must have the same positive rank")
    for row in list(basis) + list(exceptional):
        if len(row) != n or any(type(x) is not int or x < 0 or x >= p for x in row):
            raise ValueError("vectors must have n canonical field entries")
    if not independent(basis, p):
        raise ValueError("the repeated input row is not a basis")
    return n


def independent(vectors, p):
    """Constructing path: modular Gauss elimination, vectors in rows."""
    n = len(vectors)
    work = [list(row) for row in vectors]
    row = 0
    for col in range(n):
        k = next((k for k in range(row, n) if work[k][col] % p), None)
        if k is None:
            continue
        work[row], work[k] = work[k], work[row]
        inv = pow(work[row][col], -1, p)
        work[row] = [(v * inv) % p for v in work[row]]
        for i in range(row + 1, n):
            coefficient = work[i][col]
            work[i] = [(a - coefficient * b) % p
                       for a, b in zip(work[i], work[row])]
        row += 1
    return row == n


def determinant(vectors, p):
    """Independent checker: alternating Leibniz sum, never Gaussian pivots."""
    n = len(vectors)
    if n > 6:
        raise ValueError("literal determinant checker supports n <= 6")
    total = 0
    for perm in itertools.permutations(range(n)):
        inversions = sum(perm[i] > perm[j] for i in range(n) for j in range(i+1, n))
        term = -1 if inversions % 2 else 1
        for i, j in enumerate(perm):
            term *= vectors[i][j]
        total += term
    return total % p


def coefficients(basis, vector, p):
    """Solve B*x=v, treating basis vectors as columns of B."""
    n = len(basis)
    rows = [[basis[j][i] % p for j in range(n)] + [vector[i] % p]
            for i in range(n)]
    for pivot in range(n):
        k = next((i for i in range(pivot, n) if rows[i][pivot]), None)
        if k is None:
            raise ValueError("singular input basis")
        rows[pivot], rows[k] = rows[k], rows[pivot]
        inv = pow(rows[pivot][pivot], -1, p)
        rows[pivot] = [(x * inv) % p for x in rows[pivot]]
        for i in range(n):
            if i == pivot:
                continue
            mult = rows[i][pivot]
            rows[i] = [(a - mult*b) % p for a, b in zip(rows[i], rows[pivot])]
    return tuple(row[-1] for row in rows)


def exchange_masks(basis, exceptional, p):
    """Left vertices: exceptional occurrences j; right: omitted basis indices i."""
    n = validate(basis, exceptional, p)
    result = tuple(sum(1 << i for i, v in enumerate(coefficients(basis, c, p)) if v)
                   for c in exceptional)
    assert len(result) == n
    return result


def maximum_matching(masks):
    """Augmenting-path algorithm: basis index -> matched exceptional column."""
    n = len(masks)
    right_to_left = [-1] * n

    def augment(j, visited):
        for i in range(n):
            if not (masks[j] >> i & 1) or visited[i]:
                continue
            visited[i] = True
            if right_to_left[i] == -1 or augment(right_to_left[i], visited):
                right_to_left[i] = j
                return True
        return False

    for j in range(n):
        augment(j, [False] * n)
    return tuple(right_to_left)


def find_matching(masks):
    """Full matching column j -> missing basis index i, or None."""
    right_to_left = maximum_matching(masks)
    left_to_right = [-1] * len(masks)
    for i, j in enumerate(right_to_left):
        if j >= 0:
            left_to_right[j] = i
    if any(i < 0 for i in left_to_right):
        return None
    return tuple(left_to_right)


def hall_obstruction(masks):
    """Constructively recover a Hall-deficient S via alternating paths.

    The reached right vertices are exactly N(S); all are matched, but S
    contains an unmatched left vertex, proving |N(S)|<|S|.
    """
    n = len(masks)
    right_to_left = maximum_matching(masks)
    matched_left = set(right_to_left) - {-1}
    queue = [j for j in range(n) if j not in matched_left]
    if not queue:
        raise ValueError("matching exists: no Hall-deficient subset")
    seen_left = set(queue)
    seen_right = set()
    while queue:
        j = queue.pop()
        for i in range(n):
            if not masks[j] >> i & 1 or i in seen_right:
                continue
            seen_right.add(i)
            other = right_to_left[i]
            if other >= 0 and other not in seen_left:
                seen_left.add(other)
                queue.append(other)
    neighbors = {i for j in seen_left for i in range(n) if masks[j] >> i & 1}
    if neighbors != seen_right or len(neighbors) >= len(seen_left):
        raise AssertionError("alternating-path Hall witness failed")
    return {"columns": sorted(seen_left), "neighbor_indices": sorted(seen_right)}


def support_permanent(masks):
    """Exact subset DP, count all exchange-support perfect matchings."""
    n = len(masks)
    dp = [0] * (1 << n)
    dp[0] = 1
    for state in range((1 << n) - 1):
        j = state.bit_count()
        if not dp[state]:
            continue
        for i in range(n):
            if (masks[j] >> i & 1) and not (state >> i & 1):
                dp[state | (1 << i)] += dp[state]
    return dp[-1]


def latin_fixed_first(n):
    """Count Latin completions of one fixed first row; n <= 4 exactly."""
    if not 1 <= n <= 4:
        raise ValueError("exhaustive Latin completion limited to n <= 4")
    rows = tuple(itertools.permutations(range(n)))
    occupied = [1 << j for j in range(n)]

    def visit(k):
        if k == n:
            return 1
        total = 0
        for row in rows:
            if all(not (occupied[j] >> row[j] & 1) for j in range(n)):
                for j in range(n):
                    occupied[j] |= 1 << row[j]
                total += visit(k + 1)
                for j in range(n):
                    occupied[j] ^= 1 << row[j]
        return total

    return visit(1)


def construct(basis, exceptional, p):
    """Exact matching-to-cyclic-Latin construction; no theorem solver calls."""
    n = validate(basis, exceptional, p)
    masks = exchange_masks(basis, exceptional, p)
    matching = find_matching(masks)
    permanent = support_permanent(masks)
    if matching is None:
        if permanent != 0:
            raise AssertionError("permanent disagrees with matching solver")
        return {"status": "hall_obstruction", "support_masks": list(masks),
                "support_permanent": permanent, "hall_obstruction": hall_obstruction(masks)}
    if permanent == 0:
        raise AssertionError("matching found despite zero permanent")
    # For each j the omitted symbol is matching[j]. Every other symbol
    # is used exactly once across repeated rows by a cyclic Latin completion.
    repeated = [tuple(basis[(matching[j] + r) % n] for j in range(n))
                for r in range(1, n)]
    grid = repeated + [tuple(exceptional)]
    verify_grid(basis, exceptional, p, grid)
    return {"status": "grid", "support_masks": list(masks),
            "support_permanent": permanent, "missing_indices": list(matching),
            "rows": [[list(v) for v in row] for row in grid]}


def verify_grid(basis, exceptional, p, grid):
    """Direct column determinant and literal input-row multiset checks."""
    n = validate(basis, exceptional, p)
    if len(grid) != n:
        raise ValueError("a grid needs n rows")
    expected = sorted(map(tuple, basis))
    for r in range(n - 1):
        if sorted(map(tuple, grid[r])) != expected:
            raise ValueError(f"repeated row {r} does not contain B once each")
    if tuple(map(tuple, grid[-1])) != tuple(map(tuple, exceptional)):
        raise ValueError("exceptional row order changed")
    if any(len(row) != n for row in grid):
        raise ValueError("incorrect column count")
    for j in range(n):
        column = [tuple(grid[r][j]) for r in range(n)]
        if n <= 6:
            if determinant(column, p) == 0:
                raise ValueError(f"column {j} fails independent determinant check")
        elif not independent(column, p):
            raise ValueError(f"column {j} fails independent rank check")
    return True


def independent_support_masks(basis, exceptional, p):
    """Independent alternative: n^2 literal replacement determinants."""
    n = validate(basis, exceptional, p)
    if n > 6:
        raise ValueError("literal independent support checker limited to n <= 6")
    return tuple(sum(1 << i for i in range(n)
                     if determinant([basis[k] for k in range(n) if k != i] + [c], p) != 0)
                 for c in exceptional)


def brute_permanent(masks):
    return sum(all(masks[j] >> i & 1 for j, i in enumerate(perm))
               for perm in itertools.permutations(range(len(masks))))


def brute_grid_count(basis, exceptional, p):
    """Independent count from raw row permutations and literal determinants."""
    n = validate(basis, exceptional, p)
    if n > 4:
        raise ValueError("brute grid count limited to n<=4")
    result = 0
    for choices in itertools.product(itertools.permutations(range(n)), repeat=n-1):
        if any(len(set(choice[j] for choice in choices)) != n-1 for j in range(n)):
            continue
        grid = [tuple(basis[i] for i in perm) for perm in choices] + [tuple(exceptional)]
        if all(determinant([grid[r][j] for r in range(n)], p) != 0 for j in range(n)):
            result += 1
    return result


def identity(n):
    return tuple(tuple(int(i == j) for i in range(n)) for j in range(n))


def examples():
    E4 = identity(4)
    dependent = (
        (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1), (1, 1, 1, 1)
    )
    missing = (E4[0], E4[0], E4[0], E4[1])
    # Nonstandard basis B over GF(7). C_j = b_j + 2*b_(j+1) is a basis,
    # since det(I+2*P) = 1 - 2^4 = -15 != 0 modulo 7.
    B7 = tuple(tuple((int(i == j) + int(j == 0 and i == 1)) % 7
                     for i in range(4)) for j in range(4))
    C7 = tuple(tuple((B7[j][i] + 2*B7[(j+1)%4][i]) % 7
                     for i in range(4)) for j in range(4))
    # Dense I+J: determinant 5 modulo 7, all entries nonzero.
    dense7 = tuple(tuple(1 + int(i == j) for i in range(4)) for j in range(4))
    E5 = identity(5)
    C5 = tuple(tuple((E5[j][i] + E5[(j+1)%5][i]) % 3 for i in range(5))
               for j in range(5))
    return (
        ("gf2_rank4_all_equal", 2, E4, E4),
        ("gf2_rank4_dependent_matchable", 2, E4, dependent),
        ("gf2_rank4_hall_failure", 2, E4, missing),
        ("gf7_rank4_two_distinct_bases", 7, B7, C7),
        ("gf7_rank4_all_exchanges", 7, E4, dense7),
        ("gf3_rank5_two_distinct_bases", 3, E5, C5),
    )


def certificate():
    items = []
    for label, p, B, C in examples():
        result = construct(B, C, p)
        masks = exchange_masks(B, C, p)
        if independent_support_masks(B, C, p) != masks:
            raise ValueError("coordinate support differs from literal replacement determinants")
        if support_permanent(masks) != brute_permanent(masks):
            raise ValueError("support permanent differs from permutation enumeration")
        item = {"name": label, "field_prime": p, "rank": len(B),
                "exceptional_is_basis": independent(C, p), **result}
        if len(B) <= 4:
            ways = latin_fixed_first(len(B))
            item["latin_fixed_first_row"] = ways
            item["grid_count_formula"] = ways * result["support_permanent"]
            direct = brute_grid_count(B, C, p)
            if direct != item["grid_count_formula"]:
                raise ValueError("direct grid census contradicts Latin/permanent identity")
            item["grid_count_independent"] = direct
        items.append(item)
    return {
        "schema_version": 1,
        "problem_id": "M080",
        "claim_id": "X-M080-ONE-ROW",
        "scope": "n-1 identical copies of a basis B and one arbitrary labeled row C; all n >= 1",
        "theorem": "transversal basis grid iff exchange-support matching; count = permanent * fixed-first-row Latin completions; for a second basis, sharp bounds Lambda_n <= grids <= n!*Lambda_n",
        "lean_scope": "general n combinatorial cyclic completion from a supplied injective support matching",
        "literature_novelty": "not assessed; matching and Latin-square ingredients are classical",
        "examples": items,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        doc = certificate()
        serialized = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
        if args.check and (not CERT.is_file() or CERT.read_text() != serialized):
            raise ValueError("stored certificate missing/stale: run --write and inspect")
        if args.write:
            CERT.write_text(serialized)
        brief = [{k: ex[k] for k in ("name", "rank", "exceptional_is_basis",
                                     "status", "support_permanent")}
                 for ex in doc["examples"]]
        if args.json:
            print(json.dumps(brief, indent=2))
        else:
            print(f"OK: {len(brief)} exact fixtures, 2 determinant/support routes, "
                  "Latin-square/permanent count verified independently")
    except (ValueError, AssertionError) as exc:
        print(f"M080 failure: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
