# Ranking and research protocol

## Score, not prestige

Each integer metric ranges 1–5:

| Metric | Weight | Criteria |
|---|---:|---|
| impact | 30% | Mathematical consequence of an accepted full or meaningful partial proof |
| attackability | 30% | Restricted cases, reductions, exact computation, and plausible entry points |
| verifiability | 25% | Feasible independent proof, formal checker, reproducible certificate |
| spillover | 15% | Transferability of resulting tools to unrelated problems |

Score = 6*impact + 6*attackability + 5*verifiability + 3*spillover. This is a **curation heuristic** rather than a forecast of probability.

## Evidence states

- `official_open`: an official body lists this exact target open; must have dated primary source.
- `needs_review`: current open status and exact hypothesis scope not independently checked.
- `claim_needs_review`: a potentially relevant claimed proof/counterexample exists, but scope or independent acceptance has not been established.
- `verified_open`: contemporary primary specialist sources confirm that this exact claim remains open.
- `resolved`: independently accepted proof/counterexample of the full claim with cited source.
- `retired`: duplicate, superseded, ill-posed or deprioritized.

Resolved and retired targets should be replaced to keep 100 *active* candidates; do not recycle the old IDs. Never confuse a special-case proof with resolution of a universal claim.

## Research campaign for every promoted problem

1. **Status audit:** original theorem statement, precise quantifiers, exceptions, current literature and citations.
2. **First lemma:** a small new theorem or sharp barrier with explicit dependencies.
3. **Counterexample search:** finite cases, SAT/SMT, exact symbolic computation, or numerical heuristics where relevant.
4. **Proof construction:** write clear proof and formalize suitable subclaims where feasible.
5. **Independent verification:** separate checking of both theorem *meaning* and proof details; machine certificates when possible.
6. **Publish reproducibility:** archive inputs, code, seeds, exact outputs, failed paths, and compute costs.
7. **Rerank:** adjust scores only with a reason and evidence; preserve stable ID and history.

## First sprint

Audit the top ten before any full-scale proof campaign. Pick three with distinct methodologies: exact finite certificate, algebraic structural lemma, and analytic/number-theoretic restricted case. Record results even when negative.

## Governance

The ranking is automatically regenerated and checked on every pull request. CI validates structure, but it **cannot** determine mathematical correctness or automatically verify that a conjecture is still open. A source audit is a separate requirement.
