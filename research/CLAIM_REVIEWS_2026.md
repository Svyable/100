# 2026 claimed-resolution triage — issue #3

**Screened:** 2026-10-31. **Inventory:** 15 flagged IDs. **Independently accepted full resolutions:** 0.

**Purpose.** Locate the actual source theorem, test whether its quantifiers match the 100-problem registry, and record verification gaps *before* assigning scarce proof-campaign resources. This is a **bibliographic/scope audit**, not a proof audit. A manuscript, an arXiv posting, a self-reported Lean result, an independent toolchain rebuild, a second proof claim, and accepted independent mathematical validation are different kinds of evidence.

The structured source of truth for this table is [`data/claim_reviews_2026.json`](../data/claim_reviews_2026.json). The active `data/problems.json` statuses are intentionally not upgraded and `data/solved.json` stays untouched. `resolved` requires a full scope match, accepted proof/counterexample, two distinct independent external reviews and a replacement candidate (see [research engine](../docs/RESEARCH_ENGINE.md)).

## Decision map

| ID | Primary source | Scope screening | Independent acceptance | Action |
|---|---|---|---|---|
| M014 | [Hilbert's tenth problem over the rational numbers](https://github.com/openai/math/blob/main/preprints/Hilberts-tenth-problem-over-the-rational-numbers-October-6-2026/main.pdf) | Claim would resolve the registered statement if correct | Not established | Verify the reduction from integer to rational decision tests and audit each cited arithmetic input, especially the October 7 pointwise 2-converse. |
| M030 | [Log abundance in characteristic zero](https://github.com/openai/math/blob/main/preprints/Log-abundance-in-characteristic-zero-September-24-2026/paper.pdf) | Potential full claim; verify stated domain and hypotheses | Not established | Check the main theorem and dependencies against the canonical klt characteristic-zero formulation, particularly section production and actual basepoint-freeness. |
| M037 | [The Hilbert–Smith conjecture in every finite dimension](https://github.com/openai/math/blob/main/preprints/The-Hilbert-Smith-conjecture-in-every-finite-dimension-September-23-2026/paper.pdf) | Potential full claim; verify stated domain and hypotheses | Not established | Compare exact source hypotheses to a specialist formulation and obtain an expert check of the central p-adic action argument. |
| M038 | [The (3,4,∞) modular-family construction of a complex structure on S6](https://alpo.ge/s6.pdf) | Claim would resolve the registered statement if correct | Independent reconstruction preprint; no accepted review | Read Engel's independent proof and its dependency on Alpöge's construction, verify smooth gluing and topological invariants, and solicit further specialist assessment. |
| M044 | [A torsion-free group algebra that is not directly finite](https://github.com/openai/math/blob/main/preprints/A-Torsion-Free-Group-Algebra-That-Is-Not-Directly-Finite-October-4-2026/direct-finiteness.pdf) | Claim would resolve the registered statement if correct | Not established | Reproduce a finite presentation and a,b products using a genuinely independent group-ring checker; check the claimed equalities and non-equality. |
| M049 | [A torsion-free group algebra that is not directly finite](https://github.com/openai/math/blob/main/preprints/A-Torsion-Free-Group-Algebra-That-Is-Not-Directly-Finite-October-4-2026/direct-finiteness.pdf) | Claim would resolve the registered statement if correct | Not established | Independently verify M044's group algebra witness, then audit the Elek–Szabó implication from soficity to direct finiteness in the claimed coefficient field. |
| M054 | [Nonlinear stability of subextremal Kerr black holes](https://arxiv.org/abs/2606.28253) | Potential full claim; verify stated domain and hypotheses | Two separate full-range claims; no acceptance | Compare Hintz v2 and Szeftel hypotheses and companion dependencies, and seek expert adjudication of scattering and asymptotic completeness. |
| M055 | [Local smoothing for the Euclidean wave equation](https://github.com/openai/math/blob/main/preprints/Local-smoothing-for-the-Euclidean-wave-equation-October-25-2026/paper.pdf) | Universal claim only if cited consequence is valid | Not established | Check the all-dimensional local smoothing theorem, its Kakeya maximal corollary and exact hypotheses; distinguish 4D direct theorem from universal consequence. |
| M056 | [Diagonal Fourier extension for positively curved surfaces in three dimensions](https://github.com/openai/math/blob/main/preprints/Diagonal-Fourier-extension-for-positively-curved-surfaces-in-three-dimensions-September-24-2026/Diagonal-Fourier-extension-for-positively-curved-surfaces-in-three-dimensions-September-24-2026.pdf) | Restricted/interior statement, not full resolution | Not established | First rewrite M056 as a quantified restriction statement; then check each claimed interior estimate and list remaining endpoints and dimensions. |
| M060 | [Morrey's conjecture: rank-one convexity implies quasi-convexity for two-dimensional, two-component maps](https://arxiv.org/abs/1905.06571) | Potential full claim; verify stated domain and hypotheses | Not established | Compare v3 withdrawal notice with v5, audit the set-valued fixed-point and laminate-to-gradient argument, and request a calculus-of-variations review. |
| M071 | [A counterexample to Hadwiger's conjecture](https://github.com/openai/math/blob/main/preprints/A-counterexample-to-Hadwigers-conjecture-September-23-2026/paper.pdf) | Claim would resolve the registered statement if correct | Formal artifact/check only | Audit the Lean quantifiers and graph encoding against the theorem; reproduce or extract an explicit graph plus an independently checkable minor-bound obstruction. |
| M073 | [A counterexample to Sidorenko's conjecture](https://github.com/openai/math/blob/main/preprints/A-counterexample-to-Sidorenkos-conjecture-September-23-2026/paper.pdf) | Claim would resolve the registered statement if correct | Formal artifact/check only | Check H and the host-existence construction against Lean and paper; independently compute exact graphon/homomorphism inequalities or generate an explicit finite G. |
| M085 | [The Unique Games Theorem](https://github.com/openai/math/blob/main/preprints/The-Unique-Games-Theorem-September-23-2026/paper.pdf) | Claim would resolve the registered statement if correct | Not established | Independently audit the reduction's completeness and soundness estimates and its quantitative dependence on gap parameters. |
| M098 | [A counterexample to Vaught's Conjecture for L_{omega_1,omega}](https://arxiv.org/abs/2610.15217) | Different problem; not a resolution of this ID | Lean proves other logic; not M098 | De-scope the 2026 infinitary result from M098's resolution watch; retain the first-order problem and cite a current specialist open-status source before changing evidence state. |
| M100 | [The Falconer distance conjecture in all dimensions](https://github.com/openai/math/blob/main/preprints/The-Falconer-distance-conjecture-in-all-dimensions-September-23-2026/paper.pdf) | Claim would resolve the registered statement if correct | Formal artifact/check only | Audit FalconerAllDimensions.lean definition fidelity, measure conventions and proof dependencies; obtain independent harmonic-analysis review. |

## Per-claim primary statements, caveats and external evidence

### M014 — Hilbert's tenth problem over the rational numbers

- **Primary source (dated 2026-10-06):** [original manuscript](https://github.com/openai/math/blob/main/preprints/Hilberts-tenth-problem-over-the-rational-numbers-October-6-2026/main.pdf).
- **Claim, not a certified theorem:** No algorithm decides whether an arbitrary integer-coefficient polynomial, with the number of variables part of the input, has a rational zero.
- **Scope:** This is the same rational-field decision problem, not the already-settled integer version or undecidability for proper subrings of Q.
- **Verification status:** `not_established`. Unrefereed manuscript; proof depends on companion pointwise elliptic 2-converse, valuation and height arguments. No independent line-by-line verification located.
- **Next audit:** Verify the reduction from integer to rational decision tests and audit each cited arithmetic input, especially the October 7 pointwise 2-converse.

### M030 — Log abundance in characteristic zero

- **Primary source (dated 2026-09-24):** [original manuscript](https://github.com/openai/math/blob/main/preprints/Log-abundance-in-characteristic-zero-September-24-2026/paper.pdf).
- **Claim, not a certified theorem:** For projective log-canonical pairs with effective rational boundary over an algebraically closed field of characteristic zero, a nef Q-Cartier K_X+B is semiample, in every dimension.
- **Scope:** Would imply the registered projective klt rational-boundary conjecture in characteristic zero. Do not substitute the October 3 numerical-semiampleness claim, which only yields numerical equivalence to a semiample divisor.
- **Verification status:** `not_established`. Unrefereed and depends on sophisticated Iitaka/vanishing inputs; exact coefficient, characteristic and linear-versus-numerical semiampleness hypotheses need verification.
- **Next audit:** Check the main theorem and dependencies against the canonical klt characteristic-zero formulation, particularly section production and actual basepoint-freeness.

### M037 — The Hilbert–Smith conjecture in every finite dimension

- **Primary source (dated 2026-09-23):** [original manuscript](https://github.com/openai/math/blob/main/preprints/The-Hilbert-Smith-conjecture-in-every-finite-dimension-September-23-2026/paper.pdf).
- **Claim, not a certified theorem:** Every locally compact second-countable Hausdorff group acting faithfully and jointly continuously on a connected, second-countable, Hausdorff finite-dimensional topological manifold without boundary is Lie.
- **Scope:** Very close to the classical manifold formulation, but connectedness, boundary, second-countability and joint continuity are explicit. Check equivalence to the intended M037 scope.
- **Verification status:** `not_established`. No independently accepted proof found; must scrutinize reduction to p-adic group actions and high-dimensional hypotheses, not just announced theorem wording.
- **Next audit:** Compare exact source hypotheses to a specialist formulation and obtain an expert check of the central p-adic action argument.

### M038 — The (3,4,∞) modular-family construction of a complex structure on S6

- **Primary source (dated 2026-08-24):** [original manuscript](https://alpo.ge/s6.pdf).
- **Claim, not a certified theorem:** A compact complex threefold constructed from a family of complex two-tori and three special fibers is diffeomorphic to the standard smooth six-sphere.
- **Scope:** If the gluing, complex smoothness and identification with the standard S6 all hold, this is a full positive answer to the registry's integrable-complex-structure question.
- **Verification status:** `independent_reconstruction_preprint`. Philip Engel's September 29 independent 25-page self-contained proof is substantive corroborating research, not a recorded refereed acceptance or two independent specialist reviews. Reconcile claimed geometry with Campana–Demailly–Peternell constraints.
- **Other evidence (not a qualifying acceptance):** [1](https://arxiv.org/abs/2609.38442).
- **Next audit:** Read Engel's independent proof and its dependency on Alpöge's construction, verify smooth gluing and topological invariants, and solicit further specialist assessment.

### M044 — A torsion-free group algebra that is not directly finite

- **Primary source (dated 2026-10-04):** [original manuscript](https://github.com/openai/math/blob/main/preprints/A-Torsion-Free-Group-Algebra-That-Is-Not-Directly-Finite-October-4-2026/direct-finiteness.pdf).
- **Claim, not a certified theorem:** For a finitely presented torsion-free group G, there exist a,b in F_2[G] with ab=1 but ba != 1.
- **Scope:** One valid characteristic-two example would refute the universal direct-finiteness claim; no result for every field is needed for a counterexample.
- **Verification status:** `not_established`. The construction is large and has not been independently reproduced in this audit; underlying group presentation and algebra calculations are central proof obligations.
- **Next audit:** Reproduce a finite presentation and a,b products using a genuinely independent group-ring checker; check the claimed equalities and non-equality.

### M049 — A torsion-free group algebra that is not directly finite

- **Primary source (dated 2026-10-04):** [original manuscript](https://github.com/openai/math/blob/main/preprints/A-Torsion-Free-Group-Algebra-That-Is-Not-Directly-Finite-October-4-2026/direct-finiteness.pdf).
- **Claim, not a certified theorem:** The constructed finitely presented torsion-free group is nonsofic; its group ring over F_2 is not directly finite.
- **Scope:** A finitely presented nonsofic group is countable and refutes the universal soficity conjecture. The claimed nonsoficity may follow from the direct-finiteness obstruction, but is not an independently checked example.
- **Verification status:** `not_established`. Shares one manuscript and underlying construction with M044; do not count these as two independent proof sources. Soxicity inference depends on correct direct-finiteness obstruction and the sofic-group finiteness theorem.
- **Next audit:** Independently verify M044's group algebra witness, then audit the Elek–Szabó implication from soficity to direct finiteness in the claimed coefficient field.

### M054 — Nonlinear stability of subextremal Kerr black holes

- **Primary source (dated 2026-06-26):** [original manuscript](https://arxiv.org/abs/2606.28253).
- **Claim, not a certified theorem:** Vacuum evolutions from sufficiently small asymptotically flat perturbations in a specified polyhomogeneous/weighted-decay class of any fixed subextremal Kerr solution settle to another Kerr solution.
- **Scope:** Covers |a|<M for the stated initial-data classes, not literally every 'admissible' perturbation without quantified decay or gauge assumptions.
- **Verification status:** `separate_claim_not_verification`. Jérémie Szeftel also claims full subextremal stability in a separate September 30 manuscript, with its own companion estimates. Two claims are not the same as independent acceptance of either proof; compare data classes.
- **Other evidence (not a qualifying acceptance):** [1](https://arxiv.org/abs/2609.40068).
- **Next audit:** Compare Hintz v2 and Szeftel hypotheses and companion dependencies, and seek expert adjudication of scattering and asymptotic completeness.

### M055 — Local smoothing for the Euclidean wave equation

- **Primary source (dated 2026-10-25):** [original manuscript](https://github.com/openai/math/blob/main/preprints/Local-smoothing-for-the-Euclidean-wave-equation-October-25-2026/paper.pdf).
- **Claim, not a certified theorem:** Sharp local smoothing for Euclidean waves in every spatial dimension n>=2 is claimed, with the Kakeya maximal conjectures and full Hausdorff dimension for all Euclidean Kakeya sets as consequences.
- **Scope:** The separate September 24 manuscript explicitly claims the 4D Hausdorff case only; M055 concerns all n>=4, so the October 25 local-smoothing-to-Kakeya corollary is essential.
- **Verification status:** `not_established`. A full-dimensional Kakeya consequence must be proved for each n>=4; the 4D paper alone does not settle the registered universal statement.
- **Next audit:** Check the all-dimensional local smoothing theorem, its Kakeya maximal corollary and exact hypotheses; distinguish 4D direct theorem from universal consequence.

### M056 — Diagonal Fourier extension for positively curved surfaces in three dimensions

- **Primary source (dated 2026-09-24):** [original manuscript](https://github.com/openai/math/blob/main/preprints/Diagonal-Fourier-extension-for-positively-curved-surfaces-in-three-dimensions-September-24-2026/Diagonal-Fourier-extension-for-positively-curved-surfaces-in-three-dimensions-September-24-2026.pdf).
- **Claim, not a certified theorem:** For compact positively curved smooth surfaces Sigma in R^3, extension L^p(Sigma) -> L^p(R^3) is bounded for p>3.
- **Scope:** A diagonal three-dimensional theorem is not automatically the full sharp restriction conjecture. The October 25 local-smoothing manuscript separately claims the interior range for sphere/paraboloid/cone, not endpoints.
- **Verification status:** `not_established`. The registry's 'predicted sharp range' is underspecified (dimension, exponents, endpoints and surface). Cannot mark universally resolved from interior/diagonal results.
- **Next audit:** First rewrite M056 as a quantified restriction statement; then check each claimed interior estimate and list remaining endpoints and dimensions.

### M060 — Morrey's conjecture: rank-one convexity implies quasi-convexity for two-dimensional, two-component maps

- **Primary source (dated 2026-06-18):** [original manuscript](https://arxiv.org/abs/1905.06571).
- **Claim, not a certified theorem:** For two-dimensional, two-component maps, finite-valued rank-one convex energies are claimed to be quasiconvex via a fixed-point/lamination argument.
- **Scope:** The 2x2 setting matches M060, subject to the source theorem's function-domain and regularity assumptions.
- **Verification status:** `not_established`. This is arXiv v5 revised in June 2026, not a new 2026 submission. v3 was withdrawn in 2024, and the revised fixed-point/lamination step needs specialist independent reconstruction.
- **Next audit:** Compare v3 withdrawal notice with v5, audit the set-valued fixed-point and laminate-to-gradient argument, and request a calculus-of-variations review.

### M071 — A counterexample to Hadwiger's conjecture

- **Primary source (dated 2026-09-23):** [original manuscript](https://github.com/openai/math/blob/main/preprints/A-counterexample-to-Hadwigers-conjecture-September-23-2026/paper.pdf).
- **Claim, not a certified theorem:** Arbitrarily large finite simple graphs have fractional chromatic number chi_f(G) > h(G), where h is largest clique-minor order.
- **Scope:** Since chi(G)>=chi_f(G), such a graph would refute chi(G)<=h(G), the registered Hadwiger statement.
- **Verification status:** `formal_statement_check_only`. Comparator acceptance of some Lean artifact is proof-object checking, not independent verification of exactly the paper's graph construction and claimed theorem; explicit checkable witnesses were not supplied in the independent audit consulted.
- **Other evidence (not a qualifying acceptance):** [1](https://mathcommunity.github.io/oai-math-revised/papers/A-counterexample-to-Hadwigers-conjecture-September-23-2026/).
- **Next audit:** Audit the Lean quantifiers and graph encoding against the theorem; reproduce or extract an explicit graph plus an independently checkable minor-bound obstruction.

### M073 — A counterexample to Sidorenko's conjecture

- **Primary source (dated 2026-09-23):** [original manuscript](https://github.com/openai/math/blob/main/preprints/A-counterexample-to-Sidorenkos-conjecture-September-23-2026/paper.pdf).
- **Claim, not a certified theorem:** A connected bipartite H on 35 vertices with 66 edges and a finite host G satisfy t(H,G)<t(K_2,G)^66.
- **Scope:** The strict homomorphism-density violation is a direct counterexample to the registered universal Sidorenko inequality.
- **Verification status:** `formal_statement_check_only`. OpenAI's Lean scope note covers the Sidorenko counterexample but not the forcing-conjecture consequence; kernel acceptance is not a published independently audited finite witness. The host G is proved to exist rather than explicitly listed.
- **Other evidence (not a qualifying acceptance):** [1](https://github.com/openai/math/blob/main/lean/docs/161.md).
- **Next audit:** Check H and the host-existence construction against Lean and paper; independently compute exact graphon/homomorphism inequalities or generate an explicit finite G.

### M085 — The Unique Games Theorem

- **Primary source (dated 2026-09-23):** [original manuscript](https://github.com/openai/math/blob/main/preprints/The-Unique-Games-Theorem-September-23-2026/paper.pdf).
- **Claim, not a certified theorem:** For any fixed epsilon,delta in (0,1/2), a polynomial-time reduction from 3SAT to Unique Games over a fixed finite alphabet has completeness at least 1-epsilon and soundness at most delta.
- **Scope:** A uniform, valid hardness reduction with those quantifiers would resolve the registered Unique Games conjecture as normally formulated.
- **Verification status:** `not_established`. Unrefereed preprint; inspect alphabet dependence on epsilon,delta, polynomial bounds, and soundness reductions. Consequent Max-Cut hardness claims do not independently validate UGC.
- **Next audit:** Independently audit the reduction's completeness and soundness estimates and its quantitative dependence on gap parameters.

### M098 — A counterexample to Vaught's Conjecture for L_{omega_1,omega}

- **Primary source (dated 2026-10-10):** [original manuscript](https://arxiv.org/abs/2610.15217).
- **Claim, not a certified theorem:** A sentence of infinitary L_{omega_1,omega} has exactly aleph_1 countable models (and no perfect set of non-isomorphic models).
- **Scope:** M098 asks about complete first-order theories in a countable language, not infinitary L_{omega_1,omega} sentences. This manuscript does NOT refute or solve M098.
- **Verification status:** `formalized_different_statement`. The authors' repository explicitly says the formalization does not solve the first-order Vaught conjecture; a specialist MathOverflow discussion confirms the first-order version remains open.
- **Other evidence (not a qualifying acceptance):** [1](https://github.com/cameronfreer/vaught-conjecture-counterexample), [2](https://mathoverflow.net/questions/22142/has-vaughts-conjecture-been-solved/516156).
- **Next audit:** De-scope the 2026 infinitary result from M098's resolution watch; retain the first-order problem and cite a current specialist open-status source before changing evidence state.

### M100 — The Falconer distance conjecture in all dimensions

- **Primary source (dated 2026-09-23):** [original manuscript](https://github.com/openai/math/blob/main/preprints/The-Falconer-distance-conjecture-in-all-dimensions-September-23-2026/paper.pdf).
- **Claim, not a certified theorem:** For every integer d>=2 and compact E subset R^d with Hausdorff dimension greater than d/2, the Euclidean distance set Delta(E) has positive one-dimensional Lebesgue measure.
- **Scope:** The strict threshold and positive-measure conclusion match the registered Falconer formulation; no endpoint equality or pinned-distance result is claimed.
- **Verification status:** `formal_statement_check_only`. The repository describes Lean theorem scope, but a stated source/Lean match has not been established by two independent specialist proof audits.
- **Other evidence (not a qualifying acceptance):** [1](https://github.com/openai/math/blob/main/lean/docs/073.md).
- **Next audit:** Audit FalconerAllDimensions.lean definition fidelity, measure conventions and proof dependencies; obtain independent harmonic-analysis review.

## Explicit unresolved gates

1. **Primary text collected, proof not independently checked.** Links above point to original authors' manuscripts (including upstream OpenAI mathematical papers); their abstracts and theorem claims are not a substitute for source-proof review.
2. **Do not promote M098.** Its October 2026 infinitary-logic counterexample is not about a complete first-order countable-language theory. An appropriate next registry correction is `verified_open`, *only after* a dated specialist first-order status citation is recorded.
3. **Treat M038 differently from a one-author announcement.** Engel's [self-contained September 2026 reconstruction](https://arxiv.org/abs/2609.38442) is new independent mathematical evidence. Check the two constructions and the relevant complex-geometric restrictions before declaring a resolution.
4. **Separate partial from universal:** M056's three-dimensional diagonal extension is narrower than the overall Fourier restriction question; M055's four-dimensional Kakeya result alone does not settle all `n>=4`; M030's *numerical equivalence* theorem cannot be confused with *semiampleness* of the original divisor.
5. **Avoid double counting:** M044 and M049 depend on the same group-ring construction. Hintz and Szeftel's independent Kerr **proof claims** do not constitute peer acceptance of one another.
6. **Formalization caveat:** Community Lean comparator/kernel checks on some OpenAI results test proof objects for encoded propositions. A mathematically complete review must also audit definitions, hypotheses, imported axioms and correspondence to the ordinary conjecture. Use [OpenAI's release methodology](https://openai.com/index/sharing-ai-progress-in-mathematics/) and the [community notes](https://mathcommunity.github.io/oai-math-revised/) as context, not endorsement.

## Acceptance checklist for any future promotion

- [x] Source manuscript and claimed statement recorded for all 15 IDs; a narrower or different theorem is explicitly flagged.
- [x] Independent evidence or its absence is recorded without silently treating machine checks as accepted mathematics.
- [ ] Specialist review of every proof and exact hypothesized scope (with archived critiques or corrections).
- [ ] Two distinct independent external reviews accepting any proposed **full** resolution.
- [ ] Only then: update registry/solved archive, replace the slot, regenerate dashboards and pass CI.

**Screening date:** 2026-10-31. Status can change with new independent mathematical reviews or source revisions; update the record and preserve dated provenance.
