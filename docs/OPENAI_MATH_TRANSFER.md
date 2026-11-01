# OpenAI/math transfer intake: evidence before claims

**2026-10-31 | Research intake, not a theorem announcement.** Source: [openai/math](https://github.com/openai/math), pinned to commit [4eaee875](https://github.com/openai/math/commit/4eaee87548250b2682affda7d05d947c05554bae), whose `overview.tex` lists *author-claimed* results. No row below is independently validated by this transfer layer.

## Why this layer exists

The repository already maintains 100 ranked targets, formal comparator statements, a proof-obligation DAG, distinct agent roles, and a 36-cell preregistered benchmark. The missing link was *provenance-aware transfer*: map relevant external techniques to exact local obligations, preserve reusable local instruments, and determine what must be re-reviewed after source changes. It is deliberately read-only toward `data/problems.json`, `data/solved.json`, proof-obligation statuses and benchmark trial results.

| Intake | Our IDs | Exact boundary / immediate action |
|---|---|---|
| [079](../data/openai_math_transfer.json) | M055, M056 | Different consequences of local smoothing; check dimensions, strict interior vs endpoint inequalities, and the Kakeya implication separately |
| 107 | M084 | Claimed `omega <= 9/4` over the complex numbers is **not** `omega = 2`; extract and verify a finite tensor identity |
| 116 | M088 | Noncommutative formula hitting points are not general commutative arithmetic-circuit PIT; lock field and circuit model |
| 157 | M071 | Existential graph families are not an explicit independently replayed finite counterexample |
| 161 | M073 | Pattern reconstructed locally; the host violating the density inequality still needs exact independent replay |
| 179 | M094 | Circulant Hadamard obstruction is a restricted subclass, not all Hadamard matrices |
| 199 | M046 | Unreviewed claimed algebraic counterexample requires an Artin-algebra/Ext quantifier audit before changing status |

The source references and exact next action for each intake are in [data/openai_math_transfer.json](../data/openai_math_transfer.json). They are pinned to one upstream SHA; validator checks immutable-looking URL *shape* but cannot authenticate the PDF's math, peer review, or the upstream server.

The first four reusable local instruments in [data/instruments.json](../data/instruments.json) link actual source files, a SHA-256 for their bytes, proof gaps, falsifiers and proposed future reuse. `candidate_unreviewed` and `known_reproduction` are intentionally the **only** statuses the validator permits. Proposed cross-problem reuse is a research idea, not an accepted implication.

## Reproduce and inspect

From repo root:

```sh
python3 scripts/transfer.py --check
python3 scripts/transfer.py --json
python3 scripts/transfer.py --changed scripts/ch24_crosscut.py
python3 scripts/transfer.py --changed data/claim_reviews_2026.json
python3 scripts/transfer.py --upstream-sha 0000000000000000000000000000000000000000
python3 -m unittest discover -s tests -p 'test_transfer.py' -v
```

`--check` rejects unpinned/changed local instrument files, missing related evidence, unknown problem/review IDs, unsafe paths, dependency cycles, and any attempted status promotion. A changed local source requires an **explicit review and repin**, not automated trust. `--changed` and `--upstream-sha` report affected transfers/instruments transitively; they do not change the ledger. The upstream SHA must be observed separately: this offline checker does not poll GitHub.

Independent mathematical review, exact source scope comparison, novelty audit and formal proof checking remain the governing protocol. A hash is an identity check, not a theorem certificate. In particular, no result above changes the current [claim review ledger](../data/claim_reviews_2026.json) or [Solved](../data/solved.json).

## K42 deterministic checker calibration (not an agent trial)

```sh
python3 scripts/k42_calibration.py --check
python3 -m unittest discover -s tests -p 'test_k42_calibration.py' -v
```

This uses the already-merged dedicated K42 calibration, which replays the 328 pinned McKay records with two exact checkers, a one-edge adversarial mutant, and a deliberately tampered catalog. The historical evidence is pinned in [benchmarks/calibrations/k42_checker.json](../benchmarks/calibrations/k42_checker.json); `--check` replays without writing files. It makes **zero model calls**, is **not a trial in any of the four agent arms**, and never counts as new mathematics. Its purpose is to validate the checker environment and immutable reference data before a later matched-budget evaluation.

This calibration was independently added to main before this transfer PR; we reuse it rather than maintaining a second competing wrapper.

The preregistered [36-cell protocol](../benchmarks/PROTOCOL.md) is still unexecuted until real sequential, independent, conversation and proof-exchange agent sessions produce full token/tool/time logs. Our new M074 (24,8) finite candidate argument appeared after the frozen benchmark source commit; task leakage and changed difficulty must be addressed transparently before using CH24 as a blind novelty test. Do not invent completed trial rows.

## Review and promotion procedure

1. Pin an upstream source snapshot and map its *exact* hypotheses, theorem, exceptions, and claimed consequence to our problem.
2. Find a smallest reusable lemma or witness, with a falsifier and honest prior-art boundary.
3. Send the independent checker and adversarial reviewer the immutable source and scope, not the author's conclusion.
4. Replay exact finite claims, audit Lean statement fidelity and dependencies, and obtain specialist reviews where required.
5. Promote only through the existing formal/research protocols, record negative findings, and re-dispatch verified instruments to other eligible targets.

This is a dependency-aware research workspace, not an automatic proof-admission engine.
