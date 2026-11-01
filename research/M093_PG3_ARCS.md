# M093 — exact 4-arcs in PG(3,q), q ≤ 9 (known finite reproduction)

**Date:** 2026-11-01. **Claim:** [#114](https://github.com/Svyable/100/issues/114).
**Work item:** `O-M093-01`, scope digest `e0d611142957b847`.
**Classification:** published/elementary finite mathematics, reproduced by a new
exact implementation. **Not** a new bound, a general MDS proof, an independently
reviewed result, or a Solved-ledger event.

## Primary literature and exact question

A 4-arc in PG(3,q) is a set of distinct projective points represented by
nonzero vectors in GF(q)^4 such that **every four** are linearly independent.
The finite question is the largest number of points in such a set for each
prime power q ≤ 9 (there is no field GF(6)).

- Simeon Ball, [*On sets of vectors of a finite vector space in which every
  subset of basis size is a basis*](https://doi.org/10.4171/JEMS/316),
  J. Eur. Math. Soc. 14 (2012), 733–748. The prime-field MDS theorem is
  background for q=5,7; its stated range must not be applied without checking
  hypotheses to q=2,3 or nonprime fields.
- Gerzson Kéri, [*Types of superregular matrices and the number of n-arcs
  and complete n-arcs in PG(r,q)*](https://doi.org/10.1002/jcd.20091),
  J. Combin. Designs 14 (2006), 363–390. The published computational
  classification covers r=3 for q=5,7,8,9, among other cases.
- Simeon Ball and Michel Lavrauw,
  [*Arcs in finite projective spaces*](https://doi.org/10.4171/EMSS/33),
  EMS Surveys Math. Sci. 6 (2019), 133–172 (published January 2020):
  geometric and MDS context and the scope of prime-field results.

These are known maximum sizes; this is a new *replay* with a simple exhaustive
frame-normalized engine, not a specialist review of the source papers.

## Why the finite search is exhaustive

Any 5-point 4-arc can be taken to the ordered projective frame
`e1,e2,e3,e4,u`, with `u=(1,1,1,1)`, by a projective invertible
coordinate change. Indeed, the first four form a basis and the fifth has
four nonzero basis coordinates; independently rescale those basis vectors
to make the fifth coordinates all one. All 5-frames are therefore equivalent
for existence questions.

For any sixth point x, the four determinants using x and three basis
vectors require all four x coordinates to be nonzero. Normalize x1=1.
The determinants using x, u and any two basis vectors require the four
coordinates of x to be pairwise distinct. Thus **every** possible sixth
point is exactly one of the `(q-2)(q-3)(q-4)` vectors
`(1,a,b,c)`, with a,b,c distinct and drawn from GF(q) minus {0,1}.
For q=2,3,4 there is no sixth point, while the frame itself exists.

For q≥5, the engine enumerates increasing-index subsets of these candidate
points. Every newly formed 4-subset has k=1,2,3 or 4 candidate points and
4-k frame points. The recursive search explicitly checks all such
determinants; its pruning removes only a subset already failing one.
A complete `UNSAT` result for size n+1 excludes every larger arc because
any larger arc would contain an (n+1)-arc. A cutoff is labelled
`UNKNOWN`, never `UNSAT`.

Finite fields are represented exactly by GF(2), GF(3), GF(5), GF(7),
GF(4)=GF(2)[t]/(t²+t+1), GF(8)=GF(2)[t]/(t³+t+1),
GF(9)=GF(3)[t]/(t²+1). Determinants use finite-field elimination.
The separate Leibniz permutation formula checks positive witnesses and
sample determinants without using elimination.

## Reproduced finite maxima

| q | candidate sixth points | 4-arc maximum | first excluded size | DFS nodes for exclusion |
|---:|---:|---:|---:|---:|
| 2 | 0 | 5 | 6 | 0 |
| 3 | 0 | 5 | 6 | 0 |
| 4 | 0 | 5 | 6 | 0 |
| 5 | 6 | 6 | 7 | 21 |
| 7 | 60 | 8 | 9 | 3,122 |
| 8 | 120 | 9 | 10 | 32,565 |
| 9 | 210 | 10 | 11 | 512,655 |

All seven exclusion searches returned `UNSAT` **from complete deterministic
enumeration**, not from a SAT solver or a separately verified proof trace.
Each lower-bound witness was independently checked by the Leibniz
determinant formula; for q≥4 the script also checks the normal rational
curve with q+1 points. The test suite separately brute-forces all 5- and
6-subsets of the 15 projective points of PG(3,2), obtaining 168 five-arcs
and zero six-arcs. These are known finite facts.

## Reproduction, negative controls, and limitations

```sh
python3 scripts/pg3_arcs.py
python3 -m unittest discover -s tests -p 'test_pg3_arcs.py' -v
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

The eight focused tests exercise field distributivity/inverses, non-field
rejection for q=6, candidate counts, independent determinant formulas,
brute-force PG(3,2), all seven maxima, duplicate/coordinate tampering,
and a deliberate q=9 search cutoff returning `UNKNOWN`.

The field arithmetic is shared between the two determinant paths, and the
negative search uses a single implementation of frame normalization.
Therefore these tests **are not independent human mathematical review**,
nor do they prove correctness of an external classification database.
A specialist should check the frame reduction, the small-field tables,
the Kéri baseline and the exact q=8/9 exclusion against an independently
implemented finite-field engine. No proof-obligation discharge is recorded.

**Next falsifier:** independently enumerate frame extensions in GF(8) and
GF(9) using a different field representation and determinant algorithm;
look for a 10-point 4-arc in PG(3,8) or an 11-point 4-arc in PG(3,9),
or any missed 4-subset/candidate under the normalization. A genuine
counterexample would invalidate this replay; absent one, outside scope
review is still required before accepting `O-M093-01`.
