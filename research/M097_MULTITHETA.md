# M097 — exact subtour LP and TSP on subdivided parallel-path graphs

**Claim:** [#187](https://github.com/Svyable/100/issues/187). **Work packet:** `X-M097-MULTITHETA`, scope SHA-256 `b188c14d987d1307f3d5d21815b83c486f38145f1865af15c799b04604aa1ba4`. **Date:** 2026-11-01. **Classification:** author-derived all-orders restricted proof candidate, checked computationally; historical novelty and independent specialist review **not established**. No unrestricted metric-TSP 4/3 conjecture claim.

## Exact statement

Let `k>=2` and integers `L_1,...,L_k>=2`. Form a simple unweighted graph `G` from `k` internally vertex-disjoint paths of lengths `L_i` between two common hubs `u,v`, with no other edges. Let `c_G(a,b)` be shortest-path distance. Put `m=sum L_i`, `ell=min L_i`. For the **symmetric subtour-elimination LP** on the complete graph (degree equations `x(delta(v))=2`, all nonempty proper-cut inequalities `x(delta(S))>=2`, and `x>=0`), the exact formula claimed is

    SEP(c_G) = m,
    TSP(c_G) = m + (k mod 2)*(ell-2).

The ratio is one for even `k`, and `1+(ell-2)/m` for odd `k`. For odd `k`, `m>=k*ell` gives ratio strictly below `1+1/k<=4/3`, approaching `4/3` for three equal paths of increasing length. The three-path graphic-TSP lower-bound family is **classical**; this note does not claim its discovery.

## All-orders proof candidate: LP lower bound

Given any feasible complete-metric subtour point `x`, route every edge of weight `x_ab` along a fixed shortest `a-b` path in `G`. Let `y_e` be the sum of weights routed over original graph edge `e`. The routing preserves cost: `sum_e y_e = sum_{a<b} c_G(a,b)x_ab`. Every path connecting vertices on opposite sides of a cut crosses that cut at least once, so `y(delta(S))>=x(delta(S))>=2`.

On a constituent path with `L` edges `e_1,...,e_L`, any two distinct edges `e_i,e_j` delimit a nonempty internal-vertex segment whose **entire graph boundary** is precisely those two edges. Hence `y(e_i)+y(e_j)>=2`. Summing all `L(L-1)/2` pair inequalities gives `(L-1)sum_i y(e_i)>=L(L-1)`, so `sum_i y(e_i)>=L`. The path-edge sets partition `E(G)`, giving `SEP(c_G)>=m`.

## Explicit rational LP point, including all subtour cuts

Let `p_i` be the first internal vertex of path `i` next to `u`, and `q_i` the last internal vertex next to `v`. They coincide when `L_i=2`. Set `alpha=2/k`, `gamma=(k-2)/(k(k-1))`. Assign weight `alpha` to every original edge incident to a hub, weight one to every other original path edge, and for every distinct pair of paths `i,j`, add `gamma` on complete-graph edge `p_i p_j` and another `gamma` on `q_i q_j`. Coincident shortcut edges **add** weights rather than overwrite. Every hub has degree `k alpha=2`; internal vertices have degree two because `(k-1)gamma=1-alpha`, including the length-two case with contributions from both hubs.

For an arbitrary cut, let `t_u,t_v` count how many of each hub's adjacent internal vertices lie opposite that hub. The contribution of one hub's spokes and shortcut clique is `F(t)=alpha*t+gamma*t*(k-t)`. Here `F(0)=0`, `F(1)=1`, `F(k)=2`, and `F(t)>=1` for `1<=t<=k` (the function is concave for `k>2`; for `k=2`, `F(t)=t`). If both `t_u,t_v` are positive, the cut already has weight at least two. If exactly one is positive and equals `k`, it contributes two. Otherwise a constituent path has terminal-neighbor memberships forcing at least one *interior* unit-edge crossing: when hubs lie together, a first/last neighbor is on opposite sides; when hubs are separated, some path's first and last neighbors lie on their respective hubs' sides. Together with `F(t)>=1` this gives two. If both counts vanish and hubs are separated, each of the `k>=2` paths has an interior crossing. If both vanish and hubs are together, any nontrivial cut contains an internal segment with at least two interior crossings. Thus **every** cut has weight at least two, including length-two paths.

The original edges cost `m-2k+2k alpha=m-2k+4`. Each shortcut costs exactly two through its hub, and the two shortcut cliques contribute `2k(k-1)gamma=2k-4`. Total cost is `m`; therefore `SEP(c_G)=m`.

## Integer tour optimum by Eulerian parity

A metric Hamiltonian tour expands to a closed spanning walk on `G` at equal cost; conversely a closed spanning walk shortcuts to a metric tour at no greater cost. Thus TSP equals the minimum length of a connected spanning Eulerian edge-multigraph on `G`.

At each internal degree-two vertex, its two path-edge multiplicities have the same parity. Hence each path is either **odd-mode** (every edge multiplicity odd, cost at least `L_i`) or **even-mode** (all multiplicities even). An even-mode path cannot have two zero-multiplicity edges, because internal vertices between them would be disconnected from the spanning walk. Therefore at least `L_i-1` edges are used at least twice, costing at least `2(L_i-1)=L_i+(L_i-2)`. Even degree at either hub forces an **even number of odd-mode paths**.

When `k` is even, using all paths once is a connected Eulerian spanning multigraph of cost `m`. When `k` is odd, at least one path is even-mode, giving lower bound `m+ell-2`. Equality is achieved by taking the other `k-1>=2` paths once and, on a shortest path, deleting one edge and doubling every other edge. The result is connected, spanning and Eulerian. This proves the stated integer formula.

## Reproduction, adversarial controls and failed leads

    python3 scripts/m097_multitheta.py --check
    python3 -m unittest discover -s tests -p 'test_m097_multitheta.py' -v
    # Optional, with NumPy and SciPy installed:
    python3 scripts/m097_multitheta_lp.py --check

The standard-library checker independently constructs shortest paths by BFS, the rational LP point, every degree and every proper cut, and an integer subset-DP tour optimum **without using the parity proof**. The default sweep covers all **63** nondecreasing tuples with `2<=k<=5`, `2<=L_i<=6`, and at most 11 vertices: seven have fractional gap, with maximum `7/6`. Twelve adversarial tests cover the `L_i=2` coincidence, even/odd parity, path permutations, invalid parameters, tampered spoke and shortcut weights and the wrong `TSP=m` shortcut.

A separately written SciPy HiGHS formulation, using a different edge/cut construction, was run for all 63 tuples. Every proposed optimum was reconstructed into exact rational primal/dual vectors, checked against all inequalities and nonnegative reduced costs, and matched `SEP=m`. This is **author-side cross-checking, not independent mathematical review**. SciPy is optional and not required by repository CI.

Negative leads: the nine-vertex theta `(3,3,4)` has ratio `11/10`, below the eight-vertex `(3,3,3)` ratio `10/9`; adding vertices does not automatically increase the gap. A sampled nine-vertex diameter-four graph with a bridge had ratio `22/21`, defeating a naive extension of the eight-vertex diameter-four integral observation, but bridge attachments make it a weak structural lead. **No exhaustive nine-vertex census** was attempted.

## Prior art and next falsifier

- Hougardy, [*On the Integrality Ratio of the Subtour LP for Euclidean TSP*](https://arxiv.org/abs/1402.5904) (2014): discusses the classical graphic-metric constructions approaching `4/3`.
- Qian, Schalekamp, Williamson and van Zuylen, [*On the Integrality Gap of the Subtour LP for the 1,2-TSP*](https://arxiv.org/abs/1107.1630) (2015): a different restricted metric class, including exact small-instance results.
- Cook, Hougardy and Petrich, [*Extending Exact Integrality Gap Computations for the Metric TSP*](https://arxiv.org/abs/2603.12995) (2026): recent small-dimensional general-metric baseline, not audited for whether it implies this all-orders formula.
- [Prior M097 eight-vertex graphic-metric census](M097_GRAPH8.md), merged PR #176: a finite classification, not the present all-orders family theorem.

A targeted literature search did not locate this **precise all-`k`, all-length formula**, but that is **not evidence of historical novelty**. The three-path lower-bound construction is known. Next falsifiers: specialist search for subdivided dipoles/multitheta TSP formulas; a separately authored audit of the cut case split and Eulerian parity argument; and a second implementation of the rational certificate for uneven, larger path lengths. No `data/solved.json` or problem-status change is warranted.
