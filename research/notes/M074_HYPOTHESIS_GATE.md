# M074 — nonvacuity filter for a proposed degree-transfer lemma

**Candidate only. Not proved, not refuted, not a novel theorem.**
The suggested extrapolation from the exact \((24,8)\) regular-case work was:

> If an oriented, directed-triangle-free graph on \(3r\) vertices has
> outdegree exactly \(r\) at every vertex, and \(d^-(v)=r+1\),
> then some \(u\in N^+(v)\) has \(d^-(u)\le r-1\).

The exact \((24,8)\) dossier proves this *conditional consequence* for
\(r=8\) in an irregular possible-counterexample configuration.
**Do not claim it for general \(r\) based on the \(r=8\) argument.**

## Why naïve finite testing is a weak research program

The hypotheses already describe a potential counterexample to the
directed-triangle special case of Caccetta–Häggkvist: on \(3r\) vertices,
minimum outdegree \(r\) is conjectured to force a triangle (or digon).
If the conjecture is true, **no graph satisfying the antecedent exists**.
Consequently verifying the proposed implication in finite parameter
ranges already ruled out by known theorems is *vacuous*. It teaches
nothing about transfer of the local degree argument.

**Better obligation:** isolate a nonvacuous local neighborhood inequality
with hypotheses that actually occur in oriented triangle-free graphs,
then test whether it supplies a new bound in the irregular branch.

For example, in *any* oriented, triangle-free digraph with \(n\) vertices
and minimum outdegree \(\delta\), choose a vertex with outdegree \(a\)
and indegree \(b\). Its \(a\) outneighbors cannot send arcs to the root
or its \(b\) inneighbors. Thus each outneighbor sends at least

\[
\max(0,\,\delta-(n-1-a-b))
\]

arcs within the root's outneighborhood. This is an elementary existing
counting observation, not a new CH theorem. Unlike the previous
whole-graph antecedent it is meaningful on genuine triangle-free
examples, including the eight-vertex 21-arc sharp construction in
[M074_ELEMENTARY_24_REGULAR.md](M074_ELEMENTARY_24_REGULAR.md).

### Promotion gate

Before spending significant proof-search budget on any proposed
\(r\)-generalization, require (a) a nonvacuous statement on a
specified *existing* class; (b) a counterexample search on the
weaker local hypotheses; (c) explicit derivation from admissible
premises; and (d) a prior-art check against regular-digraph
Caccetta–Häggkvist literature.

Nothing here alters the unrestricted M074 status or its Solved archive.
