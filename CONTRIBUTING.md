# Contributing to 100

The goal is not to collect plausible conjectures or dramatic claims.
It is to maintain **100 exact, high-value proof/counterexample targets** and
produce **independently checkable advances**.

The [Next 100 hypothesis reservoir](NEXT_100.md) accepts unvetted, cross-domain\nideas separately from the active 100. A discovery score alone cannot promote an idea.\n\n## Ways to contribute

1. **Status correction** — supply the precise theorem statement, a dated primary
   source, and explain whether it proves or refutes *the exact full conjecture*.
2. **New lemma** — state all hypotheses and dependencies, give a complete proof
   or a trusted finite certificate, and identify the remaining unrestricted gap.
3. **Executable evidence** — supply exact inputs, the verifier, expected outputs,
   resource usage, and a reproducing command. No unverifiable solver verdicts.
4. **New candidate** — first propose an immutable N-ID hypothesis in the [reservoir](NEXT_100.md), with cross-domain consequences and a first falsifiable attack; propose replacing a resolved, duplicated or weak
   candidate; preserve stable IDs and history. Do not silently exceed 100.
5. **Shared attack shape** — extend [data/methods.json](data/methods.json) when several
   problems should move together. A shape is a template, not a theorem. Run
   `python3 scripts/approach.py` and keep the generic "specify a lemma" sentence
   out of the queue. Do not schedule a range extension that the campaign blocker
   already places inside a cited theorem.
6. **Exact probe** — add a module to `scripts/probes/` (search plus an *independent*
   checker, ideally on an existing engine), register it, add tamper tests, and wire it to a
   campaign and `reproduced_known` milestone. See "Add a probe" in [LAB.md](LAB.md). Building
   an engine from [the roadmap](data/engine_roadmap.json) unlocks a whole class of problems.
7. **Pages improvements** — submit accessible changes in `docs/`, keep all
   browser assets local, and use the generated snapshot rather than an
   independently maintained data copy.

## Evidence standard

An arXiv upload, press release, model-generated manuscript, or a proof
assistant transcript **does not alone establish** acceptance of the full claim.
Always compare precise quantifiers, conditions, and the encoded theorem.

- `official_open`: exact target listed open by an official authority.
- `verified_open`: contemporary primary specialist sources verify open remainder.
- `needs_review`: still requires a proper source and scope audit.
- `claim_needs_review`: potentially relevant proof/counterexample claim pending assessment.

Any proposed promotion to verified status should link the primary evidence and
explain why restricted results or recent claim releases do not already settle it.

## Rebuild after any registry change

```sh
python3 scripts/rank.py
python3 scripts/research.py
python3 scripts/approach.py
python3 scripts/lab.py
python3 scripts/mine.py
python3 scripts/build_site.py
python3 scripts/rank.py --check
python3 scripts/research.py --check
python3 scripts/approach.py --check
python3 scripts/lab.py --check
python3 scripts/mine.py --check
python3 scripts/build_site.py --check
node --check docs/assets/app.js\nnode --check docs/next/app.js
python3 -m unittest discover -s tests -v
```

Only edit `data/problems.json`, `data/research_program.json`, `data/engine_roadmap.json`
and source code. The Next 100 canonical records and promotion ledger live in\n`data/next_candidates.json`, `data/next_batches/*.json`, and `data/next_promotions.json`.\n`docs/data/next.json` is generated. `RANKED.md`, `ATTACK_QUEUE.md`, `LAB.md`, `data/lab_results.json` and
`docs/data/portfolio.json` are generated artifacts. CI rejects drift.

## Research contributions checklist

- [ ] Exact claim and quantified domain documented
- [ ] Strongest relevant existing theorem cited and dated
- [ ] New assertion separated from known/reproduced cases
- [ ] Proof checked independently or certificate replayed
- [ ] Failed candidates and applicable resource limits reported
- [ ] Implications for score justified, not inferred from publicity

Use the GitHub issue templates to propose evidence reviews or proof campaigns.
See [research protocol](docs/RESEARCH_PROTOCOL.md),
[source intake](docs/AUDIT_QUEUE.md), and
[Pages guide](docs/PAGES_SETUP.md).
