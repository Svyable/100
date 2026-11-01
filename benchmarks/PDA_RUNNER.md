# Perceive → Decide → Act — instrumented K42 agent calibration

This is a **single-cell, explicitly enabled, actual-model runner** for the
preregistered [Proof Exchange benchmark](PROTOCOL.md). It does not make
background calls, schedule agents, fetch unpinned research, infer novelty, or
change the **Solved** ledger.

## Perceive: inspect the frozen task without running a model

```bash
python3 scripts/pda_trial.py --plan --arm sequential --seed 11
python3 scripts/benchmark.py --check
```

The plan checks the current benchmark manifest, existing trial cells, and
the SHA-256-pinned 328-record McKay K42 corpus. It exposes four *already known*
valid candidate witnesses, frozen scope, role order, token/tool/time caps,
prompt revision, manifest digest and source hashes. **No key, internet,
model execution or write is needed for --plan.**

The runner refuses unsupported arms/seeds, moving model aliases marked
"latest", duplicate trial cells, and a changed published graph6 corpus.

## Decide: one bounded, explicitly selected experimental cell

A run requires `--model` with an explicit model identifier (the API response
must echo that exact identifier) and an operator-provided `OPENAI_API_KEY` in
the process environment. Use the same pinned model/version across arms.

```bash
# On an operator-controlled machine with a separately provided API credential:
python3 scripts/pda_trial.py --arm sequential --seed 11 \
  --model YOUR_PINNED_MODEL_VERSION --run
```

This incurs model API charges and creates *real measured* evidence on disk.
No model calls occur by default, and no API key belongs in a file, issue, PR or
committed artifact. No model is assumed to be available to GitHub Actions.

Run each of the other three arms by explicitly selecting `independent`,
`conversation`, or `proof_exchange`. Each has the same maximum resources
from the frozen protocol, but **actual consumption differs and is measured**.
The protocol's seed is included in the prompts as a label; the Responses API
request does **not** set a provider random seed, so exact generation
reproducibility is not promised.

## Act: execute, independently check, retain evidence

Every role sends a real request through the Responses API, with `store: false`.
The request uses only the four candidate published graph6 lines. The adapter
requires a completed response, the exact requested model, visible output,
and the provider's own input/output/total token counts. It does not estimate
token use from output length or silently replace a provider with a mock.

The model must return a JSON object with an unchanged source index and graph6
line and the classification `known_reproduction`. Each valid candidate is
checked against **two separate exact K5 algorithms**, in addition to replaying
the pinned source corpus. Bad bytes, unsupported proof scope, incorrect index
or checker failures cannot be treated as a passed replay. Model commentary is
not itself a mathematical check or an independent review.

Four frozen architectures differ in *communication*, not in what constitutes
evidence:

| Arm | Roles and information flow |
|---|---|
| `sequential` | One proposer |
| `independent` | Three isolated attempts; accept a checked candidate from any one |
| `conversation` | Proposer → critic → reviser, passing outputs forward |
| `proof_exchange` | Scout → adversary → checker, passing outputs forward; the final LLM "checker" is **not** external review |

The agent and exact-checker calls all count against the same tool-call cap.
Resource totals include every completed model role. After execution, the
runner writes a unique directory under
`benchmarks/runs/K42-REPLAY_<arm>_<seed>/` containing `perceive.json`,
`decide.json`, `transcript.json`, `checker.json`, and `scope.json`.
It validates the evidence and appends one row to
`data/benchmark_runs.jsonl`, with actual token/tool/wall time counts.
**Never overwrite a recorded cell.** If a request fails without metered usage,
the runner preserves an `incomplete.json` and any partial transcript,
but **does not** fabricate a benchmark record. A failed or rejected *fully
metered* attempt is recorded as `none`, not quietly dropped.

After any real run, commit the ledger row **and** immutable evidence directory
together, and run:

```bash
python3 scripts/benchmark.py --check
python3 -m unittest discover -s tests -p 'test_pda_trial.py' -v
python3 scripts/regen.py --check
```

## Important limits and next experimental gate

- The four preselected candidates are valid known results. This measures
  reliable bounded **agent handoff, instrumentation, checker verification,
  communication cost and corruption detection** — not the agent's ability
  to discover a new mathematical result.
- Full comparisons require the complete preregistered trial grid. A
  checker calibration from `k42_calibration.py` is not an agent trial.
- The frozen CH24 novelty task was contaminated after preregistration by
  published work. It **must be replaced in a separately versioned,
  prior-art-audited manifest before running novelty comparisons**.
- No externally reviewed restricted result can be accepted without
  independent specialist review of statement fidelity, novelty and proof.
  This runner deliberately cannot perform that promotion.
- This is an *operator-run CLI*, not yet a securely deployed autonomous
  work scheduler. API credentials, compute budget approval and an
  uncontaminated new task are still dependencies for later research stages.
