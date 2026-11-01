# Discovery trails: preserving the reasoning, not promoting claims

The `/discovery/` section is a **motivated proof-discovery notebook**, inspired by the broad
idea that a mathematical argument should preserve *why* each move was attempted,
not just its final statement. It is not an endorsement or contribution by Timothy Gowers.

The source is [`data/discovery_trails.json`](../data/discovery_trails.json).
The deterministic renderer is [`scripts/sitegen.py`](../scripts/sitegen.py);
[`scripts/discovery.py`](../scripts/discovery.py) validates every trail and reference.

## What belongs in a trail

A trail belongs to one existing stable `M###` problem. Each step must contain:

- A stable, lowercase node ID and an accurate `kind`:
  `observation`, `strategy`, `reproduction`, `blocker`, or `next_step`.
- A narrowly scoped title and factual description (not generic motivational prose).
- A `status`: `documented`, `reproduced_known`, `proposed`, or `blocked`.
  `reproduced_known` is valid only for reproduction nodes; it means known
  mathematical evidence or a known finite check was reproduced, **not new discovery**.
- A nonempty `sources` list of checked-in repository paths. The validator checks
  that every path exists and refuses traversal or absolute paths; cited documents
  still require human scrutiny for scientific fidelity.
- `motivated_by` IDs of earlier nodes in the *same* trail, making a reproducible,
  acyclic dependency graph. The first observation may have no dependencies.
- Optionally, a `move_id` from the shared method vocabulary and an
  `obligation_id` registered for the same problem in
  [`data/proof_obligations.json`](../data/proof_obligations.json).

A trail should state the falsification/acceptance boundary in prose and link the
specific report or certificate that motivates each claim. New moves should improve
the ability to reuse actual mathematics, not encourage duplicated brute-force runs.

## What this deliberately does *not* mean

A discovery node is **not** an independently accepted theorem, a Lean proof,
a completed proof obligation, a probability of success, or a contributor vote.
No discovery status writes to `data/solved.json`, changes registry
`evidence_state`, advances readiness or discharges an obligation. Those gates are
specified in [`docs/RESEARCH_PROTOCOL.md`](RESEARCH_PROTOCOL.md),
[`docs/PROOF_EXCHANGE.md`](PROOF_EXCHANGE.md) and [`LEAN.md`](../LEAN.md).

For a new finite claim, identify the precise proposition, prior art, explicit
witness/input, reproducible checker, independent review and remaining gap. When
no finite object is available, say so and preserve the alternative specialist
review path instead of inventing a witness.

## Contribute and verify

1. Choose one existing work item or proof obligation; follow
   [`AGENTS.md`](../AGENTS.md) to claim it before duplicating work.
2. Add or revise a **small** trail, with links to checked-in primary research
   notes and the exact conditions that would refute the proposed next step.
3. Run `python3 scripts/discovery.py --check` to validate sources, dependencies
   and referenced obligations.
4. Run `python3 scripts/regen.py` and `python3 scripts/regen.py --check --fast`
   to regenerate the `/discovery/` pages, per-problem cross-links,
   command palette entries and static JSON API, then
   `python3 -m unittest discover -s tests -v`.
5. Report whether anything was **independently accepted** under the separate
   research protocol. Do not mistake a rendered step for acceptance.

The JSON endpoints are `/api/discovery.json` and
`/api/discovery/M075.json` (replace ID with a registered trail).
Every problem dossier's API embeds its trail when one exists. The pages work
with JavaScript disabled, including links between motivations and source records.
