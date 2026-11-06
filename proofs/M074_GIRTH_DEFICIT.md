# M074 — sharp directed-girth edge deficit and a new (27,9) irregular-root filter

**Research record: 2026-11-01.** This note proves an exact extremal lemma for oriented graphs and applies it as a **necessary-condition filter** to the still-unresolved indegree-ten branch of the finite Caccetta–Häggkvist triangle problem at \(n,r\)=(27,9). The lemma is elementary; its possible prior appearance in the literature has not been excluded. The full finite case and the unrestricted conjecture are **not** proved; outside mathematical review remains pending. See the [EGRES formulation](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture).

## 1. A sharp extremal lemma for every directed girth

**Theorem (directed-girth missing-edge deficit).** Let \(G\) be a finite **oriented** graph with minimum outdegree at least one and directed girth at least \(g\), where \(g\ge4\). Writing \(n=|V(G)|\) and \(e=e(G)\), necessarily \(n\ge g\) and

\[
\boxed{e\le {n\choose2}-{g(g-3)\over2}.}
\tag{1}
\]

For every \(n\ge g\), equality is attainable with directed girth **exactly** \(g\).

**Proof.** A finite digraph of minimum outdegree at least one has a directed cycle: follow outgoing arcs indefinitely and take the first repeated vertex. Choose a directed cycle of *minimum* length \(\ell\); it has \(\ell\ge g\). This cycle has **no chord**. Indeed, a directed arc between two nonconsecutive vertices, whichever way it points, closes one of the two directed paths on the cycle into a strictly shorter directed cycle. Therefore the \(\ell\) cycle vertices span exactly its \(\ell\) cycle arcs, with all \(\binom\ell2-\ell=\ell(\ell-3)/2\) other unordered pairs absent. Since the graph is oriented, at most one arc can occupy any unordered pair. Thus

\[
{n\choose2}-e\ge {\ell(\ell-3)\over2}
\ge {g(g-3)\over2}.
\]

For sharpness, take a **chordless directed \(g\)-cycle**. Add the remaining \(n-g\) vertices one at a time as *sources*: each new vertex sends an arc to every older vertex. No newly added vertex lies on a directed cycle. The original cycle is still present, every original vertex retains outdegree one, and every unordered pair has an arc except the chords of the original cycle. Equality holds. □

For directed triangle avoidance, \(g=4\), this specializes to

\[
\boxed{\delta^+(G)\ge1,\quad C_3\text{-free},\quad
e(G)\le {n\choose2}-2.}\tag{2}
\]

This \(2\)-arc deficit is **sharp at every \(n\ge4\)**, not a guessed or asymptotic bound. The graph must be oriented; allowing digons invalidates the unordered-pair counting.

### Equality-case rigidity (new structural strengthening)

**Rigidity theorem.** Suppose \(g=4\), \(n\ge4\), \(\delta^+(G)\ge1\), and equality holds in (2):

\[
e(G)={n\choose2}-2.
\]

Then, up to an isomorphism, \(G\) consists of a chordless **directed four-cycle**, together with \(n-4\) vertices ordered transitively, each pointing to all four cycle vertices. In particular, the **entire internal outdegree multiset** is exactly

\[
\boxed{(n-1,n-2,\ldots,4,1,1,1,1).}
\tag{R}
\]

**Proof.** There are exactly two missing unordered pairs. A shortest directed cycle has length \(\ell\ge4\), and all its chords are missing; hence \(\ell(\ell-3)/2\le2\), forcing \(\ell=4\). Its two diagonals account for *all* missing pairs in the graph.

Write that directed cycle as \(c_0\to c_1\to c_2\to c_3\to c_0\). Every other vertex \(x\) is adjacent in exactly one direction to all four cycle vertices. To avoid the triangle \(c_i\to c_{i+1}\to x\to c_i\), the implication \(x\to c_i\Longrightarrow x\to c_{i+1}\) must hold for every index modulo four. Thus \(x\) either points to **all four** cycle vertices or receives from **all four**.

The vertices outside the cycle form a tournament without directed triangles; they therefore have a transitive order \(x_1\to x_2\to\cdots\to x_{n-4}\), with every earlier vertex pointing to every later one. The last vertex \(x_{n-4}\) has no outgoing arc to another outside vertex. Since \(\delta^+\ge1\), it must point to the four-cycle. If any earlier \(x_i\) instead received from the cycle, then for any \(c_j\) the arcs \(c_j\to x_i\to x_{n-4}\to c_j\) would form a directed triangle. All outside vertices must therefore point to the cycle. Their outdegrees, read in transitive order, are \(n-1,n-2,\ldots,4\); each cycle vertex retains outdegree one. The graph is the sharp construction already given. □

## 2. A new weighted high-floor subset inequality

Let \(H\) be an oriented triangle-free digraph on \(N\) vertices and let \(f_v\) be nonnegative *lower bounds* on its internal outdegrees. Sort them \(f_{(1)}\ge\cdots\ge f_{(N)}\). For a size \(s\ge4\), if

\[
f_{(s)}\ge N-s+1,
\]

then the induced subgraph on these \(s\) high-floor vertices has minimum internal outdegree at least one, because any vertex can send to at most \(N-s\) outside them. Applying (2) and counting their arcs to the complement proves the necessary inequality

\[
\boxed{\sum_{i=1}^{s}f_{(i)}
\le s(N-s)+{s\choose2}-2.}\tag{3}
\]

This improves the ordinary oriented-graph subset-capacity inequality by **two entire arcs**, but *only when the displayed minimum-outdegree premise is met*. No separate assumption on the actual induced graph is smuggled in.

## 3. Application to the (27,9) indegree-ten root

Use the partition from [the existing finite regular-branch analysis](M074_27_REGULAR.md) and [the ten-vertex B girth audit](M074_B_INTERNAL_GIRTH.md): in a hypothetical oriented triangle-free 27-vertex graph of outdegree exactly 9, an indegree-ten pivot \(v\) has \(A=N^+(v)\), \(B=N^-(v)\), and \(C\) of respective sizes 9,10,7.

Write \(\alpha(a)=d^+_A(a)\), \(m=\sum_A\alpha(a)\le29\), and \(k(b)=d^-_C(b)\). The necessary root cut is

\[
\sum_B k(b)\ge92-2m.
\]

For each \(b\in B\), put \(q(b)=|\{a\in A:\alpha(a)\ge k(b)+2\}|\) and \(f(b)=\max\{0,1+k(b)-q(b)\}\). These are proved lower bounds for \(d^+_B(b)\); see the linked root argument. In the hard \(z=4\) stratum (four vertices with \(k=0\)), apply (3) with \(N=10\). Whenever \(f_{(s)}\ge 11-s\) for \(4\le s\le10\), require

\[
\sum_{i=1}^s f_{(i)}\le {s(19-s)\over2}-2.
\tag{4}
\]

The previous [B-small-subset filters](M074_B_INTERNAL_GIRTH.md) left **295** relaxed sorted \(\alpha,k\) pairs. The new two-missing-edge bound excludes **152** of them (74 first fail at \(s=4\), 49 at \(s=5\), 29 at \(s=6\)), leaving **143**. These are exact *integer-profile counts*, not graphs.

**Extra equality test.** If equality holds in (4), every vertex of the selected high-floor set must have *exactly* its lower-bound internal outdegree, because their sum already exhausts the maximum possible internal arc count. The sorted internal lower-bound vector must therefore equal the rigid vector (R), with \(n=s\). This is a separate structural condition, strictly stronger than the total-arc inequality. Its nontrivial exclusions below occur for \(s=6\), where the rigid vector is \((5,4,1,1,1,1)\); e.g. required vector \((4,2,2,2,2,1)\) also sums to 13 but cannot occur.

### Independent C-cut combination

Let \(t=|\{a\in A:\alpha(a)=2\}|\). Each of these \(t\) vertices sends outgoing arcs to **all seven** members of \(C\); hence every \(c\in C\) has at least \(t\) incoming arcs from \(A\). Since every ambient indegree is at most ten, the induced graph \(D[C]\) has maximum indegree at most \(10-t\). For \(t\ge7\), the previously established [sharp seven-vertex lemma](M074_SEVEN_VERTEX_CAP.md) gives

\[
e(C,C)\le16.
\]

On the other hand, \(e(C,A)\le m-18\), and the seven C-vertices have exactly 63 outgoing arcs, so

\[
e(C,C)=63-\sum_B k(b)-e(C,A)
\ge81-m-\sum_Bk(b).
\]

Thus every \(t\ge7\) profile must also satisfy the **new combined necessary condition**

\[
\boxed{\sum_B k(b)\ge65-m.}\tag{5}
\]

Applying (5) **after** the new B-subset cut removes **15 more** relaxed pairs, leaving 128. Applying the equality-case rigidity test to these remaining pairs eliminates **25** more, all at \(s=6\), yielding **103** unexcluded necessary-profile pairs. A concrete survivor in this weakened arithmetic relaxation is

\[
\alpha=(2^7,7,8),\qquad
k=(0^4,5,5,6,6,7,7).
\]

It meets all the stated scalar inequalities, with \(m=29\), \(\sum k=36\), and \(e(C,C)\ge16\); **it is not a graph witness**. Crucially, the remaining 103 profiles have not been shown to realize valid incidences, let alone a complete 27-vertex counterexample.

## 4. Exact reproducibility and adversarial controls

Run from the repository root:

```sh
python3 scripts/ch27_girth_deficit.py --check
python3 -m unittest discover -s tests -p 'test_ch27_girth_deficit.py' -v
```

The checker recomputes all \(166\times924=153{,}384\) starting relaxed profiles, delegates the *previous* gates to their existing exact implementation, and applies (4) followed by (5). A separate histogram/adjacency-matrix test independently regenerates the 295 baseline, checks all 152+15+25 new exclusions and verifies exact small-graph sharpness on four and five vertices. **Negative control:** improperly weakening the two-missing-edge deficit to one **and disabling the equality test** leaves **191** profiles after the B and C cuts, instead of 103. Disabling both new B checks leaves **275** after the C cut alone. Disabling just equality-case rigidity leaves **128**.

The general lemmas are elementary universal statements, but the reduction from 295 to 103 is only an exact computation over relaxed ten-vertex degree profiles. Neither is an unrestricted Caccetta–Häggkvist proof. No novelty or external acceptance claim is made; expert inspection of proof, enumeration, and prior literature remains essential.
