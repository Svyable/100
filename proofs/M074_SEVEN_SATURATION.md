# M074 — Seven saturated neighbors cannot occur at a (27,9) high root

**Author-derived research candidate, 2026-11-01. Independent proof review and historical novelty audit pending.** This note strengthens the local *necessary structure* of a hypothetical counterexample to the directed-triangle Caccetta–Häggkvist conjecture at \((n,r)=(27,9)\). It does **not** resolve the full finite instance or the unrestricted conjecture. Claim: [#158](https://github.com/Svyable/100/issues/158).

## The theorem

**Theorem (seven-neighbor saturation obstruction).** Let \(D\) be a simple loopless **oriented** digraph on 27 vertices, containing no directed 3-cycle, with **every** outdegree equal to 9 and **every** indegree at most 10. Fix a vertex \(v\) with indegree exactly 10. Set \(A=N^+(v)\), so \(|A|=9\), and define
\[
X=\{a\in A:d^+_{D[A]}(a)=2\}.
\]
Then
\[
\boxed{|X|\le6.}
\]
The result is a conditional prohibition on a particular root-neighborhood pattern; it does not assert a graph satisfying the hypotheses exists. Unlike the earlier [saturated-shadow result](../research/M074_SATURATED_SHADOW.md), which bounded \(|X|\) by seven, the new argument rules out the equality case **for every value** of the root's zero-incoming-from-\(C\) count \(z\).

### Prior elementary premises, with exact scope

1. [The nine-vertex local lemma](M074_NINE_VERTEX.md): any oriented directed-C3-free digraph on nine vertices with minimum outdegree at least 2 has maximum indegree at most 4. Its elementary proof is independent of this note. This theorem uses **only that indegree conclusion**, not the 29-arc extremal bound.
2. [The seven-vertex local lemma](M074_SEVEN_VERTEX_CAP.md): any oriented directed-C3-free digraph on seven vertices with **maximum indegree at most 3** has at most **17 arcs by an elementary argument**. The existing same note strengthens 17 to 16 by exhaustive checking, but the **machine-based improvement is not used anywhere below**.
3. [Degree-defect transfer](DEGREE_DEFECT_TRANSFER.md): when all outdegrees are 9 and indegrees are at most 10, the number of vertices of indegree 10 equals the total deficits \(9-d^-\) among vertices with indegree below 9. We also prove this identity directly below.

None of the premises presupposes that the \((27,9)\) case has been resolved.

## The rooted cut

Suppose for contradiction that \(|X|=t\ge7\). Partition the 27 vertices into
\[
\{v\}\ \dot\cup\ A\ \dot\cup\ B\ \dot\cup\ C,
\]
where \(B=N^-(v)\) has 10 vertices and \(C\) has \(27-1-9-10=7\) vertices. Let \(Y=A\setminus X\); thus \(|Y|=9-t\le2\).

There is no \(A\to B\) arc, for it would complete \(v\to A\to B\to v\), and no \(A\to v\) arc, because the graph is oriented. As every vertex has outdegree 9, every \(x\in X\) sends its two \(A\)-arcs and all **seven** remaining arcs to \(C\):
\[
\boxed{x\to c\quad\text{for every }x\in X,\ c\in C.}\tag{1}
\]
For \(y\in Y\), the definition of \(X\) and the minimum-two-outneighbors premise below imply \(d_A^+(y)\ge3\). Since \(|Y|\le2\), some internal arc \(y\to x\) enters \(X\). Any \(c\to y\) would then create \(c\to y\to x\to c\), while \(c\to x\) is forbidden by (1) and orientation. Therefore
\[
\boxed{e(C,A)=0.}\tag{2}
\]

**Why the internal minimum outdegree is two.** Every \(a\in A\) has nine outgoing arcs, none to \(v\) or \(B\), and at most seven to \(C\). Therefore \(d_A^+(a)\ge2\), including all vertices of \(Y\). The premise of the nine-vertex lemma is satisfied.

Each \(c\in C\) receives at least seven arcs from \(X\); the ambient indegree cap 10 leaves \(d^-_{D[C]}(c)\le3\). The **hand-proved 17-arc** seven-vertex theorem gives
\[
e(C,C)\le17.
\]
Since \(C\) has seven vertices, all of outdegree nine, (2) implies that the total number of arcs \(C\to B\) is
\[
K=e(C,B)=63-e(C,C)\ge\boxed{46}.\tag{3}
\]

For \(b\in B\), let \(k_b=d^-_C(b)\in[0,7]\), \(P=\{b:k_b>0\}\), and \(Z=B\setminus P\). Put \(z=|Z|\), \(p=|P|=10-z\), so
\[
K=\sum_{b\in P}k_b\le7p.\tag{4}
\]
If \(b\in P\), it cannot point to any \(x\in X\), since a \(C\)-predecessor \(c\to b\) would form \(x\to c\to b\to x\). More generally, an arc \(b\to a\), with \(a\in A\), requires
\[
d^+_A(a)\ge k_b+2.\tag{5}
\]
Indeed, \(a\) points to \(9-d_A^+(a)\) vertices of \(C\), and these cannot intersect the \(k_b\) vertices of \(C\) pointing to \(b\), or a directed 3-cycle closes. Their disjointness within seven vertices gives \((9-d_A^+(a))+k_b\le7\).

Define \(q(k)=|\{a\in Y:d_A^+(a)\ge k+2\}|\). Since \(|Y|\le2\), \(q(k)\le2\). Furthermore, in an oriented nine-vertex graph there is **at most one** vertex of internal outdegree eight: two such vertices would point to each other, forming a digon. Thus \(q(6)\le1\), and trivially \(q(7)=0\). For every integer \(1\le k\le7\) this gives the convenient uniform bound
\[
\boxed{q(k)\le7-k.}\tag{6}
\]
For \(k=1,2,3,4,5\), use \(q\le2\le7-k\); the two endpoint cases are as just proved.

Because each \(b\in P\) points to \(v\), at most \(7-k_b\) vertices of \(C\), and at most \(q(k_b)\) vertices of \(A\), its nine outgoing arcs force
\[
d^+_{D[B]}(b)\ge9-1-(7-k_b)-q(k_b)
=1+k_b-q(k_b)\ge2k_b-6.
\]
Summing over \(P\),
\[
\boxed{e(P,B)\ge2K-6p.}\tag{7}
\]
On the other hand, an oriented graph has at most one arc per unordered pair. There are at most \(\binom p2\) arcs **within** \(P\) and \(pz\) from \(P\) to \(Z\), so
\[
\boxed{e(P,B)\le\binom p2+pz=\frac{p(19-p)}2.}\tag{8}
\]
These inequalities count actual arcs, not only relaxed integer profiles.

## The four exhaustive cases

**Case \(z\ge4\).** Here \(p\le6\) and (4) gives \(K\le42\), contrary to (3), \(K\ge46\).

**Case \(z=3\).** Here \(p=7\). By (3) and (7), \(e(P,B)\ge2(46)-6(7)=50\). But (8) bounds it by \(\binom72+7\cdot3=42\), contradiction.

**Case \(z=2\).** Here \(p=8\). Equations (3), (7) and (8) yield
\[
44\ge e(P,B)\ge2K-48\ge44.
\]
Hence **every inequality is equality**. In particular \(K=46\), \(e(P,B)=44\), and every \(b\in P\) must attain equality in (6), namely \(q(k_b)=7-k_b\). If \(k_b\le4\), then \(q(k_b)\le2<7-k_b\), impossible. Thus every \(b\in P\) has \(k_b\ge5\), and from (7) before summing
\[
d_B^+(b)\ge2k_b-6\ge4.\tag{9}
\]
But equality \(e(P,B)=\binom82+8\cdot2\) means **all** unordered pairs inside \(P\) are directed edges, and every edge from \(P\) to \(Z\) is present. Therefore \(D[P]\) is a tournament. It contains no directed 3-cycle, so it is transitive (a shortest directed cycle in a nontransitive tournament would be a triangle), and it has a sink \(b_\ast\) with **zero** outneighbors in \(P\). This sink has exactly the two vertices of \(Z\) as its \(B\)-outneighbors:
\[
d_B^+(b_\ast)=2,
\]
contradicting (9), which demands at least four. The **tournament-sink equality obstruction** closes the one case where the coarse arc budget only ties.

**Case \(z\in\{0,1\}\).** Every \(x\in X\) receives one arc from \(v\), none from \(C\), at most four from \(A\) by the nine-vertex lemma, and at most \(z\) from \(B\), since the positive-\(k\) vertices cannot point into \(X\). Thus
\[
d_D^-(x)\le1+4+z=5+z,
\quad\text{so}\quad9-d_D^-(x)\ge4-z.\tag{10}
\]
These seven or more \(x\)'s all have indegree below nine. Let \(h\) be the number of vertices of indegree 10. Since each vertex has outdegree nine, summing indegree deviations from nine shows
\[
h=\sum_{u:d_D^-(u)<9}(9-d_D^-(u)).
\]
The \(t\ge7\) distinct vertices in \(X\) alone contribute \(t(4-z)\ge7(4-z)\), so \(h\ge28\) if \(z=0\), or \(h\ge21\) if \(z=1\). But none of the \(t\ge7\) low-indegree vertices belongs to the high set, which has size at most \(27-t\le20\). Contradiction.

Every integer \(z\ge0\) has been excluded. Therefore \(t=|X|\le6\). **QED**, conditional on the named elementary prior lemmas.

## The improvement and its boundary

The previously recorded conditional saturated-shadow result gave \(|X|\le7\) for \((27,9)\). The present argument eliminates that **last seven-neighbor case**, and also trivially excludes eight or nine, without using the later stronger computational 16-arc bound on the seven-vertex subgraph. It does **not** restrict the detailed shapes of the remaining \(0\le|X|\le6\) neighborhoods, exclude every indegree-ten root, or prove the full finite instance. The complementary earlier [four-zero obstruction](M074_C_TO_A_BOTTLENECK.md) was obtained independently; this theorem does **not** require that proof.

**Sharp logical dependencies:** The 17-arc premise is essential to this elementary counting route: weakening it to 18 permits \(K=45\), and then the \(z=2\) lower/upper cut need not tie. Conversely, using only the coarse cut in the equality case \(z=2\) is insufficient; the no-triangle tournament-sink step must be included. Dropping orientation permits two internally outdegree-eight vertices, invalidating (6).

## Executable arithmetic and adversarial controls

- \`python3 scripts/ch27_seven_saturation.py --check\` — exact case-budget calculations, equality checks, deliberately weakened 18-arc negative control, and a source graph that demonstrates why a C3-free tournament sink has outdegree zero.
- \`python3 -m unittest discover -s tests -p 'test_ch27_seven_saturation.py' -v\` — separately recomputed case budgets, exhaustive small-\(k\) eligibility maxima, independent integer-deficit checks and adversarial mutations.
- Both are **bounded consistency checks**, not a 27-vertex enumeration, SAT unsatisfiability certificate, Lean formalization, originality audit, or outside specialist review.

**Prior-art starting points:** [the EGRES open-status record](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture), [Hladký–Král’–Norin](https://arxiv.org/abs/0908.2791), and [earlier exact finite exclusion with checked certificates](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md). None establishes that this exact lemma is historically new. The repository should record \`novelty: not_assessed\` until a separate expert literature review. Leave the M074 status and \`data/solved.json\` unchanged.

**Next mathematical obstacle:** prove a similarly explicit bound when only **six or fewer** members of \(A=N^+(v)\) have internal outdegree two. Then \(e(C,A)\) need not vanish, so the new cut must track which \(A\)-vertices the \(C\)-arcs are allowed to target.
