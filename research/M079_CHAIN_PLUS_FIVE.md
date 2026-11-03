# M079 — quantitative 3/8 balance candidate for chain-plus-five antichain posets

**Work:** O-M079-04; [claim #201](https://github.com/Svyable/100/issues/201); canonical work-queue scope SHA-256
`5629ffe92a7529266dc2a522e885ab96934a4d780f7cf38dbdf325fb9bbab844`
(exploratory pre-ledger digest `a9f7bf91b0171598bd03cdac0fc5e690e7b29a62dccc0796d75f06085af76b87`).

**Evidence classification:** author-derived **restricted all-orders proof candidate**,
using an elementary parameterized lemma plus a finite exhaustive certificate.
There are two exact counting algorithms and a third, relation-matrix-based
checker for the sharp finite witness. **No independent human mathematical
review or historical-novelty acceptance.** The general one-third–two-thirds
conjecture remains open; do not update the Solved ledger.

## Precisely quantified statement

Let `P` be a finite poset consisting of a designated chain
`c1 < ... < cm` and five additional elements `x0,...,x4`. Assume:

1. The five outsiders are **pairwise incomparable**.
2. The width of `P` is **exactly five**.
3. Every outsider is incomparable with **at least one chain element**.

For uniformly random linear extension `L`, set

`delta(P) = max_(u != v) min(Pr_L(u before v), Pr_L(v before u))`.

**Restricted theorem candidate:** `delta(P) >= 3/8`. The infimum for this
infinite class lies in **[3/8, 2/5]**: a 13-element example below has exactly
`delta(P)=2/5`. The lower bound is not asserted sharp. This is not a
theorem about arbitrary width-five posets, arbitrary chain-deletion-five
posets, or the unrestricted conjecture.

## Parameterized gap-atom lemma (all chain lengths)

More generally, suppose `P` is a chain plus `k>=2` pairwise incomparable
outsiders. Number the `m+1` gaps in the chain `0,...,m`. For outsider `x`,
its allowed insertion gaps form a nonempty integer interval `I_x`, of
length `L`. Its chain predecessors are a prefix and its chain successors
a suffix, so these are *all* the possible gaps.

**Lemma.** For each allowed gap `g`,

`Pr(x is inserted in g) <= k/(L+k-1)`.

**Proof.** Fix a linear extension `Q` of `P-x`. For each `g in I_x`, let
`t_g(Q)` be the number of other outsiders of `Q` in gap `g`. Because `x`
is incomparable with all of them, there are exactly `1+t_g` ways to insert
`x` at `g`, and `L+sum_(h in I_x) t_h` legal insertions overall. Thus the
conditional mass is

`(1+t_g)/(L+sum t_h) <= (1+t_g)/(L+t_g) <= k/(L+k-1)`,

since `0<=t_g<=k-1` and `(1+t)/(L+t)` is nondecreasing for `L>=1`.
The uniform distribution on extensions of `P` induces a *size-biased*
mixture of these conditional distributions over `Q`, but a pointwise
upper bound survives the mixture. This avoids incorrectly treating `Q`
as uniformly distributed after deleting `x`. QED.

**Threshold consequence.** For `0<alpha<1/2`, if

`L >= ceil(k/(1-2*alpha) - k + 1)`,

then `x` has an `alpha`-balanced pair with a chain vertex. Indeed, every
gap atom has mass at most `1-2*alpha`; the first cumulative mass at least
`alpha` is at most `1-alpha`. It is reached at a *real* chain vertex:
the final atom is at most `1-2*alpha`, so the cumulative mass before the
last gap is at least `2*alpha >= alpha`. (At equality the endpoint is
allowed.) The pair probability is precisely this cumulative gap mass.

For `alpha=1/3` the cutoff is `L>=2k+1`. In particular, this gives a
general **finite-kernel reduction** for the width-`k` antichain-outsider
class: a hypothetical counterexample must have all outsider intervals of
length at most `2k`.

## Helly/width reduction and the quantitative finite core

If two outsiders have disjoint gap intervals, the chain forces a comparison
between them, contrary to their incomparability. Thus their intervals
intersect pairwise; integer intervals satisfy Helly's property and all five
share a gap. If their common intersection contained two consecutive gaps,
the chain vertex between those gaps would be incomparable with all five
outsiders, producing an antichain of size six. Width exactly five forces
**one common gap**. Translate that gap to zero:

`max_i a_i = min_i b_i = 0,\quad I_i=[a_i,b_i],\quad b_i-a_i+1>=2.`

Conversely, these constraints construct exactly the specified class, up
to chain vertices before/after the union of intervals. Such outer padding
is comparable with every outsider, has a fixed place in every extension,
and does not change any pair probability.

The general `1/3` kernel therefore needs at most `4k-2` chain vertices
and `5k-2` total vertices: every interval has length at most `2k`,
so its left endpoint is at least `-(2k-1)` and its right endpoint at
most `2k-1`. This is a *finite decision reduction for each fixed k*,
not a proof of the conjecture for every k.

For the stronger `alpha=3/8` at `k=5`, the gap-atom bound gives

`Pr(x in g) <= 5/(L+4) <= 1/4 = 1-2*(3/8)` whenever `L>=16`.

It remains to check all five-interval multisets with lengths `2..15`,
each containing zero, and common intersection exactly `{0}`. There are
`N=2+3+...+15=119` possible intervals. Sorting the five interval
labels removes only their permutation symmetry. The number of eligible
multisets is independently given by inclusion-exclusion:

`binom(123,5) - 2*binom(109,5) + binom(95,5) = 40,355,371.`

Here one interval must have left endpoint zero and another right endpoint
zero; these two sets of intervals are disjoint because length is at least
two. The C++ enumerator checks every sorted multiset, not a sample.

### Two exact integer counting recurrences

For each multiset, the checker computes the total number `E` of linear
extensions and **every** outsider–outsider and outsider–chain before-count.

* **Sequential order-ideal recurrence:** state `(q,mask)`, where `q` is the
  chain prefix already placed and `mask` records placed outsiders. A chain
  step is legal only when it does not pass an unplaced outsider's latest
  allowed gap; an outsider step is legal at its current allowed gap.
  Forward/backward path counts weight each outsider insertion. Its
  insertion at gap `q` precedes all chain vertices `c_t` with `t>q`,
  and precedes each as-yet-unplaced outsider.
* **Factorial gap-block recurrence:** at each chain gap, choose a subset
  `T` of eligible unplaced outsiders, require every outsider whose
  last gap is now to be included, and weight that block by `|T|!`.
  Its subset transitions and forward/backward counts are structurally
  different from sequential one-element moves. For two outsiders in the
  same block, exactly half the `|T|!` permutations put one before the
  other. The two paths must agree on `E`, all ten outsider-pair counts,
  and every outsider's per-gap marginal vector, **for every multiset**.

The finite certificate compares integer numerators, not floating point:
`8*max_pair min(count,E-count) >= 3*E`. Both paths are run over the
entire residual. Their agreement is an **independent algorithmic check**,
not an independent person, formal kernel proof, or specialist acceptance.
The largest residual chain has 28 vertices, so even the crude extension
bound `33!/28! = 28,480,320` is below signed 64-bit range.

## A concrete falsifier of transferring the four-outsider constant

Take chain gaps `-4,-3,-2,-1,0,1,2,3,4` (eight chain vertices) and
five pairwise incomparable outsiders with intervals

`[-4,0], [-1,0], [-1,1], [0,1], [0,4]`.

All intervals have at least two gaps, and their common intersection is
exactly zero, so width is exactly five. The poset has **1,405** linear
extensions and best smaller-side numerator **562**, hence

`delta(P)=562/1405=2/5 < 25/61`.

The `25/61` sharp candidate for four outsiders (active PR #184) therefore
**does not transfer verbatim to five outsiders**. This is a falsifier of
that stronger extrapolation, *not* a counterexample to the 1/3–2/3
conjecture.

A compact certificate, with outsider indices in the interval order above:

- Outsider–outsider before-counts in lexicographic pair order:
  `977, 1075, 1200, 1272, 880, 1083, 1200, 880, 1075, 977`.
- Per-gap extension weights (gaps `-4,...,4`):
  `x0: 183,183,183,294,562,0,0,0,0`;
  `x1: 0,0,0,492,913,0,0,0,0`;
  `x2: 0,0,0,355,695,355,0,0,0`;
  `x3: 0,0,0,0,913,492,0,0,0`;
  `x4: 0,0,0,0,562,294,183,183,183`.

The weights in every row sum to `1405`. Prefix sums give all
outsider–chain probabilities; no pair exceeds the smaller-side numerator
`562`. In particular `x4<c5` occurs in exactly 562 extensions.

The test suite rebuilds the actual 13-element relation matrix, counts
linear extensions by a third bitmask order-ideal recurrence over **all**
vertices, and recomputes each pair count after adding that relation.
It does not use either gap-state recurrence.

## Exploratory search provenance (not proof evidence)

Before the exhaustive certificate, a seeded Python gap-state search sampled
20,000 five-interval tuples with lengths 2–9 and endpoints containing zero
(seed `97129`); 10,107 had singleton common intersection and the best
sampled balance was `2197/5110`, not a counterexample to `25/61`.
Starting instead from the four-outsider sharp tuple
`[-1,0],[0,1],[-1,1],[-4,0]`, a deterministic scan of every fifth
interval of lengths 2–30 containing zero found `2/5` at `[0,4]`.
A seven-layer bounded neighbor/beam search around that witness inspected
3,025 distinct normalized tuples and did not improve it. Those searches
are heuristic and incomplete; no inference about the infinite class or
finite minimum is drawn from them. The exact witness is reproducible via
`m079_chain5_kernel --instance "-4:0,-1:0,-1:1,0:1,0:4"` after compilation;
the full census is the actual proof obligation.

## Reproduction and adversarial controls

From the repository root (Python 3.12+, C++17 compiler):

```sh
python3 scripts/m079_chain5_kernel.py --check --json
python3 scripts/m079_chain5_kernel.py --smoke --json
python3 -m unittest discover -s tests -p 'test_m079_chain5_kernel.py' -v
python3 scripts/regen.py --check --fast
python3 -m unittest discover -s tests
```

The full check enumerates **40,355,371** normalized interval multisets,
checks every one with both recurrences, and compares the count to a separate
inclusion-exclusion formula. The finite minimum `2/5` is attained by
exactly **one** normalized interval multiset. The code prints a deterministic
64-bit FNV transcript digest `b1671adf73c7eb56` for drift detection (not a cryptographic
authenticity claim). A 21,250-case smoke check is for quick development,
not a substitute for the full certificate.

Adversarial tests include a deliberate same-gap factorial-order mutation
(which the two recurrences must disagree on), an invalid width-six shared
multi-gap example, a singleton-gap outsider, disjoint intervals, reversed
endpoints, all 120 outsider permutations of the witness, order duality,
translation, the exact 15/16-gap analytic boundary, and the false naive
product-of-interval-lengths count. A separate explicit-poset checker
verifies the witness and 20 seeded small instances.

## Literature and novelty audit (checked 2026-11-01)

- Brightwell and Wright, [*The 1/3–2/3 Conjecture for 5-Thin Posets*,
  SIAM J. Discrete Math. 5 (1992)](https://doi.org/10.1137/0405037):
  bounded incomparability degree, whereas this chain-plus-five class
  contains outsiders incomparable with arbitrarily many chain vertices.
- Zaguia, [*The 1/3–2/3 Conjecture for N-Free Ordered Sets* (2012)](https://doi.org/10.37236/2345):
  different forbidden-subposet condition; no N-free assumption here.
- Olson and Sagan, [*On the 1/3–2/3 Conjecture* (2018)](https://arxiv.org/abs/1706.04985):
  established families and dimension-two subcases, not an identified
  exact chain-plus-five quantitative theorem.
- Chen, [*A Family of Partially Ordered Sets with Small Balance Constant*
  (2018)](https://doi.org/10.37236/7337): general posets can have
  balance approaching 0.3488999, so `3/8` cannot hold universally.
- Aires and Kahn, [*Balancing Extensions in Posets of Large Width*
  (2025)](https://arxiv.org/abs/2509.11549), and Aires,
  [*Proof of the Kahn Saks Conjecture* (September 2026)](https://arxiv.org/abs/2609.30895):
  asymptotic large-width results; neither abstract establishes this
  fixed-width-five quantitative statement.
- Aires, Chan, Pak and Panova, [*Breaking the Infinite Barrier in the 1/3–2/3 Conjecture* (September 2026)](https://arxiv.org/abs/2609.30888):
  a universal epsilon improvement over the 1995 bound, still below the
  conjectured 1/3 and not an identified fixed-width-five 3/8 theorem.
- Gupta, [*Balance Constants, Majority Cycles, and the Gold Partition Conjecture through Fourteen Elements*
  (July 2026)](https://arxiv.org/abs/2607.23926): finite order-14 work,
  not the present unbounded-chain statement.
- The separately claimed [chain-plus-four candidate](https://github.com/Svyable/100/pull/184)
  has `25/61` and a different residual. Its scope, files, tests and
  landing workflow are not modified here.

A targeted source search did not identify the exact `3/8` bound for this
class, but **absence from search is not evidence of historical novelty**.
An expert should check older near-chain, dimension-two, partition-poset,
interval-order and width-five literature in full, not merely abstracts.

## Failed avenues, assumptions and next falsifiers

The original `1/3` gap cutoff (`L>=11`) gives a smaller
1,426,356-case finite kernel, but only the weaker conclusion; the
`3/8` cutoff (`L>=16`) requires the 40,355,371-case residual.
The naive `prod |I_i|` count is false because outsiders sharing a gap
can be ordered in factorially many ways (witness: `300 != 1405`).
The hoped-for transfer of the chain-plus-four `25/61` bound is
falsified exactly by the 13-element example. This method does not prove
`2/5` for the unbounded class: its gap-atom threshold for `2/5`
would require `L>=21`, leaving a much larger residual.

**Material hypotheses:** finite poset; specified chain; exactly five
outsiders; outsiders form an antichain; width exactly five; every
outsider has a chain incomparability; uniform distribution on linear
extensions. If outsider comparabilities are added, the insertion-slot
formula can fail. If width is six, the common-gap singleton reduction
fails. If an outsider has only one gap, it is outside the finite
enumeration. No claim about those excluded classes follows.

**Next falsifier:** a concrete valid five-interval multiset with
`8*best<3*E`; a mismatch in the independent full 40m-case recurrence;
a relation-matrix mismatch; an omitted interval multiset; an
overflow or off-by-one in the gap cutoff; or a primary historical
source proving the same or stronger class bound. Obtain a *human*
scope/proof review and an independent specialist novelty audit before
any acceptance or solved-status change. The current result is a
candidate awaiting those checks.
