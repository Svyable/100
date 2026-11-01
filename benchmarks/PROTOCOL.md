# Proof Exchange — preregistered, matched-budget pilot

**Status (2026-10-31): experiment defined, zero trials run.**
This is a measurement framework for [issue #55](https://github.com/Svyable/100/issues/55).
It does not run language models, deploy agents, accept proof claims, or imply
that parallel work is faster. A valid JSON schema is not a valid theorem.

## Reproduce the design

```sh
python3 scripts/benchmark.py
python3 scripts/benchmark.py --check
python3 scripts/benchmark.py --json
python3 -m unittest discover -s tests -p 'test_benchmark.py' -v
```

Sources: [preregistered manifest](../data/benchmark_prereg.json) and
[empty trial ledger](../data/benchmark_runs.jsonl). The manifest pins a full
source commit and is SHA-256 hashed into each trial record. Changing the tasks,
resource limits, arms or seeds changes the protocol digest; trials using a
different digest are rejected rather than silently pooled.

## Fixed experimental design

- **K42-REPLAY (M095, known result):** import an exact 42-vertex published
  Ramsey witness, independently check it, and audit its source. Success is a
  *reproduced known certificate*, not a new bound or a novel theorem.
- **FRANKL-TRANSFER (M075, structural):** attempt a precisely scoped canonical
  augmentation/extension lemma beyond the known n=5 orbit count. A complete
  falsifier or negative result must be preserved even if no theorem emerges.
- **CH24-IRREGULAR (M074, dependency-heavy):** attack the remaining indegree-nine
  branch at (24,8), without importing an 8-inregular assumption. The proven
  regular-case exclusion does not settle the full finite problem.

Each task is assigned to four arms, repeated at seeds **11, 23, 37**:

1. **sequential:** one agent, no parallel replicas.
2. **independent:** multiple independent attempts, best-of-k output without
   inter-worker conversation. Reviewer cost is still charged.
3. **conversation:** communicating workers with unrestricted discussion under
   the same total budget.
4. **proof_exchange:** scout, adversary and independent checker receive scoped
   evidence contracts; message passing is intentionally sparse.

There are **36 trial cells**. The per-cell *design caps* are 45,000 model
tokens, 120 tool calls and 3,600 wall-clock seconds. These are pilot assumptions,
not observed consumption. They apply to **all contributors, verification and
coordination within an arm**. If an arm cannot operate within the cap, record a
timeout/error and its actual usage; do not increase its budget after seeing
the result. External specialist review is reported separately and never
fabricated or assumed free when comparing end-to-end costs.

## Verification and scoring rules

The primary metric is *externally reviewed, independently checked new restricted
results per total resource consumed*. A claim cannot enter that numerator
without two distinct external reviews and an actual specialist audit of
novelty, mathematical scope and independence. The validator merely enforces
paths, HTTPS links and distinct domains; it cannot authenticate reviewers.

Keep these outcomes distinct:
- `none`: no accepted artifact (including failures and timeouts);
- `known_reproduction`: a result already in the literature, no novelty credit;
- `restricted_unreviewed`: an interesting restricted claim with evidence but
  no external acceptance;
- `externally_reviewed_restricted`: eligible *candidate* for novelty credit,
  **only after a human audit** of reviewers, proof, sources and scope.

For novelty tasks, explicit counterexamples and sharply delimited negative
results are valuable outcomes, but are **not automatically counted** as novel
theorems. No automated result changes the Solved ledger.

Secondary measures are time to a checked artifact, failed/invalid certificates,
true mathematical objections detected, false positive rate, scope drift,
reuse across different problem IDs, per-run resource totals and specialist
review burden. Always publish individual run records, including failed and
timed-out attempts.

**No causal performance conclusion is permitted until the full 36-cell grid
is complete under the preregistered protocol.** Even then three seeds per arm
have low statistical power: report raw denominators and uncertainty, and do
not interpret one task's result as general performance.

## Trial ledger contract

One JSON object per line in `data/benchmark_runs.jsonl`; never overwrite or
reuse a task/arm/seed triple. Each record has exactly these fields:

```json
{
  "manifest_sha256": "64 lowercase hex characters from benchmark.py",
  "task_id": "K42-REPLAY",
  "arm": "sequential",
  "seed": 11,
  "status": "timeout",
  "classification": "none",
  "resources": {
    "model_tokens": 1000,
    "tool_calls": 2,
    "elapsed_seconds": 60
  },
  "evidence": null
}
```

This is a **schema example**, not an actual observation. A completed claimed
artifact instead needs `evidence` with relative existing paths
`artifact`, `checker_log`, `scope_audit`, and an
`independent_review_urls` array. In a real run these point to immutable,
replayable trial outputs, not generic documentation.

```sh
python3 scripts/benchmark.py --check
python3 -m unittest discover -s tests -p 'test_benchmark.py' -v
```

The implementation fails closed for duplicated trials, changed protocol
digests, over-budget runs, unverified evidence paths, and fake upgrades of the
known Ramsey replay to a novel result. Its tests use synthetic examples
**only as negative controls**; they are not empirical evaluation data.

## Anti-leakage and independence

The frozen source commit is a **baseline context**, not a holdout. Since this
project is public, benchmark authors should freeze prompt templates and
reference source snapshots before testing, use fresh unpublished mathematical
subtasks where feasible, and audit answers against prior art. Keep the same
tool and internet policies across arms, pin model versions and record
checkers separately from solver attempts.

Do not rank the arms by how many tokens they emitted, how many slots they
claimed, how many textbook results they reproduced, or how many claimed
proofs lacked expert scrutiny. The research objective is *more accepted
mathematics per unit of total effort*, not higher apparent throughput.

## Next delivery

Run the first **calibration replay** of K42 in all four arms with exactly
the same dataset, then confirm the manifest digest, cost logs and independent
replay links are reproducible before committing the remaining trial outputs.
After calibration, execute all preregistered trials and publish a complete,
even if null, report. See [Proof Exchange](../docs/PROOF_EXCHANGE.md) and
[the work-claim protocol](../AGENTS.md).
