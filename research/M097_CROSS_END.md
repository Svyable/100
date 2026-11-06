# M097 — one cross-end edge: exact subtour LP and metric tour

**Date:** 2026-11-02 UTC. **Claim:** [#232](https://github.com/Svyable/100/issues/232). **Work ID:** X-M097-CROSS-END. **Scope SHA-256:** 02d08444ece094863fee99a31f711888197222f15b840f8718452cbf561d3a57.

**Evidence:** Author-derived all-orders restricted theorem **candidate** with a written proof, rational primal, independent-formulation finite LP optimization, exact Hamiltonian DP and adversarial controls. Neither historical novelty nor independent mathematical acceptance has been established. This is **not** a proof of the metric-TSP 4/3 conjecture, and is distinct from the chorded but cross-edge-free family in [draft PR #231](https://github.com/Svyable/100/pull/231).

## Exact statement

Fix k >= 3 and integers L_1,...,L_k >= 2. Take two hubs u,v joined by a direct edge, and k otherwise internally vertex-disjoint u-v paths P_i of lengths L_i. Add exactly one edge from the **first internal vertex of P_1** (next to u) to the **last internal vertex of P_2** (next to v). No other edges are allowed. Let m = sum_i L_i. Let SEP denote the symmetric complete-metric subtour LP with degree equations x(delta(w))=2, cut inequalities x(delta(S))>=2 and x>=0; TSP is the shortest Hamiltonian cycle in the unweighted graph's shortest-path metric.

**Restricted theorem candidate:**

    SEP = m - 1.
    TSP = m - 1 + [k even and min_i L_i >= 3].

Consequently TSP/SEP <= 12/11 in this class, with equality at k=4 and L=(3,3,3,3). The inequality is a restricted-class statement only; the known global 4/3 lower bound is larger.

## Reusable two-hub component-cut lemma

**Lemma (author-derived; historical priority unverified).** For any connected simple unweighted graph G with distinguished vertices u,v, suppose the nonempty connected components of G-{u,v} are W_1,...,W_r. Then for the shortest-path metric of G,

    SEP >= |V(G)| - 2 + r.

**Proof.** For a feasible complete-metric subtour point x, route each positive x_ab on any shortest a-b path in G, obtaining nonnegative original-edge loads y_e. This preserves the objective: sum_e y_e = sum_ab c_G(a,b)x_ab. For every vertex subset S, y(delta(S)) >= x(delta(S)) >= 2, since each routed path joining opposite sides crosses the cut at least once.

For each W_j write a_j for total load on edges internal to W_j, b_j for load between W_j and {u,v}. No edge joins distinct W_j. The cut W_j gives b_j>=2; summing singleton cuts at vertices of W_j gives 2a_j+b_j>=2|W_j|. Thus a_j+b_j >= |W_j|+b_j/2 >= |W_j|+1. Summing over j and ignoring the nonnegative load on uv gives the claimed bound.

**Equality rigidity.** If equality holds, the uv load is zero, each b_j=2, and every internal vertex has routed degree exactly two. For a metric tour expanded along shortest routes, y is an **integral connected spanning Eulerian multigraph**. If a W_j induces a path, equality forces all its internal path edges to have multiplicity one and its two boundary edges to attach at its two endpoints: every connected piece of the selected edges inside W_j has an even number of incident boundary-edge copies; since the total is two and the full multigraph is connected, there is exactly one such piece, containing every vertex of W_j. A connected spanning degree-two subgraph of an induced path must use all its internal edges once.

The lemma is a general lower bound; no claim is made that it is sharp for arbitrary G. It is not a new global TSP integrality-gap bound.

## Exact fractional optimum

Let x_1 be the first internal vertex of P_1 and y_2 the last internal vertex of P_2. Replace P_1 and P_2 by a single u-v path Q_0: traverse P_2 from u to y_2, the new cross edge y_2-x_1, then P_1 from x_1 to v. Its length is L_1+L_2-1. Together with P_3,...,P_k these are r=k-1 internally disjoint u-v paths of lengths >=2. Their union H is a spanning subgraph of G, and H plus the direct hub edge is a chorded multitheta.

The component-cut lemma applies to G with r=k-1 internal components, since |V|-2=m-k. Hence SEP(G)>=m-1.

For the upper bound construct the following rational point on the complete metric, using the r recombined paths Q_i. Put alpha=2/r on the first and last edge of each Q_i, weight one on all other edges of Q_i, and gamma=(r-2)/(r(r-1)) on each pair of first internal vertices of different Q_i and each pair of last internal vertices. Add coincident shortcut weights for length-two paths; all other variables are zero. Every vertex has x-degree two.

For a hub with t adjacent internal vertices across a cut, the hub spokes and same-hub shortcuts contribute F(t)=alpha*t+gamma*t*(r-t). This is concave, F(0)=0, F(1)=1, F(r)=2, so F(t)>=1 for 1<=t<=r. If both hubs have positive t, or either has t=r, the cut has weight at least two. If exactly one has 0<t<r, at least one interior unit edge crosses, giving weight at least two. If both have t=0, a nontrivial cut either crosses two interior unit edges on a path or, when hubs are opposite, at least one interior unit edge on each of r>=2 paths. This also covers length-two paths, whose first and last internal vertices coincide. Thus every cut is feasible.

All Q_i edges cost one in G and same-hub shortcuts cost at most two. The displayed point has cost at most

    (m-1)-2r + 2r*alpha + 2*r*(r-1)*gamma = m-1.

The lower bound forces equality. This proof does not require accepting the earlier chorded-multitheta theorem on trust.

## Exact integral optimum and parity obstruction

The union of all r recombined paths Q_i once is connected, spans every vertex and has degree r at both hubs, degree two elsewhere. If k is odd, r is even, so this is an Eulerian spanning multigraph of cost m-1 and shortcuts to a metric tour.

If k is even and any L_i=2, change one path component to a same-hub excursion at no cost: for i>=3, replace u-z-v by two copies of u-z; if i=1, replace the final edge x_1-v of Q_0 by u-x_1; if i=2, replace the initial edge u-y_2 of Q_0 by y_2-v. The other r-1>=2 recombined paths keep the graph connected and join the hubs. Both hub degrees become even, so TSP=m-1.

If k is even and every L_i>=3, adding the direct edge uv to all Q_i once gives an Eulerian spanning multigraph of cost m.

To exclude a tour of cost m-1 in the last case, expand such a metric tour to a connected Eulerian spanning multigraph y on G. Equality rigidity in the component-cut lemma forces uv to have zero load, each internal component to have boundary load exactly two, and every internal vertex to have degree exactly two. Each W_i for i>=3 induces a path whose endpoints can attach only to u and v respectively, so it contributes exactly one u-v path. The merged component W_1 union W_2 also induces a path, with endpoints the first internal vertex of P_2 and the last internal vertex of P_1. Because L_1,L_2>=3, those endpoints have only the respective hub attachments u and v. Thus it too contributes one u-v path. There are r=k-1 such paths; for even k, r is odd, contradicting the even degree of each hub in an Eulerian multigraph. Hence TSP>=m, proving the formula.

For even k and all L_i>=3, m>=3k>=12, so m/(m-1)<=12/11, with equality at k=4, all lengths three.

## Exact checks and adversarial boundary

Run:

    python3 -m scripts.m097_cross_end --max-vertices 10 --json
    python3 -m unittest discover -s tests -p 'test_m097_cross_end.py' -v
    python3 -m scripts.m097_cross_end_lp --max-vertices 10  # optional SciPy

The repository checker uses exact Fraction arithmetic for the rational LP witness, enumerates every nontrivial cut, reconstructs BFS metric distances, checks an explicit connected Eulerian multigraph and computes TSP independently by Held-Karp subset DP. It checks **166 labeled ordered length tuples** with 3<=k<=5, 2<=L_i<=5 and <=10 vertices (100 odd-k, 65 even-k with a length-two path, one even-k with all lengths >=3). The 8 adversarial tests include altered edge location, malformed inputs, the 12/11 sharp example, and a tampered fractional witness.

**Independent computational formulation, still same author:** a separate container script built graphs independently, optimized the *complete* symmetric subtour LP with SciPy HiGHS over all cuts, and ran an independent Held-Karp DP on the same 166 ordered tuples. Every optimum agreed with the theorem. The independently represented optional implementation is committed in `scripts/m097_cross_end_lp.py`; SciPy is not required by the base checker or repository tests. This remains exploratory author-side verification, not independent mathematical review.

**Failed stronger extension:** Moving the cross edge to join the **first** internal vertices of P_1 and P_2 breaks the formula. For k=3, L=(3,3,3), the cross-end graph has an eight-edge Hamiltonian cycle, but the first-first graph has **TSP=9 exactly**: each of the three second internal vertices has degree two and forces its edge to v in any Hamiltonian cycle, which would give v degree three, so no eight-edge Hamiltonian cycle exists. A nine-edge connected Eulerian spanning multigraph is obtained from all three original paths by deleting the two edges from u to the first internal vertices of P_1,P_2, and adding the cross edge and uv. A separately optimized subtour value is 17/2 (numerical HiGHS output, not an exact dual certificate). Thus the cross-end placement is essential. The general two-hub component-cut lemma gives only the lower bound eight for this modified graph; it is not asserted sharp there.

## Primary sources, limitations and next falsifier

- Held and Karp, *The Traveling-Salesman Problem and Minimum Spanning Trees*, Operations Research 18 (1970), https://doi.org/10.1287/opre.18.6.1138 — classical subtour-LP background.
- Sebő and Vygen, *Shorter Tours by Nicer Ears*, 2012, https://arxiv.org/abs/1201.1870 — graphic TSP and ear-structure context.
- Boyd, Sitters, van der Ster and Stougie, *The Traveling Salesman Problem on Cubic and Subcubic Graphs*, 2014, https://doi.org/10.1007/s10107-012-0620-1 — distinct restricted graphic-TSP bounds.
- Boyd and Legault, *Toward a 6/5 Bound for the Minimum Cost 2-Edge Connected Spanning Subgraph*, SIAM Journal on Discrete Mathematics (2017), https://doi.org/10.1137/16M1057486 — relevant 2EC LP context, not evidence of priority for this particular component-cut inequality.
- Cook, Hougardy and Petrich, *Extending Exact Integrality Gap Computations for the Metric TSP*, arXiv:2603.12995, first posted 2026-03-13, https://arxiv.org/abs/2603.12995 — contemporary global computational context, not an exact source for this family.
- Project-local [M097_MULTITHETA.md](M097_MULTITHETA.md), [M097_BLOCK_SUM.md](M097_BLOCK_SUM.md), and [draft chorded multitheta PR #231](https://github.com/Svyable/100/pull/231) — antecedents, none independently reviewed.

A targeted search did not locate this exact cross-end formula or the two-hub component-cut lemma. **Absence from a targeted search is not evidence of historical novelty.** The lower-bound lemma may be a known partition/degree inequality in graphic TSP. Specialist comparison with the literature on 2-edge-connected spanning subgraphs, graphic-TSP LP duals, and theta subdivisions is essential. A reviewer should attack the routing inequality, fractional cut case split, equality rigidity (especially length-two endpoints), and Eulerian construction independently. The next genuine falsifier is an explicit rational feasible point violating the m-1 bound, an Eulerian tour of length m-1 when k is even and all L_i>=3, or a shorter counterexample to the asserted first-first boundary.

**Workflow:** This packet is a candidate pending external mathematical and historical review, not an independently accepted theorem. Do not change data/solved.json, evidence states, coverage, benchmark outcomes or the separate Project 100 PR Landing task. Regenerate derived files and run full tests and exact-head CI before any mergeable PR; do not bypass checks or merge automatically.
