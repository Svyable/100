# M079 — sharp 4/11 balance for width-three chain-plus-two posets

**Work packet:** `O-M079-01` · scope SHA-256 `964d45559b467d0b87968be82c006cf2c916e04bc8ad39c0b149dfe012b55411`.
**Claim:** [#178](https://github.com/Svyable/100/issues/178).
**Classification:** author-derived, restricted all-orders proof candidate with exact arithmetic and a separately implemented finite order-ideal checker. **No independent mathematical or historical-novelty review.** The obligation remains **open** pending the prescribed independent review; no claim about the full 1/3–2/3 conjecture.

## Precise theorem candidate

Let `P` be a finite poset of width **exactly three**, and suppose there are two elements `x,y` such that `P \\ {x,y}` is a chain. For the uniform distribution on linear extensions, write

`delta(P) = max_{u != v} min(Pr(u precedes v), Pr(v precedes u))`.

**Claim (sharp restricted bound).** Every such `P` satisfies

`delta(P) >= 4/11 > 1/3`.

The constant is sharp within this class: a five-element poset described below has precisely 11 linear extensions and `delta(P)=4/11`. No assumption about an arbitrary width-three poset is being made.

This is a candidate **infinite structural class theorem**, not an extension of a finite census or a result about all width-three posets. Its proof is finite algebra after an all-orders reduction.

## Proof: gap coordinates and all-orders reduction

Write the chain as `c1 < ... < cm` (with `m >= 1`), and number its insertion gaps `0,...,m`. An outsider `x` can be inserted in exactly the consecutive gaps `I=[a,b]`: it must follow `c_a` if `a>0` and precede `c_(b+1)` if `b<m`. Similarly `y` has `J=[c,d]`. The width-three hypothesis forces `x || y`, and forces some chain element incomparable with both. Consequently the intervals overlap in **at least two consecutive gaps**:

`r = |I intersect J| >= 2`.

Conversely, with `x||y`, such a two-gap overlap gives an antichain `{x,y,c_k}`, hence width three. Every pair of distinct gaps determines one extension; a common gap determines two (both relative orders of `x,y`). Thus, with `L=|I|`, `M=|J|`,

`E = e(P) = LM+r`.

The exact insertion-gap weights of `x` are `w_i=M+1_{i in J}`, so

`Pr(x before c_k) = [sum_(i in I, i<k) (M+1_{i in J})]/E`.

The analogous formula holds for `y`. For `x,y`, the numerator is `#{(i,j) in I x J : i<j} + r`. These are exact integer counts, not a simulation or asymptotic approximation.

**Large-interval lemma.** If `L>=5`, then `M>=2` and `r>=2`. Every atom of the insertion-gap distribution of `x` has mass at most

`(M+1)/(LM+r) <= (M+1)/(5M+2) <= 1/4 < 3/11`.

The last inequality is equivalent to `4(M+1)<=5M+2`, valid for `M>=2`. Scan the chain thresholds `Pr(x before c_k)` in increasing `k`. The first cumulative value reaching `4/11` is at most `4/11+3/11=7/11`. It occurs at a real chain element, not at the artificial terminal gap, because the final atom is at most `1/4`. Hence a `4/11`-balanced pair exists. By symmetry the same applies if `M>=5`.

**Finite residual.** It remains to check `2<=L,M<=4`, `r>=2`. Translate the gaps so that `min(a,c)=0`, and put `s=c-a`. Exactly 27 triples `(L,M,s)` survive. The following table gives an actual pair and its exact probability in **every** case. The notation `x,c2` means `Pr(x precedes c2)`; the `c_k` indices are relative to the translated origin, so translation back adds the same gap offset to `k`.

| L | M | s | witness | probability |
|---:|---:|---:|---|---:|
| 2 | 2 | 0 | x,y | 1/2 |
| 2 | 3 | -1 | x,y | 3/8 |
| 2 | 3 | 0 | x,y | 5/8 |
| 2 | 4 | -2 | y,c2 | 2/5 |
| 2 | 4 | -1 | x,y | 1/2 |
| 2 | 4 | 0 | x,c1 | 1/2 |
| 3 | 2 | 0 | x,y | 3/8 |
| 3 | 2 | 1 | x,y | 5/8 |
| 3 | 3 | -1 | x,c2 | 4/11 |
| 3 | 3 | 0 | x,y | 1/2 |
| 3 | 3 | 1 | x,c2 | 7/11 |
| 3 | 4 | -2 | y,c2 | 3/7 |
| 3 | 4 | -1 | x,y | 2/5 |
| 3 | 4 | 0 | x,y | 3/5 |
| 3 | 4 | 1 | y,c3 | 4/7 |
| 4 | 2 | 0 | y,c1 | 1/2 |
| 4 | 2 | 1 | x,y | 1/2 |
| 4 | 2 | 2 | x,c2 | 2/5 |
| 4 | 3 | -1 | x,c3 | 4/7 |
| 4 | 3 | 0 | x,y | 2/5 |
| 4 | 3 | 1 | x,y | 3/5 |
| 4 | 3 | 2 | x,c2 | 3/7 |
| 4 | 4 | -2 | y,c2 | 4/9 |
| 4 | 4 | -1 | y,c2 | 9/19 |
| 4 | 4 | 0 | x,y | 1/2 |
| 4 | 4 | 1 | x,c2 | 9/19 |
| 4 | 4 | 2 | x,c2 | 4/9 |

Every displayed fraction belongs to `[4/11,7/11]`. The integer gap formulas verify each row, and `scripts/m079_chain2_balance.py` checks both **completeness of the 27 parameter cases** and each fraction using exact `Fraction` arithmetic. This closes the stated restricted proof, subject to independent scrutiny of the model and all-orders reduction.

## Sharpness and genuine width-three boundary

Take `m=3`, `I_x=[1,3]`, `I_y=[0,2]`, with `x||y`. There are `3*3+2=11` extensions. The exact probabilities of all incomparable pairs give `delta(P)=4/11`, attained for `x,c2` (and its complementary orientation). This poset has the induced `N` pattern `y<c3`, `c1<c3`, `c1<x` and no other relations on `{y,c1,c3,x}`; thus the class is not contained in the classical N-free/series-parallel class.

For every `m>=3`, `I_x=[0,m-1]`, `I_y=[1,m]` yields width three and an induced N, while `x` is incomparable with `m-1` chain elements. Hence the all-orders class is also not contained in any fixed `k`-thin class (bounded incomparability degree). These observations only rule out **those particular** existing coverage arguments; they do not establish historical novelty.

The weaker proposed constant `5/11` is **false** on the five-element sharp example. A naive denominator `LM` is also false: it forgets the extra relative order in each common gap. The proof does not extend by this argument to deletion of three outsiders: the gap weights then depend on the mutual relative order of three elements and need not have the simple `M+1` form.

## Reproduction, adversarial checks and independent computation path

Run from repository root:

```sh
python3 scripts/m079_chain2_balance.py --check --json
python3 -m unittest discover -s tests -p 'test_m079_chain2_balance.py' -v
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

The main script verifies the 27 exact witnesses, symbolic large-interval boundary arithmetic, sharp example and a seeded collection of additional interval pairs. A **separate order-ideal recurrence** counts all linear extensions of the actual poset from predecessor bitmasks, adding a comparison edge to count pair events; it does not use the insertion-gap formula. The tests additionally enumerate literal permutations of every residual small poset as a third path. Mutation controls detect missing common-gap multiplicity, invalid intervals, an overlap-one case outside the width-three scope and the false stronger bound. This is computational corroboration, **not an independent person or specialist review**.

**Assumptions:** finite poset; width exactly three; deleting `x,y` leaves a chain; no additional comparability between `x,y`; uniform distribution on all linear extensions. `x,y` incomparability is forced by width three, rather than imposed on an arbitrary poset.

**Failure modes to challenge:** a poset with chain deletion two not captured by consecutive gap intervals; a width-three instance with fewer than two overlapping gaps; an omitted translated boundary threshold; a mismatch between exact pair counts and the order-ideal DP; or an earlier published theorem covering this exact class and constant.

## Source and novelty audit (2026-11-01)

Primary literature compared:

- Linial's width-two result, as described in [Olson–Sagan (2018)](https://arxiv.org/abs/1706.04985). Our sharp example has width three, so width two does not imply this statement.
- Brightwell–Wright, [*The 1/3–2/3 Conjecture for 5-Thin Posets* (1992)](https://doi.org/10.1137/0405037). The family above has unbounded incomparability degree.
- Zaguia, [*The 1/3–2/3 Conjecture for N-Free Ordered Sets* (2012)](https://doi.org/10.37236/2345). The sharp example and an infinite subfamily contain induced N.
- Olson–Sagan, [*On the 1/3–2/3 Conjecture* (2018)](https://arxiv.org/abs/1706.04985), including several dimension-two subclasses; no matching all-orders sharp chain-plus-two statement was identified in this targeted search.
- Chen, [*A Family of Partially Ordered Sets with Small Balance Constant* (2018)](https://doi.org/10.37236/7337), constructs unrelated constants approaching ~0.3488999, so a universal `4/11` bound is false.
- Gupta, [*The Gold Partition Conjecture Holds through Fourteen Elements* (2026)](https://arxiv.org/abs/2607.23926), gives finite exhaustive results, not an all-orders theorem for this class.

**Novelty unresolved.** The argument and exact `4/11` bound were derived in this run; this is **not** a claim that no mathematician has proved them before. A specialist must search older literature on near-chain posets, dimension-two posets, balance constants and chain deletion before any novelty classification.

**Next falsifier:** independent hand audit of the 27-row table and the cumulative-threshold lemma, followed by a literature search for an exact chain-plus-two theorem. A natural next proof problem is a quantitative bound for deletion of **three** elements, which is not implied by the present calculation. No unrestricted conjecture status or `data/solved.json` is changed.
