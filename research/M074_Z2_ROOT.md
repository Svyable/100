# M074 — forbidden nine-vertex profiles at the CH(27,9) z=2 root

**2026-11-02 UTC · Work ID:** `X-M074-Z2-ROOT` · [Claim #247](https://github.com/Svyable/100/issues/247) · **scope SHA-256:** `4713c42ec0dcf8a3893010f326f49f42a58335ebdf05613e7a188af5d4b2225d`.

**Status:** Author-derived elementary **restricted lemma candidate**; no external specialist mathematical review or historical-novelty determination. Not a proof of CH(27,9) or of the general Caccetta–Häggkvist conjecture. The exploratory integer-solver infeasibility statuses described below are **not** proof certificates.

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

### Computational lead — not a theorem

A separately coded exploratory SciPy/HiGHS integer model imposes all ten-vertex B orientation constraints, forbids every directed triangle, and enforces the derived B-outdegree floors. Among the 475 relaxed profiles it reported **403 infeasible and 72 feasible**, across 292 distinct B-floor vectors. All 72 feasible B cases have either fewer than three `α=2` entries or one of P1–P4. The positive MILP witnesses were checked literally for digons, triangles and floors. **The 403 infeasibility statuses lack exact, independently replayable UNSAT certificates.** Therefore we do **not** assert `z≠2`, `z≤1`, or a CH(27,9) theorem. A full A/B/C realization was not attempted. The solver result is a promising **falsifiable proof lead** only.

## Prior art, failed avenues, provenance and next falsifier

- **Known background:** Caccetta and Häggkvist, *On minimal digraphs with given girth*, Congressus Numerantium 21 (1978), 181–187; Hladký, Kráľ and Norin, *Counting flags in triangle-free digraphs*, Combinatorica 37 (2017), 49–76, [DOI](https://doi.org/10.1007/s00493-015-2662-5); Grzesik, *On the Caccetta–Häggkvist Conjecture with a Forbidden Transitive Tournament*, EJC 24(2) (2017), [DOI](https://doi.org/10.37236/5954). These papers provide context, not independent validation of the four-profile lemma; historical novelty remains unknown.
- **Failed direct z=3 transfer:** the old root and girth cuts alone leave 475 z=2 profiles. The old z=3 endpoint arguments do not eliminate them.
- **Failed proof shortcut:** solver-reported B infeasibility is not a mathematical certificate. A passed same-author self-check is not independent specialist review.
- **Falsifiers:** (i) a literal nine-vertex counterexample with P1–P4, (ii) an additional relaxed z=2 profile passing the five existing filters, (iii) a failure of the pending three-low theorem, or (iv) a realizable B graph for one of the 403 purportedly infeasible floor vectors. The highest-value next step is **independently replayable LRAT/DRAT or exact branch certificates** for the 403 B-floor exclusions, followed by review of all imported root lemmas. No global result follows before those gates.

No solved/evidence-state, independent-acceptance, coverage, benchmark, or separate Project 100 PR Landing task/cadence changes. This research branch is **not merge-ready** without full regeneration, repository tests and exact-head CI.
