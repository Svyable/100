# Cairn-inspired proof impact

Source: [Cairn, pinned upstream revision](https://github.com/SauersML/Cairn/tree/6d1569de034a1ccc5cdc26880780b21442fe2bed), consulted 2026-11-23. This is an original, dependency-free adaptation of its frontier/impact ideas, not vendored code.

Project 100 already has a validated obligation DAG and GitHub claim protocol. Do not replace them with Cairn's advisory leases or derive mathematical truth from a route declaration.

## Worker workflow

```sh
python3 scripts/proof_impact.py
python3 scripts/proof_impact.py --id O-M044-01 --json
python3 scripts/work.py --id O-M044-01
```

The first two commands read the existing validated ledger. Inspect last-missing prerequisites, unique downstream open obligations and transitive unmet ancestors. Then check the exact work packet and live claims under AGENTS.md before acting. The command does not claim a task or change scheduling scores.

A hypothetical discharge is computed only for runnable obligations. It can make a dependent runnable or reveal an external blocker; it never discharges the dependent. The downstream count is a structural reachability count, not a guarantee of progress. The current graph represents conjunctions, not alternative proof routes, so do not interpret a last-missing prerequisite as logically necessary for every possible proof.

At the pinned Project 100 base (5703a54e036edefc1b38335f078da706f337fa0a), O-M044-01 is the last recorded dependency of O-M049-01, but the latter remains externally blocked even after the hypothetical discharge. O-M075-02 has the analogous pattern. These are ledger observations, not mathematical results.

## Next experiments

1. Pilot explicit alternative routes and scoped refutations on one campaign. Each route needs an exact implication, artifacts, statement digests, and independent acceptance before it contributes to verified closure. Keep candidate and verified graph views distinct.
2. Add before/after graph previews and compact context packets, including failed attempts, scope, falsifiers and reusable established claims. Preserve invalidated routes as historical evidence rather than deleting them.
3. Evaluate duplicate warnings against labeled positive and negative examples (especially negation, changed quantifiers and restricted domains). Never merge claims automatically.
4. Measure independently accepted outcomes per agent-hour, dead-end revisits and false warning rates on a pinned cohort before altering fleet scheduling. Do not treat graph growth as mathematical yield.

No new theorem, evidence-state change, independent acceptance or solved-state update is asserted.
