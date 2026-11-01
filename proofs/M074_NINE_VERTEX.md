# M074 — sharp nine-vertex local lemma and the (27,9) frontier

**Research record: 2026-10-31.** This is a **finite local theorem with an elementary proof** and a distinct, fully specified next obstruction at \((27,9)\). It does **not** exclude a 27-vertex directed-triangle-free 9-outregular graph. Independent mathematical review and novelty/prior-art audit remain pending. The [Caccetta–Häggkvist triangle problem](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture) remains open in general, and [wustep/maths](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md) reports earlier finite computational work. No originality claim is made for the local counting theorem.

## Theorem A: local degree and exact arc ceiling on nine vertices

Let \(H\) be a **loopless, oriented** digraph on nine vertices with **no directed 3-cycle**, and suppose every vertex has **outdegree at least two**.

1. Every vertex has indegree at most **four**.
2. There are **at most 29 arcs** in \(H\).
3. The bound **29 is sharp**.

**Proof.** Fix a vertex \(v\) of outdegree \(a\ge2\), indegree \(b\), and put \(A=N^+(v)\), \(B=N^-(v)\), \(C=V\setminus(\{v\}\cup A\cup B)\), so \(|C|=8-a-b\). There are no \(A\to B\) arcs (they would close a directed triangle through \(v\)), and no \(A\to v\) arcs (digons are excluded). Every \(u\in A\) sends at least two arcs into \(A\cup C\), hence

\[
2a\le e(A,A)+e(A,C)\le \binom{a}{2}+a(8-a-b),
\qquad\text{so}\qquad
\boxed{a+2b\le11.}\tag{1}
\]

Since \(a\ge2\), this already yields \(b\le4\).

We improve (1) to **\(a+2b\le10\)**. Equality at 11, with \(a\ge2\) and \(a+b\le8\), permits only \((a,b)=(3,4)\) or \((5,3)\).

- If \((a,b)=(3,4)\), then \(|C|=1\). The three vertices of \(A\) each need two outgoing arcs into \(A\cup C\). The upper bound is exactly \(\binom32+3|C|=6\), so equality forces every vertex of \(A\) to point to \(C\), and \(A\) to be a three-vertex tournament of minimum outdegree one. Such a tournament is a directed triangle, contradiction.
- If \((a,b)=(5,3)\), then \(C\) is empty. Every vertex of the five-vertex induced \(H[A]\) has internal outdegree at least two. This cannot occur: applying the same inequality to a triangle-free oriented graph on \(t=5\) with minimum outdegree two gives \(a'+2b'\le 2t-3-4=3\), hence every \(b'=0\), contradicting total outdegree at least ten.

Therefore **each** vertex of \(H\) satisfies \(a+2b\le10\). Let \(m=e(H)\). Sum over nine vertices and use \(\sum a=\sum b=m\):

\[
3m=\sum_{v\in V}(a_v+2b_v)\le90,
\qquad\text{so}\qquad m\le30.
\]

Suppose \(m=30\). All nine vertices must satisfy \(a+2b=10\), and the constraints \(a\ge2\), \(b\ge0\), \(a+b\le8\) allow exactly \((a,b)=(2,4),(4,3),(6,2)\).

**The pair \((6,2)\) is impossible.** It has \(|C|=0\), so its six outneighbors induce a triangle-free oriented digraph of minimum outdegree two. On six vertices the same inequality gives \(a'+2b'\le 2\cdot6-3-4=5\). Since \(a'\ge2\), every \(b'\le1\), contradicting average indegree at least two.

Consequently all nine vertices are of type \((2,4)\) or \((4,3)\). If \(x\) and \(y\) count these types, then \(x+y=9\) and \(2x+4y=30\), so **\(x=3,y=6\)**.

Choose one of the six vertices \(v\) of type \((4,3)\). It has four outneighbors \(A\) and **one** nonneighbor \(C=\{c\}\). Every vertex of \(A\) must have internal outdegree at least one (all of its other outgoing arcs can only go to \(c\)). A triangle-free oriented graph on four vertices with minimum outdegree at least one must be a directed 4-cycle: it contains a directed cycle, necessarily of length four, and either possible chord would create a directed triangle. Thus each vertex of \(A\) sends **exactly one** arc into \(A\), and at most one into \(\{c\}\). Every member of \(A\) therefore has total outdegree **two**, requiring at least **four** vertices of type \((2,4)\). But \(x=3\). Contradiction.

Hence \(m\le29\).

**Sharpness.** On vertices \(0,\ldots,6\), draw \(i\to i+1,i+2\pmod7\). This is triangle-free: each of three successive steps lies in \(\{1,2\}\), so their sum is between three and six, never seven. Add vertex 7 pointing to all of \(0,\ldots,6\), then vertex 8 pointing to all of \(0,\ldots,7\). Neither new source participates in a directed cycle. The resulting oriented digraph has minimum outdegree two and exactly \(14+7+8=\boxed{29}\) arcs. Its sorted outdegrees are \((2,2,2,2,2,2,2,7,8)\), and sorted indegrees are \((0,1,4,4,4,4,4,4,4)\). □

## Theorem B: nine vertices cannot have minimum outdegree three

Suppose instead every outdegree is at least three. The rooted argument above, now with three outgoing arcs required from each vertex of \(A\), yields

\[
a+2b\le 2\cdot9-3-2\cdot3=9.
\]

As \(a\ge3\), all indegrees satisfy \(b\le3\). But the average indegree is at least three, so **every** vertex has both indegree and outdegree exactly three.

Fix \(v\); its three outneighbors \(A\), three inneighbors \(B\), and two nonneighbors \(C\) obey \(e(A,A)+e(A,C)\ge3|A|=9\). Their total capacity is only \(\binom32+3\cdot2=9\). Equality forces every vertex of \(A\) to point to both vertices of \(C\) and \(A\) to be a tournament of minimum internal outdegree one, therefore a directed triangle. Contradiction. □

## Exact scope transported to (27,9)

Now **suppose hypothetically** that \(D\) is a loopless oriented, directed-triangle-free graph on **27** vertices with every outdegree **exactly nine**. Excess arcs in a minimum-outdegree-nine counterexample can be deleted to reach this form without introducing cycles.

For a vertex \(v\) with indegree \(b\), its nine outneighbors \(A\) have at most \(17-b\) nonneighbors outside \(A\cup B\cup\{v\}\). Every member of \(A\) therefore has internal outdegree at least \(9-(17-b)=b-8\). If \(b\ge11\), \(D[A]\) would have minimum outdegree at least **three**, contradicting Theorem B. Thus

\[
\boxed{d_D^-(v)\le10\quad\text{for every }v.}
\]

This yields a precise disjunction, **not a contradiction**: either all indegrees equal nine (the **regular branch**, not excluded here), or some vertex has indegree ten (the **irregular branch**).

At an indegree-ten vertex \(v\), set \(A=N^+(v)\), \(B=N^-(v)\), and \(C\) its nonneighbors. Then \((|A|,|B|,|C|)=(9,10,7)\), every internal outdegree in \(D[A]\) is at least two, and by Theorem A

\[
18\le m:=e(A,A)\le29,\qquad e(A,C)=81-m\ge52.
\]

Orientation on the \(9\times7\) cut and the global indegree ceiling of ten give

\[
e(C,A)\le m-18,\qquad e(B,C)+e(C,C)\le m-11.
\]

All seven \(C\)-vertices have outdegree nine, so

\[
\boxed{e(C,B)\ge63-(m-18)-(m-11)=92-2m\ge34.}\tag{2}
\]

At least \(\lceil34/7\rceil=5\) of the ten \(B\)-vertices receive an arc from \(C\). If \(a\in A\) has internal outdegree **two**, then \(a\) points to **all seven** members of \(C\) and cannot receive any arc from \(C\) or from those at least five \(B\)-vertices (such an arc creates \(a\to c\to b\to a\)). Theorem A gives \(d_A^-(a)\le4\), and therefore only

\[
d_D^-(a)\le1\text{ (from \(v\))}+4\text{ (from \(A\))}+5\text{ (from \(B\))}=\boxed{10}.
\]

**Crucial limitation:** the low-indegree set for \(r=9\) is \(\{u:d_D^-(u)\le8\}\). An upper bound of **ten** on these outneighbors does **not** put them in the low set. Even the sharp local nine-vertex graph has just **seven** vertices of outdegree two, whereas the [general degree-defect transfer lemma](DEGREE_DEFECT_TRANSFER.md) would require **eight low outneighbors per indegree-ten vertex** for automatic saturation. The (24,8) argument cannot simply be copied.

## Reproduction, checks, and next obligations

- [scripts/ch27_local.py](../scripts/ch27_local.py) verifies the local rooted degree-pair cases, the unique hypothetical 30-arc degree distribution, a real 29-arc witness, and the exact (27,9) high-root cut table.
- [tests/test_ch27_local.py](../tests/test_ch27_local.py) uses an independent adjacency-matrix triangle check; exhausts all **729** partial orientations on four vertices to validate the directed-4-cycle sublemma; checks negative controls for digons, directed triangles and malformed adjacency; and independently computes the pivot counts.
- CI replays the local integer witness. **It does not enumerate all nine-vertex graphs or prove the 27-vertex claim.** The mathematical proof is the preceding counting argument.

```sh
python3 scripts/ch27_local.py --check
python3 -m unittest discover -s tests -p 'test_ch27_local.py' -v
```

**Next mathematically decisive work:** (i) independently exclude the **nine-inregular** 27-vertex case or identify a sharper regular cross-cut; (ii) in the indegree-ten branch, improve the \(m\le29\) neighborhood information and refine \(C\to B\) / \(B\to A\) capacities until the ambient low-indegree conclusion is justified; (iii) seek outside mathematical review of both this local theorem and the earlier (24,8) proof before any publication or novelty claim. At present, the source-backed status remains **a sharp restricted lemma and a precisely characterized unproved gap**, not an advance in the full conjecture's resolved scope.
