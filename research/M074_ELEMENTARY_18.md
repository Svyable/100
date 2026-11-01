# M074 — a certificate-free exclusion of the (18,6) directed-triangle case

**Dated:** 2026-10-31. **Scope:** exact finite theorem only, not the Caccetta–Häggkvist conjecture for all parameters or the fixed-r=6 assertion at all orders. **Novelty is not claimed:** a prior independent project reports a DRAT-certified (18,6) result.

## Theorem

Every loopless digraph on 18 vertices with minimum outdegree at least 6 contains a directed cycle of length at most 3.

**Reduction.** A counterexample contains neither digons nor directed triangles, so it is an oriented graph. Delete excess outgoing arcs independently at each vertex until every outdegree is exactly 6. Deletion creates no cycles, so it suffices to rule out triangle-free oriented graphs of outdegree exactly 6 on 18 vertices.

## Lemma 1 (six-vertex obstruction)

There is no triangle-free oriented graph on six vertices with minimum outdegree at least two.

**Proof.** Such a graph has at least 12 arcs, so some vertex $v$ has indegree $b\ge2$. Let $a=d^+(v)\ge2$, $A=N^+(v)$, $B=N^-(v)$ and $C$ be the remaining $5-a-b$ vertices. No arc can go from $A$ to $B$ (it would complete a directed triangle through $v$), or from $A$ to $v$ (it would be a digon). Each vertex of $A$ needs at least two outgoing arcs into $A\cup C$. Since the graph is oriented,

$2a\le e(A,A)+e(A,C)\le a(a-1)/2+a(5-a-b)$,

which rearranges to $a+2b\le5$. This contradicts $a\ge2$ and $b\ge2$. QED.

## Lemma 2 (18-vertex regularity)

Any triangle-free oriented graph on 18 vertices with all outdegrees six has all indegrees six.

**Proof.** For any vertex $v$, let $A=N^+(v)$ have size six, let $b=d^-(v)$, and let $C$ be the remaining $11-b$ vertices. If $b\ge7$, then $|C|\le4$. Every $a\in A$ sends six arcs only into $A\cup C$, so at least two must remain inside $A$. This contradicts Lemma 1. All indegrees are thus at most six. Since the average indegree equals the fixed outdegree six, every indegree equals six. QED.

## Lemma 3 (saturated-pivot obstruction, general form)

Let $D$ be triangle-free and oriented on $3r$ vertices, with every vertex having both indegree and outdegree exactly $r$. For any vertex $v$, the induced subgraph on its outneighbors $A=N^+(v)$ has minimum internal outdegree **at least two**. Dually, the subgraph on its inneighbors has minimum internal indegree at least two.

**Proof.** Set $B=N^-(v)$ and $C=V\setminus(A\cup B\cup\{v\})$. Then $|A|=|B|=r$ and $|C|=r-1$. Each $a\in A$ must send all its $r$ outgoing arcs into $A\cup C$; it therefore has at least one outneighbor within $A$.

Suppose $a$ has exactly one such neighbor $a'$. Then $a$ sends arcs to **every** vertex of $C$. Each $b\in B$ has indegree $r$, with no incoming arc from $v$ or $A$ and at most $r-1$ possible incoming arcs from $B$. Hence some $c\in C$ satisfies $c\to b$. An arc $b\to a$ would create the forbidden triangle $a\to c\to b\to a$. Thus no $b\in B$ sends an arc to $a$. No $c\in C$ sends an arc to $a$ either, because $a\to C$ and digons are forbidden. Consequently $a$ can receive arcs only from $v$ and from $A\setminus\{a,a'\}$: at most $1+(r-2)=r-1$ arcs. This contradicts $d^-(a)=r$. So every $a\in A$ has at least two outneighbors within $A$. Reversing arcs gives the dual statement. QED.

## Proof of the finite theorem

Assume a counterexample exists. Reduce to exact outdegree six, and use Lemma 2 to obtain exact indegree six. For any vertex $v$, Lemma 3 with $r=6$ forces its six-vertex outneighborhood to have minimum internal outdegree at least two. Lemma 1 rules that out. Contradiction. QED.

The same pivot argument supplies a **necessary** neighborhood condition at order $3r$ for regular candidates of any $r$; it is not an all-$r$ CH proof. In particular, at $r\ge7$, a triangle-free oriented neighborhood of order $r$ may have minimum outdegree two.

## Independent check

Run `python3 scripts/ch_six_check.py` and `python3 -m unittest discover -s tests -p 'test_ch_elementary.py' -v`. The checker independently enumerates all partial orientations of the 15 pairs of $K_6$ with conservative triangle and degree pruning, visiting 42,002 nodes, rejecting 20,164 triangle branches and 63,841 degree-impossible branches, and finds no witness. A negative control tests the triangle-free directed circulant on seven vertices with step set {1,2} and minimum outdegree two. This computation certifies only Lemma 1; Lemmas 2–3 are the explicit mathematical arguments above, **not** a machine-check of all graphs on 18 vertices.

## Provenance and evidence boundary

- Earlier repository work: [regularity and rooted-pivot derivations](M074_REGULARITY.md). The new step is the universal **B-to-pivot exclusion** and ensuing indegree contradiction; it replaces the formerly open SAT branch with a direct finite proof.
- Independent earlier computational result: [wustep/maths, directed triangle investigation](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md) reports DRAT-verified indegree partitions at (18,6). We **do not claim novelty** or independent reproduction of those external proof files.
- Separate wider unreviewed claim: [joshp123's fixed-r=6 manuscript](https://github.com/joshp123/solve-a-maths-problem-dont-care-which-make-no-mistakes). Its full scope is not established here.
- Published context: [Hladký–Král’–Norine, Combinatorica (2017)](https://doi.org/10.1007/s00493-015-2662-5) gives a directed-triangle threshold of 0.3465n; that bound alone does not exclude n=18, r=6.

**Acceptance gate:** Seek independent specialist review before describing the elementary argument as an externally accepted or new restricted theorem. Do not change M074's full-conjecture evidence state, promote it to Solved, or treat this as proof for all orders with r=6. The existing exact CNF artifacts remain frozen as independent verification targets.
