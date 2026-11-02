# M076 — sharp seven-deletion rigidity around the classical 54-set family

**Claim:** [#206](https://github.com/Svyable/100/issues/206). **Work ID:** `X-M076-F43-SEVEN`. **Scope SHA-256:** `d3ade778162787dd0a8d73f28bb188b4139aefd6afecc22d5ac2a41e9bc62510`. **Date:** November 2, 2026 UTC. **Status:** author-derived, exact restricted theorem **candidate**; two algorithmically different cover enumerators and a separate literal set-intersection replay, **not** independent mathematical review. Historical novelty is unestablished.

## Statement and boundary

Let `F` be the 54-member, four-uniform, three-sunflower-free Abbott–Hanson–Sauer family on `U={0,...,17}`: split `U` into two nine-point components, each into three blocks of three, and in each component take all four-sets consisting of two points from each of two distinct blocks. Let a three-petal sunflower mean **three distinct sets** with identical pairwise intersections, including empty core.

**Seven-deletion rigidity candidate (sharp).** For every ambient ground set `V ⊇ U`, every `D ⊆ F` with `|D| ≤ 7`, and every family `I ⊆ binom(V,4) \ F` of **distinct** new four-sets, if `(F \ D) ∪ I` is sunflower-free, then **`|I| ≤ 2`**. Equality occurs with exactly seven deletions: remove old-set indices `{0,1,2,3,24,25,26}` (in `base_family()`) and insert `{0,1,3,18}` and `{0,1,3,19}`. The resulting 49-member family is literally checked against all `C(49,3)=18,424` triples. A third such completion is a sunflower. Thus the stronger "at most one insertion" bound is **false**.

This strengthens the separate [six-deletion candidate](https://github.com/Svyable/100/pull/204), currently [PR #204](https://github.com/Svyable/100/pull/204), without depending on its code. It rules out a 55-member family obtained by deleting at most seven old sets from **this particular** 54-member family. It does not improve the global bound `54 ≤ f(4,3) ≤ 83`, classify unrelated families, or settle the Erdős–Rado sunflower conjecture. The exact value of `f(4,3)` remains open.

## Exact proof certificate

1. **Orbit completeness, arbitrary outsiders.** The automorphisms of `F` permute points within three-point blocks, permute blocks within components, and exchange the components. Outside points are freely relabelable. A four-set outside `F` is determined up to these actions by its number of outside points `r=0,...,4` and the unordered pair of decreasing three-block occupancy triples. This gives exactly **18** orbit types, with `8,5,3,1,1` types by `r`. The 22-point support `U ∪ {18,19,20,21}` realizes all types; more outside labels do not create another type.
2. **Forbidden-pair graph and matching exclusion.** For candidate `C`, define graph `H_C` on the 54 old sets with edge `ij` iff `F_i,F_j,C` form a sunflower. Any deletion set allowing `C` is a vertex cover of `H_C`. Sixteen orbit representatives have **at least eight disjoint edges** in a deterministic greedy matching; their eight-edge literal certificates forbid any seven-deletion cover. Only two candidate types survive: an **inside** set with block counts `(2,1,1)` in one component, and a **one-outsider** set with old-support counts `(2,1,0)`. Their greedy matchings have respectively six and five edges. The two types comprise exactly **162 inside sets** and **108 outside support triples**; the outside triple may be completed with *any* outside point.
3. **Exhaustive seven-cover enumeration.** For each surviving representative, every seven-cover chooses at least one endpoint of every edge in its disjoint matching. Enumerate all `2^6` or `2^5` endpoint choices and respectively one or two additional old vertices, testing every forbidden edge. The resulting sets contain **1,456 inside-type seven-covers** and **2,306 outside-type seven-covers**, counting patterns relative to the fixed representatives, not distinct globally labeled deletions. A separate recursive edge-branching enumerator with a safe disjoint-matching prune yields **exactly the same sets**, not merely the same counts.
4. **Other simultaneously addable shapes.** For each of the **3,762** covers, check all 270 candidate old-support patterns against their full forbidden-pair graphs. Exactly **one or two** patterns are admissible; no cover admits three. These are the exhaustive distributions, where the tuple of numbers counts surviving old sets containing each admissible outside triple:

   | Admissible patterns | Old supersets per outside triple | Insertion upper bound | Covers |
   |---:|---|---:|---:|
   | 1 | none (inside) | 1 | 1,384 |
   | 1 | (0) | 2 | 48 |
   | 1 | (1) | 1 | 2,238 |
   | 2 | none (both inside) | 2 | 64 |
   | 2 | (1) (inside + outside) | 2 | 20 |
   | 2 | (1,1) (both outside) | 2 | 8 |

   Totals: `1,384+48+2,238+64+20+8=3,762`. If a triple `T` has an old surviving superset, two distinct `T∪{x}` completions plus that old set form a sunflower, so at most one completion is possible. If no old superset survives, three distinct completions form a sunflower with core `T`, so at most two are possible. Summing these per-pattern upper bounds gives **at most two insertions for every seven-cover**. This does not assume that distinct admissible patterns are mutually compatible; ignoring their possible conflicts only weakens the upper bound.
5. **Literal independence and sharpness.** A separate `frozenset` implementation rebuilds the old-old-candidate graphs without bitwise intersections and agrees on all 270 candidates and 18 representatives. An **orbit-key-free direct sweep** of all `C(22,4)-54=7,261` nonmembers, using literal intersections and a greedy eight-matching exclusion, retains exactly **594** labeled candidates (162 inside plus 432 one-outside completions); normalizing outside labels yields exactly the 270 patterns. The sharp 49-set witness is checked by literal all-triples enumeration. For fewer than seven deletions, enlarge `D` to a seven-set: admissibility can only increase, so the same upper bound applies.

The enumeration is small and deterministic, requires no SAT/LP verdict, and is accompanied by mutation/adversarial controls. All complete-checking paths are still authored in the same research effort; their agreement is **not** independent human proof verification.

## Reproduce and falsify

```sh
python3 -m scripts.m076_f43_seven --check --json
python3 -m unittest discover -s tests -p 'test_m076_f43_seven.py' -v
python3 scripts/regen.py --check --fast
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

The `--check` path runs both exact seven-cover enumerators, 3,762 cover-pattern classifications, 270 separate literal forbidden graphs, all 7,261 four-set candidates on 22 points, and the explicit sharp witness. Tests include a forged extra forbidden edge that invalidates a previously valid cover, the two-outsider matching exclusion, a surviving-old-superset negative control, and a third-completion sunflower.

**Failed stronger avenues:** At seven deletions the conjecture "at most one new set" fails already by the explicit two-insertion witness. A single eight-edge matching cannot exclude the inside/outside types (they have only six/five greedy disjoint edges); one must classify their covers. A seven-cover may admit two different inside four-sets or two different outside support triples, so "a unique addable pattern" is also false; the multiplicity/superset argument is essential. No attempt to extrapolate from seven to eight deletions is justified.

**Next falsifiers:** an omitted orbit or a candidate with two or more outsiders surviving the eight-matching test; a seven-cover missing from either enumerator; a cover with three admissible old-support patterns; an outside triple with zero surviving old supersets in a two-pattern cover; a literal 50-member counterexample to the claimed 49-member sharp witness; or an earlier primary source already proving this exact local theorem. Eight-deletion neighborhoods are **unexamined here**. External combinatorics review and a specialist prior-art audit remain required.

## Primary literature and provenance

- Abbott, Hanson and Sauer, *Intersection Theorems for Systems of Sets*, **JCTA 12** (1972), 381–389, [DOI](https://doi.org/10.1016/0097-3165(72)90103-3). Original finite Δ-system context.
- Abbott and Hanson, *On finite Δ-systems*, **Discrete Mathematics 8** (1974), 1–12, [DOI](https://doi.org/10.1016/0012-365X(74)90103-4), and *On finite Δ-systems II* (1977), [DOI](https://doi.org/10.1016/0012-365X(77)90139-X). Historical construction and local-pattern literature requiring deeper priority audit.
- Axante, Budala, Chitic, Dumitru and Nacu, *Sunflower-Free Uniform Families: Recursive Constructions and Explicit Bounds*, [arXiv:2609.06175](https://arxiv.org/abs/2609.06175) (September 5, 2026), reports `54≤f(4,3)≤83`, not this exact seven-deletion statement.
- [Prior five-deletion certificate](M076_F43_STABILITY.md), source-pinned family and original triple checker. The [six-deletion PR](https://github.com/Svyable/100/pull/204) is concurrent, not a dependency.
- An October 2026 [Babanskyy upper-bound-68 claim](https://aixiv.online/abs/2610.01292v1) is unreviewed and does not establish the exact `f(4,3)` value. No novelty or priority conclusion is drawn from a targeted search of the literature as of November 2, 2026.

**Ledger boundary:** one bounded research packet, no added proof obligation, coverage slot, accepted result, or solved-state change. Claim closure and any `merged_pending_review` outcome are conditional on an eventual CI-gated PR merge.
