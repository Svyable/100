# M075 — a proof strategy with a sharp failure boundary

**2026-10-31: KNOWN mathematics, independently executable verification.**
No new general Frankl theorem is claimed, and this record does not alter
\`data/solved.json\` or the portfolio evidence status.

## Fully general known theorem for a two-element member

**Theorem (folklore).** Let \(\mathcal F\) be any finite, nonempty,
union-closed family of distinct sets. If \(\{a,b\}\in\mathcal F\) with
\(a\ne b\), then at least one of \(a,b\) belongs to at least half of
\(\mathcal F\). There is no bound on the size of the ground set or family.

**Proof.** Partition \(\mathcal F\) into four classes by its intersection
with \(\{a,b\}\): \(F_{00},F_{10},F_{01},F_{11}\).
For each \(X\in F_{00}\), union closure gives
\(X\cup\{a,b\}\in F_{11}\). This map is **injective**, because removing
\(\{a,b\}\) from its image recovers \(X\). Hence
\(|F_{11}|\ge|F_{00}|\). Writing \(d(a),d(b)\) for element frequencies,

\[
d(a)+d(b)=|F_{10}|+|F_{01}|+2|F_{11}|
=|\mathcal F|+(|F_{11}|-|F_{00}|)\ge|\mathcal F|.
\]

Consequently \(\max\{d(a),d(b)\}\ge|\mathcal F|/2\). QED.

The inequality can be **sharp**: \(\mathcal F=\{\varnothing,\{a,b\}\}\)
has \(d(a)=d(b)=1=|\mathcal F|/2\).
This is an unrestricted theorem *within its doubleton hypothesis*.
It is not the unrestricted union-closed sets conjecture.

Prior art: the [MathWorld discussion](https://mathworld.wolfram.com/Union-ClosedSetsConjecture.html)
presents the four-class argument; this is also identified as folklore in
[the literature overview (Remark 3.4)](https://www-user.tu-chemnitz.de/~ninag/Masterarbeit_Nicolas_Nagel.pdf).

## An exact, published three-element obstruction

The tempting extension

> Whenever \(\{a,b,c\}\in\mathcal F\), one of \(a,b,c\) occurs in
> at least half of \(\mathcal F\)

is **false**, even when the triple is a smallest member.

The [Sarvate–Renaud example](https://mathoverflow.net/questions/138567/renaud-sarvate-limitation-on-frankls-conjecture),
published in *Ars Combinatoria* 29 (1990), pp. 181–185, is transcribed
as an explicit **27-set family on nine elements**. Our fixture uses
zero-based indices corresponding to the source's elements 1–9.
The exact set \(\{0,1,2\}\) belongs to the family and has minimum
cardinality three. Each of its three elements belongs to exactly
**13 of the 27** family members, strictly below half. Other elements
are abundant. Thus the example is **not** a counterexample to Frankl.

The repository checks union closure independently in two representations:
integer-bitmask unions and Python \`frozenset\` unions. It also recomputes
all element frequencies and rejects corrupted or non-closed examples.

## Reproduce both sides

\`\`\`sh
python3 scripts/frankl_pair_boundary.py --certificate examples/FRANKL_DOUBLETON.json --doubleton 0 1
python3 scripts/frankl_pair_boundary.py --certificate examples/FRANKL_SARVATE_RENAUD.json
python3 -m unittest discover -s tests -p 'test_frankl_pair_boundary.py' -v
\`\`\`

The tests separately scan **all 256 possible set families on a three-element
universe**, filter those that are union-closed and have a doubleton, and
check the exact injective partition identity. This finite testing is only
a consistency check of the *general mathematical proof* given above.

## Consequence for proof search and rankings

An AI proof engine must not extrapolate a successful local injection from
sets of size two to sets of size three. The 27-set witness is a permanent
**negative-control certificate** for any proposed "small member is abundant"
strategy. Future arguments must either select an element outside the
three-element member, or introduce additional hypotheses that the
Sarvate–Renaud family does not satisfy.

A properly recorded falsification of an **auxiliary hypothesis** is useful
mathematics, but it cannot be credited as a counterexample to M075 itself.
Do not increase solution-readiness scores just because a known theorem
or published negative control is reproduced.
