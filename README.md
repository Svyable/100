# 100 — A living portfolio of mathematical grand challenges

**Purpose:** Preserve, refine, and stack-rank 100 concrete mathematical proof/counterexample targets, looking for results and methods that create new branches of discovery.

- **[Public research dashboard](https://svyable.github.io/100/)** (once GitHub Pages is enabled: [activation guide](docs/PAGES_SETUP.md)) — ranked search, evidence filters, active proof campaigns.
- [Current rank order](RANKED.md) — deterministic generated ranking of 100 candidates.
- [Machine-readable registry](data/problems.json) — stable IDs, working questions, first attacks, weighted scores, evidence status and provenance.
- [Active proof campaigns](research/CAMPAIGNS.md) — precise statements, verifiers and bounded first attacks.
- [Ramsey R(5,5) certificate campaign](research/M095_RAMSEY.md) and [Frankl finite verification](research/M075_FRANKL.md) — reproducible small cases; neither resolves the full problem.
- [Research and verification protocol](docs/RESEARCH_PROTOCOL.md) — rules for advancing, scoring and retiring candidates.
- [Starting status sources](docs/SOURCES.md) — official Clay status and recent 2026 proof-claim precautions.

**Important:** This is a *provisional candidate pool*, **not** a claim that all 100 are currently independently verified as unsolved. Five official Millennium entries have official status citations; the remaining 95 need closer status and precise-statement review. Recent claims are explicitly flagged. The first task is the status audit and selection of tractable restricted lemmas.

The initial scores are **editorial judgments, not estimated probabilities of success**. We optimize a portfolio of ambitious results *and* independently checkable early progress: 30% mathematical impact, 30% attackability, 25% verifiability, 15% spillover. Rank and evidence state are separate.

```sh
python3 scripts/rank.py
python3 scripts/rank.py --check
python3 scripts/build_site.py
python3 scripts/build_site.py --check
python3 -m unittest discover -s tests -v
```

When changing scores or evidence states, include a dated source and a reason in the commit/PR. A Lean-checked result only proves what was *encoded*; inspect whether that exactly matches the claimed conjecture. Never label a problem solved on the basis of an announcement alone.

No ongoing research, tracking, or updates occur automatically unless separately scheduled or implemented.
