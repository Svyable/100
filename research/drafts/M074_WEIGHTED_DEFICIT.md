# M074 — an enumeration-free finite (24,8) exclusion

**Research note, 2026-10-31.** This gives a second, shorter proof route for the *finite* Caccetta–Häggkvist directed-triangle case at (n,r)=(24,8). Unlike [the first repository proof](../../proofs/M074_IRREGULAR_24.md), the mathematical argument below does **not** use its 19 × 5005 profile classification, its 83 surviving profiles, or its special six-outdegree local-triangle elimination. A separate histogram audit checks the new inequalities and includes a deliberately weakened-cut negative control. **Independent specialist review remains pending.** This is not a proof of the unrestricted conjecture, and no novelty is claimed: [wustep/maths](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md) previously reported computational exclusion of the same finite case.

## Exact statement and two established prerequisites

**Finite theorem.** Every loopless digraph on 24 vertices with minimum outdegree at least eight contains a directed cycle of length at most three.

Assume the contrary. The digraph has no directed two-cycle or triangle, so it is oriented. Delete excess outgoing arcs until all outdegrees are **exactly eight**; this cannot create a directed cycle.

We use two explicitly proved results in [the eight-vertex/regular-case dossier](../M074_ELEMENTARY_24_REGULAR.md):

1. Every directed-triangle-free oriented graph on eight vertices with minimum outdegree at least two has at most **21** arcs and maximum indegree **three**. No such graph has minimum outdegree three.
2. There is no directed-triangle-free oriented graph on 24 vertices with **both** indegree and outdegree eight everywhere. That proof is a hand 22-versus-15 cross-cut contradiction, not a solver verdict.

These are prerequisites, not conclusions imported from the present irregular argument. For any vertex v with indegree b, its eight outneighbors have internal outdegree at least b-7: they cannot point to v or to its b inneighbors. If b>=10, their internal minimum outdegree would be at least three, contradicting prerequisite 1. Hence **all indegrees are at most nine**. Their average is eight. If no indegree-nine vertex existed, all indegrees would equal eight, contradicting prerequisite 2. Let H be the nonempty set of indegree-nine vertices.

## A global weighted-deficit budget

Let L be the vertices with indegree at most seven. For a in L, write delta(a)=8-d^-(a)>=1; the remaining vertices outside H union L have indegree eight. Since every outdegree equals eight, the total indegree deficit balances the unit excess at each vertex of H:

    sum_{a in L} delta(a) = h,   h=|H|>0.

For each high vertex v, define the deficit weight of its outneighborhood

    W(v) = sum_{a in N^+(v) intersect L} delta(a).

Double-counting the weighted arcs from H to L gives

    sum_{v in H} W(v)
       = sum_{a in L} delta(a) * e(H,{a})
      <= sum_{a in L} delta(a) * d^-(a)
      <= 7 * sum_{a in L} delta(a) = 7h.                  (W)

Thus **not every high vertex can have W(v)>=8**. We will show that, for every hypothetical high vertex, either its local degree constraints are already contradictory or its outneighborhood has weight at least eight.

## Root cuts, without profile enumeration

Fix v in H. Partition the other vertices into A=N^+(v) (8 vertices), B=N^-(v) (9 vertices), and C (6 vertices). Put

    alpha(a) = d_A^+(a) >= 2,    m = e(A,A) <= 21,
    k(b) = d_C^-(b) in {0,...,6},   z = |{b in B : k(b)=0}|,
    t = |{a in A : alpha(a)=2}|.

Every a in A sends eight arcs to A union C, so e(A,C)=64-m. Since there are only 48 possible unoriented A/C pairs, e(C,A)<=m-16. The six C vertices each have indegree at most nine, and receive 64-m arcs from A, so e(B,C)+e(C,C)<=m-10. All six C vertices have outdegree eight. Subtracting the two preceding upper bounds gives

    sum_{b in B} k(b) = e(C,B) >= 74-2m.                (1)

The eight internal A outdegrees have baseline two, with total surplus m-16<=5. Each vertex whose internal outdegree exceeds two consumes at least one surplus unit, hence

    t >= 8-(m-16) = 24-m.                               (2)

For any a in A with alpha(a)=2, the vertex points to **all six** C vertices and therefore receives no arc from C. It can receive at most one from v, three from A (prerequisite 1), and z from B: if k(b)>0, an arc b->a would close a triangle a->c->b->a. Consequently

    d^-(a) <= 4+z,   so delta(a) >= 4-z,               (3)

whenever z<=3. In particular, W(v)>=t(4-z).

We also need a simple bound on outgoing arcs within B. If b->a for b in B, a in A, the sets N_C^+(a) and N_C^-(b) are disjoint (else a directed triangle). They have sizes 8-alpha(a) and k(b), respectively, and C has six vertices. Therefore alpha(a)>=k(b)+2. Define

    q(b) = |{a in A : alpha(a)>=k(b)+2}|.

At most q(b) of b's arcs enter A, at most 6-k(b) enter C, and one enters v. Hence

    d_B^+(b) >= 1+k(b)-q(b).                            (4)

For **any** subset S of s B vertices, there are at most s(s-1)/2 arcs within S and at most s(9-s) arcs from S to the rest of B. Thus

    sum_{b in S} d_B^+(b) <= s(17-s)/2.                 (5)

The cases below use only (1)–(5) and (W); **the earlier proof's lower bound on e(B,A) and its 83-profile certificate are not used**.

## Short capacity proof: four cases in z, no histogram enumeration

The bound \(16\le m\le21\) follows from the eight internal A outdegrees
being at least two, together with the established 21-arc ceiling.
Equation (1) gives \(\sum_B k(b)\ge74-2m\ge32\).
In particular, **z cannot exceed three**: four zero k values would leave
at most five positive values, with sum at most \(5\cdot6=30\).

**Case z=3 (all six values m=16,...,21 at once).**
Exactly six k values are positive, with total at least 32. Each must be
at least two: if one equalled one, their sum would be at most
\(1+5\cdot6=31\). For any one of these k values,
an eligible a counted by q(b) has \(\alpha(a)-2\ge k\).
Since \(\sum_{a\in A}(\alpha(a)-2)=m-16\le5\),

    q(b) <= floor(5/k(b)) <= 6-k(b),   2 <= k(b) <= 6.     (6)

The last inequality is the five elementary integer checks
\(2\le4, 1\le3, 1\le2, 1\le1, 0\le0\).
Using (4), the **six** positive-k vertices of B therefore send
at least

    sum (1 + k(b) - q(b))
      >= sum (2*k(b) - 5)
       = 2*sum k(b) - 30
      >= 2*32 - 30 = 34

arcs **inside B**. But (5), applied to this six-vertex subset,
allows at most \(6(17-6)/2=33\). Contradiction. This eliminates all
previously separate \(m=19,20,21;z=3\) subcases with one strict
inequality. It also exposes the exact one-unit sensitivity: replacing
\(\sum k\ge32\) by 31 would only imply 32, not 34.

**Case z<=1.** By (2), \(t\ge24-m\ge3\). Equation (3) gives
\(W(v)\ge t(4-z)\ge3\cdot3=9\).

**Case z=2 and (m<=20 or t>=4).** Here (2) guarantees
\(t\ge4\) when \(m\le20\). In either event,
\(W(v)\ge2t\ge8\).

**Only exceptional case: z=2, m=21, t=3.**
Exactly five A vertices have \(\alpha=3\), the other three
have \(\alpha=2\), because the available surplus is five.
Of the seven B vertices with positive k, write \(u\) for those
with \(k=1\). Equation (1) gives \(\sum k\ge32\),
so \(u\le2\) (three ones and four sixes sum only 27).

For k=1, q=5; for k>=2, q=0. If u<=1, the seven
positive-k vertices send at least

    (7-u) + (sum k - u) >= 7 + 32 - 2u >=37

arcs inside B, violating the s=7 bound \(7(17-7)/2=35\).
If u=2, the remaining five k values must all equal six,
so these five B vertices send at least \(5\cdot7=35\)
arcs inside B, violating the s=5 bound \(5(17-5)/2=30\).

Consequently, for every high vertex either its local cut is
impossible or its outneighborhood has weight at least eight.
The global average bound (W) says \(\sum_{v\in H}W(v)\le7h\)
with \(h>0\), contradiction. **This completes the finite
(24,8) proof given its two explicitly stated local prerequisites.**

This rearrangement simplifies an existing author-derived restricted
finite proof; it is **not** an independently reviewed theorem or a
new advance beyond the finite case previously certified externally.

## Independent arithmetic audit and adversarial control

The [compact z=3 boundary checker](../../scripts/ch24_z3_capacity.py) independently
replays the 34-versus-33 inequality, its sharp relaxed profile, the
exceptional z=2 subset contradiction, and the one-unit weakened-cut
negative control. It checks necessary integer constraints, not graphs.

The [histogram checker](../../scripts/ch24_weighted_deficit.py) enumerates **relaxed** integer histograms rather than 24-vertex graphs. It independently tests the *new* disjunction W>=8 OR B-subset-capacity violation against all integer profiles meeting (1), without using the old e(B,A) bound or its 83 survivors. It uses compositions of degree-count histograms rather than the original sorted-tuple implementation. Its unit tests include a deliberately weakened cut, replacing 74-2m by 73-2m.

| Relaxed integer audit | Exact result |
|---|---:|
| A histograms | 19 |
| C-to-B histograms | 5,005 |
| Pairs meeting the correct cut (1) | 20,500 |
| Excluded by weighted deficit alone | 20,287 |
| Remaining pairs excluded by B-subset capacity | 213 |
| Unresolved under correct inequalities | **0** |
| Unresolved if cut (1) is weakened by one | **2** |

The two one-unit-weakened survivors have A profile (2^7,7) and k multisets (0,0,0,4,5,5,5,6,6) and (0,0,0,5,5,5,5,5,6). These are **not** actual digraphs. They show that the arithmetic test would fail if a critical cut constant were silently relaxed.

Run from the repository root:

    python3 scripts/ch24_z3_capacity.py
    python3 -m unittest discover -s tests -p 'test_ch24_z3_capacity.py' -v
    python3 scripts/ch24_weighted_deficit.py
    python3 -m unittest discover -s tests -p 'test_ch24_weighted_deficit.py' -v

**Evidence boundary.** This is a second author-derived finite proof with a separate arithmetic sanity check, not an independent external mathematical review, a formal Lean proof, or an exhaustive graph census. The global Caccetta–Häggkvist conjecture remains open. Do not promote M074 or alter data/solved.json. The next high-value gate is an independent specialist's line-by-line review of the local eight-vertex lemma, the regular-case prerequisite, the weighted double count, and the four B-capacity cases; a future Lean or proof-assistant encoding should check the *quantified graph theorem*, not just these integer profiles.

**Primary context, checked 2026-10-31:** [EGRES open problem statement](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture); [Hladký–Král'–Norin, published 0.3465 threshold](https://doi.org/10.1007/s00493-015-2662-5); [earlier computational finite exclusions](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md).
