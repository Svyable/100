# M078 — induced P₄ separates the six-vertex degree–triangle collisions

**Work packet:** O-M078-01, scope digest
`c25d1f1ccd3a55bdd178da6dcb4747199d51a0190d9321ccb7e1b21af505fe62`.
**Claim:** [#126](https://github.com/Svyable/100/issues/126).
**Classification:** exact finite proposition with computational exhaustion and a
double-path verifier. **Independent mathematical and statement-fidelity review
pending. Novelty in the wider literature has NOT been established.** This does
not resolve the unrestricted graph reconstruction conjecture.

## Precise finite proposition

Let G be a simple, undirected graph on exactly six vertices. Define

- D(G): the *sorted degree sequence*, an isomorphism invariant readable
  from the deck of vertex-deleted cards;
- T(G): the number of triangles;
- P₄(G): the number of **four-element vertex subsets inducing a path of
  length three**, not the number of arbitrary non-induced length-three walks.

**Sharp signature theorem (finite proof plus explicit obstruction):** among the 156
isomorphism classes of six-vertex graphs, the signature

`(D(G), T(G), P₄(G))`

is injective. The weaker signature `(D(G), T(G))` has exactly
20 collision classes, each containing two nonisomorphic graphs. In 14
of those pairs, the P₄ counts differ by one; in the other six, by
three. No pair remains ambiguous. Conversely, for **every n >= 7**, there exist two
nonisomorphic n-vertex graphs having the same three-coordinate signature.
The positive side n <= 6 follows by census; the negative side for all n >= 7
follows from one explicit seven-vertex pair and isolate padding.

**Illustrative certificate pair:** edge codes 10376 and 25601 share
degree sequence (1,1,1,1,2,2), with zero triangles, but have 0 and 1
induced P₄ instances respectively. These codes are **not graph
identifiers independent of our bit convention**: bit positions represent
the edge pairs (0,1), (0,2), …, (4,5), ordered lexicographically.

## Explicit obstruction at seven vertices and every larger order

Set \(G = K_{1,3} \sqcup K_3\), a four-vertex star disjoint from a
triangle. Set \(H=P_3 \sqcup W\), where \(P_3\) is a three-vertex path
and \(W\) is the **paw**: a triangle with a pendant leaf.

The two degree multisets are identical:

\[
D(G)=D(H)=(1,1,1,2,2,2,3).
\]

Each graph contains exactly one triangle. Neither contains an induced
four-vertex path: each of the two components in each graph is too small
to contribute an induced P₄ except its own four-vertex component,
and neither \(K_{1,3}\) nor the paw is \(P_4\).
Thus \(P₄(G)=P₄(H)=0\), so the signatures agree.

They are **not isomorphic**: the triangle in \(G\) constitutes an
entire connected component of size 3; the triangle in \(H\) lies in a
connected component of size 4. Equivalently, the size-4 components
are a star versus a paw, which have different edge counts.

For any integer \(t \ge 0\), the graphs \(G\sqcup tK_1\) and
\(H\sqcup tK_1\) remain nonisomorphic, while their degrees acquire
the same \(t\) zeros and their triangle and induced-P₄ counts stay
unchanged. This **proves failure for every n=7+t**, without requiring
an exhaustive large-n search. The explicit edge lists and
edge-bit codes are stored under `sharpness_witness_n7` in the certificate.

## Why the invariant really comes from the deck

We use the classical **Kelly double-counting identity** (1957), not a
new lemma. Let s_H(G) count induced vertex subsets of G whose induced
graph is isomorphic to a fixed H with h vertices, where h<n=|V(G)|.
Each copy of H occurs in precisely n−h vertex-deleted cards: deleting
any vertex outside that copy retains it, and deleting one inside destroys
it. Hence

\[
   (n-h)\,s_H(G) = \sum_{v\in V(G)} s_H(G-v).
\]

For H=P₄ and n=6 this becomes

\[
   P₄(G) = \frac{1}{2}\sum_{v\in V(G)}P₄(G-v).
\]

Therefore P₄(G) is determined by the **unordered multiset** of
vertex-deleted cards; it does not require reconstructing G first.
Similarly T(G) is obtained from the card triangles divided by n−3=3.
The edge count is recovered from card edge totals divided by n−2=4;
then the degree multiset follows by subtracting each card's edge count
from the recovered edge count. Thus **all three coordinates are
deck-readable**, rather than merely directly computable on a
labelled graph.

A source for Kelly's identity and its induced-subgraph form is
Dalili et al., *Discrete Mathematics* 308 (2008), Lemma 3.2:
[reconstruction.pdf](https://www.usna.edu/Users/math/traves/_files/documents/reconstruction.pdf).
See also the discussion of induced k-decks in
[Groenland–Johnston–Scott–Tan, Reconstruction from smaller cards](https://people.maths.ox.ac.uk/scott/Papers/smalltreerecon.pdf).
Neither source should be read as claiming this particular six-vertex
three-coordinate signature is novel.

## Exhaustive proof certificate and independent verifier

Run from the repository root:

```sh
python3 scripts/m078_p4_separator.py --check --json
python3 -m unittest tests/test_m078_p4_separator.py -v
```

The committed certificate is
[`data/reference/m078_p4_pairs.json`](https://github.com/Svyable/100/blob/main/data/reference/m078_p4_pairs.json).
It lists the 20 colliding pairs in lexicographic edge-bit-code order,
their common degree sequence and triangle count, and both P₄ counts.
A SHA-256 hash pins the canonical JSON serialization of those 20
records:

`f00c172f4d827c71b6cfaf3c83f7a9b00cf6fce1c620be6a47f78b03d634120e`

The checker is not a printout of a trusted search result. It independently:

1. Constructs the complete 156-isomorphism-class census using
   orderly graph extension.
2. Certifies the count by Burnside's lemma and independently validates
   nonisomorphism with degree-respecting canonical edge-list forms.
3. Counts P₄ **directly** from induced degree patterns (1,1,2,2).
4. Recounts P₄ from all five-vertex cards using a separate predicate:
   a connected three-edge tree whose maximum degree is at most two.
   The star K₁,₃ is an adversarial negative control; **connected and
   three edges alone are not sufficient**.
5. Reconstructs the other signature coordinates from card edge and
   triangle counts, rebuilds all collision pairs from these independently
   computed values, and compares them with the committed certificate.
6. Rejects mutated records and digests through automated tests.

Completeness of the **finite** claim follows from the census
certification plus verification that every collision pair has unequal
P₄ counts. It does *not* provide a symbolic classification of arbitrary
n-vertex graphs.

## Limits and useful next question

This is an exact statement only for n=6. At n=5, degree sequence and
triangle count already distinguish the 34 graph classes. Neither
number, nor P₄, has been shown here to distinguish every graph for
n≥7. Proving that a universal finite list of such signatures separates
all graphs would be far stronger and is **not** claimed.

The immediate next mathematical experiment is to find the first n
and pair of nonisomorphic graphs with matching (D,T,P₄), and classify
what new deck-reconstructible induced-subgraph statistic separates
that pair. That work must use independently checked census, rather
than extrapolating this n=6 result.

**Status:** O-M078-01 remains pending a separate person's mathematical
and statement-fidelity review; its current automated check is not
independent human acceptance. The project's solved ledger and
conjecture evidence states are unchanged.
