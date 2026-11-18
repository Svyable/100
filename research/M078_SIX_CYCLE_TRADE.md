# X-M078-SIX-CYCLE-TRADE — candidate exact obstruction packet

**Claim:** [Svyable/100 #385](https://github.com/Svyable/100/issues/385) (2026-11-17). Author-produced calculation and checker, **not independently reviewed**, and historical novelty **not assessed**. This is about a *compressed six-leaf distance-row fingerprint*, NOT a counterexample or proof of the graph reconstruction conjecture.

## Statement (restricted)

Consider two unrooted binary phylogenetic trees on an identified set of six leaves, with strictly positive real edge lengths, no degree-two vertices, and exactly four internal degree-three vertices. Let the first internal-hub skeleton be the three-spoke star, and the second be a four-hub path. Their 15 leaf-pair distances are indexed by unordered pairs of leaves.

**Claimed restricted theorem:** The two distance matrices cannot agree outside the six edges of a single Hamilton cycle of the six leaves and differ on that cycle by an alternating exchange of two distinct values. In fact, the homogeneous equalities implied by this exchange force the **central internal edge of the path-hub tree to have length 0**, contradicting strict positivity. The conclusion holds for all real positive edge lengths; edge lengths are not enumerated or bounded.

This does **not** prohibit exchanges with a non-Hamilton support graph, 3+ colors, multiple simultaneous cycles, or arbitrary row-multiset collisions. It does **not** settle M078.

## Why these are the complete cases

Fix the star cherries `(0,1)`, `(2,3)`, `(4,5)`; every other star labeling is equivalent under its automorphism group of size `2^3 * 3! = 48`. The path-hub topology has two leaves adjacent to each endpoint and one adjacent to each middle hub; there are `6! / (2*2*2) = 90` labeled allocations, quotienting endpoint swaps and reversal. There are `(6-1)!/2 = 60` undirected six-leaf Hamilton cycles.

For any such cycle, its two alternating edge sets `R` and `B` are disjoint perfect matchings. The old matrix has common value `r` on `R` and `b` on `B`, and the new has `b` on `R` and `r` on `B`. If the original premise is expressed as *row-multiset equality with exactly this single connected 6-edge difference support*, this two-value alternation is **forced**: each leaf has exactly two modified incident pair distances, which must be exchanged. Following the six-cycle then forces the values on alternate edges to coincide. Thus the same certificate excludes a single Hamilton cycle as the entire nonzero difference support.

Let `S` and `P` be the `15 x 9` tree edge-incidence matrices for the star and path, and let `x,y` be their nine edge lengths. The 19 homogeneous equations `A (x,y)^T = 0` are:

1. `S_i x = P_i y` for the nine leaf pairs outside `R union B`;
2. for both `S x` and `P y`, the three distances on `R` are equal and the three on `B` are equal (eight equations);
3. `S_r x = P_b y`, and `S_b x = P_r y`, for representatives `r in R`, `b in B` (two equations).

For each of **142** representatives of the `48` star-automorphism action on the `90*60 = 5400` `(path allocation, undirected cycle)` pairs, the packet provides an explicit sparse *rational row combination* `z` such that `z^T A = e_16^T` (zero-based index 16 is `y_7`, the path's **middle** hub-to-hub edge). Consequently every solution has `y_7=0`. The orbit sizes are 86 of size 48, 50 of size 24, and 6 of size 12, summing to 5400. Automorphisms preserve the middle path edge under path reversal, so the conclusion transfers from representatives to every case.

These are exact rational identities: no numerical optimizer or positivity approximation is used by the checker.

## Reproduction

Requires **Python 3.9+**, standard library only. No internet, network, solver, random seed, compilation or SymPy needed for verification.

```sh
python3 scripts/m078_six_cycle_check.py scripts/certificates/m078_six_cycle_trade.json
python3 -m unittest discover -s tests -p 'test_m078_six_cycle_check.py' -v
```

Expected summary: `certificate_verified: true`, `exact_certs: 142`, `systems_proved: 5400`, `target: path_middle_edge_is_zero`. The checker reconstructs all tree-path incidence rows by BFS, enumerates all cycles and path allocations independently of the generator, recomputes all 48 star symmetries and every orbit, checks disjoint union/coverage, and **multiplies each sparse rational identity directly**. The tests reject changed certificate coefficients, a deleted orbit, an overlapping orbit, an invalid matching and a changed theorem target.

Certificate creation was done by a *separate author-controlled* SymPy dual linear solve (choose zero free variables) and cross-checked against independent integer row-reduction over all 5400 systems. This is independent **algorithmic** checking, not independent third-party mathematical or prior-art verification.

## Failed or weaker avenues (recorded)

* Holding only the nine distances outside a Hamilton cycle fixed was insufficient to force the path's central edge to zero: **1416 of 5400** cases had no coordinate identically zero in the exact homogeneous solution space. This demonstrates why we cannot replace the full 19 equations with nine.
* Nine fixed distances plus the six row-**sum** equations (rather than complete row multiset swaps) left **24 of 5400** configurations where the path's central edge was not forced to zero; no general row-sum theorem is claimed.
* A constant signed perturbation of the distances on alternate Hamilton-cycle edges has the same 24 exceptional configurations unless the matching-class equalities are imposed. So the two-level hypothesis is essential to this proof route.
* Earlier four-cycle obstruction: [#381](https://github.com/Svyable/100/issues/381), [PR #382](https://github.com/Svyable/100/pull/382). This packet analyzes the **next connected simple alternating-cycle size**, not all support-six modifications; for example, a 3-color trade supported on `K4` is outside this packet.

## Falsifiers and boundaries

* Find a six-leaf positive-real-length star/path witness with exactly one six-cycle support and identical leaf-row multisets. It would directly falsify the claimed theorem and at least one certified equality or orbit reduction.
* Find a duplicate or absent `(path,cycle)` case in the independent full 5400-set orbit partition, or a false `z^T A = e_16^T` identity; the checker is designed to fail.
* The next structural attack is a non-Hamilton six-edge 3-color trade (e.g. `K4`) or an 8+ edge simultaneous trade, not an enlarged length box.
* Independent expert review should confirm what constitutes a legitimate two-value row trade, the completeness of the 90 and 60 classifications, and the topology-to-matrix encoding; separate prior-art review is also required. Neither is claimed here.

## Primary literature and novelty

- P. Buneman, *The Recovery of Trees from Measures of Dissimilarity* (1971): https://www.research.ed.ac.uk/en/publications/the-recovery-of-trees-from-measures-of-dissimilarity/ — full tree metric context / four-point condition.
- A. Dress, K. Huber, M. Steel, *Lassoing a phylogenetic tree I: Basic properties, shellings, and covers* (2011/2012): https://arxiv.org/abs/1102.0309 — incomplete **labeled** distance information and reconstruction. Our row-multiset trade hypothesis is different; we do not claim the restricted statement is absent from literature.

No evidence of commercial operational gain, third-party acceptance, novel algorithmic advantage, or protectable exclusive IP. These are public mathematical computations. Project 100 PR Landing was not modified.
