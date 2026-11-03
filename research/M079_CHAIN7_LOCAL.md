# M079 — exact seven-outsider six-gap local balance certificate

**Work ID:** `X-M079-CHAIN7-LOCAL`; [claim #256](https://github.com/Svyable/100/issues/256).
**Scope SHA-256:** `02396fc31e0a62d19ffa8140676e82faad2040263d1d36a398a8a51499d50f11`.
**Status (2026-11-02):** author-derived **restricted theorem candidate** with exhaustive exact finite core and independent-algorithm checks. Historical novelty and independent specialist mathematical acceptance **not established**. No unrestricted one-third–two-thirds theorem, solved-state change, or new coverage slot.

## Precise theorem candidate

Let (P) be a finite poset consisting of a designated chain (c_1<\cdots<c_m) and exactly **seven** other elements (x_0,\ldots,x_6). Assume (i) the outsiders are pairwise incomparable; (ii) (P) has width exactly seven; (iii) each outsider is incomparable with between **one and five** chain elements, equivalently has **two to six** allowed insertion gaps. For uniformly random linear extensions (L), define

[
\delta(P)=\max_{u\ne v}\min\{\Pr_L(u\prec v),\Pr_L(v\prec u)\}.
]

The proposed sharp bound for this class is

[
\boxed{\delta(P)\ge \frac{1951}{4659}=0.4187593904\ldots}.
]

Equality is attained by a 17-element example described below. The claim applies to arbitrarily long designated chains through comparable outer padding; it does **not** apply when an outsider has seven or more insertion gaps, when the width is eight, or when outsiders have comparabilities. The unrestricted M079 conjecture remains open.

## Reduction to a finite complete certificate

Write the (m+1) chain insertion gaps as (0,\ldots,m). The chain predecessors of each outsider form a prefix and the chain successors a suffix, so the allowed gaps form an integer interval (I_i=[a_i,b_i]). Each interval has length (2\ldots6).

If two such intervals were disjoint, a chain vertex would lie between their forced positions and force the outsiders to be comparable. Since the outsiders are an antichain, the intervals pairwise intersect. Helly's theorem for integer intervals gives a common gap. If they had two common consecutive gaps, the intervening chain vertex would be incomparable to all seven outsiders, yielding an eight-element antichain. Conversely, one common gap precludes an eight-element antichain (there is only one chain element available in any antichain). Thus width exactly seven is equivalent here to **one** common gap. Translate it to zero:

[
\max_i a_i=\min_i b_i=0,\quad a_i\le0\le b_i,\quad2\le b_i-a_i+1\le6.
]

Chain vertices strictly outside the union of the seven gap intervals are comparable with all outsiders and appear as a fixed prefix/suffix in every extension; deleting them does not change any pair-order probability involving an incomparable pair.

There are (N=\sum_{\ell=2}^6\ell=20) possible intervals containing zero. Of these, five have (a=0), and a disjoint five have (b=0). After sorting the seven intervals (only relabeling symmetric outsiders), the number of eligible multisets is exactly

[
\binom{26}{7}-2\binom{21}{7}+\binom{16}{7}
=\boxed{436680}.
]

The independent Python combinatorial count also gives 4,887 cases at maximum length four and 55,432 at length five. The reduced core has at most ten chain vertices, 17 total vertices, and at most (17!/10!=98,017,920) linear extensions. Exact unsigned 64-bit arithmetic is sufficient for the extension counts and fraction comparisons.

## Two exhaustive exact integer algorithms

`scripts/m079_chain7_local.cpp` checks all 436,680 sorted interval multisets by **both** recurrences, requiring equality of the full extension count, every 21 outsider-pair numerator, and every outsider's per-gap marginal vector.

1. **Sequential order-ideal DP:** states ((q,S)), with (q) chain vertices already placed and outsider mask (S). The next chain element is legal only when no unplaced outsider's last allowed gap has been passed. Each outsider can be placed only in its allowed gap. Forward/backward path products count the total and pair-order numerators.
2. **Factorial gap-block DP:** at gap (q), choose a subset (T) of eligible outsiders containing all whose last gap is (q); weight this block by (|T|!). For a pair placed in the same block, precisely half of the block permutations put one before the other. This is a different transition structure, not a second invocation of the sequential DP.

All 436,680 cases agreed on all integer outputs. The minimum is attained by exactly **one normalized interval multiset** (not an isomorphism census of all posets). The deterministic noncryptographic FNV64 transcript digest is `1779f630db5c21b2`. The certificate checks the integer comparison for each case, not floating-point approximations. This is a computer-assisted finite proof candidate: correctness still depends on the stated reduction and both algorithms' implementation.

A third checker, `scripts/m079_chain7_local.py`, constructs the **literal full-poset predecessor matrix**, then counts linear extensions by a general (2^n)-state topological-order DP, with independent forward/backward counts for all pairs. It agrees with the two C++ recurrences on the sharp witness and 30 fixed-seed valid interval multisets. This checks a separate representation, not merely the same gap recurrence rewritten.

## Sharp witness and explicit falsifier

Take the ten-vertex chain with gaps (-5,-4,\ldots,5), and the seven outsiders' allowed intervals

[
[-5,0],\ [-2,0],\ [-2,2],\ [-1,0],\ [0,1],\ [0,2],\ [0,5].
]

The common intersection is exactly gap zero, all intervals have length at most six, and the width is seven. The exact number of linear extensions is (E=107157); the largest smaller-side pair-order count is (B=44873). Since (gcd(E,B)=23), this gives (B/E=1951/4659).

For outsider (x_0), its extension-weight vector across gaps (-5,\ldots,5) is
`10419,10419,10419,13616,17776,44508,0,0,0,0,0`.
The cumulative mass through gap (-2) is (44873), giving a pair attaining the bound. The general-poset checker independently reconstructs all pair counts and verifies that no pair is more balanced.

In particular the stronger conjecture (delta\ge21/50) for this class is **false** because (1951/4659<21/50). Likewise the six-outsider local candidate constant (1292/3003) does not automatically extend to seven outsiders. These are counterexamples to *extrapolations*, not to the original one-third–two-thirds conjecture.

## Reproduction, adversarial controls, and limitations

From repository root with Python 3.12+ and a C++17 compiler:

```sh
python3 scripts/m079_chain7_local.py --check
python3 -m unittest discover -s tests -p 'test_m079_chain7_local.py' -v
python3 scripts/regen.py --check --fast
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

The full dual C++ census took 10.67 seconds of CPU time on the author-side macOS machine, excluding compilation and the Python literal checks. The Python wrapper checks the expected count, sharp value, unique normalized witness, digest, 30 seeded independent-representation controls, and an intentional same-gap pair-order mutation which must be detected. Dedicated tests also check width-eight invalidity, singleton-gap invalidity, overlong intervals, outsider relabeling and order duality.

**Failed avenues / boundaries:** The sharp value for length at most four is (30028/66162=15014/33081\approx0.453856), so a simple half-balanced-pair assertion is false already at that shorter boundary. Treating all outsider insertions as independent fails when two land in the same gap: the (|T|!) factor is necessary. Replacing the same-gap pair's half-count by a full-count is rejected by the two counters. A generic five-incomparability-degree theorem does not directly cover the 17-element witness: each outsider can be incomparable to six other outsiders plus up to five chain vertices. No evidence here establishes a stronger constant for all seven-outsider intervals or the conjecture for arbitrary posets.

**Out-of-scope boundary challenge:** A separate full two-recurrence replay of **2,612,268** normalized multisets at maximum length seven found the **same** minimum and unique normalized witness (FNV64 `ddf3099a939db06b`; 74.61 seconds of CPU time). Reproduce using `clang++ -std=c++17 -O3 scripts/m079_chain7_local.cpp -o /tmp/chain7 && /tmp/chain7 --max-length 7 --dual`. This extra check is not part of the claim digest and is not used to widen the stated theorem.

**Next falsifiers:** Exhaust the length-eight boundary, independently inspect the Helly/width equivalence and integer DPs, verify the witness from a second programming language or formal proof assistant, and obtain a specialist prior-art review of quantitative chain-plus-antichain balance constants. If a full-length-seven census finds a smaller constant, the six-gap theorem remains unaffected.

## Primary literature comparison (checked 2026-11-02)

- Brightwell–Wright, [*The 1/3–2/3 Conjecture for 5-Thin Posets*](https://doi.org/10.1137/0405037), *SIAM J. Discrete Math.* 5 (1992), 467–474: proves the conjectural **one-third** threshold when each element has at most five incomparable others; does not supply this sharp (1951/4659) constant.
- Olson–Sagan, [*On the 1/3–2/3 Conjecture*](https://arxiv.org/abs/1706.04985), *Order* 35 (2018), 581–596: special poset classes and exact half-balanced pairs from certain automorphisms; the witness's seven intervals are all distinct, so that symmetry criterion does not force (1/2).
- Zaguia, [*The 1/3–2/3 Conjecture for N-Free Ordered Sets*](https://doi.org/10.37236/2345), *Electron. J. Combin.* 19 (2012): a different forbidden-subposet class; no claim that all these examples are N-free.
- Chen, [*A Family of Partially Ordered Sets with Small Balance Constant*](https://doi.org/10.37236/7337), *Electron. J. Combin.* 25 (2018): provides much lower general balance examples, not this local-class exact constant.
- Aires–Chan–Pak–Panova, [*Breaking the Infinite Barrier in the 1/3–2/3 Conjecture*](https://arxiv.org/abs/2609.30888v2), revised 2026-10-28: a small improvement to the best general lower bound, not a claimed sharp seven-outsider local-class constant.
- [Prior repository five-outsider bound](M079_CHAIN_PLUS_FIVE.md) and the [separate six-outsider claim #255](https://github.com/Svyable/100/issues/255) are different scopes. The latter is not assumed in this proof.

A targeted primary-source comparison did **not** locate the exact seven-outsider six-gap bound, but absence from these sources is **not** historical novelty evidence. This remains a candidate pending independent mathematical and literature review.
