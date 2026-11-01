# M073 — an equal-mass assortative two-block inequality with explicit margin

**2026-11-01 · Claim [#162](https://github.com/Svyable/100/issues/162) · X-M073-ASSORTATIVE2.**

**Status:** A self-contained author-derived *restricted continuum inequality* for the
specific 35-vertex/66-edge incidence graph H. The expansion is elementary and
closely related to classical high-temperature/Griffiths positivity arguments;
**global novelty and independent specialist review have not been established**.
This neither proves Sidorenko's conjecture nor challenges the claimed general
counterexample. It does not produce a finite host violating Sidorenko.

## The precise result

Let H be the bipartite incidence graph of the **22 pinned triples on 13 points**
in [the source table](../data/reference/sidorenko_faces.json),
with 35 vertices and 66 edges. Give two graphon blocks mass 1/2 each and
symmetric weights

\[
W=\begin{pmatrix}a&b\\b&c\end{pmatrix},\qquad 0\le a,b,c\le1,
\qquad a+c\ge2b.
\]

Put
\[
p=\frac{a+2b+c}{4},\qquad s=\frac{a-c}{4},\qquad
r=\frac{a-2b+c}{4}\ge0.
\]

**Proposition.** On the entire real-parameter cone above,

\[
\boxed{\ t(H,W)\ge p^{66}+204s^2p^{64}+33r^4p^{62}
                       +88r^6p^{60}\ge p^{66}.\ }
\]

Equality with \(p^{66}\) holds **if and only if** \(a=b=c\).
This includes nonmonotone cases \(b<\min(a,c)\) with \(a\ne c\),
which the previously merged [ordered-cone result](M073_MONOTONE_TWO_BLOCK.md)
does not cover. It also allows \(a\ne c\), which the previously merged
[balanced equal-diagonal result](M073_REGULAR2_CYCLE_MARGIN.md) does not cover.
The cone is *not* the PSD cone \(ac\ge b^2\); for example
\((a,b,c)=(1,1/2,0)\) lies on its boundary but has negative determinant.

## Proof — coefficient positivity for independent fair spins

Write independent Rademacher labels \(\sigma_v\in\{-1,+1\}\) at every
vertex of H. With the first block labeled +1, the edge weight is exactly

\[
W(\sigma_u,\sigma_v)=p+s\sigma_u+s\sigma_v+r\sigma_u\sigma_v.
\]

Expand the product over the 66 edges. On each edge choose exactly one
of four summands: \(p\), \(s\sigma_u\), \(s\sigma_v\), or
\(r\sigma_u\sigma_v\). Independence and symmetry of the spins imply
that the expectation of a chosen monomial is zero unless **every vertex
has an even total spin exponent**. Every surviving expectation is 1.

Suppose a surviving term chose the single-spin \(s\)-summand on \(k\)
edges and the two-spin \(r\)-summand on \(\ell\) edges. The total spin
exponent is \(k+2\ell\), which must be even, hence \(k\) is even.
Thus its coefficient \(p^{66-k-\ell}s^kr^\ell\) is **nonnegative**:
\(p\ge0\), \(r\ge0\), and \(s^k\ge0\). All surviving terms may be
retained or discarded independently to form rigorous lower bounds.

We retain four disjoint families of expansion terms:

1. The all-\(p\) choice, contributing \(p^{66}\).
2. Exactly two single-spin choices on distinct edges sharing their
   selected spin at one center vertex. These are the unordered wedges
   of H, contributing \(w(H)s^2p^{64}\), where
   \(w(H)=\sum_v\binom{d(v)}2=204\).
3. Exactly four two-spin choices on a simple four-cycle, contributing
   \(c_4(H)r^4p^{62}\), where \(c_4(H)=33\).
4. Exactly six two-spin choices on a simple six-cycle, contributing
   \(c_6(H)r^6p^{60}\), where \(c_6(H)=88\).

Every omitted surviving term is nonnegative. This proves the first
inequality, including zero weights by polynomial continuity.
The second follows by nonnegativity. If \(s\ne0\) and \(p>0\), the
wedge term is strictly positive. If \(s=0\) but \(r>0\), the four-cycle
term is strictly positive. If \(p=0\), nonnegative entries force
\(a=b=c=0\). Finally \(s=r=0\) is equivalent to \(a=b=c\), giving
exact equality. \(\square\)

The coefficient argument actually works for **any finite simple graph**
with an equal-mass two-block host on this cone; only the explicit wedge
and cycle coefficients above are specific to H. It is an application of
classical spin-expansion positivity, not a claimed new general principle.

## Source-specific coefficient audit

The point degrees are three 4s, six 5s and four 6s; the 22 face vertices
have degree 3. Thus
\[
w(H)=3\binom42+6\binom52+4\binom62+22\binom32
=18+60+60+66=\boxed{204}.
\]

Every point pair in the pinned skeleton occurs in exactly two faces;
its 33 edges give exactly 33 four-cycles. The skeleton has exactly 22
triangles; for each, four assignments of three distinct incident faces
give six-cycles, hence 88. These counts were established in the
[earlier dossier](M073_REGULAR2_CYCLE_MARGIN.md); the **new checker independently
recounts both cycle lengths by canonical graph DFS**, rather than trusting
those derived counts.

The first potentially negative coefficient outside the cone is the
\(s^2rp^{63}\) coefficient, equal to
\[
\sum_{uv\in E(H)}(d(u)-1)(d(v)-1)
=2\sum_{i\in I}d(i)(d(i)-1)=\boxed{552}.
\]
It counts paths of length three with the middle edge assigned the
\(r\)-summand and the two outer edges assigning the \(s\)-summand
to the middle vertices. This explains why the condition \(r\ge0\)
matters to the **termwise proof**. It does *not* imply that Sidorenko
fails when \(r<0\).

## Exact independent-path checks and adversarial control

Run from the repository root:

\`\`\`sh
python3 scripts/m073_assortative2.py --check
python3 -m unittest discover -s tests -p 'test_m073_assortative2.py' -v
python3 scripts/regen.py --check
\`\`\`

The exact checker pins the 22-triple table by a SHA-256 of its canonical
integer array, independently enumerates all 35 graph vertices and 66
incidences, counts wedges and simple four/six-cycles by DFS, and reduces
all \(2^{13}=8192\) point-label assignments to 372 integer profiles.
It tests 36 nonnegative integer triples \(A,B,C\in\{0,1,2,3\}\)
with \(A+C\ge2B\). These are regression tests, **not the proof of the
continuum**. Seven tests include a second, uncompressed 8192-assignment
exact-density calculation, source mutation rejection, input validation,
constant equality, and strict nonconstant cases.

For integer block weights \(A,B,C\) (with arbitrary common denominator
\(D>0\)), put \(P=A+2B+C\), \(S=A-C\), \(R=A-2B+C\). After integrating
the 22 face labels, let \(T\) be the integer sum over the 8192 point
labels of products of the 22 two-face-label sums. The exact, cleared-
denominator certificate is
\[
2^{97}T\ge P^{66}+204S^2P^{64}+33R^4P^{62}+88R^6P^{60}.
\]
No floating point enters this comparison.

**Outside-cone falsifier for the *enhanced bound*, not Sidorenko:**
for \((A,B,C)=(10,10,9)\), so \(R=-1\), the exact integer computation
finds
\[
2^{97}T>P^{66},\qquad
2^{97}T<P^{66}+204S^2P^{64}+33R^4P^{62}+88R^6P^{60}.
\]
The ordinary Sidorenko inequality remains **strictly satisfied** at
this rational host, while our stronger displayed margin is false if
its cone hypothesis is dropped. The checker and independent test path
both reproduce this negative control. There is no claim of a
counterexample to Sidorenko itself.

## Literature, boundary and next falsifier

- OpenAI, *A counterexample to Sidorenko's conjecture*, September 23, 2026,
  [source repository](https://github.com/openai/math/tree/main/preprints/A-counterexample-to-Sidorenkos-conjecture-September-23-2026),
  and its [pinned incidence table](../data/reference/sidorenko_faces.json).
  The external manuscript claims a finite host; this work does not verify it.
- Sidorenko, *Inequalities for Doubly Nonnegative Functions*, *Electronic
  Journal of Combinatorics* **28** (2021), P1.32,
  [DOI 10.37236/8947](https://doi.org/10.37236/8947).
  Nonnegative-spectrum inequalities are an active separate research program;
  our cone is not identical to PSD.
- Lovász, *Subgraph Densities in Signed Graphons and the Local
  Simonovits–Sidorenko Conjecture*, *EJC* **18** (2011), P127,
  [DOI 10.37236/614](https://doi.org/10.37236/614).
  Local inequalities around constant kernels are classical; our proof
  uses the exact equal-mass two-spin expansion instead.
- The [earlier M073 balanced/equal-diagonal dossier](M073_REGULAR2_CYCLE_MARGIN.md)
  used the classical even-subgraph high-temperature expansion;
  the [ordered-cone dossier](M073_MONOTONE_TWO_BLOCK.md) used classical
  Harris association. The present *assortative* cone is complementary,
  not a global two-block theorem.

**Next falsifier:** Attack the remaining equal-mass disassortative region
\(a+c<2b\) with \(a\ne c\), where the cubic \(552s^2r\) contribution
has negative sign. Seek a valid exact rational Sidorenko gap or a new
non-termwise inequality; then vary block masses. A counterexample to the
*enhanced bound* is not a counterexample to Sidorenko. Before any novelty
or independent-acceptance promotion, obtain external literature and proof
review by someone other than the author. No changes to \`data/solved.json\`,
conjecture evidence states or benchmark trial records.
