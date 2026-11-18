# M097 — exact subtour value with one unsubdivided core edge

**Claim:** [#383](https://github.com/Svyable/100/issues/383). **Work ID:** `X-M097-ONE-SHORT-EDGE-SEP`. **Date:** 2026-11-17.

**Status:** Author-side restricted proof candidate. Not independently reviewed or certified historically novel. No implication that the general four-thirds conjecture is solved. This scope differs from [the all-subdivided formula](M097_SUBDIVISION_CORE.md), which assumes every core path has length at least two.

## Precise theorem

Let `H=(V,E)` be a finite connected **bridgeless loopless multigraph**, with `|V|>=2`; parallel core edges are indexed separately. Choose one edge `e` and replace it by a **unit** edge. Replace each other edge `f` by an internally vertex-disjoint unweighted path of integer length `L_f>=2`. Write `G` for the resulting graph and `M=1+sum_{f != e} L_f`. Let `SEP(G)` be the symmetric complete-shortest-path-metric subtour LP (degree equalities 2 and every proper cut at least 2). Then

\[
\boxed{\operatorname{SEP}(G)=
\begin{cases}
M,&\text{if }e\text{ belongs to a two-edge cut of }H,\\
M-1,&\text{otherwise.}
\end{cases}}
\]

The first condition is equivalent to `H-e` having a bridge. The theorem is **not** asserted for two or more unit edges, nonunit edge weights, or a core with bridges.

## Proof, with external dependency made explicit

Define `z_2cut(G)` as the minimum of `sum_{a in E(G)} y_a` over nonnegative graph-edge loads satisfying `y(delta_G(S))>=2` for every proper nonempty shore `S`. The classical **parsimonious property** (Goemans–Bertsimas, 1993) identifies the complete-metric degree-two subtour optimum with the complete-metric cut-cover optimum for metric costs. The latter equals `z_2cut(G)`: any original-graph edge solution embeds at the same cost into the complete-metric cut cover, while routing each complete-metric edge along a shortest original-graph path preserves cost and yields graph-edge loads meeting every graph cut. Hence `SEP(G)=z_2cut(G)`. This classical theorem is an essential named input; the proof below is otherwise elementary.

For each subdivided core path `f` with `L=L_f>=2` and expanded edges `f_1,...,f_L`, the internal-vertex segment between `f_i` and `f_j` has boundary exactly those two edges. Thus `y_{f_i}+y_{f_j}>=2` for every `i<j`. Sum all `L(L-1)/2` inequalities and divide by `L-1` to get `sum_i y_{f_i}>=L`. Summing over `f != e` gives the universal lower bound `SEP(G)>=M-1`.

If `H-e` is bridgeless, the expanded `G-e` is a connected bridgeless spanning graph. Set `y_e=0` and every other graph-edge load to 1. Every nontrivial cut has at least two edges of `G-e`, so this is feasible and costs `M-1`. The lower bound is attained.

Otherwise `H-e` has a bridge `f`. Since `H` is bridgeless, `{e,f}` is a two-edge cut of `H`. Choose a core shore `A` whose boundary is precisely `{e,f}`. For each expanded path edge `f_i`, lift `A` to a shore in `G` with boundary exactly `{e,f_i}`: place internal vertices of every other core path on their endpoints' common side, and take the appropriate prefix of the path for `f`. Hence `y_e+y_{f_i}>=2` for every `i`.

Write `L=L_f`. We already know `sum_i y_{f_i}>=L`. If `y_e>=1`, then `y_e+sum_i y_{f_i}>=L+1`. If `0<=y_e<=1`, each `y_{f_i}>=2-y_e`, and `y_e+sum_i y_{f_i}>=2L-(L-1)y_e>=L+1`. All other subdivided paths cost at least their lengths, so `z_2cut(G)>=M`. Finally `G` is bridgeless, so `y=1` on every edge satisfies every cut and costs `M`. This proves both cases for arbitrary core size.

## Exact tour formula survives unit edges (separate observation)

For any connected loopless multigraph core with positive integer path lengths **including 1**, let `F` range over core edge subsets of even degree at every core vertex, and let `c(F)` count components of `(V,F)`, including isolates. The graphic metric tour optimum satisfies

\[
\operatorname{TSP}(G)=M+\min_{F\text{ even}}
\left[\sum_{f\notin F}(L_f-2)+2(c(F)-1)\right].
\]

Proof: expand any metric tour into a connected spanning Eulerian multigraph. Multiplicity parity is constant along each expanded path. Odd paths cost at least `L_f`. An even path may omit at most one edge, or else it strands an internal segment; a broken even path costs at least `2(L_f-1)` and a through even path at least `2L_f`. At least `c(F)-1` through paths connect the odd-path components. Conversely, choose a spanning tree on those components in the contracted core, use each odd path once, double each selected through path, and for every other even path omit its first edge and double the remaining edges. This is connected, spanning, Eulerian, and has the displayed cost. A unit even path not selected simply disappears. This extends the existing author-side derivation; the underlying even-subgraph method is classical and **novelty is not asserted**.

## Adversarial controls and boundary

- `H=K4`, one edge length 1 and all other core edges length 2: `M=11`, no two-edge cut containing the short edge, `SEP=10`. Thus extending the old all-lengths-at-least-two formula `SEP=M+B` to unit lengths is false.
- `H=C3`, core path lengths `(1,2,2)`: `M=5`, the short edge lies in a two-edge cut, `SEP=5`. Thus the naive universal `SEP=M-1` claim is false.
- Local author-side test artifact `check.py` used 115 expanded graphs of at most 11 vertices, comparing an independently formulated complete-metric subtour LP and graph-edge cut-cover LP using HiGHS, and exact Held–Karp metric TSP against even-core-subset enumeration. Results: 65 two-edge-cut cases, 50 other cases, all passing. Both LPs used the same numerical solver, and this is **not** independent specialist validation. The test code and full output must be attached or independently reimplemented before accepting this as reproducible computational evidence. The theorem does not depend on this test count.

**Failed avenue:** Extending `SEP=M+B` verbatim fails on the K4 control. **Next falsifier:** find a bridgeless core and exactly one unit edge for which the two-edge-cut classification disagrees with a rational cut-LP primal/dual certificate, or demonstrate the cited parsimonious property does not apply to this formulation.

## Sources and review gate

- M. X. Goemans and D. J. Bertsimas, [*Survivable networks, linear programming relaxations and the parsimonious property*](https://www.mit.edu/~dbertsim/papers/ApproximationAlgorithms/Survivable%20networks%2C%20LP%20relaxations%20and%20the%20parsimonious%20property.pdf), *Mathematical Programming* **60** (1993), 145–166 (external LP theorem).
- Cornuéjols, Fonlupt and Naddef, *The Traveling Salesman Problem on a Graph and Some Related Integer Polyhedra* (1985), background on graphic TSP.
- [Earlier project core-parity proof](M097_SUBDIVISION_CORE.md), `L>=2` scope only.

**Stage A:** precise author-side proof candidate. **Stage B:** third-party proof audit and exhaustive prior-art check not performed. **Stage C:** no demonstrated customer/algorithmic advantage, so no commercial handoff. No claim of patentable exclusivity, independently accepted novelty, or general metric TSP progress.
