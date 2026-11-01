# K42 certificate calibration — actual checker run

This is **not** one of the planned 36 agent-architecture trials.

The checked evidence in [k42_checker.json](k42_checker.json) was generated
by executing `python3 scripts/k42_calibration.py --record` on an
authorized development machine. Its machine-agnostic facts are replayed
on GitHub Actions with:

```sh
python3 scripts/k42_calibration.py --check
python3 -m unittest discover -s tests -p 'test_k42_calibration.py' -v
```

What actually happened:

- All **328** distinct published, SHA-256-pinned graph6 records on **42**
  vertices were accepted by two different exact monochromatic K5 checkers:
  recursive bitset search, and triangle/common-neighbor search.
- A deliberate flip of edge **(0,2)** in catalog record 0 produced a red
  K5 on vertices **(0,2,5,6,9)**. Both checkers rejected the mutant.
- The real pinned catalog replay refused a tampered byte file at its SHA-256
  guard. This validates *source integrity*, not a new mathematical theorem.
- The recorded wall time and two checker times are raw **local measurements**
  of certificate verification on one machine. They are not model token cost,
  research productivity, wall-clock comparisons between agent architectures,
  or evidence of any 100x improvement.
- Verification replays mathematical checks and pins source-file hashes.
  Runtime duration is a historical observation, so CI checks its validity
  without expecting identical timing.

**Mathematical boundary:** This is a reproduction of the established
`R(5,5) >= 43` lower bound. The code does not certify `R(5,5) = 43`,
completeness of any graph catalog, or any new Ramsey lower bound.

**Trial boundary:** The preregistered `data/benchmark_runs.jsonl` ledger
remains separate. No `arm` or `seed` is assigned to this baseline and
none of its 656 checker passes can be counted as 656 agent attempts.

## Benchmark validity notice

A new problem arose *after* the frozen pilot manifest: public repository
PRs [#60](https://github.com/Svyable/100/pull/60) and
[#70](https://github.com/Svyable/100/pull/70) now contain author-derived
proofs for the **full finite (24,8)** Caccetta–Häggkvist case (not the
unrestricted conjecture, and not independently specialist-reviewed). External
computational work already addressed that finite case.

Therefore `CH24-IRREGULAR` in the original pilot is **not a clean held-out
discovery benchmark** for an agent reading current main. New results for this
task cannot be credited as novel discoveries in the original 36-cell design;
`scripts/benchmark.py` refuses that promotion. A new, sealed task and new
explicitly versioned preregistration are necessary before an unbiased
three-task novelty comparison. The old manifest and its SHA-256 are retained
for accountability; do not change past protocols after seeing trial outcomes.

**Next:** Execute actual four-arm K42 *agent* calibration under instrumented
shared budgets (including all worker and checker tokens) using pinned model
versions, prompts and unedited logs. Then preregister a replacement for the
contaminated dependency-heavy task *before* any novelty trials. No agent
architecture performance has been measured in this file.
