# Agent protocol

Instructions for every automated or human contributor working in this repository,
including parallel AI sessions. The goal is many concurrent contributions with no
duplicated work, no broken generated files and no unsupported mathematical claims.

## 1. Pick bounded work

```sh
python3 scripts/work.py --next 5                  # highest-priority runnable items
python3 scripts/work.py --next 5 --kind comparator  # or: obligation, lean, job, roadmap, status_audit
python3 scripts/work.py --id F-M079               # one item: deliverable, acceptance, boundary, digest
python3 scripts/scale.py --budget 100             # 100-slot evidence-bound wave (see SCALE.md)
python3 scripts/scale.py --write                  # also refreshes docs/api/packets.json for fleets
python3 scripts/analogues.py --check              # structural finite-analogue ledger
```

Fleet operator guide: [docs/FLEET.md](docs/FLEET.md). Packets are claimable contracts with
scope digests, not theorems. For a **single-router, claim-gated reservation and
bounded worker-slot prototype**, see [docs/ROUTER.md](docs/ROUTER.md)
(`python3 scripts/router.py --help`). It produces mandates, not running agents;
do not start a worker without rechecking the current GitHub claim and scope.
Site discovery for independent contributors: [start here](https://svyable.github.io/100/start/), [JSON agent contract](https://svyable.github.io/100/api/agent.json), [runnable shortlist](https://svyable.github.io/100/api/agent/tasks.json), and [plain-text guide](https://svyable.github.io/100/llms.txt). These are **generated static snapshots**, not a live reservation/claim service. Always re-check the latest scope digest and current GitHub open claims before taking a task.

The 36 preregistered model/agent benchmark cells are also claimable individually
with python3 scripts/work.py --kind benchmark. These are **unfinished trial
assignments**, not a claim that an agent has run. Do not copy synthetic test
fixtures into the ledger or infer a model trial from the K42 Python calibration.
Each completed, failed or timed-out real run needs original model/tool logs,
prompt and source snapshots, the frozen task/arm/seed and measured combined
resource use. The post-freeze CH24 problem has an explicit novelty-contamination
warning, which a reviewer must not override.

The 20 currently runnable campaign verifiers have separately claimable
V-P-<problem> review packets: independent researchers rerun the exact
certificate, attack the checker with negative controls and audit the scope.
An AI author, unverified self-review or automated replay is never independent
acceptance. Outcome records require a real review by someone else.

The queue is derived from the ledgers (proof obligations, Lean targets, the dispatcher,
the roadmap, the formal catalogue and the status-audit drafts). It is browsable at
`/work/` on the site and machine-readable at `docs/api/work.json`. An item disappears
when its ledger records the result; nobody edits the queue by hand.

The scale wave packs up to 100 claimable slots with scout/adversary/checker role
guidance, refuses dominated `stop_range` jobs, and is **not** a claim that 100
agents produce 100 theorems. Prefer an open obligation or Lean target over a
mass comparator when both are free.

## 2. Claim before you start

Search open issues for the item's claim title, `[Claim] <id>`. If one is open, pick
another item. Otherwise open a claim with `.github/ISSUE_TEMPLATE/claim.yml`, including
the scope digest. Close the claim with the PR that delivers the item, or close it
unfinished with what you learned. Two pipelines for the same thing is the most expensive
failure here; a claim costs one minute.

For independent reviews, acceptance clears only the **same scope digest** from the work queue. A changed reviewed statement or acceptance contract needs a fresh review; an older accepted outcome must never suppress it.

## 3. Do only the deliverable

Meet every acceptance line and respect the item's boundary. A different idea is a new
item (add it to the ledger that should own it), not a wider PR. Keep PRs small: many
small PRs land faster than one large one.

## 4. Regenerate, never hand-merge generated files

```sh
python3 scripts/regen.py                  # rewrite every derived file (~3 s)
python3 scripts/regen.py --check --fast   # quick gate while iterating
python3 scripts/regen.py --check          # full gate (reruns lab probes, ~1 min)
python3 -m unittest discover -s tests     # full test suite
```

`python3 scripts/regen.py --list` prints the generated paths (RANKED.md, ATTACK_QUEUE.md,
LAB.md, MINES.md, APPROACH.md, ROADMAP.md, docs/data/next.json and the generated part
of `docs/`). On a merge conflict in any of them: take either side
(`git checkout --theirs -- <paths>`), run `python3 scripts/regen.py`, then commit.
Never hand-edit `docs/` outside `docs/assets/`, `docs/next/` and `docs/*.md`.

**Sequential ids collide across concurrent PRs** (roadmap `R..`, obligations `O-..`, Lean
targets `L..`): three open PRs once took `R36` at the same time. Before adding one, check
open PRs for the next free id. After merging main, a `duplicate id` failure from a validator
means renumber *your* new entry, never one that is already on main, then regenerate.

## 5. Lean

- New comparator statements go in `lean/Hundred/Statements/`, are imported by
  `lean/Hundred.lean` and catalogued in `data/formalization.json`
  (see [lean/README.md](lean/README.md)).
- Every exported theorem is registered in `data/lean_targets.json` so the Lean proof
  gate audits its axioms ([LEAN.md](LEAN.md)). `python3 scripts/formal.py --check`
  enforces this and forbids `sorry`, `admit`, `axiom`, `native_decide`.
- Keep kernel certificates small: the gate builds everything twice under a 300 s limit
  and prints per-module timings. A certificate that takes minutes belongs in the Python
  lab, with Lean checking a smaller fidelity instance.
- If you cannot run Lean locally, say so in the PR and treat the gate as the first compile.

## 6. Evidence rules (non-negotiable)

- Never mark a problem solved, or change an evidence state, on an announcement, a
  preprint, a solver verdict or a finite computation alone. Follow
  [docs/RESEARCH_PROTOCOL.md](docs/RESEARCH_PROTOCOL.md) and
  [docs/PORTFOLIO_SELECTION.md](docs/PORTFOLIO_SELECTION.md).
- A Lean proof proves only what was encoded; state what was not encoded.
- Finite ranges inside known theorems are reproductions, never progress.
- Independent review is done by someone else; an agent cannot record its own work as
  independently reviewed.

## 7. Ship, and record the outcome

Use the PR template, name the work item id in the title or body, include
`Closes #<claim issue>`, and paste the output of `python3 scripts/regen.py --check`.

Infrastructure-wide cross-problem claims may use a stable `X-...` work id when no derived
work-queue item has that scope; record these separately as infrastructure, not a
new theorem, formal result or independently accepted review.

In the same PR, append one record to `data/outcomes.json`: the item id, the claimed scope
digest, the author, the outcome (`merged_pending_review`, `gap_reported`, `falsified` or
`abandoned`) and honest agent-hours, failed attempts included. Only a reviewer who is not the
author may later record `accepted_independent` (with `accepted_on`). This is what the
repository's yield metric ([YIELD.md](YIELD.md)) is computed from: capacity is filled slots,
yield is independently accepted *work items* per 10 agent-hours. An accepted work item is not
a new theorem; only a separately audited `novelty: new_restricted_result` counts as one.
Independence here is structural (reviewer is not the author, public link), not authenticated
expertise. Review is the bottleneck, so `review` items in the queue (`V-...`) are the
highest-value work for anyone who did not write the artifact.
