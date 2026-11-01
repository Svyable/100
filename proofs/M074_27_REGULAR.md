# M074 — a finite (27,9) in/out-regular exclusion

**Research candidate, 2026-10-31.** This note excludes the *in/out-regular* part of the directed-triangle Caccetta–Häggkvist finite case with n=27 and r=9. It does **not** prove the full minimum-outdegree-nine finite case or the unrestricted conjecture. Its exact integer calculation has an independent implementation, but the mathematical deduction awaits outside specialist review. No novelty or priority claim is made.

## Prerequisites already on main

1. The [sharp nine-vertex lemma](M074_NINE_VERTEX.md) proves that a nine-vertex oriented, directed-triangle-free graph of minimum outdegree two has **at most 29 arcs**, and no nine-vertex such graph has minimum outdegree three. The 29 bound is attained. This theorem was independently committed before the present regular-branch argument; its proof is not duplicated here.
2. The [general saturated-pivot lemma](../research/M074_ELEMENTARY_18.md) says that if a 3r-vertex directed-triangle-free oriented graph is both r-inregular and r-outregular, then every vertex of its outneighborhood has at least two internal outneighbors, and dually every vertex of its inneighborhood has at least two internal inneighbors.
3. The [general regular-root cross-cut lemma](../research/M074_ELEMENTARY_24_REGULAR.md) applies at any r. Write A=N⁺(v), B=N⁻(v), C for the r−1 nonneighbors, m_A=e(A,A), m_B=e(B,B), alpha(a)=d⁺_A(a), beta(b)=d⁻_B(b), and t=e(B,A). Then

    t >= r²−2*m_A,
    t >= r²−2*m_B,

and any edge b→a with b in B, a in A requires alpha(a)+beta(b)>=r+1. The last condition follows because N⁺_C(a) and N⁻_C(b) must be disjoint within C, otherwise a→c→b→a is a directed triangle.

## The regular-branch theorem

**Theorem.** No oriented directed-triangle-free graph on 27 vertices has indegree **and** outdegree equal to nine at every vertex.

**Proof.** Assume a counterexample. At a root v, the sets A and B each have nine vertices and C has eight. Saturation gives internal outdegree at least two on A and, after reversing arcs, on B. The sharp nine-vertex lemma gives m_A,m_B<=29. Therefore the crossing demand is

    t=e(B,A) >= max(81−2m_A,81−2m_B) >= 23.       (1)

All nine alpha-values and nine beta-values lie in the integer interval [2,8], each array has sum at most 29. An edge b→a is eligible only if alpha(a)+beta(b)>=10.

There are exactly **166** sorted nine-tuples with entries in [2,8] and sum at most 29. For each of the **27,556** ordered pairs of such tuples, count the eligible pairs. The exact integer maximum is

    max #{(a,b): alpha(a)+beta(b)>=10} = 22.      (2)

This small finite statement is verified by [scripts/ch27_crosscut.py](../scripts/ch27_crosscut.py) and independently generated and evaluated by the histogram-convolution implementation in [tests/test_ch27_crosscut.py](../tests/test_ch27_crosscut.py). The bound 22 is sharp **as a relaxed integer bound**; it is attained by

    alpha=(2,2,2,2,2,2,2,7,8),
    beta =(2,2,2,3,3,3,3,3,8).

No jointly realizable graph is implied by these tuples. Every B→A edge must use an eligible ordered pair. By (1) and (2), 23<=t<=22, a contradiction. QED, subject to independent review of the handwritten prerequisites and their composition.

## What remains at minimum outdegree nine

Suppose a hypothetical triangle-free oriented digraph on 27 vertices had minimum outdegree at least nine. Deleting extra outgoing edges gives exact outdegree nine without adding any cycle. For a vertex of indegree b, its nine outneighbors need at least b−8 internal outgoing edges apiece; if b>=11 they would have minimum internal outdegree three, contrary to the nine-vertex lemma. Thus every indegree is at most ten. If none were ten, averaging would force all indegrees equal nine, contradicted above. **A hypothetical counterexample must therefore contain an indegree-ten root.** This is a reduction, not the desired contradiction.

Fix such a root v; let A=N⁺(v), B=N⁻(v), C be its nonneighbors, of sizes 9, 10, 7. Put m=e(A,A)<=29 and k(b)=d⁻_C(b) for b in B. The cut and indegree-ten ceiling imply

    e(A,C)=81−m,
    e(C,A)<=m−18,
    e(B,C)+e(C,C)<=m−11,
    sum_{b in B} k(b)=e(C,B)>=92−2m>=34.        (3)

Let z count the B vertices with k=0. As 0<=k<=7, equation (3) first gives z<=5. In fact **z<=4**. If z=5, the remaining five k-values sum to at least 34, so four equal seven and the fifth is at least six.

For each b in B, an edge b→a with a in A is permitted only when alpha(a)>=k(b)+2, where alpha(a)=d⁺_A(a). Define q(b) as the number of eligible a's. Since b sends one edge to v and at most 7−k(b) into C, its internal B-outdegree is at least 1+k(b)−q(b).

For k=7, q=0 because alpha<=8, so d⁺_B(b)>=8. For k=6, q<=1: two alpha=8 vertices would consume at least 12 surplus units beyond the baseline alpha=2, whereas m<=29 allows only 11. Therefore the five positive-k vertices in B would send at least 4·8+6=38 arcs into B. But any five vertices in a ten-vertex oriented graph can send at most binom(5,2)+5(10−5)=35 arcs into B. Contradiction; **z<=4**.

However, this does not close the irregular branch. A relaxed necessary profile is

    alpha=(2,2,2,2,2,2,2,7,8), m=29,
    k=(0,0,0,0,5,5,5,5,7,7), sum k=34, z=4.

It passes (3) and every subset-capacity inequality for the B-internal outdegrees. It is **not** a 27-vertex graph. It only demonstrates that this layer of degree constraints does not yet imply the global low-indegree requirements needed for a transfer contradiction. In particular, a vertex in A with internal outdegree two receives at most 1+4+z<=9 arcs, which need not place it in the low indegree<=8 class.

## Exact reproduction and falsifiers

From the repository root:

    python3 scripts/ch27_crosscut.py
    python3 -m unittest discover -s tests -p 'test_ch27_crosscut.py' -v

| Check | Result |
|---|---:|
| Sharp local nine-vertex example | 29 arcs |
| Sorted nine-vertex degree profiles | 166 |
| Ordered profile pairs checked | 27,556 |
| Minimum crossing demand | 23 |
| Maximum eligible crossing pairs | 22 |
| Unexcluded regular pairs | **0** |
| Unexcluded when local cap is weakened from 29 to 30 | **60** |
| Irregular z=4 relaxed profile passes B subset capacities | Yes, not a graph |

The six focused unit tests independently generate the degree profiles with histogram compositions instead of sorted tuples; compute the eligible bound by histogram convolution; validate the sharp graph example with loop/digon/triangle negative controls; and retain the one-arc weakening and irregular-survivor controls. The program is an exact **integer** checker, not a 27-vertex graph census, a SAT/UNSAT proof, or a proof-assistant formalization.

**Next obligation:** strengthen or eliminate the indegree-ten, z=4 local incidence branch, and obtain independent mathematical review of the full derivation. Do not change M074's global evidence state or data/solved.json. The unrestricted [Caccetta–Häggkvist conjecture](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture) remains open.

