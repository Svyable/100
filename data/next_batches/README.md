# Next-100 intake batches

Drop a new cohort as `YYYY-MM-label.json` containing an array of candidates.
Each object must follow the Next-100 schema (`N` + ≥4 digits, scores 1–5,
`evidence_state: unvetted_hypothesis`). Prefer **50–100 differentiated**
hypotheses per batch. See [NEXT_100.md](../../NEXT_100.md).

```sh
python3 scripts/next.py
python3 scripts/next.py --check
python3 scripts/next.py --similarity 20
```

Do not auto-promote into the active 100. Promotions require a PR and an entry
in `data/next_promotions.json`.
