# Roadmap — 100 mathematical grand challenges

As of **2026-10-31**. This page tracks the program as a whole: what has shipped, what is running now, and what comes next. The live numbers come from generated files ([LAB.md](LAB.md), [ATTACK_QUEUE.md](ATTACK_QUEUE.md), [RANKED.md](RANKED.md)); if they disagree with this page, they are right.

> **Ground rule.** Nothing on this roadmap is a new theorem. Every finished item is either infrastructure, a reproduction of known mathematics, or an audit. The [Solved archive](data/solved.json) holds **0** entries and gets one only through the promotion gate in [docs/RESEARCH_ENGINE.md](docs/RESEARCH_ENGINE.md).

## Where we are

| Metric | Now |
|---|---:|
| Candidate problems registered, scored and ranked | 100 / 100 |
| Problems with an exact, independently checked verifier | 17 / 100 (started at 3) |
| Computable-modality problems covered | 16 / 19 |
| Exact probes / reusable engines | 15 / 11 |
| Standalone verifiers (M074, M075, M095) | 3 |
| 2026 proof claims triaged for scope | 15 / 15 |
| Independently accepted full resolutions | 0 |

## Shipped

### Phase 0 — Foundation
- [x] Registry of 100 problems with stable IDs, working questions, first attacks, weighted scores (30/30/25/15) and provenance — [data/problems.json](data/problems.json).
- [x] Deterministic ranking with a `--check` mode — [RANKED.md](RANKED.md), `scripts/rank.py`.
- [x] Research and verification protocol, source policy and contribution templates — [docs/RESEARCH_PROTOCOL.md](docs/RESEARCH_PROTOCOL.md), [docs/SOURCES.md](docs/SOURCES.md), [CONTRIBUTING.md](CONTRIBUTING.md).

### Phase 1 — Research engine
- [x] Verified milestones, proof campaigns, execution readiness and a strict solved ledger — [data/research_program.json](data/research_program.json), `scripts/research.py`.
- [x] Execution-priority queue that separates editorial score from evidence — [ATTACK_QUEUE.md](ATTACK_QUEUE.md).
- [x] Five active proof campaigns with precise statements and bounded first attacks — [research/CAMPAIGNS.md](research/CAMPAIGNS.md).
- [x] Tests for the ledger and the promotion gate, including future Solved transitions.

### Phase 2 — First exact benchmarks
- [x] **M074 Caccetta–Häggkvist:** tiny-digraph verifier, a symmetry-certified five-vertex orbit census, a proof-aware SAT encoder plus an independent compact encoding with semantic tests, and an n=18, r=6 SAT research target — [research/M074_CH.md](research/M074_CH.md).
- [x] **M075 Frankl:** exhaustive small-ground-set verification — [research/M075_FRANKL.md](research/M075_FRANKL.md).
- [x] **M095 Ramsey R(5,5):** certificate campaign for small cases — [research/M095_RAMSEY.md](research/M095_RAMSEY.md).
- [x] External proof corpus pinned, with a streaming hash verifier and negative tests — `scripts/check_external_artifact.py`, [data/external_claims.json](data/external_claims.json).

### Phase 3 — Exact probe lab
- [x] 15 probes on 11 engines, each with a search **and** an independent checker, at smoke and deep levels — [LAB.md](LAB.md), [research/LAB_CAMPAIGNS.md](research/LAB_CAMPAIGNS.md).
- [x] Engines: `primes`, `finite_fields`, `graph_census`, `poset_census`, `cyclotomic`, `tensor_certificates`, `symmetry_reduction`, `exact_lp`, `graph_homomorphisms`, `polynomial_algebra`, `clique_search`.
- [x] Recent additions: Held–Karp exact LP probe (M097), Sidorenko homomorphism falsifier (M073), plane Jacobian probe (M041), and a Williamson construction closing Hadamard engine gap 92 (M094).
- [x] Every problem tagged with a computational `modality`, and an [engine roadmap](data/engine_roadmap.json) for the computable problems still without a probe.

### Phase 4 — Claim triage
- [x] Sourced scope audit of all 15 IDs flagged by 2026 resolution claims (M014, M030, M037, M038, M044, M049, M054, M055, M056, M060, M071, M073, M085, M098, M100) — [research/CLAIM_REVIEWS_2026.md](research/CLAIM_REVIEWS_2026.md), [data/claim_reviews_2026.json](data/claim_reviews_2026.json). M098 identified as a different problem; no status upgraded.

### Phase 5 — Publishing and CI
- [x] Public dashboard driven by the verified records (ranks, proof queue, campaigns, Solved ledger) — [docs/index.html](docs/index.html), `scripts/build_site.py --check`.
- [x] CI validates data, rankings, the site snapshot and JavaScript syntax; a weekly workflow reruns every probe at deep level plus the M074 orbit and SAT-encoding checks — [.github/workflows](.github/workflows).

## Now (in progress)

Top of the [execution queue](ATTACK_QUEUE.md):

1. **M074** — replay the external fixed-r=6 proof corpus on an independent host, check its hash and proof traces, and audit the hand-reduction steps before running duplicate SAT searches.
2. **M092 Zauner SIC** — extend the cyclotomic engine to the number fields for d = 4..8 and replay published exact fiducials.
3. **M075 Frankl** — canonicalize families under ground-set permutations; target a restricted lemma on minimal counterexamples.
4. **M078 / M079** — mine the graph and poset censuses for deck invariants and near-1/3 extremal posets.
5. **M093 / M094** — arcs in PG(3,q) for q ≤ 9; multiplier-group symmetry for Williamson order 116, then Goethals–Seidel for 156 and 172.

## Next

- **Close the computable gap (16/19 → 19/19).** Build the three engines on the roadmap: `interval_arithmetic` (M001 zeta zero counts, then M002 Dirichlet L-functions) and `group_characters` (M048).
- **Claim follow-ups that compute.** Independent group-ring checker for the M044/M049 witness; extract and check an explicit graph for the M071 Hadwiger claim and an explicit host for the M073 Sidorenko claim. Formal and proof claims (M014, M030, M037, M038, M054, M055, M056, M060, M085, M100) stay with specialist review.
- **Trusted proof output.** Emit DRAT/LRAT proofs from the SAT pipelines (M074, M096) and check them with an independent checker.
- **Deeper probes.** 8–9 vertex census with a faster canonical labeller (M071), step-graphon search (M073), degree-4 Jacobian maps (M041), flip-graph rank reduction (M084), the published K42 witness (M095).
- **Restricted lemmas for the +0 readiness tier.** Write falsifiable restricted statements and prior-art audits for M076, M042, M072, M077 and the complexity cluster (M082–M090).

## Later

- Status audit of the 95 non-Millennium entries against dated specialist sources, replacing resolved or duplicate candidates without going over 100.
- Lean or other formal encodings for statements where a fidelity check against the registered conjecture is feasible.
- First **independently reviewed new restricted result**, the only readiness bonus not yet earned (+3).
- An outside contributor pipeline: issue templates for certificates, a reproducibility bot, and published resource budgets per probe.

## Keeping this page current

When a PR ships a probe, engine, campaign milestone or claim review, tick or add the item here in the same PR and refresh the numbers from `python3 scripts/lab.py` and `python3 scripts/research.py`.
