# M075 — six-point support boundary for a triple-local falsifier

**2026-11-01 — author-checked working note, not externally reviewed.**
Associated claim [#138](https://github.com/Svyable/100/issues/138); related global
19-member optimization claim [#133](https://github.com/Svyable/100/issues/133)
is separate. No unrestricted Frankl theorem or novelty assertion.

## The precise finite statement

Let F be a finite family of distinct subsets of a ground set U, closed under
pairwise union, with ∅ and the **exact set** T={a,b,c} present.
Say T is *locally rare* if each of a,b,c occurs in strictly fewer than
|F|/2 members of F.

**Finite support result (computer-enumerated lower half, explicit upper half).**
There exists such a family whose support has **six** points and |F|=19.
There is no such family with support on **at most five** points, as verified
by an exhaustive closure-pruned enumeration with a written completeness
argument and independently counted small negative controls.

This is about the smallest *ground-set size*, **not** the global minimum
number of family members, which needs an independent proof for every
cardinality below 19. The published seven-point 19-member witness is an
antecedent of the construction, so originality of the support observation
is **not established**.

## Explicit 19-member construction on six points

Write T={0,1,2}, B={3,4,5}, and let

    P0={3,4}, P1={3,5}, P2={4,5}.

Define F as the disjoint union of

    {∅, T}
    {P_i, P_i ∪ {i}, P_i ∪ T : i=0,1,2}
    {B ∪ S : S ⊆ T}.

The three blocks contribute 2, 9 and 8 distinct sets: |F|=19.
Every pair of sets in one P_i fiber is nested; union with T is in that
fiber's top member. Two different P_i fibers have outside union B, hence
their union belongs to the final block; the final block itself is
union-closed and absorbs every other block. The empty set is neutral.
This checks union-closure **without** relying on a SAT solver.

Each i in T occurs once in T, in the three P_j ∪ T sets, once in its
own P_i ∪ {i} set, and in four of the eight B ∪ S sets:

    f(0)=f(1)=f(2)=1+3+1+4=9 < 19/2.

Each b in B occurs in two P_i fibers (three sets each), and in all
eight members of the final block, so f(b)=6+8=14.
T is inclusion-minimal among nonempty members, **but not smallest by
cardinality**: each P_i is a 2-set. Some elements outside T are abundant,
so this does not refute Frankl's existential conjecture.

The 2026 published
[van der Hout–Roos example](https://doi.org/10.23952/jano.8.2026.1.02),
transcribed in
[FRANKL_VAN_DER_HOUT_ROOS_19.json](../../examples/FRANKL_VAN_DER_HOUT_ROOS_19.json),
has one extra point 6 present in all its members except ∅ and T.
Erasing 6 from every member **maps exactly onto the 19 sets above**;
the map is injective on the published family. Since projection commutes
with union, it preserves union-closure. The smaller example is therefore
a **compression of published mathematics**, not a new unrelated 19-set
construction. Verified by full member-set comparison, not a frequency-only
test.

## Exhaustive five-point boundary — proof obligation and algorithm

For fixed U={0,...,n-1} and T={0,1,2}, iterate all possible subsets S
in **descending cardinality** order. At each step either exclude S, or
include it only when every union S ∪ A with an already included member
A is present among already processed members, unless that union equals
S or A. Enforce that ∅ and T are included.

**Soundness:** the currently chosen members are union-closed at every
step: the include check enforces exactly the missing closure pairs.
**Completeness:** for *any* target union-closed family, follow its
include/exclude choices. When S is included, every strictly larger
union S ∪ A belongs to the target family, was processed earlier and
was included. No valid family is pruned. The decision path is unique,
so no family is double-counted. There is no full-support assumption.

The self-contained Python implementation enumerates:

| n | Families containing ∅ and T | All three target elements rare |
|---|---:|---:|
| 3 | 45 | 0 |
| 4 | 1,575 | 0 |
| 5 | **710,830** | **0** |

At n=3,4 a **structurally different** routine examines all
2^(2^n) raw membership bitmasks and independently agrees on the
union-closed family counts and the absence of counterexamples.
At n=5 the generator traverses 3,080,453 decision nodes; its
completeness follows from the argument above. For smaller universes,
embed the family into five points by adding unused ground elements.
This establishes the finite five-point boundary conditional on the
correctness/replay of the supplied exhaustive program, not a general
or externally reviewed theorem.

The independent existing definition-level checker
`scripts/frankl_triple_sat.py:independent_check` validates the six-point
family without using this generator. Negative controls mutate the
witness and reject broken union closure, frequency and set requirements.

## General 19-member lifting lemma (k≥3)

For every integer k≥3, there is a union-closed family on k+3
active elements with 19 members, including ∅ and an
**inclusion-minimal** nonempty member T of cardinality k, such
that *each element of T occurs in exactly nine members*.

Proof: partition the new ground set into six nonempty disjoint blocks
C_0,...,C_5 where C_0={0}, C_1={1},
C_2={2,...,k-1}, and C_3,C_4,C_5 are three singletons.
Replace each original element j in every member S of the six-point
family by its entire block C_j. This substitution is injective
(because blocks are nonempty and disjoint) and commutes with union.
It preserves the 19 distinct members, closure and the empty set.
The image of {0,1,2} is T of size k, with every T-element appearing
whenever its source element appeared: exactly nine times. The image
of T remains inclusion-minimal; its external elements still occur
14 times each. QED.

This is a mathematically exact *cloning consequence* of a known
construction, not a claim that a novel general conjecture was solved.

## Reproduce

    python3 scripts/frankl_triple_support.py --check
    python3 scripts/frankl_triple_support.py --json
    python3 -m unittest discover -s tests -p 'test_frankl_triple_support.py' -v

An optional mixed-integer solver report originally suggested the
six-point support and an 18-set infeasibility verdict. Neither that
solver verdict nor a different agent's self-check is a proof of global
19-member minimality. This submitted finite result rests only on the
explicit 19-member certificate and exhaustive n≤5 closure enumeration.

**Prior-art boundary:** [Poonen, "Union-closed families" (1992)](https://doi.org/10.1016/0097-3165(92)90068-6)
proves an existential abundant element under much broader finite
conditions; it does not assert that a *designated* triple contains
one. Community 2026 claims of 19-member lower bounds for a
*smallest-cardinality* nonempty triple have different hypotheses
and have not been specialist-audited here. Independent review is
necessary before calling this finite observation mathematically novel.
