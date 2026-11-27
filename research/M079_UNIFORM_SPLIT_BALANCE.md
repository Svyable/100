# M079 — unconditional all-width balance for chain–antichain posets (candidate)

**Claim:** [#414](https://github.com/Svyable/100/issues/414), O-M079-05, exploratory scope SHA-256 `a4e556be5bfbd95f6a0838e55e29fa843e894c64c5b606fb8fa05c3bd3378c2f` (exact hashed text in issue). Date: 2026-11-27.

**Evidence:** author-derived all-orders mathematical argument with a small exhaustive exact residual certificate and a separately implemented counting algorithm. No conjectural mathematical inputs. Independent mathematical review and historical novelty audit are pending; do not classify this as an accepted new theorem or change the unrestricted M079 status.

## Statement

Let P be any finite non-total poset whose ground set is the disjoint union of a chain C and an antichain X. There is no bound on the size of either part, on the width, on the number of incomparable chain–outsider pairs, or on the common intersection of the insertion intervals. In a uniformly random linear extension, some incomparable pair has order probability in [1/3, 2/3].

This is the full one-third–two-thirds conclusion on the entire stated class, not the unrestricted conjecture. The constant 1/3 is sharp for the class: a two-element chain and one isolated element have three extensions, and both incomparable pairs have smaller-side probability 1/3.

## Proof

**1. Gap model and common intersection.** Write the chain as c_1 < ... < c_m and label its gaps 0,...,m. For x in X, let I_x=[a_x,b_x] be the consecutive integer gaps after all chain predecessors of x and before all chain successors of x. Since X is an antichain, an arbitrary assignment of each outsider to one of its allowed gaps, followed by an arbitrary permutation of outsiders within each gap, gives exactly a linear extension; conversely all extensions arise this way.

The intervals intersect pairwise: if b_x < a_y, then x < c_(b_x+1) <= c_(a_y) < y, contradicting the antichain hypothesis. By the elementary interval Helly property, there is a common gap h. Set k=|X| and translate h to 0. Let p_x(g) be the probability that x is in gap g. Chain comparison probabilities are its cumulative gap probabilities. If k=0 the poset is a chain; if k=1 the allowed gaps are equiprobable, and at least two are allowed in the nonchain case. A median threshold then has probability in [1/3,2/3]. Hence assume k>=2.

**2. Two-gap occupancy lemma (all k).** For each gap g define r(g)=#{y in X: g not in I_y}. For every x with g in I_x,
   
    p_x(g) <= p_x(0) <= (r(g)+1) p_x(g).           (1)

For g=0 this is equality. For distinct g and 0, fix the ordered words of outsiders in all other gaps and consider the remaining labeled elements, among them x. All remaining elements are eligible for gap 0. Let q be the number ineligible for g, and let the others be flexible. Encode the two gap words by a single permutation with a separator: the first word is for 0, the second for g. This is a counting device even when the actual chain order of the gaps is reversed. Exactly the q forced labels must occur before the separator; there is no restriction on the flexible labels. In a uniform admissible word, the relative order of x, the separator and the q forced labels is uniform among orders with all q forced labels before the separator. Of these, the fraction with x before the separator is (q+1)/(q+2), and the fraction with x after it is 1/(q+2). Indeed, the number of relative orders in the first case is (q+1)!, and in the second q!. Thus the counts of extensions with x in 0 versus in g in this fiber are in ratio q+1:1. Since 0<=q<=r(g), summing over all fibers establishes (1). Fibers with x already fixed outside the two gaps contribute zero to both counts. No independence or uniformity of the poset obtained by deleting x is assumed.

In particular 0 is a mode for every outsider. Dividing (1) by r(g)+1 and summing over allowed gaps gives

    p_x(0) <= 1 / (1 + sum_{g in I_x, g != 0} 1/(r(g)+1)).   (2)

**3. Eliminate nesting and repeated common gaps.** Suppose there is no 1/3-balanced pair anywhere in P. For each x all cumulative probabilities at actual chain vertices avoid [1/3,2/3]. With artificial boundary values 0 and 1, there is consequently a unique gap g_x with left and right tail probabilities both strictly less than 1/3. Its atom is strictly greater than 1/3, and every other atom is strictly less than 1/3. This is the unique mode; by (1), g_x=0 for every outsider. If there were a second common gap g, r(g)=0 would imply p_x(g)=p_x(0), a contradiction. Thus the common intersection is exactly {0}.

Suppose I_x is contained in I_y, including equality. Whenever y is placed in I_x, interchange the labels x,y at their two positions. Both placements remain eligible, so this is a bijection reversing the relative order. When y lies strictly to the left of I_x it must precede x; when strictly to the right it must follow x. Therefore

    Pr(y before x) - Pr(x before y)
        = Pr(g_y < a_x) - Pr(g_y > b_x),              (3)

where g_y on the right denotes the random gap of y (not the deterministic modal gap). Because 0 belongs to I_x, both right-hand tail terms are strictly below 1/3. The absolute difference is strictly below 1/3, so x,y are balanced: contradiction.

A hypothetical counterexample therefore has pairwise inclusion-incomparable intervals. Relabel outsiders so that

    a_1 < a_2 < ... < a_k = 0 = b_1 < b_2 < ... < b_k.

This follows from strict nonnesting, since equal endpoints or reversed endpoint order would imply containment. From (2) and p_x(0)>1/3 every outsider must satisfy

    sum_{g in I_x, g != 0} 1/(r(g)+1) < 2.          (4)

Since r(g)<=k-1 for g in I_x, the interval length is at most 2k. This recovers the previous fixed-k gap cutoff, now with a stronger occupancy parameter.

**4. Harmonic obstruction for every k>=7 (no enumeration).** For outsider i the gaps a_j for i<=j<k and b_j for 2<=j<=i are distinct, nonzero and allowed. At a_j<0 exactly j outsiders are eligible, hence r(a_j)=k-j. At b_j>0 exactly k-j+1 outsiders are eligible, hence r(b_j)=j-1. Keeping just these terms in (4) gives

    sum_{g in I_i, g != 0} 1/(r(g)+1)
      >= sum_{j=i}^{k-1} 1/(k-j+1) + sum_{j=2}^i 1/j
      = H_(k-i+1) + H_i - 2,

where H_n=sum_{s=1}^n 1/s. Take i=4. For k>=7, the lower bound is at least 2H_4-2=13/6>2, contradicting (4). This is a uniform structural proof for all k>=7, including arbitrarily large chains.

**5. Complete finite residual for 2<=k<=6.** By Step 3 the normalized strictly ordered endpoint lists have a_k=b_1=0 and every length <=2k. Consequently the negatives of the other k-1 left endpoints and the other k-1 right endpoints are both (k-1)-element subsets of {1,...,2k-1}. Choose each subset once, sort the negative left endpoints and positive right endpoints, and pair corresponding endpoints. Reject precisely the tuples with a length >2k or a violation of (4). This covers every possible counterexample; no assumption of a minimal total vertex count is used. Chain vertices outside the interval union are fixed prefix/suffix padding, so omitting them changes no pair probability.

The remaining cases are checked by [scripts/m079_uniform_split.py](../scripts/m079_uniform_split.py). For every case, an outsider–chain pair satisfies 3 min(N,E-N)>=E, where E is the total extension count and N counts extensions placing the outsider before the chain vertex at the corresponding threshold. The verifier uses two exact recurrences:

* Sequential count: state (g,S) stores the current gap and the subset already placed; insert one eligible unplaced outsider, or advance a chain step only if no unplaced outsider has its last gap at or before g. Forward/backward path products give every gap marginal and hence every chain threshold.
* Factorial-block count: choose a subset of the eligible remaining labels to occupy the current gap, including every remaining label whose last gap is current; multiply by the factorial of its size. Count E and independently recount N by truncating the selected outsider's upper endpoint to the chosen threshold. No floating point or randomized search.

| k | Residual cases | Minimum best outsider–chain balance over residuals |
|---:|---:|---:|
| 2 | 9 | 2/5 |
| 3 | 32 | 28/69 |
| 4 | 65 | 671/1537 |
| 5 | 49 | 6529/15414 |
| 6 | 49 | 40423/88060 |
| Total | 204 | All strictly greater than 1/3 |

These minima apply only to the residual sets, not to the entire class. Together with Steps 1–4, they exclude every counterexample in the stated infinite class. QED (candidate, pending independent review).

## Reproduction, counterexample to an overstrong route, and review

Run from the repository root:

    python3 scripts/m079_uniform_split.py

Author-side run (Python standard library, exact integer/Fraction arithmetic): all 204 residuals passed; both recurrence counts agreed on every total and selected witness; every two-gap occupancy inequality passed; a deliberately altered witness count was rejected. Wall time 3.70 s, maximum RSS 96,776 KiB in the execution container (not a benchmark guarantee). Local script SHA-256: `f12079a1a5051acc39a02a39416b67c167f2ece6561961fcce3a44ace0f1b72f`.

A tempting stronger inference fails: two outsiders with the same unique modal gap need not themselves be balanced. Intervals [-1,0], [0,1] yield E=5; each has probability 3/5 of the central gap, yet the first outsider precedes the second in 4/5 of extensions. The chain comparisons are balanced (2/5, 3/5), and the verifier checks the gap marginals. This is why the nesting hypothesis and the absence of a balanced chain pair are essential in Step 3. Do not extend the argument to general posets: even two disjoint two-element chains (2+2) cannot be partitioned into a chain and an antichain. For general outsiders with comparabilities, the two-word permutation count in Step 2 no longer applies.

## Sources and novelty boundary

* [Olson–Sagan, On the 1/3–2/3 Conjecture (2018)](https://arxiv.org/abs/1706.04985): known restricted classes and the open general problem.
* [Aires–Chan–Pak–Panova, Breaking the Infinite Barrier (2026)](https://arxiv.org/abs/2609.30888): general bound improvement and large-width results, not used in this argument.
* [Gupta, balance constants through fourteen elements (2026)](https://arxiv.org/abs/2607.23926): finite verification; not used as a proof input.
* [M079_CHAIN_PLUS_FIVE.md](M079_CHAIN_PLUS_FIVE.md): previous project gap-atom and Helly reductions, fixed-k exact computations. This candidate replaces the need to increase k one at a time for the 1/3 conclusion by a two-gap comparison, nesting obstruction and harmonic sum. It does not establish the sharper constants claimed in the earlier restricted classes.

Targeted literature search on chain-plus-antichain/split posets and balance constants did not establish whether the full stated class is already covered by a published theorem. Do not label it historically novel without a specialist audit; in particular compare generalized semiorders and dimension-two/interval-order literature.

**Next falsifier / independent acceptance:** reproduce the 204-case enumerator with an independent endpoint generator and a relation-matrix linear-extension counter, verify the two-gap fiber ratio and nesting-swap argument for all boundary cases, and search prior art for the exact chain–antichain class. A missed normalized tuple, a wrong count, or a counterexample to the occupancy lemma would invalidate the candidate proof. Scope and proof review must be by someone other than the author; the two same-author algorithms are not independent mathematical review. No full conjecture or Solved-archive update, no commercial advantage claim.
