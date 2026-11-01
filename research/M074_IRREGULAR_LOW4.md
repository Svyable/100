# M074 — a four-neighbor obstruction in the irregular (24,8) branch

**Date:** 2026-10-31. **Status:** internally checked restricted structural theorem and exact eight-vertex local witness; no independent specialist review or originality determination. **Not** a proof of the unrestricted Caccetta–Häggkvist conjecture, nor an independently new finite (24,8) result. The full finite case has already been [reported computationally by another project](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md).

This strengthens the one-low-indegree-neighbor observation in [the preceding (24,8) note](M074_ELEMENTARY_24_REGULAR.md) to **four distinct neighbors** without assuming that the candidate is inregular.

## Statement and scope

Let D be a loopless oriented graph on 24 vertices, with **outdegree exactly eight at each vertex** and no directed triangle. If a vertex v has indegree nine, then **at least four distinct vertices in N⁺(v) have indegree at most seven**.

Consequently, if such a D existed, it would have at least four indegree-nine vertices and at least four vertices of indegree at most seven. If h is the number of indegree-nine vertices and l is the number with indegree at most seven, then

    4 <= l <= h <= 14,
    5h <= 8l.

These are **necessary conditions on a hypothetical counterexample**, not a construction or a proof of impossibility.

We may delete excess outgoing arcs from any candidate with minimum outdegree eight until every outdegree is exactly eight; deleting arcs cannot create directed triangles. This statement therefore constrains the original minimum-outdegree case only through that outregular reduction.

## Local lemma: at least four degree-two vertices on eight vertices

**Lemma.** If H is an oriented directed-triangle-free graph on eight vertices and every vertex has outdegree at least two, then **at least four vertices have outdegree exactly two**.

**Proof.** The previously proved [eight-vertex lemma](M074_ELEMENTARY_24_REGULAR.md) states:

1. Every vertex has indegree at most three.
2. Any vertex of indegree three has outdegree exactly two.
3. The arc count m satisfies 16 <= m <= 21, the lower bound following directly from minimum outdegree two.

Let q be the number of vertices of outdegree exactly two. Every other vertex has outdegree at least three, so

    m >= 2q + 3(8-q) = 24-q,
    hence q >= 24-m.

Let p be the number of vertices of indegree three. Since the remaining indegrees are at most two,

    m <= 3p + 2(8-p) = 16+p,
    hence p >= m-16.

All p indegree-three vertices also have outdegree two, so q >= p >= m-16. Thus

    q >= max(24-m, m-16).

For each integer m from 16 through 21, this lower bound is respectively 8, 7, 6, 5, **4**, 5. It is always at least four. QED.

### Exact sharpness example

The bound four cannot be raised **for the standalone eight-vertex lemma**. On vertices 0,...,7, take the following outgoing neighbor lists:

| Vertex | Outneighbors |
|---|---|
| 0 | 3, 6 |
| 1 | 0, 7 |
| 2 | 1, 5 |
| 3 | 2, 4 |
| 4 | 1, 2, 5 |
| 5 | 0, 1, 7 |
| 6 | 2, 3, 4 |
| 7 | 0, 3, 6 |

There are 20 arcs, outdegree vector (2,2,2,2,3,3,3,3) and indegree vector (3,3,3,3,2,2,2,2). Direct enumeration confirms **zero digons and zero directed triangles**. This does **not** establish that this local graph extends to a 24-vertex counterexample.

## Four low-indegree neighbors at an indegree-nine root

Fix v with indegree nine. Partition its other vertices as

- A = N⁺(v), with |A|=8;
- B = N⁻(v), with |B|=9;
- C = nonneighbors of v, with |C|=6.

There are no A→B arcs, because v→a→b→v would be a directed triangle, and no A→v arcs because D is oriented. Consequently, every a in A must send at least two of its eight outgoing arcs inside A (the only other possible outneighbors are the six in C). The local lemma gives **at least four distinct a in A with exactly two outgoing arcs in A**.

Each such a sends its other six outgoing arcs to **all six vertices of C**. Thus no c in C points to a (that would be a digon).

We first bound the indegree of any vertex of D by nine. If some x had indegree b >= 10, its eight outneighbors would each need at least b-7 >= 3 outgoing arcs within their own induced eight-vertex graph (the nonneighbor set has size 15-b <=5). This contradicts the eight-vertex local lemma's impossibility of minimum outdegree three.

Write m = e(A,A), so 16 <= m <=21. Since each of the eight A vertices has outdegree eight and no A→B or A→v arcs,

    e(A,C) = 64-m.

There are 8*6=48 possible unordered A–C pairs and no digons, giving

    e(C,A) <= 48-e(A,C) = m-16.

The six C vertices each have outdegree eight, none directed to v, so

    e(C,B)+e(C,C) = 48-e(C,A) >= 64-m.

Each C vertex has indegree at most nine, hence total indegree into C is at most 54. Its incoming sources are A, B and C, so

    e(B,C)+e(C,C) <= 54-e(A,C) = m-10.

Discarding the nonnegative e(B,C) term gives e(C,C) <= m-10 and therefore

    e(C,B) >= (64-m)-(m-10) = 74-2m >=32.

Each of the nine B vertices can receive arcs from at most six C vertices. Since at least 32 arcs run C→B, **at least six B vertices have a predecessor in C**; at most three do not.

For any a in A with exactly two outgoing arcs within A, we have a→c for every c in C. If c→b for some b in B, then b→a is forbidden, because it would close the directed triangle a→c→b→a. So **at most three B vertices can point to a**. The eight-vertex local lemma also gives d⁻ within A at most three. Finally a has one predecessor v and zero from C. Thus

    d⁻_D(a) <= 1 + 3 + 0 + 3 = 7.

This holds for at least four distinct a. QED.

## Global degree-count corollary (not a contradiction)

Let h be the number of vertices of indegree nine, l the number with indegree at most seven. There is at least one indegree-nine vertex: if no indegree exceeded eight, the average indegree eight would make D inregular, already excluded by the [regular-case theorem](M074_ELEMENTARY_24_REGULAR.md).

Because every outdegree is eight, total indegree is 192. With all indegrees <=9,

    h = sum_{d⁻(x)<=7} (8-d⁻(x)).

Each summand is at least one, so l <= h. The four-neighbor theorem gives l>=4 and therefore h>=4. Count arcs from indegree-nine vertices to low-indegree vertices: each high vertex sends at least four such arcs, giving at least 4h. All incoming arcs to the low vertices together number

    sum_low d⁻ = 8l-h.

Therefore 4h <= 8l-h, i.e. **5h <= 8l**. Since h+l <=24, we get 13h <=192 and hence **h<=14**.

These constraints are jointly feasible as degree counts. They have **not** been promoted into a global infeasibility or a new finite theorem beyond the stated structural restriction.

## Reproduction and adversarial controls

From repository root:

    python3 scripts/ch24_irregular.py
    python3 -m unittest discover -s tests -p 'test_ch24_irregular.py' -v

The self-contained checker records the explicit eight-vertex sharp witness and the six integer budget cases. Unit tests include independent set-based directed-triangle checking and deliberate loop, digon and directed-triangle corruptions. They do not perform a 24-vertex enumeration, verify prior literature completeness, or provide external mathematical review.

**Next falsifier:** Add the four-high/four-low and 5h<=8l degree restrictions as redundant, **proved** constraints in a separately scoped 24-vertex SAT/certificate experiment. Check whether the independence and triangle constraints actually close the irregular branch. A solver's UNSAT verdict requires a replayable proof trace checked independently; do not count an encoding or a lack of found witnesses as a proof.

**Prior art and open status:** [EGRES Caccetta–Häggkvist problem statement](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture); [Hladký–Král'–Norin directed-triangle bound](https://doi.org/10.1007/s00493-015-2662-5); [reported external finite (24,8) computations](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md). No claim of originality, peer review, full finite resolution, or unrestricted conjecture resolution is made. Leave the main registry and solved ledger unchanged.
