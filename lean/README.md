# The Lean library: how formal statements are built

`lean/Hundred/Statements/` holds a **comparator statement** for each formalised
target in the 100: the exact proposition a proof or counterexample must establish.
It lives in the same dependency-free Lake project as the proof pipeline described in
[LEAN.md](../LEAN.md) (core Lean 4, no Mathlib) and passes through the same gate.

```sh
python3 scripts/formal.py --check   # catalogue, escape-hatch scan, independent replay
python3 scripts/lean_verify.py      # needs elan: build, warnings as errors, axiom audit
```

Each module (`Hundred/Statements/<Name>.lean`, namespace `Hundred.Statements.<Name>`) contains:

1. a header naming the registry id, what is encoded, what is **not** encoded, and the frontier;
2. `Statement` (or `Conjecture`), a `Prop`, never proved here;
3. fidelity examples (hand-checked cases must agree, degenerate objects must be rejected,
   axioms must be satisfiable), all proved by `decide`;
4. where possible, kernel-checked finite instances whose witness tables come from the exact
   probe lab. `scripts/formal.py` replays the same tables in Python.

Rules, enforced in CI (the Lean proof gate in `.github/workflows/lean.yml` plus `validate.yml`):

- no `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by`, `extern` or `unsafe`;
- every module is imported by `Hundred.lean` and listed in `data/formalization.json`;
- every kernel-checked theorem is registered in `data/lean_targets.json`, so the gate
  compiles it with warnings as errors and audits its transitive axioms (only `propext`,
  `Classical.choice` and `Quot.sound` are allowed).

Lean checks only what was encoded. A statement is labelled `author_checked` until a
second reviewer compares every definition with a primary source
(`independently_reviewed`). A kernel-checked finite range lies inside known mathematics
and is never progress on the open statement.

This mirrors the comparator-statement idea used by
[openai/math](https://github.com/openai/math/tree/main/lean): statement first, scope
explicit. Here every statement also carries kernel-checked fidelity tests, finite
certificates tied to an independent checker, and a public page per problem.
