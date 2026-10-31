"""Exact rational linear programming with checkable duality certificates.

Search side: a dense two-phase simplex over Fractions with Bland's rule
(no cycling, no floating point). Check side never trusts the simplex: it
verifies primal feasibility, dual feasibility and equal objective values,
which by weak duality proves both solutions optimal.

Problem form:  minimise c.x  subject to  A_eq x = b_eq,  A_ge x >= b_ge,  x >= 0.
Dual:          maximise b_eq.y + b_ge.z  subject to  A_eq^T y + A_ge^T z <= c,  z >= 0.
"""
from fractions import Fraction


class Infeasible(Exception):
    pass


class Unbounded(Exception):
    pass


def solve(c, A_eq, b_eq, A_ge, b_ge):
    """Return (value, x, y, z) exactly, all as Fractions."""
    n = len(c)
    rows = [list(map(Fraction, r)) for r in A_eq] + [list(map(Fraction, r)) for r in A_ge]
    rhs = [Fraction(v) for v in b_eq] + [Fraction(v) for v in b_ge]
    m_eq, m = len(A_eq), len(rows)
    n_sur = m - m_eq
    # columns: x (n) | surplus (n_sur) | artificial (m)
    width = n + n_sur + m
    sign = []
    T = []
    for i in range(m):
        row = rows[i] + [Fraction(0)] * (n_sur + m)
        if i >= m_eq:
            row[n + i - m_eq] = Fraction(-1)
        s = -1 if rhs[i] < 0 else 1
        row = [s * v for v in row]
        row[n + n_sur + i] = Fraction(1)
        T.append(row + [s * rhs[i]])
        sign.append(s)
    basis = [n + n_sur + i for i in range(m)]
    art = set(basis)

    def pivot(r, col):
        pv = T[r][col]
        T[r] = [v / pv for v in T[r]]
        for i in range(m):
            if i != r and T[i][col] != 0:
                f = T[i][col]
                Ti, Tr = T[i], T[r]
                T[i] = [a - f * b for a, b in zip(Ti, Tr)]
        basis[r] = col

    def run(cost, allowed):
        while True:
            # reduced costs r_j = c_j - c_B B^-1 A_j, read from the tableau
            cb = [cost[b] for b in basis]
            enter = None
            for j in range(width):
                if j in allowed and j not in basis:
                    rj = cost[j] - sum(cb[i] * T[i][j] for i in range(m))
                    if rj < 0:
                        enter = j  # Bland: smallest index with negative reduced cost
                        break
            if enter is None:
                return
            best, leave = None, None
            for i in range(m):
                if T[i][enter] > 0:
                    ratio = T[i][-1] / T[i][enter]
                    if best is None or ratio < best or (ratio == best and basis[i] < basis[leave]):
                        best, leave = ratio, i
            if leave is None:
                raise Unbounded("objective unbounded below")
            pivot(leave, enter)

    phase1 = [Fraction(0)] * (n + n_sur) + [Fraction(1)] * m
    run(phase1, set(range(width)))
    if sum(T[i][-1] for i in range(m) if basis[i] in art) != 0:
        raise Infeasible("no feasible point")
    for i in range(m):  # drive degenerate artificials out of the basis where possible
        if basis[i] in art:
            for j in range(n + n_sur):
                if T[i][j] != 0 and j not in basis:
                    pivot(i, j)
                    break
    cost = [Fraction(v) for v in c] + [Fraction(0)] * (n_sur + m)
    run(cost, set(range(n + n_sur)))
    x = [Fraction(0)] * width
    for i, b in enumerate(basis):
        x[b] = T[i][-1]
    cb = [cost[b] for b in basis]
    # dual of transformed row i is minus the reduced cost of its artificial column
    duals = []
    for i in range(m):
        j = n + n_sur + i
        rj = cost[j] - sum(cb[k] * T[k][j] for k in range(m))
        duals.append(-rj * sign[i])
    value = sum(Fraction(ci) * xi for ci, xi in zip(c, x[:n]))
    return value, x[:n], duals[:m_eq], duals[m_eq:]


def certify(c, A_eq, b_eq, A_ge, b_ge, x, y, z):
    """Independent optimality check. Returns the optimal value or raises ValueError."""
    F = Fraction
    x, y, z = [F(v) for v in x], [F(v) for v in y], [F(v) for v in z]
    if any(v < 0 for v in x) or any(v < 0 for v in z):
        raise ValueError("sign constraints violated")
    for row, b in zip(A_eq, b_eq):
        if sum(F(a) * v for a, v in zip(row, x)) != b:
            raise ValueError("equality constraint violated")
    for row, b in zip(A_ge, b_ge):
        if sum(F(a) * v for a, v in zip(row, x)) < b:
            raise ValueError("inequality constraint violated")
    for j in range(len(c)):
        lhs = sum(F(A_eq[i][j]) * y[i] for i in range(len(A_eq))) + \
            sum(F(A_ge[i][j]) * z[i] for i in range(len(A_ge)))
        if lhs > c[j]:
            raise ValueError(f"dual constraint {j} violated")
    primal = sum(F(ci) * v for ci, v in zip(c, x))
    dual = sum(F(b) * v for b, v in zip(b_eq, y)) + sum(F(b) * v for b, v in zip(b_ge, z))
    if primal != dual:
        raise ValueError(f"duality gap {primal - dual}")
    return primal
