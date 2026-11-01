# Lab campaigns: problems under exact computation

**Date:** 2026-10-31. This dossier covers the campaigns driven by the [exact probe lab](../LAB.md).
Each probe has a search and a separate checker, runs in CI at a small "smoke" size, and can be
rerun at a larger "deep" size with `python3 scripts/lab.py --level deep`.

**What this is not.** Every range verified here lies inside known mathematics. None of these
runs is a new theorem, and none can enter the [Solved archive](../data/solved.json). They give
each problem a working falsifier and certificate format, so a genuinely new case can be
checked as soon as it appears, and so the engines carry over to the next problem.

## Why a lab instead of more one-off scripts

Before the lab, each campaign needed its own hand-built verifier, and three problems had one.
The lab separates **engines** (finite fields, graph and poset censuses, cyclotomic arithmetic,
tensor certificates, symmetry reductions, clique search, primes, interval arithmetic, group
characters) from **probes** (about 100 lines that state one finite claim, search, and check
independently). Most new probes reuse an existing engine. For example, the finite-field engine
serves five problems: Hadamard, projective planes, MDS codes, Ramsey colourings and Rota's
conjecture.

Every problem also has a `modality` (see [the protocol](../docs/RESEARCH_PROTOCOL.md)) recording
whether finite computation can refute it at all. All 19 problems where it can now have exact
verifiers. [data/engine_roadmap.json](../data/engine_roadmap.json) is empty.

## Per-problem notes

### M048 — Alperin weight conjecture (`alperin`, engine `group_characters`)
For each named group G and each prime p dividing |G|, counts p-regular conjugacy classes
(simple FG-modules) and Alperin weights (defect-zero ordinary degrees of N_G(Q)/Q summed over
radical p-subgroup representatives). Character degrees of groups of order ≤ 60 are recovered
from (|G|, class number, |G:G'|), which uniquely determines the degree multiset in this range.
Smoke: nine groups through D10. Deep: adds C5, C6, D12, S4 and A5. **Frontier:** published
computational verification covers every group of order ≤ 100; enlarging the catalog inside that
bound is not a theorem.

### M001 — Riemann hypothesis (`riemann`, engine `interval_arithmetic`)
Certifies N(T) by the argument principle and matches it to sign changes of the Hardy
Z-function. The checker repeats both counts with a different Euler–Maclaurin and Stirling
truncation. Smoke: N(23) = 2. Deep: N(36) = 5. **Frontier:** direct verification already
passes height 3·10^12. This is a certificate format for the low zeros, not a new region.

### M002 — Generalized Riemann hypothesis (`dirichlet_l`, engine `interval_arithmetic`)
The same engine on the real primitive characters modulo 3, 4 and 5, each with root
number +1 checked from its Gauss sum (τ(χ₃)² = −3, τ(χ₅)² = 5). Smoke: N(11) = 2 for
χ₄ and N(9) = 1 for χ₃. Deep: those plus N(17) = 4, N(15) = 2, and N(12) = 3 for the
Legendre symbol modulo 5. **Next:** a complex character, where Lambda is not real.

### M006 — Strong Goldbach (`goldbach`, engine `primes`)
Certifies the least Goldbach prime for every even n up to the run limit. The search side uses a
sieve; the check side uses deterministic Miller–Rabin, or an independent odd-only sieve for large
runs. The deep run reproduces the known record least prime 751 at n = 3,807,404. **Frontier:**
4·10^18 (Oliveira e Silva, Herzog & Pardi 2014). A larger range has no research value; the
useful output is the least-partition table, as data for restricted lemmas.

### M019 — Erdős–Straus (`erdos_straus`, engine `primes`)
Gives an explicit triple for every n, found with a divisor solver for 1/y + 1/z = a/b. The checker
tests only the identity 4xyz = n(xy + yz + zx). The residue mine clusters primes n ≡ 1 (mod 24);
[`research/M019_IDENTITIES.md`](M019_IDENTITIES.md) turns the residue-3/7 clusters into nine
polynomial identities covering 106/117 such primes through 8,000. **Next:** attack the remaining
classes n ≡ 1 or 49 (mod 120) with a non-Mordell idea, without extending the search range.

### M041 — Plane Jacobian conjecture (`jacobian`, engine `polynomial_algebra`)
The class is every map (f, g) of degree ≤ d with zero constant terms and coefficients in a small
set. J(f,g) is linear in g's coefficients, so the maps with constant Jacobian are the lattice points
of an exact kernel. Each one gets an inverse G of degree ≤ d from an exact linear system; by
Gabber's bound, an F with no such inverse would be a counterexample. The checker re-derives the
set of constant-Jacobian maps from a different linear system (evaluations on a grid, with
fraction-free integer elimination), and verifies G∘F = F∘G = id by independent dense composition.
Smoke: all 59,049 maps of degree ≤ 2 (240 with constant Jacobian, matching brute force).
Deep: all 387,420,489 maps of degree ≤ 3 (816). **Frontier:** degree ≤ 100 in the plane (Moh).

### M071 — Hadwiger (`hadwiger`, engine `graph_census`)
Each graph gets a proper t-colouring and a K_t minor model with t branch sets. Since χ ≤ t, and
K_t contains every smaller complete minor, the checker never has to trust a chromatic-number
computation. **Caveat:** every graph on at most 7 vertices falls under the proved t ≤ 6 theorem.

### M073 — Sidorenko (`sidorenko`, engines `graph_homomorphisms`, `graph_census`)
For each bipartite pattern H and every host graph G in the census, the probe compares
t(H,G) with t(K2,G)^e(H) exactly, as hom(H,G)·n^(2e−v) ≥ (2e(G))^e in integers.
Homomorphisms are counted by enumerating one side of H. The checker recounts them from the other
side, and the tests cross-check both against full brute-force enumeration on tiny hosts. The
**proven** controls (C4, C6, K₃,₃, P4) are the reproduced milestone. P4 attains equality on
regular hosts, as theory predicts. The open pattern K_{5,5}∖C₁₀ is recorded on the same hosts
as **exploratory falsifier data only** (minimum ratio ≈ 1.0248 over all 1,252 hosts on ≤ 7
vertices). That is not a result. **Next:** rational step-graphon hosts and exact local search.

### M078 — Graph reconstruction (`reconstruction`, engine `graph_census`)
The census is complete because its size matches Burnside's count and its members are pairwise
non-isomorphic under an independent canonical form. All decks are distinct.
**Frontier:** at least 11 vertices (McKay).

### M079 — 1/3–2/3 (`one_third`, engine `poset_census`)
Posets are generated by adding a new maximal element over an order ideal. Completeness is checked
in two ways: pairwise non-isomorphism, and the identity Σ n!/|Aut P| = A001035(n). Balance
witnesses are recounted with an independent DP over minimal elements. The minimum best balance is
exactly 1/3. **Frontier:** 11 elements (Peczarski).

### M080 — Rota's basis conjecture (`rota`, engines `finite_fields`, `symmetry_reduction`)
B₁ is fixed to the standard basis, which is valid because GL(n,p) is transitive on ordered bases.
The search enumerates every multiset of the remaining bases and stores one byte-coded grid per
instance. The deep run covers all 1,753,128 instances over GF(3)³. **Next:** orbit reduction for
GF(2)⁴.

### M084 — ω = 2 (`strassen`, engine `tensor_certificates`)
Checks Strassen's scheme and its Kronecker powers exactly. `verify_decomposition` replays any
external decomposition, such as one from a flip-graph or learned search, coefficient by
coefficient over ℤ.

### M092 — Zauner / SIC (`sic`, engine `cyclotomic`)
d = 2 uses the Bloch-sphere tetrahedron. In d = 3 the probe finds every Weyl–Heisenberg fiducial
over a small alphabet in ℤ[ω], and checks each one with a separate a + bω implementation.
**Next:** number fields for d ≥ 4.

### M093 — MDS conjecture, k = 3 (`mds_arcs`, engines `finite_fields`, `symmetry_reduction`)
Finds the maximum arc in PG(2,q) by frame-fixed exhaustive search. The checker rebuilds the field
from the certified irreducible modulus. It recounts arcs through the frame and gets q − 2 conics
for odd q, as theory predicts. For q ≤ 4 it brute-forces all subsets with no symmetry assumption.

### M094 — Hadamard (`hadamard`, engine `finite_fields`)
Builds matrices with Sylvester, Paley I/II over every prime-power field, and Kronecker closure.
Orders those miss get Williamson quadruples: four symmetric circulant ±1 matrices with
A² + B² + C² + D² = 4nI, found by meet-in-the-middle on periodic autocorrelations and assembled
with the Williamson array. Order 92 (n = 23, row sums 3, 3, −5, 7) is the historic 1962 case. Each
matrix is checked as H Hᵀ = nI via popcounts, without trusting any construction. The remaining
orders, such as 116 and 156, are **engine gaps**, not open cases.
**Next:** symmetry-reduced Williamson search for n = 29, then Goethals–Seidel arrays.

### M095 — Ramsey witnesses (`ramsey_witnesses`, engines `finite_fields`, `clique_search`)
Certifies classical lower bounds with Paley and circulant colourings. The deep run checks
Paley(37) for R(5,5) > 37, every 5-subset enumerated. This complements the existing
`scripts/ramsey.py` campaign; the best known lower bound is 43.

### M096 — Projective plane of order 12 (`projective_planes`, engine `finite_fields`)
Checks PG(2,q) axioms purely combinatorially from the line lists, and recomputes Bruck–Ryser
exclusions by brute force. Order 10 is recorded as an external computer proof.
12 remains the smallest open order.

### M097 — Metric TSP 4/3 (`held_karp`, engines `exact_lp`, `graph_census`)
For the shortest-path metric of every connected graph in the census, the probe solves the Held–Karp
(subtour) LP exactly. It uses cutting planes over a rational simplex, then finds the optimal tour
by dynamic programming. The checker never trusts the simplex. It re-proves LP optimality from the
duality certificate (primal feasible for **every** subtour constraint, dual feasible, equal
objectives) and recomputes the optimal tour by brute force over all Hamiltonian cycles.
Every graph on up to 6 vertices has gap exactly 1. On 7 vertices the largest gap is 16/15
(OPT 8, HK 15/2, a genuinely fractional optimum). **Frontier:** exact maximum gaps for all metrics
on small n (Benoit–Boyd 2008); 4/3 ≤ gap ≤ 3/2 in general.

## Reproduce

```sh
python3 scripts/lab.py --list
python3 scripts/lab.py --check
python3 scripts/lab.py --level deep --check
python3 scripts/lab.py --probe hadamard --emit /tmp/certs
python3 scripts/lab.py --replay /tmp/certs/hadamard.smoke.json
```
