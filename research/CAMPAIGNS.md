# Four concrete proof campaigns — first research tranche

**Date:** 2026-10-30. These are research proposals, not assertions of new theorems. The first three are the current top-ranked candidates; the fourth is the independent-certificate benchmark.

## M074 — Caccetta–Häggkvist (directed graphs)

**Current executable attack:** [dedicated orbit census and (18,6) SAT dossier](M074_CH.md).

**Statement.** Every finite loopless simple digraph on n vertices with minimum outdegree at least r≥1 has a directed cycle of length at most ceil(n/r).

**Source:** [Hoàng–Reed, *A note on short cycles in digraphs* (1987)](https://doi.org/10.1016/0012-365X(87)90122-1) discusses exact low-outdegree cases. [EGRES Open overview](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture) distinguishes the directed-triangle form from the full statement.

**First experiment.** Build small directed graphs with degree constraints and no cycles up to k, encoded as SAT/SMT. Compare with known small-case theorems before reporting a result. Try structural restrictions (vertex transitivity, forbidden 2-cycles, high minimum indegree), then state a *new* conditional lemma only if it is absent from the literature. A finite failure-to-find-counterexample is not a universal proof.

**Verifier.** Check vertex count, looplessness, minimum outdegree, and independently compute shortest directed cycles for candidate counterexamples.

## M088 — Deterministic polynomial identity testing

**Statement.** Is identity testing for explicitly represented arithmetic circuits possible in deterministic polynomial time in the input size (under a fixed, fully specified coefficient and circuit model)?

**Source:** [Kabanets–Impagliazzo, *Derandomizing Polynomial Identity Tests Means Proving Circuit Lower Bounds* (2004)](https://www.cs.sfu.ca/~kabanets/Research/poly.html).

**First experiment.** Pick an *explicit restricted circuit class* (bounded-depth or bounded-top-fanin, with named field/characteristic and degree restrictions), implement a deterministic hitting set and prove the stated size/hitting property. Distinguish black-box from white-box PIT; do not extrapolate a result on restricted circuits to arbitrary circuits.

**Verifier.** Exact symbolic expansion on small instances, independently checked hitting-set construction, then a conventional or formal proof for the whole restricted family.

## M092 — Zauner / SIC existence

**Statement.** For each integer d≥2, do there exist d² unit vectors in C^d whose off-diagonal squared overlaps are 1/(d+1)? The stronger Weyl–Heisenberg covariant claim must not be confused with this general form.

**Status:** Extensive exact/numerical dimension results, but no universal construction established in this portfolio. Relevant 2026 algebraic preprints should undergo independent scope and correctness review before updates. [Open-problem starting reference](https://papex.org/problems/zauners-conjecture).

**First experiment.** For chosen small dimensions, encode normalized fiducial constraints as exact polynomial equations and verify candidate vector sets with rational/algebraic arithmetic (not float tolerances). Look for an arithmetic construction *uniform in a family of dimensions*. Explicitly document conditional Galois hypotheses in any 2026 approach.

**Verifier.** Exact norm and all pairwise squared-inner-product identities for every vector. A list of finite-dimensional solutions cannot prove existence in all dimensions.

## M095 — Ramsey R(5,5)

**Statement.** Determine the minimum n for which every two-edge-coloring of K_n contains a monochromatic K5.

**Source:** [Angeltveit–McKay (2026)](https://doi.org/10.1002/jgt.70029) establishes R(5,5)≤46; prior lower bound is 43.

**First experiment and certificate:** [M095 executable protocol](M095_RAMSEY.md), with a deterministic verifier, SAT encoder, unit tests and an exact R(3,3) smoke test.

## Common proof standards

1. Quote the exact source theorem, quantifiers, exceptions, and date checked.
2. Name the *smallest* novel claim, and search hard for counterexamples and prior proofs.
3. Require independently checkable evidence before assigning “proved”.
4. Preserve failed ideas and cost measurements without pretending they are evidence for the conjecture.
5. Rank mathematical significance separately from the chance of shipping a checkable intermediate theorem.
