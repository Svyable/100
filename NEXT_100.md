# Next 100 — hypothesis reservoir

**Explore on Pages:** [Next 100](https://svyable.github.io/100/next/) ·
[Active 100](https://svyable.github.io/100/)

Next 100 is the **intake layer** for [the active 100](data/problems.json), not
another claim that 120 (or eventually thousands of) new mathematical theorems
are open. It holds hypothetical statements with potentially consequential
spillovers across multiple fields of mathematics, scientific practice or the
real world. Some are research sketches awaiting exact formalization.
Some may be already proved, false, equivalent to known results, or impossible
under their stated assumptions. **Do not present them as discoveries.**

The first release seeds **120 editorial hypotheses across 15 domains**.
The format and statically paginated browser can grow to thousands without
changing the 100-slot active list. Favor quality over numerical inflation.

## Data architecture

- `data/next_candidates.json`: seed cohort with immutable `N0001` IDs.
- `data/next_batches/*.json`: optional additional arrays of candidates. Use
  a fresh batch per intake round so review diffs remain manageable.
- `data/next_promotions.json`: immutable provenance records mapping an `N`
  candidate into the active `M` slot it eventually replaces.
- `scripts/next.py`: schema, duplicate, promotion and active-cap validator;
  deterministic discovery-priority ranking and static Pages builder.
- `docs/data/next.json`: generated client snapshot, not a source of truth.
- `docs/next/`: searchable Pages explorer with filters, linkable IDs and
  expandable motivations / first attacks.

Run `python3 scripts/next.py` after source edits. Run
`python3 scripts/next.py --check` or `python3 scripts/next.py --top 20`.
CI checks the generated artifact and browser JavaScript syntax.

## Candidate schema and editorial scores

Each record has an immutable `id` (N followed by at least four digits), a
short `title`, a **hypothetical** `statement`, its mathematical `domain`,
at least two concrete `spillovers`, a clear `consequence` conditional on
success, a falsifiable `first_attack`, a `stage`, `evidence_state` and
`scores`. The evidence state must remain `unvetted_hypothesis` at intake.

- `formalize`: substantial definitions, quantifiers or assumptions still needed.
- `prior_art_review`: more concrete statement but literature/status unverified.

Four 1–5 **editorial** scores mirror the active ranking weights: impact 30%,
tractability 30%, independent verifiability 25%, cross-domain transfer 15%.
The discovery index = 6×impact + 6×tractability + 5×verifiability + 3×transfer.
It is **not** a probability of success, novelty, truth or scientific validity.
Ties are broken by stable ID. Promotions do not rewrite historical hypotheses.

## Intake → active 100

1. **Specify.** Define every term, quantifier, exception and objective. State
   a mathematical theorem/counterexample target, rather than an untestable
   statement about future technology. Describe at least two nontrivial ways
   resolving it would matter.
2. **Audit.** Compare current specialist/primary sources and existing
   conjectures. Record dated URLs, exact equivalences and prior counterexamples.
   A missing source is **not** evidence that a problem is open.
3. **Attack.** Identify a restricted lemma, explicit falsifier, finite instance
   generator or independent verifier. Add a reproducible campaign if useful.
4. **Select.** Compare against the weakest/solved/duplicated active slot
   using both long-term significance and runnable proof-work readiness. **No
   automatic displacement from a high discovery index alone.**
5. **Promote via a reviewable GitHub PR.** Replace one active record, maintain
   exactly 100 distinct `M` IDs, record the departing candidate's history
   in the PR, and add a promotion entry with `next_id`, `active_id`,
   `promoted_on`, `review_url`, and a substantive `reason`. The active
   problem must follow the full [research protocol](docs/RESEARCH_PROTOCOL.md)
   (including evidence-state rules). Promoting does not certify a proof.
6. **Check.** Rebuild `RANKED.md`, `ATTACK_QUEUE.md`, lab/research and Pages
   snapshots with existing scripts. Run the full test suite and CI.

Never reuse an `N` ID for another statement. A changed or withdrawn idea
should receive a documented decision, not vanish from the ledger. Retain
the source even when it has been promoted. The Next 100 page preserves a
direct link to the active `M` record once a promotion is logged.

## Adding a batch

Put an array of objects following the existing schema at, for example,
`data/next_batches/2026-11-round-01.json`, with fresh N IDs.
After literature triage and duplicate checks, run:

```sh
python3 scripts/next.py
python3 scripts/next.py --check
node --check docs/next/app.js
python3 -m unittest discover -s tests -v
```

This system is a **reservoir of proposals**, not autonomous paper monitoring or
an automatic conjecture generator. Verification and promotion need documented
research decisions.
