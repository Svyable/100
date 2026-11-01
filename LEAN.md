# Lean proof pipeline

The objective is more independently checked, reusable mathematics per unit of effort.
“100x” is an ambition, not a measured speedup or a promise to solve the portfolio.
The implementation has thirteen audited declarations across Ramsey and the two-element
Frankl case. Caccetta–Häggkvist remains queued, not formalized.

## Run the gate

Install [elan](https://github.com/leanprover/elan), then from the repository root:

```sh
python3 scripts/lean_verify.py --validate-only  # Metadata only; not proof verification
python3 scripts/lean_verify.py                # Build, negative cases, axiom audit, evidence
```

Lean is pinned in `lean/lean-toolchain`. The initial core uses Std and has no external
Lake packages; this keeps certificate checking small and reproducible. Add mathlib
when a target needs it, pin a compatible commit and commit the resulting Lake manifest;
remove the manifest ignore then. Do not run unpinned dependency upgrades in CI.

The [Lean proof gate](.github/workflows/lean.yml) runs on every PR and main push.
Its `lean-evidence-<SHA>` artifact records source hashes, compiler version, revision,
working-tree state and transitive axioms for every registered export. No report is
written on failure; old success reports are removed before verification starts.
Use a clean-checkout CI report for review. Local dirty reports are diagnostic only.
The workflow must be configured as a required branch check by a repository administrator
if enforcement against direct merges is desired.

## Separate four questions

1. **Did it compile?** Run the pinned toolchain with warnings as errors on proof sources.
2. **What did it assume?** Audit each exported theorem with `#print axioms`. Only
   `propext`, `Classical.choice`, and `Quot.sound` are allowed. Ordinary `decide`
   reduces in the kernel; native evaluation, custom axioms and `sorryAx` are rejected.
3. **Did we encode the intended mathematics?** A separate reviewer checks domains,
   quantifiers, nonemptiness, distinctness, strict versus weak inequalities and
   conventions. Passing Lean cannot answer this question by itself.
4. **Is it new and does it settle the target?** Review primary literature and the exact
   unrestricted claim. Nothing here automatically changes `data/solved.json`.

See the official [proof validation guide](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)
and [axiom reference](https://lean-lang.org/doc/reference/latest/Axioms/).

## Work in reusable proof obligations

| Priority | Target | Next rigorous deliverable | Remaining gap |
|---|---|---|---|
| 1 | M095 Ramsey | General `(s,t)` clique certificate with a soundness theorem and deterministic witness import | Large search and exact R(5,5) remain open in this project |
| 2 | M075 Frankl | Two-element case implemented; next prove representation completeness and generalize to n elements | Arbitrary ground-set size remains unproved |
| 3 | M074 directed girth | SAT decoding soundness, then encoding completeness and checked UNSAT replay | Solver verdicts and symmetry heuristics are not proofs |

Canonical target contracts: [data/lean_targets.json](data/lean_targets.json).
The C5 encoding is deliberately independent of the Python implementation. Its positive
certificate is accompanied by complete-graph, empty-graph, self-loop and asymmetric-edge
negative cases. The generic `check_sound` theorem proves that every accepted finite checker result
entails the encoded certificate. It does not claim the checker accepts every graph.
The `restrict` theorem is a reusable transport lemma, not another
independent experimental discovery. Seven declarations do not mean six solved problems.

For each target, split work into definitions → semantic equivalence → checker soundness
→ concrete certificate → scope review. Keep the hard mathematics visible rather than
hiding it as an assumption. A conditional theorem is useful only if its missing hypothesis
is explicitly tracked; proving `P → P` never closes the obligation `P`.

## Contribution contract

- Add small modules under `lean/Hundred/`, import them through `Hundred.lean`, and
  register each exported theorem with its stable problem ID and exact remaining gap.
- Use proof search and external SAT/computation as discovery tools. Retain a proof term
  or replayable certificate. A timeout is unknown, never a negative result.
- Keep unsuccessful experiments outside the trusted import root. No admitted lemmas,
  custom axioms, or native computation in accepted exports. Review changes to the gate
  itself as changes to the trust boundary; it is not a sandbox for malicious source.
- Add an invalid nearby case to catch vacuous or weakened formulations, and a downstream
  use that exercises the intended interface. Prefer general soundness once, many
  small certificates afterward.
- PR evidence: source revision, exact declaration, scope comparison, axiom artifact,
  reviewer and novelty citation. Independent review remains pending until actually done.

## Measure the improvement

Track wall time to a clean kernel check, distinct reviewed obligations discharged,
reusable lemmas consumed by another campaign, rejected malformed certificates and
percentage of exports with independent scope review. Establish a baseline before
claiming any throughput multiplier. Do not optimize for generated proof lines, lemma
counts, bounded cases tested, or attempted solver calls.

## Frankl restricted theorem

`Hundred.Frankl.frankl_two` quantifies over all `Fin 16` family masks. If a family
contains a nonempty member and is union-closed, there exists an element of `Fin 2`
whose frequency is at least half the family size. `union_membership` checks that
bitwise union agrees with elementwise membership on all four set masks.

This is an exhaustive restricted theorem, not just one accepted certificate. It is
known elementary mathematics, not a new result. The existing Python enumeration
independently covers the same 16 masks. `small` replays the meaning of
`examples/FRANKL_SMALL.json` (mask 3); the input file is not dynamically imported
into Lean. A change to that fixture requires a fresh encoding comparison.

Remaining formal gap: prove the representation correspondence from arbitrary
extensional families of subsets of `Fin 2` to the bitmask encoding. The current
statement explicitly quantifies over masks. Neither this finite theorem nor its
sample application proves the conjecture for arbitrary finite universes. The
independent scope-review and novelty gates remain unchanged.
