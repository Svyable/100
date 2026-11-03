# M076 — sharp eight-deletion stability of the classical 54-set family

**Date:** 2026-11-02 UTC. **Claim:** [#212](https://github.com/Svyable/100/issues/212).
**Work ID:** `X-M076-F43-EIGHT`.
**Scope SHA-256:** `b22d7b8a1bc3115b51cc948c3068fca1c255d6622f0edcc05e58eb4077688a9e`.

**Status:** Author-derived exact **restricted theorem candidate**, supported by two
algorithmically distinct exhaustive cover enumerators, a separate literal
set-intersection/cover-existence sweep, and a sharp explicit witness.
**No independent mathematical review or historical priority audit.**
This is not a global bound on the sunflower function or a resolution of the
Erdős–Rado conjecture.

## Statement

Let `F` be the following explicitly defined 54-member family on
`U={0,...,17}`: partition `U` into two nine-point components, each
partitioned into three blocks of size three; in each component take every
four-set with two points from each of two different blocks.
There are `2 × 3 × 3 × 3 = 54` such sets.
A three-sunflower is **three distinct sets with identical pairwise
intersections**, including the empty intersection.

**Eight-deletion theorem candidate (sharp):** For every ambient set
`V ⊇ U`, every `D ⊆ F` with `|D| ≤ 8`, and every collection
`I ⊆ binom(V,4) \\ F` of distinct new sets, if
`(F \\ D) ∪ I` is three-sunflower-free, then **`|I| ≤ 4`**.
The bound is attained with eight deletions:

- Delete the old sets at `base_family()` indices
  `{0,1,10,11,18,21,25,26}`.
- Insert `{0,1,3,6}`, `{0,1,3,7}`, `{0,1,4,8}`, `{0,1,5,8}`.

The resulting 50-set family is checked against **all 19,600 triples**,
with zero sunflowers. The stronger extension of the seven-deletion
`|I|≤2` claim to eight deletions is **false**. The new upper bound
does not yield a 55-set construction: eight deletions would require
**nine** insertions to exceed 54.

## Exact certificate and completeness proof

1. **All ambient universes reduce to 18 candidate orbits.** Permute
   elements within each three-point block, blocks within components,
   the two components, and all outside points. A new four-set is
   characterized by the number of outsiders `r∈{0,...,4}` and the
   unordered pair of sorted block-occupancy triples. All 18 types are
   realized on the 22-point set `U∪{18,19,20,21}` (8, 5, 3, 1, 1
   types for `r=0,1,2,3,4`), comprising 7,261 nonmembers.
   The arbitrary number of outsider *labels* cannot introduce
   a new type; their multiplicity is handled below.

2. **Nine-disjoint-pair obstruction for 16 types.** For a candidate
   `C`, make a graph on the 54 old sets, joining `i,j` when
   `F_i,F_j,C` form a sunflower. Any deletion set allowing `C`
   is a vertex cover of this graph. The source file contains **nine
   vertex-disjoint verified edges** for each of 16 candidate orbit
   representatives, excluding those types under eight deletions.
   The only survivors are the inside type `(0,(2,1,1),(0,0,0))`
   and one-outsider type `(1,(2,1,0),(0,0,0))`. Their candidates
   are exactly **162 inside four-sets** and **108 old-support triples**,
   the latter completed by an arbitrary single outside point.

3. **Every eight-cover, two enumerations.** For the inside and outside
   representatives, greedy disjoint matchings have respectively six
   and five edges. Choosing an endpoint from each matched edge and
   respectively two or three further old vertices, then testing all
   forbidden edges, gives **32,416** and **35,811** eight-covers.
   A different recursion branches on an uncovered forbidden edge,
   prunes by a disjoint-matching lower bound, and expands all
   discovered covers to size eight. It agrees **as a set** on both
   counts. There are **16** covers common to the two representatives,
   hence **68,211 distinct eight-cover patterns** relative to the
   fixed orbit representatives (not a count of globally distinct
   labeled deletion sets).

4. **Simultaneous insertion upper bound.** For each of those 68,211
   covers, test all 270 admissible old-support patterns against their
   full forbidden-pair graphs. Each inside candidate contributes at
   most one new set. For each outside triple `T`, if an old set
   containing `T` survives, at most one `T∪{x}` completion can
   be inserted (two completions plus that old set form a sunflower).
   Otherwise at most two completions can be inserted (three
   completions form a sunflower). Sum these *individual* upper
   bounds, deliberately ignoring any conflicts between distinct
   candidates. The exhaustive distribution is:

   | Admissible patterns | Sum of insertion upper bounds | Covers |
   |---:|---:|---:|
   | 1 | 1 | 62,552 |
   | 1 | 2 | 1,107 |
   | 2 | 2 | 4,372 |
   | 2 | 3 | 40 |
   | 3 | 3 | 120 |
   | 4 | 4 | 20 |
   | **Total** | | **68,211** |

   Every row has upper bound at most four. Combined with the explicit
   50-set sharpness witness, this proves the claimed local optimum
   **conditional on the correctness of the finite certificate**.
   For `|D|<8`, extend `D` to eight old sets: deleting more old
   sets can only relax insertion constraints.

5. **Separate literal adversary.** An orbit-free `frozenset`
   implementation checks each of the **7,261** nonmember four-sets
   on 22 points, rebuilding forbidden pairs from literal
   intersections. A recursive cover-existence test, with an
   independently computed greedy matching lower bound, retains
   exactly **594** labeled candidates (162 inside, 432 outside
   completions). Normalizing outsider labels gives precisely the
   270 patterns above. The sharp witness is also checked by
   independently represented literal sets against all triples.
   These are separate computational paths **by the same author**,
   not independent specialist proof acceptance.

## Reproduction and negative controls

```sh
python3 -m scripts.m076_f43_eight --check --json
python3 -m unittest discover -s tests -p 'test_m076_f43_eight.py' -v
python3 scripts/regen.py --check --fast
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

Ten dedicated tests exercise exact cover agreement, forbidden-pair
witness validity, a forged eight-deletion cover, a malformed repeated
vertex pair, outside orbit exclusion, the independent 22-point sweep,
the sharp four-insertion witness, rejection of a fifth candidate,
and all 19,600 triples of the final 50-set family. No SAT/ILP verdict
is used in the proof certificate; SciPy and NetworkX were used only
for *exploration* of minimum covers/matchings, and their outputs
were reduced to literal verified matching witnesses.

**Exploratory failures:** Extrapolating the seven-deletion
two-insertion upper bound fails: four insertions are possible after
eight deletions. An eight-edge matching is not sufficient to exclude
the `(3,1,0)` inside type; it has a nine-edge witness, which is
essential at this threshold. Counting admissible patterns alone
would overestimate multiplicities of outside completions; the
surviving-old-superset rule is needed. The local eight-deletion
maximum **does not** improve the global lower bound.

**Next falsifiers:** A candidate type missing from the 18 orbits;
an invalid nine-edge witness; an eight-cover omitted by either
enumerator; a cover allowing a fifth unit of insertion capacity;
a new set with two outsiders surviving the literal sweep; a sunflower
in the 50-set sharp witness; or a prior published theorem already
implying the same eight-deletion bound. The nine-deletion
neighborhood and general 55-set search remain untouched.
Independent combinatorics and historical novelty review are
necessary before any acceptance claim.

## Primary sources and historical boundary

- Erdős and Rado, *Intersection Theorems for Systems of Sets*,
  J. London Math. Soc. **35** (1960), 85–90,
  [DOI](https://doi.org/10.1112/jlms/s1-35.1.85).
- Abbott, Hanson and Sauer, *Intersection Theorems for Systems of
  Sets*, JCTA **12** (1972), 381–389,
  [DOI](https://doi.org/10.1016/0097-3165(72)90103-3).
- Abbott and Hanson, *On finite Δ-systems*, Discrete Mathematics
  **8** (1974), 1–12,
  [DOI](https://doi.org/10.1016/0012-365X(74)90103-4);
  *On finite Δ-systems II* (1977),
  [DOI](https://doi.org/10.1016/0012-365X(77)90139-X).
  Contemporary accounts attribute the 54-member lower bound
  specifically to Abbott–Hanson (1974); the repository's broader
  Abbott–Hanson–Sauer label is construction context, not a priority
  finding.
- Axante, Budala, Chitic, Dumitru and Nacu,
  *Sunflower-Free Uniform Families: Recursive Constructions and
  Explicit Bounds*, [arXiv:2609.06175](https://arxiv.org/abs/2609.06175),
  September 5, 2026: reports `54≤f(4,3)≤83`, not the exact local
  eight-deletion statement.
- Rao, *The story of sunflowers*, J. London Math. Soc. **113**
  (2026), [DOI](https://doi.org/10.1112/jlms.70380):
  general survey, not a review of this candidate.
- Previous five-deletion certificate
  [on main](M076_F43_STABILITY.md), and separate unmerged
  [six-deletion PR #204](https://github.com/Svyable/100/pull/204)
  and [seven-deletion PR #207](https://github.com/Svyable/100/pull/207).

A targeted primary-source comparison did not identify this
particular local eight-deletion theorem. **Absence of a search hit
is not proof of historical novelty.** No evidence state, solved
status, coverage allocation or independent-acceptance metric
should change. The Project 100 PR Landing workflow is separate
and unchanged.
