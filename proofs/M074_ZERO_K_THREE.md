# M074 — triangle-propagated missing pairs exclude the (27,9) z=4 branch

**Research candidate, 2026-11-01.** A strictly stronger necessary condition on a hypothetical Caccetta–Häggkvist directed-triangle counterexample at (27,9). The argument below is an **enumeration-free mathematical deduction** from the previously documented nine-vertex local lemma and B-subset girth lemma. The independent integer checker is a falsifier, not a proof premise. This does not solve the full finite (27,9) case, the unrestricted conjecture, or establish novelty or independent specialist acceptance.

## Theorem

Let D be a loopless oriented directed-triangle-free graph on 27 vertices with outdegree **exactly nine** at every vertex. Suppose v has indegree ten. Set A=N⁺(v), B=N⁻(v), C the seven remaining vertices; then (|A|,|B|,|C|)=(9,10,7). Write k(b)=d⁻_C(b). Then

\[
\boxed{z:=|\{b\in B:k(b)=0\}|\le3.}
\]

This improves the z≤4 result in [the preceding CH27 proof](M074_27_REGULAR.md). Any minimum-outdegree-nine counterexample can be thinned to exact outdegree nine without introducing a directed 2- or 3-cycle; the theorem concerns the thinned graph.

## 1. New ingredient: triangle propagation creates missing A–C pairs

For a∈A let α(a)=d⁺_A(a), P_a=N⁺_C(a), and m=e(A,A)=Σ_A α(a). Because A cannot send arcs to v or B, |P_a|=9−α(a). The [sharp nine-vertex lemma](M074_NINE_VERTEX.md) gives 2≤α(a)≤8 and 18≤m≤29.

Let M be the number of pairs (a,c) in A×C that are **nonadjacent in both directions**. Suppose a→a′ is an arc within A. Every c∈P_{a′}\P_a must be nonadjacent to a: a→c is absent by definition of P_a, while c→a would form a→a′→c→a. Thus

\[
 M\ge |P_{a'}\setminus P_a|\ge
 \max(0,\alpha(a)-\alpha(a')). \tag{P}
\]

Furthermore, when two distinct source vertices a send degree-descending internal A-arcs, the missing (a,c) pairs have different first endpoints. They contribute **at least two** to M, even if they involve the same c.

There are 9×7=63 possible A–C pairs. The A vertices send 81 arcs, of which m stay within A, so

\[
e(A,C)=81-m,\qquad e(C,A)=m-18-M.
\]

Every ambient indegree is at most ten: an indegree-eleven root would induce a nine-vertex outneighborhood of minimum internal outdegree at least three, forbidden by the local nine-vertex lemma. The seven C vertices thus receive at most 70 arcs total, of which 81−m arrive from A, giving

\[
e(B,C)+e(C,C)\le m-11.
\]

The C vertices send 63 arcs in total. Therefore the number K=e(C,B) obeys

\[
\boxed{K\ge92-2m+M.} \tag{C}
\]

The earlier cut omitted M. Each missing A–C pair strengthens the forced C→B traffic by one.

## 2. Bound K above when z=4

Assume z=4 for contradiction. Exactly six values k(b) are positive, each at most seven.

An arc b→a from B to A requires α(a)≥k(b)+2: otherwise some c belongs to both N⁺_C(a) and N⁻_C(b), forming a→c→b→a. Set q(j)=|{a∈A:α(a)≥j+2}|. Each b sends one arc to v and at most 7−k(b) to C and q(k(b)) to A, so

\[
d_B^+(b)\ge1+k(b)-q(k(b)). \tag{B}
\]

The proved [ten-vertex B-subset girth lemma](M074_B_INTERNAL_GIRTH.md) states that three internal outdegree floors of eight force a directed triangle, while five floors of seven or six floors of six force a directed-triangle-free graph on at most six vertices of minimum outdegree two, impossible.

Write p=max_A α. These constraints bound the sum of the six positive k-values:

- **p=8:** There is at most one A vertex of outdegree eight (two would require at least 2·8+7·2=30 arcs). Hence q(6)≤1. Every k≥6 forces a B-outdegree floor ≥6, and k=7 forces floor 8. Thus at most five positive k are ≥6 and at most two equal 7, yielding **K≤2·7+3·6+5=37**.
- **p=7:** q(6)=0. Every k≥6 forces a floor ≥7; k=7 forces floor 8. At most four k are ≥6 and at most two equal 7, giving **K≤2·7+2·6+2·5=36**.
- **p≤6:** q(5)=q(6)=0. Values k=5,6,7 force floors at least 6,7,8. At most five k are ≥5, four are ≥6, and two equal 7. Thus **K≤2·7+2·6+5+4=35**.

These bounds hold for any actual oriented triangle-free graph and require no profile enumeration.

## 3. Five elementary cases for p

The total internal A outdegree surplus over baseline two is m−18≤11.

**Case p=8.** An A vertex a of internal outdegree eight points to every other A vertex, including some vertex a′ of outdegree two; otherwise m≥8+8·3=32. By (P), M≥8−2=6. Then (C) gives K≥92−2·29+6=40>37.

**Case p=7.** At least two other A vertices have outdegree two; with fewer, m≥7+2+7·3=30. A vertex of internal outdegree seven points to seven of eight possible A targets and must hit at least one of those two. Hence M≥7−2=5, giving K≥39>36.

**Case p=6.** Fix a with internal outdegree six. Its surplus four leaves at most seven surplus units among the other eight A vertices; at most two of those can have degree at least five, each consuming three. Of the six distinct targets of a, one therefore has degree at most four. The directed arc to that target forces M≥6−4=2. Hence K≥36>35.

**Case p=5.** Fix a of degree five. After its three surplus units, at most eight remain. At most four of the other eight vertices have degree at least four, each consuming two. Among the five targets of a is one of degree at most three, forcing M≥5−3=2 and K≥36>35.

**Case p≤4.** Since K≤35, (C) excludes m≤28 outright: even with M=0, K≥92−2·28=36. Thus m=29 and p=4. Let H be the A vertices of internal outdegree four and h=|H|. We have 2≤h≤5: h=1 would imply m≤4+8·3=28, and h≥6 would imply m≥18+2h≥30. The h high vertices send 4h arcs into A, at most h(h−1)/2 internally within H. Consequently at least

\[
4h-\binom h2\in\{7,9,10,10\}\quad(h=2,3,4,5)
\]

arcs run from H to lower-degree vertices. Since a single high vertex sends only four arcs, at least **two distinct high sources** have such descending arcs. By the additive observation after (P), M≥2. So K≥92−58+2=36>35.

All values of p are impossible under z=4. The already proved z≤4 bound excludes z≥5, hence **z≤3**. □

## Immediate low-indegree consequence

The nine-vertex lemma also excludes minimum internal outdegree three on A, so at least one a∈A has α(a)=2. It points to all seven C vertices and receives no arc from C. By the local nine-vertex lemma, it receives at most four arcs inside A; from B, only the z≤3 vertices with k=0 can point to it, or a→c→b→a would be a triangle. Including v→a gives

\[
d^-_D(a)\le1+4+3=8.
\]

Thus **every indegree-ten vertex has an outneighbor of indegree at most eight**. This is a genuine additional structural restriction, not a contradiction for the whole (27,9) finite case.

## Audit and scope

Run from repository root:

    python3 scripts/ch27_zero_k_three.py
    python3 -m unittest discover -s tests -p 'test_ch27_zero_k_three.py' -v

The independent relaxed-integer audit starts from 166 possible sorted A-degree profiles and 924 sorted k-profiles with exactly four zero entries: 153,384 pairs, *not graphs*. Existing root-cut and B-capacity/girth tests leave 295 relaxed pairs. The new cut eliminates all **295**: 160 with p=8, 102 with p=7, and 33 with p=6. Tests independently generate both profile families, implement the arithmetic again, remove the missing-pair gate as an adversarial mutation, and check triangle propagation over all partial orientations on five labeled vertices. The **hand case split is the proof**; the audit is a reproducibility and falsification check.

**Boundaries:** z=0,1,2,3 remain as possible local cases. No complete proof of the (27,9) minimum-outdegree-only case, no general Caccetta–Häggkvist resolution, no new theorem acceptance, and no originality claim. Seek independent graph-theory review and prior-art comparison before publication. Do not change the conjecture registry or data/solved.json. See [EGRES](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture) and [external finite computations](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md) for context.
