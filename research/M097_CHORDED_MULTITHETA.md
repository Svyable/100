# M097 — a direct hub edge in a multitheta graphic metric

**Date:** 2026-11-02 UTC. **Claim:** [#228](https://github.com/Svyable/100/issues/228). **Work ID:** `X-M097-CHORDED-MULTITHETA`. **Scope SHA-256:** `66124a539f83fe23968a5896b795c2361a3a8ddc8acd1da4afce68093819c5ab`.

**Status:** Author-derived all-orders restricted theorem **candidate**, exact finite checks and a separate LP implementation. Historical novelty and independent specialist acceptance **not established**. This is not a new global bound for metric TSP, and does not settle the 4/3 conjecture. The unchorded multitheta proof candidate is [M097_MULTITHETA.md](M097_MULTITHETA.md); the chord case was deliberately excluded there.

## Exact statement

Let `k>=2` and `L_1,...,L_k>=2` be integers. Form a finite simple unweighted graph `G` with two hubs `u,v`, a **direct edge uv**, and `k` internally vertex-disjoint `u-v` paths of lengths `L_i`, with no other edges. Write `m=sum_i L_i` and `ell=min_i L_i`. On the complete-graph shortest-path metric `c_G`, use the symmetric subtour LP with nonnegative edge variables, degree exactly two, and cut weight at least two for every nontrivial cut.

**Restricted theorem candidate:**

```
SEP(c_G) = m
TSP(c_G) = m + (k mod 2) * min(1, ell - 2).
```

Thus the subtour LP is **unchanged** by the added direct hub edge, despite the metric becoming shorter. If `k` is even, or any long path has length two, the integrality gap is one. Otherwise `k` is odd and `ell>=3`, and the gap is `1+1/m <= 10/9`, with equality at `k=3, L=(3,3,3)`. This bound is specific to the chorded class.

## Proof: fractional lower bound and explicit primal

Take any feasible subtour point `x` on the complete metric. For every pair `a,b`, route `x_ab` along a shortest `a-b` path in `G` and call the resulting original-edge load `y`. Routing preserves cost, and `y(delta(S))>=x(delta(S))>=2` for every cut.

On any long constituent path `P` with `L>=2` edges `e_1,...,e_L`, the internal segment strictly between any two distinct edges `e_i,e_j` has graph boundary **exactly those two edges**: all internal path vertices have degree two, and the added hub edge never touches them. Consequently `y(e_i)+y(e_j)>=2`. Summing the `L(L-1)/2` inequalities gives `sum_{e in P}y_e>=L`. Sum over the `k` long paths; the hub-edge load is nonnegative. Therefore `SEP(c_G)>=m`.

For a matching primal, let `p_i` and `q_i` be the first and last internal vertices of path `i`. Put `alpha=2/k` on each long-path edge incident to a hub, weight one on each remaining long-path edge, and `gamma=(k-2)/(k(k-1))` on each shortcut `p_i p_j` and each `q_i q_j` for `i<j`. Coincident shortcut contributions (length-two paths) are **added**, not overwritten. Put zero on all other complete-graph edges, including `uv`.

Every vertex has degree two: hubs have `k alpha=2`, and each internal vertex receives `2 alpha+2(k-1)gamma=2` if it is both first and last, or `1+alpha+(k-1)gamma=2` otherwise. To verify all subtour cuts, for each hub count `t` adjacent internal vertices on the opposite side. Its spoke-plus-shortcut contribution is `F(t)=alpha*t+gamma*t*(k-t)`, with `F(0)=0`, `F(1)=1`, `F(k)=2`, and `F(t)>=1` for `1<=t<=k` (concavity, including `k=2`). If both hubs have positive counts, the cut is at least two. If exactly one count is positive and equals `k`, that hub alone contributes two. If exactly one is strictly between zero and `k`, the endpoint membership on a suitable long path forces at least one interior unit-edge crossing, making the cut at least two. If both counts vanish and the hubs lie on opposite sides, each long path forces an interior unit-edge crossing (at least `k>=2`); if the hubs lie on the same side, a nontrivial cut must isolate an internal segment and has at least two interior unit-edge crossings. These cases include length-two paths (where the first and last internal vertices coincide).

Every used long-path edge costs one in the chorded metric; every used same-hub shortcut between different paths costs exactly two. The primal cost is
`m-2*k+2*k*alpha + 2*k*(k-1)*gamma = m`.
Thus `SEP(c_G)=m`. The proof also follows by observing that the unchorded feasible point has cost `m` and adding the hub edge cannot increase its metric cost; the explicit cut argument above avoids relying on an independently unreviewed earlier theorem.

## Proof: integral tour parity

A complete-metric Hamiltonian tour expands to a connected spanning Eulerian edge-multigraph on `G` with the same cost; conversely an Eulerian spanning walk shortcuts to a metric Hamiltonian tour without increasing cost. On every long path, the two edge multiplicities at an internal degree-two vertex have the same parity, so **all edges of a given path have the same parity**.

An odd-mode path costs at least `L_i`. An even-mode path has at most one edge of multiplicity zero (otherwise an intervening internal vertex segment is disconnected); all other edges have multiplicity at least two. It costs at least `2(L_i-1)=L_i+(L_i-2)`. If `q` long paths are odd-mode and the direct edge has multiplicity `t`, even degree at a hub requires `t congruent q (mod 2)`.

For even `k`, all long paths once and no direct edge form a connected Eulerian spanning graph of cost `m`, which meets the pathwise lower bound. For odd `k`, all long paths once plus the direct edge form an Eulerian spanning graph of cost `m+1`. If `ell=2`, a better graph of cost `m` uses every long path except a length-two path once, and on that short path doubles one edge and omits the other (the internal vertex remains attached); the direct edge is omitted. If `ell>=3`, every even-mode path costs at least one above its baseline, while all-odd mode requires the direct edge an odd number of times, so every tour costs at least `m+1`. This establishes the formula.

## New optimal-face rigidity and quantitative stability (2026-11-02)

**Additional author-derived lemma (same claimed class, not a second claim).**
Let (x) be *any* feasible symmetric subtour-LP point on the chorded graph's
complete shortest-path metric, with objective (m+arepsilon). Let
(B) be the set of unordered vertex pairs ({a,b}) for which **at least
one** shortest (a)-(b) route in the original graph uses the direct hub edge
(uv). Then

[
arepsilonge 0,qquad sum_{{a,b}in B}x_{ab}learepsilon.
]

In particular **every** LP optimum has (x_{ab}=0) for every pair in
(B), including (x_{uv}=0). This is a statement about the *entire
optimal face*, not merely the displayed fractional witness. It is stronger
than observing that one optimum avoids the chord. It does not assert that
optimal *integral tours* always avoid the chord: when (k) is odd and all
(L_ige3), the integral optimum has value (m+1), not (m).

There is also a pathwise stability conclusion. For any choice of shortest
routes used to expand (x) to original-edge loads (y), and any constituent
path of length (Lge3), each of its edge loads satisfies

[
1-rac{arepsilon}{L-2} le y_e le 1+arepsilon.
]

Thus all loads on paths of length at least three are **exactly one** at
an LP optimum, irrespective of shortest-path tie-breaking. A path of length
two is exceptional: its two loads are forced to sum to two but need not
individually equal one by this argument.

**Proof.** Route every positive metric edge (ab) along an arbitrary
shortest (a)-(b) path in the original graph, obtaining nonnegative
loads (y) with total load equal to (m+arepsilon). Every cut of the
original graph has load at least two because its routed metric-edge
cut load is at least the original subtour cut. For any two edges (e,f)
on the same long path, the internal vertices strictly between them
have original graph boundary precisely ({e,f}). Hence
(y_e+y_fge2). Summing all such pairs gives
(sum_{ein P}y_ege L). Put
(delta_P=sum_{ein P}y_e-Lge0). Since the original edges consist of
the long paths and (uv),

[
arepsilon=y_{uv}+sum_Pdelta_P.
]

Choose the shortest route through (uv) for **every** pair in (B)
simultaneously; this is allowed because shortest paths are routed
independently. Then (y_{uv}gesum_{abin B}x_{ab}), proving the first
inequality. For the second, fix a path of length (Lge3) and set
(z_e=y_e-1). The pair inequalities say (z_e+z_fge0). If one
(z_e=-t<0), every other (z_fge t), so
(delta_P=sum z_fge(L-2)t). If one (z_e=t>0),
either all other deviations are nonnegative, or exactly one is
negative and the remaining (L-2) deviations compensate for it;
in either case (delta_Pge t). Because
(0ledelta_Plearepsilon), the claimed interval follows.
This proof is all-orders and does not invoke numerical optimization.

**Adversarial exact checks.** A separate script
`scripts/m097_chorded_optimal_face.py` builds the graph independently,
identifies all chord-geodesic pairs by comparing distances with and without
the chord, routes exact rational LP points, and checks both inequalities
against 26 optimum witnesses and 52 feasible tour/convex-combination
perturbations (at most nine vertices). Five dedicated tests additionally
compare the chord-geodesic set against a separate exhaustive DFS over all
simple shortest paths, test a deliberately infeasible perturbation, and
exercise a 13-pair forbidden set for the (k=3,L=(3,3,3)) instance.
The initially overstrong test assertion that every length-two example
has multiple chord-geodesic pairs was falsified: for ((2,2)) and
((2,2,2)), only ({u,v}) qualifies. The test was corrected; the
mathematical lemma was unaffected. These are same-author computational
cross-checks, **not** independent specialist acceptance.

The next meaningful falsifier is a feasible rational subtour point
with objective (m+arepsilon) but forbidden-pair mass greater than
(arepsilon), or a path-edge load outside the stated interval.
An external reviewer should separately audit the cut-routing implication,
the pairwise-boundary cuts, and the geodesic tie case. No historical
novelty is asserted.

## Reproduction and adversarial checks

```sh
python3 -m scripts.m097_chorded_multitheta --max-vertices 12 --json
python3 -m unittest discover -s tests -p 'test_m097_chorded_multitheta.py' -v
python3 -m scripts.m097_chorded_mincut
python3 -m scripts.m097_chorded_optimal_face --max-vertices 9 --json
python3 -m unittest discover -s tests -p 'test_m097_chorded_optimal_face.py' -v
python3 -m unittest discover -s tests -p 'test_m097_chorded_mincut.py' -v
```

Observed author-side exact sweep: **92** nondecreasing tuples, `2<=k<=5`, `2<=L_i<=7`, and at most 12 vertices; 45 even-k, 35 odd-k with a length-two path, 12 odd-k with all lengths at least three. Each instance reconstructs the shortest-path metric by BFS, verifies the proposed rational LP point against every degree and nontrivial cut, and independently computes the exact Hamiltonian tour optimum by subset DP (not by the parity formula). **Seven** targeted adversarial tests pass, including altered LP degree, invalid parameters, the direct edge's presence, parity boundaries and a false naive extension.

A separate, optional SciPy HiGHS implementation, written with a different graph representation and all full-subtour inequalities, independently optimized **20** instances of at most eight vertices and matched `SEP=m`. This is author-side cross-checking, **not** an independent specialist review.

**Additional adversarial min-cut replay (same author, separate algorithm).** The standalone `scripts/m097_chorded_mincut.py` reconstructs the rational witness from scratch as an integer-capacity weighted graph scaled by `k(k-1)`, without importing the original checker. It checks degree `2k(k-1)` at every vertex, cost `m k(k-1)`, and the **global** cut minimum `2k(k-1)` via a separately implemented Stoer–Wagner algorithm. The cut algorithm is itself compared with brute-force bipartitions on 210 seeded arbitrary weighted graphs with 2–8 vertices, including disconnected cases. The seven large/boundary examples include 20 length-two paths (22 vertices, cut 760 at scale 380), 13 length-three paths (28 vertices, cut 312 at scale 156), and four lengths (5,7,9,11) (30 vertices, cut 24 at scale 12). A one-unit edge-capacity tamper reduces a singleton cut below the bound, and invalid-length inputs are rejected. The independent algorithm and representation reduce shared implementation risk, but are still **author-produced checks, not external mathematical review**. These checks do not establish historical novelty or the completeness of the paper search.

**Failed extrapolations and boundaries:** (1) Treating the direct edge as a length-one path in the old unchorded formula predicts `SEP=m+1`, which is false already for `k=2,L=(2,2)` (actual `SEP=4`, not 5). (2) A direct hub edge does not always eliminate the fractional gap: `k=3,L=(3,3,3)` has `SEP=9,TSP=10`. (3) The restriction `k>=2` matters: with only one long path, `G` is a simple cycle and `SEP=TSP=L+1`, not `L`. (4) Adding the hub edge does not necessarily shorten the optimal tour; for even `k`, both chorded and unchorded formulas equal `m`. (5) The first tempting extension, allowing **one cross-path edge**, already falsifies `SEP=m`: start with `k=3`, lengths `(3,3,3)` and paths `0-2-3-1`, `0-4-5-1`, `0-6-7-1`, plus hub edge `0-1`; add only cross edge `2-5`. The 8-edge Hamiltonian cycle `0-4-5-2-3-1-7-6-0` proves `TSP<=8`. Every metric edge has cost at least one and the degree-two equations imply `SEP>=8`, hence **`SEP=TSP=8<m=9`**. This is an exact literal counterexample to extending the LP formula beyond degree-two path interiors, not a counterexample to the restricted theorem or to the 4/3 conjecture. An independent exploratory SciPy full-cut LP and subset tour DP gave the same values; the displayed cycle and trivial lower bound are the rigorous certificate.

## Primary literature, limits and next falsifiers

- Held and Karp, *The Traveling-Salesman Problem and Minimum Spanning Trees*, Operations Research 18 (1970), [DOI](https://doi.org/10.1287/opre.18.6.1138): classical LP baseline.
- Sebő and Vygen, *Shorter Tours by Nicer Ears*, [arXiv:1201.1870](https://arxiv.org/abs/1201.1870) (2012): graphic TSP and 2-edge-connectivity context.
- Qian, Schalekamp, Williamson and van Zuylen, *On the Integrality Gap of the Subtour LP for the 1,2-TSP*, Mathematical Programming 150 (2015), [author page](https://www.davidpwilliamson.net/work/publication/qian-s-wv-z-15/): distinct metric subclass.
- Boyd, Sitters, van der Ster and Stougie, *The Traveling Salesman Problem on Cubic and Subcubic Graphs*, Mathematical Programming 144 (2014), [DOI](https://doi.org/10.1007/s10107-012-0620-1): proves a 4/3 bound for the subcubic graphic class; the present graph has hub degree k+1 and for k>=3 is not subcubic. This paper gives context, not priority for the exact formula.
- Mnich and Mömke, *Improved Integrality Gap Upper Bounds for Traveling Salesperson Problems with Distances One and Two* (2018), [institutional record](https://cris.maastrichtuniversity.nl/en/publications/improved-integrality-gap-upper-bounds-for-traveling-salesperson-p/): a 10/9 result for a particular 1,2-TSP LP-support class; equality of the numerical constant does not identify the same metric family.
- Cook, Hougardy and Petrich, *Extending Exact Integrality Gap Computations for the Metric TSP*, [arXiv:2603.12995](https://arxiv.org/abs/2603.12995) (March 2026): current small-dimensional baseline.
- [M097_MULTITHETA.md](M097_MULTITHETA.md) and [M097_BLOCK_SUM.md](M097_BLOCK_SUM.md): repository-local antecedents, not external priority evidence.

The 8-vertex sharp example k=3, L=(3,3,3) lies within the repository's existing eight-vertex graph-metric census [M097_GRAPH8.md](M097_GRAPH8.md); its 10/9 ratio is **not** a new global lower-bound example. Targeted primary-literature searches did not identify this **exact** chorded formula. That is insufficient to claim historical priority: subdivided-dipole graphic TSP and the parity argument may be implicit in earlier work. An external specialist should check that the LP cut case split is complete, that the Eulerian mode argument covers arbitrary multiplicities, and that no published exact family formula subsumes this one. The one-cross-edge extension has now been **falsified by the explicit 8-vertex cycle above**. A genuinely different next falsifier is whether a controlled cross-edge class admits a revised formula in terms of the placement of the extra edge; that would require a new nonoverlapping claim and a separate literature audit. **No** full 4/3 bound, accepted outcome, solved status, coverage slot, benchmark result, or independent novelty credit follows.

**Workflow boundary:** The research branch carries this note, script and tests. Full repository regeneration, the complete repository test suite and exact-head CI have **not** been run in this environment; no mergeable PR is asserted. Add a conditional outcomes-ledger record and regenerate all derived files before opening a CI-gated PR. The separate Project 100 PR Landing task and cadence remain untouched.
