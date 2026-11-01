# M074 — rigidity at the eight-vertex, 21-arc boundary

**Research record: 2026-11-01.** This is a self-contained elementary structural lemma, a corollary for nine-vertex neighborhoods, and a bounded new filter on *relaxed* (27,9) integer profiles. The mathematical derivation is presented for independent specialist inspection; a machine check of integer profiles does **not** confer independent review. In particular, the (27,9) minimum-outdegree case and the unrestricted Caccetta–Häggkvist conjecture remain unresolved here. Originality over the historical literature has **not** been established. Claim: [#132](https://github.com/Svyable/100/issues/132).

## Theorem 1: equality in the eight-vertex bound is rigid

Let \(H\) be a finite **oriented** graph (simple, loopless, with no digons) on eight vertices, with **no directed 3-cycle** and \(\delta^+(H)\ge2\).

The existing [eight-vertex local lemma](../research/M074_ELEMENTARY_24_REGULAR.md) proves \(e(H)\le21\), and this bound is attained. We strengthen its equality case:

> **Rigidity theorem.** If \(e(H)=21\), there is a vertex \(s\) with \(N^+(s)=V(H)\setminus\{s\}\). The induced graph \(H-s\) has exactly seven vertices and is **2-in/2-out regular**.

The theorem describes degree structure, not a unique isomorphism class of 7-vertex cores.

### Proof: sharpen one local degree pair

For any vertex \(v\), write \(a=d^+(v)\), \(b=d^-(v)\), and partition the other seven vertices into \(A=N^+(v)\), \(B=N^-(v)\) and \(C\), of sizes \(a,b,7-a-b\). Because of the oriented and directed-triangle-free hypotheses, there are no \(A\to(B\cup\{v\})\) arcs. Every member of \(A\) has at least two outgoing arcs, whence

\[
2a\le e(A,A)+e(A,C)\le \binom a2+a(7-a-b).
\]

Division by \(a\ge2\) yields \(a+2b\le9\), and in particular \(b\le3\). As shown in the previous eight-vertex lemma, these consequences can be sharpened:

* \(b=3\) forces \(a=2\). Indeed, \(a\le3\); if \(a=3\), then \(C\) has one vertex and the three vertices of \(A\) have positive outdegree inside \(A\), forcing a directed triangle.
* \(b=2\) forces \(a\le4\). If \(a=5\), \(C\) is empty, and \(H[A]\) has minimum outdegree at least two, impossible on five vertices by the same rooted inequality.
* \(b=1\) forces \(a\le5\). If \(a=6\), then \(C\) is empty and \(H[A]\) has minimum outdegree at least two, impossible on six vertices by the same rooted inequality.
* \(b=0\) has the trivial bound \(a\le7\).

**New strengthening: \(b=2\) actually forces \(a\le3\).** Suppose \(a=4\) and \(b=2\). Then \(C=\{c\}\). Each vertex of \(A\) has at least two outgoing arcs but none can lead to \(v\) or \(B\), so every vertex has at least one outneighbor inside the four-vertex graph \(H[A]\). Any oriented, directed-triangle-free graph on four vertices with minimum outdegree one must be a directed four-cycle: the minimum-outdegree condition produces a directed cycle, whose length must be four, and every extra chord would make a directed triangle. Thus every member of \(A\) has *exactly one* outgoing arc inside \(A\), and its required second arc must point to \(c\). All four vertices of \(A\) therefore point to \(c\), giving \(d^-(c)\ge4\), contradicting the universal bound \(d^-\le3\). Hence \(a\le3\) whenever \(b=2\).

### Proof: classify the equality deficit

Assume \(e(H)=21\). All eight indegrees are at most three, so the total deficiency from indegree three is

\[
\sum_{v\in V(H)} (3-d^-(v))=24-21=3.
\]

Since the deficiencies are nonnegative integers, their unordered positive parts can only be \((3)\), \((2,1)\), or \((1,1,1)\).

* **Deficiencies \((2,1)\)** would give six vertices of indegree three, one of indegree one, and one of indegree two. The outdegree bounds just proved give
  \[
  e(H)=\sum d^+(v)\le6\cdot2+5+3=20,
  \]
  contradiction.
* **Deficiencies \((1,1,1)\)** would give five vertices of indegree three and three of indegree two. Hence
  \[
  e(H)\le5\cdot2+3\cdot3=19,
  \]
  contradiction.
* Thus the only possibility is **\((3)\)**: seven vertices have indegree three and one vertex \(s\) has indegree zero. The first bullet above forces each of the seven to have outdegree exactly two. Those seven vertices contribute 14 arcs, so \(s\) must contribute \(21-14=7\) arcs. Hence \(s\) points to all other vertices. They have no arcs into \(s\), so each retains outdegree two inside \(H-s\), and loses the one incoming arc from \(s\), leaving indegree two.

This proves the theorem. \(\square\)

**Sharp witness:** On \(\mathbb Z/7\mathbb Z\) put \(i\to i+1,i+2\pmod7\), then adjoin \(s\) with arcs to all seven. There are 14+7=21 arcs; the old seven-vertex graph has directed girth at least four (three steps of size 1 or 2 never total 7 modulo 7). This realizes the theorem's equality case.

## Corollary 2: the nine-vertex source-chain restriction

Let \(J\) be a nine-vertex oriented graph without directed triangles and with \(\delta^+(J)\ge2\). Suppose \(e(J)=29\) **and** there is a vertex \(t\) of outdegree eight.

Because \(J\) is oriented, \(t\) has indegree zero; removing it preserves the minimum outdegree of all other vertices. The resulting eight-vertex graph has \(29-8=21\) arcs and meets Theorem 1. Thus its seven-vertex core is 2-in/2-out regular and its additional vertex \(s\) sends arcs to all seven. Reinstating \(t\), the sorted outdegree sequence of \(J\) is necessarily

\[
\boxed{(2,2,2,2,2,2,2,7,8).}
\]

In fact \(t\to s\), \(t\to U\), \(s\to U\), and \(J[U]\) is 2-in/2-out regular on seven vertices. This conclusion is **conditional on the outdegree-eight vertex**; an arbitrary 29-arc graph on nine vertices has not been classified.

## Consequence for the (27,9) indegree-ten branch

Follow the established cut notation in [the (27,9) regular/irregular analysis](M074_27_REGULAR.md) and [the \(B\)-internal small-set obstruction](M074_B_INTERNAL_GIRTH.md). In a hypothetical outdegree-nine, directed-triangle-free oriented graph on 27 vertices, at an indegree-ten root \(v\), put

* \(A=N^+(v)\) (nine vertices), \(B=N^-(v)\) (ten vertices), \(C\) (seven vertices);
* \(\alpha(a)=d_A^+(a)\ge2\) for \(a\in A\), and \(m=\sum_{a\in A}\alpha(a)\le29\);
* \(k(b)=d_C^-(b)\in[0,7]\) for \(b\in B\), and \(\sum k=e(C,B)\);
* \(z=|\{b\in B:k(b)=0\}|\).

Prior work gives \(\sum k\ge92-2m\), and \(z\le4\). The already-published local filter for \(z=4\) leaves **295 relaxed sorted integer profile pairs** \((\alpha,k)\). They are necessary constraints only, not actual graph constructions.

### New source-chain exclusion

If \(m=29\) and \(\max\alpha=8\), Corollary 2 applies to \(D[A]\). Necessarily

\[
\alpha=(2,2,2,2,2,2,2,7,8).
\]

Any other profile with these two properties is impossible. This one implication eliminates **120** of the 295 previously unexcluded relaxed pairs.

### Previously established \(C\)-cut cap, now applied systematically

Whenever at least seven of the nine \(\alpha\)'s equal two, each corresponding \(a\in A\) points to **all seven** vertices in \(C\): it has nine total outgoing arcs, two internal arcs in \(A\), and none to \(v\) or \(B\). Every \(c\in C\) therefore has at least seven incoming arcs from \(A\), leaving internal indegree at most three because all ambient indegrees are at most ten. The independently checked [seven-vertex cap](M074_SEVEN_VERTEX_CAP.md) yields \(e(C,C)\le16\).

But \(e(A,C)=81-m\), hence \(e(C,A)\le m-18\) by orientation. Counting the 63 outgoing arcs of the seven \(C\)-vertices gives

\[
e(C,C)=63-e(C,A)-e(C,B)\ge81-m-\sum k.
\]

Consequently, **if there are at least seven \(\alpha=2\) entries, the profile requires**

\[
\boxed{\sum k\ge65-m.}
\]

Applying this *existing* bound to the profiles surviving the new rigidity cut eliminates another **20** pairs. The two exclusions are disjoint in the recorded sequential order.

| Exact stage on sorted relaxed \(z=4\) profiles | Pairs surviving |
|---|---:|
| Existing \(B\)-subset and small-set girth tests | 295 |
| **New** 8-vertex equality rigidity | 175 |
| **Existing** sharp 7-vertex \(C\)-cap applied to all survivors | **155** |

Thus the new theorem and a systematic application of an existing theorem remove **140 of 295** necessary integer profiles (47.5% of those profiles, not 47.5% of hypothetical graphs or of the conjecture). **155 profiles remain, and even those have not been shown realizable.**

## Checks and falsifiers

The [exact integer profile checker](../scripts/ch27_rigidity.py) imports the earlier profile enumerator and records every sequential count. The [independent test](../tests/test_ch27_rigidity.py) checks the indegree-deficiency alternatives, the directed-four-cycle argument on all 729 partial orientations of four vertices, the positive circulant source-chain witness, and the profile counts by a second loop.

~~~sh
python3 scripts/ch27_rigidity.py --check
python3 -m unittest discover -s tests -p 'test_ch27_rigidity.py' -v
~~~

The programs do **not** enumerate all eight-vertex graphs, provide a Lean proof, certify 27-vertex graph nonexistence, or verify mathematical originality. A genuine counterexample to Theorem 1 would be an eight-vertex oriented directed-triangle-free graph of minimum outdegree two and 21 arcs without a source. A graph realizing an excluded \((\alpha,k)\) would falsify the stated transfer, and a profile surviving our integer tests is **not** a positive counterexample.

**Prior-art boundaries:** [the published CH literature](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture); [Brown–Erdős–Simonovits, *Extremal problems for directed graphs* (1973)](https://doi.org/10.1016/0095-8956(73)90034-8); [some approaches to short cycles in digraphs (2002)](https://doi.org/10.1016/S0166-218X(01)00279-7); and [previous finite CH computations](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md). None of these links establishes that this exact rigidity lemma is unpublished. Outside specialist prior-art review is still required.

**Next nontrivial obligation:** use the actual incidence pattern of the remaining 155 profile pairs—not only their ordered degree multisets—to derive a contradiction or construct a falsifier at the indegree-ten root. Preserve the original M074 evidence state and empty Solved ledger.
