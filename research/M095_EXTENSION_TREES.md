# M095 — compact one-vertex extension refutations for the pinned K42 catalog

**2026-11-01; bounded certificate, not a new Ramsey bound.**
Work item `X-M095-K42-EXTENSION`, [claim #173](https://github.com/Svyable/100/issues/173);
scope SHA-256 `d7ad170a225683e60d1fcaad99cf57638acffb2d293331aec72af84deda07660`.

## Exact statement

Let `G_1,...,G_328` be the **specific** 42-vertex graphs in the publisher's
[graph6 catalog](https://users.cecs.anu.edu.au/~bdm/data/r55_42some.g6),
whose bytes are pinned at SHA-256
`067902e853d87b49bcef0d1d4c0e3bbadd238ee18bc65341b079a3ca4780eccb`.

**Finite certificate theorem.** For every one of these 328 graphs, the Boolean
one-vertex-extension formula has a complete unit-propagation binary
refutation tree containing **at most 51 nodes** (at most 25 branch nodes and
26 conflict leaves), with **maximum decision depth nine**. An independently implemented checker replays every
stored tree, directly recomputing the constraints from the source graph.
Consequently **none of these 328 colorings, nor their 328 color-swaps, can be
extended by a single vertex without creating a monochromatic K5**.

This is a **new compact certificate representation in this repository** of
a **known negative fact**. Nonextendibility of the 656 catalogued colorings
was reported by McKay–Radziszowski (1997) and separately checked by later
SAT work. No historical novelty of the 51-node bound, peer review, or
independent mathematical acceptance is claimed. The catalog is *not known
complete* among all 42-vertex Ramsey colorings, so the result does **not**
exclude K43 Ramsey colorings or prove R(5,5)=43.

## Reduction, with no hidden symmetry assumption

Fix one catalog graph G on vertex set {0,...,41}, with red edges of G and
blue nonedges. Let x_i=1 mean that the edge from a new vertex * to i is
red; x_i=0 means blue.

Every pre-existing red K4 on Q forces
`OR_{i in Q} NOT x_i`, because assigning all four red would make a red
K5 with *. Every pre-existing blue K4 on Q forces
`OR_{i in Q} x_i`. Since the original G has no monochromatic K5, **all**
new monochromatic K5s must contain *. Thus this CNF is satisfiable **if
and only if** the graph admits a valid one-vertex extension. There are
exactly 42 Boolean variables, and every clause has four literals.
No degree restriction, automorphism assumption, or catalog-completeness
assumption is imposed.

The generator enumerates K4s by bitset intersections and performs
deterministic DPLL with unit propagation. It stores **both branches**
of every binary decision; every leaf is a unit-propagation contradiction.
The verifier does **not** trust the DPLL search, its variable heuristic,
or the generator's K4 enumeration. It independently enumerates all
C(42,4) four-subsets, tests all six edges for monochromaticity, scans
the resulting clauses in reverse order using a separate list-valued
assignment engine, and checks each leaf has a contradiction. It rejects
incomplete trees, forced/invalid branch variables and premature leaves.

## Exact certificate

- `data/ramsey_extension_certificate.json`: all 328 indexed binary
  refutation trees, the original publisher digest, each red/blue K4
  count and each tree's node count. Archive size: **86,527 bytes**;
  SHA-256: `f8fa8f5ee2a9a7e8c63b9f53b5623fd927f222c61a49e606e7a9b816a1a2fc57`.
- `scripts/ramsey_extension.py --check`: replay **every** stored tree
  against the original source, using the independent verifier.
- `scripts/ramsey_extension.py --write`: rebuild the proof trees from
  the generator, then replay all of them before writing a replacement
  certificate. Never hand-edit the archive.
- `python3 -m unittest discover -s tests -p test_ramsey_extension.py -v`:
  positive SAT control, independently recomputed K4s, and adversarial
  malformed/shortened refutation trees.

The generator's exact scan of all 328 instances returned zero SAT
assignments. The 328 tree sizes were:

| Nodes (including conflict leaves) | Graphs |
|---:|---:|
| 39 | 215 |
| 41 | 66 |
| 43 | 39 |
| 45 | 6 |
| 47 | 1 |
| 51 | 1 |
| **Total** | **328** |

The decision-depth distribution is 5:217, 6:66, 7:37, 8:6, 9:2.
The **51-node / depth-nine maxima are upper bounds for this specific
unit-propagation DPLL proof system on this specific catalog**, not lower
bounds on SAT proof size, results about arbitrary K42 graphs, or a proof
of a new Ramsey bound.

## Failed avenues and prior art

The attempt to find a K43 coloring by extending the 328 published K42
examples failed on **all** examples; this is expected in light of the
published literature. A different K42 coloring, if one exists outside
the catalog, may still extend. No proof of catalog completeness or
enumeration of all K43 colorings was attempted.

- [McKay and Radziszowski, *Subgraph Counting Identities and Ramsey Numbers*,
  JCTB 69 (1997)](https://doi.org/10.1006/jctb.1996.1741):
  earlier known nonextendibility and conjectural catalog completeness.
- [Angeltveit and McKay, *R(5,5) ≤ 46*, JGT (2026)](https://doi.org/10.1002/jgt.70029):
  contemporary primary bound `43 ≤ R(5,5) ≤ 46`.
- [Janowska and Gniewislawa (May 2026), independent SAT extension
  verification](https://github.com/antydizajn/ramsey-r55-verification):
  reports UNSAT on the same 656 source/color-swap instances, so the
  negative nonextendibility finding is **not new**.
- [McKay's source catalog](https://users.cecs.anu.edu.au/~bdm/data/ramsey.html):
  source of the pinned 328 graph6 records.

## Next falsifier and review boundary

Attempt to corrupt one stored tree or source record: the verifier must
reject it. Independently implement graph6 decoding and a third
constraint enumerator, compare all 328 trees and the SHA lock, and
seek a specialist review of the reduction and certificate replay.
For progress on the **open** Ramsey problem, the meaningful next
target is a K43 coloring not obtained by one-vertex extension of
these 656 known K42 examples, or a **complete** classification of
the relevant K42 deletion class with independently checked proof
traces. This record does not discharge O-M095-01, change
`data/solved.json`, or record independent acceptance.
