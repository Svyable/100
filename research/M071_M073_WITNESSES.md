# M071 / M073 — claimed finite-witness extractability audit

**Audited:** 2026-10-31. **Issue:** [#13](https://github.com/Svyable/100/issues/13). **Parent triage:** [CLAIM_REVIEWS_2026.md](CLAIM_REVIEWS_2026.md). **Frozen ledger:** [`data/claim_witness_replay.json`](../data/claim_witness_replay.json).

This note records what can be independently reconstructed from the pinned OpenAI math release (`openai/math@4eaee87548250b2682affda7d05d947c05554bae`) and what cannot. It does **not** accept either manuscript, promote either ID to `resolved`, or touch [`data/solved.json`](../data/solved.json).

## Commands

```sh
python3 scripts/verify_claim_witnesses.py --check
python3 -m unittest discover -s tests -p 'test_verify_claim_witnesses.py' -v
```

## M073 — Sidorenko pattern reconstructed; host missing

**Pinned source.** Comparator statement [`SidorenkoCounterexample.lean`](https://github.com/openai/math/blob/4eaee87548250b2682affda7d05d947c05554bae/lean/ComparatorChallenges/SidorenkoCounterexample.lean) (SHA-256 `489688f5…87de9`) and scope note [`lean/docs/161.md`](https://github.com/openai/math/blob/4eaee87548250b2682affda7d05d947c05554bae/lean/docs/161.md).

**What is explicit.** Table `faces : Fin 22 → Finset (Fin 13)` lists twenty-two triples. The pattern `H` is the bipartite incidence graph of those triples: 13 point vertices, 22 face vertices, and three edges per face.

**Independent reconstruction.** [`data/reference/sidorenko_faces.json`](../data/reference/sidorenko_faces.json) freezes that table. `scripts/verify_claim_witnesses.py` rebuilds the edge list and, separately, recounts edges from point/face degree sums. Both paths give **35 vertices and 66 edges**, every face degree 3, and a connected incidence graph. A tiny-host sanity check (`n ≤ 2`) confirms the homomorphism engine accepts the encoding and that Sidorenko still holds on those hosts; `n^13` map enumeration makes a lab-style census of this `H` infeasible, and that is recorded rather than faked.

**What is not published.** The comparator theorem is existential:

> `∃ n > 0, ∃ host : SimpleGraph (Fin n), (host has an edge) ∧ t(H, host) < (edgeDensity host)^66`.

The upstream `RandomHost` development samples a finite simple graph from a symmetric counter-kernel and proves that for all sufficiently large `n` the expectation gap forces some concrete bitstring to work. **No adjacency list, graph6 string, or numeric order `n` is shipped.** Without that object, this repository cannot replay a finite Sidorenko counterexample outside Lean.

**Status recorded:** `pattern_reconstructed_host_missing`. Evidence state stays `claim_needs_review` / `formal_statement_check_only`.

## M071 — Hadwiger construction is existential; no finite graph

**Pinned source.** Comparator [`HadwigerCounterexample.lean`](https://github.com/openai/math/blob/4eaee87548250b2682affda7d05d947c05554bae/lean/ComparatorChallenges/HadwigerCounterexample.lean) (SHA-256 `83f9f9c4…06b898`) and scope note [`lean/docs/157.md`](https://github.com/openai/math/blob/4eaee87548250b2682affda7d05d947c05554bae/lean/docs/157.md).

**What the Lean statement asserts.** For every `M` there exists `m ≥ max(M, 5)` and a graph on `Fin m` with independence number at most 2, touching-matching number `< m/100`, and

`h(G) < 26m/75 + 2/3 < m/2 ≤ χ(G)`.

The ordinary chromatic form of Hadwiger is therefore the formalized claim; the paper's fractional strengthening is outside the selected comparator statement.

**Why there is no finite witness here.** The construction is a binary-frame / sampled-graph argument with analytic parameters. Upstream `ParameterExistence` seeds `birthG = 10^9+1`. That is an existence family, not a listed adjacency matrix. Xie’s survey of the release likewise notes that the argument supplies neither an explicit graph nor an explicit clique-minor number. [EdouardBonnet/hadwiger-counterexample](https://github.com/EdouardBonnet/hadwiger-counterexample) reports a local kernel replay of the vendored construction (`lax-342547`); that remains Lean proof-object checking and does not yield a portable finite certificate for this repository’s graph engines.

**Status recorded:** `no_explicit_finite_graph`. Evidence state stays `claim_needs_review` / `formal_statement_check_only`.

## What would close the witness-replay gate

| ID | Missing object | Independent check required |
|---|---|---|
| M073 | Explicit host `G` (order `n`, edges) | Exact `hom(H,G)` and `e(G)` with `t(H,G) < t(K₂,G)^66`, plus a second recount |
| M071 | Explicit finite `G` | Proper colouring lower bound (or fractional certificate) and a clique-minor / touching-matching upper bound, each checked outside the author Lean tree |

Comparator acceptance, a second Lean kernel replay, or a survey description is not that gate. Specialist mathematical review of the existential proofs is a separate track from finite-witness replay.

## Regression

CI runs `python3 scripts/verify_claim_witnesses.py --check`. Tampering with the pinned faces table, dropping the host/graph gap flags, or drifting the frozen ledger fails closed.
