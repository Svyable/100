# M074 — five-low obstruction at a zero-free CH(27,9) high root

**2026-11-02 UTC.** Work ID `X-M074-Z0-ROOT`; [claim #252](https://github.com/Svyable/100/issues/252); scope SHA-256 `1885916a20816601272789f54ca2cc3e538a45c04ccccd7b3e5a579fe4fe3ed6`.

**Status:** Author-derived, precisely restricted elementary theorem **candidate**, with two algorithmically distinct exact finite audits and literal graph controls. No independent specialist mathematical review or historical-novelty confirmation. No full CH(27,9) result or global Caccetta–Häggkvist resolution. Imported local lemmas are themselves unreviewed; the pending three-low theorem and z=2 exclusion are **not** proof dependencies.

## Precisely quantified claim

Let D be a loopless **oriented**, directed-triangle-free graph on 27 vertices, every vertex having outdegree exactly nine. Fix an indegree-ten vertex v, let A=N⁺(v) (9 vertices), B=N⁻(v) (10), C the seven nonneighbors, and write α(a)=d⁺_A(a), k(b)=d⁻_C(b). Suppose **k(b)≥1 for every b∈B** (the z=0 branch). Then

\[
\boxed{|\{a\in A:\alpha(a)=2\}|\le4.}
\]

If the separate, unreviewed nine-vertex three-low candidate is correct, the surviving number is three or four. This result does **not** rule out z=0 or show that four lows can occur in a full 27-vertex graph.

## Elementary proof

The existing [nine-vertex local lemma](../proofs/M074_NINE_VERTEX.md) proves that an oriented, triangle-free nine-vertex graph of minimum outdegree at least two has at most 29 arcs and satisfies d⁺(a)+2d⁻(a)≤10. The same local obstruction bounds every ambient indegree by ten in a hypothetical 27-vertex nine-outregular triangle-free graph. We use these previously authored (not externally reviewed) facts.

**Root cuts.** No A→B arcs exist. Every a∈A sends α(a) arcs within A and 9−α(a) to C, so α(a)≥2. Let m=Σ_A α≤29, and let M be the number of pairs across A×C that are nonadjacent in both directions. Counting 63 possible A–C pairs yields e(C,A)=m−18−M. The ambient indegree ceiling gives e(B,C)+e(C,C)≤m−11. Summing the 63 outgoing C-arcs therefore yields

\[
K:=\sum_{b\in B}k(b)=e(C,B)\ge92-2m+M. \tag{1}
\]

**Five lows force K≥44.** Assume exactly five a∈A have α=2; call this set L, with H=A\L of size four. Every low a points to all seven C vertices. If x∈H points to some a∈L, each of the α(x)−2 C vertices not reached by x must be nonadjacent to x, since c→x→a→c would be a directed triangle. Thus x contributes at least α(x)−2 missing A–C pairs.

Every x∈H with α(x)≥4 must point to L, since there are only three other H vertices. A vertex with α(x)=3 can avoid L only by pointing to all three other H vertices; **at most one** such vertex can do this, since two would form a digon. Contributions have distinct first endpoints, hence

\[
M\ge\sum_{x\in H}(\alpha(x)-2)-1=m-19.
\]

Together with (1) and m≤29, this gives

\[
\boxed{K\ge73-m\ge44.} \tag{2}
\]

**High B vertices require two eligible A targets.** Let b∈B have ambient indegree ten and put k=k(b). No A or v arc enters b, so d⁻_B(b)=10−k and, by orientation within the ten-vertex B, d⁺_B(b)≤k−1. An arc b→a requires α(a)≥k+2: otherwise a reaches 9−α(a) vertices of C and one of those also points to b, closing a directed triangle. Write q(k)=|\{a∈A:α(a)≥k+2\}|. Because b sends one arc to v, at most 7−k to C and at most q(k) to A, its B-outdegree is at least 1+k−q(k). Therefore

\[
1+k-q(k)\le k-1,\qquad \boxed{q(k)\ge2}. \tag{3}
\]

If s is the second-largest α-value, every indegree-ten b∈B consequently satisfies k(b)≤s−2.

**Global degree deficits.** Each low a∈L receives one arc from v, at most four from A, none from C (it points to all C), and none from B (every k(b)>0, so b→a would form a triangle through C). Hence d⁻(a)≤5. Let h be the number of ambient indegree-ten vertices. Summing d⁻−9 over all 27 vertices gives

\[
h=\sum_{u:d^-(u)<9}(9-d^-(u))\ge4\cdot5=20.
\]

Five low A vertices cannot be high. Of the 17 vertices outside B, at most 12 can have indegree ten, so **at least eight B vertices** have indegree ten.

Since five α-values equal two and the other four are at least three, s≤6: two values at least seven would force m≥5·2+2·7+2·3=30>29.

- If s≤5, at least eight B vertices have k≤s−2≤3 by (3), while the other two have k≤7. Therefore K≤8·3+2·7=38, contradicting (2).
- If s=6, one of the four higher α-values equals three; otherwise m≥5·2+6+6+4+4=30. From K≥44 and 1≤k≤7, at most four k-values equal one, because K≤n₁+7(10−n₁)=70−6n₁. Fix a with α(a)=3. Its internal A-indegree is at most three by the local lemma; at most one C vertex can point to it, and only B vertices with k=1 can point to it. Including v→a gives d⁻(a)≤1+3+1+4=9. This additional nonhigh A vertex means at most 11 of the 17 non-B vertices are high, forcing **at least nine high B vertices**. Their k-values are at most s−2=4, and the tenth k≤7. Thus K≤9·4+7=43, contradicting (2).

Therefore exactly five lows are impossible. For t≥6 lows, each has indegree≤5, so h≥4t, but h≤27−t since these t vertices are nonhigh. Hence 5t≤27 and t≤5. Combined with the five-low exclusion, **t≤4**. □

The proof is a handwritten counting argument, not a MILP or SAT infeasibility claim. It does not assume that any relaxed profile is graph-realizable.

## Reproduction and adversarial checks

```sh
python3 -m scripts.ch27_z0_five_low --check --json
python3 -m unittest discover -s tests -p 'test_ch27_z0_five_low.py' -v
```

The main checker enumerates **35** sorted nine-vertex outdegree profiles with exactly five twos and sum at most 29, and **8,008** sorted ten-tuples with 1≤k≤7. Of **280,280** relaxed degree pairs, **200,489** fail the missing-pair lower bound K≥73−m; the remaining **79,791** fail the high-B eligibility count. Zero unresolved pairs remain. This challenges the algebra but does **not** enumerate 27-vertex digraphs.

A separately written histogram-composition enumeration regenerates all counts without calling the main classifier. Literal adjacency-set tests independently check two actual nine-vertex triangle-free oriented graphs, with four and five outdegree-two vertices respectively, plus A→C/C→A triangle propagation, a forged digon, a forged directed triangle, and a k=0 hypothesis violation. These small graphs are **not** full 27-vertex counterexamples. Seven dedicated tests and the exact standalone checker passed locally. Full repository regeneration, all repository tests, exact-head CI, Lean formalization, independent specialist review and novelty assessment were **not** run or claimed.

## Literature boundary, failed routes, and next falsifier

- Caccetta–Häggkvist, *On minimal digraphs with given girth*, Congressus Numerantium 21 (1978), 181–187: original open conjecture.
- Hladký, Kráľ and Norin, *Counting flags in triangle-free digraphs*, Combinatorica 37 (2017), 49–76, [DOI](https://doi.org/10.1007/s00493-015-2662-5): published 0.3465n triangle-forcing bound, not the conjectured n/3 threshold.
- [EGRES open-problem record](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture): the directed-triangle case remains open.
- Existing [nine-vertex lemma](../proofs/M074_NINE_VERTEX.md), [zero-k root analysis](../proofs/M074_ZERO_K_THREE.md), [seven-saturation candidate](../proofs/M074_SEVEN_SATURATION.md), and distinct pending [z=2 claim #247](https://github.com/Svyable/100/issues/247). These are unreviewed author-side results, not independent acceptance. No matching exact published z=0/t≤4 statement was identified in a targeted source search; **that does not establish historical priority**.

**Failed stronger avenues:** Global indegree-deficit counting alone gives only 5t≤27, i.e. t≤5. It is invalid to assume all ten B vertices are high; the proof initially forces only eight. A literal nine-vertex triangle-free graph with five low vertices refutes any attempt to derive t≤4 from A alone. A stronger t≤3 conclusion is not established: the local nine-vertex four-low example is realizable, but its 27-vertex z=0 extension is unknown. Exploratory small-graph integer optimization was used only to locate test witnesses; no optimizer verdict is a proof premise.

**Next falsifier:** A literal 27-vertex oriented, triangle-free, nine-outregular graph with an indegree-ten root, all ten k(b)>0, and at least five α=2 vertices would refute the result. Also check the imported nine-vertex bound and global indegree ceiling, the M≥m−19 missing-pair count, and the exact 35×8,008 audit. The next substantive target is the t=4 z=0 root under full A/C/B incidence constraints. Seek outside specialist review and a historical novelty audit before any accepted status. Do not change solved/evidence status, coverage, benchmarks, or the separate PR-landing task/cadence.
