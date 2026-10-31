# Proof-driven research engine

This is an **operational research ledger**, not an automated theorem-proving claim.
It separates mathematical ambition, proof readiness, reproducible evidence, and
confirmed full resolutions. Last program update: 2026-10-31.

## The two stack ranks

The existing **editorial ranking** (20–100 points) remains:

- Mathematical impact: 30%
- Attackability: 30%
- Independent verifiability: 25%
- Cross-problem method spillover: 15%

A separate **execution index** adds up to ten *documented readiness* points:

| Evidence of readiness | Bonus | Meaning |
|---|---:|---|
| Exact research campaign brief | +2 | The first proof obligation and falsifier are written |
| Allowlisted independently runnable verifier | +3 | A checking program exists and is tested |
| Reproduced known mathematical benchmark | +2 | Established result independently reproduced; **not novel** |
| Independently reviewed restricted new theorem | +3 | New, carefully scoped partial theorem with two independent reviews |

The execution index is **not** a probability, and high readiness is not
evidence for a general conjecture. Each factor is deliberately bounded to
prevent repeated runs of the same toy case from inflating the rank. The site's
default sort is execution order; the original editorial rank is always available.

- Source registry: [data/problems.json](../data/problems.json)
- Research campaigns / reproducibility milestones:
  [data/research_program.json](../data/research_program.json)
- Generated execution queue: [ATTACK_QUEUE.md](../ATTACK_QUEUE.md)
- Canonical solved archive: [data/solved.json](../data/solved.json)

## Proof work loop (10 operations, not ten speculative agents)

1. Precisely formulate the conjecture with quantified domain.
2. Identify the strongest existing theorems and unresolved residue.
3. Pick the smallest falsifiable restricted statement.
4. Specify exact counterexample and construction certificates.
5. Implement a separate verifier before launching costly search.
6. Reproduce known toy results and measure verifier coverage.
7. Search both for proof lemmas *and* adversarial counterexamples.
8. Preserve exact inputs, scripts, resource usage, and negative results.
9. Require independent mathematical and scope review of any novel claim.
10. Add verified methods to the library and rerank the work queue.

A failed search or an unreviewed manuscript is logged as a research lead, not
a theorem. Mathematical scope review is different from code correctness.

## Three distinct exact verification baselines

```sh
python3 scripts/ramsey.py demo
python3 scripts/union_closed.py exhaustive --n 4
python3 scripts/digraph.py exhaustive --n 4
python3 scripts/digraph_orbits.py --n 5
python3 scripts/ch_sat.py cnf --n 18 --r 6 --output /tmp/ch18-6.cnf
```

The first four reproduce **known** statements in finite domains. The fifth command generates a SAT problem encoding only, not a result. They do not resolve
Ramsey R(5,5), Frankl, or Caccetta–Häggkvist in general. Each script is
independently exercised in the test suite and in a weekly GitHub Actions
reproducibility workflow (when Actions scheduling is enabled by GitHub).
The periodic job reruns existing tests—it does **not** research new literature,
discover a lemma, or verify newly published claims on its own.

## Promote a result to Solved

Only a **full** proof or counterexample of the exact archived statement
qualifies. The archive is intentionally empty initially, and may grow only through reviewed full resolutions. Every entry must
include:

1. A stable ID removed from the 100 active candidates (without recycling it).
2. The precise original statement and proved/refuted outcome.
3. A published full proof URL and dated acceptance record.
4. **Two distinct independent external review URLs** with the result checked
   for the same exact theorem scope.
5. Verification notes and a unique new active candidate replacing the solved one.
6. If the prior target had a campaign, move it to the `resolved_archived` stage so its research history remains accessible without entering the active execution queue.

Schema and consistency checks reject entries lacking those references or
whose old ID remains active. These checks cannot replace real specialist
judgment; a maintainer must investigate the independence and correctness
of the cited assessments.

A *restricted new theorem* goes in the milestone ledger, with review evidence,
but cannot enter Solved until the entire conjecture is accepted as resolved.
A reproduced previously known theorem also stays out of Solved.

## Change management

```sh
python3 scripts/rank.py
python3 scripts/research.py
python3 scripts/build_site.py
python3 scripts/rank.py --check
python3 scripts/research.py --check
python3 scripts/build_site.py --check
python3 -m unittest discover -s tests -v
```

Do not hand-edit generated `RANKED.md`, `ATTACK_QUEUE.md` or
`docs/data/portfolio.json`. CI checks all three for consistency.
The site exposes evidence and ranked research priorities, never asserts a
universal proof merely because a finite verifier passed.
