# Research-source audit — 2026-10-30

This is a **targeted source intake**, not a blanket verification of all 100 open statuses.
The five updated entries remain `needs_review`; a filled `checked_on` field means the
cited source was inspected, **not** that a full latest-literature search was completed.
No editorial score was changed merely because a source link was found.

| ID | Source examined | Confirmed scope | Remaining status gap |
|---|---|---|---|
| M074 | [Hoàng–Reed (1987)](https://doi.org/10.1016/0012-365X(87)90122-1) | Original short-cycle conjecture and some bounded outdegree cases | Fresh specialist status audit and strongest current restricted theorem |
| M075 | [Costa–Sadhu (Oct 2026 preprint)](https://arxiv.org/abs/2610.02295) | Authors give a universal abundance lower bound 0.3828852549667978, strictly below 1/2 | Independent review of preprint and separate claimed unrestricted proofs |
| M088 | [Kabanets–Impagliazzo (2004)](https://www.cs.sfu.ca/~kabanets/Research/poly.html) | Identity-test derandomization has major circuit-lower-bound implications | Recent restricted PIT developments and exact computational model |
| M092 | [Zauner/SIC survey summary](https://papex.org/problems/zauners-conjecture) | General SIC existence vs stronger Weyl–Heisenberg covariant form are different targets | Primary 2026 preprints, precise conditional Galois hypotheses, independent review |
| M095 | [Angeltveit–McKay (2026)](https://doi.org/10.1002/jgt.70029) | Published 43 ≤ R(5,5) ≤ 46; upper bound independently implemented by authors | Any post-publication better bounds and verified K42 input for local checker |

## Immediate promotion gates

A target moves from `needs_review` to `verified_open` only after recording:
1. Exact claim and quantifiers (including characteristic, dimensionality, and exceptions);
2. At least one contemporary primary specialist source discussing the still-open remainder;
3. Comparison against claimed proofs/counterexamples published after that source;
4. A dated note explaining why the latest evidence does or does not settle the *full* claim.

Work already done: two executable small-case verification harnesses
([Ramsey](../scripts/ramsey.py) and [union-closed families](../scripts/union_closed.py)).
Neither establishes a new general theorem.

## Portfolio discipline

**Do not silently modify rank scores to make active campaigns appear more attractive.**
Rank changes should cite a theorem, new reusable method, reproducible computation, or
specific negative feasibility result. Preserve the 100-slot portfolio independently of
the smaller active-campaign slate.
