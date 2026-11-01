# Lamport protocol — make every missing implication explicit

This is a proof-work discipline inspired by Leslie Lamport's insistence on
precise statements, hierarchical proof structure, explicit assumptions and
independently checkable steps. It is **not** a claim that TLA+ model checking
proves mathematical conjectures. The purpose is to multiply the number of
worthwhile conjectures we can **falsify, reduce or prove rigorously per unit of
research effort**, not to multiply agents or finite-search repetitions.

The repository's source of truth remains the 100-problem registry, the research
program, and the strict Solved gate. This protocol adds a **proof-obligation
dependency graph** that is deliberately smaller than the backlog. It does not
replace the shared attack shapes or Lean proof gate being developed separately.

## 1. Start from the missing implication

For each serious attack write an exact target:

- **Statement:** domain, quantifiers, parameters, assumptions and conclusion.
- **Known boundary:** the strongest *applicable* published result; which
  cases or conditions it already covers.
- **Smallest missing implication:** A implies B, with no implicit step between.
- **Falsifier:** a concrete object or failure mode which would refute that
  implication; distinguish a failed search from a mathematical counterexample.
- **Certificate:** what an independent checker could accept, and exactly what
  it would certify.
- **Exit:** the observable artifact that closes the obligation, and the next
  action if it does not close.

Write a hierarchical proof whose children are named obligations, rather than
asking a language model to fill a whole conjecture-sized hole. Every assumption
is scoped where used. A universal statement is never inferred from finite
enumeration unless a separately proved reduction covers the remaining domain.

## 2. The smallest state machine that is useful

The public [Lamport proof map](https://svyable.github.io/100/lamport/) renders this DAG and each node's exact statement, falsifier, boundary, next action and evidence state. A [static JSON projection](https://svyable.github.io/100/api/lamport.json) supports independent reuse. Both are generated from the validated canonical registry; neither is an alternative discharge or Solved gate.

Canonical source: [data/proof_obligations.json](../data/proof_obligations.json).
Structural validator: [scripts/proof_obligations.py](../scripts/proof_obligations.py).

An obligation has an immutable ID, a problem ID, one precise statement, its
prior-art boundary, a falsifier, a next action, dependencies, a kind and a state.

States:

1. **open** — live, falsifiable step; no proof certificate claimed.
2. **blocked** — dependent on an unresolved mathematical or computational
   gate; the next action names what unblocks it.
3. **discharged** — scoped statement has an evidence bundle: a hash binding
   the exact statement, a replayable artifact, the checking implementation, a
   scope audit and two independent review links.

Discharge is permitted only if **every dependency is discharged**. The
dependency graph must be finite, acyclic and refer to valid active campaigns.
Changing a statement invalidates its bound evidence hash. Open and blocked
nodes may not carry discharge evidence. Adding a claimed restricted-verified
milestone requires a discharged **lemma** node in the same campaign.

The validator checks file existence and structural coherence, not proof
semantics, reviewer identity or the mathematical legitimacy of an implication.
A human scope audit and independent mathematical review remain essential.
A discharge can certify only the node's statement; it cannot change the
parent conjecture's open status or enter Solved automatically.

### Safety properties

- **No scope inflation:** computational finite-range evidence never becomes
  a universal theorem by renaming an output.
- **No circular justification:** the proof-obligation graph has no cycles.
- **No dependency laundering:** a discharged node cannot depend on open work.
- **No stale evidence:** certificate hashes bind exact statement text; revision
  requires re-review.
- **No synthetic novelty:** reproductions of published bounds are tagged as
  such in prior-art boundaries, not announced as new results.
- **No self-grading:** search and checker must be independent, and statement
  fidelity is separately audited.

### Progress property

Every non-discharged node has a falsifier and a specific next action. This is
an *operating obligation*, not a liveness theorem that guarantees discovery.
If the next action cannot be executed or no longer separates possibilities,
replace it with a documented blocker or retire the attack.

## 3. One atomic research cycle

1. **Specify.** Fix the exact statement, its quantifier order and dependency
   premises. Compare with the actual source theorem, not a paraphrase.
2. **Split.** Break the target into independent smallest missing implications.
   Flag any new lemma stronger than the original target: it is a gap, not a
   proof step.
3. **Attack in parallel.** A constructor, a counterexample hunter and a
   proof/scope auditor work on the same *versioned* statement. Independence
   means different mechanisms or independently written checkers, not three
   agents repeating the same computation.
4. **Adjudicate.** Record the shortest surviving proof or the smallest
   concrete counterexample. Negative searches get precise bounded scope,
   inputs, budgets and reproducibility; they do not close a universal claim.
5. **Replay.** On a separate path, validate certificate, source assumptions,
   theorem encoding and full dependency closure. Reject on mismatch.
6. **Integrate.** Discharge exactly one verified node; propagate the newly
   available premise to dependent nodes. Keep failed approaches in the
   research note, and route the reusable method to other campaign shapes.

Re-run (1) after **any** significant change of assumptions, graph model,
field, parameter regime or target statement. A shorter proof with a hidden
strengthened hypothesis is not a shorter proof.

## 4. Three live pilots, not three solved problems

| Pilot | Proof gap | Concrete next output | Not a success claim |
|---|---|---|---|
| M074 Caccetta-Häggkvist | Separate published fixed-r=6 UNSAT traces from the completeness of the hand reduction; their conjunction is required | Trace manifest, independent checker replay, numbered quantified reduction audit | Neither trace replay nor an unproved reduction solves unrestricted CH |
| M075 Frankl | Define an S5 orbit-canonical invariant, then prove an exact-once representative generator | Canonicalization lemma, collision falsifier, audited n=5 enumeration | The existing n=4 orbit census is known mathematics |
| M095 Ramsey | Independently review the now-pinned 328-record K42 source and the two exact checkers | Offline replay: 656 colorings including complements; source digest and scope audit | The known lower bound R(5,5) ≥ 43 does not prove the upper bound |
| M048 Alperin | Name a defect-group family outside the order-100 census and state its weight-count lemma | Restricted lemma text with an exact certificate format | The named-group probe through A5 is a known benchmark |

The n=5 Frankl orbit-counting dependency now has a second exact route: [Burnside fixed-point certification](../research/M075_BURNSIDE.md) reproduces the known 28,960 full-support relabeling orbits without individual canonicalization. Neither the new finite calculation nor a paper argument replaces independent mathematical scope review. The live nodes encode these dependencies. Do not dispatch a costly search when
the missing operation is a scope audit, a proof-trace replay or a symbolic lemma.

## 5. Proof throughput, not activity throughput

Measure over each completed campaign interval:

- **Discharged new obligations**, each with exact statement and independent
  review; separate reproduced-known from novel restricted results.
- **Rejected candidate lemmas with certified counterexamples** and saved
  investigator time due to early falsification.
- **Reusable checked methods**, counted by distinct target statements they
  genuinely support, not by number of times a script was run.
- **Gap age and unblocked time:** whether the critical unresolved step is
  shrinking, or whether the research team is accumulating unrelated activity.
- **Verifier cost per useful distinction**, with exact bounds and
  independently replayed artifacts.

The proposal is a 10x *operating objective* for proof-obligation throughput, and
the companion [proof-exchange wave](PROOF_EXCHANGE.md) targets **100 claimable
parallel slots** across the portfolio. Neither number is an achieved theorem
speedup. Test both against the existing baseline. An extra ledger that does not
accelerate verified progress is overhead and should be removed.

## 6. Enforced checks and integration

Run:

    python3 scripts/proof_obligations.py --check
    python3 -m unittest discover -s tests -v

Unit tests tamper with dependency edges, proof hashes and false discharge
states. The ordinary repository validation already runs the entire test suite
for every PR, so this gate runs without modifying or conflicting with a
concurrent Lean workflow change.

For a real discharge, insist on both independently checked proof content and
independent **statement-fidelity** review. A Lean kernel can verify a precise
encoded theorem while that theorem still misses the advertised conjecture.
[Research engine](RESEARCH_ENGINE.md) and [Contributing](../CONTRIBUTING.md)
continue to govern the stronger result-promotion decision.
