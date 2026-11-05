# M097 — sharp four-thirds bound and exact LP equality in fully subdivided graph metrics

**Claim:** [#283](https://github.com/Svyable/100/issues/283). **Work ID:** `X-M097-SUBDIVIDED-FOURTHIRDS`. **Scope SHA-256:** `2e3b6f583bf4c2a9a49143f8ceea86d2b2d441179abb32c91e36119e43b6ada4`. **Date:** 2026-11-02 (America/Chicago).

**Status:** author-derived all-orders restricted proof candidate. The argument is **unconditional** in the mathematical sense: it uses only the already established Edmonds–Johnson theorem for the `T`-join polyhedron and the exact core-parity/subtour formulas proved in [M097 subdivision core](M097_SUBDIVISION_CORE.md). No unproved conjecture or computation-to-infinity extrapolation is used. The proposed corollaries **have not received independent mathematical review, Lean verification, or historical-novelty certification**. This is **not** the four-thirds conjecture for arbitrary metric TSP.

## 1. Theorem and sharp boundary

Let `H=(V,E)` be a finite, connected, undirected **loopless multigraph**, at least two vertices, with individually indexed parallel edges allowed. Replace each core edge `e` by an internally vertex-disjoint simple path of integer length `L_e>=2`; denote the resulting unweighted graph `G_L`, and take the complete shortest-path metric on its vertices. Write

\[
M=\sum_{e\in E}L_e,\qquad
B=\sum_{e\in\operatorname{Br}(H)}L_e,\qquad b=|\operatorname{Br}(H)|.
\]

The symmetric metric subtour LP (SEP) has value \(\operatorname{SEP}(G_L)=M+B\), by the exact subdivision-core theorem. Then:

**(A) Exact zero-gap criterion.** \(\operatorname{TSP}(G_L)=\operatorname{SEP}(G_L)\) **if and only if** there exists an even-degree spanning edge subset \(F\subseteq E(H)\) satisfying both

1. every nonbridge edge of \(E\setminus F\) has path length **exactly two**, and
2. the graph \((V,F)\), counting isolated core vertices as components, has **exactly \(b+1\)** components.

Consequently, for uniform length two and bridgeless `H`, LP exactness is equivalent to `H` having a **connected spanning Eulerian subgraph** (the classical `supereulerian` property). If **every nonbridge length is at least three**, LP exactness is equivalent to all degrees of \(H-\operatorname{Br}(H)\) being even. There is no claim of a new characterization of supereulerian graphs.

**(B) Sharp four-thirds bound with additive slack.** If every degree of \(H-\operatorname{Br}(H)\) is even, then

\[
\boxed{\operatorname{TSP}(G_L)=\operatorname{SEP}(G_L)=M+B.}
\]

Otherwise,

\[
\boxed{\operatorname{TSP}(G_L)\leq \frac43 M+\frac23 B-2
=\frac43\operatorname{SEP}(G_L)-\frac23B-2.}\tag{1}
\]

In both cases, \(\operatorname{TSP}(G_L)<\frac43\operatorname{SEP}(G_L)\) for every finite instance; the coefficient \(\frac43\) is **asymptotically sharp** over this class, and the additive constant **2 is sharp** in (1), both with and without bridges. This includes unequal path lengths and articulation vertices, and does not require a degree bound on the core.

**(C) Algorithmic scope.** A minimum-weight `T`-join in the core (obtainable by standard shortest-path/matching algorithms) and the Eulerian-walk/shortcut construction in the base note yield a polynomial-time certifiable tour satisfying (1). This is an approximation guarantee for this restricted family, not an algorithm for arbitrary metric TSP.

## 2. Exact zero-gap characterization — proof

Let \(T\subseteq V\) be the odd-degree vertices of `H`; \(|T|\) is even. For every even-degree edge subset \(F\subseteq E\), its complement \(D=E\setminus F\) is a `T`-join. Every bridge of `H` belongs to `D`: cut at that bridge, and the number of odd-degree vertices on either shore is odd, forcing every `T`-join to cross the singleton cut.

Recall the **exact** formulas from the base note, which apply for arbitrary lengths \(L_e\ge 2\):

\[
\operatorname{TSP}(G_L)
=M+\min_{F\text{ even}}\left[
\sum_{e\notin F}(L_e-2)+2(c(F)-1)\right],
\qquad\operatorname{SEP}(G_L)=M+B,
\]

where \(c(F)\) counts **all** connected components, including isolates.

Deleting all \(b\) bridges from a connected multigraph leaves exactly \(b+1\) components. Since every even `F` omits all bridges, \(c(F)\ge b+1\). For each `F`, subtract the SEP value from its candidate tour cost:

\[
\begin{aligned}
&M+\sum_{e\in D}(L_e-2)+2(c(F)-1)-(M+B)\\
&\quad=
\sum_{e\in D\setminus\operatorname{Br}(H)}(L_e-2)
+2(c(F)-b-1).\tag{2}
\end{aligned}
\]

Both terms on the last line are **nonnegative integers**, by the length restriction and component bound. Their sum vanishes precisely under the two conditions in part (A). As there are finitely many even `F`, the minimum is equal to the SEP value precisely when at least one `F` satisfies them. This proves the iff, not merely a sufficient condition.

For the stated uniform-length-two specialization with \(b=0\), every \(L_e-2=0\) and the sole condition is \(c(F)=1\). For the every-nonbridge-length-at-least-three specialization, equality forces `D` to contain **no nonbridge**, so `D` is the set of all bridges, equivalent to the edge subset `H-Br(H)` having even degrees. If that evenness condition holds, the same `F=E\setminus Br(H)` gives equality for **all** lengths at least two.

## 3. Sharp four-thirds inequality — unconditional proof

**Step 1: A fractional `T`-join.** For each core edge set

\[
x_e=\begin{cases}
1,&e\in\operatorname{Br}(H),\\
1/3,&e\notin\operatorname{Br}(H).
\end{cases}\tag{3}
\]

For every shore \(S\subsetneq V\) with \(|S\cap T|\) odd, the handshake identity says
\(|\delta_H(S)|\equiv |S\cap T|\pmod2\). Thus the cut has **odd** cardinality. If it contains a core bridge, its `x`-capacity is at least one; otherwise it has at least **three** nonbridge edges (a one-edge cut would itself be a bridge), so again \(\sum_{e\in\delta(S)}x_e\ge1\).

The **Edmonds–Johnson (1973) integral `T`-join polyhedron theorem** states that for nonnegative edge weights the minimum `T`-join weight equals the minimum of the linear program \(x\ge0,\ x(\delta(S))\ge1\) for every `T`-odd cut. This established theorem is a named external input, **not** a result claimed here. Applying it to positive weights \(w_e=L_e\) and candidate (3), there exists a `T`-join `D` with

\[
w(D)\le \sum_{e}L_ex_e=B+\frac{M-B}{3}.\tag{4}
\]

All bridges are forced into `D`.

**Step 2: When there is no nonbridge parity correction.** If all degrees of \(H-\operatorname{Br}(H)\) are even, take \(F=E\setminus\operatorname{Br}(H)\). It is even, has \(c(F)=b+1\), and its cost equals \(M+B\) by (2). The SEP lower bound proves (B)'s first branch.

**Step 3: When a nonbridge correction is necessary.** Otherwise **every** `T`-join contains a nonbridge. In particular the `D` from Step 1 contains some \(e\) that was not a bridge of the connected core. Delete this edge **first**; the graph remains connected. Delete the other \(|D|-1\) edges next; each can increase the number of components by **at most one**. Therefore

\[
c(E\setminus D)\le |D|,\qquad |D|-c(E\setminus D)+1\ge1.\tag{5}
\]

Use the even subset \(F=E\setminus D\) in the exact tour formula. It gives

\[
\begin{aligned}
\operatorname{TSP}(G_L)
&\le M+\sum_{e\in D}(L_e-2)+2(c(F)-1)\\
&=M+w(D)-2(|D|-c(F)+1)\\
&\le M+B+\frac{M-B}{3}-2\\
&=\frac43 M+\frac23 B-2.
\end{aligned}
\]

Since \(\frac43(M+B)-(\frac43 M+\frac23 B-2)=\frac23 B+2>0\), the integrality ratio is strictly below \(4/3\) in this branch. In the even branch it is exactly one. This completes the all-orders argument, without requiring a numerical verifier, a conjectural input, or an unspecified constant.

## 4. Exact sharpness, length-sensitive falsifier, and boundaries

**Three-parallel-edge theta.** Take a loopless two-vertex core with exactly three parallel edges, each subdivided to length \(L\ge2\). It has \(M=3L,B=0,T=V\). The only even `F` are the empty edge subset and the three two-edge subsets. Choosing two edges gives a one-component `F` and cost \(3L+(L-2)=4L-2\); the empty subset costs \(6L-4\), which is always larger. Thus

\[
\boxed{\operatorname{SEP}=3L,\qquad\operatorname{TSP}=4L-2,\qquad
\frac{\operatorname{TSP}}{\operatorname{SEP}}=\frac43-\frac{2}{3L}.}
\]

This exactly attains bound (1) for each \(L\ge2\) and approaches \(4/3\) as \(L\to\infty\). **This lower-bound family is related to classical graphic-TSP examples; we do not claim priority for it.**

**Sharp with bridges.** Add a single pendant core edge of length \(K\ge2\) to one of the theta endpoints. The pendant path must be doubled in any spanning Eulerian walk, hence
\(\operatorname{SEP}=3L+2K\) and \(\operatorname{TSP}=4L-2+2K\). Here \(M=3L+K,B=K\), and (1) is attained **with equality**.

**Coordinate-wise monotonicity is false.** For the three parallel core edges, lengths \((3,3,3)\) give \(\operatorname{SEP}=9,\operatorname{TSP}=10\), ratio \(10/9\). Lengthening the first edge to \((4,3,3)\) gives \(\operatorname{SEP}=10,\operatorname{TSP}=11\), ratio \(11/10<10/9\). This does **not** contradict the uniform-length monotonicity corollary recorded on #279. The theorem here does not assert coordinate-wise monotonicity.

**Length-one exclusion.** The formula \(\operatorname{SEP}=M+B\) is not valid without \(L_e\ge2\): an unsubdivided `K4` has \(\operatorname{SEP}=\operatorname{TSP}=4\) although \(|E|=6\). No statement is made about length-one edges or arbitrary metrics.

## 5. Reproduction and falsification

```sh
python3 scripts/m097_subdivision_fourthirds.py --check
python3 -m unittest discover -s tests -p 'test_m097_subdivision_fourthirds.py' -v
python3 scripts/regen.py --check
```

The new standard-library script **independently enumerates every `T`-join**, computes bridge indices by literal deletion, checks all `T`-odd cuts of the rational fractional certificate, enumerates all candidate exact costs and tests the iff classification and the strict/branched inequalities. Its exhaustive simple-core sweep uses all connected labeled simple graphs on 2–4 core vertices, with each edge of length two or three; it adds all connected loopless 2–4-vertex multigraphs of at most five edges (parallel edges included; lengths two or three), all two-vertex parallel-edge cores with up to five parallel edges of lengths two to four, and seeded connected small-multigraph cases. The source script records the exact count in its JSON output. It also checks the theta family, pendant bridges, a nonuniform-ratio counterexample, and two negative controls.

The dedicated tests cross-check selected instances against the **different** core-parity implementation from #279. The finite checks are falsifiers and regression controls; **the proof rests on Sections 2–3**, not on extrapolation from any finite range. Both checkers are project/author-side, not independent specialist review.

## 6. Prior art and novelty boundary

Sources checked 2026-11-02 (America/Chicago):

- J. Edmonds and E. L. Johnson, *Matching, Euler Tours and the Chinese Postman*, Mathematical Programming 5 (1973), 88–124: the integral `T`-join cut polyhedron. A standard modern formulation is Theorem 12.18 in [Korte–Vygen, *Combinatorial Optimization*, Chapter 12](https://www.mathematik.uni-muenchen.de/~kpanagio/KombOpt/book.pdf). The odd-cut bound in Step 1 is **entirely classical**.
- M. Goemans and D. Bertsimas, *Survivable Networks, Linear Programming Relaxations and the Parsimonious Property* (1993), [author-hosted text](https://www.mit.edu/~dbertsim/papers/ApproximationAlgorithms/Survivable%20networks%2C%20LP%20relaxations%20and%20the%20parsimonious%20property.pdf). The degree-restricted subtour value is related to this established property, not claimed as novel here.
- S. Boyd, R. Sitters, S. van der Ster and L. Stougie, *The traveling salesman problem on cubic and subcubic graphs*, Mathematical Programming 144 (2014), 227–245, [DOI](https://doi.org/10.1007/s10107-012-0620-1). Stronger \(4/3\)-type results exist for subcubic graph metrics; this note must **not** advertise a new first four-thirds theorem for that class.
- Wigal, Yoo and Yu, *Approximating TSP walks in subcubic graphs*, JCTB 158 (2023), [DOI](https://doi.org/10.1016/j.jctb.2022.09.002). Subcubic even-cover results and the relationship to subdivision are prior art.
- Project 100's merged [M097 subdivision-core identity](M097_SUBDIVISION_CORE.md), whose general formulas are used verbatim and whose novelty is not independently settled.

**Potentially useful restricted deliverables:** the exact LP-zero-gap iff for arbitrary unequal subdivisions, the additive-two sharp bridge-sensitive inequality, and the explicit rational/parity test suite. Their **historical originality is unestablished**; this is an exact scoped synthesis with an unconditional proof, not an independently confirmed breakthrough or a resolution of M097.

**Next independent review:** verify that the minimum `T`-join polyhedron theorem is used with precisely the stated odd-cut and nonnegative-weight conventions; independently audit the bridge-deletion and zero-gap iff; search literature for pre-existing arbitrary-degree subdivided-TSP inequalities or supereulerian characterizations. Do not mark `solved`, modify the 100-problem evidence state, or claim theorem acceptance without such review.
