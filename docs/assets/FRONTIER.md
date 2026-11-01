# Evidence-first proof frontier and agent handoff

This is a progressive enhancement of the existing **100** static Pages site.
It is not a Gödel agent runtime, theorem prover, research scheduler, claim issuer,
or evidence-promotion service.

## What is added

- Every active problem page gets a small **proof frontier** derived from its
  existing rendered formal statement, milestones, and work-item status. The
  expandable dependency list reads the committed, schema-controlled
  `/api/work.json` queue and exposes only declared dependency edges.
- Each individual work-item page offers a **copyable Markdown handoff** built
  from the canonical work queue: the exact deliverable, source, digest,
  acceptance criteria, known boundary, falsifier, prerequisites, and
  reproducibility requirements. A blocked or waiting item explicitly says
  **NOT READY TO DISPATCH**.
- Every new surface uses `textContent` for ledger data, avoids external scripts,
  preserves the original HTML if JavaScript is disabled or the API fetch fails,
  and inherits the site's light/dark/reduced-motion styling.

The queue is deliberately **read only**. Creating an issue, assigning agents,
accepting a review, changing evidence states, or claiming a proof always uses
the existing repository protocol rather than a browser-side action.

## Verification

```sh
node --check docs/assets/app.js
node --check docs/assets/frontier.js
node --test tests/test_frontier.cjs
python3 scripts/build_site.py --check
python3 -m unittest discover -s tests -v
```

Open `/problems/M075/` or `/problems/M095/` for examples with actual proof
and Lean obligations; open `/work/L002/` to export an agent handoff. The JSON
queue is deliberately loaded **only on opening** a dependency panel or packet
so normal page loads stay lightweight.

## Next experimental gate (not yet implemented)

Evaluate a Gödel-style iterative proof-search agent against the repository's
pre-registered `benchmarks/PROTOCOL.md`. The **agent may vary** tactics,
prompt templates, decomposition and reusable lemmas. It **may not change** the
pinned Lean checker, its axioms gate, the problem statements, the independent
review identity requirements, the novelty gate or the Solved promotion schema.

1. Select one runnable, unclaimed proof/Lean task, preferably an M075 or M095
   bounded lemma, and freeze its scope digest.
2. Measure matched-budget baseline and experimental attempts on held-out
   tasks; preserve time/cost/tool invocations, exact inputs, errors, failures,
   generated proofs and hashes.
3. Replay claimed proof artifacts through pinned Lean/independent checkers.
   A passing kernel check is not proof of statement fidelity or novelty.
4. Route scope and novelty through external independent review, and record
   accepted work separately from new restricted theorems and full resolution.
5. Promote only *verified* improvements to agent strategies, not to the
   trusted checking or evidence-promotion logic.

The useful outcome is **independently accepted, reusable mathematical work per
unit effort**, not the number of generated lemmas, messages, agents or open PRs.
