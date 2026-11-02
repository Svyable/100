# M076 — seven insertions after eleven deletions, and an exact one-step neighborhood

**Date:** 2026-11-02 UTC. **Claim:** [#225](https://github.com/Svyable/100/issues/225).
**Work ID:** `X-M076-F43-ELEVEN-WITNESS`.
**Scope SHA-256:** `e8fe0b925f5dc99324f41ae75572ad91d2d5557355adf54763d6cbac6b910f1a`.

**Status:** author-derived restricted computational theorem **candidate** and
explicit finite witness, with two differently structured exhaustive checkers.
Neither checker is an independent mathematical reviewer. Historical priority
has not been established. No improvement to the global four-uniform sunflower
bound is claimed.

## Construction and exact statement

Let `F=(F_0,...,F_53)` be the ordered 54-set family returned by
`scripts.m076_f43_stability.base_family()`. On each of two disjoint
nine-point components, partition into three blocks of size three and take all
four-sets with two points from each of two different blocks. A sunflower
is a triple of **distinct** sets with all three pairwise intersections equal,
including the empty intersection.

Start with the ten-deletion/five-insertion configuration described in
[PR #221](https://github.com/Svyable/100/pull/221):

```text
D0 = {0,2,3,5,6,8,18,24,25,26}        # old-set indices
I0 = {{0,1,3,18}, {0,2,3,18}, {1,2,3,18},
      {3,6,7,18}, {5,6,7,18}}          # new four-sets
```

**Exact one-step classification (candidate).** Let `V` be any ambient set
containing `{0,...,18}`. For `j∉D0` and any four-set
`C⊆V` not in `F∪I0`, the family
`(F \ {F_i : i∈D0∪{j}}) ∪ I0 ∪ {C}` is sunflower-free **if and only if**
one of the following holds, where `x` is *any* point of `V\{0,...,17}`:

| Extra deleted old index | Added four-set |
|---|---|
| 19 or 22 | `{3,6,8,x}` |
| 20 or 23 | `{3,7,8,x}` |
| 19 | `{5,6,8,18}` |
| 20 | `{5,7,8,18}` |

The four potentially deleted old sets are respectively
`F19={3,4,6,8}`, `F20={3,4,7,8}`,
`F22={3,5,6,8}`, and `F23={3,5,7,8}`.
This table gives exactly **22 labeled (extra deletion, insertion) pairs**
on the representative universe `{0,...,22}`, and a complete symbolic
description on *arbitrary* ambient universes.

**Stronger sharp fixed-deletion result (candidate).** For the *particular*
eleven-deletion set
`D11=D0∪{19}={0,2,3,5,6,8,18,19,24,25,26}`, the maximum number of
simultaneously insertable new four-sets over **any** ambient universe is
exactly **seven**. A sharp witness uses
`I7=I0∪{{3,6,8,18},{5,6,8,18}}`. The resulting family contains
`54−11+7=50` distinct four-sets on 19 points, and passes a literal
check of all `binom(50,3)=19,600` triples. Thus even a six-insertion
upper bound does **not** persist at eleven deletions. This result fixes
`D11` and does **not** bound all eleven-deletion neighborhoods.

## Proof of the bounded classification

1. **One-deletion edge lemma.** Fix the 49-member sunflower-free family
   `G=(F\{F_i:i∈D0})∪I0`. For a new four-set `C`, define `E_C` to contain
   every pair `{A,B}⊆G` for which `A,B,C` form a sunflower. Then
   `(G\{F_j})∪{C}` is sunflower-free exactly when **every** pair in
   `E_C` contains `F_j`. This follows because all new sunflowers
   must contain `C`; the old family `G` is already sunflower-free.
   The requirement that `j` index an *old retained* set is essential.

2. **Finite ambient reduction.** The five existing inserted sets use only
   one outsider, point 18. Any candidate `C` has at most four outsider
   points, so every candidate on any `V` is equivalent, under a
   permutation fixing `0,...,18`, to one supported in `{0,...,22}`.
   This equivalence preserves `F`, `I0`, and the sunflower predicate.
   Conversely, a representative solution with one fresh outsider
   relabels to any such point of `V`.

3. **Complete edge-intersection enumeration.** There are
   `binom(23,4)=8,855` four-sets on the representative universe.
   Exclude the 54 members of `F` and five of `I0`, leaving **8,796**
   candidates. For each, construct all `binom(49,2)=1,176` pair
   intersections of `G` and intersect the allowed old-deletion
   endpoints of every forbidden pair. The resulting 22 pairs are
   precisely the table above. The procedure evaluates
   `44×8,796=387,024` potential old-deletion/new-insertion pairs,
   without an orbit assumption or randomized pruning.

4. **Separate direct enumeration.** A standalone C++17 program rebuilds
   `F` from the block definition, checks that the 49-member baseline
   is sunflower-free, loops over all 44 retained old deletion indices
   and all 8,796 candidate four-sets, and tests the new set directly
   against every pair of the resulting 48-member family. It independently
   returns exactly the same 22 pairs. A third, `frozenset`-based Python
   representation replays all 18,424 triples for each one-step witness
   and tests adversarial negative modifications.

5. **Fixed-`D11` seven-insertion upper bound.** A second direct C++ sweep
   and a separately written Python forbidden-pair scan independently
   classify the new sets compatible with the 43 retained old sets
   `F\{F_j:j∈D11}`. On the 23-point representative universe, there
   are **36** individually admissible candidates: the single inside set
   `{0,1,2,3}` and the seven old-support triples
   `{0,1,3}`, `{0,2,3}`, `{1,2,3}`, `{3,6,7}`,
   `{3,6,8}`, `{5,6,7}`, `{5,6,8}`, each completed
   by any of five outsider labels 18–22. By the same ambient reduction,
   this list is exhaustive for *each individual* new set over arbitrary
   universes. Each of the seven triples is contained in a surviving
   old set (respectively indices **1, 4, 7, 21, 22, 21, 22**).
   Therefore two distinct completions of the *same* triple with
   different outsiders would form a sunflower with that surviving old
   set. At most **one** new set per triple can be selected. The inside
   set conflicts with five of the seven triples (the first three and
   the last two), because it and a completion of those triples form
   a sunflower with a retained old set. Hence any simultaneous
   insertion family has at most seven members if it excludes the inside
   set, and at most `1+2=3` if it includes it. The seven-insertion
   witness `I7` meets this upper bound. Independent integer-mask and frozenset
   all-triples verifiers check all **19,600** triples of its 50 sets.

Thus the finite classifications, elementary retained-superset argument,
and outsider-relabeling reduction establish the *fixed-`D11`* sharp
bound and one-step classification as exact restricted candidates.
They do not classify other eleven-deletion neighborhoods of `F`.

## Reproduction, failures, and next falsifiers

```sh
python3 -m scripts.m076_f43_eleven --check --json
python3 -m unittest discover -s tests -p 'test_m076_f43_eleven.py' -v
python3 scripts/regen.py --check --fast
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

The C++17 checker is `scripts/m076_f43_eleven_direct.cpp`, compiled with
`CXX` or `c++`. The independent-style Python edge checker and literal
replay are `scripts/m076_f43_eleven.py`. All 22 one-step positives are
checked, as are the 36 fixed-deletion individually admissible candidates;
negative controls reject a wrong deleted index, a repeated point, a
previously inserted set, and a proposed fresh-outsider completion not in
the table. No random seed is used.

**Failed stronger claims and corrected lead:** The ten-deletion cap of
five insertions does not persist after eleven deletions. Initially the
first extra set `{3,6,8,18}` suggested six insertions; an adversarial
sweep found `{5,6,8,18}` also compatible with the same deletion set,
so the **six-insertion cap is false even for this fixed `D11`**.
A tempting extra deletion at index 21 combined with `{3,6,8,18}` is
invalid. The 22 extensions exhaust *only* the one-old-deletion/one-new-set
extensions of this particular pinned ten-deletion configuration. The
sharp seven bound applies to the fixed `D11` only; it does not assert
a bound for *all* eleven-deletion configurations. No 55-member family
follows. To exceed the classical 54-set lower bound after eleven
deletions would require **twelve** insertions.

**Literature comparison and limits:** Abbott–Hanson–Sauer,
*Intersection Theorems for Systems of Sets*, JCTA 12 (1972), 381–389,
[DOI](https://doi.org/10.1016/0097-3165(72)90103-3);
Abbott–Hanson, *On finite Δ-systems*, Discrete Mathematics 8 (1974), 1–12,
[DOI](https://doi.org/10.1016/0012-365X(74)90103-4);
Axante et al., *Sunflower-Free Uniform Families: Recursive Constructions
and Explicit Bounds*, [arXiv:2609.06175](https://arxiv.org/abs/2609.06175),
posted 2026-09-05, reports `54≤f(4,3)≤83`. The older papers establish
construction/bound context; the 2026 paper studies global extremal bounds,
not this pinned one-step deletion classification. A targeted search found
no matching local statement, but absence from a search is **not** proof
of novelty. Both algorithmic paths were written by the same author and
are not independent mathematical acceptance.

**Next falsifiers:** Independently reimplement the 23-point direct
enumeration without sharing code; have a specialist check the old-index
convention and all-ambient reduction; search all eleven-deletion
neighborhoods for **eight** simultaneous insertions, rather than
extrapolating from this fixed eleven-deletion seed. No solved status,
independently accepted outcome, coverage slot, or benchmark result changes.
