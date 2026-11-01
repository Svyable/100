# Fleet v1 — experiment planning, not mathematical execution

The repository's 100 active challenges remain curated. The fleet maps the existing
evidence-bound work queue to **up to 10,000 deterministic experiment identities**.
It does **not** launch models, pay for compute, open or reserve GitHub issues,
verify a proof, accept a result or change the Solved/outcomes ledgers.

## Reproduce the first milestone

```sh
python3 scripts/fleet.py --count 100 --check
python3 scripts/fleet.py --count 100 --json > /tmp/fleet-plan.json
python3 scripts/fleet.py --count 10000 --check
python3 -m unittest discover -s tests -p 'test_fleet.py' -v
```

Default work ordering is the first 100 packets from `scripts/scale.py`, followed
by all other runnable items from `scripts/work.py`. Source-bound scope digests,
deliverables, acceptance criteria and falsifiers are **carried through**.
Externally blocked, dependency-blocked and stop-range items are refused.
Every runnable work item gets one attempt before repeats. Repeated attempts
reference the same issue claim title, never an independent new claim.

`--json` emits a planning snapshot with the derived source digest,
per-experiment SHA-256 identity and resource envelopes. Snapshot the JSON file
for a real campaign before running anything. If the source queue or scope
changes, regenerate the plan and treat it as a different experiment batch.
Use a **new campaign slug** for independent batches; never silently reuse
an identity for another attempt.

## Budgets are ceilings, not consumption

Per-slot defaults mirror the **planning caps** of the existing matched-budget
pilot: 45,000 model tokens, 120 tool calls and 3,600 wall seconds.
With 10,000 slots the *hypothetical* envelope is 450 million tokens,
1.2 million tool calls and 36 million wall seconds **summed across jobs**.
These are *not* measured usage, dollars, a sequential duration or a forecast.
The Python `plan(..., total_caps=...)` API also fails closed when any sum
of slot maxima exceeds a caller-supplied aggregate budget. CLI cap flags
can lower the per-experiment ceilings.

## Run ledger and proof status

The initial `data/experiments/runs.jsonl` is empty intentionally; dry-run
plans do not write synthetic results. When a real executor is available,
each observed completed/error/timeout attempt must be appended as a unique
JSONL record with these exact fields:

- `protocol`, `experiment_id`, `work_id`, `scope_sha256`, `attempt`,
  `campaign`, `status`, `classification`
- `resources` and `resource_caps`, each containing `model_tokens`,
  `tool_calls` and `elapsed_seconds` as nonnegative/positive integers
- `evidence`: null for no-result, or relative existing paths named
  `artifact`, `checker_log`, `scope_audit` for submitted work.

An identity is SHA-256 of canonical JSON containing `protocol`, `campaign`,
`work_id`, `scope_sha256`, and `attempt`. Validation rejects duplicated
identities, forged digest strings, unsafe or missing evidence paths, over-budget
resource records, and proof claims attached to failed runs.

Permitted classifications are `none`, `known_reproduction` and
`restricted_unreviewed`. **Externally reviewed or solved is not a fleet
classification**. Any mathematical acceptance must pass the independent
review system (`scripts/outcomes.py`), existing evidence/Lean gates and
the separate Solved promotion rules. A path existing on disk is *not* a
checker replay or an authenticated external review.

The ledger is source-controlled, but this first stage does not yet provide an
append-only write service, verify the authenticity of reported costs or check
that model tools were actually run. It validates schema and consistency only.

## Gate before real execution

1. Run the existing [matched-budget 36-cell pilot](../../benchmarks/PROTOCOL.md);
   its trial ledger and results are separate from the fleet dry run.
2. Implement an executor with claim locking, source snapshot pinning, explicit
   per-run spending enforcement, isolated worker roles and independent replay.
3. Measure novelty-gated accepted results per total effort **before** scaling.
   Compare against sequential and best-of-k baselines, with failures included.
4. Only then progressively authorize 100, 1,000 and 10,000 *real* runs.

No unreviewed mathematical result should enter `data/solved.json`.
