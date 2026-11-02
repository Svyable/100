# M079 — sharp bounded-local-incomparability balance for six antichain outsiders

**2026-11-02 UTC.** Work ID `X-M079-CHAIN6-BOUNDARY`; [claim #255](https://github.com/Svyable/100/issues/255). Scope SHA-256 `31eb289592fb6e4ca6728f065a218c3c0dc3df304444a7c87a29a6797f34e3c5`. **Evidence:** author-derived, exact-computation-backed restricted theorem **candidate**; no independent specialist proof review or historical-novelty determination. The general one-third–two-thirds conjecture remains open. This does not duplicate the [five-outsider claim #254](https://github.com/Svyable/100/issues/254).

## Precisely quantified claim

Let `P` be a finite poset consisting of a designated chain `c1 < ... < cm` and **six pairwise incomparable outsiders** `x0,...,x5`. Assume `width(P)=6`, and that each outsider is incomparable with **between one and seven chain vertices**. For uniformly random linear extensions put

`delta(P) = max_(u != v) min(Pr(u before v), Pr(v before u))`.

**Restricted theorem candidate:** `delta(P) >= 1292/3003 = 0.4302364302...`, with equality attained. Up to outsider permutations, translation of the common insertion gap and chain padding comparable to every outsider, the only two equality configurations are order duals. The class contains arbitrarily long chains, but the outsider-chain incomparability bound is essential. This neither proves the conjecture for all width-six posets nor settles the `2/5` extrapolation for *all* chain-plus-six posets.

## Structural reduction (all chain lengths)

An outsider's allowed insertion gaps in the chain form an integer interval `I_i=[a_i,b_i]`. The number of chain elements incomparable to it is `b_i-a_i`, so `2 <= |I_i| <= 8`. If two outsider intervals were disjoint, an intervening chain vertex would force those outsiders to be comparable. Their pairwise incomparability therefore makes all six intervals intersect pairwise. Helly's property for intervals gives a common gap. Two common consecutive gaps would make the chain vertex between them incomparable with all six outsiders, yielding width at least seven. Thus the intersection is **exactly one gap**, which we translate to zero:

`max_i a_i = min_i b_i = 0; a_i <= 0 <= b_i; 2 <= b_i-a_i+1 <= 8`.

Conversely, these conditions construct a width-exactly-six poset with six mutually incomparable outsiders. Chain vertices outside the union of these intervals are in a fixed prefix or suffix of every linear extension, and do not affect pair probabilities.

If two outsiders have identical intervals, transposing them is a poset automorphism, giving a perfectly balanced pair with probability `1/2`. This **known** automorphism argument (Olson–Sagan 2018) discharges all repeated-interval cases. Thus for the minimum below `1/2`, consider only distinct intervals.

There are `2+3+...+8=35` intervals of length `2..8` containing zero. Exactly seven have left endpoint zero and exactly seven have right endpoint zero, and these groups are disjoint. A singleton common intersection requires at least one from each group. The number of sorted, distinct six-interval configurations is therefore

`C(35,6) - 2*C(28,6) + C(21,6) = 923,944`.

The enumeration traverses **all** such configurations, not a random sample. The essential chain has at most 14 vertices, so `E <= 20!/14! = 27,907,200`, safely within 64-bit integer arithmetic.

## Proof certificate and independent paths

The full exact enumeration is implemented in [`scripts/m079_chain6_local.cpp`](../scripts/m079_chain6_local.cpp). The **sequential order-ideal recurrence** has states `(q,M)` with `q` chain elements and outsider subset `M` placed. An outsider can be placed if `a_i <= q <= b_i`; a chain step is allowed only when no unplaced outsider has deadline at or before `q`. Forward and reverse counts give the total number `E` of extensions, each outsider's gap marginals and all ordered outsider-pair counts. Prefix sums give outsider-chain pair counts. For `B(P)`, the maximum smaller-side numerator over all pairs, the exact claim is `3003*B(P) >= 1292*E(P)`.

A structurally different **factorial gap-block recurrence** selects, at each gap, a subset `T` of eligible unplaced outsiders, requires all outsiders with deadline at that gap, and weights the transition by `|T|!`. For two outsiders in the same block, exactly half of the orders put one before the other. This second algorithm independently recomputes `E` and `B` for every 97th configuration, **9,525** deterministic cases. The implementations agree on all checked cases; this is independent *algorithm design*, not independent specialist mathematical review.

Full local census, with exact rational comparison (not floats):

| Quantity | Result |
|---|---:|
| Eligible distinct interval multisets | **923,944** |
| Minimum `B/E` | **`25840/60060 = 1292/3003`** |
| Equality configurations | **2**, related by order duality |
| Independent factorial-block checks | **9,525** |
| 64-bit FNV-1a transcript fingerprint | **`9a36908f323ec1f1`** |

The fingerprint hashes all interval endpoints, extension counts and best-pair numerators in deterministic order. It is a drift detector, **not** a cryptographic authenticity proof.

## Literal sharp witness and independent relation-matrix replay

Take the six outsider intervals

`[-2,0], [-3,0], [0,3], [-2,2], [-6,0], [-2,4]`.

They have lengths `3,4,4,5,7,7`, singleton common gap zero, and ten essential chain vertices, so the poset has **16 vertices**. The exact counts are `E=60060` and `B=25840`, giving `delta=1292/3003`. One maximizing pair is `x5` against the chain vertex between gaps `0` and `1`. The other equality multiset is the order dual

`[0,2], [-3,0], [0,3], [-2,2], [-4,2], [0,6]`.

A third implementation in [`tests/test_m079_chain6_local.py`](../tests/test_m079_chain6_local.py) constructs the **literal 16-vertex predecessor relation** and counts all linear extensions by a full `2^16`-state ideal DP, independently of either gap recurrence. It independently obtains `60060` and `25840`, checking all 120 unordered pairs. It also agrees on 35 seeded small instances, order duality and outsider permutations. The naive product of gap-interval lengths is `11760`, **not** `60060`; this is a negative control against losing same-gap order multiplicities.

## Reproduction

From the repository root, with C++17 and Python 3:

```sh
c++ -std=c++17 -O3 scripts/m079_chain6_local.cpp -o /tmp/m079_chain6_local
/tmp/m079_chain6_local --max-length 8 --check
/tmp/m079_chain6_local --max-length 4 --check
/tmp/m079_chain6_local --instance '-2:0,-3:0,0:3,-2:2,-6:0,-2:4' --check
python3 -m unittest discover -s tests -p 'test_m079_chain6_local.py' -v
```

The full local census ran in about 35 seconds. Six dedicated adversarial test methods passed, including invalid shared-multiple-gap, singleton interval, missing outsider, invalid endpoint, duality, permutations and the independent full-poset recount. The `--check` gate rejects drift in the exact census, sharp ratio, equality count and transcript fingerprint. **Full repository regeneration, repository-wide tests and exact-head CI have not run** because a complete checkout was unavailable. No PR has been opened; this branch is an unreviewed research record, not an accepted result.

## Literature, negative paths, assumptions and falsifiers

Primary comparison: [Olson–Sagan, *On the 1/3–2/3 Conjecture* (2018)](https://arxiv.org/abs/1706.04985) includes the known automorphism-based perfect-balance observation; [Chen, *A Family of Partially Ordered Sets with Small Balance Constant* (2018)](https://doi.org/10.37236/7337) gives general posets with balance approaching `0.3488999`; [Aires–Chan–Pak–Panova (2026)](https://arxiv.org/abs/2609.30888) improves the general lower bound; [Aires–Kahn (2025)](https://arxiv.org/abs/2509.11549) concerns large-width asymptotics. The repository's [five-outsider bound](M079_CHAIN_PLUS_FIVE.md) and [claim #254](https://github.com/Svyable/100/issues/254) have a different scope. A targeted search on **2026-11-02** did not find the exact six-outsider `1292/3003` constant; absence from search **does not establish novelty**. Older near-chain and interval-order results require expert review.

**Failed attempts:** Adding a sixth interval to the known five-outsider `2/5` witness across 440 sixth-interval choices did not produce `delta<2/5`; the smallest was `1236/2753` for `[-5,0]` or `[0,5]`. A seeded random search of 200,000 six-interval configurations (seed `3719`) and 288,151 annealing evaluations (seed `73231`) likewise found no `delta<2/5` case. These are heuristic negatives and **prove nothing** about the unrestricted six-outsider class. An attempted exact length-nine census, containing 3,540,208 eligible configurations, exceeded the run budget; no length-nine conclusion is asserted.

**Material assumptions:** finite poset; designated chain; exactly six mutually incomparable outsiders; width exactly six; each outsider incomparable with 1–7 chain elements; uniform linear extensions. Nothing follows for longer intervals, comparable outsiders, width seven, or arbitrary posets. The only mathematical novelty candidate is the **sharp restricted constant and its equality classification**, not the Helly reduction or twin automorphism.

**Next falsifier:** a valid interval tuple within the stated class with `3003*B<1292*E`; an omitted interval in the 923,944-case classification; a disagreement on a full independent recurrence; an overflow or same-gap factorial error; or a primary historical theorem subsuming this result. For the broader six-outsider `2/5` question, analyze length-nine and longer intervals and seek a symbolic long-interval lemma. External scope/proof review and novelty audit are required before any accepted outcome or solved-status change. No coverage, evidence, benchmark, or separate Project 100 PR Landing task/cadence change was made.
