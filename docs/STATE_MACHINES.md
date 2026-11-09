# State-machine inventory and safe evolution

This is a **code-level audit of the stateful interaction and research-control surfaces** in Project 100. It is not a new proof-status source and not an assertion that a running worker fleet exists. Source-of-truth ledgers and generated HTML remain authoritative in their respective domains.

**Decision:** make the highest-friction asynchronous UI transition explicit and test it; preserve already-tested, fail-closed mathematical and reservation transitions. Avoid a repository-wide state-machine framework: a second runtime or ledger would reduce no-JavaScript UX, increase DX maintenance and invite agents to confuse UI state with research evidence.

## Client interaction machines

| Surface and owner | States and transitions (previously implicit unless noted) | Failure / contract | Decision |
| --- | --- | --- | --- |
| Command palette, `docs/assets/app.js` | **Explicit:** `idle → loading → ready` on a valid search index; `loading → error → loading` on a failed request and retry. Independently, dialog `closed ↔ open`. | Focus immediately; show a pending indication; keep typing during load; single-flight fetch; successful index cached; outdated responses cannot repaint a closed or newer dialog; bad JSON and HTTP failures remain errors. | **Hardened** with session guards and `tests/test_palette.cjs`. Static navigation exists without the palette. |
| Problem list filters, `docs/assets/app.js` | Form controls + URL query determine `all / filtered / empty`; sort and checkboxes change the projection, not the data. `input → debounce → render → replaceState`; reset restores defaults. | `q`, field, status, modality, sort, verifier, campaign, Lean filters are shareable. No history entries are pushed. | Retain; test URL restoration, filter combinations, empty state when editing here. Do not create another cached problem ledger. |
| Theme, `docs/assets/app.js` and stylesheet | `system preference` or explicit `dark/light`; click sets `data-theme` and best-effort local storage. | Private browsing may reject storage. Theme is a presentation choice, never evidence. | Retain; future cross-tab/multiple-toggle synchronization is optional, not a prerequisite to the state audit. |
| Copy feedback, `docs/assets/app.js` | `idle → copied → idle` timer, or clipboard failure with no success label. | Clipboard permissions may be absent. Never imply a successful copy before the promise resolves. | Retain; prefer an announced status and timestamp/token guard if new copy controls are added. |
| Next-100 reservoir, `docs/next/app.js` | `loading → ready/error`; filters `available/promoted/all`, domain, stage, order, search; pagination `24 → 48 → …`; `?focus=N…` adjusts filters and opens details. | Remote JSON is a generated snapshot, not a live admission or proof-status system; failed load shows a fallback; unvetted hypotheses must stay labeled unvetted. | Retain; next behavioral priority is restore/filter URL consistency and isolated malformed review-link handling, with tests first. |
| Proof frontier, `docs/assets/frontier.js` | `unmounted → fetching → enhanced` or `fallback` on rejected API requests; atlas family selection `A → B`. | Canonical `api/work.json` and `api/problems.json` are read only; server-rendered dossier is always available. A methodology edge is **not** a proved implication. | Retain progressive enhancement; do not let network error erase primary content. |
| Agent handoff, `docs/assets/handoff.js` | Lazy details `closed → loading → ready/error`, currently represented by `ready` and a cached/retryable `queuePromise`. Clipboard has success/manual-copy states. | Packet binds exact id and `scope_sha256`; blocked work is marked **not runnable**. It creates neither a GitHub claim nor a worker and cannot confer review. | Retain its independent read-only boundary and `tests/test_handoff.cjs`; explicit cancellation guards are a future bounded change, not a reason for a shared framework. |
| Lamport explorer, `docs/assets/lamport.js` | `all ↔ selected problem` from `?problem=`, change event and resize-triggered graph redraw scheduling. | Dependency edges are visual projections of a ledger, not proof-validity votes; all cards remain in HTML with no JS. | Retain; test query/hash navigation before changing URL history behavior. |

## Agent and research control machines

These are **domain state machines**, not UI flags. They already have explicit enums, validators or independent evidence gates. Never collapse them into a generic `complete` boolean.

| Contract / owner | States and permitted meaning | Non-negotiable guard |
| --- | --- | --- |
| Work queue, `scripts/work.py` | `runnable`, `externally_blocked`, `waiting_on_dependencies` are **derived projections** of current source ledgers and dependency graph. A delivered item disappears from the queue. | Do not mutate the generated queue, reuse a stale scope digest, or treat a snapshot as claim ownership. |
| GitHub work claim, `AGENTS.md`, `scripts/router.py` | Unclaimed → one fresh, unique `[Claim]` issue with matching 16/64-hex digest → bounded ticket admission, or refusal. | A complete and fresh open-issues snapshot is mandatory; duplicate, absent or mismatched claims fail closed. Claim issue text is not the worker mandate. |
| Router ticket, `scripts/router.py` | **Already explicit:** `reserved → running/needs_human/ended`; `running → needs_human/ended`; `needs_human → running/ended`; `quarantined → ended`; `ended` terminal. Vanished/duplicate/drifted claims quarantine active tickets. | `reserved`, `running`, `quarantined` occupy slots; `needs_human` releases slot but **not ownership**. Ended tickets never auto-restart. `tests/test_router.py` checks forbidden transitions and capacity. |
| Review backlog admission, `scripts/router.py` and `data/outcomes.json` | Below review-WIP limit → general tasks eligible; at limit → **review-only** reservations. | No unreviewed merged artifact is treated as independently accepted; priority and capacity are not evidence. |
| Proof obligation, `data/proof_obligations.json` / `scripts/proof_obligations.py` / `scripts/scale.py` | `open`, `blocked`, `discharged` with dependency-aware runnable projection. | Recorded discharge requires evidence and independent review; UI completion is never discharge. |
| Work outcome, `scripts/outcomes.py` | `merged_pending_review`, `gap_reported`, `falsified`, `abandoned`, `accepted_independent` are **recorded outcomes**, not a simple linear progression. | Accepted requires separate reviewer, dated evidence link and scope; `new_restricted_result` adds a distinct novelty review. `YIELD.md` is generated. |
| Benchmark trial, `scripts/benchmark.py` | Trial is absent or recorded as `completed`, `timeout`, `error`; classification `none/known_reproduction/restricted_unreviewed/externally_reviewed_restricted` is separate. | Frozen manifest, measured budgets, original logs and explicit eligibility/reviews are required. A calibration or synthetic fixture is not a run. |
| Portfolio proof/evidence, `data/problems.json`, `data/solved.json`, research protocol | Evidence classification, finite/Lean checking, independent review, novelty and whole-conjecture resolution are **distinct dimensions**, not one progress bar. | Solver verdicts, preprints, finite computations, an agent's own review or successful CI never automatically mark a problem solved. |
| Generated publication, `scripts/regen.py` / `scripts/build_site.py` | Editable canonical source → generated snapshots → byte-checked publication. A drifted snapshot is an invalid build, not a competing truth source. | Never hand-edit generated `docs/` pages or API JSON; no-JS HTML must remain usable. |

## Transition design rule (UX + DX + AX)

1. **One owner:** domain state stays in a ledger/validator; temporary view state stays in the browser. Agents consume a current contract and digest, not a UI badge or copied stale snapshot.
2. **Named phases for async boundaries:** use `idle/loading/ready/error` when delayed work, retry or cancellation can race. Make errors visible and retryable, preserve input during waits, and ignore results from an expired dialog session.
3. **No false success:** copied, runnable, reviewed, accepted, proved and solved mean different things. Never promote one to another because a request or check completed.
4. **Progressive enhancement and reversible changes:** keep static HTML and direct links, edit only allowed source assets, and prefer tested local state transitions to a new dependency or central orchestrator.
5. **Contract tests before expanding state:** test success, delay, failure, retry, close/reopen, stale response and untrusted payloads for UI fetches; test scope drift, duplicate claims, forbidden transitions and independent-review gates for backend changes.

## Verification

```sh
node --check docs/assets/app.js
node --test tests/test_palette.cjs tests/test_handoff.cjs
python3 -m unittest discover -s tests -p 'test_frontier_ui.py' -v
python3 -m unittest discover -s tests -p 'test_router.py' -v
python3 scripts/regen.py --check --fast
python3 scripts/regen.py --check
python3 -m unittest discover -s tests -v
```

This audit identifies source-level state surfaces; it does **not** substitute for a cross-browser accessibility run or a live deployment test. The explicit palette transition is intentionally the only application behavior changed in this pass.
