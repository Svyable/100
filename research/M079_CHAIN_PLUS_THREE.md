# M079 — sharp 11/28 balance for a width-three chain-plus-three class

**Work packet:** `O-M079-02`, scope digest `6f875a09c8b9a70a`.
**Claim:** [#180](https://github.com/Svyable/100/issues/180).
**Classification:** author-derived restricted all-orders **proof candidate**, with two exact finite implementations and literal permutation controls. Neither an independent mathematical review nor historical novelty is established. The original 1/3–2/3 conjecture remains open. The new obligation remains open for review.

## Exact statement

Let `P` be a finite poset with a specified chain `c1 < ... < cm` and three elements `x,y,z` outside the chain. Assume:

1. `x,y,z` are **pairwise incomparable**;
2. `P` has **width exactly three**;
3. each of `x,y,z` is incomparable with **at least one** chain element.

For a uniformly chosen linear extension let
`delta(P) = max_(u!=v) min(Pr(u<v), Pr(v<u))`.

**Claim (sharp restricted theorem):** `delta(P) >= 11/28`. This is sharp, already for a seven-element poset with four chain elements. In particular it proves the one-third–two-thirds inequality for this infinite class with a quantitative margin. It says nothing about a general width-three poset, about three outsiders that are not an antichain, or about historical novelty.

The requirement that all three outsiders have a chain incomparability is material: it excludes the chain-plus-two subclass treated separately in [M079_CHAIN_PLUS_TWO.md](M079_CHAIN_PLUS_TWO.md). The sharp seven-element example below has no chain of five elements, so it cannot be placed in that earlier class.

## All-orders reduction

Number chain insertion gaps `0,...,m`. The allowable gaps for an outsider `u` form a **nonempty integer interval** `I_u=[a_u,b_u]`: any earlier chain vertex must precede `u`, and any later one must follow it. Conversely every gap in the interval is legal.

Two outsiders are incomparable only if their intervals intersect (otherwise the chain forces their order). By the interval Helly property the three intervals have a common gap. If their common intersection included **two consecutive gaps**, the chain vertex between those gaps would be incomparable with all three outsiders, giving a four-element antichain, contrary to width three. Therefore the triple intersection consists of **exactly one gap**. Translate that gap to zero. Each interval then has length at least two by hypothesis, contains zero, and the unique common gap is zero. Arbitrary chain vertices entirely outside the union of intervals are comparable with every outsider and do not affect any incomparable-pair probability.

Let `I,J,K` be the three gap sets with lengths `L,M,N`. For fixed gaps `i,j,k`, the number of linear extensions is the product of factorials of the multiplicities of equal gaps. Exactly,
`w(i,j,k) = 1 + [i=j] + [i=k] + [j=k] + 2[i=j=k]`.
Consequently, writing `r_AB=|A intersect B|` and `t=|I intersect J intersect K|=1`, the total number of extensions is

`E = LMN + r_IJ*N + r_IK*M + r_JK*L + 2t.`

For a fixed insertion gap `i in I` of `x`, its extension weight is

`w_x(i) = MN + r_JK + N*[i in J] + M*[i in K] + 2*[i in J intersect K].`

For outsider pair `x,y`, the exact numerator `E Pr(x<y)` is

`sum_(i in I, j in J, i<j) (N+[i in K]+[j in K]) + sum_(i in I intersect J) (N+2*[i in K]).`

For chain vertex `c_q`, the numerator `E Pr(x<c_q)` is `sum_(i in I, i<q) w_x(i)`. Permuting `x,y,z` gives every remaining incomparable pair. All computations use integers, not floats.

### Long-interval lemma

Put `B=MN+r_JK`. The intervals `J,K` intersect, so `B>=MN+1`. For positive integers `M,N`, `M+N<=2MN`, hence
`w_x(i) <= B+M+N+2 <= 3B`.
As `E=sum_(i in I) w_x(i)>=LB`, every atom of the insertion-gap distribution of `x` has probability at most `3/L`.

If **any** of `L,M,N` is at least **14**, its atom masses are at most `3/14`. Scan the chain thresholds from left to right. The first cumulative probability reaching `11/28` is at most
`11/28+3/14=17/28`. The crossing occurs at a genuine chain vertex: the final atom is at most `3/14`, so the preceding cumulative value is at least `11/14`. Thus an `11/28`-balanced pair exists. This is a symbolic, all-orders argument; no bound on the original chain length is assumed.

### Finite residual

It remains to check `2<=L,M,N<=13`. For each length `L`, all intervals containing zero are `[a,a+L-1]` with `1-L<=a<=0`. Enumerate all ordered triples of such intervals and retain precisely those with `max(a_x,a_y,a_z)=min(b_x,b_y,b_z)=0`. This produces **67,392 labeled normalized triples**; they are actual possible width-three posets up to irrelevant outer chain padding. There is no symmetry quotient and no omitted interval configuration.

For each triple, `scripts/m079_chain3_balance.py` evaluates every outsider–outsider and outsider–chain pair using the closed formulas above, and separately reconstructs **all** extension counts by a state recurrence over order ideals `(chain-prefix length, outsider-mask)`. It asserts exact agreement for every pair and tests `28*best >= 11*E`. The smallest balance is exactly **11/28**, attained in **12 labeled normalized triples**. The deterministic full-census transcript digest is:

`0414a61f4d9cbc33afa4fd6aeea4c0e70304498bb5a7e4a066d686fa8eb3facf`

The recurrence counts each legal next chain or outsider insertion, using prefix/suffix path counts to reconstruct pair events. It is algorithmically distinct from the closed multiplicity formula, although both are implementations by the same author and neither substitutes for external mathematical review.

## Sharpness, falsified strengthening and scope

Take the chain `c1<c2<c3<c4` and outsiders with allowed gap intervals
`I_x=[0,3], I_y=[2,3], I_z=[3,4]`; leave `x,y,z` pairwise incomparable. Their triple intersection is gap three, each interval has length at least two, and the width is exactly three. There are exactly **28** linear extensions. Direct enumeration of all `7!=5040` permutations gives the same 28 and all pair numerators as both other checkers. The best pair has probability `11/28` (for example `y<c3`); all other pairs are no better. Therefore the proposed stronger `2/5` bound is **false**, with a concrete seven-element counterexample.

The poset has height four, so is not covered merely by a height-two result. The class has unbounded incomparability degree (take `I_x=[-h,0], I_y=[-1,0], I_z=[0,1]` for arbitrarily large `h`), so a fixed-thinness theorem alone does not cover it. These exclusions are not a complete novelty audit.

**Failed avenues and limits:** The atom bound `3/L` does **not** by itself close length 13, since `3/13>3/14`; those cases are genuinely in the finite residual. The naive `LMN` denominator is false because ties within gaps create multiple extensions. The `2/5` strengthening fails at the sharp witness. Dropping the antichain, width-three, or minimum-two-gap hypotheses invalidates this reduction and is not certified.

## Reproduction and adversarial controls

```sh
python3 scripts/m079_chain3_balance.py --check --json
python3 -m unittest discover -s tests -p 'test_m079_chain3_balance.py' -v
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

The first command checks all **67,392** cases twice and prints the SHA-256 digest. The tests additionally use a **third** implementation that literally enumerates permutations on small instances, including the sharp example, and check translation, order duality, interval invalidity, width-four exclusion, the singleton boundary, the false `2/5` bound, and a mutation omitting same-gap multiplicity. No random seeds or external numerical solvers are used. The independent-DP label means an independent *algorithmic path*, not an independent reviewer.

## Primary literature comparison (2026-11-01)

- [Brightwell and Wright, *The 1/3–2/3 Conjecture for 5-Thin Posets* (1992)](https://doi.org/10.1137/0405037): fixed incomparability-degree bound, unlike this unbounded-degree family.
- [Zaguia, *The 1/3–2/3 Conjecture for N-Free Ordered Sets* (2012)](https://doi.org/10.37236/2345): a different forbidden-poset restriction; overlap not comprehensively audited.
- [Olson and Sagan, *On the 1/3–2/3 Conjecture* (2018)](https://arxiv.org/abs/1706.04985): known families and balanced-pair arguments, no exact matching sharp `11/28` theorem found in this targeted search.
- [Chen, *A Family of Partially Ordered Sets with Small Balance Constant* (2018)](https://doi.org/10.37236/7337): constructions with balance near `0.3488999`, so this bound cannot hold universally.
- [Gupta, *The Gold Partition Conjecture Holds through Fourteen Elements* (2026)](https://arxiv.org/abs/2607.23926): finite exhaustive work; it does not establish the all-orders statement here.
- [M079 chain-plus-two prior result in this repository](M079_CHAIN_PLUS_TWO.md): a different, previously proposed sharp `4/11` class, itself unreviewed.

A targeted search for the phrase `11/28` with poset balance and for chain-deletion-three results did not identify an exact precedent, but **absence from search is not proof of novelty**. An expert should audit older near-chain, interval-insertion, dimension-two, and width-three literature.

**Next falsifier:** Independent human proof audit of the Helly/width reduction, 14-gap threshold, finite enumeration and seven-element sharp example; independently reimplement the 67,392-case enumeration from poset relations; search historical literature for an equal or stronger theorem; then try allowing one comparability among the three outsiders. Do not discharge `O-M079-02`, change `data/solved.json`, or classify novelty without that review.
