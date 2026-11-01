# Degree-defect saturation: a reusable graph-counting lemma

**2026-10-31.** This is a self-contained elementary counting argument extracted from the [CH (24,8) proof candidate](M074_IRREGULAR_24.md). Its proof is valid for arbitrary finite order and arbitrary positive outdegree; the current independent specialist review and novelty gates remain open for the CH application. No novelty is claimed for this counting observation.

## Precise statement

Let \(D=(V,E)\) be a finite **loopless simple directed graph** with *every*
vertex of outdegree exactly \(r\ge1\). Two-cycles are permitted. Suppose
every vertex has indegree **at most** \(r+1\). Set

\[
H=\{v:d^-(v)=r+1\},\qquad
L=\{v:d^-(v)<r\},\qquad
h=|H|,\quad \ell=|L|.
\]

Thus vertices outside \(H\cup L\) have indegree exactly \(r\).

### General transfer inequality

If every \(v\in H\) sends at least \(q\ge0\) arcs to **distinct** vertices of
\(L\), then

\[
\boxed{(q+1)h\ \le\ r\ell.}\tag{T1}
\]

**Proof.** Double-count all arcs. Outregularity gives
\(\sum_{v\in V}(d^-(v)-r)=0\). Every \(v\in H\) contributes \(+1\),
every vertex outside \(H\cup L\) contributes zero, and every \(v\in L\)
contributes a negative amount. Therefore

\[
\boxed{h=\sum_{v\in L}(r-d^-(v))\ge\ell.}\tag{T2}
\]

It also gives the *total* number of arcs whose destination lies in \(L\):

\[
\boxed{\sum_{v\in L}d^-(v)=r\ell-h.}\tag{T3}
\]

At least \(qh\) of those incoming arcs originate in \(H\), by hypothesis.
Hence \(qh\le r\ell-h\), proving (T1). □

### Saturation

If \(H\neq\varnothing\) and **every** vertex in \(H\) has at least
\(r-1\) outneighbors in \(L\), then all of the following hold:

1. **\(h=\ell\).**
2. **Every low vertex has indegree exactly \(r-1\)**, i.e. no low vertex
   has a deficit of two or more.
3. **Every incoming arc to \(L\) comes from \(H\)**: \(e(V\setminus H,L)=0\).
   In particular the subgraph induced by \(L\) contains **zero arcs**.
4. Every \(v\in H\) has **exactly** \(r-1\) outneighbors in \(L\).

**Proof.** Substitute \(q=r-1\) in (T1) to get \(h\le\ell\); (T2)
gives \(h\ge\ell\), hence equality. The \(\ell\) low vertices have
positive integer indegree deficits totaling \(h=\ell\), so each deficit
equals one. Thus (T3) equals \((r-1)\ell\). But the \(h=\ell\) high
vertices each send at least \(r-1\) arcs into \(L\), already accounting
for **all** arcs whose destination is in \(L\). No other incoming arc
exists, and no high vertex can contribute extra arcs. □

**Contrapositive useful in proof search:** If there is at least one
indegree-\((r+1)\) vertex and one can prove that the induced low set
\(L\) contains an arc, then **some high vertex has at most \(r-2\)
outneighbors in \(L\)**. If a separate local argument forces every
high vertex to have \(r-1\) or more low outneighbors, the graph cannot
exist.

The condition on **every** high vertex is indispensable. This is not
a result about a single favorable root without quantifying over all
indegree-\((r+1)\) roots.

## Transport to the CH (24,8) calculation

The local neighborhood argument in [M074_IRREGULAR_24.md](M074_IRREGULAR_24.md)
separately establishes the *hypothetical* facts needed to instantiate
the theorem:

- Deleting excess outgoing arcs leaves every outdegree \(r=8\);
  the eight-vertex local lemma bounds all indegrees by nine.
- The regular-case exclusion makes \(H\) nonempty.
- For **every** \(v\in H\), the exact local profile filter and
  three-cycle elimination force an outneighborhood consisting of one
  vertex of internal outdegree seven and seven vertices of internal
  outdegree two. Each of the seven has ambient indegree at most seven,
  so every high vertex sends at least \(r-1=7\) arcs into \(L\).
- Those same seven low outneighbors have **14 arcs between them**,
  all within \(L\).

Saturation gives \(e(L,L)=0\), contradicting the locally required 14.
This cleanly separates the **generic counting theorem** from the
CH-specific **local structural obligations**. The counting lemma does
not establish any of those obligations on its own.

## Independent finite controls and limits

[Exact checker](../scripts/degree_defect.py) validates the theorem's
hypotheses and computes every count from explicit directed edges.
An independent [test suite](../tests/test_degree_defect.py)
re-enumerates all **81** loopless 1-outregular digraphs on four vertices
and all **7,776** loopless 2-outregular digraphs on five vertices,
allowing digons. These are complete *small* sanity checks, not proof
of the general theorem; the proof is the algebra above.

The negative controls include a graph with two low-to-low arcs but
**without** high-to-low saturation; a saturated nonregular graph
attaining all equalities; and malformed graphs with excess indegree,
loops, repeated edges, or nonconstant outdegrees.

```sh
python3 scripts/degree_defect.py --check
python3 -m unittest discover -s tests -p 'test_degree_defect.py' -v
```

### Boundary

This elementary lemma neither proves a new unrestricted CH range nor
certifies the local eight-vertex lemma, the 95,095-profile pruning, or
the 24-vertex proof candidate. It is useful precisely because its
**assumptions and conclusion can be audited separately** and reused
in other directed-graph problems when the matching hypotheses arise.
