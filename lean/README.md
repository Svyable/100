# The Lean library: how formal statements are built

`lean/` is a dependency-free Lake project (core Lean 4, no Mathlib) holding a
**comparator statement** for each formalised target in the 100: the exact
proposition a proof or counterexample must establish.

```sh
cd lean && lake build             # kernel-checks every statement, example and certificate
python3 ../scripts/formal.py      # catalogue, escape-hatch scan, independent replay
```

Each module (`Hundred/<Name>.lean`) contains:

1. a header naming the registry id, what is encoded, what is **not** encoded, and the frontier;
2. `Statement` (or `Conjecture`), a `Prop`, never proved here;
3. fidelity examples (hand-checked cases must agree, degenerate objects must be rejected,
   axioms must be satisfiable), all proved by `decide`;
4. where possible, kernel-checked finite instances whose witness tables come from the exact
   probe lab. `scripts/formal.py` replays the same tables in Python.

Rules, enforced in CI (`.github/workflows/lean.yml`):

- no `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by`, `extern` or `unsafe`;
- every module is imported by `Hundred.lean` and listed in `data/formalization.json`;
- `#print axioms` for every kernel-checked theorem must not mention `sorryAx`.

Lean checks only what was encoded. A statement is labelled `author_checked` until a
second reviewer compares every definition with a primary source
(`independently_reviewed`). A kernel-checked finite range lies inside known mathematics
and is never progress on the open statement.

This mirrors the comparator-statement idea used by
[openai/math](https://github.com/openai/math/tree/main/lean): statement first, scope
explicit. Here every statement also carries kernel-checked fidelity tests, finite
certificates tied to an independent checker, and a public page per problem.
