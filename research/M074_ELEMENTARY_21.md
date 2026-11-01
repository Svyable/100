# M074 — elementary exclusion of the (21,7) directed-triangle case

**Dated:** 2026-10-31. **Scope:** a finite theorem, **not** the Caccetta–Häggkvist conjecture at arbitrary parameters or the entire fixed-outdegree-seven case. **Novelty is not claimed**: external work earlier reported DRAT-checked (21,7) UNSAT certificates; the proof here needs independent specialist review.

## Finite theorem and reduction

**Theorem.** Every loopless simple digraph on 21 vertices with minimum outdegree at least seven contains a directed cycle of length at most three.

A counterexample has no digons or directed triangles, hence is oriented. Delete surplus outgoing arcs until every vertex has outdegree exactly seven; this cannot create a short directed cycle. It is enough to exclude such a triangle-free oriented 7-outregular digraph.

## Lemma A: seven-vertex rigidity

Every triangle-free oriented graph on seven vertices with minimum outdegree at least two has **all indegrees and outdegrees exactly two**.

**Proof.** For any vertex, write a >= 2 for its outdegree, b for its indegree, A and B for its out- and inneighbor sets, and C for the remaining 6-a-b vertices. No arc goes from A to B (directed triangle) or from A to the root (digon). Each vertex of A needs at least two outgoing arcs within A or C. Thus

    2a <= e(A,A) + e(A,C) <= a(a-1)/2 + a(6-a-b).

Hence a+2b <= 7. If b >= 3, then a+2b >= 8, impossible. Therefore every indegree is at most two; since all seven outdegrees are at least two, double-counting the arcs forces every in- and outdegree to equal two. QED.

This is sharp: the oriented circulant on Z/7 with outgoing steps 1 and 2 has semidegrees two and no triangle, since three positive steps sum to at most 6, not 7.

## Lemma B: indegree at most eight

For any vertex of indegree b >= 9, its seven outneighbors A can send arcs neither to that vertex nor to its b inneighbors. There are at most 13-b <= 4 remaining vertices. Every a in A therefore needs at least 7-4 = 3 outgoing arcs within A, contradicting Lemma A. Thus **every indegree is at most eight**. QED.

## Lemma C: indegree eight is impossible

Suppose a vertex v has indegree eight. Partition the other vertices into A=N+(v) of size 7, B=N-(v) of size 8, and C of size 5.

Each a in A sends seven outgoing arcs into A or C, so its internal outdegree is at least two. Lemma A forces the induced graph on A to be **2-in/2-out-regular**. Consequently every a in A sends arcs to *all five* vertices of C.

By Lemma B, each c in C has indegree at most eight, already receiving seven arcs from A. So there is room for at most one extra arc into each c, giving

    e(B,C) + e(C,C) <= 5.

Each c has outdegree seven, cannot point to v (nonneighbor) or A (would be a digon), and therefore sends all its arcs into B or C. Thus

    e(C,B) + e(C,C) = 35, hence e(C,B) >= 30.

There are five vertices in C, so each b in B can receive at most five arcs from C. At least six of the eight B-vertices must receive one or more arcs from C. Such a b cannot send any arc to A: for every a in A and every c in C, a→c, so b→a and c→b would form a→c→b→a.

Thus at most **two** B-vertices can point into A. Each b in B already points to v and has total outdegree seven, so each such b can point to at most six A-vertices. Therefore e(B,A) <= 12.

Count all indegrees in the digraph by destination:
- Into v: exactly 8.
- Into A: 7 from v, 14 from A (Lemma A), zero from C, at most 12 from B; total <=33.
- Into B: at most 8*8=64 (Lemma B).
- Into C: at most 5*8=40 (Lemma B).

This totals at most 8+33+64+40 = **145**, although exact outdegree seven on 21 vertices requires **147** arcs. Contradiction. QED.

## Lemma D: exact in/out regularity also impossible

By Lemmas B and C, all indegrees are at most seven. Their average equals the fixed outdegree seven, so **every indegree is exactly seven**.

Fix v, with outneighbors A of size seven, inneighbors B of size seven and nonneighbors C of size six. The [saturated-pivot lemma](M074_ELEMENTARY_18.md) says that in any oriented, triangle-free r-in/out-regular digraph on 3r vertices, each outneighborhood has minimum internal outdegree at least two, and each inneighborhood has minimum internal indegree at least two. Applying Lemma A to the induced graph on A and to the reversal of the induced graph on B shows that **both A and B are 2-in/2-out-regular**.

Each a in A must therefore send 7-2=5 arcs into the six-element C. Each b in B receives 7-2=5 arcs from C. Two five-element subsets of six elements necessarily intersect; hence for every a in A and b in B there is a c in C with a→c→b. An arc b→a would close a triangle, so **no arc goes from B to A**.

But each a in A can now receive at most one arc from v, two from A, none from B, and one from C (it points to five of the six vertices in C, preventing their reverse arcs). Its indegree is at most 1+2+0+1=**4**, contradicting indegree seven. QED.

The reduction and Lemmas A–D prove the stated finite theorem without an SAT solver.

## Provenance, verification and scope boundary

This extends the repository's [elementary (18,6) proof](M074_ELEMENTARY_18.md) using an exact seven-vertex degree lemma and a 145-versus-147 global arc budget. The [wustep/maths investigation](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md) already reports DRAT-verified (21,7) indegree partitions. We **do not assert novelty** or claim to have replayed its proof files. The published [Hladký–Král’–Norine bound](https://doi.org/10.1007/s00493-015-2662-5) does not cover the threshold 7/21=1/3.

Run `python3 -m unittest discover -s tests -p 'test_ch_seven.py' -v` for integer-bound checks and a sharp seven-vertex circulant control. These arithmetic tests are **not an exhaustive 21-vertex graph search** and do not replace independent expert review of the written proof. No Solved promotion, fixed-r=7 all-orders claim, or status change to the general conjecture is made.
