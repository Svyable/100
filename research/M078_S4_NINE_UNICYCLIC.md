# M078 — connected unicyclic obstructions to paired card-motif signatures

**Date:** 2026-11-02. **Work ID:** `X-M078-S4-NINE`; [claim #262](https://github.com/Svyable/100/issues/262).
**Scope SHA-256:** `d4e86c4ea0c6af8aa1668d0dd37e1e13dcb1022b3ff62fc1b3a7b08923f040ce`.

**Evidence status:** elementary all-orders proof written by the author, plus two distinct exact card-counting algorithms and adversarial tests. **Not independently reviewed; historical novelty is unestablished.** This is a failure of a *compressed deck statistic*, **not** a counterexample to graph reconstruction. No M078 solved-status or independent-outcome promotion is justified.

## Precise result

For a finite simple graph `G`, write `D(H)` for the sorted degree multiset of `H`, and `c_j(H)` for its number of simple (not necessarily induced) cycles of length `j`. Define the **paired** card statistic

`S_k(G) = multiset_{v in V(G)} (D(G-v), c_3(G-v), ..., c_k(G-v))`.

For `k=4`, this is exactly the prior repository's `S4`: degrees, triangles and four-cycles in each card, kept together before sorting.

**Proposition (connected, all-orders counterexamples).** For every integer `k >= 4` and every `n >= k+5`, there are two **connected, unicyclic, nonisomorphic** simple graphs `G_{k,n},H_{k,n}` on `n` vertices such that `S_k(G_{k,n})=S_k(H_{k,n})`. Their unique cycle lengths are respectively `k+2` and `k+1`. Both are **planar and subcubic** (maximum degree three). Since these cycle lengths have opposite parity, **one graph is bipartite and the other is not**. In particular, **S4 is not injective for any n >= 9, even on connected unicyclic graphs, and cannot determine bipartiteness there.** Relative to the repository's exact n<=8 S4 certificate, nine is the sharp first failure order; that smaller-order census has not been independently specialist-reviewed.

The proposition is an exact negative result about *every fixed finite cutoff of cycle-count augmentations*. It does not imply failure of the full vertex-deleted deck, or of richer card invariants such as induced five-vertex subgraph counts.

## Explicit nine-vertex pair

Use vertices `0,...,8`, and the following unordered edge lists:

```text
A9: (0,1) (1,2) (2,3) (3,4) (4,5) (5,0) (0,6) (5,7) (7,8)
B9: (0,1) (1,2) (2,3) (3,4) (4,0) (0,5) (5,6) (5,7) (7,8)
```

Both have nine edges and are connected. `A9` has a unique six-cycle; `B9` has a unique five-cycle. Their shared degree multiset is `(1,1,2,2,2,2,2,3,3)`. Every triangle and four-cycle count in every card is zero. The exact paired card-degree multisets are equal; the independently counted direct-card transcript is:

```text
degree multiset of card              multiplicity
(0,1,1,2,2,2,2,2)                     1
(0,1,2,2,2,2,2,3)                     1
(1,1,1,1,2,2,2,2)                     1
(1,1,1,1,2,2,3,3)                     2
(1,1,1,2,2,2,2,3)                     2
(1,1,2,2,2,2,3,3)                     1
(1,2,2,2,2,2,2,3)                     1
```

The full decks **are** different: `B9` has a five-cycle and `A9` does not. Deleting a vertex outside the five-cycle retains it. Equivalently, Kelly's double-counting identity recovers `c_5(G)` from the full deck whenever `n>5`.

## Proof

**Degree-neighborhood lemma.** Define `P(G)` as the multiset over vertices `v` of pairs `(d_G(v), multiset{d_G(u): u adjacent to v})`. If `P(G)=P(H)`, then the multisets `{D(G-v):v in G}` and `{D(H-w):w in H}` are equal. Indeed, `P` determines the global degree multiset `D`; for a vertex of profile `(d,N)`, the card degree multiset is obtained from `D` by deleting one occurrence of `d` and, for every neighbor-degree occurrence `q` in `N`, replacing one occurrence of `q` by `q-1`. This is exact even when degree values repeat.

The two base graphs have **identical** profile multisets:

| Degree | Multiset of neighbor degrees | Multiplicity |
|---:|---|---:|
| 1 | (2) | 1 |
| 1 | (3) | 1 |
| 2 | (1,3) | 1 |
| 2 | (2,2) | 2 |
| 2 | (2,3) | 2 |
| 3 | (1,2,3) | 1 |
| 3 | (2,2,3) | 1 |

Since each is unicyclic with unique cycle longer than four, all triangle and four-cycle card counts vanish. The lemma proves `S4(A9)=S4(B9)` without relying on enumeration.

**Cycle subdivision.** In each base graph, the cycle edge `(1,2)` has degree-two endpoints. Subdivide that edge once in both graphs. All existing degree-neighborhood profiles remain unchanged (a degree-two neighbor is replaced by a degree-two neighbor), and each graph gains exactly one profile `(2,(2,2))`. Repeat `s=k-4` times, always subdividing a degree-two-to-degree-two edge in the same cycle segment. The unique cycles now have lengths `6+s=k+2` and `5+s=k+1`. Both are longer than `k`, so every card has `c_3=...=c_k=0`. The degree-neighborhood lemma gives `S_k` equality at order `9+s=k+5`.

**Connected extension to every larger order.** Both original graphs have the common terminal leaf `8`, whose neighbor `7` has degree two and whose other neighbor `5` has degree three. The cycle subdivision leaves this tail unchanged. Append one new leaf to the current terminal leaf **in both graphs**. The old leaf changes degree 1 to 2, its degree-two neighbor's profile changes by replacing a neighbor-degree 1 by 2, and the new leaf has profile `(1,(2))`. The corresponding affected profiles are identical in both graphs. Inductively this remains true for any number of appended vertices (after the first step the other neighbor of the degree-two predecessor has degree two). No new cycles arise, and connectivity is preserved. Thus the construction works at every `n >= k+5`.

**Nonisomorphism.** A connected unicyclic graph has exactly one simple cycle; an isomorphism preserves its length. The constructed graphs have unequal cycle lengths. QED.

## Reproduction and adversarial verification

```sh
python3 scripts/m078_s4_nine.py --check --json
python3 -m unittest discover -s tests -p 'test_m078_s4_nine.py' -v
python3 scripts/regen.py --check --fast
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

The direct checker physically deletes each vertex, recounts triangles over vertex triples, and recounts four-cycles via the three undirected cyclic orders on each four-set. A separate bitset implementation counts triangles by edge/common-neighbor incidences and four-cycles by opposite-pair common neighbors. The tests compare the two on 75 seeded random graphs of orders 5, 7, 9, including motif-rich graphs; positive controls include a four-cycle and `K4` (three four-cycles). Mutation, duplicate-edge and disconnected-unicyclic controls must fail. The all-orders argument itself is **structural**, not an extrapolation from tested orders.

**Discovery and failed avenues.** A seeded random nine-vertex graph scan first produced many signature collisions that were merely relabelings. A later 18-edge pair had matching S4 but 36 versus 37 five-cycles; it was correct but unnecessarily dense. A fixed-nine-edge sample found the sparse pair above, with zero versus one five-cycle. Random sampling is a discovery heuristic, not proof of minimality or a complete nine-vertex census. The deterministic proof above replaces the sampling assumption. The independent card counter was implemented separately from the bitset search counter. No full census of all 274,668 nine-vertex unlabeled graphs is claimed.

## Prior art and novelty boundary (checked 2026-11-02)

- Brendan D. McKay, [*Reconstruction of small graphs and digraphs*](https://arxiv.org/abs/2102.01942) (2021/2022): the **full deck** reconstructs graphs through order 13. Our pair does not contradict that, because S4 forgets most of each card.
- Wendy Myrvold, [*The degree sequence is reconstructible from n-1 cards*](https://doi.org/10.1016/0012-365X(92)90053-I) (1992): reconstructing the original degree sequence from cards is different from reconstructing the graph from only the cards' degree sequences.
- Groenland, Johnston, Kupavskii, Meeks, Scott and Tan, [*Reconstructing the degree sequence of a sparse graph from a partial deck*](https://doi.org/10.1016/j.jctb.2022.07.004) (2022): partial-deck degree recovery, not the paired S4 threshold.
- [Existing repository M078 card-signature dossier](M078_CARD_SIGNATURE.md): author-checked injectivity through order eight and an explicit failure of the weaker S3 at order eight. Our connected S4 failure at order nine is a new **repository-side** negative boundary, not an assertion of historical mathematical priority.

The degree-neighborhood profile is a standard first-round color-refinement statistic, and its limitations are classical. No exhaustive literature search or specialist priority adjudication has established that the precise paired S4 statement or the fixed-cutoff family is unpublished.

**Next falsifiers:** Independently check the seven-row profile table and the all-orders subdivision/extension argument; replay the n<=8 completeness certificate with a separate graph-isomorphism implementation; compare against prior literature on vertex-deleted degree decks and color refinement. Challenge whether any additional **fixed-radius** card invariant defeats this construction, and test an induced-five-vertex motif augmentation on the nine-vertex witness. No independent review, accepted outcome, new coverage slot or Solved-ledger change is recorded.
