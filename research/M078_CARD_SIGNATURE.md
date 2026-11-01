# M078 — a sharp finite boundary for paired card-motif signatures

**Status 2026-11-01:** exact finite computational classification; independently
replayed card statistics and Burnside class counts. **Mathematical novelty has
not been established; this is not a proof of the reconstruction conjecture.**
[Bounded research claim #130](https://github.com/Svyable/100/issues/130).
The separate [O-M078-01 / induced-P4 proposal](https://github.com/Svyable/100/issues/126)
is not discharged by this work.

## Question

How much of a graph's vertex-deleted deck do we need to distinguish small
graphs without comparing the full graph isomorphism types of the cards?

For a finite simple graph `G`, write `D(G) = {G-v : v in V(G)}` as a
**multiset**, counting repeated cards. For a graph `H`, let:

- `d(H)`: sorted multiset of vertex degrees;
- `t(H)`: number of (not necessarily induced) triangles;
- `q(H)`: number of (not necessarily induced) four-cycles, each counted once.

Consider two deck-computable signatures, with each card's statistics **paired**
before sorting:

```
S3(G) = multiset_{v in V(G)} (d(G-v), t(G-v))
S4(G) = multiset_{v in V(G)} (d(G-v), t(G-v), q(G-v))
```

These are much smaller summaries than the full isomorphism types of the cards.
Do not replace the paired multiset with separate unpaired histograms: that is a
different invariant and is not tested here.

## Three exact finite assertions

1. **Completeness of S3 through seven vertices.** Among all finite simple
   graphs on each fixed order `3 <= n <= 7`, `S3` separates every graph
   isomorphism class. It is not assumed complete at larger orders.
2. **Sharp obstruction at eight vertices.** Two explicitly listed, triangle-free
   graphs of order eight share `S3`, but one has two four-cycles and the other
   has one. They are not isomorphic. This is a counterexample to **S3 as a
   complete signature**, **not** to the graph reconstruction conjecture.
3. **Completeness of S4 through eight vertices.** At each fixed order
   `3 <= n <= 8`, `S4` separates every graph isomorphism class.

All three assertions follow from the finite enumeration certificates below.
They are not universal structural theorems and have not received independent
specialist mathematical review.

## Certificate table

| n | Graph isomorphism classes | distinct S3 | S3 excess | distinct S4 | S4 excess |
|---:|---:|---:|---:|---:|---:|
| 3 | 4 | 4 | 0 | 4 | 0 |
| 4 | 11 | 11 | 0 | 11 | 0 |
| 5 | 34 | 34 | 0 | 34 | 0 |
| 6 | 156 | 156 | 0 | 156 | 0 |
| 7 | 1,044 | 1,044 | 0 | 1,044 | 0 |
| 8 | 12,346 | 12,257 | **89** | 12,346 | **0** |

"Excess" is the number of nonisomorphic classes minus the number of
signature values. It is not necessarily the number of colliding *pairs*.

**Constructive completeness:** the project's graph-census generator builds one
representative for each isomorphism class at orders 3 through 7. Its separate
Burnside count and a second canonical-labelling check already certify the
smaller census. For order 8, delete any vertex from an arbitrary graph; its
seven-vertex remainder is isomorphic to one of those 1,044 representatives.
That graph is therefore isomorphic to one of the **1,044 × 128 = 133,632**
extensions formed by connecting a new vertex to every subset of the old seven.
Some extensions are isomorphic; that is harmless because only distinct
signatures are counted.

Independently, Burnside's lemma counts unlabeled n-vertex graphs as

```
(1/n!) * sum over permutations p in S_n of 2^(orbits of p on unordered vertex pairs).
```

It gives 12,346 classes at n=8. A signature is invariant under relabeling,
so its number of distinct values can never exceed the number of classes.
The exact search finds **12,346 distinct S4 values** in the complete extension
cover. Equality gives injectivity up to isomorphism at n=8. The same counting
argument applies to S3 through n=7. The executable checker also stores SHA-256
fingerprints of sorted signature values; hashes detect drift but are not
the mathematical justification.

## Eight-vertex witness: S3 fails, S4 detects the difference

Vertices are integers `0,...,7`. In the fixed edge-list format `[u,v]`
with `u<v`, graph **A** has edges:

```text
(0,4) (0,7) (1,4) (1,5) (1,7)
(2,5) (2,6) (3,5) (3,6) (4,6)
```

Graph **B** has edges:

```text
(0,4) (0,7) (1,4) (1,5)
(2,5) (2,6) (2,7) (3,5) (3,6) (4,6)
```

Both have degree sequence `(2,2,2,2,3,3,3,3)`, ten edges and zero triangles.
Their full paired **S3** multisets agree exactly, including repeated cards
(see the JSON certificate). But **A has two four-cycles and B has one**,
which proves they are nonisomorphic without relying on a canonical-label
algorithm. This discrepancy is itself reconstructible from the full deck:
each four-cycle survives deletion of exactly `n-4` vertices, so
`q(G) = sum_v q(G-v)/(n-4)` for `n>4`. The pair is therefore
**not a same-deck counterexample**. S4 distinguishes them.

## Independent checks

```sh
python3 scripts/deck_signature_frontier.py --write
python3 scripts/deck_signature_frontier.py --check         # exhaustive two-path card recheck
python3 scripts/deck_signature_frontier.py --check --quick # still exhaustive signature and Burnside counts
python3 -m unittest discover -s tests -p test_deck_signature_frontier.py -v
```

The **search path** uses bitset adjacency, deletion identities for degree and
triangle counts, and common-neighbor counts for C4 in each card. The
**independent card checker** physically constructs each deleted edge set,
recomputes degree sequences from incident edges, enumerates triples for
triangles and three possible cyclic orders per quadruple for C4.
Its full mode checks every generated input independently. The
**isomorphism-class count** is a distinct Burnside orbit calculation and
does not depend on interpreting the signature. The tests inject a mutated
edge, invalid edge lists, and vertex relabelings as negative/positive controls.

The frozen data live in
[`data/card_motif_signatures.json`](../data/card_motif_signatures.json).
An accepted proof of a stronger reconstruction theorem would still need an
independent scope and novelty review.

## Prior art and novelty boundary

- Brendan McKay, [*Reconstruction of small graphs and digraphs*
  (Australasian Journal of Combinatorics 83, 2022)](https://ajc.maths.uq.edu.au/pdf/83/ajc_v83_p448.pdf),
  computationally verifies full graph reconstruction through 13 vertices.
  This result is about a **weaker compression of the full deck** and does
  not extend his reconstruction bound.
- Kelly's classical reconstruction observations apply to subgraph counts;
  degree sequences are also reconstructible from cards. See Wendy
  Myrvold, [*The degree sequence is reconstructible from n−1 cards*
  (Discrete Mathematics 102, 1992)](https://doi.org/10.1016/0012-365X(92)90053-I).
- Separate work on [induced P4 counts](https://github.com/Svyable/100/pull/120)
  addresses a different invariant and at most six vertices in its initial PR.

I did not find an exact published formulation of this **paired S3/S4
signature threshold** in a targeted search; absence from a search is
not evidence of priority. Treat it as a reproducible mathematical
candidate requiring external literature and specialist review.

**Next research step:** test S4 at nine vertices with a complete
isomorph-free generator or find a small independent collision. Do not
announce a universal bound or change `data/solved.json`, the evidence state
of M078, or the O-M078-01 obligation on these data.
