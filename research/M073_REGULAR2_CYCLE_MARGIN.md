# M073: a quantitative Sidorenko margin on an entire graphon subfamily

**Claim [#123](https://github.com/Svyable/100/issues/123), November 1, 2026.**

This note proves a bounded, author-derived mathematical statement, not merely
checks finitely many hosts. Its underlying even-subgraph identity is the
**classical high-temperature expansion** of the Ising model, not our
invention; see [Friedli–Velenik, *The Ising Model*, Section 3.5,
equation (3.45)](https://www.unige.ch/math/folks/velenik/smbook/Ising_Model.pdf).
The *specific numeric margin* and special graph coefficient counts below
were independently derived in this project. Their global novelty and the
argument's specialist acceptance **have not been established**.

The graph \(H\) is exactly the 35-vertex, 66-edge incidence graph of the
22 triples on 13 points from the September 2026
[OpenAI Sidorenko preprint](https://github.com/openai/math/tree/main/preprints/A-counterexample-to-Sidorenkos-conjecture-September-23-2026).
Its exact triple table is frozen, source-identified and SHA-256 checked at
[data/reference/sidorenko_faces.json](../data/reference/sidorenko_faces.json).
The manuscript claims an existential finite host violating Sidorenko; the
independent finite-host witness gate in this repository remains **open**.

**Independent complementary extension:** [M073_MONOTONE_TWO_BLOCK.md](M073_MONOTONE_TWO_BLOCK.md) proves a quantitative
real-parameter inequality for all ordered asymmetric two-block graphons with
*arbitrary* class masses. Neither theorem covers the entire nonmonotone two-block
region; the classical method and independent novelty boundary remain explicit.

## Exact statement

**Proposition (balanced, equal-diagonal, two-step graphons).** Let
\(a,b\in[0,1]\) and let \(W\) be the symmetric graphon on two measurable
classes of measure \(1/2\) each, having block matrix

\[
W=\begin{pmatrix}a&b\\b&a\end{pmatrix}.
\]

For \(p=(a+b)/2>0\) and \(r=(a-b)/(a+b)\), the fixed graph \(H\) satisfies

\[
\boxed{
t(H,W)\ \ge\ p^{66}\big(1+33r^4+88r^6\big)
\ \ge\ p^{66}.
}
\]

The first inequality is **strict when \(a\ne b\)**. Equality in either
inequality holds exactly when \(a=b\), including the separate
\(p=0\) case \(a=b=0\), when both sides vanish. No restriction on
\(a,b\) to rational values or a finite test grid is needed.

The same *method*, for every finite bipartite graph \(F\) with \(m\)
edges and \(c_4,c_6\) simple cycles of lengths four and six, proves

\[
t(F,W) \ge p^m(1+c_4r^4+c_6r^6).
\]

This general inequality is a straightforward application of the known
even-subgraph identity; **do not treat it as an independently novel theorem**.
Our application computes the previously unrecorded-in-this-project
coefficients \((c_4,c_6)=(33,88)\) for the source-pinned \(H\).

## Proof

Write independent block labels as Rademacher variables
\(\sigma_v\in\{-1,+1\}\). Then
\(W(\sigma_u,\sigma_v)=p(1+r\sigma_u\sigma_v)\), and
by expanding one factor per edge,

\[
\frac{t(F,W)}{p^m}
=\mathbb{E}\prod_{uv\in E(F)}(1+r\sigma_u\sigma_v)
=\sum_{S\subseteq E(F)} r^{|S|}
 \prod_{v\in V(F)}\mathbb E[\sigma_v^{\deg_S(v)}]
=\sum_{\substack{S\subseteq E(F)\\
  \deg_S(v)\equiv0\ (\mathrm{mod}\ 2)\,\forall v}}
 r^{|S|}. \tag{1}
\]

The expectation vanishes if any selected degree is odd; otherwise it is
one. **For bipartite \(F\)**, with color class \(L\), an even-degree
edge subset satisfies
\(|S|=\sum_{v\in L}\deg_S(v)\equiv0\pmod2\).
Thus all surviving powers of \(r\) are even and **nonnegative** even
when \(r<0\). The empty subset supplies 1. In a simple bipartite
graph, a nonempty Eulerian subgraph with four edges is exactly a
four-cycle; with six edges it is exactly a six-cycle (there are no
two-cycles or odd cycles). Keeping just those terms gives the
general inequality.

We now derive the **exact source-specific coefficients** without invoking
a numerical graphon search. Define the *point skeleton* \(K\) on 13 points:
two points are adjacent if they occur together in a listed triple.
An explicit finite audit of the pinned 22 triples yields:

1. \(K\) has **33 edges**, and each skeleton edge lies in **exactly
   two** listed triples.
2. \(K\) has **exactly 22 triangles**; they are precisely the
   22 listed triples (there are no additional triangles).
   This checks all \(\binom{13}{3}=286\) point triples.

Every four-cycle of the incidence graph is specified by a skeleton edge
and the two distinct incident face vertices. Therefore
\(c_4=33\).

Every six-cycle is specified by three point vertices \(u,v,w\)
forming a skeleton triangle, together with **three distinct** face
vertices, one containing each of \(uv,vw,wu\).
There are two possible faces for each of the triangle's three edges.
One choice is the common triangle face, the other its distinct neighboring
face. Of the \(2^3=8\) assignments, exactly **four** select the common
face zero or one times; these and only these give three distinct face
vertices. (The neighboring faces are mutually distinct, because no
other listed triple contains all three points.)
Hence \(c_6=22\times4=88\).

The empty, four-edge, and six-edge Eulerian subsets contribute
\(1+33r^4+88r^6\) in (1). Every omitted term is nonnegative.
As \(c_4>0\), the inequality is strict for \(r\ne0\), equivalently
\(a\ne b\). For \(p=0\), both block probabilities are zero and
\(t(H,W)=0\). This completes the proof.

## Adversarial controls and exact replay

The two coefficient counts are independently checked with:

- a **point-triple combinatorial census** and the 22-triangle skeleton
  structural audit; and
- a **different DFS on the entire 35-vertex incidence graph** that
  counts unoriented simple cycles once via canonical traversal.

The exact \(25\)-point rational subgrid \(a,b\in
\{0,1/4,1/2,3/4,1\}\) is separately checked via integer homomorphism
densities from the existing M073 face-elimination engine; four cases use
its independent 66-edge factor-elimination engine too. These samples
are regressions **not the proof of the continuum statement**.

Additional tests directly enumerate *all even edge subsets* of small
graphs and compare the spin sum to exact pairwise graphon factors.
A deliberately **nonbipartite** triangle with cross-only weights has
\(t(K_3,W)=0<p^3\): dropping the bipartiteness step would make a
false argument. Boolean weights, invalid probabilities, and a mutated
source table fail closed. The incidence graph is independently verified
connected, and its cycle-space rank \(66-35+1=32\) gives an endpoint
checksum: at \(|r|=1\), the full even-subgraph polynomial evaluates
to \(2^{32}\). This checksum **does not claim** that all \(2^{32}\)
Eulerian subsets were individually enumerated.

Run from repository root:

```sh
python3 scripts/sidorenko_regular2.py --check
python3 -m unittest discover -s tests -p 'test_sidorenko_regular2.py' -v
python3 scripts/sidorenko_twoblock.py --check
python3 scripts/verify_claim_witnesses.py --check
python3 scripts/regen.py --check
```

## Evidence boundary and next falsifier

This excludes the entire **equal-mass, equal-diagonal two-step graphon**
subfamily as a source of the claimed M073 counterexample. It does *not*
exclude unequal diagonal entries, unequal class masses, three-plus
blocks, arbitrary graphons or finite simple hosts in general. It does
not prove that Sidorenko's conjecture holds, nor refute the September
2026 alleged counterexample.

**Next:** Attack the missing symmetry assumptions by testing
\(a\ne c\) and unequal masses, or derive a higher-block exact rational
negative witness and then a finite host. Preserve the fixed incidence
pattern, exact normalization and a second independent density check.
Prior-art audit of the specific quantitative bound and specialist
review of this proof remain required before claiming a novel
published mathematical result or changing the Solved/evidence ledgers.

Related: [first 27-cell audit](M073_TWOBLOCK_EXACT.md),
[finite-witness gap](M071_M073_WITNESSES.md), [claim #123](https://github.com/Svyable/100/issues/123).
