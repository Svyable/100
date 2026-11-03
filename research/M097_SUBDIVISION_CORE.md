# M097 — exact subdivision costs from core parity and connectivity

**Claim:** [#278](https://github.com/Svyable/100/issues/278). **Work ID:** `X-M097-SUBDIVISION-CORE`. **Scope SHA-256:** `3f60aa554a30aab86bcaedb85492f47ffc13881a2dbd252d9bd3d346639062c9`. **Date:** 2026-11-02 (America/Chicago).

**Status:** author-derived, all-orders restricted proof candidate. The arguments below use no unproved conjecture, heuristic solver verdict, or finite-to-infinite extrapolation. They have **not** received independent mathematical review or Lean verification. **Historical novelty is not established.** Several ingredients and the subcubic even-cover specialization are classical. No unrestricted metric-TSP or 4/3 resolution is claimed.

## 1. Precise theorem

Let `H=(V,E)` be a finite connected undirected loopless multigraph with `|V|>=2`. Parallel edges are allowed and individually indexed. Replace each edge `e` by an internally vertex-disjoint unweighted path of integer length `L_e>=2`, with no additional edges; denote the resulting simple graph by `G_L`. Write

\[
M=\sum_{e\in E}L_e,\qquad
\mathcal E(H)=\{F\subseteq E:\deg_F(v)\text{ is even for every }v\in V\}.
\]

For `F` in this cycle space, let `c(F)` count **all** connected components of `(V,F)`, including isolated vertices. Let `B(H)` be the bridge edges of the core. For the shortest-path metric of `G_L`,

\[
\boxed{\operatorname{TSP}(G_L)=
M+\min_{F\in\mathcal E(H)}
\left[\sum_{e\notin F}(L_e-2)+2(c(F)-1)\right].}\tag{1}
\]

The symmetric subtour LP, with nonnegative complete-metric edge weights, degree exactly two, and every proper nonempty cut of weight at least two, satisfies

\[
\boxed{\operatorname{SEP}(G_L)=M+\sum_{e\in B(H)}L_e.}\tag{2}
\]

Thus (1) determines **every** subdivision-length instance of a fixed core by the same finite list of `2^(|E|-|V|+1)` core states. The minimization remains exponential in the core's cycle rank; this is not a polynomial-time solution of arbitrary TSP. Only the arithmetic, not the number of states, depends on the path lengths.

## 2. Proof of the exact tour formula

A metric Hamiltonian tour expands along shortest paths to a connected spanning Eulerian edge-multigraph on `G_L` of equal cost. Conversely such a multigraph has a closed Euler walk that shortcuts to a metric Hamiltonian tour without increasing cost. Consequently these two minima agree.

At an internal degree-two path vertex, the two incident edge multiplicities have the same parity. A whole replacement path therefore has one parity. Let `F` consist of the paths of odd parity. Eulerian parity at every core vertex says `F` is in `mathcal E(H)`.

An odd path costs at least `L_e`. An even path can omit at most one of its edges: two omitted edges would strand the nonempty internal segment between them. Its cost is at least `2(L_e-1)`. If the even path omits no edge, its cost is at least `2L_e`, an extra two. Call such a path **through**. A broken even path never connects its two core endpoints.

Contract the components of `(V,F)`. The through even paths must connect the resulting `c(F)` vertices, since the expanded walk is connected. At least `c(F)-1` through paths are needed. Summing the three contributions proves the lower bound in (1), including isolated core vertices and bridges.

For the matching upper bound, choose any spanning tree of this contracted core. Use every edge of each odd path once. Double every edge of the even paths selected by that tree. On every remaining even path, delete its first edge and double the others. The original core is connected, so the contracted spanning tree exists. The result spans all vertices, is connected, has even degree at every vertex, and has exactly the cost inside (1). This proves equality for each selected `F` and then for the minimum. No search-completeness assumption is used.

## 3. Proof of the subtour value

**Lower bound.** Route any feasible complete-metric point along shortest paths in `G_L`. The resulting nonnegative loads `y` on graph edges preserve cost and satisfy `y(delta(S))>=2` for every cut. Every expanded edge of a core bridge is itself a bridge, so it has load at least two.

For a nonbridge core path of length `L`, any two different path edges bound a nonempty internal-vertex segment whose entire boundary consists of those two edges. Sum the `L(L-1)/2` pair-cut inequalities with coefficient `1/(L-1)`. Each path edge has coefficient one, and the lower bound on the path is `L`. The bridge singleton cuts and all these pair cuts partition the graph-edge coefficients, giving the right side of (2).

**Explicit upper bound on a block without articulations.** Start with weight one on each graph edge. At a core vertex `v` of degree `d>=3`, let `p_1,...,p_d` be its distinct adjacent subdivision vertices. Replace each spoke weight by

\[
\alpha_d=2/d,
\]

and add weight

\[
\gamma_d=(d-2)/(d(d-1))
\]

to each complete-metric edge `p_i p_j`, `i<j`. All other original edges retain weight one. Coincident shortcut edges receive the **sum** of contributions. Every edge is subdivided, so a spoke belongs to only one modified core star, and each internal vertex receives total incident contribution one from each of its two directions. At a core vertex the degree becomes `d alpha_d=2`. Thus every degree is two.

The neighbors `p_i,p_j` are at distance exactly two. The reduction of `d-2` units of spoke cost is balanced by `2 binom(d,2) gamma_d=d-2` units of shortcut cost. The objective remains the number of graph edges.

For any cut, write `t` for the number of these neighbors lying opposite `v`. The star and its shortcut clique contribute

\[
f_d(t)=\alpha_d t+\gamma_d t(d-t).
\]

Here `f_d(0)=0`, `f_d(d)=2`, and `f_d(t)>=1` for `1<=t<=d`: concavity reduces the last assertion to the endpoints `f_d(1)=1` and `f_d(d)=2`. Contributions from distinct stars and unchanged edges add, including coincident shortcuts.

A cut of weight less than two could therefore cross only one unchanged edge and no star, or only one star and no unchanged edge. The first case would make that unchanged edge a bridge. In the second case, deleting the star center leaves the block connected; because no other graph edge crosses, all remaining vertices must lie on the same side. Hence `t=d`, giving weight two after all. Both contradictions establish every subtour inequality. A block that is a cycle needs no star modification. A single bridge has the local point of weight two.

**Articulations.** Decompose `G_L` into its ordinary vertex blocks, including single-edge bridges. Each nonbridge block is itself a fully subdivided block, so the preceding construction applies. To glue two local points `x,y` sharing only `v`, write `a_u=x(v,u)` and `b_w=y(v,w)`, each summing to two. Halve all incident weights at `v`, retain other weights, and add `a_u b_w/4` on each cross edge `uw`.

The degrees remain two. For a cut avoiding `v`, let `A,B` be its portions on the two sides and put `a=sum_{u in A} a_u`, `b=sum_{w in B} b_w`. If the old cut weights are `d_1,d_2`, the new cut weight is `d_1+d_2-ab/2`. If only one portion is nonempty, the subtracted term is zero. If both are nonempty, the expression is at least `4-2=2`. Complementation handles cuts containing `v`. Cross-block distances add through `v`, so gluing preserves total cost. Induction constructs a feasible complete-metric point of the lower-bound value, proving (2).

This supplies an elementary witness for a value also obtainable from the classical parsimonious property. We do not claim that property as new.

## 4. Exact stabilization under uniform subdivision

Let all `L_e=L>=2`, and put `m=|E|`. A subset `D=E\F` is a `T`-join, where `T` is the odd-degree vertex set of `H`. For each attainable cardinality `d=|D|`, set

\[
c_d=\min\{c(E\setminus D):D\text{ is a }T\text{-join},\ |D|=d\}.
\]

Let `q` be the smallest attainable `d`, and `c_0=c_q` (the subscript zero here denotes the minimum-join case). Formula (1) becomes the finite lower envelope

\[
\operatorname{TSP}(G_L)=\min_d\{(m+d)L-2(d-c_d+1)\}.\tag{3}
\]

In particular, the exact first integer length from which the minimum-join line stays optimal is

\[
L_*=
\left\lceil\max\left(2,\max_{d>q}\left\{2+\frac{2(c_0-c_d)}{d-q}\right\}\right)\right\rceil,\tag{4}
\]

where the inner maximum is omitted if there is no larger attainable cardinality. For every integer `L>=L_*`,

\[
\operatorname{TSP}(G_L)=(m+q)L-2(q-c_0+1),\qquad L_*\le2c_0\le2|V|.\tag{5}
\]

Subtract the `d=q` line from a competing line: the difference is `(d-q)(L-2)+2(c_d-c_0)`. This proves (4), the permanent optimality in (5), and the bound from `c_d>=1`. If `L_*>2`, at `L_*-1` at least one competing line is strictly smaller, so (4) is an exact threshold, not just a sufficient bound. Ties at the threshold are allowed.

The slopes `m+d` selected by the lower envelope cannot increase as `L` increases. Equivalently, subdivision eventually favors minimum-size parity corrections, but need not favor them at short lengths. This is a structural consequence, not an assumption about the optimum.

## 5. A completely specified infinite family with a change at length three

Take two disjoint octahedral graphs `K_(2,2,2)`, with vertex sets `0,...,5` and `6,...,11`. Within each, the pairs `(0,1),(2,3),(4,5)` (shifted by six in the second copy) are the nonedges. Add exactly the cross edges `(0,6)` and `(1,7)`. This connected bridgeless core has 12 vertices and 26 edges. Uniformly subdivide every edge to length `L>=2`.

The four odd-degree vertices are `0,1,6,7`. Their induced graph consists of just the two cross edges. Hence the unique two-edge `T`-join is those cross edges. Its complement has two components, giving cost `28L-2`.

There is no three-edge `T`-join. A simple three-edge graph with exactly these four odd vertices can only have the relevant shape of a three-edge star, or a disjoint two-edge path and one edge; a triangle has no odd vertices and three disjoint edges have six. The star would need its center and three leaves to be the four terminals, but their induced graph has only two disjoint edges. In the path-plus-edge case the single edge must be one cross edge, and the remaining opposite-copy terminals have no common neighbor, so no two-edge path joins them. A three-edge path has only two odd vertices. These exhaust three-edge simple graphs with four odd vertices.

There is a four-edge `T`-join

\[
D=\{(0,2),(1,2),(6,8),(7,8)\}.
\]

Deleting it leaves both octahedral sides connected, and the two cross edges connect them to each other. Thus `c(E\D)=1`, giving cost `30L-8`. Every larger join has `d>=4`, so its line is at least `26L+d(L-2)>=30L-8`. We have proved, for **every** integer `L>=2`,

\[
\boxed{\operatorname{SEP}(G_L)=26L,\qquad
\operatorname{TSP}(G_L)=\min(28L-2,30L-8).}\tag{6}
\]

Equivalently, TSP is 52 at `L=2` and `28L-2` at every `L>=3`. The minimum-cardinality `T`-join alone gives 54 at `L=2` and is strictly suboptimal; both displayed joins tie at `L=3`. This explicitly falsifies the tempting shortcut “always choose a minimum-size parity correction.” The proof uses no exhaustive computation.

| Path length | Expanded vertices | Subtour LP | Exact TSP |
|---:|---:|---:|---:|
| 2 | 38 | 52 | 52 |
| 3 | 64 | 78 | 82 |
| 4 | 90 | 104 | 110 |
| L >= 3 | 26L-14 | 26L | 28L-2 |

This family has limiting ratio `14/13`, not `4/3`, and provides no larger global lower bound.

## 6. Reproduction, scope attacks, and failures

```sh
python3 scripts/m097_subdivision_core.py --check
python3 -m unittest discover -s tests -p 'test_m097_subdivision_core.py' -v
python3 scripts/regen.py --check
```

The full standalone sweep compares the parity formula with a separate integer Hamiltonian subset DP on **483** literal expanded metrics: all connected labeled simple cores through four vertices, independent path lengths two or three, and at most 11 expanded vertices, plus five parallel-edge/articulation/bridge controls. The distance implementation is Floyd–Warshall; it does not use the core formula. Each case also checks a constructed spanning Eulerian walk, a rational primal point, and a weighted cut-dual cover.

Primal checks verify every degree and the global minimum cut using exact rational Stoer–Wagner. Through ten vertices the minimum cut is also compared with literal enumeration of all cuts. Dual verification checks the boundary of each supplied shore and coefficient one on every expanded edge. On the 38-, 64-, and 90-vertex examples, exact cuts and walks are verified, but Hamiltonian DP is **not** run. All 32,768 even core subsets give a secondary check of the elementary family proof. These are different algorithms run by the same author, **not independent review**.

Fourteen targeted tests include parity-basis completeness against all edge subsets, a literal Hamiltonian permutation check, bridge doubling, unequal parallel-path lengths, explicit disconnected-support and parity failures, corrupt primal/dual certificates, and all four-vertex core stabilization checks.

Failed or invalid shortcuts, retained as controls:

1. Omitting `2(c(F)-1)` can produce a disconnected walk. The empty even subset of a path core demonstrates this immediately.
2. Applying the star point across an articulation can violate subtour feasibility. For two triangles sharing one core vertex with every edge subdivided once, the unglued star construction has a cut of weight **5/3**. Block gluing repairs it.
3. The SEP identity needs the subdivision hypothesis: the unsubdivided `K4` has `SEP=TSP=4`, not six. The parity reduction itself can be extended to length-one edges; it is the common domain and the explicit LP identity that are restricted here.
4. Minimum-cardinality `T`-joins need not give the exact short-subdivision optimum; (6) is a literal counterexample.
5. A first attempt to obtain an upper LP point by keeping all original edges at weight one fails the degree equations at branching vertices. The rational stars and articulation construction supply the missing step.

## 7. Prior art and what remains unestablished

Primary sources checked 2026-11-02 (America/Chicago):

- Goemans and Bertsimas, *Survivable Networks, Linear Programming Relaxations and the Parsimonious Property*, Mathematical Programming 60 (1993), 145–166, [author-hosted paper](https://www.mit.edu/~dbertsim/papers/ApproximationAlgorithms/Survivable%20networks%2C%20LP%20relaxations%20and%20the%20parsimonious%20property.pdf). Theorem 1 preserves cut-LP optima after imposing degree constraints in metric costs. Thus our SEP value can also follow from a classical theorem plus the explicit cut lower bound; it must not be advertised as a new general LP equivalence.
- Wigal, Yoo and Yu, *Approximating TSP walks in subcubic graphs*, [arXiv:2112.06278](https://arxiv.org/abs/2112.06278), published JCTB 158 (2023), [DOI 10.1016/j.jctb.2022.09.002](https://doi.org/10.1016/j.jctb.2022.09.002). Equation (1) explicitly gives `tsp(G)=n(G)+exc(G)-2` for subcubic graphs and attributes it to Dvořák–Král'–Mohar. Our formula specializes to that identity: an even core subgraph consists of cycles and isolated vertices, and every broken replacement path contributes its isolated internal vertices. **The subcubic specialization is therefore known, not novel.** Our presentation permits arbitrary core degrees and unequal lengths, but priority for that generalization is unresolved.
- Frei, Ghazy, Hartmann, Hörsch and Marx, *From Chinese Postman to Salesman and Beyond*, ISAAC 2024, [DOI 10.4230/LIPIcs.ISAAC.2024.31](https://doi.org/10.4230/LIPIcs.ISAAC.2024.31). Section 3.3 relates cubic continuous tours to cycle subpartitions and records a subdivision correspondence. This is directly related prior work; this note does not claim to introduce the connection between subdivisions and postman/TSP optimization.
- Project 100's [multitheta](M097_MULTITHETA.md) and [block-sum](M097_BLOCK_SUM.md) candidates supply earlier special-family formulas and articulation gluing. Equation (1) recovers the multitheta expression by core parity; those notes do not constitute external novelty certification.

The potentially distinct deliverables are the arbitrary-degree unequal-length core formula with executable certificates, the exact uniform-length threshold (4), and the explicitly solved two-octahedron family (6). A targeted search did not establish that any of these is historically new. A negative search result cannot do so.

**Next falsifiers/review tasks:** audit the all-orders connectivity lower bound; challenge the star-cut case split and articulation bookkeeping; compare arbitrary-degree even-subgraph formulations and continuous-tour reductions for a prior equivalent formula; independently check the exact threshold and the three-edge-join exclusion. No problem status, Solved entry, benchmark result, coverage slot, or independently accepted outcome changes are justified.
