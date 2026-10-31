# Future Next 100 batches

Add a versioned JSON array such as `2026-11-round-01.json` with records
following [the seed schema](../next_candidates.json). Every candidate gets
a new stable `N` ID, at least two substantive spillover areas, a conditional
consequence and a first falsification or formalization step.

Do not copy active `M` problems or claim a proposed hypothesis is novel or
independently confirmed open. Run `python3 scripts/next.py` and
`python3 scripts/next.py --check` after every batch. The builder reads
all `*.json` files here in deterministic filename order and rejects duplicate
IDs or titles across the seed, all batches and the active 100.

Large future intakes can be split into multiple small reviewable files.
A new batch never changes the capped 100 without an explicit promotion PR.

## Completed intakes

- `2026-10-cohort-02.json`: N0121–N0216, 96 hypotheses across 12 additional
  domains. Schema and lexical screening do **not** establish novelty.
  See `../next_review_queue.json` for twelve bounded first-review briefs.
