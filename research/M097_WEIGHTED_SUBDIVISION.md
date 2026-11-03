# M097 — arbitrary weighted subdivision TSP and the limit of subdivision-based LP bounds

**Claim:** [#287](https://github.com/Svyable/100/issues/287). **Work item:** `X-M097-WEIGHTED-SUBDIVISION`. **Scope SHA-256:** 43428220042675fcd9e9c4811b28c098a254c3912344a664a46a1ea1b9291e1d. **Date:** 2026-11-02 (America/Chicago).

**Evidence:** Author-derived all-orders restricted theorem candidates using only elementary Eulerian graph arguments and the established *metric subtour parsimonious property*. No unproved conjecture is assumed. All numerical tests are falsification checks, **not** evidence that finite experiments imply the formulas for all orders. No independent mathematical review, Lean formalization of these statements, or historical novelty acceptance. The 4/3 conjecture is not solved.

## Theorem A: exact weighted parity–MST formula

Let H=(V,E) be a connected loopless undirected multigraph on at least two core vertices. Every indexed core edge e=uv is replaced by an internally vertex-disjoint path P_e of **at least two edges**, each with a strictly positive real weight. Write W_e for the sum of weights along P_e, and a_e for its **largest individual edge weight**. Let W=∑_e W_e. No equality among weights, symmetry, or degree bound is assumed.

Let ℰ(H) be the set of **all even-degree core edge subsets**, including the empty set. For F∈ℰ(H), contract each connected component of (V,F), **including isolated core vertices**. Let τ(F) be the weight of a minimum spanning tree in the resulting connected multigraph, where each retained indexed core edge e outside F has weight a_e; loops created by contraction are ignored. Define τ(F)=0 if F is connected and spanning.

**Exact identity:**

\[
\boxed{\operatorname{TSP}(G,\operatorname{dist}_w)
=W+\min_{F\in\mathcal{E}(H)}
\bigg\{\sum_{e\notin F}(W_e-2a_e)+2\tau(F)\bigg\}.}\tag{1}
\]

Here TSP means the shortest **metric Hamiltonian cycle through every subdivided vertex**, not just the original core vertices. If there are two total expanded vertices, interpret the tour as the two-way closed walk, of length twice their mutual distance.

**Consequences.** For fixed core H, TSP depends on each replacement path *only* through the two numbers **(total weight W_e, maximum edge weight a_e)**; permuting its edge weights or replacing it with any other positive-weight path having the same two statistics leaves the exact optimum unchanged, despite changing intermediate distances and possibly the number of vertices. The cycle-space dimension is r=|E|−|V|+1, so (1) has precisely 2^r core states. Every state's τ(F) is an ordinary minimum spanning tree and supplies an explicit optimum witness. This is an exact **2^r·poly(input size)** algorithm for these weighted subdivisions, not a polynomial algorithm for arbitrary unbounded-rank graph TSP. General parameterized TSP methods and even-cover constructions are classical; novelty is not established.

### Proof of the lower bound

First observe that the minimum metric Hamiltonian tour cost equals the minimum cost of a **connected spanning Eulerian edge-multigraph on G**. Expanding each tour edge along a shortest path gives such a multigraph with the same cost; conversely an Eulerian closed walk can be shortcut at repeat visits by the triangle inequality, yielding a Hamiltonian metric tour no more expensive. Thus both minima are equal.

Consider any connected spanning Eulerian edge-multigraph M on G. At every degree-two **internal** vertex of P_e, the two adjacent original-edge multiplicities have the same parity. Therefore all edges of P_e have a common parity. Let F be the core paths of **odd** parity. At each core vertex, the Eulerian parity condition implies deg_F(v) is even, so F∈ℰ(H).

An odd-parity path uses each edge at least once and costs ≥W_e. An even-parity path uses each edge either zero or at least twice. It cannot omit **two or more** distinct edges: the nonempty internal segment between two missing edges would be disconnected from the core (if the omissions are adjacent, the internal vertex between them would be isolated), contradicting the connected spanning requirement. Thus an even-parity path either:

* is **through** (no edge omitted), costs at least 2W_e; or
* is **broken** (exactly one edge omitted), costs at least 2(W_e−a_e), since the omitted edge's weight is at most a_e.

For every even-parity path first charge its broken-path baseline 2(W_e−a_e). Switching it to through costs at least another 2a_e. The odd paths connect precisely the components of (V,F). Broken even paths cannot connect distinct core components because they have a missing edge. Hence the set of through even paths must connect all contracted components; their total a-weight is at least τ(F). Combining these charges,

\[
\operatorname{cost}(M)\ge
\sum_{e\in F}W_e+
\sum_{e\notin F}2(W_e-a_e)+2\tau(F)
=W+\sum_{e\notin F}(W_e-2a_e)+2\tau(F).
\]

Minimizing over the actual parity set F establishes the claimed lower bound.

### Proof of the matching upper bound

Fix any F∈ℰ(H). Take a minimum spanning tree T_F of H/F for the weights a_e. Construct an original-edge multigraph:

* traverse every edge of each odd path P_e, e∈F, **once**;
* traverse every edge of each even path e in T_F **twice**;
* on every remaining even path, omit **one maximum-weight edge** and traverse all its other edges **twice**.

All internal vertices are present (because each P_e has at least two edges), and have even degree. At every core vertex the odd incidences form F and hence sum to an even number; all other contributions are even. The support is connected because the odd paths connect their F-components and the through doubled paths connect these components along T_F. Every internal vertex in a broken path is attached to at least one of its two core endpoints. Therefore this is a connected spanning Eulerian multigraph, with **exactly** the displayed cost for F. Shortcut its Eulerian walk. Taking the best F yields the matching upper bound and proves (1) unconditionally.

**Specializations / sanity checks:** If every individual edge has unit weight and P_e has L_e≥2 edges, then W_e=L_e, a_e=1, τ(F)=c(F)−1. Equation (1) becomes exactly the unit-weight [M097 subdivision-core formula](M097_SUBDIVISION_CORE.md). If H is a tree, ℰ(H) contains only ∅ and the optimum is exactly 2W. If H is a single core cycle (hence G a weighted cycle), ℰ(H)={∅,E} and (1) gives \(\min\{W,2(W-\max_{e,j}w_{e,j})\}\). An edge of weight 100 on an otherwise unit-weight cycle can therefore be skipped at optimum: blindly replacing total weights in the unweighted formula is **false**.

## Theorem B: weighted full subdivisions are universal for the metric subtour-LP integrality gap

For any finite positive symmetric metric d on n≥3 points, construct the weighted graph \(G_\epsilon\) by taking the complete graph K_n with original edge weights d(i,j) and replacing each edge ij (say i<j) by a new two-edge path \(i-z_{ij}-j\), with positive weights **ε** and **d(i,j)** respectively.

Then G_ε is simple, connected, bipartite, **2-degenerate**, and has girth at least six. Let SEP mean the symmetric metric subtour-elimination LP with degree exactly two, nonnegative variables and cuts at least two. **For every original metric d,**

\[
\boxed{\lim_{\epsilon\downarrow0}
\frac{\operatorname{TSP}(G_\epsilon)}
     {\operatorname{SEP}(G_\epsilon)}
=
\frac{\operatorname{TSP}(d)}{\operatorname{SEP}(d)}.}\tag{2}
\]

Consequently

\[
\boxed{
\sup_{\substack{G=\text{positive-weighted}\\
\text{one-subdivision of }K_n,\ n\ge3}}
\frac{\operatorname{TSP}(G)}{\operatorname{SEP}(G)}
=
\sup_{\text{finite positive symmetric metrics }d}
\frac{\operatorname{TSP}(d)}{\operatorname{SEP}(d)}.}\tag{3}
\]

The restriction to these weighted bipartite two-degenerate girth-six graphs **does not lower the worst-case subtour gap at all** (supremum, not necessarily attained). In particular, extending the unit-weight 4/3 theorem of [#285](https://github.com/Svyable/100/pull/285) to *all arbitrary positive edge weights* on this graph class would prove the entire open metric-TSP 4/3 conjecture. This is a **barrier/equivalence**, **not** an instance with ratio exceeding 4/3 and **not** a proof of that conjecture.

### Proof, with no informal continuity shortcut

**Lemma (zero-distance twin invariance).** Take any finite metric d on at least three points, and adjoin a twin v′ of a point v with distance zero from v and distances d(v,u) to every other original point. Then both the metric Hamiltonian tour optimum and the symmetric subtour LP optimum are **unchanged**. This holds after adjoining any finite number of such twins.

*Tour.* Insert v′ immediately after v in any original Hamiltonian tour, without increasing its length. Conversely project any augmented tour to the original points, remove repeated names and shortcut; the triangle inequality prevents the projected Hamiltonian tour from costing more. The two inequalities prove equality.

*LP upper bound, explicitly.* Take any feasible original subtour point x. Set x′_{vv′}=1, split each original incident value equally as x′_{vu}=x′_{v′u}=x_{vu}/2, and retain every other value. All augmented degrees equal two. A cut containing both twins or neither inherits an original cut with load at least two. A cut separating v from v′ has load **2 plus the sum of non-twin edges crossing the partition of the other vertices**, hence at least two. Thus x′ is subtour-feasible at exactly the same objective cost (the twin edge costs zero). Iterating this construction gives the upper bound for multiple twins.

*LP lower bound, using one established input.* Project an arbitrary augmented feasible point y by aggregating all edges between each pair of original-vertex clone groups, discarding zero-cost edges inside a group. The projected z has nonnegative coordinates and **z(δ(S))≥2** for every proper nonempty original shore S, because this is exactly the augmented cut of the union of clone groups. Its objective equals the augmented objective. It need not have exact degree two, so here we use the classical **parsimonious property** of the subtour cut LP in a metric: dropping the degree equalities does not improve its minimum objective (Goemans–Bertsimas 1993). Therefore original SEP ≤ cost(z) = cost(y). Combining with the explicit extension proves LP invariance. The named parsimonious property is a proven theorem, not a conjecture; we do **not** independently re-prove it here.

As ε→0, the weighted graph \(G_\epsilon\) becomes a **zero-distance clone** of the original metric: every z_ij has distance zero from i, while traversing its other edge costs d(i,j); the triangle inequalities ensure that the induced distances between original points remain d. The clone lemma gives exact equality of both optima at ε=0.

Every pairwise shortest-path distance in \(G_\epsilon\) is a minimum over finitely many simple paths, each with an edge-sum continuous in ε, hence converges to its ε=0 value. On a fixed expanded N-point vertex set, the Hamiltonian optimum is a minimum over finitely many continuous tour costs, hence continuous. The subtour LP feasible polytope is nonempty and **compact**, independently of edge costs, because degrees are two and nonnegative variables imply every coordinate is at most two. Its optimal linear objective is therefore continuous in the distance vector. Equivalently, if all distances move by at most δ, both TSP and SEP values move by at most Nδ because each tour uses N edges and every subtour-feasible point has sum of edge variables N.

Thus TSP(G_ε)→TSP(d) and SEP(G_ε)→SEP(d)>0, proving ratio convergence in (2). For (3), the left-hand class is a subset of all finite positive metric instances, giving ≤. Conversely every finite positive metric d supplies a sequence from that left-hand class whose ratio tends to d's ratio, giving ≥ after taking suprema. QED.

### Quantitative epsilon bound and integer-weight version

Let μ be the minimum positive off-diagonal original distance, D the maximum, N=n+binom(n,2), and K=N(N−1). Every original instance satisfies the explicit **ratio-error certificate**

\[
\left|\frac{\operatorname{TSP}(G_\epsilon)}{\operatorname{SEP}(G_\epsilon)}
-\frac{\operatorname{TSP}(d)}{\operatorname{SEP}(d)}\right|
\le \frac{KD}{n\mu^2}\,\epsilon.\tag{4}
\]

Thus any rational tolerance δ>0 can be achieved by choosing a rational \(0<\epsilon\le\delta n\mu^2/(KD)\). For rational metric inputs the choice has polynomial binary encoding length. Scale all rational edge weights by a common denominator to make them **positive integers** without changing the ratio. Rational metric instances are dense among real metric instances: rationally approximate complete-graph edge costs and take shortest-path closure. Consequently the supremum equality in (3) holds even over **positive-integer-weighted** bipartite one-subdivisions.

**Proof.** A zero-clone shortest path can be taken simple, so it uses at most N−1 edges. Increasing the zero edges to ε therefore changes any shortest-path distance by between zero and (N−1)ε. Every Hamiltonian cycle has N metric edges, and every symmetric-subtour feasible point has total x-weight N by the degree constraints. Both objective optima therefore increase from their zero-clone values by amounts between zero and Kε. If A=TSP(d), B=SEP(d), and Aε,Bε are their subdivided values, then A≤Aε≤A+Kε and B≤Bε≤B+Kε. Because A≥B>0, elementary fraction subtraction gives \(|Aε/Bε-A/B|\le (A/B)Kε/B\). Also A≤nD (any tour) and B≥nμ (every subtour point has x-sum n), giving A/B≤D/μ and proving (4). Neither the unknown optimum A nor B is needed to select ε.

**Why the graph class really is sparse:** In each one-subdivision of a simple K_n, originals have no direct edges, every new subdivision vertex has degree exactly two and joins two originals, and there are no 4-cycles because original pairs have a unique subdividing vertex. Every cycle has at least six edges; every induced subgraph containing a subdivider has a vertex of degree at most two, and any induced subgraph without a subdivider has no edges. This proves bipartiteness, girth≥6 and 2-degeneracy, rather than assuming them.

## Verifiers and deliberately false extensions

Run:

    python3 scripts/m097_weighted_subdivision.py --check
    python3 -m unittest discover -s tests -p 'test_m097_weighted_subdivision.py' -v
    python3 scripts/regen.py --check

The new independent-in-code checks use: a cycle-space basis of the indexed multigraph rather than an unrestricted core-edge mask; exact fractional Kruskal MSTs on component contractions; a literal edge-copy expansion and an actual Hierholzer Eulerian walk; and a **separately programmed all-pairs shortest-path plus Hamiltonian subset DP** on the expanded graph. Small rational subtour LP instances use a separate exact rational simplex with independently replayed primal/dual optimality certificates. Negative tests cover path-length-one inputs, disconnected cores, zero/negative weights, false certificate cost, bridges, parallel edges, articulations, and the failure of naive unweighted cost substitution.

The proof of Theorem A does not rely on the finite tests; Theorem B relies on the **established parsimonious property**, the explicit twin construction, cut projection and elementary continuity. A Lean kernel execution for these full statements has **not** been performed. Neither theorem says that arbitrary weighted full subdivisions satisfy 4/3.

## Literature and historical novelty

References consulted 2026-11-02 (America/Chicago):

- [Goemans–Bertsimas, *Survivable Networks, Linear Programming Relaxations and the Parsimonious Property* (1993)](https://dspace.mit.edu/entities/publication/0c44288b-5f0c-4c32-8722-3f6fe47817c0): the metric cut-LP parsimonious property, central to Theorem B, **is classical**.
- [Bertsimas–Teo, *The parsimonious property of cut covering problems and its applications* (1997)](https://doi.org/10.1016/S0167-6377(97)00032-1): generalization of the same classical method.
- [Matthias Walter, *The Graphical Traveling Salesperson Problem has no Integer Programming Formulation in the Original Space* (2021)](https://arxiv.org/abs/2106.10097): standard definition of weighted graphical TSP as minimum-cost connected spanning Eulerian multigraph.
- [Blažej et al., *Parameterized Complexity of Directed Traveling Salesman Problem* (ISAAC 2025)](https://arxiv.org/abs/2506.22127): feedback-edge-number parameterization is a known algorithmic direction, not claimed as new here.
- [Cook–Hougardy–Petrich, *Extending Exact Integrality Gap Computations for the Metric TSP* (2026)](https://arxiv.org/abs/2603.12995): contemporary evidence and still-open general integrality-gap context.
- Project 100: [M097 unit-weight subdivision identity](M097_SUBDIVISION_CORE.md) and [unit-weight four-thirds restricted theorem candidate](M097_SUBDIVIDED_FOURTHIRDS.md).

The exact parity–MST compression may be an instance of classical even-cover/connected-Eulerian structure. The zero-clone technique and gap universality may be folklore or follow implicitly from parsimonious-property literature. **No claim of first historical discovery is made.** The deliverable is a precise full proof, a boundary showing why an apparently natural stronger theorem is as hard as the open general conjecture, and executable falsifiers. Independent specialist novelty and proof reviews remain necessary; no project status is promoted.
