# Execution queue — evidence-aware research priorities

Program intake: 2026-10-31. **0 independently reviewed full solutions** archived.
These ranks measure *where to deploy proof effort*, not the likelihood of proving a conjecture.
Full shapes and the cohort jobs are in [APPROACH.md](APPROACH.md).

Dispatch score = editorial score + readiness + an action bonus from [data/methods.json](data/methods.json). Readiness counts a campaign brief (+2),
an allowlisted exact verifier (+3), a reproduced **known** benchmark (+2), and an
independently reviewed new restricted result (+3). The action bonus schedules work:
it lifts a claimed finite witness, a missing engine and a published certificate, and
it sinks a range extension the campaign itself says cannot be a theorem. A known
benchmark never counts as a new theorem. The bonus is not evidence.

| Dispatch | ID | Problem | Action | Base | Ready | Bonus | Score | Next step |
|---:|---|---|---|---:|---:|---:|---:|---|
| 1 | M071 | Hadwiger conjecture | `replay_claim_witness` | 85 | +7 | +40 | 132 | Extract a concrete finite graph from the binary-frame construction, or obtain two independent specialist reviews of the existential proof; do not treat comparator or second-kernel replay as a finite witness. |
| 2 | M073 | Sidorenko conjecture | `replay_claim_witness` | 85 | +7 | +40 | 132 | Derive an explicit finite host G (order n and edges) from the counter-kernel parameters and replay t(H,G)<t(K2,G)^66 with two independent homomorphism counts, or obtain specialist acceptance of the existence proof without a listed witness. |
| 3 | M044 | Kaplansky direct-finiteness conjecture | `replay_claim_witness` | 74 | +0 | +40 | 114 | Reproduce a finite presentation and a,b products using a genuinely independent group-ring checker; check the claimed equalities and non-equality. |
| 4 | M049 | Soficity conjecture | `replay_claim_witness` | 74 | +0 | +40 | 114 | Independently verify M044's group algebra witness, then audit the Elek–Szabó implication from soficity to direct finiteness in the claimed coefficient field. |
| 5 | M074 | Caccetta–Häggkvist conjecture | `replay_published` | 94 | +7 | +12 | 113 | Replay the external fixed-r=6 proof corpus on an independent host, verify its published hash and proof traces, and audit the hand-reduction steps before launching duplicate SAT search. |
| 6 | M092 | Zauner SIC conjecture | `replay_published` | 94 | +7 | +12 | 113 | Extend the cyclotomic engine to the number fields needed for d = 4..8 and replay published exact fiducials there. |
| 7 | M093 | Linear MDS code main conjecture | `replay_published` | 91 | +7 | +12 | 110 | Generalise the arc engine to PG(3,q) with 5-point frames and reproduce known maximum arc sizes for q <= 9. |
| 8 | M094 | Hadamard matrix conjecture | `replay_published` | 91 | +7 | +12 | 110 | Add multiplier-group symmetry reduction to the Williamson meet-in-the-middle search so that n = 29 (order 116) becomes feasible, then implement Goethals-Seidel arrays for orders 156 and 172. |
| 9 | M088 | Deterministic polynomial identity testing | `lock_restriction` | 94 | +2 | +10 | 106 | Lock the field, the circuit shape, the degree and the oracle model in one paragraph inside the algebraic-complexity shape. Only then implement a falsifier. A checker with no declared class does not raise readiness. |
| 10 | M075 | Frankl union-closed sets conjecture | `mine_structure` | 91 | +7 | +6 | 104 | The certified mine frankl_orbits quotients the n <= 4 census by ground-set permutations: 4,958 families become 366 orbits at n = 4, and the minimum abundance is exactly 1/2. The next lemma has to generate canonical representatives without enumerating 2^(2^5). |
| 11 | M078 | Graph reconstruction conjecture | `mine_structure` | 91 | +7 | +6 | 104 | The certified mine deck_invariants reads degree sequence and triangle count from decks. Together they separate every graph through 5 vertices and leave 20 excess graphs at 6 vertices. A reconstruction lemma needs a deck invariant strictly stronger than those two. |
| 12 | M079 | One-third–two-thirds conjecture | `mine_structure` | 91 | +7 | +6 | 104 | The certified mine poset_balance finds 11 posets on at most 6 elements with best balance exactly 1/3, and every one of them has width 2, which Linial already settled. A new lemma has to treat width at least 3; this census has no tight example there. |
| 13 | M096 | Projective plane order 12 | `replay_published` | 85 | +7 | +12 | 104 | Encode order-12 planes with a prescribed collineation as SAT with DRAT proof output, starting from cases the literature already excludes. |
| 14 | M084 | Matrix multiplication exponent omega=2 | `replay_published` | 83 | +7 | +12 | 102 | Import one published exact decomposition, such as a cited rank-23 scheme for the <3,3,3> tensor, and replay it on the tensor checker. A flip-graph search is not the next step: small formats cannot beat the laser-method bounds the blocker cites. |
| 15 | M095 | Exact Ramsey number R(5,5) | `replay_published` | 82 | +7 | +12 | 101 | Import and check the published K42 witness; reproduce a small structural exclusion with a trusted proof checker. |
| 16 | M080 | Rota basis conjecture | `mine_structure` | 85 | +7 | +6 | 98 | Quotient instances by the stabiliser of the standard basis so that GF(2)^4 becomes exhaustive, storing one grid certificate per orbit. |
| 17 | M097 | Metric TSP four-thirds conjecture | `mine_structure` | 85 | +7 | +6 | 98 | Extend from graphic metrics to 1-2 and vertex-weighted metrics, and enumerate extreme points of the subtour polytope at n = 8 to search for gap-maximising instances. |
| 18 | M019 | Erdős–Straus conjecture | `mine_structure` | 82 | +7 | +6 | 95 | Nine polynomial identities from the straus_identities mine now cover 106 of the 117 primes n <= 8000 with n = 1 (mod 24), including the primary progressions n = 120t+73 and n = 120t+97. The 11 uncovered primes all lie in {1, 49} (mod 120). Attack those two remaining classes with a non-Mordell idea, or name an explicit family outside the recorded progressions; do not extend the verified search range. |
| 19 | M002 | Generalized Riemann Hypothesis | `replay_published` | 72 | +7 | +12 | 91 | Reproduce a published primitive character modulo 3 or 5 with the correct root number, branch conventions and independently checked zero count; document why this is known mathematics, not GRH progress. |
| 20 | M076 | Erdős–Rado sunflower conjecture | `specify_shape` | 91 | +0 | +0 | 91 | Shape extremal_asymptotics (3 problems, one write-up): Name a structured family and an explicit constant, and compare it with a cited general bound before calling it an improvement. Full shape, certificate and falsifier are in APPROACH.md. |
| 21 | M085 | Unique Games conjecture | `scope_audit` | 83 | +0 | +8 | 91 | Independently audit the reduction's completeness and soundness estimates and its quantitative dependence on gap parameters. |
| 22 | M042 | Dixmier conjecture A1 | `specify_shape` | 89 | +0 | +0 | 89 | Shape polynomial_maps (2 problems, one write-up): Name a polynomial or Weyl family that published degree bounds do not cover, and refuse exhaustive search inside those bounds. Full shape, certificate and falsifier are in APPROACH.md. |
| 23 | M100 | Falconer distance-set conjecture | `scope_audit` | 80 | +0 | +8 | 88 | Audit FalconerAllDimensions.lean definition fidelity, measure conventions and proof dependencies; obtain independent harmonic-analysis review. |
| 24 | M006 | Strong Goldbach conjecture | `mine_structure` | 72 | +7 | +6 | 85 | The certified mine goldbach_growth lists the 12 record least primes through 20,000; the largest is 173 at n = 7426. Test an explicit upper bound against those 12 pairs. Do not extend the range toward the published 4*10^18 verification. |
| 25 | M072 | Erdős–Hajnal conjecture | `specify_shape` | 85 | +0 | +0 | 85 | Shape extremal_asymptotics (3 problems, one write-up): Name a structured family and an explicit constant, and compare it with a cited general bound before calling it an improvement. Full shape, certificate and falsifier are in APPROACH.md. |
| 26 | M077 | Komlós discrepancy conjecture | `specify_shape` | 85 | +0 | +0 | 85 | Shape extremal_asymptotics (3 problems, one write-up): Name a structured family and an explicit constant, and compare it with a cited general bound before calling it an improvement. Full shape, certificate and falsifier are in APPROACH.md. |
| 27 | M082 | NP versus coNP | `specify_shape` | 83 | +0 | +0 | 83 | Shape complexity_barriers (6 problems, one write-up): Name the model and audit any claimed reduction's alphabet, completeness and soundness before writing a new reduction. Full shape, certificate and falsifier are in APPROACH.md. |
| 28 | M083 | Valiant VP versus VNP | `specify_shape` | 83 | +0 | +0 | 83 | Shape algebraic_complexity (4 problems, one write-up): Fix the field and the format, then replay a published certificate or state the class a new hitting set claims to cover. Full shape, certificate and falsifier are in APPROACH.md. |
| 29 | M086 | Quantum PCP conjecture | `specify_shape` | 83 | +0 | +0 | 83 | Shape complexity_barriers (6 problems, one write-up): Name the model and audit any claimed reduction's alphabet, completeness and soundness before writing a new reduction. Full shape, certificate and falsifier are in APPROACH.md. |
| 30 | M087 | P versus BPP | `specify_shape` | 83 | +0 | +0 | 83 | Shape complexity_barriers (6 problems, one write-up): Name the model and audit any claimed reduction's alphabet, completeness and soundness before writing a new reduction. Full shape, certificate and falsifier are in APPROACH.md. |
| 31 | M089 | Strongly polynomial linear programming | `specify_shape` | 83 | +0 | +0 | 83 | Shape algebraic_complexity (4 problems, one write-up): Fix the field and the format, then replay a published certificate or state the class a new hitting set claims to cover. Full shape, certificate and falsifier are in APPROACH.md. |
| 32 | M090 | Graph isomorphism in polynomial time | `specify_shape` | 83 | +0 | +0 | 83 | Shape complexity_barriers (6 problems, one write-up): Name the model and audit any claimed reduction's alphabet, completeness and soundness before writing a new reduction. Full shape, certificate and falsifier are in APPROACH.md. |
| 33 | M014 | Hilbert's tenth problem over Q | `scope_audit` | 72 | +0 | +8 | 80 | Verify the reduction from integer to rational decision tests and audit each cited arithmetic input, especially the October 7 pointwise 2-converse. |
| 34 | M030 | Abundance conjecture | `scope_audit` | 72 | +0 | +8 | 80 | Check the main theorem and dependencies against the canonical klt characteristic-zero formulation, particularly section production and actual basepoint-freeness. |
| 35 | M091 | Yang–Mills existence and mass gap | `specify_shape` | 80 | +0 | +0 | 80 | Shape gauge_theory (1 problems, one write-up): The mass gap is not finitely falsifiable; name the lattice, the gauge group, and which Clay axiom the restriction drops. Full shape, certificate and falsifier are in APPROACH.md. |
| 36 | M098 | Vaught conjecture | `specify_shape` | 80 | +0 | +0 | 80 | Shape logic_decision (2 problems, one write-up): Write the logic in the registry entry, and do not let a manuscript about a different logic move the evidence state. Full shape, certificate and falsifier are in APPROACH.md. |
| 37 | M099 | Decidability of real exponential field | `specify_shape` | 80 | +0 | +0 | 80 | Shape exponential_fields (2 problems, one write-up): Treat Schanuel and the real exponential field as one shape: one explicit tuple or one explicit exponential sentence, certified. Full shape, certificate and falsifier are in APPROACH.md. |
| 38 | M054 | Nonlinear Kerr stability | `scope_audit` | 69 | +0 | +8 | 77 | Compare Hintz v2 and Szeftel hypotheses and companion dependencies, and seek expert adjudication of scattering and asymptotic completeness. |
| 39 | M055 | Higher-dimensional Kakeya conjecture | `scope_audit` | 69 | +0 | +8 | 77 | Check the all-dimensional local smoothing theorem, its Kakeya maximal corollary and exact hypotheses; distinguish 4D direct theorem from universal consequence. |
| 40 | M056 | Fourier restriction conjecture | `scope_audit` | 69 | +0 | +8 | 77 | State M056's exact dimension and p/q exponent range, audit the October 25 local-smoothing-to-restriction implication (including endpoint exclusions), compare the author Lean scope to its paper, and obtain independent harmonic-analysis review. |
| 41 | M060 | Morrey 2x2 conjecture | `scope_audit` | 69 | +0 | +8 | 77 | Compare v3 withdrawal notice with v5, audit the set-valued fixed-point and laminate-to-gradient argument, and request a calculus-of-variations review. |
| 42 | M043 | Kaplansky idempotent conjecture | `specify_shape` | 74 | +0 | +0 | 74 | Shape group_rings (3 problems, one write-up): Take one finitely presented group and one coefficient field, and check a product or an idempotent by an independent multiplication. Full shape, certificate and falsifier are in APPROACH.md. |
| 43 | M045 | Finitistic dimension conjecture | `specify_shape` | 74 | +0 | +0 | 74 | Shape artin_algebras (2 problems, one write-up): Fix one finite-dimensional algebra by a quiver and relations, and recompute its finitistic dimension or the Auslander-Reiten vanishing. Full shape, certificate and falsifier are in APPROACH.md. |
| 44 | M046 | Auslander–Reiten conjecture | `specify_shape` | 74 | +0 | +0 | 74 | Shape artin_algebras (2 problems, one write-up): Fix one finite-dimensional algebra by a quiver and relations, and recompute its finitistic dimension or the Auslander-Reiten vanishing. Full shape, certificate and falsifier are in APPROACH.md. |
| 45 | M047 | Broué abelian defect conjecture | `specify_shape` | 74 | +0 | +0 | 74 | Shape modular_representations (2 problems, one write-up): Take one finite group and one prime, and compare the number of weights with the number of simple modules in a block. Full shape, certificate and falsifier are in APPROACH.md. |
| 46 | M050 | Cherlin–Zilber algebraicity conjecture | `specify_shape` | 74 | +0 | +0 | 74 | Shape homogeneous_structures (1 problems, one write-up): State the language, then check amalgamation for one explicit finite relational structure. Full shape, certificate and falsifier are in APPROACH.md. |
| 47 | M061 | 2D self-avoiding walk exponents | `specify_shape` | 74 | +0 | +0 | 74 | Shape lattice_models (5 problems, one write-up): Name the lattice and the exponent, then certify an exact count or inequality on one finite torus. Full shape, certificate and falsifier are in APPROACH.md. |
| 48 | M062 | Critical percolation no-infinite-cluster conjecture | `specify_shape` | 74 | +0 | +0 | 74 | Shape lattice_models (5 problems, one write-up): Name the lattice and the exponent, then certify an exact count or inequality on one finite torus. Full shape, certificate and falsifier are in APPROACH.md. |
| 49 | M063 | Planar first-passage KPZ exponent | `specify_shape` | 74 | +0 | +0 | 74 | Shape lattice_models (5 problems, one write-up): Name the lattice and the exponent, then certify an exact count or inequality on one finite torus. Full shape, certificate and falsifier are in APPROACH.md. |
| 50 | M064 | FPP limit-shape strict convexity | `specify_shape` | 74 | +0 | +0 | 74 | Shape lattice_models (5 problems, one write-up): Name the lattice and the exponent, then certify an exact count or inequality on one finite torus. Full shape, certificate and falsifier are in APPROACH.md. |
| 51 | M065 | Mandelbrot local-connectivity conjecture | `specify_shape` | 74 | +0 | +0 | 74 | Shape rigidity_dynamics (5 problems, one write-up): Name the map or the billiard, and certify one periodic orbit, one entropy enclosure, or one correlation check. Full shape, certificate and falsifier are in APPROACH.md. |
| 52 | M066 | Birkhoff billiard conjecture | `specify_shape` | 74 | +0 | +0 | 74 | Shape rigidity_dynamics (5 problems, one write-up): Name the map or the billiard, and certify one periodic orbit, one entropy enclosure, or one correlation check. Full shape, certificate and falsifier are in APPROACH.md. |
| 53 | M067 | Sarnak Möbius disjointness conjecture | `specify_shape` | 74 | +0 | +0 | 74 | Shape rigidity_dynamics (5 problems, one write-up): Name the map or the billiard, and certify one periodic orbit, one entropy enclosure, or one correlation check. Full shape, certificate and falsifier are in APPROACH.md. |
| 54 | M068 | Furstenberg times-two times-three conjecture | `specify_shape` | 74 | +0 | +0 | 74 | Shape rigidity_dynamics (5 problems, one write-up): Name the map or the billiard, and certify one periodic orbit, one entropy enclosure, or one correlation check. Full shape, certificate and falsifier are in APPROACH.md. |
| 55 | M069 | Standard map positive metric entropy | `specify_shape` | 74 | +0 | +0 | 74 | Shape rigidity_dynamics (5 problems, one write-up): Name the map or the billiard, and certify one periodic orbit, one entropy enclosure, or one correlation check. Full shape, certificate and falsifier are in APPROACH.md. |
| 56 | M070 | 3D Ising conformal scaling conjecture | `specify_shape` | 74 | +0 | +0 | 74 | Shape lattice_models (5 problems, one write-up): Name the lattice and the exponent, then certify an exact count or inequality on one finite torus. Full shape, certificate and falsifier are in APPROACH.md. |
| 57 | M003 | Birch–Swinnerton-Dyer conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape galois_representations (6 problems, one write-up): Pick one explicit number field or elliptic curve and one finite invariant the conjecture predicts, and compute it two ways. Full shape, certificate and falsifier are in APPROACH.md. |
| 58 | M004 | abc conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape effective_diophantine (4 problems, one write-up): State one explicit identity or inequality on a named class that a cited theorem or computation does not already settle. Full shape, certificate and falsifier are in APPROACH.md. |
| 59 | M005 | Twin prime conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape sieve_infinitude (5 problems, one write-up): Name one modulus, admissible tuple or polynomial that a cited sieve theorem does not already settle, and write the missing estimate. Full shape, certificate and falsifier are in APPROACH.md. |
| 60 | M007 | Bateman–Horn conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape sieve_infinitude (5 problems, one write-up): Name one modulus, admissible tuple or polynomial that a cited sieve theorem does not already settle, and write the missing estimate. Full shape, certificate and falsifier are in APPROACH.md. |
| 61 | M008 | Elliott–Halberstam conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape sieve_infinitude (5 problems, one write-up): Name one modulus, admissible tuple or polynomial that a cited sieve theorem does not already settle, and write the missing estimate. Full shape, certificate and falsifier are in APPROACH.md. |
| 62 | M009 | Montgomery pair-correlation conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape critical_zeros (3 problems, one write-up): Build one interval-arithmetic zero-count certificate and reuse it for every problem in this shape. Full shape, certificate and falsifier are in APPROACH.md. |
| 63 | M010 | Generalized Ramanujan conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape galois_representations (6 problems, one write-up): Pick one explicit number field or elliptic curve and one finite invariant the conjecture predicts, and compute it two ways. Full shape, certificate and falsifier are in APPROACH.md. |
| 64 | M011 | Schanuel's conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape exponential_fields (2 problems, one write-up): Treat Schanuel and the real exponential field as one shape: one explicit tuple or one explicit exponential sentence, certified. Full shape, certificate and falsifier are in APPROACH.md. |
| 65 | M012 | Artin primitive-root conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape sieve_infinitude (5 problems, one write-up): Name one modulus, admissible tuple or polynomial that a cited sieve theorem does not already settle, and write the missing estimate. Full shape, certificate and falsifier are in APPROACH.md. |
| 66 | M013 | Leopoldt's conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape galois_representations (6 problems, one write-up): Pick one explicit number field or elliptic curve and one finite invariant the conjecture predicts, and compute it two ways. Full shape, certificate and falsifier are in APPROACH.md. |
| 67 | M015 | Inverse Galois problem | `specify_shape` | 72 | +0 | +0 | 72 | Shape galois_representations (6 problems, one write-up): Pick one explicit number field or elliptic curve and one finite invariant the conjecture predicts, and compute it two ways. Full shape, certificate and falsifier are in APPROACH.md. |
| 68 | M016 | Fontaine–Mazur conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape galois_representations (6 problems, one write-up): Pick one explicit number field or elliptic curve and one finite invariant the conjecture predicts, and compute it two ways. Full shape, certificate and falsifier are in APPROACH.md. |
| 69 | M017 | Global Langlands functoriality | `specify_shape` | 72 | +0 | +0 | 72 | Shape galois_representations (6 problems, one write-up): Pick one explicit number field or elliptic curve and one finite invariant the conjecture predicts, and compute it two ways. Full shape, certificate and falsifier are in APPROACH.md. |
| 70 | M018 | Infinitely many primes n²+1 | `specify_shape` | 72 | +0 | +0 | 72 | Shape sieve_infinitude (5 problems, one write-up): Name one modulus, admissible tuple or polynomial that a cited sieve theorem does not already settle, and write the missing estimate. Full shape, certificate and falsifier are in APPROACH.md. |
| 71 | M020 | Lehmer's Mahler-measure conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape effective_diophantine (4 problems, one write-up): State one explicit identity or inequality on a named class that a cited theorem or computation does not already settle. Full shape, certificate and falsifier are in APPROACH.md. |
| 72 | M021 | Hodge conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape motivic_cycles (5 problems, one write-up): Fix dimension, codimension and coefficients, then compute one cycle class on one explicit variety in a range a cited source still treats as open. Full shape, certificate and falsifier are in APPROACH.md. |
| 73 | M022 | Generalized Hodge conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape motivic_cycles (5 problems, one write-up): Fix dimension, codimension and coefficients, then compute one cycle class on one explicit variety in a range a cited source still treats as open. Full shape, certificate and falsifier are in APPROACH.md. |
| 74 | M023 | Tate conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape motivic_cycles (5 problems, one write-up): Fix dimension, codimension and coefficients, then compute one cycle class on one explicit variety in a range a cited source still treats as open. Full shape, certificate and falsifier are in APPROACH.md. |
| 75 | M024 | Lefschetz standard conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape motivic_cycles (5 problems, one write-up): Fix dimension, codimension and coefficients, then compute one cycle class on one explicit variety in a range a cited source still treats as open. Full shape, certificate and falsifier are in APPROACH.md. |
| 76 | M025 | Grothendieck section conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape diophantine_geometry (4 problems, one write-up): Fix dimension and the geometric hypothesis, then certify a rational-point or section search up to an explicit height on one variety. Full shape, certificate and falsifier are in APPROACH.md. |
| 77 | M026 | Bombieri–Lang conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape diophantine_geometry (4 problems, one write-up): Fix dimension and the geometric hypothesis, then certify a rational-point or section search up to an explicit height on one variety. Full shape, certificate and falsifier are in APPROACH.md. |
| 78 | M027 | Vojta main conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape diophantine_geometry (4 problems, one write-up): Fix dimension and the geometric hypothesis, then certify a rational-point or section search up to an explicit height on one variety. Full shape, certificate and falsifier are in APPROACH.md. |
| 79 | M028 | Zilber–Pink conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape diophantine_geometry (4 problems, one write-up): Fix dimension and the geometric hypothesis, then certify a rational-point or section search up to an explicit height on one variety. Full shape, certificate and falsifier are in APPROACH.md. |
| 80 | M029 | Mumford–Tate conjecture | `specify_shape` | 72 | +0 | +0 | 72 | Shape motivic_cycles (5 problems, one write-up): Fix dimension, codimension and coefficients, then compute one cycle class on one explicit variety in a range a cited source still treats as open. Full shape, certificate and falsifier are in APPROACH.md. |
| 81 | M037 | Hilbert–Smith conjecture | `scope_audit` | 63 | +0 | +8 | 71 | Compare exact source hypotheses to a specialist formulation and obtain an expert check of the central p-adic action argument. |
| 82 | M038 | Complex structure on S6 | `scope_audit` | 63 | +0 | +8 | 71 | Read Engel's independent proof and its dependency on Alpöge's construction, verify smooth gluing and topological invariants, and solicit further specialist assessment. |
| 83 | M081 | P versus NP | `specify_shape` | 71 | +0 | +0 | 71 | Shape complexity_barriers (6 problems, one write-up): Name the model and audit any claimed reduction's alphabet, completeness and soundness before writing a new reduction. Full shape, certificate and falsifier are in APPROACH.md. |
| 84 | M051 | 3D Euler regularity | `specify_shape` | 69 | +0 | +0 | 69 | Shape pde_regularity (5 problems, one write-up): Write the equation, the dimension and the function space, and certify one symmetric ansatz the literature has already isolated. Full shape, certificate and falsifier are in APPROACH.md. |
| 85 | M052 | Inviscid SQG regularity | `specify_shape` | 69 | +0 | +0 | 69 | Shape pde_regularity (5 problems, one write-up): Write the equation, the dimension and the function space, and certify one symmetric ansatz the literature has already isolated. Full shape, certificate and falsifier are in APPROACH.md. |
| 86 | M053 | Weak cosmic censorship | `specify_shape` | 69 | +0 | +0 | 69 | Shape pde_regularity (5 problems, one write-up): Write the equation, the dimension and the function space, and certify one symmetric ansatz the literature has already isolated. Full shape, certificate and falsifier are in APPROACH.md. |
| 87 | M057 | Bochner–Riesz conjecture | `specify_shape` | 69 | +0 | +0 | 69 | Shape harmonic_analysis (5 problems, one write-up): Fix the dimension and the exponent endpoint before treating a corollary as a settlement of the registered conjecture. Full shape, certificate and falsifier are in APPROACH.md. |
| 88 | M058 | Kannan–Lovász–Simonovits conjecture | `specify_shape` | 69 | +0 | +0 | 69 | Shape harmonic_analysis (5 problems, one write-up): Fix the dimension and the exponent endpoint before treating a corollary as a settlement of the registered conjecture. Full shape, certificate and falsifier are in APPROACH.md. |
| 89 | M059 | Hilbert invariant subspace problem | `specify_shape` | 69 | +0 | +0 | 69 | Shape harmonic_analysis (5 problems, one write-up): Fix the dimension and the exponent endpoint before treating a corollary as a settlement of the registered conjecture. Full shape, certificate and falsifier are in APPROACH.md. |
| 90 | M031 | Smooth 4D Poincaré conjecture | `specify_shape` | 63 | +0 | +0 | 63 | Shape four_manifolds (3 problems, one write-up): Restrict to one homeomorphism type or one unimodular form, and certify either a Kirby diagram or a named obstruction for that form. Full shape, certificate and falsifier are in APPROACH.md. |
| 91 | M032 | Smooth 4D Schoenflies conjecture | `specify_shape` | 63 | +0 | +0 | 63 | Shape four_manifolds (3 problems, one write-up): Restrict to one homeomorphism type or one unimodular form, and certify either a Kirby diagram or a named obstruction for that form. Full shape, certificate and falsifier are in APPROACH.md. |
| 92 | M033 | 11/8 conjecture | `specify_shape` | 63 | +0 | +0 | 63 | Shape four_manifolds (3 problems, one write-up): Restrict to one homeomorphism type or one unimodular form, and certify either a Kirby diagram or a named obstruction for that form. Full shape, certificate and falsifier are in APPROACH.md. |
| 93 | M034 | Borel rigidity conjecture | `specify_shape` | 63 | +0 | +0 | 63 | Shape index_rigidity (4 problems, one write-up): Name the group or the manifold and compute one index or signature identity on one explicit complex of small dimension. Full shape, certificate and falsifier are in APPROACH.md. |
| 94 | M035 | Novikov conjecture | `specify_shape` | 63 | +0 | +0 | 63 | Shape index_rigidity (4 problems, one write-up): Name the group or the manifold and compute one index or signature identity on one explicit complex of small dimension. Full shape, certificate and falsifier are in APPROACH.md. |
| 95 | M036 | Singer conjecture | `specify_shape` | 63 | +0 | +0 | 63 | Shape index_rigidity (4 problems, one write-up): Name the group or the manifold and compute one index or signature identity on one explicit complex of small dimension. Full shape, certificate and falsifier are in APPROACH.md. |
| 96 | M039 | Hopf sign conjecture | `specify_shape` | 63 | +0 | +0 | 63 | Shape index_rigidity (4 problems, one write-up): Name the group or the manifold and compute one index or signature identity on one explicit complex of small dimension. Full shape, certificate and falsifier are in APPROACH.md. |
| 97 | M040 | Higher-dimensional Weinstein conjecture | `specify_shape` | 63 | +0 | +0 | 63 | Shape geometric_topology (3 problems, one write-up): Name the dimension, boundary and smoothness, then compare a manuscript or certify one Reeb orbit on one explicit manifold. Full shape, certificate and falsifier are in APPROACH.md. |
| 98 | M041 | Plane Jacobian conjecture | `stop_range` | 89 | +7 | -36 | 60 | Do not enumerate degree-4 maps with coefficients in {-1,0,1}: Moh (1983) already covers plane maps of degree at most 100. Name one Newton-polygon family outside that degree bound and state the coefficient ring before any search. |
| 99 | M048 | Alperin weight conjecture | `stop_range` | 74 | +7 | -36 | 45 | Do not enlarge the named catalog inside order 100: that range is already covered by the 2007 computational verification. State a restricted family (for example blocks with a named defect-group isomorphism type) and a lemma outside that census. |
| 100 | M001 | Riemann Hypothesis | `stop_range` | 66 | +7 | -36 | 37 | Do not prioritize extending T = 36 inside the already-published critical-line verification range. First identify a mathematically new zero-free region, explicit bound, or verified statement not implied by existing computations. |

## Active proof campaigns

### M071 — Hadwiger conjecture

**Dispatch:** `replay_claim_witness` · rank 1 · The extractability audit found no published finite Hadwiger graph. Extracting one, or obtaining specialist reviews of the existential proof, still outranks another small-n census. Robertson, Seymour and Thomas already cover chromatic number at most 6.

**Proof obligation:** Choose a restricted class beyond the proved t <= 6 range (for example 7-chromatic graphs with small independence number) and state a checkable lemma absent from the literature.

**Falsifier:** A graph with a certified chromatic-number lower bound t and an exhaustive certificate that no K_t minor model exists.

**Recommended step:** Extract a concrete finite graph from the binary-frame construction, or obtain two independent specialist reviews of the existential proof; do not treat comparator or second-kernel replay as a finite witness.

**Not the current recommendation:** Extend the census engine to 8-9 vertices with a faster canonical labeller, then target contraction-critical 7-chromatic graphs where a K7 minor model must be certified.

**Current blocker:** Every graph a naive census reaches is inside the proved t <= 6 range; t = 7 needs much larger graphs and exact chromatic lower-bound certificates.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M073 — Sidorenko conjecture

**Dispatch:** `replay_claim_witness` · rank 2 · The Sidorenko pattern H is now reconstructed here, but the claimed host G is still unpublished. Deriving that host outranks a step-graphon search.

**Proof obligation:** Confirm in current literature that K_{5,5} minus a Hamiltonian cycle is still the smallest open pattern, then fix a restricted host class (vertex-transitive graphs or small rational step graphons) where the inequality can be proved or exhausted.

**Falsifier:** A host graph or rational step graphon W with exactly computed t(H,W) < t(K2,W)^e(H).

**Recommended step:** Derive an explicit finite host G (order n and edges) from the counter-kernel parameters and replay t(H,G)<t(K2,G)^66 with two independent homomorphism counts, or obtain specialist acceptance of the existence proof without a listed witness.

**Not the current recommendation:** Extend hosts from unweighted graphs to rational step graphons and run exact local search that minimises t(H,W)/t(K2,W)^15, replaying every candidate with the exact counter.

**Current blocker:** Any counterexample is expected to need large or finely weighted hosts; unweighted hosts on at most 7 vertices give a minimum ratio of about 1.025 for the open pattern.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M074 — Caccetta–Häggkvist conjecture

**Dispatch:** `replay_published` · rank 5 · The fixed-r=6 corpus is published and hashed, and this repository has not replayed its proof traces.

**Proof obligation:** Independently audit the public computer-assisted fixed-r=6 proof claim, including proof-to-CNF reductions, finite certificates and cited premises; distinguish restricted result from full CH.

**Falsifier:** An explicitly checked digraph with min outdegree r and no directed cycle of length <=ceil(n/r).

**Recommended step:** Replay the external fixed-r=6 proof corpus on an independent host, verify its published hash and proof traces, and audit the hand-reduction steps before launching duplicate SAT search.

**Current blocker:** External fixed-r=6 proof corpus (438 MB) and independent specialist review have not been reproduced in this repo; neither encoding supplies a SAT/UNSAT certificate.

**Stage:** `benchmark_reproduced` · [Dossier](research/M074_PRIOR_ART.md)

### M092 — Zauner SIC conjecture

**Dispatch:** `replay_published` · rank 6 · Exact fiducials for dimensions above 3 are published, and the cyclotomic engine does not yet replay them.

**Proof obligation:** Replay a published exact fiducial beyond d = 3 with exact arithmetic, and state the precise Galois hypotheses of any proposed uniform family.

**Falsifier:** An exact failed Gram matrix relation or a missing required vector under the stated algebraic construction.

**Recommended step:** Extend the cyclotomic engine to the number fields needed for d = 4..8 and replay published exact fiducials there.

**Current blocker:** Exact fiducials beyond d = 3 live in larger number fields than the current Z[zeta_m] engine supports; floating-point SICs are not proofs.

**Stage:** `benchmark_reproduced` · [Dossier](research/CAMPAIGNS.md)

### M093 — Linear MDS code main conjecture

**Dispatch:** `replay_published` · rank 7 · The next experiment reproduces known maximum arcs in PG(3,q). The plane k=3 case is already the proved Segre-Bose range.

**Proof obligation:** Extend from k = 3 (Segre/Bose) to k = 4 arcs in PG(3,q) for small non-prime q (q = 8, 9), certifying maximum arc sizes.

**Falsifier:** An explicit n-arc exceeding the bound, verified by exact determinant checks.

**Recommended step:** Generalise the arc engine to PG(3,q) with 5-point frames and reproduce known maximum arc sizes for q <= 9.

**Current blocker:** The conjecture is proved for prime q (Ball 2012); open non-prime cases need far larger searches than k = 3.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M094 — Hadamard matrix conjecture

**Dispatch:** `replay_published` · rank 8 · Orders 116, 156 and 172 are engine gaps. The literature already constructs them. They are not the open case, which the probe frontier places at order 668.

**Proof obligation:** Close the remaining engine gaps (116, 156, 172, ...) with symmetry-reduced Williamson and Goethals-Seidel constructions, then document the first order no implemented method reaches.

**Falsifier:** A proof that no Hadamard matrix of some order 4k exists; a finite search failure is not sufficient.

**Recommended step:** Add multiplier-group symmetry reduction to the Williamson meet-in-the-middle search so that n = 29 (order 116) becomes feasible, then implement Goethals-Seidel arrays for orders 156 and 172.

**Current blocker:** Plain meet-in-the-middle over symmetric circulants is practical up to n = 23 in pure Python; n = 29 needs symmetry reduction, and order 668 remains the smallest open case.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M088 — Deterministic polynomial identity testing

**Dispatch:** `lock_restriction` · rank 9 · The campaign blocker says no circuit class is locked. A checker written before the class is fixed does not raise readiness.

**Proof obligation:** State field characteristic, circuit shape, degree and oracle model, then prove the exact hitting property.

**Falsifier:** A nonzero circuit in the declared class vanishing at every proposed hitting-set point.

**Recommended step:** Lock the field, the circuit shape, the degree and the oracle model in one paragraph inside the algebraic-complexity shape. Only then implement a falsifier. A checker with no declared class does not raise readiness.

**Not the current recommendation:** Implement small exact arithmetic circuits and a falsifier that searches for circuits escaping a proposed hitting set.

**Current blocker:** No restricted circuit class or field is locked down yet.

**Stage:** `specified` · [Dossier](research/CAMPAIGNS.md)

### M075 — Frankl union-closed sets conjecture

**Dispatch:** `mine_structure` · rank 10 · The frankl_orbits mine has quotiented the n <= 4 census. Naive 2^(2^n) enumeration is still the blocker at n = 5, so the next step is a generator that does not list every family.

**Proof obligation:** Verify the exact conjecture for bounded universes before deriving any universal structural reduction.

**Falsifier:** An exact union-closed family whose maximum element frequency is less than half the family size.

**Recommended step:** The certified mine frankl_orbits quotients the n <= 4 census by ground-set permutations: 4,958 families become 366 orbits at n = 4, and the minimum abundance is exactly 1/2. The next lemma has to generate canonical representatives without enumerating 2^(2^5).

**Current blocker:** Naive exhaustive enumeration scales as 2^(2^n); structural quotient required.

**Stage:** `benchmark_reproduced` · [Dossier](research/M075_FRANKL.md)

### M078 — Graph reconstruction conjecture

**Dispatch:** `mine_structure` · rank 11 · The deck_invariants mine shows degree sequence plus triangle count still leaves collisions at 6 vertices. A larger census sits inside the published computational range.

**Proof obligation:** Pick a graph family not yet known to be reconstructible and isolate a lemma that reconstructs a new invariant for it.

**Falsifier:** Two non-isomorphic graphs with identical decks, confirmed by independent canonical forms.

**Recommended step:** The certified mine deck_invariants reads degree sequence and triangle count from decks. Together they separate every graph through 5 vertices and leave 20 excess graphs at 6 vertices. A reconstruction lemma needs a deck invariant strictly stronger than those two.

**Current blocker:** Computer verification already reaches at least 11 vertices; novelty has to come from a structural lemma, not from range.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M079 — One-third–two-thirds conjecture

**Dispatch:** `mine_structure` · rank 12 · The poset_balance mine shows every tight example on at most 6 elements has width 2, which is Linial's settled case. Published verification already reaches 11 elements.

**Proof obligation:** State and prove a balance bound for a restricted poset class (bounded width or height) that improves on published results.

**Falsifier:** A non-chain poset whose every incomparable pair has balance below 1/3, with linear extensions counted exactly by two independent methods.

**Recommended step:** The certified mine poset_balance finds 11 posets on at most 6 elements with best balance exactly 1/3, and every one of them has width 2, which Linial already settled. A new lemma has to treat width at least 3; this census has no tight example there.

**Current blocker:** Published verification already reaches 11 elements; a new structural invariant is needed.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M096 — Projective plane order 12

**Dispatch:** `replay_published` · rank 13 · The next experiment encodes literature-excluded collineation cases with a proof trace. Unconstrained search of order 12 is the blocker, not the plan.

**Proof obligation:** Reproduce a published partial nonexistence result for order 12 (for example a restriction on collineations) before any search.

**Falsifier:** An explicit order-12 incidence structure passing the combinatorial axiom check would settle existence.

**Recommended step:** Encode order-12 planes with a prescribed collineation as SAT with DRAT proof output, starting from cases the literature already excludes.

**Current blocker:** Unconstrained search is far out of reach; the order-10 nonexistence proof needed a massive computation.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M084 — Matrix multiplication exponent omega=2

**Dispatch:** `replay_published` · rank 14 · Import a published decomposition onto the existing checker. The blocker says a small-format search cannot beat laser-method bounds below 2.372.

**Proof obligation:** Replay published small-format decompositions (rank-23 <3,3,3> and recent flip-graph or learned schemes) as exact certificates and record the implied exponent bounds.

**Falsifier:** Not finitely falsifiable: omega is a limit, and certified decompositions only give upper bounds.

**Recommended step:** Import one published exact decomposition, such as a cited rank-23 scheme for the <3,3,3> tensor, and replay it on the tensor checker. A flip-graph search is not the next step: small formats cannot beat the laser-method bounds the blocker cites.

**Not the current recommendation:** Add a JSON import path and a flip-graph rank-reduction search over small formats, with every candidate replayed by the exact checker.

**Current blocker:** Small-format ranks cannot beat laser-method bounds below 2.372; the probe is certificate infrastructure.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M095 — Exact Ramsey number R(5,5)

**Dispatch:** `replay_published` · rank 15 · The lab certifies R(5,5) greater than 37. The published K42 colouring is the next certificate, and an upper bound needs a proof trace rather than a solver verdict.

**Proof obligation:** Verify a candidate K43 two-coloring or independently certify the nonexistence of a K45 valid coloring.

**Falsifier:** A verified K43 coloring would refute any claimed R(5,5)<=43; a valid K45 coloring would refute R(5,5)<=45.

**Recommended step:** Import and check the published K42 witness; reproduce a small structural exclusion with a trusted proof checker.

**Current blocker:** A SAT solver UNSAT output without a verified proof trace does not establish an upper bound.

**Stage:** `benchmark_reproduced` · [Dossier](research/M095_RAMSEY.md)

### M080 — Rota basis conjecture

**Dispatch:** `mine_structure` · rank 16 · Chan (1995) covers rank at most 3. The next experiment is the orbit quotient that makes the rank-4 case GF(2)^4 exhaustive.

**Proof obligation:** Specify the next finite case not yet covered here (GF(2)^4) with an orbit-reduced instance count and a per-orbit certificate format.

**Falsifier:** n bases of GF(p)^n with an exhaustive certificate that no valid grid exists.

**Recommended step:** Quotient instances by the stabiliser of the standard basis so that GF(2)^4 becomes exhaustive, storing one grid certificate per orbit.

**Current blocker:** GF(2)^4 has about 10^8 raw instances; orbit reduction under the stabiliser is not implemented yet.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M097 — Metric TSP four-thirds conjecture

**Dispatch:** `mine_structure` · rank 17 · Graphic metrics through 7 vertices are a certified reproduction. The next experiment changes the metric class rather than adding vertices inside the published small-n range.

**Proof obligation:** Reproduce published exact maximum integrality gaps for all small metrics (Benoit-Boyd) with LP-duality certificates, then target a structured class such as graphic metrics of subcubic graphs beyond published ranges.

**Falsifier:** A metric instance with an exactly certified Held-Karp value and a brute-force optimal tour longer than 4/3 of it.

**Recommended step:** Extend from graphic metrics to 1-2 and vertex-weighted metrics, and enumerate extreme points of the subtour polytope at n = 8 to search for gap-maximising instances.

**Current blocker:** Exhaustive extreme-point enumeration grows very quickly beyond n = 10; graphic metrics up to 7 vertices reach only a 16/15 gap.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M019 — Erdős–Straus conjecture

**Dispatch:** `mine_structure` · rank 18 · Nine polynomial identities already cover 106 of 117 hard-class primes through 8,000. Extending the verified range stays inside published computations; the missing piece is a non-Mordell idea for the classes 1 and 49 mod 120.

**Proof obligation:** Find a polynomial identity family covering a residue class of primes not covered by the classical Mordell identities, and prove it symbolically.

**Falsifier:** An n together with a proof that no positive-integer triple exists; a finite search failure is not a counterexample.

**Recommended step:** Nine polynomial identities from the straus_identities mine now cover 106 of the 117 primes n <= 8000 with n = 1 (mod 24), including the primary progressions n = 120t+73 and n = 120t+97. The 11 uncovered primes all lie in {1, 49} (mod 120). Attack those two remaining classes with a non-Mordell idea, or name an explicit family outside the recorded progressions; do not extend the verified search range.

**Current blocker:** Classical identities leave quadratic-residue classes uncovered, and known results show identities of the standard polynomial type cannot cover them all; a different idea is needed.

**Stage:** `benchmark_reproduced` · [Dossier](research/M019_IDENTITIES.md)

### M002 — Generalized Riemann Hypothesis

**Dispatch:** `replay_published` · rank 19 · The new engine verifies χ4 only; the generalized Riemann hypothesis concerns all Dirichlet characters. Replaying a separate primitive-character certificate tests the reusable contour and gamma-factor implementation.

**Proof obligation:** Extend the phase to a complex character modulo 5, where the root number is not real and the completed Lambda is no longer real on the critical line.

**Falsifier:** A primitive character and a height T at which the certified argument count exceeds the number of critical-line sign changes.

**Recommended step:** Reproduce a published primitive character modulo 3 or 5 with the correct root number, branch conventions and independently checked zero count; document why this is known mathematics, not GRH progress.

**Not the current recommendation:** Extend the phase to a complex character modulo 5, where the root number is not real and the completed Lambda is no longer real on the critical line.

**Current blocker:** Three real characters at height at most 17 do not constrain complex characters or large conductors.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M006 — Strong Goldbach conjecture

**Dispatch:** `mine_structure` · rank 24 · The goldbach_growth mine already lists the record least primes through 20,000. A longer verified range cannot compete with the published 4*10^18 check.

**Proof obligation:** State a restricted, checkable lemma (for example an explicit bound on the least Goldbach prime in a named residue class or range) that is not already implied by the 4*10^18 verification or by the ternary Goldbach theorem.

**Falsifier:** An even n >= 4 with no prime p <= n/2 such that n - p is prime, confirmed by an independent primality oracle.

**Recommended step:** The certified mine goldbach_growth lists the 12 record least primes through 20,000; the largest is 173 at n = 7426. Test an explicit upper bound against those 12 pairs. Do not extend the range toward the published 4*10^18 verification.

**Current blocker:** Range extension cannot compete with the published 4*10^18 verification; real progress needs a new restricted theorem.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M041 — Plane Jacobian conjecture

**Dispatch:** `stop_range` · rank 98 · Moh (1983) covers plane maps of degree at most 100. Degree-4 search on coefficients in {-1,0,1} sits inside that theorem, so the recorded experiment is refused.

**Proof obligation:** Reproduce the classical low-degree cases (Wang: degree <= 2; Moh: plane degree <= 100) on exhaustive integer classes, then isolate a structured family, such as maps with a prescribed Newton polygon, not covered by known degree bounds.

**Falsifier:** A plane map with exactly verified constant nonzero Jacobian and an exact proof (an infeasible linear system under Gabber's bound) that no inverse of degree <= deg F exists.

**Recommended step:** Do not enumerate degree-4 maps with coefficients in {-1,0,1}: Moh (1983) already covers plane maps of degree at most 100. Name one Newton-polygon family outside that degree bound and state the coefficient ring before any search.

**Not the current recommendation:** Enlarge the class to degree 4 with coefficients in {-1,0,1} using kernel enumeration per monomial support, and record the distribution of inverse degrees and of tame decompositions.

**Current blocker:** Known results already cover plane maps of degree <= 100, so exhaustive small classes cannot reach new territory; novelty needs structural families.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M048 — Alperin weight conjecture

**Dispatch:** `stop_range` · rank 99 · Computational verification already covers every group of order at most 100. Extending the named catalog inside that bound cannot be a new theorem.

**Proof obligation:** State a restricted family of blocks (for example a named defect-group isomorphism type outside the order-100 census) and prove or refute the weight count for that family.

**Falsifier:** A finite group G and prime p for which the independently recomputed weight count differs from the number of p-regular conjugacy classes.

**Recommended step:** Do not enlarge the named catalog inside order 100: that range is already covered by the 2007 computational verification. State a restricted family (for example blocks with a named defect-group isomorphism type) and a lemma outside that census.

**Current blocker:** Every group of order at most 100 is already covered by published computational verification; a larger named catalog inside that bound is not a theorem.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

### M001 — Riemann Hypothesis

**Dispatch:** `stop_range` · rank 100 · The new exact interval verifier reaches T = 36, but published computations cover zeta zeros vastly farther. Increasing a tiny certified height is not a new attack on the Riemann hypothesis.

**Proof obligation:** A finite height is already classical. The next obligation is a zero-free statement with an explicit constant that does not follow from plugging this height into a known explicit formula, or a machine-checked count past the range a hand calculation can audit.

**Falsifier:** A height T at which the certified argument count N(T) strictly exceeds the number of disjoint intervals where Z changes sign.

**Recommended step:** Do not prioritize extending T = 36 inside the already-published critical-line verification range. First identify a mathematically new zero-free region, explicit bound, or verified statement not implied by existing computations.

**Not the current recommendation:** Raise the certified height by tightening the contour enclosures, then compare the isolating intervals against a published zero table entry by entry.

**Current blocker:** T = 36 is far below Platt–Trudgian (at least 3*10^12). Extending the height needs a faster contour, not a new idea about the hypothesis.

**Stage:** `benchmark_reproduced` · [Dossier](research/LAB_CAMPAIGNS.md)

## What counts as solved?

Only an independently confirmed *full* proof or counterexample with exact theorem scope,
two distinct independent reviews, dated acceptance, and a replacement active candidate
can enter [data/solved.json](data/solved.json). Existing known small-case reproductions
remain research milestones, never Solved entries.
