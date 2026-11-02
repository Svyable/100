# M079 — seven-gap eight-outsider sharp balance boundary (candidate)

**Date:** 2026-11-02. **Work ID:** `X-M079-CHAIN8-SEVENGAP`; [claim #269](https://github.com/Svyable/100/issues/269). **Scope SHA-256:** `25964eaa7731a1810499577dcc89eb37b7586c5b6c3c9eb68cbdf579ed2b5703`.

**Status:** original bounded computational proof candidate, not independently accepted; historical novelty not established. No claim is made about all width-eight posets or the unrestricted one-third–two-thirds conjecture.

## Exact mathematical target

Let `P` consist of an arbitrarily long chain and eight mutually incomparable outsiders. Assume `width(P)=8` and each outsider is incomparable with between one and six chain vertices (equivalently, has between two and seven allowed insertion gaps). For uniformly random linear extension `L`, set

`delta(P) = max_{u != v} min(Pr_L(u precedes v), Pr_L(v precedes u))`.

**Sharp restricted theorem candidate:** `delta(P) >= 418779/939501 = 46531/104389 ≈ 0.445746199312188`. The bound is attained by the explicit self-dual 20-vertex poset with twelve chain vertices and eight outsider insertion intervals

`[-6,0], [-3,0], [-2,0], [-1,0], [0,1], [0,2], [0,3], [0,6]`.

The exact extension count is `E=939501`, and the maximum smaller-side pair numerator is `B=418779`; the two maximizing pairs in the literal 20-vertex representation (chain vertices 0..11, outsiders 12..19) are `(5,13)` and `(6,18)`. The minimum is attained by **one** normalized distinct interval set; it is its own order dual. This uniqueness assertion is only about normalized interval sets, not an independently certified classification of all poset isomorphisms.

## All-orders reduction, including the repeated-interval shortcut

An outsider's chain predecessors are a prefix and successors a suffix; its possible insertion gaps form a nonempty integer interval `[a_i,b_i]`. Two disjoint outsider intervals would force the outsiders comparable via a chain vertex, so all eight intervals pairwise intersect. The interval Helly property gives a common gap. If two adjacent gaps were common, the intervening chain vertex would be incomparable with all eight outsiders and create width nine. Conversely, a nine-element antichain must consist of the eight outsiders and one chain vertex, so a **single** common gap is equivalent to width exactly eight. Translate that unique gap to zero:

`a_i <= 0 <= b_i`, `max a_i=0`, `min b_i=0`, `2 <= b_i-a_i+1 <= 7`.

Any chain vertices before the smallest allowed gap or after the largest are fixed outside all outsiders in every extension. Removing them leaves every incomparable pair probability unchanged. There are at most twelve chain vertices in the reduced poset (`-6,...,6` gaps), and at most twenty total vertices. Thus this reduction covers **arbitrary original chain lengths**.

**New finite-core simplification:** If two outsiders have the same interval, transposing those two outsiders is a poset automorphism and pairs every extension with one having their relative order reversed. Therefore `delta(P)=1/2`. Since our target bound is strictly less than `1/2`, repeated intervals require no enumeration. Among the `2+3+...+7=27` interval types containing zero, six start at zero and six end at zero; the two groups are disjoint. The exact number of valid **distinct** eight-interval sets is

`C(27,8) - 2*C(21,8) + C(15,8) = 1,819,530`.

The corresponding count **with repetition** is `C(34,8)-2*C(28,8)+C(22,8)=12,259,764`, of which `10,440,234` are discharged by the automorphism argument. An independent Python combinations enumeration checked the distinct count exactly. Sorting removes only permutations of outsider labels. This is a proof reduction, not coverage-slot inflation.

## Exact algorithms and integer safety

The standalone C++17 checker `scripts/m079_chain8_sevengap.cpp` visits each of the 1,819,530 valid distinct normalized sets and compares two separate exact methods on the entire finite core:

1. A sequential forward/backward order-ideal recurrence on `(chain-prefix length, placed-outsider mask)` counts each legal next element and every pair event.
2. A factorial gap-block recurrence chooses subsets placed at each gap, weights each by the factorial of its size, and splits same-gap outsider pairs equally. The two paths must agree on the total extension count, all 28 outsider-pair numerators, and all eight insertion-gap marginals.

For every instance, `B` is the maximum of the smaller before/after counts over all incomparable outsider pairs and outsider–chain pairs. The balance constant is exactly `B/E`, compared by integer cross multiplication, not floating point. With at most twelve chain vertices and eight outsiders, `E <= 20!/12! = 5,079,110,400`. Even the largest cross product `(E/2)*E` is below `2^64`, and each transition contribution counts a subset of extensions, so unsigned 64-bit arithmetic suffices for the stated scope.

The separate Python checker constructs the **literal full-poset predecessor relation**, counts topological orders by subsets of all vertices, and computes every pair numerator without either C++ interval-state recurrence. Independent-representation seeded checks and negative controls are described below. These are independent **algorithms run by the same author**, not an independent mathematical review.

**Full exact transcript** (`clang++ -std=c++17 -O3`, connected macOS host, 214.70 seconds including shell/process):

```
cases=1819530 dual=1819530 negative=0 minimum=418779/939501 multiplicity=1 max_length=7 intervals=27 distinct=1 fnv64=df3b1c32cf646fb7 witness=[-6,0][-3,0][-2,0][-1,0][0,1][0,2][0,3][0,6]
```

Every distinct case was compared across both C++ recurrences; zero mismatches and zero instances below one third. The FNV64 digest is a deterministic drift check, **not** a cryptographic proof or specialist review. An additional **113,145-case dual census** for the six-gap distinct core independently confirms the earlier observed six-gap minimum `1425408/3193368` with multiplicity two (digest `bf95440f185d886c`). A separate Python `itertools.combinations` enumeration confirms the 1,819,530 valid distinct interval sets. The Python literal full-poset DP reproduces the 20-vertex witness and 25 seeded controls (24 involving a seven-gap interval), all agreeing with C++ pair counts. A fourth method recounts topological orders after forcing each of four specified ordered pairs, including both critical pairs. A same-gap order mutation is rejected. Thirteen dedicated tests cover these controls, width-nine and eight-gap exclusions, repeated intervals, self-duality, outsider permutations and literal enumeration of a small example. These are all **author-controlled** checks.

**Code provenance:** The C++ two-recurrence and Python literal-poset scaffolds were adapted from the still-open five-gap [PR #265](https://github.com/Svyable/100/pull/265); this PR adds the seven-gap scope, new distinctness reduction, exact exhaustive transcript, new extremizer and boundary falsifier. They are different counting algorithms but not independent software authorship or external review.

## Assumptions, adverse searches and falsifiers

The uniform linear-extension distribution, outsider antichain, exact width eight, unique common insertion gap, length limit seven, distinctness reduction and exact integer transitions are essential. The previously reported five-gap constant `22648/50201` does **not** extend to six gaps: [PR #265](https://github.com/Svyable/100/pull/265) supplies the explicit six-gap witness with `E=3,193,368`, `B=1,425,408`, hence `delta=59392/133057`. That PR reports a single-recurrence six-gap minimum observation, not a dual-checked sharp seven-gap theorem. **The six-gap constant is false at seven gaps:** our witness gives `418779/939501 < 1425408/3193368`, with exact positive cross-product gap `1425408*939501 - 418779*3193368 = 1,856,783,736`. This is an explicit new negative boundary to extrapolation, not a counterexample to the 1/3–2/3 conjecture. Our claim #269 has a separate scope and does not change or land #265.

**Failed or abandoned avenues:** An initial unpruned all-multiset seven-gap sequential census was terminated after approximately 103 seconds without a complete transcript; it is **not** counted as evidence. The duplicate-interval automorphism then removed 10,440,234 unnecessary cases exactly. The five-gap sharp constant already fails at six gaps, and the six-gap constant fails at seven, so neither extrapolation is a proof strategy. The current result still depends on a finite core; no all-width or unbounded-gap inequality was obtained. The checker does not contain a Lean proof or an independently authored mathematical review.

A candidate falsifier is any valid seven-gap interval set with a smaller exact `B/E` than the reported minimum, or any mismatch between the two recurrences or a literal-poset witness. The next boundary is eight allowed gaps, where the distinct-interval core has `17,523,100` cases; a stronger symbolic reduction is preferable to blindly increasing the census. A primary source establishing the same exact restricted constant would falsify a historical-novelty claim (which is not made here). Obtain specialist review of the Helly/width reduction, event counting, finite completeness and historical priority before any independent acceptance.

## Reproduction

```sh
python3 scripts/m079_chain8_sevengap.py --check
python3 scripts/m079_chain8_sevengap.py --full
python3 -m unittest discover -s tests -p 'test_m079_chain8_sevengap.py' -v
python3 scripts/regen.py --check --fast
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

No solved state, evidence state, coverage allocation, benchmark result or separate Project 100 PR Landing task/cadence is modified.

## Primary literature and priority boundary (checked 2026-11-02)

- Brightwell–Wright, *The 1/3–2/3 Conjecture for 5-Thin Posets*, SIAM J. Discrete Math. 5 (1992), 467–474, https://doi.org/10.1137/0405037. Their five-incomparables theorem does not imply this exact width-eight quantitative bound; each outsider here has seven other incomparable outsiders.
- Olson–Sagan, *On the 1/3–2/3 Conjecture*, Order 35 (2018), 581–596, https://arxiv.org/abs/1706.04985. Special classes and symmetry-induced half-balanced pairs, but no identified exact seven-gap eight-outsider sharp value.
- Chen, *A Family of Partially Ordered Sets with Small Balance Constant*, Electron. J. Combin. 25 (2018), https://doi.org/10.37236/7337. Examples with smaller constants in a different family.
- Aires–Chan–Pak–Panova, *Breaking the Infinite Barrier in the 1/3–2/3 Conjecture*, https://arxiv.org/abs/2609.30888 (posted 2026-09-25, revised 2026-10-28). Universal epsilon improvement, not a sharp finite width-eight local constant.
- Prior repository [five-gap theorem candidate](https://github.com/Svyable/100/pull/265) and [seven-outsider eight-gap candidate](https://github.com/Svyable/100/pull/260) have different hypotheses. No historical novelty or independent specialist acceptance is inferred from a targeted search or author-controlled computation.
