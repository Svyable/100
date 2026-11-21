# November 2026 RH / Dirichlet GRH: verified scope and research impact

**Status as of 2026-11-21:** external formal certification reported; **not reproduced or independently accepted by Project 100**. This is a research intake and dependency audit, not a new proof, solution ledger update, or cryptanalytic breakthrough.

## Primary evidence and exact scope

1. [Lean/Mathlib joint statement (2026-11-21)](https://leanprover-community.github.io/blog/posts/riemann-hypothesis/) certifies the ordinary Riemann Hypothesis theorem in Mathlib and reports independent proof export and kernel checks of Alpöge's 2026-11-20 Lean library.
2. [Andrew Sutherland's MIT verification record](https://math.mit.edu/~drew/grh/) reports compilation of 175,187 modules, axiom audits, and independent checks. Its five exported theorems include ordinary RH and GRH for **Dirichlet L-functions**; the record explicitly says “GRH” here means Dirichlet L-functions only.
3. [Contemporary mathematical outline](https://hexagonmath.org/pdf/2611.00812v1) is an exposition, not an independent formal verification or proof of additional L-function cases.

**Do not conflate:** ordinary RH (Riemann zeta), Dirichlet GRH (all Dirichlet character L-functions), and broader Dedekind/Hecke/Artin/automorphic GRH. No source above certifies the latter families. A formal theorem establishes its encoded statement relative to its trusted foundations; external checks do not constitute Project 100's own replay, semantic review, or independent acceptance. Clay/prize adjudication and wider mathematical assimilation are separate matters.

## Conditional consequence triage (not automatic theorem imports)

| Area | Relevant hypothesis | Concrete follow-up / boundary |
| --- | --- | --- |
| Prime gaps | RH | Audit explicit interval bounds and constants; a bound of order sqrt(x) log x is a numerical interval guarantee, not polynomial time in log x for naive search. |
| Primes in residue classes | Dirichlet GRH | Record effective least-prime bounds with exact coprimality, modulus, logarithmic factors and constants. A q-polynomial search is not necessarily polynomial in bit length log q. |
| Miller primality test | Dirichlet GRH | Audit exact deterministic witness bound and input assumptions. AKS already supplies unconditional deterministic polynomial-time primality testing. |
| Modular square roots | Dirichlet GRH | Verify least quadratic nonresidue and resulting deterministic complexity; distinguish fixed-degree root extraction from unrestricted cases. |
| Finite-field polynomial factoring | Typically GRH-conditioned | Audit specific Evdokimov-type quasipolynomial algorithms, field size and degree parameters; do not claim general deterministic polynomial-time factoring. |
| Totient-to-factoring reduction | GRH-conditioned | Check original reduction and complexity model; not a direct practical factoring attack. |
| Number-field class groups / PARI/GP / Magma | Often Dedekind GRH | **Not discharged** by Dirichlet GRH alone; identify each routine's assumptions. |
| Elliptic-curve isogeny graphs and discrete-log reductions | Often Hecke GRH | **Not discharged** without exact Hecke-family theorem. No new break of ECC follows. |
| Hilbert Nullstellensatz in AM | Stronger number-field prime estimates | **Not discharged** solely by the five checked Dirichlet theorems; audit Koiran's exact hypothesis. |
| Lattice, isogeny and code-based crypto | Scheme-specific, often stronger assumptions | No general quantum attack or BIKE guarantee follows automatically; require theorem-by-theorem dependency tracing. |
| RH-linked Turing machine | RH | Verify the exact 744-state machine and equivalence in the original formal source before promoting any claim. |

## Project 100 actionable work packets

- **GRH-01 (evidence):** pin source revision, archive hashes, toolchain and Mathlib commit; reproduce the five exported statement types and transitive axiom inventory in a clean environment. Treat the 17M-line proof as an *external dependency* until reproducibly checked; avoid importing it into the current small pinned Lean build.
- **GRH-02 (dependency graph):** for each active problem and Next 100 candidate mentioning RH/GRH, record the *exact L-function family* and whether the claimed result is theorem-level, algorithmic, or heuristic. No bulk status changes.
- **GRH-03 (algorithm benchmarks):** implement small deterministic primality and modular-square-root examples with explicit bounds; compare against unconditional baselines, measuring bit complexity and wall time without presenting finite tests as mathematical proofs.
- **GRH-04 (formal transfer):** select one small RH/Dirichlet-GRH corollary with a published theorem statement, formalize its assumptions and a downstream use in a separately pinned dependency environment, then seek independent scope review.
- **GRH-05 (status monitoring):** re-check the joint statement, MIT verification log, corrections and expert expositions; preserve dated snapshots and record any changes to the verified scope.

## Acceptance and safety gates

Do not mark any of the 100 problems solved merely because an external announcement or formal certificate exists. A candidate status change requires exact statement correspondence, primary literature, a reproducible proof/certificate path, and independent review under [the research protocol](RESEARCH_PROTOCOL.md). Separate *external formal certification* from *locally reproduced* and *independently reviewed by Project 100*. No novel mathematical result, performance improvement, or cryptographic exploit is claimed here.

Claim: [#392](https://github.com/Svyable/100/issues/392). Infrastructure work ID: `X-GRH-2026-SCOPE`.

## Direct active-target mapping and hard stop

- **M001 — Riemann Hypothesis:** the verified Mathlib statement corresponds to the active problem's critical-line zeta-zero question. The registry's `official_open` label is dated 2026-10-30; it is now a **stale status needing explicit review**, not evidence of a new open result. Propose `claim_needs_review` after a current-status audit, never `resolved` on this intake alone.
- **M002 — Generalized Riemann Hypothesis:** the active problem explicitly asks about **Dirichlet L-functions**, not all number-field zeta functions. The MIT record's theorem `LFunction_eq_zero_re` (and its primitive variant) appears to match this scope, subject to an independent semantic check. M002's `needs_review` status is also stale.
- Neither M001 nor M002 is to be retired, swapped out of the 100, or inserted into `data/solved.json` by this PR. An external certification is important evidence, but the project requires separate reproducibility, meaning, and independence gates.

## Reproducibility pin (MIT report, as viewed 2026-11-21)

| Asset or environment | Reported value |
| --- | --- |
| Lean | v4.33.1 (commit `819816b2`) |
| Mathlib | v4.33.1 (commit `0df444a3`) |
| Source archive, joined 14 parts | SHA-256 `9631b4f020199e580ba86178cb56c6e9b09f690c2369a80dc4334aa93f49c7fc` |
| Compressed solution export | SHA-256 `61a8938ad5f5e57397c1c0e3b954916af546d9004ade01c3555744a681b05381` |
| Decompressed solution export | SHA-256 `5ea74b912147c5c93cc2b6d70cc727cf908df2f62ac6a20480a3fa02f6be244e` |
| Compressed challenge export | See the MIT [SHA256SUMS](https://math.mit.edu/~drew/grh/SHA256SUMS); compare the full decompressed challenge hash `bd484ac9886a96f26b1d9a7a59ebd45b7a70d102c015d4f31f9302bbdd6ab2b9` |
| Reported axioms | `propext`, `Classical.choice`, `Quot.sound` only |
| Checker coverage | 175,187/175,187 modules replayed via `leanchecker`; nanoda and con-leche accepted independently; MIT logs distinguish completed from in-progress checks |

These are **reported upstream** hashes and results, not local Project 100 hash checks. The machine reading the report must have sufficient memory and disk (MIT estimates ~100 GB RAM / 70 GB disk for the Comparator route); do not insert a mandatory 60+ GB export step into routine PR CI.

## Newly usable arithmetic transfer

The MIT verification also reports an **independent proof composition** with the Robin1984 Lean formalization (commit `acab1a3`), yielding unconditional, kernel-checked statements of Robin's inequality for all integers above 5040 and Lagarias's divisor-sum inequality. This is a stronger practical exemplar for Project 100 than simply recording a headline: it demonstrates a pathway from a newly checked theorem to independent downstream arithmetic definitions. See the [MIT arithmetic consequences section](https://math.mit.edu/~drew/grh/#arithmetic-consequences). Project 100 **has not reconstructed** that bridge.

**Next bounded deliverable:** encode an auditable dependency map (which target or algorithm requires which *L-function family*), then select one small, published corollary as a separately pinned formal transfer. Never infer a general prime-time search guarantee from a numerical bound polynomial in a modulus.
