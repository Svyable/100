# 100 — A living portfolio of mathematical grand challenges

**Purpose:** Preserve, refine, and stack-rank 100 concrete mathematical proof/counterexample targets, looking for results and methods that create new branches of discovery.

- **[Lean proof pipeline](LEAN.md)** — pinned workspace, Ramsey benchmark, reusable restriction lemma, axiom audits and commit-bound CI evidence; scope review remains separate.
- **[Roadmap](ROADMAP.md)** ([on the dashboard](https://svyable.github.io/100/#roadmap)) — live scoreboard against targets, and every shipped, current, next and later item with evidence and exit criteria. Source: [data/roadmap.json](data/roadmap.json).
- **[Next 100 hypothesis reservoir](https://svyable.github.io/100/next/)** — 216 cross-domain, unvetted proposals across 27 research domains in a scalable pipeline; ranked discovery priorities, not claimed new open results ([protocol](NEXT_100.md)). The active 100 remains capped.
- **[Public research dashboard](https://svyable.github.io/100/)** (once GitHub Pages is enabled: [activation guide](docs/PAGES_SETUP.md)) — ranked search, evidence filters, active proof campaigns.
- **[Exact probe lab](LAB.md)**: 15 independently checked probes on 11 reusable engines give **17 of the 100 problems** an exact verifier (previously 3), including 16 of the 19 problems where finite computation can refute or settle the claim. All ranges are known mathematics; see [the lab dossier](research/LAB_CAMPAIGNS.md).
- **[Statement-scope review drafts](data/statement_scope_reviews.json)** — five provisional problem formulations and exact unresolved assumptions; *not* independent open-status confirmations.
- **[Evidence-gated portfolio curation](docs/PORTFOLIO_SELECTION.md)** — targeted review flags, replacement standards, and [unvetted admission alternatives](data/portfolio_triage.json).
- **[Execution-priority queue](ATTACK_QUEUE.md)** — evidence-aware ordering of the top 100 with precise proof obligations for active campaigns.
- **[Solved archive](data/solved.json)** — strict full-resolution ledger, initially empty; known finite benchmarks are kept separate.
- [Caccetta–Häggkvist finite census and 18-vertex SAT target](research/M074_CH.md) — exact symmetry coverage, independent cycle check and reproducible CNF encoding; no new proof claimed.
- [Research engine and verification rules](docs/RESEARCH_ENGINE.md) — how results, readiness, rankings and CI interact.
- [Current rank order](RANKED.md) — deterministic generated ranking of 100 candidates.
- [Machine-readable registry](data/problems.json) — stable IDs, working questions, first attacks, weighted scores, evidence status and provenance.
- [Active proof campaigns](research/CAMPAIGNS.md) — precise statements, verifiers and bounded first attacks.
- [Ramsey R(5,5) certificate campaign](research/M095_RAMSEY.md) and [Frankl finite verification](research/M075_FRANKL.md) — reproducible small cases; neither resolves the full problem.
- [Research and verification protocol](docs/RESEARCH_PROTOCOL.md) — rules for advancing, scoring and retiring candidates.
- [Starting status sources](docs/SOURCES.md) — official Clay status and recent 2026 proof-claim precautions.
- [2026 claimed-resolution triage](research/CLAIM_REVIEWS_2026.md) — primary manuscripts, exact scope comparisons, independent review gaps and next checks for the 15 flagged IDs ([structured ledger](data/claim_reviews_2026.json)).

**Important:** This is a *provisional candidate pool*, **not** a claim that all 100 are currently independently verified as unsolved. Five official Millennium entries have official status citations; the remaining 95 need closer status and precise-statement review. Recent claims are explicitly flagged. The first task is the status audit and selection of tractable restricted lemmas.

The initial scores are **editorial judgments, not estimated probabilities of success**. We optimize a portfolio of ambitious results *and* independently checkable early progress: 30% mathematical impact, 30% attackability, 25% verifiability, 15% spillover. Rank and evidence state are separate.

```sh
python3 scripts/lab.py --list
python3 scripts/lab.py
python3 scripts/lab.py --check
python3 scripts/lab.py --level deep --check
python3 scripts/rank.py
python3 scripts/rank.py --check
python3 scripts/research.py
python3 scripts/research.py --check
python3 scripts/roadmap.py
python3 scripts/roadmap.py --check
python3 scripts/build_site.py
python3 scripts/build_site.py --check
python3 -m unittest discover -s tests -v
```

When changing scores or evidence states, include a dated source and a reason in the commit/PR. A Lean-checked result only proves what was *encoded*; inspect whether that exactly matches the claimed conjecture. Never label a problem solved on the basis of an announcement alone.

Every problem has an editorial computational `modality` (finitely refutable, finite parameter, existence family, asymptotic, structural), and [data/engine_roadmap.json](data/engine_roadmap.json) names the engine still needed for each computable problem without a probe. A passing probe certifies a finite range only. Exit code 3 from the lab means a confirmed violation inside known mathematics, which almost certainly indicates a bug; it never adds anything to Solved.

The scheduled GitHub workflow reproduces existing finite baselines weekly when GitHub Actions scheduling is enabled. It also reruns every lab probe at deep level. It does not invent proofs or check the changing research literature on its own.
