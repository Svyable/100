# M074 — a saturated-shadow obstruction across the (3r,r) frontier

**Research candidate · 2026-11-01.** A self-contained conditional structural lemma for directed-triangle-free orientations. The derivation is written below and independently audited by `scripts/ch_saturated_shadow.py` and `tests/test_ch_saturated_shadow.py`. **External priority, originality, and specialist mathematical review are not established.** The lemma does **not** solve Caccetta–Häggkvist for any new order; the full (27,9) irregular branch remains open in this repository.

## Exact statement

Let `r >= 3` and let `D` be a loopless **oriented** graph on `3r` vertices, with **every outdegree exactly `r`**, with **no directed 3-cycle**, and with **maximum indegree at most `r+1`**. Fix a vertex `v` of indegree `r+1`. Let

- `A = N+(v)`, of size `r`;
- `B = N-(v)`, of size `r+1`;
- `C = V minus ({v} ∪ A ∪ B)`, of size `r−2`;
- `X = {a∈A : d+_A(a)=2}`, and `t=|X|`.

**Saturated-shadow theorem.** For each `s∈{1,2,3}`, if `r >= 4s+5`, then

`|X| <= r−s−1.`

There is an **additional strict improvement at `(r,s)=(8,1)`**, using the known six-vertex lemma. Thus the first exclusions for `s=1,2,3` occur respectively at **`r=8,13,17`**. Equivalently, at these thresholds an indegree-`r+1` root cannot have at least `r−1`, `r−2`, or `r−3` internally degree-two outneighbors.

This is a *conditional* theorem. In particular, for `r>9` the needed ambient maximum-indegree bound is **not** claimed to follow from earlier nine-vertex lemmas.

## Proof: the shadow cut

Suppose `t>=r−s`, and put `h=r−t<=s<=3`. There are no `A→B` arcs (such an arc closes `v→A→B→v`) and no `A→v` arcs (digons are forbidden). A vertex `x∈X` therefore sends its two internal arcs into `A` and **all** its other `r−2` outgoing arcs into `C`. In particular, `x→c` for every `c∈C` and every `x∈X`.

Any `y∈A minus X` has internal outdegree at least three: every A-vertex needs at least two internal outneighbors, and `y` is not in `X`. At most `h−1<=2` of these outneighbors belong to `A minus X`. Consequently `y→x` for some `x∈X`. If `c→y` for some `c∈C`, then `c→y→x→c` is a directed triangle. Thus no such arc exists. Since also no `C→X` arc is possible (it would be a digon), we have the exact *shadow* restriction

`e(C,A)=0.`                                                            (1)

Every `c∈C` already receives at least `t>=r−s` arcs from `X`. The global indegree ceiling `r+1` implies `d−_C(c)<=s+1`. Hence

`e(C,C)<= (s+1)(r−2).`                                                (2)

All `r−2` vertices in `C` have outdegree `r`, and none points to `v`. Equations (1)–(2) force

`S := e(C,B) >= r(r−2) − (s+1)(r−2) = (r−s−1)(r−2).`                 (3)

For each `b∈B`, put `k_b = d−_C(b)`. Let `P={b∈B:k_b>0}`. For a vertex `b∈P`, an arc `b→x` with `x∈X` would close `x→c→b→x` using one of its C-predecessors. So `b` sends at most `h<=s` arcs to `A`. It sends one arc to `v` and at most `(r−2)−k_b` arcs to `C` (orientation forbids the reverse of each `C→b` arc). Its outdegree `r` yields

`d+_B(b) >= r−1−s−[(r−2)−k_b] = k_b−(s−1).`

Summing only over `P`, and noting that `|P|<=r+1`, gives

`e(B,B) >= S−(s−1)|P| >= (r−s−1)(r−2)−(s−1)(r+1).`              (4)

But `D[B]` is oriented on `r+1` vertices, so

`e(B,B) <= r(r+1)/2.`                                                  (5)

Subtracting twice the right side of (5) from twice the last lower bound in (4) gives the integer polynomial

`Q(r,s) = r² − (4s+5)r + 2(s+3).`                                      (6)

If `r>=4s+5`, then `Q(r,s)>=2(s+3)>0` (the quadratic is increasing on this range). So (4) exceeds (5), contradiction.

**The exceptional six-vertex improvement.** Set `r=8,s=1`. Then `|C|=6` and each C-vertex has internal indegree at most two. The generic bound `e(C,C)<=12` is **not attainable**: equality would force every vertex of `D[C]` to have internal indegree exactly two. Reversing all arcs would give a directed-triangle-free oriented graph on six vertices of **minimum outdegree two**, excluded by the independently proved [six-vertex lemma](M074_ELEMENTARY_18.md). Hence `e(C,C)<=11`. Equations (1) and (3) now force `e(C,B)>=8*6−11=37`. For every positive-`k_b` B-vertex, at most one A-target is allowed, so `d+_B(b)>=k_b` and `e(B,B)>=37`, but `|B|=9` gives `e(B,B)<=36`. Contradiction.

This extra argument proves the `r=8,s=1` case as well. **QED.**

### Why the exact assumptions matter

The proof uses **all** of: outregularity, orientation/no digons, absence of directed 3-cycles, a root of indegree precisely `r+1`, and an ambient indegree ceiling of `r+1`. It does not follow from an arbitrary average degree condition. The threshold is the strict boundary of this *particular count*, not an optimality or sharpness theorem for graphs.

At `r=4s+4`, the **generic** count does **not** contradict (5): the excess in (6) is `2−2s<=0`. The only improvement asserted here is the proved six-vertex exception `(8,1)`; for `s=2,3` the generic near misses remain. Integer consistency below a threshold is not a counterexample graph.

## Consequence at (24,8): an alternate elimination of the final local profile

The existing [complete finite (24,8) research candidate](../proofs/M074_IRREGULAR_24.md) reduces an indegree-nine root to two internal A-outdegree profiles after exact integer cut checks. An elementary triangle obstruction excludes `(2^6,3,6)`, leaving `(2^7,7)`, a profile with **seven** saturated degree-two outneighbors.

The exceptional `(r,s)=(8,1)` theorem above directly excludes **that remaining profile**, using only the earlier six-vertex lemma and the root indegree-nine ceiling. This gives an alternate final step to the existing global high/low-degree contradiction. It does **not** independently verify the preceding 19×5005 profile classification, establish priority over the earlier reported computational finite exclusion, or prove any larger case.

## Consequence at (27,9): seven saturated low vertices

Here the hypotheses are applicable to any hypothetical directed-triangle-free orientation on 27 vertices with outdegree exactly nine: the nine-vertex local lemma rules out indegree eleven or more. The in/out-regular case is already excluded [in the previous note](../proofs/M074_27_REGULAR.md), so a hypothetical counterexample must have an indegree-ten root `v`.

The `s=1,r=9` case gives **at most seven** vertices of internal outdegree two in `A=N+(v)`. If there are exactly seven, call them `X`, and let `m=e(A,A)`. The argument above gives `e(C,A)=0`. Each `c∈C` receives seven arcs from `X`, so its internal indegree in `C` is at most three. The separately checked [seven-vertex sharp cap](../proofs/M074_SEVEN_VERTEX_CAP.md) gives `e(C,C)<=16`, improving the generic bound of 21. Thus

`e(C,B) = 7*9−e(C,C) >=47.`

Each `b∈B` receives at most seven C-arcs; at least seven of the ten B-vertices therefore receive some. **At most three** have no C-predecessor. Such a predecessor prevents `b→x` for every `x∈X`. Furthermore `C→x` is forbidden, `v→x`, and the nine-vertex lemma bounds `d−_A(x)<=4`. Therefore

`d−_D(x) <= 1+4+0+3 = 8` for **all seven distinct** `x∈X`.

There is also a nontrivial induced low-degree subgraph. The other two A-vertices, `Y=A minus X`, have internal outdegrees totaling `m−14`. Each has at most one outneighbor in `Y`, hence together they send at least `m−16` arcs into `X`. Orientation then gives `e(X,Y)<=14−(m−16)=30−m`; the seven vertices of `X` each have two A-outneighbors, so

`e(X,X)=14−e(X,Y)>=m−16>=4` (since both Y-vertices have internal outdegree at least three and hence `m>=20`).

**Conditional corollary.** A hypothetical `(27,9)` counterexample cannot have eight or nine saturated neighbors at an indegree-ten root. If a root has seven, these seven are all globally low-indegree (at most eight) and induce at least `m−16>=4` directed arcs. This does **not** eliminate profiles with zero through seven saturated neighbors, nor does it establish a new finite (27,9) theorem.

## Audit, controls and originality boundary

Run:

```sh
python3 scripts/ch_saturated_shadow.py --check
python3 -m unittest discover -s tests -p 'test_ch_saturated_shadow.py' -v
```

The checker recomputes both sides of the B-capacity inequality using independent integer expressions, verifies the first strict thresholds (8, 13, 17), the exceptional six-vertex gain, and the one-step weaker negative controls, checks the seven-neighbor `(27,9)` budget, and validates the independently existing nine-vertex C3-free local example. It does **not** enumerate 27-vertex digraphs or check novelty.

Prior-art starting points: [Hladký–Král'–Norin's directed-triangle threshold](https://arxiv.org/abs/0908.2791), [Razborov's forbidden-subgraph analysis](https://arxiv.org/abs/math/0604317), and [independently reported finite exclusions](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md). A targeted public search did not establish that the saturated-shadow inequality is unpublished. Treat it as **new-to-this-repository, originality unverified**, and seek a graph-theory referee before claiming novelty. The main M074 status, Solved ledger, and all proof-obligation discharge gates remain untouched.
