# M079 — sharp 25/61 balance for a chain plus four incomparable outsiders

**Work packet:** O-M079-03, claim [#183](https://github.com/Svyable/100/issues/183), canonical work-queue scope SHA-256 36362184e179a52f5dfa06a25f1b26725de83f0120ba68c3aaeecb7005e6541c (initial exploratory scope hash 200d987df8348755035077cd4aa34307114aa0198075031e1199abacebd5e1af).

**Classification:** author-derived, all-orders **restricted proof candidate** with a finite exhaustive integer core and two distinct exact algorithms. It is not independently mathematically reviewed, not historically established as novel, and not a solution of the unrestricted one-third–two-thirds conjecture. Do not change the Solved ledger.

## Precisely quantified claim

Let P be a finite poset consisting of a designated chain c1 < ... < cm and four elements x0,x1,x2,x3 outside the chain. Assume:

1. The four outsiders are pairwise incomparable.
2. P has width **exactly four** (not merely at least four).
3. Every outsider is incomparable with at least one chain element.

For a uniformly random linear extension L define

    delta(P) = max_{u != v} min(Pr_L(u before v), Pr_L(v before u)).

**Restricted theorem candidate:** Every such P satisfies **delta(P) >= 25/61**. The constant is sharp: a nine-element P has 183 extensions and delta(P) = 75/183 = 25/61. This is a quantitative result for an infinite width-four class, not a general width-four theorem. The proposed stronger 5/12 bound is false.

## Structural reduction (all chain lengths)

Number the m+1 gaps around the chain 0,...,m. An outsider x has a nonempty interval of allowed gaps I_x=[a_x,b_x], since its lower chain predecessors form a prefix and its upper chain successors a suffix. Its incomparability with a chain element is equivalent to |I_x| >= 2.

Because any two outsiders are incomparable, their gap intervals must intersect: otherwise a chain vertex separates them and forces an order relation. Intervals have the Helly property, so all four share a gap. If they shared two consecutive gaps, the intervening chain vertex would be incomparable with all four outsiders, making a five-element antichain. Width four therefore forces the common intersection to be a **single gap**. Translate it to 0:

    max_i a_i = min_i b_i = 0,   a_i <= 0 <= b_i,   b_i-a_i+1 >= 2.

Conversely these conditions define exactly the claimed class (up to padding by chain vertices outside the union of the intervals, which are comparable to all outsiders and leave all relevant probabilities unchanged). Permuting the four outsider labels does not change delta(P), so sorting the four intervals gives one representative per interval multiset. There is no assumption that the intervals themselves are distinct.

## Long-interval lemma: a 19-gap threshold

Fix outsider x with L=|I_x| allowed gaps. Remove x and let B be the number of linear extensions of the remaining chain plus three outsiders. For each such extension Q, write k_g(Q) for the number (0,...,3) of remaining outsiders in gap g. Reinserting x in gap g gives exactly 1+k_g(Q) legal positions, because all outsiders are pairwise incomparable. Thus

    w_x(g) = sum_Q (1+k_g(Q))
           = B * (1 + sum_{y != x} Pr_{P-x}(y is in gap g)).

For any one of the three remaining outsiders y, condition on a linear extension of P-{x,y}. It can be inserted in at least two allowed gaps. At a specified gap it has at most three insertion positions (two other outsiders may already occupy that gap); at any other allowed gap it has at least one. Hence, conditionally and unconditionally,

    Pr_{P-x}(y is in gap g) <= 3/(3+1) = 3/4.

Consequently w_x(g) <= (13/4)B. Since every allowed gap admits at least one insertion, the total number E of extensions of P satisfies E >= LB, so

    Pr_P(x is in gap g) = w_x(g)/E <= 13/(4L).

For L >= 19, 13/(4L) <= 13/76 < 11/61 = 1-2(25/61). Scan the cumulative distribution of x over successive allowed gaps. The first cumulative mass reaching 25/61 is at most 25/61 + 11/61 = 36/61. It is reached before the final gap (whose mass is at most 11/61). The intervening actual chain vertex therefore forms a 25/61-balanced pair with x. This is a symbolic proof for **every** chain length, with no finite-size assumption.

The crude bound w_x(g) <= 4B would require L >= 23 and was discarded. The conditional 3/4 bound is essential to reduce the finite core to length <=18; the estimate 13/(4*18) is *not* small enough for this crossing argument.

## Finite residual and two exact counting paths

It remains to check 2 <= |I_xi| <= 18 for all four outsiders. For each length ell, the ell intervals containing 0 are [a,a+ell-1] for a=1-ell,...,0. Enumerate nondecreasing quadruples of these intervals, retain only max(a_i)=min(b_i)=0, and count all linear extensions and pair-order numerators. There are **3,456,151 normalized interval multisets**. This is a complete finite reduction by the preceding lemma, not a census of all width-four posets.

The source file scripts/m079_chain4_balance.cpp checks every case using **two structurally different integer recurrences**:

* **Sequential order-ideal paths.** A state (q,mask) records q chain elements and the set of outsiders already placed. Add a legal chain element or one outsider. Forward and backward path counts yield E and every outsider-before-outsider and outsider-before-chain numerator.
* **Factorial gap blocks.** For each gap independently choose a subset T of eligible unplaced outsiders and weight the block by |T|!. A different forward/backward subset transfer counts extensions; when x,y share a block exactly half the block permutations put x before y. Every pair numerator and E must agree exactly with the sequential path implementation, not merely the final minimum.

The complete ordered transcript (each sorted interval multiset, E and best numerator) has SHA-256:

    79017e785d0fd236d5aa87fb1c2869fcf039c1e2a36fb75be667d3236a04be88

Both counters agree on all 3,456,151 cases. The minimum is **25/61**, attained by exactly **two** interval multisets under outsider permutations (not a claim about all unlabelled poset isomorphism classes). All comparisons use exact 64-bit integers, with the finite bound making their magnitudes safe. No SAT/LP solver or randomized sampling is involved.

## Sharp nine-element witness and adversarial checks

Use the four gap intervals

    I_x0=[-1,0], I_x1=[0,1], I_x2=[-1,1], I_x3=[-4,0].

The core chain has five vertices, corresponding to gaps -4,...,1. The common intersection is exactly gap 0; each interval has length at least two; the four outsiders form an antichain and no chain vertex is incomparable to all four. Thus width is exactly four. There are **183** linear extensions. The maximum smaller side among all pair-order counts is **75**, attained for instance by x3 versus the chain vertex separating shifted gaps 2 and 3. Directly enumerating all 9! = 362,880 permutations, rejecting those that violate the poset, independently recovers E=183 and all pair counts. Hence delta(P)=75/183=25/61 and the proposed 5/12 strengthening is false.

The witness contains an induced N (so the N-free theorem alone does not cover it), has a chain of five vertices (not a height-two case), and is not a semiorder (it contains a 3+1). The class has unbounded incomparability degree by lengthening one interval while keeping the other three of length >=2 with common gap 0; it is not automatically within a fixed 5-thin theorem. These observations do not constitute a complete literature novelty audit.

Adversarial tests reject a width-five shared-two-gap tuple, a singleton-gap outsider, nonoverlapping intervals and reversed endpoints; check all 24 outsider relabelings, order duality and the exact cutoff; and verify that a deliberate mutation replacing half of same-gap pair orders by all of them makes the two C++ counters disagree. This is an independent **algorithmic** path plus a third small-instance implementation, not independent specialist acceptance.

## Reproduction

From the repository root with Python 3 and a C++17 compiler:

    python3 scripts/m079_chain4_balance.py --check --json
    python3 -m unittest discover -s tests -p 'test_m079_chain4_balance.py' -v
    python3 scripts/regen.py --check
    python3 -m unittest discover -s tests

The --check command compiles the C++ census in a temporary directory, checks both counters for all cases and hashes the full transcript. --smoke checks 21,511 normalized cases with max interval length eight; --witness runs the independent literal-permutation test. All generated artifacts must be regenerated from their source ledgers, never manually merged.

## Literature and historical-novelty boundary (2026-11-01)

* Brightwell and Wright, [The 1/3–2/3 Conjecture for 5-Thin Posets](https://doi.org/10.1137/0405037), SIAM J. Discrete Math. 5 (1992): a bounded incomparability-degree class, not obviously this unbounded class.
* Zaguia, [The 1/3–2/3 Conjecture for N-Free Ordered Sets](https://doi.org/10.37236/2345), Electronic J. Combinatorics 19 (2012): a different forbidden-subposet class; the sharp witness has an induced N.
* Olson and Sagan, [On the 1/3–2/3 Conjecture](https://arxiv.org/abs/1706.04985), 2018: several known classes, including some dimension-two orders, but no exact matching 25/61 claim found in a targeted search.
* Chen, [A Family of Partially Ordered Sets with Small Balance Constant](https://doi.org/10.37236/7337), Electronic J. Combinatorics 25 (2018): unrestricted posets can have much smaller balances.
* Trotter, [Interval Orders and Interval Graphs](https://trotter.math.gatech.edu/papers/103.pdf): interval-order and poset balance context; this class may overlap stronger historical results and needs a specialist audit.
* [Earlier M079 chain-plus-three restricted candidate](M079_CHAIN_PLUS_THREE.md), 11/28: width three, not this width-four class.

The exact fraction 25/61 and this chain-plus-four class were searched in current literature, without locating an exact precedent. **Failure to find a source is not a novelty proof.** The result should remain a candidate until an independent expert checks the proof, exhaustive reduction, mathematical scope and relevant interval-order literature.

**Failed avenues and remaining falsifiers:** No counterexample to 11/28 was found; instead a sharper candidate 25/61 emerged. A naive product-of-interval-lengths count is false because equal-gap outsiders have factorial multiplicities. The crude 4/L atom bound leaves a larger finite core. The 5/12 strengthening fails on the nine-element witness. The next falsifiers are an independently written finite-case enumerator not sharing either C++ recurrence, a direct human audit of the conditional 3/4 insertion bound and common-gap reduction, a comprehensive older interval-order literature audit, and extension to five outsiders or to four outsiders with comparabilities. No claim of an unrestricted theorem or independent acceptance is made.
