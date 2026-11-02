# M076 — bipartite conflict graphs and the exact one-insertion deletion spectrum

**Date:** 2026-11-02 UTC. **Claim:** [#223](https://github.com/Svyable/100/issues/223). **Work ID:** `X-M076-F43-ORBIT-THRESHOLDS`. **Scope SHA-256:** `09dc1a6fcd21524f108dcd72ad20e7582ce3f3c25a3847fef201fc469e4d59e9`.

**Classification:** author-derived, restricted structural theorem and exact finite certificate **candidate**. The analytic bipartiteness argument is separate from the numerical orbit census. An independently represented bitmask sweep and an optional independent integer-programming calculation agree, but **neither is external specialist review**. Historical novelty is unestablished. This does not improve `f(4,3)`, resolve the Erdős–Rado conjecture, or establish a simultaneous-insertion bound after eleven deletions.

## Exact statement

Let `U={0,...,17}` be partitioned into two nine-point components, each further partitioned into three blocks of size three. Let `F` contain, within **each** component, every four-set formed by selecting two points from each of two different blocks. There are `2 * 3 * 3 * 3 = 54` distinct members, and `F` has no three-petal sunflower, including one with empty core.

For an arbitrary ambient set `V` containing `U` and an arbitrary subset `C` of `V`, define the **sunflower-conflict graph** `H_C` on the 54 members of `F`: distinct `A,B` are adjacent precisely when `A∩B=A∩C=B∩C`.

**Structural lemma (all subsets `C`, not just four-sets).** Every `H_C` is bipartite.

**Exact single-insertion theorem candidate.** If `C` is a four-set not already in `F`, the least number `d(C)` of old members that must be deleted before inserting `C` without creating a three-petal sunflower equals both the minimum vertex-cover number and maximum matching number of `H_C`:
\[
d(C)=\tau(H_C)=\nu(H_C).
\]
It depends only on the number of points of `C` outside `U` and the unordered pair of sorted three-block occupancy vectors in the two components. The following table gives **all 18 possibilities**, even if `V` is arbitrarily large. The `|orbit|` column counts labelled candidates on the test universe `{0,...,21}` (four outside labels); it is not a count for an arbitrary ambient universe.

| Outside | Block occupancy vectors | Representative `C` | `|orbit|` | `|E(H_C)|` | `d(C)` |
|---:|---|---|---:|---:|---:|
| 0 | (1,1,0) / (1,1,0) | 0,3,9,12 | 729 | 77 | 19 |
| 0 | (1,1,1) / (1,0,0) | 0,3,6,9 | 486 | 75 | 21 |
| 0 | (2,0,0) / (1,1,0) | 0,1,9,12 | 486 | 86 | 16 |
| 0 | (2,0,0) / (2,0,0) | 0,1,9,10 | 81 | 99 | 15 |
| 0 | (2,1,0) / (1,0,0) | 0,1,3,9 | 972 | 67 | **11** |
| 0 | (2,1,1) / (0,0,0) | 0,1,3,6 | 162 | 32 | **6** |
| 0 | (3,0,0) / (1,0,0) | 0,1,2,9 | 54 | 180 | 24 |
| 0 | (3,1,0) / (0,0,0) | 0,1,2,3 | 36 | 93 | **9** |
| 1 | (1,1,0) / (1,0,0) | 0,3,9,18 | 1944 | 137 | 19 |
| 1 | (1,1,1) / (0,0,0) | 0,3,6,18 | 216 | 93 | 15 |
| 1 | (2,0,0) / (1,0,0) | 0,1,9,18 | 648 | 162 | 18 |
| 1 | (2,1,0) / (0,0,0) | 0,1,3,18 | 432 | 85 | **5** |
| 1 | (3,0,0) / (0,0,0) | 0,1,2,18 | 24 | 270 | 18 |
| 2 | (1,0,0) / (1,0,0) | 0,9,18,19 | 486 | 261 | 27 |
| 2 | (1,1,0) / (0,0,0) | 0,3,18,19 | 324 | 203 | 13 |
| 2 | (2,0,0) / (0,0,0) | 0,1,18,19 | 108 | 252 | **12** |
| 3 | (1,0,0) / (0,0,0) | 0,18,19,20 | 72 | 423 | 21 |
| 4 | (0,0,0) / (0,0,0) | 18,19,20,21 | 1 | 729 | 27 |

**Eleven-deletion transition.** At most ten deletions permit a new set from only three orbit types, with thresholds 5, 6 and 9. At eleven, exactly one additional type first appears: the inside-support pattern `(2,1,0)/(1,0,0)`, spanning both nine-point components. For example, inserting `C={0,1,3,9}` is possible after deleting the eleven old-set indices `{0,2,24,25,26,27,28,29,30,31,32}` in the deterministic order of `base_family()`. The resulting 44-set family passes literal old-old-new intersection tests; the graph contains an explicit eleven-edge matching, so ten deletions never suffice. This says **nothing** about how many different new sets can be inserted together after eleven deletions.

## Structural proof: why every conflict graph is bipartite

Fix `C`, of any cardinality, and partition the old sets by their **trace** `T=A∩C`. Every edge of `H_C` joins old sets of the **same** trace `T`, and their intersection must equal `T`. Hence `H_C` is a disjoint union of trace-induced graphs.

1. **Empty trace.** Two old sets within one nine-point component always intersect: their occupied block pairs share a block, and two two-subsets of a three-point block intersect. Thus an empty-trace edge can only join the two different components. This graph is bipartite (in fact complete bipartite between the trace-empty old sets in the two components).
2. **Singleton trace.** Both old sets must occupy the block containing the singleton. If they occupied the same second block, their intersection would contain at least two points, contradicting intersection exactly `T`. Color by which of the two *other* blocks is occupied. Every edge changes color.
3. **Two-point trace in one block.** Both old sets occupy that block. They cannot have the same second occupied block, because then they would intersect in at least one additional point there. Again color by the other occupied block.
4. **Two-point trace in two blocks.** Both old sets occupy precisely those two blocks. In either block, a two-subset containing the specified trace point has exactly two choices. To intersect *only* in the trace, the old sets must choose different second points in **both** blocks. Color by the second point chosen in one fixed block; every edge changes color.
5. **Three-point trace.** At most two old sets contain a given triple: a triple can extend to a member of `F` only with block occupancy `(2,1,0)`, and then there are only two choices for the fourth point. Hence this trace graph has at most two vertices. **Four-point trace** has at most one vertex, because the old members are distinct four-sets.

Every trace graph is bipartite, so their disjoint union is bipartite. The argument uses the exact 2-of-3 block structure; it is **not** a theorem for arbitrary sunflower-free families.

For a new four-set `C`, a triple sunflower in `(F\D)∪{C}` either lies entirely in `F\D` (impossible by construction) or contains `C` and two surviving old sets. The latter exists exactly when an edge of `H_C` survives. Therefore admissible deletion sets are exactly vertex covers. Bipartiteness and the classical König matching-cover theorem imply `d(C)=\nu(H_C)`.

## Hand calculation of the first eleven-deletion orbit

The new cross-component representative at deletion radius eleven is
\(C=\{0,1,3,9\}\). The conflict edges split into trace components,
and the **nontrivial** ones have the following exact graph structures:

| Common trace \(T=A\cap C\) | Conflict graph | Maximum matching |
|---|---|---:|
| Empty | \(K_{3,15}\) | 3 |
| \(\{9\}\) | Two disjoint copies of \(K_{3,3}\) | 6 |
| \(\{0,1\}\) | \(K_{1,3}\) | 1 |
| \(\{0,1,3\}\) | \(K_2\) | 1 |

All other trace classes are edgeless. These counts follow directly
from choosing two points in each of two three-point blocks: the empty
trace has three first-component and fifteen second-component old
members; the trace \(\{9\}\) splits by the two possible pairs
containing point 9, with three opposite choices on either side;
\(\{0,1\}\) has one eligible second-block choice versus three
third-block choices; and \(\{0,1,3\}\) has two eligible completions.
Therefore the exact deletion threshold is
\[
d(\{0,1,3,9\})=3+6+1+1=11.
\]
This is a hand-checkable lower bound by disjoint matchings and an
attained upper bound by taking a minimum vertex cover in each of
these four complete bipartite pieces. It does not require trusting
the 7,261-candidate census or an integer-programming solver.

## Finite numerical certificate and completeness

The automorphisms permuting points inside each three-block, the three blocks in each component, the two components, and outside labels preserve `F`. A four-set uses at most four outside labels; consequently every orbit has a representative on 22 points. The invariant (outside count, unordered sorted component occupancy vectors) is complete under this action. Enumerating all `C(22,4)-54=7,261` nonmembers yields exactly 18 orbits, with distribution `8+5+3+1+1` by outsider count.

For each representative, `scripts/m076_f43_orbit_thresholds.py` builds `H_C` from literal `frozenset` intersections, constructs the explicit trace coloring, obtains a maximum matching by augmenting paths, and constructs a same-cardinality vertex cover by alternating reachability. It checks disjoint matching edges, that the cover meets **every** conflict edge, and that the resulting deleted-and-inserted family has no old-old-new sunflower. The matching is a lower-bound certificate, the cover is an upper-bound certificate; equality is exact, not an optimizer status.

An **orbit-free** second implementation checks every one of the 7,261 labelled nonmembers on 22 points using integer bit masks, independently reconstructs the conflict graph, colors it by breadth-first search (not the trace proof), and computes matching/cover cardinalities. All agree with the 18-entry table. The sorted threshold multiset is
`[5,6,9,11,12,13,15,15,16,18,18,19,19,21,21,24,27,27]`.
The SHA-256 of the deterministic table projection is
`25affd4db98cb19db6bf91729c54c5dfd03c2479b589d71239f182c365ffb435`.
Running with `--json` emits every explicit matching edge and cover vertex.

A separate local exploratory implementation used SciPy `milp` with binary cover variables and constraints `x_i+x_j≥1` for each edge; all 18 optimum values agreed with the matching sizes, with zero reported MIP gap. This was **same-author computational cross-checking**, not an independent mathematician's verification; SciPy is not needed for the reproducible certificate.

Reproduce:

```sh
python3 -m scripts.m076_f43_orbit_thresholds --check --json
python3 -m unittest discover -s tests -p 'test_m076_f43_orbit_thresholds.py' -v
python3 scripts/regen.py --check --fast
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

The tests include a forged deletion cover and a **counterexample to universal bipartiteness**: the five two-element edges of a five-cycle are sunflower-free, but their conflict graph against a disjoint set is itself an odd five-cycle. Thus the bipartite conclusion relies on the special construction, not a generic property of sunflower-free families.

## Sources, failed avenues and next falsifier

- H. L. Abbott, D. Hanson, N. Sauer, *Intersection Theorems for Systems of Sets*, JCTA 12 (1972), 381–389, [DOI](https://doi.org/10.1016/0097-3165(72)90103-3): original finite Δ-system construction context.
- H. L. Abbott and D. Hanson, *On finite Δ-systems*, Discrete Mathematics 8 (1974), 1–12, [DOI](https://doi.org/10.1016/0012-365X(74)90103-4), and *On finite Δ-systems II* (1977), [DOI](https://doi.org/10.1016/0012-365X(77)90139-X): historical finite extremal work requiring a deeper novelty audit.
- E. Axante et al., *Sunflower-Free Uniform Families: Recursive Constructions and Explicit Bounds*, [arXiv:2609.06175](https://arxiv.org/abs/2609.06175) (posted September 5, 2026): reports `54≤f(4,3)≤83` and the intersecting maximum 27. It does not report this exact local conflict-graph spectrum.
- [Previous five-deletion analysis](M076_F43_STABILITY.md) and [ten-deletion candidate PR #221](https://github.com/Svyable/100/pull/221): prior bounded neighborhood work. This packet **does not** claim to independently validate their simultaneous-insertion proofs.

**Failed/abandoned approaches:** An integer-programming cover optimization produced the same 18 numbers, but alone it would not explain completeness or yield a short structural proof. The naive conjecture that `H_C` is bipartite for *every* sunflower-free family is false (five-cycle control). A graph matching lower bound alone is not generally sharp for arbitrary conflict graphs; the explicit bipartiteness argument is essential. The earlier repeated deletion-radius enumeration is not necessary for the **single-insertion** spectrum, because König's theorem supplies the exact minimum directly.

**Next falsifiers:** independently audit the trace-case proof and all 18 orbit representatives; search older finite Δ-system literature for an equivalent bipartiteness/spectrum statement; test whether the new `(2,1,0)/(1,0,0)` type at eleven deletions can coexist with multiple insertions; and independently check a witness outside the symmetry-reduced 22-point universe. An actual 55-set family after eleven deletions would require **at least twelve** insertions. No evidence-state, solved-status, coverage or benchmark changes are justified. The Project 100 PR Landing task and cadence are unchanged.
