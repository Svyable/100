# M079 — sharp eight-outsider five-gap balance certificate (candidate)

**Work ID:** `X-M079-CHAIN8-FIVEGAP`; [claim #264](https://github.com/Svyable/100/issues/264).
**Claim digest:** `942df0b779572efeb770428d95ebce6bda37b9a4bd0247465706c50ff21da08b`.
**Status (2026-11-02):** author-derived, computer-assisted **restricted theorem candidate**, not an independently accepted result. Historical novelty unestablished. The unrestricted one-third–two-thirds conjecture remains open.

## Exact claim and sharpness

Let `P` be a finite poset consisting of a designated chain `c_1 < ... < c_m` and **eight pairwise incomparable** elements `x_0,...,x_7`. Assume the width of `P` is **exactly eight**, and each outsider has **between two and five permitted insertion gaps** in the chain (equivalently, is incomparable with between one and four chain elements). For uniformly random linear extensions define

`delta(P) = max_{u != v} min(Pr(u before v), Pr(v before u))`.

The proposed sharp result is

`delta(P) >= 22648/50201 = 0.4511463915061453...`.

Equality occurs, in the normalized interval representation below, in exactly **two** interval multisets related by order duality. This statement covers arbitrary chain lengths through forced outer padding; it does **not** cover six-gap outsiders, width nine, comparable outsiders, or all posets of width eight.

## Structural reduction, with all assumptions

Index the chain's insertion gaps by `0,...,m`. The chain elements below an outsider form a prefix, those above it a suffix, and its permitted gaps are therefore an integer interval `I_i=[a_i,b_i]`. Conversely, any such interval gives the corresponding chain–outsider relations. Each has `2 <= b_i-a_i+1 <= 5`.

Two disjoint outsider intervals would force the corresponding outsiders to be comparable via an intervening chain element, contrary to the antichain hypothesis. Pairwise intersecting integer intervals share a common gap (interval Helly). If the common intersection contained two consecutive gaps, the chain vertex between them would be incomparable with all eight outsiders, giving an antichain of size nine. Thus width exactly eight forces the common intersection to be **one** gap. Conversely, a common single gap prevents a nine-element antichain: any antichain of size nine would contain all eight outsiders and a chain vertex incomparable with all of them. Translate the unique common gap to zero:

`a_i <= 0 <= b_i, max_i a_i=0, min_i b_i=0, 2 <= b_i-a_i+1 <= 5`.

All chain elements outside the union of intervals are comparable with all outsiders, have fixed relative placement, and cannot change an incomparable pair's order probability. Delete this padding. The remaining gap span is at most `[-4,4]`, hence at most eight chain elements and 16 total vertices. This is an **all-chain-length reduction**, not an enumeration restricted to original chains of length eight.

There are `N=2+3+4+5=14` permitted intervals containing zero, with four having `a=0` and four having `b=0`; these two groups are disjoint. Sorting the eight intervals removes outsider-label permutations. Inclusion–exclusion gives exactly

`C(21,8) - 2*C(17,8) + C(13,8) = 156157`

eligible multisets, requiring at least one left-zero and one right-zero endpoint. Direct generation checks the same count. No continuous or probabilistic approximation enters the proof obligation.

## Two distinct exact finite counting methods

The C++17 source `scripts/m079_chain8_fivegap.cpp` enumerates **all 156,157** sorted eligible multisets and checks, for each, both exact integer algorithms against each other on the total number `E` of linear extensions, all 28 outsider-pair before-counts and every outsider's insertion-gap marginal.

1. **Sequential order-ideal DP:** a state `(q,S)` records the chain prefix length `q` and which outsiders have already been placed. It transitions by placing one legal outsider in gap `q`, or the next chain vertex if doing so would not pass an unplaced outsider's deadline. Forward and backward counts `F,B` give the number of extensions and event counts `F[state] * B[next]`.
2. **Factorial gap-block DP:** for each gap, choose a subset `T` of still-unplaced outsiders eligible there, including all whose last permissible gap has arrived. Weight the block by `|T|!`, independently of the one-at-a-time state transitions. For a pair in the same block, exactly half of these permutations put either one first; pairs in different blocks have the gap order. Forward/backward weighted transfers give the same totals and all marginals.

The best numerator is the maximum of `min(N,E-N)` over every outsider pair and outsider–chain threshold, where `N` is the relevant before-count. The checker requires `3*best >= E` as a separate sanity guard, and minimizes `best/E` by **integer cross multiplication**. Every compared count is well below 64-bit unsigned capacity (the reduced poset has at most 16 vertices). The full normalized transcript (intervals, `E`, best numerator) has FNV64 regression digest `36b2327ab1fb0f89`; this is **not** a cryptographic proof or independent review. Both recurrences agree on all 156,157 cases, with zero mismatches and exactly two normalized minimizers.

A third, structurally different Python implementation, `scripts/m079_chain8_fivegap.py`, builds the **literal full-poset predecessor matrix** and counts all linear extensions and pair events by a `2^n`-state topological-order DP. It independently reproduces the sharp witness, its order dual, 35 fixed-seed valid multisets (including repeated intervals), and the six-gap boundary witness below. A further literal topological-sort enumeration of a ten-element control (144,576 extensions) agrees on every pair count. An intentional mutation that counts same-gap pair order as all rather than half is rejected by the C++ dual comparison. These are independent *algorithms* by the same author, not independent mathematical specialist validation.

## Explicit sharp witness

Use the eight-vertex chain with gaps `-4,-3,...,4`, and outsider intervals

`[-4,0], [-3,1], [-2,0], [-2,1], [-1,1], [0,1], [0,2], [0,4]`.

The common intersection is exactly zero and every interval has length 2–5, so the poset meets every hypothesis. Exact counts are `E=1204824` and `best=543552`, giving `543552/1204824 = 22648/50201`. For example, `Pr(x_1 before x_3)=661272/1204824`; its reverse has numerator `543552`. All other incomparable pairs have smaller or equal smaller-side numerator, as verified by the literal predecessor-matrix DP.

The only other normalized minimizer is the order dual:

`[-4,0], [-2,0], [-1,0], [-1,1], [-1,2], [-1,3], [0,2], [0,4]`.

This two-minimizer assertion is only about sorted normalized interval multisets, not a complete poset-isomorphism classification.

## Adversarial boundary and failed avenues

**Six-gap extrapolation fails.** The eight intervals

`[-5,0], [-3,0], [-2,2], [-2,3], [-1,0], [-1,3], [0,3], [0,4]`

form a valid width-eight poset with an outsider allowed **six** gaps. Exact counts from the C++ and literal full-poset checker are `E=3193368`, `best=1425408`, so `delta=59392/133057 = 0.4463650916524497...`, **strictly below** `22648/50201`. This refutes extension of the five-gap sharp constant to six gaps; it does not refute the five-gap result or the one-third–two-thirds conjecture. A separate author-side *single-recurrence* scan of all `1,604,845` six-gap normalized multisets found this as the smallest value with multiplicity two (FNV64 `1571ec2ec3a4c35a`), but that larger-scope sharpness observation is **not claimed** as a theorem and lacks a full dual-census check.

Other failed shortcuts: `delta >= 1/2` is false even in the five-gap class (the explicit sharp witness); independent uniform insertion-gap weights would miss the factorial multiplicity of outsiders sharing a gap; a two-gap common intersection creates width nine and is outside the theorem. The previous seven-outsider constant `1951/4659` cannot simply be transplanted to eight outsiders as a sharp value. All claims about exact minima rely on complete finite enumeration, not a closed-form inequality for arbitrary `k`.

**Next falsifiers:** Audit the Helly/width equivalence and the two transition rules independently; replay the 156,157-case core in a separate language or proof assistant; attack the six-gap boundary with a fully separate dual census; inspect seven-gap outsiders; and request a specialist historical-novelty comparison. A flaw in either structural reduction or pair-event accounting invalidates the candidate theorem.

## Reproduce and review

From a repository checkout with Python 3.12+ and a C++17 compiler:

```sh
python3 scripts/m079_chain8_fivegap.py --check
python3 -m unittest discover -s tests -p 'test_m079_chain8_fivegap.py' -v
python3 scripts/regen.py --check --fast
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

The complete dual 156,157-case census took about **14.6 seconds** including compilation and process startup on the author-side macOS host (the bare C++ sequential pass took about 5.7 seconds). A separate out-of-scope 1,604,845-case six-gap sequential scan took 57 seconds. These are observed approximate wall times, not controlled benchmark trials. All commands, failed attempts, seeds and source paths above are reproducible; no external solver is trusted.

## Primary-literature comparison (checked 2026-11-02)

- Brightwell–Wright, [*The 1/3–2/3 Conjecture for 5-Thin Posets*](https://doi.org/10.1137/0405037), *SIAM J. Discrete Math.* 5 (1992), 467–474: proves the one-third threshold when each element has at most five incomparables, but not this sharp quantitative width-eight local constant. Each outsider here is incomparable with seven other outsiders and up to four chain vertices.
- Olson–Sagan, [*On the 1/3–2/3 Conjecture*](https://arxiv.org/abs/1706.04985), *Order* 35 (2018): several special classes and automorphism-based half-balanced pairs. The witness intervals are all distinct, so a simple outsider-swap symmetry does not explain its constant.
- Chen, [*A Family of Partially Ordered Sets with Small Balance Constant*](https://doi.org/10.37236/7337), *Electronic J. Combin.* 25 (2018): general families with smaller balance, not this fixed eight-outsider class.
- Aires–Kahn, [*Balancing Extensions in Posets of Large Width*](https://arxiv.org/abs/2509.11549) (2025), and Aires, [*Proof of the Kahn Saks Conjecture*](https://arxiv.org/abs/2609.30895) (2026-09-25): asymptotic large-width balance results; no claim here that a fixed width of eight triggers their near-half asymptotic conclusion.
- Aires–Chan–Pak–Panova, [*Breaking the Infinite Barrier in the 1/3–2/3 Conjecture*](https://arxiv.org/abs/2609.30888), posted 2026-09-25, revised 2026-10-28: improves the **general** lower bound, not an identified exact eight-outsider local constant.
- [Existing seven-outsider six-gap result](M079_CHAIN7_LOCAL.md) and [concurrent seven-outsider eight-gap claim #259](https://github.com/Svyable/100/issues/259) have different hypotheses and are not imported into this proof.

A targeted source search did not locate the exact `22648/50201` constant. This is **not proof of historical novelty**. The finite certificate, meaning of the theorem, and novelty all require external independent review. No problem solved status, coverage, acceptance, or Project 100 PR Landing automation was changed.
