# M080 — an all-ranks one-exceptional-row basis theorem

**Date:** 2026-11-02. **Claim:** [#288](https://github.com/Svyable/100/issues/288).
**Work ID:** X-M080-ONE-ROW. **Claim scope SHA-256:**
4efd6a1a9149782b61da5760c2cb08f86342a0761842ccca4713593132d5d9e3.

**Classification:** An **unconditional, elementary theorem for a restricted
infinite class**, not a proposed proof of Rota's full basis conjecture.
An all-ranks *combinatorial completion* is Lean 4 kernel-checked; the full
matroid matching/Hall argument and exact counting bijection are written
on paper and tested on exact finite instances, **not formalized in Lean**.
No independent mathematical review or historical originality certification.
The bijective basis exchange and Latin-square techniques are classical.

## 1. State the objects, including labeled occurrences

Let M be **any** finite matroid of rank n >= 1 on a ground set E. Let
B=(b_0,...,b_(n-1)) enumerate a basis, and let C=(c_0,...,c_(n-1))
be **any** list of n elements of E (repetitions permitted; it need not
be a basis or even independent). We have n rows: n-1 independently
labeled copies of B and one **exceptional** row C, whose order is
kept fixed across columns. Repeated elements are distinct *occurrences*
but cannot both be present in an independent column.

A **grid** is a permutation of each of the n-1 B rows such that every
column is a basis of M. Rows and columns are individually labeled;
we do **not** quotient by row or column symmetries.

Define the n-by-n 0/1 exchange matrix

\[
A_{ji}=\begin{cases}
1 &\text{if }(B\setminus\{b_i\})\cup\{c_j\}
        \text{ is a basis of }M,\\
0 &\text{otherwise}.
\end{cases}
\]

Here j indexes the exceptional **column** occurrence and i is the
missing element of B. A matching is a bijection
m:{0,...,n-1}->{0,...,n-1} with A_(j,m(j))=1 for each j.

Let \(\Lambda_n\) be the number of Latin squares of order n with one
specified row equal to (0,...,n-1).

## 2. Sharp characterization and exact enumeration theorem

**Theorem (all ranks, arbitrary matroid and arbitrary exceptional row).**
Under the precise hypotheses above:

1. A valid grid exists **iff** A has a perfect matching. Equivalently,
   \(\operatorname{perm}(A)>0\), or, for **every** set S of exceptional
   row positions, \(|N(S)|\ge|S|\) (Hall).
2. The exact number of valid grids is
   \[
   \boxed{\#\operatorname{Grid}(B,C)
      =\operatorname{perm}(A)\,\Lambda_n.}\tag{1}
   \]
3. **Corollary (one exceptional *basis*).** If C is also a basis,
   then \(\operatorname{perm}(A)\ge1\), hence a valid grid exists.
   Quantitatively there are at least \(\Lambda_n\) valid grids,
   and this universal lower bound is **sharp**: take C=B in the
   prescribed order. Its support matrix is a permutation matrix, so
   its permanent is exactly one.
4. **Sharp all-ranks two-sided counting bounds:** If C is a basis, then
   \[
   \boxed{\Lambda_n\ \le\ \#\operatorname{Grid}(B,C)\ \le\ n!\,\Lambda_n.}	ag{2}
   \]
   Both extremes occur for vector spaces, in *every* rank. The lower
   endpoint is C=B. For the upper endpoint, take B to be the standard
   basis and C the columns of the matrix I+J over a prime field GF(p)
   with p>n+1. Every entry is 1 or 2, hence nonzero; moreover
   \(\det(I+J)=n+1\ne0\) in GF(p), so C is a basis. Every exchange
   edge exists and \(\operatorname{perm}(A)=n!\). The bound is sharp
   without a limiting argument, finite search, or conditional field
   conjecture. This is a direct consequence of (1), not a full RBC
   theorem.

These statements apply to **every rank**, not just dimensions checked
by the finite GF(2)^4 orbit census.

### Step 1 — necessity, including the missing-symbol permutation

Consider any valid grid. Every column contains n-1 copies of distinct
elements from B, because a column with a duplicated element would
not be a basis. Thus column j omits **exactly one** b_(m(j)).

Each b_i occurs in precisely n-1 cells among the repeated rows,
because each repeated row is a permutation of B. No column can
contain b_i twice, and there are n columns, so precisely **one**
column omits b_i. Therefore m is a bijection.

The j-th column contains precisely
(B minus {b_(m(j))}) plus c_j; it is a basis, so A_(j,m(j))=1.
Every valid grid therefore induces a perfect matching of A.

### Step 2 — explicit sufficiency, no induction or search required

Given a perfect matching m, place in repeated row r=1,...,n-1
and column j the basis element

\[
b_{(m(j)+r)\bmod n}.
\]

For each fixed r, modular addition by r permutes the symbols;
since m is already a permutation, every repeated row contains
each element of B exactly once. For each fixed column j, the shifts
1,...,n-1 give **all** basis indices except m(j), with no repetitions.
The j-th column is therefore exactly
(B minus {b_(m(j))}) union {c_j}, a basis by the matching edge.
This constructs the promised grid for arbitrary n.

**Lamport-style invariant:** After putting down the first r repeated
rows, every column has exactly r distinct B-symbols, none equal to its
designated omission. The cyclic recipe maintains this for r+1; its
row-permutation property is independent of prior columns.

### Step 3 — exact count by a reversible bijection

Given any grid, Step 1 recovers a unique matching m. Insert
the row (m(0),...,m(n-1)) above the n-1 B-symbol rows, forgetting
the exceptional vector entries. Each row is a permutation and
each column contains every B-symbol exactly once: this is a
Latin square with **first row prescribed to m**.

Conversely, any matching m and any Latin square with first row m
recover a unique valid grid by deleting the first row and replacing
its symbols with the exceptional vector occurrences in their
original order. These mappings are exact inverses; no quotient,
symmetry assumption, uniform distribution, or unverified numeric
count is involved.

There are exactly \(\Lambda_n\) Latin squares with a given first row m,
independent of m (relabel the symbols). The number of admissible m
is the permanent \(\operatorname{perm}(A)\). Multiplication proves (1).

**If the exceptional row is not fixed in order**, the numerical
counting convention changes; equation (1) intentionally fixes it.

### Step 4 — Hall's condition when C is itself a basis

This is the *only* place the hypothesis "C is a basis" is needed.

Fix any S of its positions and let N(S) be the union of exchangeable
basis indices. For c_j already in B, its only exchangeable index
is the index of the same b_i, so c_j belongs to the closure of B_N(S).
For c_j not in B, the **fundamental circuit** of c_j with respect
to B consists of c_j together with its exchangeable indices.
Thus c_j belongs to the closure of the subset of B indexed by N(S).

Therefore the independent set {c_j : j in S}, of size |S|,
lies in the closure of B_N(S), whose rank is exactly |N(S)|:
\[
|S|=\operatorname{rank}(C_S)
   \le \operatorname{rank}(\operatorname{cl}(B_{N(S)}))
   =|N(S)|.
\]
Hall's marriage theorem supplies a perfect matching. This is a
standard matroid basis-exchange argument (Brualdi's bijective
basis-exchange property), not an invented general RBC proof.

**Vector-space alternative:** Express the second basis C in B
coordinates. Its change-of-basis determinant is nonzero. In the
Leibniz expansion, at least one permutation term is nonzero;
its coordinates give the matching m immediately. This
argument works over **any field**, including small characteristic.

## 3. Boundary examples that prevent a false theorem

The exceptional row need **not** be a basis. Over GF(2), with
B=(e0,e1,e2,e3), take

\[
C=(e_0+e_3,\ e_1+e_3,\ e_2+e_3,\
   e_0+e_1+e_2+e_3).
\]

The four vectors are **dependent**: the last is the sum of the
first three. Their exchange support still has **four**
perfect matchings, so the number of valid grids is
4 times \(\Lambda_4=24\), or exactly **96**.
A separate raw row-permutation/determinant enumeration returns 96.

The tempting statement "any exceptional row of nonzero vectors works"
is **false**. For C=(e0,e0,e0,e1) over GF(2)^4, the first three
positions only exchange with b0: S={0,1,2} has |N(S)|=1<3.
No valid grid can exist. A constructive alternating-path algorithm
returns an explicit Hall-deficient subset. This failure is
not a counterexample to Rota: C is not a basis.

Other exact controls with the exceptional row fixed:

| Rank and field | Input | Exchange permanent | Grid count |
| --- | --- | ---: | ---: |
| 4, GF(2) | C=B | 1 | 24, independently enumerated |
| 4, GF(2) | dependent C above | 4 | 96, independently enumerated |
| 4, GF(2) | Hall-deficient C | 0 | 0, independently enumerated |
| 4, GF(7) | two distinct bases, B not standard | 2 | 48, independently enumerated |
| 4, GF(7) | C=I+J, all exchanges possible | 24 | 576, independently enumerated |
| 5, GF(3) | two distinct bases | 2 | 2688 from (1) and published \(\Lambda_5=1344\); grid itself checked exactly, but **2688 is not exhaustively enumerated here** |

The independently established Latin values \(\Lambda_1,\dots,\Lambda_4
=(1,1,2,24)\) are reproduced by direct recursion and agree with
[OEIS A000479](https://oeis.org/A000479) and
[MathWorld: Latin Square](https://mathworld.wolfram.com/LatinSquare.html).
All finite matrix checks use **prime fields only**: modular arithmetic
modulo four is not silently treated as GF(4).

## 4. Proof-carrying artifacts and exact fidelity

Reproduce from the repository root:

~~~sh
python3 scripts/m080_one_exceptional.py --check --json
python3 -m unittest tests/test_m080_one_exceptional.py -v
python3 scripts/formal.py --check
python3 scripts/lean_verify.py
python3 scripts/regen.py --check --fast
~~~

The static certificate
[data/reference/m080_one_exceptional.json](../data/reference/m080_one_exceptional.json)
contains the six literal input instances, support masks, actual
cyclic grids, matchings or explicit Hall-deficient sets, and exact
finite permanent and grid counts. The producing script uses modular
Gaussian elimination and bipartite augmenting paths. An **independent
arithmetical path** computes every support entry by a literal
Leibniz determinant of a replacement basis, counts the permanent
by permutations rather than subset DP, and independently counts
complete grids by row permutations (n<=4). Twelve adversarial tests
include dependent-but-matchable and Hall-deficient rows, nonstandard
bases, multiple characteristics, randomly generated bases, tampered
column certificates, invalid dimensions and composite moduli. A
complete GF(2)^3 sweep challenges all 512 exceptional rows against
a raw row-permutation census. An all-rank sharpness family is sampled
at every rank 1..6 over GF(11), including the exact n! support
permanent and independent replacement determinants.

**What Lean checks:** The dependency-free Lean module
[lean/Hundred/OneExceptional.lean](../lean/Hundred/OneExceptional.lean)
proves, for **arbitrary positive n**, that an injective omitted-symbol
matching can be completed by cyclic Latin rows. Each repeated row is
injective, each column's basis symbols are pairwise distinct, the
omission is absent, and the supplied exchange predicate is preserved.
The Lean proof uses no sorry/admit/unsafe shortcut and is registered
for the kernel axiom audit as L010.

**What Lean does NOT check:** The matroid rank and closure axioms,
fundamental circuits, Hall's theorem, determinant nonzero-term
existence, or the bijective counting identity (1). Those are complete
**paper arguments**, but calling the entire matroid theorem
kernel-verified would be false. Finite tests exercise the model, not
all infinite matroids.

## 5. Literature and the actual open remainder

- [Oxley, Matroid Theory](https://www.math.ens.psl.eu/~benoist/refs/Oxley.pdf), Chapter 11 exercise citing Brualdi (1969):
  bijective basis exchange via Hall's theorem; this is clearly
  *known* mathematics on which our corollary rests.
- [Rota's basis conjecture, Polymath background](https://polymathprojects.org/2017/03/06/rotas-basis-conjecture-polymath-12-2/):
  the full problem is not the n-1-identical-row case.
- [Montgomery–Sauermann, Asymptotically-tight packing and covering
  with transversal bases](https://arxiv.org/abs/2508.05601) (2025):
  contemporary status; almost all required transversal bases in
  the general setting, not all n for arbitrary n bases.
- [MathWorld Latin squares](https://mathworld.wolfram.com/LatinSquare.html):
  values and normalization of \(\Lambda_n\).
- [Project 100's earlier GF(2)^4 repeated-basis certificate](M080_REPEATED_ORBIT_GATE.md):
  covers four-row input with **at least two equal bases** by
  finite enumeration, a different and broader rank-four class.

**Priority:** The proof combines classical basis exchange, Hall's
theorem and Latin squares. A targeted literature audit found the
ingredients already published and did not establish whether equation
(1) appears elsewhere. This manuscript **does not claim**
historical novelty, new global RBC progress, or independent
mathematical acceptance. It is a useful sharp general theorem and
a reusable, auditable proof mechanism for the research program.

**Next attack (actually outside this theorem):** Retain n-2 copies of
B and allow **two arbitrary** exceptional bases. Each column now
needs *two* omitted B-symbols, and the incidence/Latin structure is
no longer a single perfect matching. A naive application of (1)
does not establish the two-exceptional-row case, even over GF(2).
Seek either a new matching-plus-2-factor argument or a formal
counterexample to a proposed restricted sufficient condition;
do not extrapolate this theorem into full RBC.

**Ledger integrity:** O-M080-01 (the 4,111,138 unchecked all-distinct
GF(2)^4 rooted orbits) remains open. No solved status, independent
review, historical novelty certification or portfolio evidence state
has been changed by this manuscript.
