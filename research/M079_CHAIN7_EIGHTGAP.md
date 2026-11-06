# M079 — seven-outsider eight-gap boundary: exact restricted certificate

**2026-11-02. Work ID:** `X-M079-CHAIN7-EIGHTGAP`; [claim #259](https://github.com/Svyable/100/issues/259). **Scope SHA-256:** `a09c31bdbaa1c05a78547da092212181b6655d9aa8007610a3a9e91a26cd37a0`. This is an **author-derived restricted theorem candidate / exact negative boundary search**, not an independently reviewed mathematical result. Historical novelty unestablished. The unrestricted one-third–two-thirds conjecture remains open.

## Exact target and outcome

Let `P` consist of a designated chain `c_1<...<c_m` and exactly seven pairwise incomparable outsiders `x_0,...,x_6`. Assume `width(P)=7` and every outsider is incomparable with between one and seven chain elements, equivalently has between **two and eight allowed insertion gaps**. For uniformly random linear extension `L`, define
`delta(P)=max_{u!=v} min(Pr_L(u<v),Pr_L(v<u))`.

**Sharp restricted theorem candidate:** `delta(P) >= 44873/107157 = 1951/4659 ≈ 0.4187593904`. Equality is attained by the 17-element poset with ten chain vertices (gaps -5 through 5) and outsider intervals `[-5,0],[-2,0],[-2,2],[-1,0],[0,1],[0,2],[0,5]`. The exact extension count is `E=107157`, and the largest smaller-side pair count is `B=44873`. This is the **same** sharp witness as the previously merged six-gap result, now established for the larger eight-gap class by a new complete finite certificate. It is a genuine exact extension of scope, **not** an independently established historically novel theorem or a new sharp constant.

The scope includes arbitrarily long chains only through prefix/suffix padding comparable to every outsider. It excludes width eight, outsiders with only one allowed gap, outsider comparabilities, and outsiders with nine or more gaps. No global 1/3–2/3 result follows.

## Structural reduction for all chain lengths

For each outsider `x_i`, its chain predecessors form a prefix and its chain successors form a suffix. Hence the permitted insertion gaps form an integer interval `I_i=[a_i,b_i]`. If two outsiders' intervals were disjoint, their relative order would be forced, contradicting pairwise incomparability. By Helly's property for intervals, all seven intervals share a gap. Two shared consecutive gaps would make the intervening chain element incomparable with all seven outsiders and produce width eight. Conversely, if their intersection is exactly one gap, an eight-element antichain cannot exist because it would require all seven outsiders and one chain element. Translate the common gap to zero:
`a_i<=0<=b_i`, `max_i a_i=min_i b_i=0`, `2<=b_i-a_i+1<=8`.

Removing chain elements before the first or after the last allowed gap preserves all incomparable pair probabilities: those elements are globally comparable and have fixed locations in every extension. Sorting the seven intervals loses only outsider-label permutations. There are `N=2+...+8=35` interval types containing zero; seven have left endpoint zero and seven disjoint types have right endpoint zero. The exact number of normalized multisets with both types is
`C(41,7)-2*C(34,7)+C(27,7)=22,481,940-10,759,232+888,030=12,610,738`.
This count is derived independently of the search traversal. At most 14 chain elements and 21 total elements remain; the crude linear-extension bound `21!/14!=586,051,200` fits in unsigned 64-bit integers.

## Two complete exact algorithms and third representation

The modified `scripts/m079_chain7_local.cpp` accepts `--max-length 8 --dual`, preserving the prior six-gap code path and its expected transcript. Every normalized interval multiset is checked by both:

1. A sequential forward/backward order-ideal recurrence over `(q, S)` (chain prefix length and placed-outsider mask), with individual legal next-element transitions.
2. A factorial gap-block recurrence that chooses an eligible outsider subset at each gap and weights its permutations by `|T|!`. Pair order within a block contributes exactly half of its permutations.

They compare the extension count, all 21 outsider-pair before-counts and all seven per-gap marginal vectors **on every instance**. Integer comparisons use `B/E` without floating point. The `scripts/m079_chain7_eightgap.py` checker independently constructs the full literal predecessor matrix and counts order ideals with a separate bitmask recursion; its all-pair counts and per-gap marginal vectors agree with the C++ code on the old sharp witness and 32 deterministic seeded configurations, including eight-gap cases. A deliberate same-gap tie-order mutation is rejected. These are distinct algorithms and representations, but all are **author-run** and do not constitute external review.

**Exact transcript (direct binary run, 606.12 seconds wall on the connected macOS host):**

`cases=12610738 dual=12610738 negative=0 minimum=44873/107157 multiplicity=1 max_length=8 intervals=35 fnv64=ddf479309a0661ab witness=[-5,0][-2,0][-2,2][-1,0][0,1][0,2][0,5]`

The unique normalized minimizer includes intervals of length six, so no new eight-gap equality case appeared. The digest is computed by the deterministic FNV64 code path, not by an independent cryptographic transcript.

Reproduce with C++17 and Python 3.12+:
```sh
python3 scripts/m079_chain7_eightgap.py --check
python3 -m unittest discover -s tests -p 'test_m079_chain7_eightgap.py' -v
python3 scripts/regen.py --check --fast
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

## All-orders sharpened noncentral gap-atom inequality

**Lemma (for any `k>=2` outsiders with a unique common gap).** Fix an outsider `x` with `L` allowed gaps. For its common gap `g_0`, `Pr(x at g_0)<=k/(L+k-1)`; for every other permitted gap `g!=g_0`,
`Pr(x at g)<=(k-1)/(L+k-2)`.

**Proof.** Delete `x` and fix any linear extension `Q` of the remaining poset. Let `t_g(Q)` count the other outsiders in gap `g`. There are exactly `1+t_g(Q)` insertions of `x` in gap `g` and `L+sum_{h in I_x}t_h(Q)` insertions in total. For `g!=g_0`, the singleton-intersection condition supplies some other outsider whose interval excludes `g`: if `g>g_0`, an outsider ending at `g_0`; if `g<g_0`, one beginning there. It cannot be `x`, since `g` is allowed for `x`. Therefore `t_g<=k-2`, and the conditional fraction is at most `(1+t_g)/(L+t_g)<=(k-1)/(L+k-2)`. For the common gap use `t_g<=k-1`, yielding `k/(L+k-1)`. The uniform extension measure is a size-biased mixture over `Q`; the pointwise bound survives this mixture. QED.

For `k=7`, the noncentral bound is `6/(L+5)` rather than `7/(L+6)`. The nine dedicated tests check this inequality against literal-poset marginal counts on 32 seeded cases. This is a modest structural sharpening of the earlier generic gap-atom lemma, **not** a proof of the sharp balance bound without the finite census. Its historical novelty is unassessed.

## Adversarial failure: widening an outsider interval is not balance-monotone

A tempting way to extend a six-gap bound was to assume that widening an allowed insertion interval cannot decrease the balance constant. This is **false**, even within the seven-outsider class. Start with
`(-6:0),(-4:0),(-3:0),(-3:1),(-3:2),(-1:3),(0:4)`,
then replace just `(-3:2)` by `(-3:3)`. Both have width exactly seven and all outsider intervals have at most seven gaps. The exact full-poset and dual C++ checks give
`(E,B)=(836706,417008)` before and `(935968,458980)` after, so
`delta_before=208504/418353≈0.4983925` while `delta_after=114745/233992≈0.4903800`.
The strictly decreasing inequality is the exact cross-product `458980*836706 < 417008*935968`. Thus a naive monotonicity reduction from the six-gap result cannot justify the eight-gap result. This is a counterexample to a **proof strategy**, not to the one-third–two-thirds conjecture.

## Failed nine-gap extrapolation searches (not proof)

An exact dual-C++ challenge widened each interval of the previous six-gap sharp witness to length nine wherever the unique common gap remained valid: **43** one-interval expansions, none below `1951/4659`; the smallest observed balance was `67645/152781≈0.442758`. A separate seeded `Random(79009)` sample generated 5,000 tuples from the 2–9-gap interval types; **2,174** were valid and had at least one nine-gap interval. No tuple beat `1951/4659`; the sample minimum was `235446/512376≈0.459518`. Neither sample establishes anything about the complete nine-gap boundary. The next exhaustive count is 51,307,360.

## Primary literature and novelty boundary

- Brightwell–Wright, [*The 1/3–2/3 Conjecture for 5-Thin Posets*](https://doi.org/10.1137/0405037), SIAM J. Discrete Math. 5 (1992), 467–474. Their at-most-five-incomparables theorem does not imply the exact constant for our seven outsiders, which may each be incomparable with 13 elements.
- Olson–Sagan, [*On the 1/3–2/3 Conjecture*](https://arxiv.org/abs/1706.04985), Order 35 (2018), 581–596, includes special classes and symmetry-induced half-balanced pairs, but no identified sharp eight-gap constant.
- Chen, [*A Family of Partially Ordered Sets with Small Balance Constant*](https://doi.org/10.37236/7337), Electron. J. Combin. 25 (2018), gives examples tending to ~0.3488999, outside this particular restricted family.
- Aires–Chan–Pak–Panova, [*Breaking the Infinite Barrier in the 1/3–2/3 Conjecture*](https://arxiv.org/abs/2609.30888), posted 2026-09-25, revised 2026-10-28, gives a universal improvement over the 1995 general bound, not an identified sharp fixed-seven-outsider constant.
- The prior [six-gap certificate](M079_CHAIN7_LOCAL.md) covers 436,680 normalized configurations, and its out-of-scope seven-gap challenge covers 2,612,268. Neither is an eight-gap proof.

Search and abstract comparison as of 2026-11-02 did not locate the exact quantitative eight-gap claim; this is **not** evidence of historical novelty. Older near-chain, bounded-width, interval-order and linear-extension literature still requires specialist inspection.

## Assumptions, limitations, failed paths and next falsifiers

Uniform linear-extension measure, finite posets, exactly seven outsiders forming an antichain, width exactly seven, 2–8 gaps for every outsider, exact integer arithmetic, and the interval/Helly reduction are all essential. The two C++ recurrences share interval normalization, so a common reduction error is possible; the literal-poset checker targets this risk but covers only sampled configurations. The FNV64 transcript is a drift check, **not** a cryptographic proof. No independent mathematician has accepted the proof or established novelty.

The existing all-orders gap-atom lemma gives a `1/3`-balanced outsider-chain pair if any interval has length at least `2k+1=15` for `k=7`; for the stronger `1951/4659` target its direct threshold is length 38. Thus it does **not** close the nine-through-37-gap region. A wider-class conclusion requires a new structural argument or larger exact search; merely counting more slots is not the objective.

**Next falsifiers:** any valid eight-gap tuple with balance below the claimed fraction; an omitted multiset in the inclusion-exclusion count; a mismatch in all-pair integer numerators or a full-poset check; overflow; an invalid Helly/width implication; or a primary historical source establishing the same bound. The immediate computational boundary is nine allowed gaps (51,307,360 normalized multisets). Obtain independent specialist review before any accepted outcome, novelty promotion or solved-state change. The separate PR-landing workflow is untouched.
