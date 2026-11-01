# 100 — A living portfolio of mathematical grand challenges

**Purpose:** Preserve, refine, and stack-rank 100 concrete mathematical proof/counterexample targets, looking for results and methods that create new branches of discovery.

- **[M073 ordered two-block quantitative bound](research/M073_MONOTONE_TWO_BLOCK.md)** — an unequal-mass, unequal-diagonal continuous-parameter inequality on the ordered matrix cone, supported by a certified partition of 66 edges into 33 wedges and Harris association; independent novelty/review pending.
- **[M073 quantitative regular-two-block theorem](research/M073_REGULAR2_CYCLE_MARGIN.md)** — a self-contained continuous-parameter inequality with an explicit \(33r^4+88r^6\) margin for the 35-vertex Sidorenko pattern, using a classical even-subgraph expansion and independently counted short cycles; novelty and independent review remain open.
- **[Sidorenko exact two-block negative check](research/M073_TWOBLOCK_EXACT.md)** — a 27-cell rational graphon grid independently evaluated by face and pairwise-factor algorithms for the 35-vertex pattern; no finite host found or claim promoted.
- **[OpenAI/math transfer intake](docs/OPENAI_MATH_TRANSFER.md)** — seven pinned, scope-bounded author-claim research leads and four SHA-256-pinned reusable instruments with transitive impact analysis (`python3 scripts/transfer.py --check`); K42 dual-checker calibration (`python3 scripts/k42_calibration.py --check`) is *not* a model benchmark trial.
- **[Lean proof pipeline](LEAN.md)** — pinned workspace, Ramsey benchmark, two-element Frankl case, axiom audits and commit-bound CI evidence; scope review remains separate.
- **[Matched-budget research benchmark](benchmarks/PROTOCOL.md)** — preregistered M095/M075/M074 pilot, four solver architectures, three seeds, exact cost accounting and evidence-gated trial ledger (`python3 scripts/benchmark.py --check`); no experimental trials claimed yet.
- **[Proof exchange / scaling protocol](docs/PROOF_EXCHANGE.md)** — 100 claimable, evidence-bound wave slots with scout/adversary/checker roles, dependency-gated proof obligations and coverage ablations (`python3 scripts/scale.py --budget 100`; [SCALE.md](SCALE.md)).
- **[Coverage depth plan](COVERAGE.md)** — evidence-separated breadth-first 200-slot allocation: two distinct planned work kinds per each of 100 problems, compared at equal budget with leverage-first dispatch (`python3 scripts/coverage.py --json`). Planning is not executed research, verification, or independently accepted output.
- **[Superagent claim router](docs/ROUTER.md)** — a fail-closed intake/slot reservation prototype that gates worker mandates on unique, fresh GitHub claims and current work scopes; no agent execution or proof acceptance implied.
- **[Agent work queue](AGENTS.md)** — derived claimable items across obligations, Lean, jobs, roadmap, comparators and status audits (`python3 scripts/work.py --next 5`).
- **[Roadmap](ROADMAP.md)** ([on the dashboard](https://svyable.github.io/100/#roadmap)) — live scoreboard against targets, and every shipped, current, next and later item with evidence and exit criteria. Source: [data/roadmap.json](data/roadmap.json).
- **[Next 100 hypothesis reservoir](https://svyable.github.io/100/next/)** — 216 cross-domain, unvetted proposals across 27 research domains in a scalable pipeline; ranked discovery priorities, not claimed new open results ([protocol](NEXT_100.md)). The active 100 remains capped.
- **[Discovery trails](https://svyable.github.io/100/discovery/)** — five sourced, motivation-linked reasoning trails for M071, M073, M075, M078 and M095; each distinguishes known reproductions, blocked claims and proposed next moves, with per-problem cross-links and [contribution protocol](docs/DISCOVERY_PROTOCOL.md). No discovery note is a proof certificate.
- **[Reading-first guides](https://svyable.github.io/100/problems/M071/#reading-guide)** — explanatory starting points for Hadwiger, Caccetta–Häggkvist and Frankl; every problem page now separates status, finite/formal checks and next action. Editorial prose and cross-problem method links are *not* proof claims; canonical evidence remains in the ledgers ([source](data/reading_guides.json)).
- **[Public research site](https://svyable.github.io/100/)** (once GitHub Pages is enabled: [activation guide](docs/PAGES_SETUP.md)) — generated static site: one permanent page per problem (`/problems/M071/`) and per field, atlas charts, lab, formal statements, campaigns, claim triage, roadmap, ledger, every research dossier, a `/` command palette, JSON/CSV API and Atom feed. Works without JavaScript; CI byte-checks it against the ledgers and link-checks every page.
- **[Start here — for humans and agents](https://svyable.github.io/100/start/)** — three navigable routes for readers, specialist reviewers, and scoped contributors. Agents get a [machine-readable contract](https://svyable.github.io/100/api/agent.json), a [20-task runnable shortlist](https://svyable.github.io/100/api/agent/tasks.json) and [plain-text site guide](https://svyable.github.io/100/llms.txt). Task availability is a static snapshot, **not** a live GitHub claim check.
- **[Work queue](https://svyable.github.io/100/work/)** — every bounded, claimable unit of work (proof obligations, Lean targets, cohort jobs, roadmap items, one Lean comparator and one status audit per problem that needs them), derived from the ledgers; `python3 scripts/work.py --next 5`. Parallel contributors and agents follow [AGENTS.md](AGENTS.md): claim, deliver, `python3 scripts/regen.py`, ship.
- **[Yield](YIELD.md)** — independently accepted work items per 10 recorded agent-hours, from the [outcomes ledger](data/outcomes.json). An accepted work item is not a new theorem (new restricted results need a separate novelty audit and are counted separately); capacity (filled slots) is not yield; review is the bottleneck, so reviews are claimable `V-…` items in the work queue.
- **[Formal comparator statements](lean/README.md)** — exact Lean 4 statements for 9 targets (Goldbach, Erdős–Straus, Caccetta–Häggkvist, Frankl, Hadwiger, reconstruction, Hadamard, R(5,5), projective plane of order 12) with kernel-checked fidelity tests and finite certificates, every exported theorem axiom-audited by the [Lean proof gate](LEAN.md) ([catalogue](data/formalization.json)).
- **[Exact probe lab](LAB.md)**: 18 independently checked probes on 13 reusable engines give **20 of the 100 problems** an exact verifier (previously 3), including all 19 problems where finite computation can refute or settle the claim. All ranges are known mathematics; see [the lab dossier](research/LAB_CAMPAIGNS.md).
- [Frankl's independent Burnside orbit certificate](research/M075_BURNSIDE.md) — n=5 full-support orbit count 28,960 from seven S5 cycle types, reproducible without canonicalizing millions of families.
- **[Frankl triple-local global search](research/M075_TRIPLE7_SAT.md)** — exact, independently tested 128-variable subset-membership CNF for every fixed family size 2..18 on seven elements; 19-member published positive control; real 17/18-member CaDiCaL attempts remain **unknown**, not UNSAT proofs.
- [Frankl's closure-pruned canonical orbit generator](research/M075_CANONICAL.md) — proved orbit-minimum equivalence, n=5 known full-support count and n=4 orbit census reproduced, no new bound claimed.
- **[Structure mines](MINES.md)**: six certified tables read off those certificates (Goldbach records, Erdős–Straus residues and parametric identities, deck invariants, poset balances, Frankl orbits). Each table is recomputed by a second code path. A table is not a theorem.
- [Erdős–Straus parametric identities](research/M019_IDENTITIES.md) — nine polynomial identities on hard-class progressions (including $n=120t+73$ and $n=120t+97$); 106 of 117 primes through 8,000 covered by closed form; not a full proof.
- **[Statement-scope review drafts](data/statement_scope_reviews.json)** — five provisional problem formulations and exact unresolved assumptions; *not* independent open-status confirmations.
- **[Evidence-gated portfolio curation](docs/PORTFOLIO_SELECTION.md)** — targeted review flags, replacement standards, and [unvetted admission alternatives](data/portfolio_triage.json).
- **[Execution-priority queue](ATTACK_QUEUE.md)** — ordered by dispatch score (editorial + readiness + an action bonus), not by readiness alone. Claimed finite witnesses, missing engines and published certificates move up. A range extension the campaign itself says is already known mathematics is refused. Cohort jobs and the shared attack shapes are in [APPROACH.md](APPROACH.md).
- **[Solved archive](data/solved.json)** — strict full-resolution ledger, initially empty; known finite benchmarks are kept separate.
- [Caccetta–Häggkvist finite census and 18-vertex SAT target](research/M074_CH.md) — exact symmetry coverage, independent cycle check and reproducible CNF encoding; no new proof claimed.
- [CH (27,9) sharp nine-vertex local lemma](proofs/M074_NINE_VERTEX.md) — elementary 29-arc upper bound with a sharp witness, no nine-vertex minimum outdegree 3, global indegree cap 10, and explicit remaining regular/irregular branches; no full (27,9) result claimed.
- [CH (27,9) regular-branch exclusion](proofs/M074_27_REGULAR.md) — builds on the sharp nine-vertex lemma: a 23-versus-22 cross-cut contradiction excludes 9-in/9-out regular candidates; the indegree-ten irregular branch remains unresolved and awaits review.
- [CH (27,9) irregular B-subset obstruction](proofs/M074_B_INTERNAL_GIRTH.md) — independently audited girth/min-outdegree floor cuts reduce relaxed z=4 profiles from 473 to 295; no full-case resolution.
- [General degree-defect transfer lemma](proofs/DEGREE_DEFECT_TRANSFER.md) — exact high/low indegree saturation for any finite outregular digraph, with independent exhaustive small graph tests and explicit CH (24,8) application.
- [CH (24,8) full finite candidate proof](proofs/M074_IRREGULAR_24.md) — 19 × 5005 exact integer-profile reduction, local triangle elimination, high/low degree contradiction; independent specialist review pending and prior finite DRAT work acknowledged.
- [CH (24,8) regular-case obstruction](research/M074_ELEMENTARY_24_REGULAR.md) — an optimal 8-neighborhood 21-arc ceiling and cross-cut demand of 22 versus capacity of 15 exclude exact 8-in/8-out-regular candidates. The regular-case proof alone does not address irregular indegrees; see the separate full finite (24,8) candidate proof above (independent review pending).
- [CH (21,7) elementary finite exclusion](research/M074_ELEMENTARY_21.md) — seven-vertex degree rigidity plus a 145-vs-147 arc-budget contradiction excludes the 21-vertex triangle-free case; no general resolution or originality claim.
- [CH (18,6) elementary finite exclusion](research/M074_ELEMENTARY_18.md) — a saturated-pivot/indegree contradiction removes the need for a SAT proof for this **finite case**, while retaining frozen CNFs as independent audit targets; no full-conjecture or novel-result claim.
- [CH 18-vertex regularity reduction](research/M074_REGULARITY.md) — self-contained six-vertex lemma, proof-derived in/out-regularity and symmetry-fixed CNF; SAT/UNSAT certificate still pending.
- [Research engine and verification rules](docs/RESEARCH_ENGINE.md) — how results, readiness, rankings and CI interact.
- [Current rank order](RANKED.md) — deterministic generated ranking of 100 candidates.
- [Machine-readable registry](data/problems.json) — stable IDs, working questions, first attacks, weighted scores, evidence status and provenance.
- [Active proof campaigns](research/CAMPAIGNS.md) — precise statements, verifiers and bounded first attacks.
- [Published Ramsey K42 replay](research/M095_RAMSEY.md) — offline SHA-256-pinned McKay catalog, 328 known 42-vertex graph6 witnesses plus color-swapped complements, checked by two independent exact K5 algorithms; reproduces R(5,5) ≥ 43, not a novel bound.
- [Ramsey R(5,5) certificate campaign](research/M095_RAMSEY.md) and [Frankl finite verification](research/M075_FRANKL.md) — reproducible small cases; neither resolves the full problem.
- [Research and verification protocol](docs/RESEARCH_PROTOCOL.md) — rules for advancing, scoring and retiring candidates.
- [Starting status sources](docs/SOURCES.md) — official Clay status and recent 2026 proof-claim precautions.
- [2026 claimed-resolution triage](research/CLAIM_REVIEWS_2026.md) — primary manuscripts, exact scope comparisons, independent review gaps and next checks for the 15 flagged IDs ([structured ledger](data/claim_reviews_2026.json)). M098 is `verified_open` on the first-order statement; the infinitary counterexample is a different problem ([note](research/M098_VAUGHT.md)).
- [M071/M073 witness extractability audit](research/M071_M073_WITNESSES.md) — Sidorenko pattern H reconstructed (35 vertices, 66 edges); Hadwiger claim recorded as existential with no finite adjacency list; neither manuscript accepted ([frozen ledger](data/claim_witness_replay.json)).

**Important:** This is a *provisional candidate pool*, **not** a claim that all 100 are currently independently verified as unsolved. Five official Millennium entries have official status citations; the remaining 95 need closer status and precise-statement review. Recent claims are explicitly flagged. The first task is the status audit and selection of tractable restricted lemmas.

The initial scores are **editorial judgments, not estimated probabilities of success**. We optimize a portfolio of ambitious results *and* independently checkable early progress: 30% mathematical impact, 30% attackability, 25% verifiability, 15% spillover. Rank and evidence state are separate.

```sh
python3 scripts/lab.py --list
python3 scripts/lab.py
python3 scripts/lab.py --check
python3 scripts/lab.py --level deep --check
python3 scripts/mine.py
python3 scripts/mine.py --check
python3 scripts/rank.py
python3 scripts/rank.py --check
python3 scripts/research.py
python3 scripts/research.py --check
python3 scripts/formal.py --check
python3 scripts/approach.py
python3 scripts/approach.py --check
python3 scripts/work.py --check
python3 scripts/scale.py --write
python3 scripts/scale.py --check
python3 scripts/roadmap.py
python3 scripts/roadmap.py --check
python3 scripts/regen.py --check --fast
python3 scripts/build_site.py
python3 scripts/build_site.py --check
python3 scripts/lean_verify.py   # needs elan; builds Lean and audits axioms
python3 -m unittest discover -s tests -v
```

When changing scores or evidence states, include a dated source and a reason in the commit/PR. A Lean-checked result only proves what was *encoded*; inspect whether that exactly matches the claimed conjecture. Never label a problem solved on the basis of an announcement alone.

Every problem has an editorial computational `modality` (finitely refutable, finite parameter, existence family, asymptotic, structural), and [data/engine_roadmap.json](data/engine_roadmap.json) names the engine still needed for each computable problem without a probe. A passing probe certifies a finite range only. Exit code 3 from the lab means a confirmed violation inside known mathematics, which almost certainly indicates a bug; it never adds anything to Solved.

The scheduled GitHub workflow reproduces existing finite baselines weekly when GitHub Actions scheduling is enabled. It also reruns every lab probe at deep level. It does not invent proofs or check the changing research literature on its own.
