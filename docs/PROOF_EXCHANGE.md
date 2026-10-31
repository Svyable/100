# Proof exchange: scaling mathematical work without scaling unsupported claims

**Prototype 2026-10-31.** Run `python3 scripts/scale.py --budget 5` for a short plan,
`python3 scripts/scale.py --budget 5 --json` for machine-readable work packets,
and `python3 scripts/scale.py --check` for source/schema validation.
`--unit-type shape` and `--unit-type engine` are ablations. Nothing is written
to the research ledgers by this tool.

## The constraint

Adding parallel reasoning is not the same as increasing accepted discoveries.
Research on multi-agent systems reports large gains for decomposable tasks but
important failure modes for sequential dependencies, correlated errors and
expensive coordination:

- [Google Research, January 2026](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/) finds architecture selection depends strongly on task properties.
- [Nature Machine Intelligence, 2026](https://www.nature.com/articles/s42256-026-01268-y) reports no universal gain from more agents under matched budgets.
- [Anthropic, 2025](https://www.anthropic.com/research/multi-agent-research-system) reports parallel research gains, substantial token cost and the advantage of passing artifact references rather than repeatedly summarizing all work.
- [AutoformBot, 2026](https://ai.meta.com/research/publications/autoformbot-formalizing-mathematics-at-scale/) demonstrates large-scale dependency-aware Lean formalization. That is evidence for engineering feasibility, **not** validation that new open conjectures are solved by scaling agent count.
- [Scaling Discovery through Test-Time Communication, September 2026](https://arxiv.org/abs/2609.21032) finds communicating agents can outperform independent attempts when progress feedback is available, with important compute-dependent exceptions.

We therefore separate two scarce resources: **creative attempts**, which can be
parallelized, and **independent acceptance**, which cannot be asserted by an agent.
Agents exchange *bounded, source-linked contracts*, not truth claims.

## Formal problem

Let `P` be the 100 active registered mathematical targets, and let `U`
contain the 30 method shapes and the engine names explicitly listed in
`data/methods.json`. Each unit `u` has candidate target set `C(u)`.
An engine-to-target link means only that the problem's method names the engine,
**not** that the engine already works on that target.

With a budget `k` of equal *planning slots* the routing objective is

```
F(S) = | union(C(u) for u in S) |,   |S| <= k.
```

The incremental gain is `|C(u) - covered|`; choose the largest, breaking ties
by existing independently checked lab anchors, then stable ID. This is a
deterministic greedy maximum-coverage algorithm. Because union coverage is
monotone submodular, it achieves at least `1 - 1/e` of the optimum coverage
for the **equal-unit-cost coverage objective**. This theorem says nothing about
mathematical probability of success, proof quality, actual labor costs, tokens,
or wall-clock time. The units do not have observed equal costs.

The separate `data/proof_obligations.json` DAG is the acceptance frontier:
- `runnable`: open with all listed prerequisites discharged;
- `externally_blocked`: blocked despite satisfied graph prerequisites;
- `waiting_on_dependencies`: at least one listed prerequisite not discharged;
- `discharged`: structural ledger state, **not** a machine guarantee of truth.

A waiting or externally blocked node is never reported as runnable. For every
selected routing unit, the output includes exact candidate IDs, existing
finite-lab anchors, required certificate, falsifier and a SHA-256 of that
contract. Changing its statement or falsifier changes its digest; receiving
the digest alone verifies **identity**, never mathematical validity.

## Current reproducible readout

Using the repository's 2026-10-31 registers:

| Observable | Value | Boundary |
|---|---:|---|
| Active targets / method shapes | 100 / 30 | Editorial classification only |
| Candidate units | 43 | 30 method shapes + 13 named method engines; not 43 independent proof solvers |
| Targets routed in five equal slots | 33 | Potential target *coverage*, **not** verified results or measured speedup |
| Targets routed in ten equal slots | 58 | Same limit |
| `symmetry_reduction` routing reach | 11 | Only 2 of these targets have existing deep-level lab anchors with that engine |
| Recorded proof obligations | 6 | Three runnable, one externally blocked, two waiting on dependencies |
| New mathematical conjectures solved | 0 | This tool does not alter `data/solved.json` |

The first equal-slot plan is `engine:symmetry_reduction`,
`shape:complexity_barriers`, `shape:galois_representations`,
`engine:exact_lp`, and `shape:harmonic_analysis`. Their candidate
marginal coverages are 11, 6, 6, 5, and 5. These are scheduling hypotheses,
**not** recommendations to claim engine support on every named target.
The number 33 is not a speedup factor: the objective treats unequal research
tasks as one planning slot each.

## Proof-carrying handoff

1. **Scout:** receives the named target, method family, cited prior-art boundary,
   explicit restricted statement and falsifier. Returns an immutable artifact
   or a negative result with exact inputs and resources.
2. **Adversary:** actively searches for missing hypotheses, scope mismatches,
   counterexamples and contamination from already-known results. Their output is
   stored separately, never summarized away by the proposer.
3. **Checker:** replays a witness or proof in an independent code path or proof
   kernel where possible; compares the exact theorem meaning with the source;
   reports what remains unproved. This must not be the same untrusted agent
   asserting that its own output is correct.
4. **Integrator:** adds an independently accepted result to the right local
   ledger only after the project's documented gates, and reevaluates the
   remaining proof-DAG frontier. A method link alone never discharges a node.

The source bound SHA-256 is an anti-drift guard, **not** a signature,
an authentication protocol, or a proof certificate. For a real distributed
network, add authenticated artifact storage, resource limits, trusted replay,
independent attestations and revocation; those are not implemented here.

## Experiment needed before calling this a breakthrough

Run a preregistered, held-out comparison across naturally parallel,
high-dependency and mixed-structure tasks, using identical models, total token
budget, tool access, time caps and verification standards:

- A: strong sequential solver;
- B: independent `best-of-k` explorers with no artifact sharing;
- C: unconstrained agent conversation;
- D: proof-exchange routing with source-bound artifacts and sparse,
  verifier-triggered communication.

Measure **independently accepted new restricted results per unit cost**, not raw
agent messages or target coverage. Record theorem-scope fidelity, checker
replay failures, novel counterexamples, cost, elapsed time and the proportion
of accepted work reused on a second target. Run ablations without the blocker
DAG, without contract hashes and without independent checking. Publishing a
null result is preferable to claiming a multiplier from an editorial model.

## Relationship to existing architecture

This prototype **does not replace** `scripts/approach.py`'s 44 active jobs,
`scripts/lab.py`'s independent exact probes, the six-node proof DAG,
the research protocol, or the human/specialist review gates. It adds a
*cross-problem opportunity index* and machine-readable, source-bound dispatch
packets on top. Routing, working, checking, and promoting remain separate.

Run `python3 -m unittest discover -s tests -v` to include the new source
and adversarial scheduling tests; run `python3 scripts/scale.py --check`
in any workflow that consumes its output.
