# M097 — eight-vertex graph-metric subtour gap census

**Date:** 2026-11-01 UTC. **Claim:** [#175](https://github.com/Svyable/100/issues/175). **Work packet:** X-M097-GRAPH8. **Status:** author-derived, exact finite computation with rational self-checks, **pending independent mathematical and prior-art review**. Not the unrestricted metric TSP four-thirds conjecture, not a new asymptotic bound, and not a claim of historical novelty.

## Exact question and result

For each connected simple undirected unweighted graph G on exactly eight vertices, set c_G(i,j) equal to its shortest-path distance. This defines a complete-graph metric. Let TSP(c) be the minimum Hamiltonian-cycle cost and HK(c) the minimum of the **symmetric subtour LP**:

- minimize sum_{i<j} c_ij x_ij;
- x(delta(v)) = 2 for every vertex;
- x(delta(S)) >= 2 for every nonempty proper S;
- x_ij >= 0.

The finite census, as computed and exactly replayed by the author, gives

    max_G TSP(c_G) / HK(c_G) = 10/9.

There are **11,117** connected unlabelled eight-vertex graph classes. Their ratios are:

| Ratio | Graph classes |
|---|---:|
| 1 | 11,055 |
| 18/17 | 44 |
| 20/19 | 16 |
| 10/9 | 2 |

The two maximizers have graph6 strings "Gk_G`K" and "Gk_GdK", and **both have diameter three**, so they are *not* instances of the 1–2 metric subclass. Each has TSP = 10 and HK = 9. The first graph's nine edges, with vertices numbered 0..7, are

    (0,1) (0,3) (0,4) (1,2) (2,7)
    (3,6) (4,5) (5,7) (6,7).

The first maximizer is the three-path theta graph with internally disjoint 0-to-7 paths of length three; the second adds the direct edge (0,7). This is structurally related to the classical graphic-metric lower-bound family, so the extremal construction itself is **not** claimed new. The stdlib-only verifier decodes both graph6 strings and checks all shortest-path distances without using the enumeration library.

A further *finite census observation* is that all connected eight-vertex graph metrics of diameter at least four have ratio one. This is not a general theorem for larger n.

## Exhaustiveness and exact certificates

1. NetworkX's 1,044 unlabelled seven-vertex atlas graphs are extended by every one of the 2^7 possible neighborhoods of a new eighth vertex. Every eight-vertex graph has a seven-vertex vertex-deletion graph, so this generates all eight-vertex isomorphism classes. Disconnected extensions are removed. Weisfeiler–Lehman hashes only **bucket** candidates; NetworkX's exact graph-isomorphism test determines duplication. The final count 11,117 agrees with the standard connected-unlabelled-graph count, but an independent generator is still desirable.
2. Every graph metric is recomputed from exact integer shortest paths. A 2,520-row matrix of Hamiltonian cycles (one vertex fixed, reversal quotiented) computes TSP. The two maximizers are independently checked by a different, pure-Python Held–Karp integer dynamic program and brute-force tours.
3. SciPy HiGHS proposes primal variables, degree duals and nonnegative cut duals for the 28-variable LP with eight degree equations and 119 nonredundant nonsingleton cut inequalities (one of each complementary pair; singleton cuts follow from degree equalities). **For every graph**, the script rationally reconstructs these numbers, checks every primal constraint, every nonnegative dual reduced cost, and exact equality of primal and dual objectives. An LP solver exit code or floating-point optimum alone is never accepted.
4. The entire graph6/TSP/HK stream, in enumeration order, hashes to SHA-256 `0c45fd5d90681c36e45502c571b3d96daed62adaaa0826132aac3a88966d0d6f`. The exact script asserts this hash, all 11,117 classes, the ratio histogram and both maximizers on a full rerun.

**Witness certificate:** The two maximizers share an exact primal with nonzero x entries (0:1, 2:1/2, 3:1/2, 7:1, 16:1/2, 17:1/2, 18:1/2, 20:1, 22:1, 26:1, 27:1/2), degree duals y_1,...,y_6 = 1/2 (other y=0), and cut duals indexed 89,100,118 equal to 1/2 (others zero). The order of the 28 edges and 119 cuts is defined explicitly in the script. These give matching primal and dual objective 9, independently of HiGHS. The tour with edge indices (0,7,13,20,27,26,22,3) costs 10; a separate DP certifies that no tour is cheaper.

## Reproduce and attack

    python3 scripts/m097_graph8.py --check
    python3 -m unittest discover -s tests -p 'test_m097_graph8.py' -v

Both commands use the Python standard library only. Ten adversarial tests check graph6 padding, graph connectivity, primal tampering, dual tampering, missing cut multipliers, all 2,520 tours, a second tour DP, and the difference between shortest-path metrics and 1–2 truncations. The quick check **does not** certify the complete census.

To replay the full enumeration and all 11,117 exact LP optimality checks:

    # Reference local versions: Python 3.13, networkx 3.6.1,
    # numpy 2.3.5, scipy 1.17.0 (HiGHS)
    python3 scripts/m097_graph8.py --full

This is an optional-dependency research replay, not part of the default CI gate. The full run was split into four consecutive nonoverlapping chunks locally (6,000 + 2,500 + 2,000 + 617 classes), with each case rationally certified and the final ordered stream independently concatenated. A first *discarded* attempt accidentally shadowed a chunk-start index with a clock variable; an inconsistent last-index diagnostic exposed it. All four chunks were rerun after correcting the variable and checking there were exactly 11,117 distinct graph6 strings. The discarded partial counts are not evidence.

**Failure modes and limits:** the 11,117-class coverage depends on the external seven-vertex graph atlas and exact isomorphism implementation; the full-census primal/dual certificates are regenerated on demand rather than individually archived. Both primal and dual checkers use the same edge/cut indexing code, so an independent LP formulation and a second graph generator are required before acceptance. The default tests certify the two extremal instances, **not** that none was missed. This is author/tool replay, not independent mathematical review.

## Primary-source boundary and novelty

- Qian, Schalekamp, Williamson, van Zuylen, [*On the Integrality Gap of the Subtour LP for the 1,2-TSP*](https://arxiv.org/abs/1107.1630), Mathematical Programming 150 (2015), 131–151: reports the 10/9 bound for 1–2 metrics up to twelve cities. The present maximizers have a distance-three pair and are outside that subclass; however this does **not** establish historical novelty of the finite maximum.
- Cook, Hougardy, Petrich, [*Extending Exact Integrality Gap Computations for the Metric TSP*](https://arxiv.org/abs/2603.12995), 2026: exact general metric subtour-polytope extreme-point computations in small dimensions. This is a potentially stronger existing baseline; it must be audited for implicit or explicit coverage of this eight-vertex graph-metric result before any novelty promotion.
- Hougardy, [*On the Integrality Ratio of the Subtour LP for Euclidean TSP*](https://arxiv.org/abs/1402.5904), 2014: explicitly notes the well-known graphic-metric family approaching 4/3, a warning against novelty claims for the theta construction.
- Held and Karp, *The Traveling-Salesman Problem and Minimum Spanning Trees*, Operations Research 18 (1970): original LP background.

**Rejected separate lead:** a proposed M079 three-cycle automorphism balance lemma was found already subsumed by Ganter–Hafner–Poguntke (1987), as cited explicitly in Olson–Sagan, [*On the 1/3–2/3 Conjecture*](https://arxiv.org/abs/1706.04985), Theorem 2.2. It was not presented as new work or assigned an M079 result.

**Next falsifier:** independently enumerate all connected eight-vertex graphs with nauty/geng or another canonical generator; use a separately written LP primal/dual checker and tour DP on every case; challenge the two graph6 maximizers and the hash. Then test the nine-vertex frontier or a non-enumerative diameter-sensitive inequality. No change to `data/solved.json` or O-M097-01 is justified.
