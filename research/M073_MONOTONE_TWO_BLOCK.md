# M073: an unequal-mass, unequal-diagonal Sidorenko margin on an ordered cone

**November 1, 2026.** Scoped mathematical note under
[claim #151](https://github.com/Svyable/100/issues/151), building on the
already merged [regular two-block proof](M073_REGULAR2_CYCLE_MARGIN.md).
This note proves a real-parameter inequality, not just 85 sampled cases.
**Originality and specialist independent review remain unverified.**
The main mathematical input is the classical
[Harris–FKG positive-association theorem for independent coordinates
(Grimmett, *Probability on Graphs*, §4.2)](https://www.statslab.cam.ac.uk/~grg1000/books/pgs-cup1.pdf).
The adjacent-edge pairing has a classical line-graph interpretation;
the existence of perfect matchings for connected even-order claw-free
graphs is due to Sumner / Las Vergnas, independently of this project.
Here we give an **explicit, smaller constructive certificate** rather
than appealing to that theorem.

The fixed pattern is the exact 35-vertex, 66-edge **bipartite** incidence
graph \(H\) of the 22 triples on 13 points from the 2026 OpenAI
Sidorenko manuscript, with a pinned source table at
[data/reference/sidorenko_faces.json](../data/reference/sidorenko_faces.json).
The external manuscript's general/finite host claim remains a different,
unreviewed question, not settled here.

## Proposition — arbitrary block masses, ordered 2×2 weights

Let \(a,b,c,q\in[0,1]\). Give the first of two vertex blocks mass
\(q\) and the other mass \(1-q\), and let their symmetric edge-weight
matrix be

\[
W=\begin{pmatrix}a&b\\b&c\end{pmatrix}.
\]

Assume either \(a\ge b\ge c\) or \(c\ge b\ge a\)
(**the ordered/monotone cone**, inclusive of its boundary).
Put

\[
\begin{aligned}
d_0&=qa+(1-q)b, & d_1&=qb+(1-q)c,\\
p&=qd_0+(1-q)d_1
  =q^2a+2q(1-q)b+(1-q)^2c,\\
V&=q(1-q)(d_0-d_1)^2
  =q(1-q)\left[q(a-b)+(1-q)(b-c)\right]^2.
\end{aligned}
\]

Then

\[
\boxed{\qquad t(H,W)\ \ge\ (p^2+V)^{33}\ \ge\ p^{66}.\qquad} \tag{1}
\]

Both inequalities are **strict if \(0<q<1\) and \(a\ne c\)**.
Equality holds when \(q\in\{0,1\}\) or \(a=b=c\).
This includes sparse and zero graphons, and makes *no* equal-diagonal
(\(a=c\)) or equal-mass (\(q=1/2\)) assumption.

This is a **newly derived application in this repository** of standard
positive association to a source-specific edge-pair certificate.
It should not be advertised as an independently novel general theorem.
For any graph with an adjacent pairing of its \(2k\) edges, exactly
the same argument yields \(t(F,W)\ge(p^2+V)^k\) on the ordered cone.
Consequently, the method is not exclusive to \(H\); its role here is
to establish a specific quantitative exclusion within the active
counterexample search.

## Proof

**Part A: 66 exact edges can be partitioned into 33 wedges.**
For each of the source's face triples \(f_j\) make edges
\((i,13+j)\) for its three points \(i\). The resulting
66-edge graph is connected. The committed
[33-wedge cover](../data/reference/m073_wedge_cover.json) partitions
those 66 distinct edges into 33 pairs, each pair sharing a center
vertex. It is independently validated against the separately pinned
face table: every source edge occurs **once and only once**, and each
wedge's two edges meet its declared center.

The cover is not guessed: a deterministic **postorder spanning-tree
construction** independently regenerates the same 33 groups.
Root the connected graph, visit all nonroot vertices in reverse
breadth-first order, and at each vertex pair all still-free incident
edges except the parent edge. If their number is odd, include the
reserved parent edge. The root necessarily has even residual degree
because the graph started with an even number of edges and every
previous step consumed pairs. Thus no edge remains unmatched.
The source JSON and algorithm also receive independent tampering tests.

**Part B: positive association with no appeal to bipartiteness.**
Give each vertex of \(H\) an *independent* block label \(X_v\),
with \(\Pr(X_v=0)=q\). If \(a\ge b\ge c\), every edge function
\(W(X_u,X_v)\) is coordinatewise nonincreasing in the labels
\(0<1\); if \(c\ge b\ge a\), it is nondecreasing. Each wedge
factor is the product of two nonnegative edge functions and is
therefore coordinatewise monotone in **the same direction**.
Harris's product-measure inequality applies to the 33 wedge
factors \(G_1,\ldots,G_{33}\):

\[
t(H,W)=\mathbb{E}\prod_{j=1}^{33}G_j
\ge \prod_{j=1}^{33}\mathbb{E}G_j.
\]

Within wedge \((xy,xz)\), conditioning on its center label \(X_x\)
makes \(X_y,X_z\) independent, whence

\[
\mathbb{E}G_j
=\mathbb{E}[d(X_x)^2]
=p^2+\operatorname{Var}(d(X_x))
=p^2+q(1-q)(d_0-d_1)^2.
\]

Multiplication proves both non-strict inequalities in (1).

**Part C: strictness.** The first two explicitly checked wedges
have center vertex \(0\) and edge pairs
\(\{(0,13),(0,14)\}\) and
\(\{(0,15),(0,16)\}\). Their four leaf vertices are all
distinct. Group these two wedges as one monotone factor, then
apply Harris to that factor and the other 31 wedge factors.
The grouped pair has expectation
\(\mathbb{E}d(X_0)^4\), strictly exceeding
\((\mathbb{E}d(X_0)^2)^2\) when
\(0<q<1\) and \(d_0\ne d_1\).
Indeed the difference equals
\(q(1-q)(d_0^2-d_1^2)^2\).
Ordered nonnegative \(a,b,c\) imply \(d_0\ne d_1\) exactly when
\(a\ne c\), because
\(d_0-d_1=q(a-b)+(1-q)(b-c)\), whose summands have the same
sign. The strict inequality follows. When \(q=0,1\), the support
has only one class; when \(a=b=c\), the graphon is constant.
Both yield equality. \(\square\)

## Exact machine audit and independent falsifiers

The fixed pattern is SHA-256 pinned in
[data/reference/sidorenko_faces.json](../data/reference/sidorenko_faces.json).
The separate JSON wedge-cover witness is **not** the sole authority:
the independent validation route checks its 66-edge multiset, centers,
distinctness and source hash; the other route constructs it afresh
from a rooted graph traversal. Tests alter the witness by deleting,
repeating, reversing and changing edges and centers, and require
fail-closed behavior.

For a *rational* graphon use integer mass numerators
\(q=P/Q\) and integer edge entries \(a/D,b/D,c/D\).
The independent face-based evaluator returns \(T\) such that

\[
t(H,W)=\frac{T}{Q^{35}D^{66}}.
\]

Writing

\[
B=P\big(Pa+(Q-P)b\big)^2+
(Q-P)\big(Pb+(Q-P)c\big)^2,
\]

the **exact cleared-denominator test** is
\(TQ^{64}\ge B^{33}\). This is integer arithmetic; no
floating-point comparison or graph sampling. The identity
\(BQ=(P^2a+2P(Q-P)b+(Q-P)^2c)^2
 +P(Q-P)[P(a-b)+(Q-P)(b-c)]^2\)
separately checks the covariance normalization.

The checker replays **85** preregistered test cases across all
ordered triples \(a,b,c\in\{0,1/2,1\}\) and five rational
masses \(q\in\{0,1/3,1/2,2/3,1\}\), including the zero
and constant boundaries. Four of those cases are independently
recounted via **35-variable pairwise-edge factor elimination**,
rather than the face-based 13-point summation. On tiny independent
patterns both exact algorithms agree with direct brute-force
enumeration of *all* vertex labels. Negative controls reject
nonmonotone matrices, invalid probabilities, a malformed wedge
and a changed source triple; **they do not assert that Sidorenko
fails in the nonmonotone region**.

Reproduce:

```sh
python3 scripts/sidorenko_monotone.py --check
python3 -m unittest discover -s tests -p test_sidorenko_monotone.py -v
python3 scripts/sidorenko_regular2.py --check
python3 scripts/regen.py --check
```

## Scope and next falsifier

This result excludes the **entire ordered cone of two-block graphons**
for *all* block masses as witnesses against M073. It is substantially
broader than our prior balanced equal-diagonal theorem but does not
contain it: antimonotone off-diagonal patterns (for example
\(a=c<b\)) lie outside the ordered cone and were handled differently
in [M073_REGULAR2_CYCLE_MARGIN.md](M073_REGULAR2_CYCLE_MARGIN.md).

The rest of the three-parameter space is still open to attack:
\(b<\min(a,c)\) or \(b>\max(a,c)\), including unequal
diagonals and nonuniform masses. Search those **nonmonotone**
regions for rational negative density gaps, or obtain the explicit
finite host claimed in the upstream preprint. Any discovery must
be independently recounted against the same SHA-256-pinned \(H\).
This restricted proposition has not passed an external novelty audit,
specialist independent review, or the unrestricted Solved gate.
