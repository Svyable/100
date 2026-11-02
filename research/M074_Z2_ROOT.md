# M074 — forbidden nine-vertex profiles at the CH(27,9) z=2 root

**2026-11-02 UTC · Work ID:** `X-M074-Z2-ROOT` · [Claim #247](https://github.com/Svyable/100/issues/247) · **scope SHA-256:** `4713c42ec0dcf8a3893010f326f49f42a58335ebdf05613e7a188af5d4b2225d`.

**Status:** Author-derived elementary **restricted lemma and conditional CH(27,9) root theorem candidates**; no external specialist mathematical review or historical-novelty determination. Not a proof of the full CH(27,9) case or of the general Caccetta–Häggkvist conjecture. The conditional root theorem relies on two other unreviewed repository lemmas. Exploratory integer-solver infeasibility statuses are **not** used as proof certificates.

## Precise new local obstruction

Let `H` be a loopless **oriented** graph on nine vertices, with no directed triangle and minimum outdegree at least two. Then its sorted outdegree multiset cannot be any of:

| Profile | Outdegrees | Arcs |
|---|---|---:|
| P1 | `2,2,2,3,4,4,4,4,4` | 29 |
| P2 | `2,2,2,3,3,3,3,3,8` | 29 |
| P3 | `2,2,2,2,4,4,4,4,5` | 29 |
| P4 | `2,2,2,2,4,4,4,4,4` | 28 |

This does not exclude all 28- or 29-arc graphs. A known 29-arc witness is the seven-vertex circulant with steps 1 and 2, augmented by two successive dominating sources; its outdegrees are `2,2,2,2,2,2,2,7,8`.

### Elementary proof

Write `a(w)=d⁺(w)`, `b(w)=d⁻(w)`, and `L={w:a(w)=2}`. Use the earlier nine-vertex rooted inequality `a(w)+2b(w)≤10` from [M074_NINE_VERTEX.md](../proofs/M074_NINE_VERTEX.md). An outdegree-eight vertex has indegree zero by orientation.

**Saturation lemma.** A vertex `w` with `(a(w),b(w))=(4,3)` points to four distinct vertices of outdegree two. Indeed, its outneighborhood `Q` has four vertices, its inneighborhood three, and it has just one nonneighbor `c`. No vertex of `Q` can point to `w` or to an inneighbor of `w`, by orientation and the triangle prohibition. Thus every vertex of `Q` needs at least one outgoing arc inside `Q`. A four-vertex oriented triangle-free graph with minimum outdegree one is a directed four-cycle: it has a directed cycle, necessarily of length four, and a chord creates a triangle. Every vertex of `Q` therefore has exactly one outgoing arc in `Q` and must point to `c` for its second. Hence all four have total outdegree exactly two.

If `|L|=3`, no vertex of outdegree four can have indegree three, so its indegree is at most two. In P1 the sum of indegree upper bounds is `3·4+3+5·2=25<29`. In P2 the outdegree-eight vertex has indegree zero, so the upper bound is `3·4+5·3+0=27<29`. Both are impossible.

Now let `|L|=4` and let `S` consist of vertices of outdegree four and indegree three. Each `s∈S` points to **all** four low vertices, so it receives no arc from any low vertex or from any other member of `S`. It has at most `5−|S|` possible inneighbors. Since its indegree is three, **`|S|≤2`** whenever `S` is nonempty.

For P3, the indegree sum is at most `4·4+(2·3+2·2)+2=28<29`, contradiction. For P4, the corresponding upper bound is `4·4+(2·3+3·2)=28`, exactly its arc count. Equality forces two saturated vertices `s₁,s₂`, all four low vertices of indegree four, and each of the remaining three high vertices `Y` of indegree two. Each `sᵢ` receives its three arcs from all of `Y`, while each `sᵢ` points to every low vertex. A low vertex cannot point to `sᵢ` (orientation), or to `y∈Y` (the directed triangle `y→sᵢ→low→y`). All four low vertices would have to send their two outgoing arcs within `L`, demanding eight arcs among four vertices, more than `binom(4,2)=6`. Contradiction. □

This proof uses a previous elementary rooted inequality and the literal four-cycle fact, **not** a solver or the pending three-low theorem.

## Exact z=2 necessary-profile reduction

In a hypothetical 27-vertex oriented directed-triangle-free graph with all outdegrees nine, choose an indegree-ten root `v` and put `A=N⁺(v)` (9 vertices), `B=N⁻(v)` (10), `C` (7). Let `α(a)=d⁺_A(a)` and `k(b)=d⁻_C(b)`; define `z=|{b∈B:k(b)=0}|`. The earlier [z=3 root dossier](../proofs/M074_ZERO_K_TWO.md) proves necessary inequalities for `m=Σα≤29`, `K=Σk≥92−2m+R(α)`, internal B-outdegree floors, subset capacities and girth deficits.

For **z=2**, there are **166** sorted `α` profiles and **3,003** sorted `k` profiles, or **498,498** relaxed pairs. The previous necessary conditions leave **475**. The proposed nine-vertex **three-low** theorem in [PR #237](https://github.com/Svyable/100/pull/237), *conditional on its correctness*, reduces these to **287**. The four forbidden profiles proved here remove **226** (P1: 137, P2: 80, P3: 8, P4: 1), leaving **61 relaxed pairs**. These are integer necessary-condition profiles, **not** 27-vertex graphs. The main checker reproduces the counts and independently enumerates all `3^6=729` four-vertex partial orientations; six labelled admissible directed four-cycles survive.

```sh
python3 -m scripts.ch27_z2_root --check --json
python3 -m unittest discover -s tests -p 'test_ch27_z2_root.py' -v
```

## Further elementary cuts: conditional exclusion of z=2

The preceding 61 residual profiles can be eliminated **without the exploratory MILP**. This produces the following precise **conditional theorem candidate**:

> Assume the rooted necessary inequalities from [M074_ZERO_K_TWO.md](../proofs/M074_ZERO_K_TWO.md), the eight-vertex min-outdegree-two arc cap from [M074_ELEMENTARY_24_REGULAR.md](../research/M074_ELEMENTARY_24_REGULAR.md), and the nine-vertex three-low theorem candidate in [PR #237](https://github.com/Svyable/100/pull/237). Then a 27-vertex 9-outregular oriented directed-triangle-free graph cannot have an indegree-ten root `v` for which exactly two vertices of `B=N⁻(v)` receive no arc from `C`. Combined with the earlier candidate `z≤2`, this yields **`z≤1` at each indegree-ten root** under the same unreviewed dependencies. It does **not** exclude the remaining `z=0,1` branches or the regular branch, and is **not** an independently accepted theorem.

**New seven/eight-vertex B-subset capacity cuts.** Let `f₁≥⋯≥f₁₀` be the forced internal B-outdegree floors, and let `S` contain the top `s` vertices. Every member of `S` has at most `10−s` B-outneighbors outside `S`.

For `s=7`, if `f₇≥5`, every vertex of `B[S]` has internal outdegree at least two. The elementary rooted inequality for a seven-vertex oriented triangle-free graph of minimum outdegree two gives `a+2b≤7`, so every indegree is at most two. Therefore `e(B[S])=14` exactly, and

```
f₁+⋯+f₇ ≤ 14 + 7·3 = 35.                 (A)
```

For `s=8`, if `f₈≥4`, the induced eight-vertex graph has minimum outdegree at least two and hence at most 21 arcs by the earlier elementary eight-vertex lemma. Therefore

```
f₁+⋯+f₈ ≤ 21 + 8·2 = 37.                 (B)
```

These are necessary conditions on **actual B graphs**, not heuristic cuts. Applied in order (A), then (B), they exclude **75+83** of the 475 old relaxed profiles.

Next apply the pending three-low lemma (144 additional exclusions), the four forbidden A profiles proved above (156 additional exclusions), and the elementary indegree budgets below (16 exclusions). Exactly **one** integer pair remains:

```
α=(2,2,2,2,3,3,3,3,8),  m=28
k=(0,0,3,4,5,6,6,6,6,6),  K=42
f=(6,6,6,6,6,5,4,3,0,0).
```

The 16 indegree-budget exclusions concern `α=(2,2,2,2,3,3,3,4,8)` (12 pairs) and `α=(2,2,2,3,3,3,3,4,7)` (4 pairs). In the first, the maximum indegree sum is `4·4+3·3+3+0=28<29=m` (the outdegree-eight vertex has indegree zero). In the second, the three low vertices force the outdegree-four vertex's indegree to be at most two by the saturation lemma, so the indegree sum is at most `3·4+4·3+2+1=27<29=m`.

**Final eight-vertex equality obstruction.** For the last floor tuple, take the top eight B vertices `S`. Each sends at most two arcs outside `S`, so its internal outdegree is at least its floor minus two. The eight internal lower bounds are

```
(4,4,4,4,4,3,2,1), whose sum is 26.
```

Every vertex of `B[S]` has positive outdegree. Any triangle-free oriented graph on eight vertices with minimum outdegree at least one contains a directed cycle of length at least four; a shortest directed cycle is chordless, so the graph has **at least two missing unordered pairs**. Thus it has at most `binom(8,2)−2=26` arcs. Equality here would force the displayed internal outdegrees exactly.

We now classify equality: with exactly two missing pairs, the shortest cycle must be a directed four-cycle `Q`, and the two missing pairs are its diagonals. All other pairs are oriented. The four vertices `T` outside `Q` form a tournament, necessarily transitive (no directed triangle). Every vertex of `T` must either dominate all of `Q` or be dominated by all of `Q`: any mixed orientation has a transition along the directed cycle creating a directed triangle. If one `t∈T` is dominated by `Q` and another `t'∈T` dominates `Q`, then `t'→t` is forced (otherwise `t→t'→Q→t` is a triangle). The last vertex of the transitive tournament cannot be dominated by `Q`, since then it would have outdegree zero. Consequently **every** vertex of `T` dominates `Q`. The only possible sorted outdegrees are therefore

```
(1,1,1,1,4,5,6,7),
```

incompatible with `(1,2,3,4,4,4,4,4)`. This eliminates the final relaxed profile. □

**Exact certificate ledger:** of the 475 original z=2 relaxed pairs, the mutually exclusive exclusions are `75` (seven-vertex cap), `83` (eight-vertex cap), `144` (conditional three-low), `156` (four forbidden profiles), `16` (final A indegree budgets), and `1` (eight-vertex equality), totaling **475**, with **zero residual integer profiles**. The standalone script independently classifies every pair using the stated inequalities. A separate test enumerates the 16 possible all-in/all-out patterns between a fixed four-cycle and four transitively ordered external vertices and finds only the expected extremal degree multiset. These are author-side controls, **not independent mathematical review**.

The conditional theorem does **not** use the 403 exploratory MILP infeasibility verdicts. Its unresolved obligations are the correctness of the imported root and three-low lemmas, independent verification of the new exact integer classification and eight-vertex equality proof, and historical priority.

### Computational lead — not a theorem

A separately coded exploratory SciPy/HiGHS integer model imposes all ten-vertex B orientation constraints, forbids every directed triangle, and enforces the derived B-outdegree floors. Among the 475 relaxed profiles it reported **403 infeasible and 72 feasible**, across 292 distinct B-floor vectors. All 72 feasible B cases have either fewer than three `α=2` entries or one of P1–P4. The positive MILP witnesses were checked literally for digons, triangles and floors. **The 403 infeasibility statuses lack exact, independently replayable UNSAT certificates.** They are **not used** in the conditional z=2 exclusion proved above. No full A/B/C realization was attempted. The solver result is a promising **falsifiable proof lead** only.

## Prior art, failed avenues, provenance and next falsifier

- **Known background:** Caccetta and Häggkvist, *On minimal digraphs with given girth*, Congressus Numerantium 21 (1978), 181–187; Hladký, Kráľ and Norin, *Counting flags in triangle-free digraphs*, Combinatorica 37 (2017), 49–76, [DOI](https://doi.org/10.1007/s00493-015-2662-5); Grzesik, *On the Caccetta–Häggkvist Conjecture with a Forbidden Transitive Tournament*, EJC 24(2) (2017), [DOI](https://doi.org/10.37236/5954). These papers provide context, not independent validation of the four-profile lemma; historical novelty remains unknown.
- **Failed direct z=3 transfer:** the old root and girth cuts alone leave 475 z=2 profiles. The old z=3 endpoint arguments do not eliminate them.
- **Failed proof shortcut:** solver-reported B infeasibility is not a mathematical certificate. A passed same-author self-check is not independent specialist review.
- **Falsifiers:** (i) a literal nine-vertex counterexample with P1–P4, (ii) an additional relaxed z=2 profile passing the five existing filters, (iii) a failure of the pending three-low theorem, or (iv) a realizable B graph for one of the 403 purportedly infeasible floor vectors. The highest-value next step is **independent specialist review** of the new seven/eight-vertex cuts, eight-vertex extremal classification, exact profile enumeration, and the imported three-low and root lemmas. Independent LRAT/DRAT certificates for the exploratory 403 B-floor exclusions would provide a genuinely separate proof path, not a prerequisite for the new conditional argument. No global result follows before those gates.

No solved/evidence-state, independent-acceptance, coverage, benchmark, or separate Project 100 PR Landing task/cadence changes. This research branch is **not merge-ready** without full regeneration, repository tests and exact-head CI.
