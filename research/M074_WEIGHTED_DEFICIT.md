# M074 — an enumeration-free finite (24,8) exclusion

**Research note, 2026-10-31.** This gives a second, shorter proof route for the *finite* Caccetta–Häggkvist directed-triangle case at (n,r)=(24,8). Unlike [the first repository proof](../proofs/M074_IRREGULAR_24.md), the mathematical argument below does **not** use its 19 × 5005 profile classification, its 83 surviving profiles, or its special six-outdegree local-triangle elimination. A separate histogram audit checks the new inequalities and includes a deliberately weakened-cut negative control. **Independent specialist review remains pending.** This is not a proof of the unrestricted conjecture, and no novelty is claimed: [wustep/maths](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md) previously reported computational exclusion of the same finite case.

## Exact statement and two established prerequisites

**Finite theorem.** Every loopless digraph on 24 vertices with minimum outdegree at least eight contains a directed cycle of length at most three.

Assume the contrary. The digraph has no directed two-cycle or triangle, so it is oriented. Delete excess outgoing arcs until all outdegrees are **exactly eight**; this cannot create a directed cycle.

We use two explicitly proved results in [the eight-vertex/regular-case dossier](M074_ELEMENTARY_24_REGULAR.md):

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

## Exhaustive hand case split: 16 <= m <= 21

Since each k(b)<=6, (1) implies 6(9-z)>=74-2m.

**Case m<=18.** We have z<=2 and t>=24-m>=6. By (3), at least six outneighbors have deficit at least two. Therefore W(v)>=12>7.

**Case m=19.** Here z<=3, t>=5. If z<=2, (3) gives W(v)>=10>7. If z=3, exactly six B vertices have positive k; (1) requires their k-sum at least 36, so **all six have k=6**. The A-surplus is only three, so every alpha<=5 and q(b)=0 for those six. By (4) they each have at least seven outgoing arcs inside B, totaling at least 42. Formula (5) for s=6 permits only 33. Contradiction.

**Case m=20.** Here z<=3, t>=4. If z<=2, (3) gives W(v)>=8. If z=3, the six positive k values sum to at least 34, so **each is at least four** and the sum of their deficits from six is at most two. The A-surplus is four: for k>=4, q(b) can be positive only at k=4, and then q(b)<=1 (only one A vertex can have alpha=6). There can be at most one k=4, so the six q values sum to at most one. By (4) their B-outdegrees sum to at least 6+34-1=39, again exceeding the s=6 capacity 33.

**Case m=21.** Here z<=3, t>=3.

- If z<=1, (3) gives W(v)>=3*3=9.
- If z=2 and t>=4, (3) gives W(v)>=4*2=8.
- If z=2 and t=3, the five non-two A degrees must each use one of the five surplus units: the A profile is necessarily (2^3,3^5). There are seven positive k values with sum at least 32. Let u be the number equal to one. Since the others are at most six, u<=2. For k=1, q=5, giving no positive lower bound in (4); for k>=2, q=0, so d_B^+>=1+k. If u<=1, the seven positive-k vertices together have at least 7+32-2u>=37 B-outgoing arcs, exceeding the s=7 capacity 35. If u=2, the five remaining k values must all equal six; those five vertices each have at least seven B-outgoing arcs, totaling 35, exceeding the s=5 capacity 30.
- If z=3, the six positive k values sum to at least 32, so each k>=2. Write x(a)=alpha(a)-2, with sum_A x=5. Each of the six positive-k B vertices satisfies

      q(b) <= floor(5/k(b)) <= 6-k(b),   k=2,...,6.

  The last inequality is checked directly for the five integers 2,3,4,5,6. Therefore their q-sum is at most 36-sum k<=4. By (4), their B-outdegrees total at least 6+32-4=34, exceeding the s=6 capacity 33.

Every high vertex is thus either locally impossible or has W(v)>=8. Since H is nonempty, this contradicts the global average bound (W). The finite theorem follows. **No integer-profile enumeration is part of this proof.**

## Independent arithmetic audit and adversarial control

The [histogram checker](../scripts/ch24_weighted_deficit.py) enumerates **relaxed** integer histograms rather than 24-vertex graphs. It independently tests the *new* disjunction W>=8 OR B-subset-capacity violation against all integer profiles meeting (1), without using the old e(B,A) bound or its 83 survivors. It uses compositions of degree-count histograms rather than the original sorted-tuple implementation. Its unit tests include a deliberately weakened cut, replacing 74-2m by 73-2m.

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

    python3 scripts/ch24_weighted_deficit.py
    python3 -m unittest discover -s tests -p 'test_ch24_weighted_deficit.py' -v

**Evidence boundary.** This is a second author-derived finite proof with a separate arithmetic sanity check, not an independent external mathematical review, a formal Lean proof, or an exhaustive graph census. The global Caccetta–Häggkvist conjecture remains open. Do not promote M074 or alter data/solved.json. The next high-value gate is an independent specialist's line-by-line review of the local eight-vertex lemma, the regular-case prerequisite, the weighted double count, and the four B-capacity cases; a future Lean or proof-assistant encoding should check the *quantified graph theorem*, not just these integer profiles.

**Primary context, checked 2026-10-31:** [EGRES open problem statement](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture); [Hladký–Král'–Norin, published 0.3465 threshold](https://doi.org/10.1007/s00493-015-2662-5); [earlier computational finite exclusions](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md).
