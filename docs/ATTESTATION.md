# Mechanical attestations — making independent review cheap

**Status: mechanical pre-review evidence. Not an independent review, an acceptance, or a result about any untested range.**

## Why this exists

The repository's yield is the number of work items accepted by an independent reviewer, per agent-hour ([YIELD.md](../YIELD.md)). At the time of writing, 0 items had been accepted, 47 `review` items were open and nobody had acted as an independent reviewer. That makes review the bottleneck. More workers ([docs/ROUTER.md](ROUTER.md), [SCALE.md](../SCALE.md)) only add to the queue in front of it.

This follows the principle behind DeepSeek's superagent prototype: a person is needed only where a machine cannot decide. A campaign-verifier review (`V-P-<problem>`) asks for three things:

| Part of the review | Who can do it | Lane |
|---|---|---|
| Rerun the verifier and pin the certificate | Machine | `scripts/attest.py`: replay |
| Corrupt the input and certificate; confirm the checker rejects every corruption | Machine | `scripts/attest.py`: controls and mutants |
| Decide whether a surviving corruption is an equivalent valid certificate or a checker gap | Person, using a short list | Survivor triage |
| Compare the finite scope with the cited published boundary | Person | Scope audit |

The machine parts run before any reviewer is involved. The reviewer then starts from a short list of survivors and a scope question, not from a codebase. Mechanical evidence can never be recorded as `accepted_independent`. The rules in [AGENTS.md](../AGENTS.md) and [docs/RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) are unchanged.

## What is checked

For every allowlisted probe in `scripts/probes/` (the `search` / `check` / `scope` contract), at a given level:

1. **Replay.** `search` must reproduce the `certificate_sha256` committed in `data/lab_results.json`, and `check` must accept it. A mismatch makes the probe `broken`.
2. **Mandatory negative controls.** Flipping `holds` and emptying the certificate must both be rejected. A probe whose checker accepts either one is `weak`. The probe contract requires a confirmed counterexample whenever `holds` is false, so a checker that ignores `holds` does not bind the verdict it publishes.
3. **Summary binding.** Every leaf of the published `summary` (up to 48 per probe) is mutated once. `summary` is copied into `data/lab_results.json` and the Pages portfolio. A surviving mutant means that published number is not checked.
4. **Certificate mutants.** Seeded, structure-aware corruptions of the certificate: integer and fraction nudges, boolean flips, and dropping, duplicating or swapping list entries. A survivor may be an equivalent valid certificate (for example a reordered edge set) or a real gap. Only a person can decide which.

Each mutant runs with an alarm-based timeout that a broad `except Exception` in a checker cannot swallow. A rejection by a non-`ProbeFailure` exception counts as rejected and is tallied as `crashed`: the run is fail-closed, but the error is untyped. The seed comes from the probe id, the level and the seed version, so a rerun reproduces exactly.

Status per probe: `clean`, `triage` (survivors to classify), `weak` (a mandatory control survived) or `broken` (no replay).

## Commands

~~~sh
python3 scripts/attest.py                            # all probes (~6 min plus dirichlet_l), writes data/attestations.json
python3 scripts/attest.py --probe ramsey_witnesses   # one probe
python3 scripts/attest.py --probe dirichlet_l --mutants 4   # slow checker, smaller budget
python3 scripts/attest.py --check                    # rerun with each probe's recorded budget; fail on drift
python3 scripts/attest.py --render                   # Markdown table, marks probes whose code changed since
~~~

The weekly research workflow runs `--check`. When a probe's code changes, its attestation goes stale. Rerun the tool and review the diff in the same PR as the probe change.

## How a reviewer uses it

1. Read the probe's record in `data/attestations.json`: replay, tally and survivors.
2. For each survivor, classify it as an equivalent certificate or a checker gap. File a checker gap as `gap_reported` against the review item, with the mutant path as the falsifier.
3. Do the scope-versus-source audit. This is the only open-ended part of the review.

A `weak` or `unbound_summary` flag is already a concrete answer to the `V-P` falsifier "a tampered certificate passes". It should be fixed in the probe as its own claimed work item before any acceptance of that verifier.

## Boundaries

- No probe, ledger entry, fidelity flag, evidence state or Solved entry is changed by this tool.
- A `clean` status means only that the sampled corruptions were rejected. It is not proof that the checker is complete, and it never extends the finite scope.
- The tool is the author's instrument, not an independent reviewer. Independence is still structural (someone else, a public link).
