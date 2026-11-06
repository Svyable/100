# M097 — separated chord networks preserve exact graphic-metric TSP and subtour optima

**Date:** 2026-11-02 UTC. **Work ID:** `X-M097-DEEP-CHORD-NET`. **Claim:** [#243](https://github.com/Svyable/100/issues/243). **Scope SHA-256:** `ebd4e155b0221930f6f52a6bbf4a6ace8091747dbec90b63121a29cd4570c163`.

**Evidence:** Author-derived all-orders **restricted theorem candidate**, with a self-contained elementary proof, exact all-cut rational certificates, a separately coded Hamiltonian subset DP, and independent numerical LP checks. **No independent specialist mathematical review or historical novelty determination.** Not the global metric TSP four-thirds conjecture. Unlike the concurrently claimed one-cross-edge result [#241](https://github.com/Svyable/100/issues/241), this statement permits arbitrarily many simultaneous chords, including a chord triangle and chords within a single path.

## Exact statement

Let `k>=3` and `L_i>=2` be integers. Let `G_0` consist of two hubs `u,v`, the edge `uv`, and `k` internally vertex-disjoint `u-v` paths `P_i` of lengths `L_i`. Mark any finite collection of internal vertices on each `P_i` such that **every consecutive pair in the ordered list `u, marks, v` is separated by at least two original path edges**. Add an **arbitrary simple graph of unit-weight chords** whose edges join pairs of marked vertices and are not original path edges; different chords may share marked endpoints and may join marks of the same original path. Require at least one chord when referring to the chorded class. All vertices and edges remain undirected and unweighted.

Let `m=sum_i L_i` and `c_G` be the complete shortest-path metric on the vertices of the resulting graph `G`. Let `SEP(c_G)` be the symmetric subtour LP with `x(delta(S))>=2` for all nonempty proper `S`, `x(delta(v))=2`, and `x>=0`. Let `TSP(c_G)` be the minimum metric Hamiltonian tour cost.

**Candidate theorem (all orders and all allowed chord networks):**

```
SEP(c_G) = m
TSP(c_G) = m + (k mod 2) * min(1, min_i L_i - 2).
```

Thus any number of suitably separated internal chords leaves **both** optima equal to those of the graph without chords. In particular, the exact integrality ratio is `1` if `k` is even or some `L_i=2`, and `(m+1)/m` otherwise.

**Joint quantitative optimal-face statement.** For *every* feasible subtour vector `x` with cost `m+epsilon`, let `B` be the set of unordered metric pairs `ab` for which **some** shortest `a-b` path in `G` uses either the direct hub edge `uv` or **at least one of the added chords**. Then

```
sum_{ab in B} x_ab <= epsilon.
```

This is a **single joint inequality**, not a sum of separate bounds for individual chords. In particular, every LP optimum excludes *all* metric pairs admitting a shortest path through any special edge, even with shortest-path ties.

**Sharp ratio with at least two distinct chords:** the maximum within this restricted multi-chord class is **13/12**, attained by three length-four paths with a chord triangle joining their middle vertices (or two edges of that triangle). For a nonintegral instance all `L_i>=3` and `k` is odd. Two distinct simple chords need at least three marked vertices. If these lie on three different paths, those three paths have length at least four, giving `m>=12+3(k-3)`; if they occupy at most two paths, one path has at least two marks and length at least six, yielding `m>=6+4+3(k-2)` or the stronger one-path bound. Hence `m>=12` and the ratio is at most `13/12`. The 11-vertex three-path example has `m=12`, `SEP=12`, `TSP=13`.

## Proof, independent of the earlier one-chord result

**A. Segment-cut lower bound.** Partition every original long path at its marked vertices. The resulting segments `A` have lengths `s_A>=2`, and their interior vertices have degree exactly two in `G`. Take any feasible subtour vector `x`. Route every metric pair `ab` along an arbitrary shortest `a-b` path in `G`, producing nonnegative original-edge loads `y_e` of total weight `cost(x)`. For every vertex cut `S`, `y(delta_G(S))>=x(delta(S))>=2`, because every path between opposite sides crosses the cut at least once.

For any two distinct edges `e,f` of one segment `A`, the nonempty consecutive vertex interval strictly between these edges has exactly `e,f` as its edge boundary: no marked vertex is internal to the segment. Thus `y_e+y_f>=2`. Sum over all unordered edge pairs in a segment of length `s`: `(s-1) sum_{e in A}y_e >= s(s-1)`, so `sum_{e in A}y_e>=s`. The segments partition the `m` original long-path edges; all special-edge loads are nonnegative. Consequently `cost(x)>=m`, regardless of the number or placement of allowed chords.

**B. Explicit exact subtour primal.** Let `alpha=2/k` and `gamma=(k-2)/(k(k-1))`. On each original long path, give its first and last edges weight `alpha` and every other original edge weight one. For each unordered pair of distinct paths, give their first internal vertices a metric edge of weight `gamma`, and likewise their last internal vertices; if a length-two path causes coincidences, add the weights. All other `x` variables vanish. Every vertex has degree exactly two. The used original edges have metric cost one. The same-hub shortcuts have metric cost exactly two: the two-edge route through the hub exists, while no new chord is incident with a first or last internal vertex (all marks are at least two edges from both hubs), so a direct edge of cost one cannot exist. Thus the objective is exactly `m`.

For completeness, all subtour cuts hold. Let `t_u` count first internal vertices opposite `u`, and `t_v` count last internal vertices opposite `v`. At either hub the spokes and same-hub shortcuts contribute `F(t)=alpha*t+gamma*t*(k-t)`, with `F(0)=0`, `F(1)=1`, `F(k)=2`, and `F(t)>=1` for all integer `1<=t<=k` by concavity. If both counts are positive the cut is at least two. If either is `k`, that hub contributes two. If one is zero and the other strictly between zero and `k`, a path has first and last internal vertices on opposite sides, forcing a unit-weight interior edge across the cut (whether the hubs are on the same or opposite sides). If both are zero and hubs are opposite, every path contributes an interior crossing (a length-two path would be impossible), giving at least `k>=3`. If both are zero and hubs are on the same side, a nontrivial cut must contain an internal vertex away from the first and last internal vertices of its path and has at least two interior crossings. Hence `SEP=m`. Chords do not change these complete-graph LP cut constraints.

**C. Eulerian parity lower bound.** Any metric Hamiltonian tour expands into a connected spanning Eulerian multigraph of the same total integer length on `G`. Apply part A to its integer multiplicities. If total length equals `m`, every segment must attain its lower bound and **all** special edges `uv` and added chords have multiplicity zero. For a segment of length at least three, pair inequalities and equality force every edge multiplicity to be exactly one. A segment of length two has exactly the possibilities `(1,1)`, `(2,0)`, or `(0,2)`. At each internal vertex, including every marked vertex, Eulerian degree and zero chord multiplicities force the parities of the two neighboring original-path edges to agree. Thus each original path has a common edge parity.

An unmarked path of length at least three cannot have even parity at equality. A marked path cannot either: if its parity were even, every segment would have length two and contain one zero edge, hence the path would have at least two zero edges. Between two consecutive zero edges lies a nonempty vertex interval disconnected from both hubs and all other paths, because every chord is unused. This contradicts connectedness. Therefore, when `k` is odd and all `L_i>=3`, every original path is odd and hub `u` has odd degree `k` (the hub edge is unused), impossible. So `TSP>=m+1`.

For matching upper constructions: if `k` is even, take every long path once, omit all special edges. If `k` is odd and a length-two path exists, take all other long paths once, replace that two-edge path by twice one of its edges, and omit its other edge. Both are connected spanning Eulerian multigraphs of cost `m`. In the remaining case, take every long path and the direct hub edge once for cost `m+1`. Shortcutting Euler tours in the complete metric gives Hamiltonian tours no more expensive. This proves the claimed exact formula.

**D. Joint geodesic-mass inequality.** In the routing in part A, write `delta_A=sum_{e in A}y_e-s_A>=0`. Then the *exact* excess decomposition is

```
epsilon = y_uv + sum_{e added chord} y_e + sum_A delta_A.
```

For every metric pair in `B`, choose a shortest route that traverses at least one special edge. This independent choice of routes gives `sum_{ab in B}x_ab <= y_uv+sum_chords y_e <= epsilon`. This proves the joint inequality. It does not assume uniqueness of shortest paths or independence of chord events.

## Adversarial checks and negative boundary

- `python3 -m scripts.m097_deep_chord_net --check --json` reconstructs each graph and its BFS metric, checks the explicit primal in exact `Fraction` arithmetic against **every** nontrivial subtour cut and every degree equation, and computes the metric Hamiltonian optimum by a separate subset DP. Fixed cases include a two-chord path, a three-chord triangle, a same-path chord, two separated crossings on the same two paths, odd/even `k`, and length-two uncrossed paths. A deterministic seeded sweep also attacks variable length and chord patterns.
- The checker enumerates metric pairs admitting geodesics through **any** special edge, checks zero optimal-primal mass there, and challenges the joint mass inequality with seeded Hamiltonian tours. Dedicated tests reject close or shallow marks, duplicate chords, a forged primal and an overly broad theorem.
- A separately written SciPy/HiGHS optimizer on a different machine solves the **full** subtour LP, independently of the explicit-primal constructor. It matched `SEP=m` on seven of the eight fixed cases (the remaining 14-vertex case was checked exactly by all cuts and DP); numerical LP confirmation is not an external mathematical review.
- **Failed broader hypothesis:** permitting a chord with one endpoint adjacent to a hub can reduce TSP. For `L=(4,4,3)`, add a chord between position 2 on the first path and position 3 on the second. The tour `0-2-5-6-7-3-4-1-9-8-0` has cost 11, whereas the separated-chord formula would predict 12. Literal metric subset DP verifies 11. Thus the spacing condition cannot simply be dropped. A second, LP-specific boundary is three length-three paths with a direct hub edge and an extra edge between the first internal vertices of two paths: the eight-vertex metric has **SEP=17/2 < m=9** (full-cut SciPy/HiGHS optimization) and **TSP=9** (exact subset DP). This is outside the separated-mark hypothesis and independently challenges the LP extrapolation.
- **Unproved stronger avenue:** a similar support-mass inequality for *all* pairs outside the original long-path and same-hub-shortcut support may hold, as in the chord-free case, but is **not asserted here**. The segment argument directly controls only special-edge geodesics.

## Sources, provenance, limitations and next falsifier

- Held and Karp, *The Traveling-Salesman Problem and Minimum Spanning Trees*, **Operations Research 18** (1970), [DOI](https://doi.org/10.1287/opre.18.6.1138): subtour-relaxation background.
- Sebő and Vygen, *Shorter Tours by Nicer Ears*, [arXiv:1201.1870](https://arxiv.org/abs/1201.1870) (2012): ear decompositions and graphic TSP; **not** a claim that this exact chord-network invariance is new.
- Qian, Schalekamp, Williamson and van Zuylen, *On the Integrality Gap of the Subtour LP for the 1,2-TSP*, [arXiv:1107.1630](https://arxiv.org/abs/1107.1630), published 2015: different restricted metric family.
- Cook, Hougardy and Petrich, *Extending Exact Integrality Gap Computations for the Metric TSP*, [arXiv:2603.12995](https://arxiv.org/abs/2603.12995) (March 2026; updated September 2026): exact finite extreme-point census, not this all-orders graph class.
- Existing repository [chord-free claim #228](https://github.com/Svyable/100/issues/228) and [single deep crossing claim #241](https://github.com/Svyable/100/issues/241) are **author-derived pending-review** baselines, not independent validation. The present proof is written without assuming either theorem.

**Historical novelty is unknown.** The pair-cut argument may be subsumed by older subdivision or 2-edge-connected-spanning-multigraph polyhedral results. A targeted source search found no exact statement but cannot establish priority. An independent specialist should audit the cut case split, the connectedness obstruction for a marked path with two zero edges, and whether an existing ear-decomposition theorem already implies the result. A next concrete falsifier is a small graph with multiple marked vertices per path and a nontrivial chord cycle whose exact LP or TSP differs from the formula; the present checker handles some such cases, not all.

No solved status, independently accepted outcome, benchmark trial, coverage slot or separate Project 100 PR Landing task/cadence is changed.
