# M097 — same-hub cross-edge: exact graphic-metric TSP and subtour LP

**Date:** 2026-11-02 UTC. **Claim:** [#238](https://github.com/Svyable/100/issues/238). **Work ID:** X-M097-CROSS-SAME. **Scope SHA-256:** a45c367b8d2a08b894810c63ca97c29b7c6c0b6b16561c276cacf5adae1f2802.

**Status:** Author-derived all-orders restricted theorem **candidate**, with exact rational cuts/tours and a separately formulated numerical LP. Historical novelty and independent specialist mathematical acceptance **unestablished**. Not a global metric-TSP bound or a solution of the 4/3 conjecture.

## Exact statement — the first two paths are distinguished

For integers k≥3 and L₁,…,Lₖ≥2, form a simple unweighted graph with two hubs u,v, a direct edge uv, internally disjoint u-v paths Pᵢ of lengths Lᵢ, and exactly one additional edge joining the **first** internal vertices p₁,p₂ of P₁,P₂ (near u). There are no other edges. Put m=ΣLᵢ and n=m−k+2. Let SEP be the symmetric degree-two subtour LP on the complete shortest-path metric and TSP the shortest Hamiltonian tour.

**All-orders restricted theorem candidate:**

- SEP = m−1/2 if k=3 and L₁,L₂≥3; SEP = m−1 otherwise.
- TSP = m−1 if k is even, or min(L₁,L₂)=2, or k≥5 and some Lᵢ=2 for i≥3; TSP = m otherwise.

The maximum ratio in this graph class is **15/14**, attained at k=5, lengths (3,3,3,3,3). The ordered example (3,3,2) has SEP=15/2 and TSP=8; by contrast (2,3,3) has SEP=TSP=7. Sorting lengths before attaching the extra edge is not a valid symmetry.

## Lower bound: two-hub component cuts

For any feasible complete-metric subtour point x, route each metric edge along an arbitrary shortest path in G, obtaining nonnegative original-edge loads y. This preserves objective cost and cannot decrease cut loads. Let W=V\{u,v}, and let c be the number of connected components of G[W]. Let A be y-load on hub–W edges, B on edges inside W, and C on uv. Each component has cut load at least two, so A≥2c. The routed degree of every internal vertex is at least its x-degree two, so 2B+A≥2|W|. Consequently

\[
\operatorname{cost}(x)=A+B+C\ge |W|+A/2+C\ge |W|+c.
\]

The extra edge joins the first two internal components; hence c=k−1 and |W|=m−k, proving SEP≥m−1, and the same lower bound for TSP. This is an elementary specialization of the component-cut lemma also used in [cross-end draft #233](https://github.com/Svyable/100/pull/233), not a separately claimed general discovery.

## Exceptional k=3 lower bound

Assume k=3 and L₁,L₂≥3, allowing L₃=2. Let qᵢ be the last internal vertex of Pᵢ, adjacent to v. All three qᵢ are distinct and have **graph degree exactly two**. Every subtour variable x_ab≤1: the degree equations and the cut on {a,b} give 4−2x_ab≥2. Let z be total x-mass on pairs not present as graph edges, and zᵢ the nonedge mass incident to qᵢ. Degree two at qᵢ and the bound one on its other graph-edge variable imply x_(v,qᵢ)≥1−zᵢ. Summing, using degree two at v, yields Σzᵢ≥1. Each nonedge contributes to at most two zᵢ, so z≥1/2. All graph edges have metric cost one, all nonedges cost at least two, and Σx=n=m−1. Thus cost(x)≥n+z≥m−1/2.

For equality, put weight one on all edges of P₃ and on the suffix paths pᵢ…qᵢ of P₁,P₂; weight 1/2 on up₁,up₂,vq₁,vq₂,p₁p₂,q₁q₂; zero elsewhere. The last shortcut has metric cost two. Degrees are two and cost is m−1/2. For every cut separating u and v, P₃ contributes ≥1 and the two crossed-network u-v routes each contribute ≥1/2. If u,v lie on the same side and any P₃ vertex is opposite, P₃ contributes ≥2. Otherwise let a,b,c,d∈{0,1} indicate whether p₁,p₂,q₁,q₂ are opposite the hubs. The crossed network contributes at least

\[
\max(a,b)+\max(c,d)+|a-c|+|b-d|\ge2
\]

when any indicator is nonzero; if all are zero but an interior suffix vertex is opposite, two unit suffix edges cross. Hence every nontrivial cut is at least two. This proves the exceptional LP value for **all** path lengths in its scope, not just the computed examples.

## k≥4 LP construction: a fractional ear

Set h=k−2≥2. On the chorded subgraph comprising P₃,…,Pₖ and uv, place α=2/h on every hub spoke, weight one on each internal path edge, and γ=(h−2)/(h(h−1)) on every pair of first internal vertices and every pair of last internal vertices (add coincident contributions for length-two paths). Degrees equal two. If t first/last vertices lie opposite a hub, its spoke-plus-shortcut cut contribution is F(t)=αt+γt(h−t). This satisfies F(0)=0, F(h)=2, and F(t)≥1 for 1≤t≤h by concavity. The two hub contributions plus any crossed unit interior edges establish all subtour cuts: if both are positive, their sum is ≥2; if only one is positive, it is either 2 or there is an interior crossing; if both vanish, a nontrivial cut has at least two interior crossings (using h≥2 when hubs differ). This gives a feasible point of cost Σ_{i≥3}Lᵢ in the chorded metric.

**Ear-insertion lemma (proved here).** Let x be any subtour-feasible point on old vertices including v. Choose t_a∈[0,x_va] with Σt_a=1, possible since degree_x(v)=2. Introduce new vertices w₁,…,wᵣ in a unit-weight path, with an additional unit edge wᵣv. Replace t_a of each va by t_a on aw₁. Degrees remain two. For a cut with v on its selected side, let T be its old vertices on that side and t(T)=Σ_{a∈T}t_a. If all new vertices lie with v, the cut equals the old cut; if all lie opposite, it equals the old cut plus 2t(T). If the new path is split, let q≥1 count crossings on w₁…wᵣv: the cut equals the old cut plus q when w₁ is with v, or plus q−1+2t(T) otherwise. These are ≥2 whenever T is a proper nonempty old cut. When T contains every old vertex, the new path itself contributes ≥2 in each nontrivial case. Thus the new point is subtour-feasible.

Insert the crossed internal chain w₁=q₂,…,p₂,p₁,…,q₁=wᵣ and edge q₁v. The chain has L₁+L₂−3 edges. Since d(a,q₂)≤d(a,v)+1, the added metric cost is at most L₁+L₂−1. The resulting feasible point costs at most m−1, matching the component-cut lower bound. This construction does not rely on an LP solver verdict.


## Integral optimum: exact equality rigidity

Expand any metric Hamiltonian tour to a connected spanning Eulerian multigraph in G. At total cost m−1, equality in the component-cut bound forces (i) no uv traversal, (ii) every internal vertex has degree exactly two, and (iii) exactly two hub-boundary traversals per component of G[W]. An uncrossed path of length at least three must therefore be traversed once from u to v: doubling an endpoint edge would disconnect the remaining internal chain. An uncrossed length-two path u-w-v can instead use two copies of uw or two of wv.

If L₁,L₂≥3, the crossed component's induced internal graph is exactly the chain q₁,…,p₁,p₂,…,q₂. Its unique connected spanning degree-two traversal with two hub-boundary edges uses the entire chain once and exits **twice at v**. Thus the crossed component contributes zero degree at u and two at v. For odd k, the number k−2 of uncrossed components is odd. To make u's degree even, at least one length-two uncrossed path must be traversed as a doubled pendant edge; to connect u and v, at least one other uncrossed component must remain a u-v path. This is impossible for k=3, and impossible if every uncrossed path has length at least three. Therefore in precisely these odd-k cases TSP≥m.

The upper bounds are explicit connected Eulerian traversals, which shortcut to Hamiltonian tours without increasing cost. Use the crossed chain with both exits to v, a cycle of length L₁+L₂−1, and each remaining u-v path once. For even k this is Eulerian and costs m−1. For odd k, add uv to obtain cost m. If an odd-k crossed path has length two, exit the crossed chain through its sole internal vertex to u instead of v: it becomes one u-v path, giving even hub degrees and cost m−1. If k≥5 is odd and an uncrossed path has length two, replace that u-w-v path by two copies of uw; the remaining k−3≥2 uncrossed paths keep the graph connected and both hub degrees even, still at cost m−1. These exhaust the cases in the statement.

The only nonunit ratios are m/(m−1/2) for k=3 with L₁,L₂≥3 (m≥8), and m/(m−1) for odd k≥5 with all lengths at least three (m≥15). The maximum is 15/14 at five length-three paths.

## Reproduction and adversarial controls

Run these from the repository root:

    python3 -m scripts.m097_cross_same --max-vertices 12 --max-k 7 --max-length 6 --json
    python3 -m unittest discover -s tests -p 'test_m097_cross_same.py' -v
    # Optional SciPy/NumPy independent graph and LP formulation:
    python3 -m scripts.m097_cross_same_lp --max-vertices 10 --json
    python3 scripts/regen.py --check --fast
    python3 scripts/regen.py --check
    python3 -m unittest discover -s tests

The primary checker builds exact rational primal points, exhaustively verifies degree and all subtour cuts, constructs an explicit connected Eulerian multigraph and metric-shortcuts it, and separately runs Hamiltonian subset DP. **371 ordered cases** up to 12 vertices, k≤7, lengths≤6 passed author-side exact checks. The independently implemented adjacency-list/SciPy HiGHS full-cut LP and separate subset DP matched **112 ordered cases** up to 10 vertices. Distinct implementations by the same author are **not** independent mathematical acceptance.

**Failed stronger avenues and why:** An initial search sorted all lengths, incorrectly treating the first two paths as interchangeable with the rest; this missed the (3,3,2) exception. The extrapolation SEP=m−1 universally fails at (3,3,2), where SEP=15/2. The assertion that any length-two path forces TSP=m−1 also fails there: TSP=8=m. A naive Eulerian construction doubling the sole uncrossed length-two path when k=3 is disconnected, so it cannot certify m−1. The component-cut lower bound alone misses the half-unit LP obstruction; the degree-two-neighbor nonedge-mass inequality supplies it.

**Sources and novelty boundary:** Held–Karp (1970) for the classical subtour LP; [Mnich–Mömke, arXiv:1312.2502](https://arxiv.org/abs/1312.2502) on 1,2-TSP and support structure; [Cook–Hougardy–Petrich, arXiv:2603.12995](https://arxiv.org/abs/2603.12995) (March 2026, updated September 2026) on exact small-instance integrality gaps. The [chorded class PR #231](https://github.com/Svyable/100/pull/231) has no cross edge; [cross-end PR #233](https://github.com/Svyable/100/pull/233) joins a first and a **last** internal vertex, not two first vertices. The shared two-hub lower bound and chorded primal are reused with attribution, not represented as new standalone discoveries. A targeted search has not established historical priority; a specialist literature audit remains necessary.

**Next falsifier:** An independently constructed feasible rational point below the stated SEP for an ordered k=3 case, a connected Eulerian m−1 tour in an excluded odd-k case, or a cut violating the ear-insertion lemma. External review should audit the all-orders equality rigidity, the length-two connectedness exception, the fractional ear cut cases and possible earlier literature. No solved/evidence status, accepted-independent outcome, benchmark trial or coverage slot is changed.
