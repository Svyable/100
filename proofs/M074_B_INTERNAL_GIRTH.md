# M074 — small-subset girth obstruction in the (27,9) irregular branch

**2026-10-31.** A restricted, author-derived *necessary condition* for hypothetical counterexamples in the (27,9) directed-triangle case of Caccetta–Häggkvist. Independent specialist review remains pending. The full minimum-outdegree-nine finite problem and the unrestricted conjecture are not resolved.

## Exact small-subset lemma

Let \(G\) be an oriented, directed-triangle-free digraph on ten vertices. For each vertex \(b\), let \(f_b\) be any integer lower bound on its outdegree **inside \(G\)**. Sort the ten bounds in descending order, \(f_{(1)}\ge\cdots\ge f_{(10)}\).

**Lemma.** The following inequalities are necessary:

\[
f_{(3)}\le7,\qquad f_{(4)}\le7,\qquad f_{(5)}\le6,\qquad f_{(6)}\le5.
\]

(The fourth-vertex bound follows already from the three-vertex bound, but records the separate six-vertex-family criterion.)

**Proof.** For any subset \(S\subseteq V(G)\) of size \(s\), each \(b\in S\) has at most \(10-s\) outneighbors outside \(S\). Hence
\[
d^+_{G[S]}(b)\ \ge\ f_b-(10-s).
\]
If \(s=3\) and its three vertices all have \(f_b\ge8\), then all three have at least one internal outneighbor; on three vertices this forces a directed triangle. Thus \(f_{(3)}\le7\).

For \(s\in\{4,5,6\}\), if the top \(s\) bounds are all at least \(12-s\), every member of the induced \(s\)-vertex digraph has at least **two** internal outneighbors. A directed-triangle-free oriented graph on at most six vertices cannot have minimum outdegree two: the [six-vertex obstruction](../research/M074_ELEMENTARY_18.md) proves the six-vertex case; for smaller orders the same rooted inequality
\[
a+2b\le2s-7\le5
\]
contradicts a vertex with \(a,b\ge2\) (which exists because average indegree is at least two). Therefore the thresholds \(f_{(4)}\ge8\), \(f_{(5)}\ge7\), and \(f_{(6)}\ge6\) are all impossible. QED.

This **is stronger than** the familiar total-arc subset capacities
\[
\sum_{i=1}^s f_{(i)}\le {s\choose2}+s(10-s)=\frac{s(19-s)}2.
\]
For example, three floors of eight have total 24, *equal* to the allowed capacity for \(s=3\), but their individual internal minimum-outdegree-one requirements would force a forbidden three-cycle.

## Application to an indegree-ten pivot

Continue the notation of [the (27,9) regular-branch proof](M074_27_REGULAR.md): a hypothetical 27-vertex oriented, triangle-free graph has outdegree exactly nine, global indegrees at most ten, and a vertex \(v\) with indegree ten. Let \(A=N^+(v)\) (nine vertices), \(B=N^-(v)\) (ten vertices), and \(C\) the seven nonneighbors.

Write \(\alpha(a)=d_A^+(a)\), \(m=\sum\alpha(a)\le29\), and \(k(b)=d^-_C(b)\) with \(0\le k(b)\le7\). The root cut gives
\[
\sum_{b\in B} k(b)\ge92-2m.
\]
A directed edge \(b\to a\) with \(b\in B\), \(a\in A\), requires \(\alpha(a)\ge k(b)+2\), otherwise an \(a\to c\to b\to a\) triangle appears. Put \(q(b)=|\{a\in A:\alpha(a)\ge k(b)+2\}|\). Since \(b\) sends one edge to \(v\), at most \(q(b)\) to \(A\), and at most \(7-k(b)\) to \(C\),
\[
d_B^+(b)\ge f(b)=\max\{0,1+k(b)-q(b)\}.
\]

The lemma applies **to these floors**, not merely to actual \(B\)-degrees. It rules out additional integer profiles that pass total subset capacities; it does **not** by itself exclude the entire indegree-ten branch.

### Auditable \(z=4\) frontier

Restrict to \(z=|\{b\in B:k(b)=0\}|=4\), the most difficult presently isolated zero-\(k\) boundary. [The checker](../scripts/ch27_b_internal.py) enumerates all sorted \(\alpha\) arrays in \([2,8]^9\) with \(\sum\alpha\le29\), and all sorted \(k\) arrays with exactly four zeros and six positive entries in \([1,7]\). These are **relaxed integer necessary conditions**, not ten- or twenty-seven-vertex graph realizations.

| Sequential filter | Number of profile pairs |
|---|---:|
| Total relaxed pairs | 153,384 |
| Fail the \(C\to B\) root cut | 149,396 |
| Fail standard \(B\)-subset total-arc capacity | 3,515 |
| Fail the new three-vertex girth test | 132 |
| Fail the five-vertex minimum-outdegree-two test | 22 |
| Fail the six-vertex minimum-outdegree-two test | 24 |
| **Unexcluded relaxed pairs** | **295** |

The four-vertex minimum-outdegree-two test adds no separate exclusions after the stronger three-vertex test. These are *sequential* filters, not disjoint graph types.

A previous relaxed profile from the parallel seven-vertex investigation,
\[
\alpha=(2^7,6,8),\quad
k=(0^4,4,5,6,7^3),
\]
passes the aggregate \(B\) arc-capacity checks, but the three vertices with \(k=7\) have \(q=0\) and hence each have at least eight outgoing neighbors *inside* \(B\). The three-vertex girth lemma rules it out. This is a different obstruction from the [seven-vertex \(C\)-cut analysis under PR #97](https://github.com/Svyable/100/pull/97).

An explicit **unexcluded relaxed pair** remains:
\[
\alpha=(2^7,6,8),\qquad k=(0^4,4,6,6,6,7,7).
\]
It meets the root cut, the total subset capacities and the new small-subset restrictions. It is *not* a constructed digraph and does not establish incidence feasibility.

## Reproduction and falsification

From the repository root:

    python3 scripts/ch27_b_internal.py
    python3 -m unittest discover -s tests -p 'test_ch27_b_internal.py' -v

The unit tests independently produce both histogram families using compositions rather than sorted-tuple combinations; recompute eligibility floors; verify the exact exclusions and a surviving **integer** negative control; and deliberately remove the three-vertex test, restoring 132 relaxed survivors (427 instead of 295). This mutation detects loss of the new obstruction.

**Next falsifier:** combine the \(B\)-subset girth bounds with the separately derived sharp seven-vertex \(C\)-cut and incidence constraints, *then* attempt exact rooted graph-level SAT or a more substantial elementary transfer. Require independently checked proof traces for any solver-based exclusion. Do not change the M074 conjecture registry or \`data/solved.json\`, and obtain independent specialist review before asserting broader theorems.
