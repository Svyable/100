# M074: a sharper necessary condition for the (24,8) irregular branch

**Status:** internal elementary consequence and independently enumerable degree-profile pruning, not an accepted new theorem, not a proof of the full (24,8) case, not a new bound for the Caccetta–Häggkvist conjecture. Written 2026-10-31. The full finite (24,8) case is already computationally excluded in external work; the purpose of this note is a shorter, auditable **local structural reduction**.

**Prerequisites:** [the existing eight-vertex local lemma and regular-case proof](../M074_ELEMENTARY_24_REGULAR.md) and [the saturated-pivot argument](../M074_ELEMENTARY_18.md). They establish, among other things, that every directed-triangle-free oriented graph on eight vertices with minimum outdegree two has indegree at most three, at most 21 arcs, and each vertex of indegree three has outdegree exactly two.

## A four-neighbor strengthening

**Proposition (conditional).** Suppose a directed-triangle-free oriented graph on 24 vertices has outdegree exactly eight at every vertex. If a vertex `v` has indegree nine, **at least four distinct outneighbors of `v` have indegree at most seven in the ambient graph**.

This strengthens the previously recorded necessary condition of *at least one* low-indegree outneighbor, but does not contradict the existence of a hypothetical irregular candidate by itself.

**Proof.** Put `A=N⁺(v)`, `B=N⁻(v)`, and `C` equal to the nonneighbors of `v`. They have sizes 8, 9, and 6. No arc goes `A→B` (a directed triangle) or `A→v` (a digon). Every `a∈A` must therefore send at least two of its eight arcs into `A`. Thus `H=D[A]` is an eight-vertex directed-triangle-free oriented graph with minimum internal outdegree at least two.

Let `m=e(H)`, and let `t` be the number of vertices of `H` with internal outdegree exactly two. Every other vertex sends at least three internal arcs, so

```
m >= 2t + 3(8-t) = 24-t,  hence t >= 24-m.
```

The eight-vertex lemma gives indegree at most three in `H`, and any internal indegree-three vertex must have outdegree two. At most `t` vertices can therefore have indegree three; the rest have indegree at most two. Consequently

```
m <= 3t + 2(8-t) = 16+t,  hence t >= m-16.
```

Adding the two inequalities gives `2t >= 8`, hence **`t >= 4`**. This does not depend on enumerating the 24-vertex digraph.

The previous cross-cut argument gives an upper bound of nine on **every** ambient indegree: if any vertex had indegree at least ten, its eight outneighbors would have internal minimum outdegree three, contradicting the eight-vertex lemma. Therefore
`e(A,C) >= 64-21=43`; by the nine-indegree cap, `e(B,C)+e(C,C)<=6·9-43=11`. Since `A` and `C` are disjoint sets of sizes eight and six, digon-freeness gives `e(C,A)<=48-43=5`. As each of the six vertices in `C` has outdegree eight and no arc connects `v` to `C`,

```
e(C,B) = 48 - e(C,A) - e(C,C) >= 48-5-11 = 32.
```

At least six of the nine vertices of `B` receive an arc from `C`, because each can receive at most six. Thus at most **three** `B` vertices have no incoming arc from `C`.

For each of the `t>=4` vertices `a∈A` of internal outdegree two, `a` sends its six remaining arcs to **all six vertices of `C`**. Consequently `a` cannot receive an arc from `C` (digon) or from any `b∈B` with an incoming arc from `C` (it would form `a→c→b→a`). It receives at most one arc from `v`, three within `A`, and three from `B`. Hence `d⁻(a)<=1+3+3=7`. The four `a` are distinct. QED.

## A global necessary inequality

Let `h` be the number of vertices of indegree nine in a hypothetical counterexample, and `ℓ` the number of vertices of indegree at most seven. All other vertices have indegree eight. Total indegree equals the 24·8 outdegree sum, so

```
h = sum_{d⁻(u) <= 7} (8-d⁻(u)).
```

By the proposition, each of the `h` nine-indegree vertices sends at least **four** arcs to this low-indegree set. Counting those arcs at their destinations gives

```
4h <= e(High, Low) <= sum_{Low} d⁻(u) = 8ℓ-h,
```

so necessarily **`5h <= 8ℓ`**.

The already excluded 8-in/8-out-regular case guarantees any remaining hypothetical counterexample has at least one indegree-nine vertex, and total-degree balance guarantees at least one low-indegree vertex.

## Exact arithmetic reduction (not an exhaustive graph search)

There are **1,076** unordered integer indegree histograms for 24 vertices with all indegrees in `[0,9]` and total indegree 192. One is all-eight regular and is excluded by the earlier theorem, leaving **1,075** numerically irregular histograms with an indegree-nine root. Exactly **83** of those satisfy `5h<=8ℓ`. Thus this *necessary arithmetic test* excludes **992 of 1,075** numerically irregular histograms (approximately 92.3%).

**Crucial boundary:** these are degree multisets, **not** 24-vertex oriented graphs. A surviving histogram does not imply a realizable digraph, still less a triangle-free one. The result prunes potential degree-profile branches of a future independent checker; it neither disproves nor establishes any full graph case.

Two independent enumerators check the count: one ranges over bounded indegree histograms `(c₀,…,c₉)` of length 24 with weighted sum 192; the other partitions 24 units of deficit relative to indegree nine. They produce **identical sets**, not merely equal totals.

## Sharpness of the local four bound

The condition `t>=4` cannot be improved to five using only the eight-vertex lemma. An explicit eight-vertex, 20-arc oriented digraph has outdegree sequence `(2,2,3,3,2,2,3,3)`, indegree sequence `(3,3,2,2,3,3,2,2)`, and no directed triangle. Its edge list is frozen in [`scripts/ch24_profiles.py`](../../scripts/ch24_profiles.py) as `LOCAL_EDGES`; a direct checker verifies every arc, both degree sequences, no digons, and no directed triangles. It is **only a local eight-vertex example**, not a 24-vertex CH counterexample.

## Reproduce

```sh
python3 scripts/ch24_profiles.py --check
python3 -m unittest discover -s tests -p 'test_ch24_profiles.py' -v
```

The counting argument remains a paper proof dependent on the documented eight-vertex lemma; the code is a second arithmetic check and a sharpness witness. Specialist review, prior-art comparison and machine-checking of the reduction from graph hypotheses remain separate obligations before any external mathematical acceptance.

**Next attack:** use the 83 surviving integer profiles to restrict a transparent independent finite search or derive a second discharging inequality, without assuming full indegree regularity or confusing local sharpness with global realizability.
