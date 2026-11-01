# Lab campaigns: twenty problems under exact computation

**Date:** 2026-11-01. This dossier covers the campaigns driven by the [exact probe lab](../LAB.md).
Each probe has a search and a separate checker, runs in CI at a small "smoke" size, and can be
rerun at a larger "deep" size with `python3 scripts/lab.py --level deep`.

**What this is not.** Every range verified here lies inside known mathematics. None of these
runs is a new theorem, and none can enter the [Solved archive](../data/solved.json). They give
each problem a working falsifier and certificate format, so a genuinely new case can be
checked as soon as it appears, and so the engines carry over to the next problem.

## Why a lab instead of more one-off scripts

Before the lab, each campaign needed its own hand-built verifier, and three problems had one.
The lab separates **engines** (finite fields, graph and poset censuses, cyclotomic arithmetic,
tensor certificates, symmetry reductions, clique search, primes, exact LP, homomorphism counts,
polynomial algebra, interval arithmetic, L-functions, group characters) from **probes** (about
100 lines that state one finite claim, search, and check independently). Most new probes reuse an
existing engine. For example, the finite-field engine serves five problems: Hadamard, projective
planes, MDS codes, Ramsey colourings and Rota's conjecture.

Every problem also has a `modality` (see [the protocol](../docs/RESEARCH_PROTOCOL.md)) recording
whether finite computation can refute it at all. All 19 problems where it can now have exact
verifiers, so [data/engine_roadmap.json](../data/engine_roadmap.json) is empty; the validator
fails if a computable problem ever loses its verifier without returning to the roadmap.

## Per-problem notes

### M001 — Riemann Hypothesis (`zeta_zeros`, engines `interval_arithmetic`, `l_functions`)
No floating point decides anything. Values are fixed-point intervals with outward rounding, and
exp, log, sin, cos, atan and π come from series with an explicit remainder bound. ζ(s) is
evaluated by Euler–Maclaurin summation with the rigorous remainder |B₂ₘ|/(2M)!·|(s)₂ₘ|·N^(1−σ−2M)/(σ+2M−1),
and θ(t) by Stirling's series after a shift, with the sec^(2m)(arg z/2) remainder bound (DLMF 5.11.ii).
The count is exact: N(T) = θ(T)/π + 1 + S(T) (Backlund), where S(T) is the change of arg ζ along
2 → 2+iT → 1/2+iT. On Re s = 2 we have Re ζ ≥ 2 − π²/6 > 0; the horizontal segment is covered by
boxes, each certified inside an open half-plane, so the winding is determined. Then Z(t) needs
N(T) certified sign changes on (0, T]. Distinct sign changes of the real function Z equal to the
count with multiplicity prove every zero below T is simple and on the line. At every point the
checker also demands that Im(e^(iθ)ζ) contain 0, a live test of the θ enclosure. It repeats the
whole computation at 128 bits with a different truncation and Stirling shift. Smoke: all 29 zeros
below 100. Deep: all 649 zeros below 1000, including the first failures of Gram's law near 282.
**Frontier:** 3·10¹² (Platt & Trudgian 2021). **Next:** Turing's method and Riemann–Siegel.

### M002 — GRH for real characters (`dirichlet_zeros`, engines `interval_arithmetic`, `l_functions`)
For every fundamental discriminant D with |D| ≤ 24, the Kronecker symbol χ_D is a real primitive
character, and the deep run covers all 17 of them. The same engine sums over residue classes mod |D|. For a real
primitive character the count is N(T, χ) = (θ(T, χ) + Δ arg L)/π − N₀/2, where N₀ counts real
zeros in (0, 1). N₀ = 0 is certified on [1/2, 1] by point values and the Lipschitz bound
|L′(σ, χ)| ≤ 2·max|Σ_{n≤x} χ(n)|/(eσ), which follows from partial summation; the functional
equation covers (0, 1/2). The checker rebuilds the character independently: complete
multiplicativity, primitivity, parity, and Euler's criterion at every prime below |D|. It also
certifies the root number +1 from the Gauss sum, which is what makes Z(t, χ) real. Zeros of real
characters are symmetric about the real axis, so the certificate covers |Im s| < T.
**Frontier:** every primitive character of modulus q ≤ 400,000 to height at least 10⁸/q (Platt 2016).
**Next:** complex characters, with exact Gauss sums from the cyclotomic engine.

### M006 — Strong Goldbach (`goldbach`, engine `primes`)
Certifies the least Goldbach prime for every even n up to the run limit. The search side uses a
sieve; the check side uses deterministic Miller–Rabin, or an independent odd-only sieve for large
runs. The deep run reproduces the known record least prime 751 at n = 3,807,404. **Frontier:**
4·10^18 (Oliveira e Silva, Herzog & Pardi 2014). A larger range has no research value; the
useful output is the least-partition table, as data for restricted lemmas.

### M019 — Erdős–Straus (`erdos_straus`, engine `primes`)
Gives an explicit triple for every n, found with a divisor solver for 1/y + 1/z = a/b. The checker
tests only the identity 4xyz = n(xy + yz + zx). **Next:** mine solutions for primes n ≡ 1 (mod 24)
to look for parametric identities.

### M041 — Plane Jacobian conjecture (`jacobian`, engine `polynomial_algebra`)
The class is every map (f, g) of degree ≤ d with zero constant terms and coefficients in a small
set. J(f,g) is linear in g's coefficients, so the maps with constant Jacobian are the lattice points
of an exact kernel. Each one gets an inverse G of degree ≤ d from an exact linear system; by
Gabber's bound, an F with no such inverse would be a counterexample. The checker re-derives the
set of constant-Jacobian maps from a different linear system (evaluations on a grid, with
fraction-free integer elimination), and verifies G∘F = F∘G = id by independent dense composition.
Smoke: all 59,049 maps of degree ≤ 2 (240 with constant Jacobian, matching brute force).
Deep: all 387,420,489 maps of degree ≤ 3 (816). **Frontier:** degree ≤ 100 in the plane (Moh).

### M048 — Alperin's weight conjecture (`alperin_weights`, engine `group_characters`)
Global form: l(G), the number of p-Brauer characters, equals the number of p-regular classes
(Brauer). The probe compares it with w(G), the sum over p-radical subgroups Q up to conjugacy of
the number of p-defect-zero characters of N_G(Q)/Q. The search takes a Sylow subgroup by Cauchy
steps and enumerates all its subgroups. Each G-class is tested for radicality as Q = core of a
Sylow subgroup of N_G(Q), and the character degrees of the quotients come from Dixon's method:
common eigenvectors of the class matrices mod a prime r ≡ 1 (mod exponent) with r > 2√|G|. The
checker is independent at every step. It confirms the p-regular class representatives by
centraliser sizes and pairwise non-conjugacy, and re-enumerates the Sylow subgroup's subgroups
from every generating set of at most log_p|P| elements. It decides radicality by a different
criterion: no N-class of x with x^p ∈ Q generates, together with Q, a larger p-group. It recomputes
every degree list with a different prime and a reversed splitting order. Deep: 46 (group, prime)
cases, including PSL(2,8), PSL(2,11), PSL(2,13), A7, S7 and the sporadic Mathieu group M11.
**Frontier:** p-solvable groups, symmetric groups, GL(n,q) and many simple groups are proved,
with a reduction to simple groups (Navarro–Tiep). **Next:** the blockwise form.

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
