# M095 — Ramsey R(5,5): first verifiable campaign

**Status audit, 2026-10-30:** Published bound **43 ≤ R(5,5) ≤ 46**, exact value unknown in the cited primary 2026 paper. No improved bound is claimed by this repository.

Primary: [Angeltveit–McKay, *R(5,5) ≤ 46*, Journal of Graph Theory (2026)](https://doi.org/10.1002/jgt.70029). Their computational proof independently implemented its principal checks. Background: [McKay–Radziszowski, *R(4,5)=25* (1995)](https://doi.org/10.1002/jgt.3190190304).

## Exact statement and two certificate types

R(5,5) is the least n for which **every** two-coloring of the edges of the complete graph K_n contains a monochromatic K_5.

- **Lower-bound advancement:** find an explicit two-coloring of K_43 having neither a red nor blue K_5. A small independent checker verifies the witness and would establish R(5,5) ≥ 44. Such a witness is **not** known here.
- **Upper-bound advancement:** prove that no valid coloring exists on K_45. A UNSAT claim needs a complete exhaustive argument or independently checked proof certificate (e.g. LRAT), not just a solver's output.
- **Exact determination:** requires a matching lower and upper bound.

## Executable baseline (standard library only)

```sh
python3 scripts/ramsey.py check examples/R33_C5.json --red 3 --blue 3
python3 scripts/ramsey.py demo
python3 scripts/ramsey.py cnf --n 6 --red 3 --blue 3 > /tmp/ramsey33.cnf
python3 -m unittest discover -s tests -v
```

The C5 coloring is a valid lower-bound witness for R(3,3) ≥ 6. The `demo` command exhaustively examines all 2^15 = 32,768 labeled K_6 two-colorings and finds none avoiding both kinds of triangles. **This reproduces the already-known theorem R(3,3)=6; it is a reproducibility smoke test, not a new mathematical result.**

Certificate schema `svyable.ramsey.red-edges.v1`: an integer `n` and a list of pairs `[u,v]` with `0 <= u < v < n` enumerating **red** edges. **Every omitted pair is blue**. Duplicate edges and invalid vertices are rejected. Checker reports explicit monochromatic-clique witnesses on failure.

## CNF construction and proof obligation

For every edge e, Boolean variable x_e is true iff the edge is red. For each set of s vertices, include one clause `OR(not x_e)` over their pairs. For each set of t vertices, include one clause `OR(x_e)` over their pairs. Thus satisfying assignments are precisely red-K_s / blue-K_t-free colorings. The encoder writes `C(n,s)+C(n,t)` clauses when both sizes fit; very large outputs require explicit `--force`. It **does not solve** the CNF.

Known structural filter (not a new lemma): using R(4,5)=25, any red/blue K5-free coloring of K_n has at each vertex red degree d satisfying `n-25 <= d <= 24`. Proof: among red neighbors, a red K4 makes a red K5 and a blue K5 is forbidden, so d≤24. The blue-neighbor analog yields n-1-d≤24. For n=45 this narrows degrees to 20–24.

## Next experiments

1. Import a published K_42 lower-bound coloring with a source and verify it independently. Do not manufacture a certificate.
2. Test exactly which smaller restricted degree-sequence families are feasible on K_43; record SAT inputs, compiler, solver, runtime, hashes, and all proof outputs.
3. Reproduce a small portion of the published upper-bound approach before claiming any new exclusion.
4. A solver-reported UNSAT is **not a theorem** until the full encoding and an independent UNSAT proof are validated.
