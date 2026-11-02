# M097 — exact metric TSP and subtour LP on trees of multitheta blocks

**Claim:** [#189](https://github.com/Svyable/100/issues/189). **Work ID:** `X-M097-BLOCK-SUM`. **Scope SHA-256:** `a30860c84ceb8a1d24b6bedb10bbdc085b6560e7060888dff6ceb675846f974f`. **Date:** 2026-11-01.

**Classification:** author-derived all-orders restricted proof candidate, with exact rational certificates and separate tour/LP checks. **Historical novelty is unestablished and independent mathematical review has not occurred.** The unrestricted metric-TSP 4/3 conjecture is not resolved.

## Exact statement

Let G be a finite connected **simple unweighted** graph with at least two vertices, constructed by repeatedly identifying exactly one vertex of a new block with one existing vertex. Each block is one of: a bridge (single edge); a simple cycle of length at least 3; or a subdivided parallel-path graph with k>=2 internally vertex-disjoint paths between two hubs, of integer lengths L_i>=2, and no additional edges. These are genuine blocks in a block-cut tree, not arbitrary overlapping subgraphs.

Let c_G be the shortest-path metric. The symmetric Held–Karp subtour LP has nonnegative complete-graph edge variables, degree exactly two at every vertex, and cut weight at least two for every nontrivial cut. A two-vertex local bridge uses edge weight two, without an upper-bound-one convention.

Let b be the number of bridge blocks. For each cycle C let |C| be its edge count. For each multitheta block B put m_B=sum_i L_i, k_B=number of paths, and ell_B=min_i L_i. Then

\[
\operatorname{SEP}(c_G)=2b+\sum_C |C|+\sum_B m_B,
\]

\[
\operatorname{TSP}(c_G)=2b+\sum_C |C|+
\sum_B\bigl(m_B+(k_B\bmod 2)(\ell_B-2)\bigr).
\]

Consequently the ratio is exactly

\[
1+\frac{\sum_{B:\ k_B\ {\rm odd}}(\ell_B-2)}
{2b+\sum_C|C|+\sum_Bm_B}<4/3.
\]

It is one for every cactus graph (all blocks bridges or cycles), and can be greater than one even with bridges: theta(3,3,3) plus one pendant edge has SEP=11, TSP=12. The 4/3 limit is approached by a single classical theta(L,L,L) as L grows, not newly discovered here.

## Proof A: fractional articulation gluing

Suppose G1 and G2 meet only in vertex v. Let x1,x2 be feasible subtour points for their respective shortest-path metrics, with degree of v equal to two in each. Write a_u=x1(v,u), b_w=x2(v,w), so sum_u a_u=sum_w b_w=2. Retain every edge not incident to v; halve all weights on v-u and v-w; add cross-edge weight a_u b_w/4 between u in G1-v and w in G2-v.

Every other vertex retains degree two: the removed a_u/2 is replaced by sum_w a_u b_w/4=a_u/2. At v degree is (2+2)/2=2. All weights remain nonnegative.

For a cut with v outside, write A⊆V(G1)-v, B⊆V(G2)-v, a=sum_{u∈A}a_u, b=sum_{w∈B}b_w, and d_i the original x_i cut weights for A and B. Direct expansion gives the new cut weight

\[
d_1+d_2-\frac{ab}{2}.
\]

If only one of A,B is nonempty, the cut is at least two. If both are nonempty, d1,d2≥2 and 0≤a,b≤2, so the result is at least 4-2=2. Cuts containing v follow by complementation. Every cross-block shortest path passes through v. Replacing half of each v-edge with cross weights preserves total objective exactly, since each side's removed cost is replaced by its contribution to cross-edge distances. Iterate to glue arbitrarily many blocks.

**Failed first approach:** simply taking the union of local subtour points gives articulation degree four, not two. The cross-edge gluing is necessary.

## Proof B: explicit global rational cut-dual lower bound

For any complete-metric feasible x, route each x_ab along any shortest path in G. Let y_e be the resulting nonnegative load on original graph edge e. Routing preserves objective, and y(δ(S))≥x(δ(S))≥2 for every cut S.

The following nonnegative weighted cuts have total coefficient **exactly one on every original edge**:

- For each bridge e, remove e and take either component, with cut weight 1. Its boundary is {e}.
- For each cycle vertex w, remove its two cycle edges and take the component containing w, including any attached blocks. Give that cut weight 1/2. Each cycle edge occurs in exactly two cuts.
- For each multitheta path of length L, for each pair i<j of its L edges, remove those two edges and take the component containing the internal path segment between them, including attached blocks. Give that cut weight 1/(L-1). Each path edge occurs in L-1 cuts.

The block-cut-tree assumption ensures that these boundaries contain exactly the claimed original edges: an outside detour joining two distinct vertices of a block would destroy the decomposition. Summing weighted cut inequalities yields

\[
\sum_{e\in E(G)}y_e\ \ge\
2b+\sum_C |C|+\sum_Bm_B.
\]

`dual_cut_cover` checks every boundary and coefficient in exact rational arithmetic; the proof does not rely on a general graphical-TSP splitting-off theorem. Bridge and cycle blocks have evident matching local primal points (edge weight two for a bridge, one per cycle edge). For multitheta blocks use the explicit rational point from [the prior M097 multitheta dossier](M097_MULTITHETA.md), including its cut analysis. Proof A glues the local points without changing their summed objective. This matches the lower bound exactly.

## Proof C: integer tour additivity

A metric tour expands into a closed spanning walk on G at equal cost; conversely such a walk shortcuts to a metric tour at no greater cost. In a 1-sum, every excursion from one side into the other returns through the same articulation vertex. Therefore the walk restricted to each side is itself a closed spanning walk. Conversely concatenate optimal closed walks at the articulation. Induction gives TSP additivity.

A bridge must be traversed twice, a cycle has optimum its length, and the [multitheta Eulerian parity argument](M097_MULTITHETA.md) gives m_B+(k_B mod 2)(ell_B-2). This proves the integer formula. For each odd k_B≥3, ell_B-2<m_B/3; the aggregate ratio is strictly below 4/3.

## Reproduction, independent algorithmic paths, and negative controls

Run:

```sh
python3 scripts/m097_block_sum.py --check --json
python3 -m unittest discover -s tests -p 'test_m097_block_sum.py' -v
python3 scripts/regen.py --check
```

The standard-library script checks all degree equations and all complete-graph subtour cuts for a rational glued primal; every component-cut boundary and exact coefficient for the cut dual; and a separate iterative Held–Karp tour DP that ignores the block formula, including the 15-vertex two-theta case. Direct permutation enumeration checks a small glued-cycle example. Sixteen tests include 40 seeded random block trees, tampered primal and dual certificates, invalid blocks, bridge pitfalls and parity boundaries.

A separately authored SciPy HiGHS full-subtour-LP formulation (outside the committed standard-library script) returned optima **9, 11, 12, 13** for theta(3,3,3), that theta plus a leaf, plus a triangle, and plus a square, respectively. These numerical checks are secondary to the exact rational certificates and are **not** independent specialist review.

**Negative results:** (i) naive union of block LP points violates the degree equation at an articulation; (ii) "any graph with a bridge has an integral Held–Karp optimum" is false (nine-vertex theta plus leaf: 12/11); (iii) attaching blocks cannot increase the maximum block ratio within this class, by the weighted-average formula. (iv) extending block additivity to two-vertex overlap fails: two triangles sharing an edge have a four-edge Hamiltonian cycle, not the naive six-edge sum. No exhaustive search over all graph metrics was attempted.

## Literature, provenance and next falsifiers

- Held and Karp, *The Traveling-Salesman Problem and Minimum Spanning Trees*, Operations Research 18 (1970), [DOI 10.1287/opre.18.6.1138](https://doi.org/10.1287/opre.18.6.1138): classical LP framework.
- Sebő and Vygen, *Shorter Tours by Nicer Ears*, [arXiv:1201.1870](https://arxiv.org/abs/1201.1870) (2012): graphic TSP and 2-edge-connectivity context.
- Cook, Hougardy and Petrich, *Extending Exact Integrality Gap Computations for the Metric TSP*, [arXiv:2603.12995](https://arxiv.org/abs/2603.12995) (2026): recent small-n baseline.
- [Merged M097 multitheta proof candidate](M097_MULTITHETA.md), claim #187 / PR #188: the local block formula, not independent novelty certification.
- A targeted search for articulation-additive subtour bounds and cactus graphic TSP did not locate this exact cut-cover and gluing presentation. This **does not establish historical novelty**: articulation decomposition and graphical subtour relaxations are classical, and a specialist may find it implied by prior work.

**Next falsifiers:** independently audit the gluing cut identity and the two-removed-edges boundary in arbitrary block trees; find prior published 1-sum/additivity results subsuming the statement; independently regenerate rational primal/dual objects; test whether any analogous decomposition survives **two-vertex** attachment (cross-block paths may bypass the interface). No change to `data/solved.json`, evidence states or PR-landing cadence is justified.
