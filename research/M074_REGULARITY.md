# M074 — a self-contained regularity reduction at (n=18, r=6)

**Date:** 2026-10-31. **Status:** proved structural reduction plus a reproducible CNF; **not** an UNSAT result and **not** a new resolution of Caccetta–Häggkvist. Mathematical novelty is **not** claimed. This dossier supplements [M074_CH.md](M074_CH.md), [M074_PRIOR_ART.md](M074_PRIOR_ART.md) and the independent compact encoding.

## Hypotheses and exact scope

All digraphs are loopless. In a counterexample to CH at `(18,6)` there is no directed cycle of length 2 or 3. Therefore it is an **oriented** digraph with no directed triangles. We may delete excess outgoing arcs independently for each vertex, leaving exact outdegree 6; this cannot create a directed cycle.

**Lemma (six-vertex obstruction).** Every oriented digraph on six vertices with minimum outdegree at least two contains a directed triangle.

**Proof.** Suppose there is no triangle. Fix any vertex `v`. Put `a=d⁺(v)≥2`, `b=d⁻(v)` and partition the other five vertices into its `a` outneighbors `A`, its `b` inneighbors `B`, and `C`, with `|C|=5−a−b`. No vertex of `A` can send an arc to `v` (no digons) or to `B` (else `v→A→B→v` is a directed triangle). Every vertex in `A` has at least two outgoing arcs, so

~~~
2a ≤ e(A,A) + e(A,C)
   ≤ a(a−1)/2 + a(5−a−b).
~~~

The first upper bound uses absence of digons, the second counts all possible arcs from `A` to `C`. Dividing by `a` and rearranging gives `a+2b≤5`; since `a≥2`, we obtain `b≤1`. This holds for every vertex, so the total indegree is at most 6, whereas the total outdegree is at least 12. Both sums must equal the total number of arcs. Contradiction. ∎

**Theorem (regularity at 18).** Every oriented, directed-triangle-free digraph on 18 vertices with outdegree exactly six at every vertex has indegree exactly six at every vertex.

**Proof.** Take any vertex `v`, let `A=N⁺(v)` have size six, let `B=N⁻(v)` have size `b`, and let `C` be the remaining `11−b` vertices. There are no arcs from `A` to `B`, nor from `A` to `v`, by the same two-cycle/triangle exclusions. If `b≥7` then `|C|≤4`. Every vertex in `A` has six outgoing arcs, of which at most four can reach `C`, so the oriented subgraph induced by `A` has minimum outdegree at least two. This contradicts the six-vertex lemma. Therefore every indegree is at most six. The total number of arcs is `18×6=108`, so the average indegree is six. Every indegree must equal six. ∎

**Corollary (safe root fixing).** In a hypothetical counterexample reduced to the above regular graph, relabel any root as vertex 0, its six outneighbors as 1–6, its six inneighbors as 7–12, and its five nonneighbors as 13–17. All three sets are disjoint because the graph is oriented. This loses no unlabeled candidate. The root label-fixing removes `C(17,6)×C(11,6)=5,717,712` equivalent choices of the two neighborhood sets for vertex 0 (not a claim about the number of graph isomorphism classes). Other vertices remain unrestricted except for their regularity and triangle-free constraints.

## Reproducible successor to the compact CNF

Run from the repository root:

~~~sh
python3 scripts/ch_regularity.py --output /tmp/ch18-regular.cnf
python3 -m unittest discover -s tests -p 'test_ch_regularity.py' -v
sha256sum /tmp/ch18-regular.cnf
~~~

The new encoding **reuses** the original `CompactCNF(18,6)` without changing its existing frozen checksum. It adds the same four-clause prefix-threshold equivalence gates for each **incoming** row, requiring exactly six incoming arcs, plus the 34 root-unit constraints. In each direction, every arc assignment uniquely determines all threshold variables. Thus, after projecting the auxiliary variables, the new CNF represents exactly the fixed-root, oriented, triangle-free, 6-in/6-out-regular graphs. By the theorem and relabeling corollary, the new CNF is **equisatisfiable** with the original `(18,6)` counterexample search, but it is not assignment-by-assignment identical.

| Certificate property | Value |
|---|---:|
| Arc variables | 306 |
| Auxiliary prefix variables | 3,528 |
| Total variables | 3,834 |
| No-digon clauses | 153 |
| No-triangle clauses | 1,632 |
| Exact-outdegree clauses | 6,660 |
| Exact-indegree clauses | 6,660 |
| Root symmetry unit clauses | 34 |
| **Total clauses** | **15,139** |
| File size | 233,697 bytes |
| SHA-256 | `16448ff34866b74e7b98ea38e599841363503de88590eca564ae29e2b9891d35` |

This has **more** clauses than the 8,445-clause exact-outdegree CNF; the practical solver advantage, if any, is **unmeasured**. The root symmetry and regularity constraints could substantially improve propagation, but that is a testable conjecture, not a performance claim. Negative tests separately check incoming-cardinality semantics and canonical relabeling of a 6-regular circulant graph (which does *not* itself qualify as a triangle-free counterexample).

## Prior-art and acceptance gate

- [wustep/maths, directed-triangle attack](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md) reports six in-degree branch DRAT refutations for `n=18, d=6`, but its [compute README](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/compute/README.md) says the cube DRAT files are **not in the Git tree**. We have **not** obtained and independently replayed those traces. Its claimed `(18,6)` result, if independently accepted, supersedes a fresh finite novelty claim.
- The separate [joshp123 fixed-outdegree-six manuscript](https://github.com/joshp123/solve-a-maths-problem-dont-care-which-make-no-mistakes) claims the *entire* `r=6` case, with a published 438 MB proof corpus. Its status remains an unpeer-reviewed external claim, not an independently accepted theorem here.

**Next proof gate:** obtain a proof-logged UNSAT trace for the *exact hash* of the new CNF and replay it with an independent checker; alternatively retrieve the external trace and independently reconstruct/check its CNF, symmetry assumptions, and partition coverage. No solver has been run on the new CNF here. A positive assignment needs independent graph-level verification. Even a verified `(18,6)` UNSAT theorem does not prove CH for all `n,r`, and the `Solved` ledger must remain unchanged.
