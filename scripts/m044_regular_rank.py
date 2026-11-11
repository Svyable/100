"""Independent GF(2) left-regular matrix unit test for finite group rings.

No group word problem or infinite/torsion-free group is represented here.
"""
from m044_group_ring_core import cyclic, symmetric_three, multiply, validate


def rank_gf2(columns, dimension):
    """Binary Gaussian elimination on packed columns, without ring multiplication."""
    pivots = {}
    for value in columns:
        if value < 0 or value >= 1 << dimension:
            raise ValueError("column outside vector space")
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def left_regular_columns(a, table):
    """Columns for L_a(x)=ax, assembled directly from Cayley coefficients."""
    n = len(table)
    if a < 0 or a >= 1 << n:
        raise ValueError("element outside group algebra")
    columns = []
    for basis in range(n):
        column = 0
        for i in range(n):
            if (a >> i) & 1:
                column ^= 1 << table[i][basis]
        columns.append(column)
    return columns


def check():
    results = {}
    for name, table in (("C3", cyclic(3)), ("S3", symmetric_three())):
        identity = validate(table)
        n = len(table)
        units = 0
        singular = 0
        for a in range(1 << n):
            full_rank = rank_gf2(left_regular_columns(a, table), n) == n
            inverse_exists = any(
                multiply(a, b, table) == (1 << identity)
                and multiply(b, a, table) == (1 << identity)
                for b in range(1 << n)
            )
            assert full_rank == inverse_exists, (name, a)
            units += full_rank
            singular += not full_rank
        results[name] = (units, singular)
    assert rank_gf2([1, 1, 0], 3) == 1
    assert rank_gf2([1, 2, 4], 3) == 3
    return results


if __name__ == "__main__":
    print(check())
