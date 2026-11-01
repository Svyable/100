# M094 — n=29 multiplier-symmetry no-go (bounded negative result)

**2026-11-01 · O-M094-01 · [claim #116](https://github.com/Svyable/100/issues/116)**

This is a necessary-condition obstruction to **two over-restrictive search
strategies**, not nonexistence of Williamson matrices of order 29, Hadamard
matrices of order 116, or the solution of any open Hadamard problem. It is a
direct elementary consequence of the standard Williamson row-sum identity;
**no novelty or independent review is claimed**.

## Exact model and result

Let A, B, C, D be symmetric circulant matrices of order 29 with entries
in {+1,-1} and A²+B²+C²+D²=116 I. Write a, b, c, d for their first rows.
For each row x, let R_x be its sum. Summing the 29 cyclic correlation
equations over all shifts gives the necessary identity

    R_a² + R_b² + R_c² + R_d² = 116.                (1)

The zero shift contributes 4*29=116, and the other shifts contribute zero.
This argument uses integer arithmetic, not floating-point spectral tests.

A common multiplier g means **each of the four rows separately** satisfies
x_i=x_(g*i mod 29) for every i. Symmetric circulants also have x_i=x_(-i).
The multiplicative group F_29^* is cyclic of order 28.

* **g=12 (order 4, containing -1):** the index orbits under multiplication
  by 12 and reversal have sizes 1,4,4,4,4,4,4,4. A row sum is
  e+4(2k-7), e in {±1}, 0<=k<=7. If its square is <=116, its
  absolute value is 3 or 5. Four such squares sum to at most
  4*25=100, contradicting (1).
* **g=7 (order 7; with reversal, order 14):** the index orbits have sizes
  1,14,14. The row sum is e+14u+14v with e,u,v in {±1}. Under
  the same square bound it must be ±1. Four squares then sum to 4,
  contradicting (1).

Every subgroup of F_29^* properly containing {-1,+1} has order 4, 14,
or 28, and therefore contains the subgroup of order 4 or 14. Thus
**no Williamson quadruple at n=29 can have a common multiplier symmetry
strictly stronger than reversal**. This is not a prohibition on using
multiplier *equivalence* to quotient candidates, nor on different multipliers
for different rows. It only excludes the extra *invariance* hypothesis.

## Reproduction and independent-path controls

    python3 scripts/williamson_multiplier.py --check
    python3 scripts/williamson_multiplier.py
    python3 -m unittest discover -s tests -p 'test_williamson_multiplier.py' -v

The executable computes orbits by closure under two index actions and
enumerates their row sums; a separate arithmetic path uses only subgroup
orders and orbit lengths. Tests independently expand all 256 assignments
for g=12 and eight for g=7 into full 29-sign rows, check invariance,
and recount sums. Invalid multipliers and altered orbit data are rejected
or detected. The **reversal-only g=28 control passes** the row-sum screen,
which confirms the screen is not spuriously declaring all n=29 searches
impossible. Passing this necessary condition is *not* a construction.

Negative outcome: the proposed shortcut of forcing a shared nontrivial
multiplier symmetry cannot produce the missing order-116 certificate.
No full 2^14 symmetric-sequence search, 116x116 orthogonality replay,
order-156 or order-172 Goethals–Seidel replay, or independent reviewer
assessment was performed. **O-M094-01 remains open**.

Next falsifier: produce a fully specified n=29 Williamson quadruple without
the extra common multiplier invariance, check all 28 nonzero autocorrelation
shifts by an independent path, and verify the assembled 116x116 matrix by
integer dot products. Alternatively import published Goethals–Seidel base
blocks for 156 or 172 with independent matrix verification. Do not infer
nonexistence from a restricted symmetry search.

## Prior art / provenance

* Williamson, *Hadamard's determinant theorem and the sum of four squares*
  (Duke Math. J. **11**, 1944), DOI:
  https://doi.org/10.1215/S0012-7094-44-01108-7
  — Williamson array and four-square framework.
* Bright, Kotsireas and Ganesh, *Applying Computer Algebra Systems with SAT
  Solvers to the Williamson Conjecture* (2018/2019),
  https://arxiv.org/abs/1804.01172 — modern row-sum Diophantine
  prefilter and exact enumeration context; this work is not their result.
* Baumert, *Hadamard matrices of orders 116 and 232*, Bull. Amer. Math.
  Soc. **72** (1966), p. 237 (cited by
  https://doi.org/10.1016/0012-365X(88)90040-4) — order 116 is
  historically constructed, so this gate is **not** a nonexistence claim.

No change to `data/solved.json`, no novelty promotion, and no claimed
independent mathematical acceptance.
