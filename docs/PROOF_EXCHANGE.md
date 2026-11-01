# Proof exchange: scaling mathematical work without scaling unsupported claims

**Protocol `svyable.proof-exchange.v2` (2026-10-31).** Run:

```sh
python3 scripts/scale.py --budget 100            # 100-slot claimable wave
python3 scripts/scale.py --budget 100 --json     # machine-readable fleet packets
python3 scripts/scale.py --write                 # regenerate SCALE.md
python3 scripts/scale.py --check                 # source + SCALE.md drift
python3 scripts/scale.py --mode coverage --budget 5   # equal-slot shape/engine ablation
```

Nothing here writes to Solved. A filled slot is a **claimable work packet** with a
scope digest, not a theorem.

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

## Operating model: 100 claimable slots

The default wave packs up to **100 distinct items** from the derived
[work queue](../AGENTS.md) (`scripts/work.py`), ranked by a leverage score that
prefers:

1. runnable proof obligations,
2. Lean targets,
3. cohort jobs (shared attack shapes),
4. roadmap now/next items,
5. comparator statements and status-audit drafts.

Dominated `stop_range` jobs and nodes waiting on undischarged dependencies are
**refused**. Each packet carries:

- exact problems, deliverable, acceptance criteria and boundary,
- a SHA-256 scope digest (identity, not validity),
- a claim title and GitHub claim URLs,
- a recommended **scout / adversary / checker** split under that single claim.

Roles are a recommended independence pattern inside one claim, **not** three
votes that a result is true. Two pipelines for the same digest remain the most
expensive failure mode; open a `[Claim]` issue before starting.

The number 100 is an **operating capacity** target aligned with the portfolio
size. It is not a measured speedup, not a promise of 100 theorems, and not a
change to readiness or Solved.

## Coverage ablation (v1 objective, still available)

Let `P` be the 100 active targets and `U` the method shapes plus named engines
in `data/methods.json`. With equal planning slots the greedy maximum-coverage
objective

```
F(S) = | union(C(u) for u in S) |,   |S| <= k
```

is monotone submodular and achieves at least `1 - 1/e` of the optimum for that
*equal-unit-cost coverage* objective. Run it with `--mode coverage`. It says
nothing about theorem probability, tokens or wall-clock time.

## Proof-obligation frontier

`data/proof_obligations.json` is the acceptance DAG. Categories:

- `runnable`: open with all listed prerequisites discharged;
- `externally_blocked`: blocked despite satisfied graph prerequisites;
- `waiting_on_dependencies`: at least one listed prerequisite not discharged;
- `discharged`: structural ledger state, **not** a machine guarantee of truth.

Every active campaign now has at least one obligation node. A waiting or
externally blocked node is never sold as constructive scout work. Changing a
statement or falsifier changes its digest.

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

The source-bound SHA-256 is an anti-drift guard, **not** a signature,
authentication protocol, or proof certificate.

## Experiment needed before calling this a breakthrough

Run a preregistered, held-out comparison across naturally parallel,
high-dependency and mixed-structure tasks, using identical models, total token
budget, tool access, time caps and verification standards:

- A: strong sequential solver;
- B: independent `best-of-k` explorers with no artifact sharing;
- C: unconstrained agent conversation;
- D: proof-exchange wave with source-bound claims, role split and sparse,
  verifier-triggered communication.

Measure **independently accepted new restricted results per unit cost**, not raw
agent messages or target coverage. Record theorem-scope fidelity, checker
replay failures, novel counterexamples, cost, elapsed time and the proportion
of accepted work reused on a second target. Publishing a null result is
preferable to claiming a multiplier from an editorial model.

## Relationship to existing architecture

This layer does **not** replace `scripts/approach.py`, `scripts/work.py`,
`scripts/lab.py`, the Lean gate, the research protocol, or human/specialist
review. It schedules claimable work so many agents can move without duplicating
effort or inventing theorems. See [SCALE.md](../SCALE.md) for the current wave.

Run `python3 scripts/scale.py --check` and
`python3 -m unittest discover -s tests -v` in any workflow that consumes the
packets.
