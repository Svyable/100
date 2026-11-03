# M076 — sharp nine-deletion stability of the 54-set sunflower family

**Date:** 2026-11-02 UTC. **Claim:** [#217](https://github.com/Svyable/100/issues/217).
**Work ID:** `X-M076-F43-NINE`. **Scope SHA-256:**
`f11f4860e2b1b166b9a5426d1ffbfcac811bd69b8a7aa48bca7dd1ed83e63ed5`.

**Classification:** author-derived, exact, restricted **theorem candidate**. Two
complete cover enumerators, a separate literal-set orbit-free sweep, and
exhaustive equality-pattern verification of simultaneous insertions agree.
These are same-author checks, **not independent mathematical review**.
Historical novelty is **unestablished**. This does not improve a global
sunflower bound or solve the Erdős–Rado conjecture.

## Exact statement and sharpness

Let `U={0,...,17}` consist of two disjoint nine-point components, each
partitioned into three blocks of size three. Let `F` consist of all
four-sets taking two points from each of two different blocks *in one
component*. Thus `|F|=2×3×3×3=54`. A three-petal sunflower means three
**distinct** sets with all three pairwise intersections equal, including
the empty intersection.

**Nine-deletion theorem candidate.** For every ambient set `V⊇U`,
every `D⊆F` with `|D|≤9`, and every collection of distinct
`I⊆binom(V,4)\\F`, if `(F\\D)∪I` contains no three-sunflower, then

```text
|I| ≤ 4.
```

This is **sharp at nine deletions**: delete the old `base_family()`
indices `{0,1,9,10,11,18,21,25,26}` and insert

```text
{0,1,3,6}, {0,1,3,7}, {0,1,4,8}, {0,1,5,8}.
```

The resulting 49 distinct four-sets pass a literal check of all
`binom(49,3)=18,424` triples. This witness comes from the prior
eight-deletion sharp example with one additional deletion; **sharpness
is inherited**, not a new global lower-bound construction. A local
55-set improvement after nine deletions would require at least **ten**
insertions. The candidate excludes even five.

## Complete finite proof certificate

1. **Automorphisms and ambient reduction.** Permutations inside the
   three-point blocks, permutations of the three blocks of each component,
   exchange of the components, and arbitrary permutations of outside
   labels preserve `F`. A four-set's orbit is determined by its
   number of outside points and the unordered pair of sorted
   block-occupancy triples. The existing orbit classifier gives
   exactly **18** types (8, 5, 3, 1, 1 for 0–4 outsiders). The separate
   orbit-free 22-point `frozenset` sweep checks all
   `binom(22,4)−54=7,261` alternatives, without using an orbit key
   to decide admissibility.

2. **Fifteen orbit exclusions.** For any new candidate `C`, construct
   a graph `H_C` on the 54 old members, joining `i,j` precisely
   when `F_i,F_j,C` form a sunflower. Every deletion set allowing
   `C` must be a vertex cover of `H_C`. In **15 of the 18**
   representative graphs, a deterministic matching contains at least
   **ten pairwise vertex-disjoint edges**, each rechecked by literal
   set intersections. Nine deletions cannot cover ten disjoint edges.
   The three remaining orbit types are

   | Outside points | Component occupancy | Labeled normalized candidates | Matching |
   |---:|---|---:|---:|
   | 0 | (2,1,1) | 162 four-sets | 6 |
   | 1 | (2,1,0) | 108 old triples, each with one outsider | 5 |
   | 0 | (3,1,0) | 36 four-sets | 9 |

   The third orbit first becomes feasible at this deletion threshold:
   exactly **eight** nine-covers permit its representative. Those
   eight are already among the outside-type representative covers.
   The literal 22-point sweep finds exactly **630** labeled candidates
   (162+36 inside and 108×4 outside completions), normalizing to
   precisely the **306** patterns in the table.

3. **All nine-covers, twice.** For the three representative forbidden
   graphs, recursively branch on an uncovered edge, pruning only when
   a disjoint matching exceeds the remaining deletion budget; expand
   every terminal cover to nine vertices. A second enumerator instead
   chooses one endpoint from each edge of a fixed disjoint matching,
   adds all remaining vertices, and tests all edges. The two methods
   agree **as sets**, not merely in cardinality:

   | Orbit | Branch terminals | Nine-covers |
   |---|---:|---:|
   | Inside (2,1,1) | 128 | 470,632 |
   | One-outsider (2,1,0) | 30 | 408,481 |
   | Inside (3,1,0) | 8 | 8 |

   The first two cover sets overlap in **712** patterns; all eight
   third-orbit covers are already in the second. Their union contains
   **878,401 distinct deletion masks relative to the fixed orbit
   representatives**. This is *not* the number of all labeled
   nine-deletion subsets globally. Completeness follows because any
   admissible candidate can be conjugated to one of the three
   representatives; its conjugated deletion set must be in this union.

4. **Potential insertion capacity.** For each of the 878,401 deletion
   masks, test all 306 normalized candidate graphs. An inside
   four-set contributes at most one insertion. A one-outsider support
   triple `T` contributes at most one completion if an old set
   containing `T` survives (that old set and two completions would
   form a sunflower), and at most two otherwise (three completions
   form a sunflower with core `T`). Ignoring cross-candidate
   incompatibilities gives a rigorous **upper bound**, with census:

   | Sum of individual insertion capacities | Covers |
   |---:|---:|
   | 1 | 752,354 |
   | 2 | 115,481 |
   | 3 | 9,104 |
   | 4 | 1,331 |
   | 5 | 80 |
   | 6 | 51 |
   | **Total** | **878,401** |

   Therefore only **131** cover masks could possibly admit five
   insertions; none has capacity above six.

5. **Exhaustive simultaneous-insertion obstruction.** For each of
   those 131 masks, independently reconstruct the surviving old
   sets as literal `frozenset` objects. Independently verify
   old-old-new compatibility for every individually allowed
   candidate. Form the finite list of all available insertion slots
   (one per inside candidate, one or two per outside support triple).
   Enumerate **all 386 five-slot subsets**. For outside slots,
   enumerate **all equality partitions of outsider labels** up to
   renaming (the Bell number for six slots is 203), rejecting duplicate
   labels for two completions of the same triple. Exactly **1,118**
   admissible equality-pattern instances are checked. In each,
   some new-new-old or new-new-new triple is a sunflower. Thus
   **five simultaneous insertions are impossible**. Any hypothetical
   larger insertion set contains a five-subset, so at most four
   are possible. The sharp witness establishes equality. For fewer
   than nine deletions, enlarge `D` to nine old sets; admissibility
   only becomes easier.

No SAT/ILP solver result, randomized search, or global classification
of all 54-member sunflower-free families is assumed.

## Reproduction and adversarial controls

```sh
python3 -m scripts.m076_f43_nine --check --json
python3 -m unittest discover -s tests -p 'test_m076_f43_nine.py' -v
python3 scripts/regen.py --check --fast
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

The complete check uses the two cover enumeration algorithms, all
18 orbit graphs and ten-disjoint-pair obstructions, the orbit-free
literal 22-point sweep, the 878,401-mask capacity census, the 131-mask
simultaneous-insertion falsifier search, and a literal sharpness check.
Adversarial tests include forged covers, invalid five-set augmentation,
partition completeness, and the new third-orbit threshold.

**Failed avenues and corrections:** The natural extension of the
eight-deletion proof that only the (2,1,1) and one-outsider (2,1,0)
orbits matter is **false**: (3,1,0) becomes possible after nine
deletions. The naive individual-capacity bound is **six**, not four,
so it does not prove the theorem; explicit new-new-old and
new-new-new incompatibility checks are essential. No five-set
insertion was found in the complete 131-mask residual search.
The search is exact within its stated exhaustive reduction, not a
heuristic failure to find a witness.

**Next falsifiers:** A ten-edge matching that is not disjoint or is
not genuinely forbidden; a missed orbit; a missing nine-cover in
either enumeration; a capacity-six mask with five compatible new
sets under an untested outsider equality pattern; a sunflower in the
49-set witness; or a historical theorem already implying this
specific local bound. The ten-deletion neighborhood is **not**
classified. A new independent orbit/action checker, formalized
small-cover lemma, and external specialist review of the 1972–2026
finite Δ-system literature are appropriate next steps.

## Primary-source and prior-work boundary

- Erdős–Rado, *Intersection Theorems for Systems of Sets*,
  J. London Math. Soc. **35** (1960), 85–90,
  [DOI](https://doi.org/10.1112/jlms/s1-35.1.85).
- Abbott–Hanson–Sauer, *Intersection Theorems for Systems of Sets*,
  JCTA **12** (1972), 381–389,
  [DOI](https://doi.org/10.1016/0097-3165(72)90103-3).
- Abbott–Hanson, *On finite Δ-systems*, Discrete Mathematics **8**
  (1974), 1–12,
  [DOI](https://doi.org/10.1016/0012-365X(74)90103-4).
  The 54-set lower bound is attributed specifically to
  Abbott–Hanson (1974) in contemporary accounts.
- Abbott–Hanson, *On finite Δ-systems II* (1977),
  [DOI](https://doi.org/10.1016/0012-365X(77)90139-X).
- Axante, Budala, Chitic, Dumitru and Nacu,
  *Sunflower-Free Uniform Families: Recursive Constructions and
  Explicit Bounds*, [arXiv:2609.06175](https://arxiv.org/abs/2609.06175)
  (September 5, 2026): reports `54≤f(4,3)≤83`, not this exact
  nine-deletion neighborhood.
- [Eight-deletion result on main](M076_F43_EIGHT.md);
  [seven-deletion PR #207](https://github.com/Svyable/100/pull/207);
  [six-deletion PR #204](https://github.com/Svyable/100/pull/204).

The targeted literature comparison found no identical nine-deletion
statement. **That is not evidence of historical priority.** The
claim remains an author-derived restricted proof candidate pending
independent mathematical and novelty review. Do not change
`data/solved.json`, registry evidence states, coverage slots,
or independent-acceptance counts. The separate Project 100 PR
Landing workflow and its cadence remain unchanged.
