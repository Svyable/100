# M073 — low-order Ising coefficients detect separating triangles in surface triangulations

**2026-11-02 · Work ID `X-M073-LOW-ORDER-SPECTRUM` · [claim #274](https://github.com/Svyable/100/issues/274).**
**Evidence:** author-derived combinatorial identities, an explicit pair of nine-vertex triangulated spheres, and independently formulated exact algorithms. No independent specialist review or historical-novelty assessment. No result for arbitrary graphons, no claimed counterexample host, and no resolution of Sidorenko's conjecture.

## Precise theorem

Let `T` be a finite **closed simplicial triangulated surface** (connected or not), with `v` vertices, `e` edges, and `f` triangular faces. Every edge is in exactly two distinct faces and every vertex link is a cycle. Let `s(T)` be the number of **nonfacial triangles**: three vertices pairwise adjacent in the one-skeleton that do not constitute a face. Let `H(T)` be the bipartite graph with point vertices and distinct face vertices, and one incidence edge per point in each face. Define

```text
Z_T(q) = sum_{A subset E(H(T)), all vertex degrees in A even} q^|A|
       = 1 + c4 q^4 + c6 q^6 + c8 q^8 + ...
```

**Low-order coefficient theorem (candidate, elementary proof below):**

```text
c4 = e,
c6 = 4f + 8s(T),
c8 = C8(H(T)) + binom(e,2) - 3f.                    (1)
```

Here `C8(H)` is the number of **unoriented simple eight-cycles**, not closed walks. It has an exact one-skeleton formula: sum over all unoriented simple four-cycles `(a,b,c,d)` of `T` of the number of assignments of **four distinct faces** to the edges `ab,bc,cd,da`, choosing each face from the two incident with its edge. Thus the entire displayed polynomial prefix is determined by the triangulation's incidence structure without enumerating its exponentially many even subgraphs.

The first two identities, and the decomposition of the third, hold more generally for finite simple 2-dimensional triangle complexes in which each edge is in exactly two faces; connected vertex links are not needed for those identities. They do **not** hold as written for boundary edges, repeated faces, or arbitrary hypergraphs.

**Sphere corollary.** For a connected triangulated 2-sphere, Euler gives `e=3v-6`, `f=2v-4`, and every nonfacial triangle is a separating 3-cycle. Hence

```text
c6 = 8v - 16 + 8 * (number of separating triangles).
```

For `v>=5`, the one-skeleton is 4-vertex-connected **if and only if** `c6=8v-16`, using the standard separating-triangle characterization of 4-connected plane triangulations. This is a restricted, exactly testable connection between a high-temperature Ising coefficient and graph connectivity, not a new characterization of planar 4-connectivity itself.

## Proof of the coefficients

An even edge set of a simple bipartite graph with exactly four or six edges must be a single simple cycle of that length: all cycles have length at least four, and two cycles need at least eight edges.

A four-cycle of `H(T)` consists of two point vertices and two faces containing both points. Every edge `ab` of `T` belongs to exactly two faces, so it determines exactly one such square; no nonedge can. Thus `c4=e`.

A six-cycle consists of three distinct point vertices `a,b,c` and three **distinct** face vertices assigned in cyclic order to `ab,bc,ca`. The three point edges must form a triangle in the one-skeleton. If `abc` is **not** a face, all `2^3=8` assignments are valid: a face assigned to two of these edges would contain all three points, contrary to nonfaciality. If `abc` **is** a face `F`, each point edge has choices `F` and its distinct opposite face. An assignment repeats a face exactly when it chooses `F` on at least two edges: there are `binom(3,2)+1=4` such assignments, leaving four valid ones. The other three faces cannot coincide because each contains exactly two of `a,b,c` and a third point outside `abc`. There are `f` facial and `s(T)` nonfacial triangles, proving `c6=4f+8s(T)`.

An eight-edge even set is either one simple eight-cycle or a union of two edge-disjoint four-cycles. Each four-cycle corresponds to an edge of `T`. Two such squares share an incidence edge precisely when the corresponding edges of `T` belong to a common triangular face. Every face contains three unordered pairs of its edges, and any pair of distinct edges can belong to at most one common face. Thus the number of edge-disjoint pairs of squares is `binom(e,2)-3f`. Such a pair has a **unique union**: two squares whose incidence-edge sets are disjoint cannot share a face vertex (two edges of one triangle necessarily share an incidence edge if both squares use that face); they may share at most one point vertex, and in either case their two four-cycles are uniquely recovered. They cannot also be an eight-cycle. This proves the last identity in (1). Finally every simple eight-cycle alternates four distinct point vertices with four distinct faces, yielding the stated four-cycle face-assignment formula, with no multiplicity.

## Sharp nine-vertex boundary and explicit same-f-vector falsifier

In a simplicial triangulated sphere with minimum vertex degree **at least four**, a separating triangle has **at least three interior vertices on each side**. Indeed, cap either side with its boundary triangle. With one interior vertex, the capped sphere is a tetrahedron and that interior vertex has degree three. With two interior vertices, the capped sphere is the unique five-vertex maximal planar graph `K5` minus one edge. Its two degree-three vertices are nonadjacent, so the triangular boundary cannot contain both; an interior vertex has degree three. The degree of an interior vertex is unchanged by capping. Both possibilities contradict the minimum-degree hypothesis. Hence `v>=3+3+3=9`.

This bound is attained. Two explicit closed, connected, minimum-degree-four triangulated spheres on **the same nine vertices, 21 edges, and 14 faces** have different spectra:

| Construction | Nonfacial triangles | `c4` | `c6` | `C8(H)` | `c8` |
|---|---:|---:|---:|---:|---:|
| Glue two octahedral spheres along one removed face | 1 | 21 | **64** | 357 | 525 |
| Split the octahedral edges `(0,2)`, `(0,3)`, `(1,2)` successively | 0 | 21 | **56** | 413 | 581 |

For the first, take octahedron faces `{(a,b,c): a in {0,1}, b in {2,3}, c in {4,5}}`. Remove `(0,2,4)` from each of two copies and identify their boundary points; label the three nonboundary vertices of the second copy `6,7,8`. For the second, an edge split replaces the two triangles `(u,v,a),(u,v,b)` by `(u,x,a),(v,x,a),(u,x,b),(v,x,b)` with a new point `x`. The code constructs the complete face lists literally, verifies links, Euler characteristic, connectivity and minimum degree, and counts cycles.

Consequently the stronger proposal **`c6=4f` for every closed triangulation is false**, and even the entire f-vector plus the minimum-degree-four condition does not determine `c6`. This is a counterexample to an auxiliary spectral extrapolation, **not** to Sidorenko's conjecture.

## Exact source-pinned M073 application

The 22-face, 13-point [pinned M073 triangulation](../data/reference/sidorenko_faces.json) has `e=33`, `s(T)=0`, and the new formulas give `c4=33`, `c6=88`, `C8(H)=361`, and `c8=361+binom(33,2)-66=823`. These agree with the independently generated [23-coefficient parity spectrum](M073_INFORMATION_ALIGNMENT.md), but **reproducing those four pinned numbers is not the novel claim**: the contribution is the structural formula for all closed simplicial surfaces and the separating-triangle boundary/falsifier.

For the equal-mass symmetric two-block graphon `W=[[a,b],[b,a]]`, let `p=(a+b)/2>0`, `q=(a-b)/(a+b)`. The classical spin/high-temperature expansion gives exactly

```text
t(H(T),W)/p^(3f) = 1 + e q^4 + (4f+8s(T)) q^6
                   + (C8(H(T))+binom(e,2)-3f) q^8 + ...
```

The series is a **finite polynomial identity**. It is not an inequality for arbitrary block masses or asymmetric diagonal entries. Its coefficients are nonnegative, but it does not by itself resolve Sidorenko's conjecture.

## Reproducibility, independent representations and failures

```sh
python3 scripts/m073_low_order_surface.py
python3 -m unittest discover -s tests -p 'test_m073_low_order_surface.py' -v
python3 scripts/regen.py --check --fast
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

The checker validates edge multiplicities and cyclic vertex links, computes nonfacial triangles and eight-cycles **from the one-skeleton**, and separately counts literal length-four/six/eight cycles by DFS **in the bipartite incidence graph**. Tests additionally use the existing **parity-state face-elimination recurrence** to count even subgraphs without either cycle formula, and apply seeded topology-preserving diagonal flips, relabelings, a nonmanifold wedge, a boundary, a repeated face and a corrupted face. These are three author-controlled exact representations, **not** independent mathematical review. No random sampling is substituted for the proof of the all-orders identities.

Failed stronger avenue: `c6=4f` appears to hold for the octahedron, icosahedron and the 22-face source, but fails on the glued octahedra by exactly eight. A pure f-vector formula therefore cannot capture the sixth-order coefficient. Counting only simple eight-cycles also fails: for the source it would give 361 rather than 823 because the 462 unions of disjoint squares contribute. A naive count of **all** pairs of squares overcounts by `3f`.

**Boundary:** The proof assumes a simplicial complex with distinct faces and exactly two faces per edge; a generic triple system, a surface with boundary, or a graphon with unequal class masses is outside scope. The nine-vertex minimality uses the **sphere** and minimum degree four, not arbitrary closed surfaces. The source-pinned 22-face table does not provide the unknown counterexample host from the September 2026 Sidorenko manuscript.

**Next falsifiers:** challenge the unique decomposition of eight-edge even sets with a face-sharing square pair; enumerate nonorientable closed triangulations and pseudomanifolds; test whether the same `c6` formula appears in earlier incidence-spectrum or simplicial-complex literature; seek an independent specialist proof/scope audit before promoting the result.

## Literature / provenance checked 2026-11-02

- Friedli and Velenik, *Statistical Mechanics of Lattice Systems* (Cambridge, 2017), [DOI 10.1017/9781316882603](https://doi.org/10.1017/9781316882603): the Ising high-temperature even-subgraph identity is classical.
- Jackson and Yu, *Hamilton cycles in plane triangulations* (J. Graph Theory 41, 2002), [DOI 10.1002/jgt.10057](https://doi.org/10.1002/jgt.10057): separating triangles and 4-connected triangulation structure are classical; this paper does **not** establish novelty of the coefficient formula.
- Lo and Qian, *Hamiltonian Cycles in 4-Connected Planar and Projective Planar Triangulations with Few 4-Separators* (SIAM J. Discrete Math. 36, 2022), [DOI 10.1137/21M1419556](https://doi.org/10.1137/21M1419556): modern primary context for 4-connected triangulations.
- [M073_INFORMATION_ALIGNMENT.md](M073_INFORMATION_ALIGNMENT.md) and [M073_EDGE_NEIGHBORHOOD.md](M073_EDGE_NEIGHBORHOOD.md): earlier repository source-pinned spectrum and surface-incidence correlation inequality. Neither is asserted independently accepted.

No targeted search identified this exact `4f+8s(T)` coefficient formula, but absence from the searched sources does **not** establish historical priority. The theorem remains an author-derived restricted candidate pending independent specialist review. No solved, accepted, coverage, benchmark or PR-landing workflow state changes.
