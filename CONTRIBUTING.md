# Contributing to 100

The goal is not to collect plausible conjectures or dramatic claims.
It is to maintain **100 exact, high-value proof/counterexample targets** and
produce **independently checkable advances**.

## Ways to contribute

1. **Status correction** — supply the precise theorem statement, a dated primary
   source, and explain whether it proves or refutes *the exact full conjecture*.
2. **New lemma** — state all hypotheses and dependencies, give a complete proof
   or a trusted finite certificate, and identify the remaining unrestricted gap.
3. **Executable evidence** — supply exact inputs, the verifier, expected outputs,
   resource usage, and a reproducing command. No unverifiable solver verdicts.
4. **New candidate** — propose replacing a resolved, duplicated or weak
   candidate; preserve stable IDs and history. Do not silently exceed 100.
5. **Exact probe** — add a module to `scripts/probes/` (search plus an *independent*
   checker, ideally on an existing engine), register it, add tamper tests, and wire it to a
   campaign and `reproduced_known` milestone. See "Add a probe" in [LAB.md](LAB.md). Every
   computable problem now has a probe ([the roadmap](data/engine_roadmap.json) is empty), so
   the highest-value probes push an existing campaign's `next_experiment` past known ranges.
6. **Pages improvements** — submit accessible changes in `docs/`, keep all
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
python3 scripts/lab.py
python3 scripts/build_site.py
python3 scripts/rank.py --check
python3 scripts/research.py --check
python3 scripts/lab.py --check
python3 scripts/build_site.py --check
node --check docs/assets/app.js
python3 -m unittest discover -s tests -v
```

Only edit `data/problems.json`, `data/research_program.json`, `data/engine_roadmap.json`
and source code; `RANKED.md`, `ATTACK_QUEUE.md`, `LAB.md`, `data/lab_results.json` and
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
