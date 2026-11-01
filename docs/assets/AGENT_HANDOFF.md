# Agent-ready handoff for 100

This extension complements the existing proof frontier on problem, homepage and atlas pages. It does not replace that explorer or alter any source evidence.

On individual `/work/<ID>/` pages, open **Agent-ready handoff** to read a source-bound Markdown work packet generated from `api/work.json` on demand. The packet preserves the ledger's scope SHA-256, deliverable, prior-art boundary, falsifier, acceptance checks, dependencies, and claim links. It explicitly marks tasks that are not runnable as **NOT READY TO DISPATCH**.

Nothing is automatically claimed, executed, merged, verified or promoted. A SHA-256 digest is an identity guard, not a proof. Agent output must still pass the independent scope/novelty/reviewer requirements in `AGENTS.md`, `LEAN.md`, and `docs/PROOF_EXCHANGE.md`.

## Validation

```sh
node --check docs/assets/handoff.js
node --test tests/test_handoff.cjs
python3 scripts/build_site.py --check
python3 -m unittest discover -s tests -v
```

The static work page remains complete when scripts are disabled or the API cannot load. The handoff requests only same-origin `api/work.json`, and ledger-derived data is inserted as text, not HTML.

## A safe Gödel-style experiment

The next research step is not automatic proof promotion: compare iterative proof-search strategies against the preregistered matched-budget baseline in `benchmarks/PROTOCOL.md`. Allow the search agent to vary decomposition and tactics, but **do not** allow it to modify the Lean kernel, problem statement, evidence or Solved promotion gates. Measure independently accepted and reusable work per compute cost, preserve failed attempts, and submit any claimed novel result to separate mathematical review.
