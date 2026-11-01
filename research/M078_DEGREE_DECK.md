# M078 — card degree-sequence deck through 7 vertices

**Dated:** 2026-11-01. **Scope:** a deck-readable invariant on the complete census of graphs with 3 to 7 vertices. **Not claimed:** a reconstruction theorem, a result past McKay's published verification through 11 vertices, or a discharge of obligation `O-M078-01` (that still needs a reviewer who is not the author).

## The invariant

For a graph G, write D(G) for the multiset of degree sequences of its vertex-deleted subgraphs, and t(G) for the number of triangles. Both are functions of the deck: each card determines its own degree sequence, and the triangle count is the sum of the cards' triangle counts divided by n-3 (Kelly's count for n >= 4).

## Certificate

The mine [`deck_invariants`](../scripts/mines/deck_invariants.py) enumerates every graph through 7 vertices (OEIS A000088: 4, 11, 34, 156, 1044). Two implementations of D(G) must agree on every graph: the packed cards, and deletion from the adjacency list.

| n | Graphs | Excess of degree sequence + triangles | Excess of D(G) + t(G) |
|---:|---:|---:|---:|
| 6 | 156 | 20 | 0 |
| 7 | 1044 | 422 | 0 |

D(G) alone does not finish n = 6. Four pairs share a degree-sequence deck; each pair is one triangle-free graph and one graph with two triangles. Adding t(G) separates them. So D(G) + t(G) is strictly stronger than degree sequence plus triangle count.

`degree sequence + triangles` separates the census only through 5 vertices. `D(G) + t(G)` separates it through 7.

## What this does not do

McKay (1997) already checked reconstruction for every graph on at most 11 vertices. Matching a coarse invariant through 7 vertices does not improve that verification and does not prove the reconstruction conjecture. The next useful lemma is structural, for a family outside that published range.
