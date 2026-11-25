# Cogentic discovery intake — 2026-11-25

Claim [#404](https://github.com/Svyable/100/issues/404). Pinned upstream [4a7bc8ab0bc770e71a259b7966c500496b99010a](https://github.com/google-research/google-research/commit/4a7bc8ab0bc770e71a259b7966c500496b99010a). See [machine-readable ten-paper intake](../data/cogentic_2026_intake.json) for every README and PDF blob identity, date, stated result, scope boundary, proposed task and formalization availability. The six new papers are CC-BY-4.0; older four have the directory's Apache-2.0 notices. No manuscript text or algorithm copied. Source summaries paraphrased.

## Evidence boundary

This is source/README-level intake. PDF identities were inspected through GitHub directory metadata; manuscript proofs have not been read or independently verified. Six November 25 READMEs describe complete Mathlib-only Lean formalizations (three 4.35.0 and three 4.33.0) as forthcoming; pinned directories contain only README and PDF, not Lean source. No kernel replay, independent acceptance, executable implementation of the claimed algorithms, actual speedup or status promotion. Older papers' READMEs make no corresponding Lean assertion. Do not confuse this inventory with acceptance.

## Portfolio decision

M078 explicitly concerns vertex-deleted decks. The edge-deck result is related, not equivalent. The other nine subjects have no exact title/keyword match in the active register or current next_candidates.json; map them to proposed reservoir tracks, not assigned N-IDs. Related M081/M083/M085/M087/M088/M089/M090 links are thematic, not implications. No replacement or new coverage slot is authorized by this intake. Consult all existing work and claims before starting each follow-up. No claim for a follow-up is implied by this document.

## Priority queue (proposals, not executed)

1. Edge reconstruction: obtain full PDF proof, audit deck conventions and density theorem, independently check the min-degree consequence and the exact interface to vertex reconstruction; keep M078 vertex-deck work separate. A synthetic small counterexample cannot touch the theorem's range.
2. Factoring: audit claimed uniform Turing bit-time/space bounds, zero error, deterministic vs expected distinction, conditional prerequisites and the deterministic paper's stated conversion between exponential and L notation. For the nonresidue bound, exp(O(sqrt(log p) loglog p)) does not imply L_p[1/2,O(1)] because the latter has only sqrt(loglog p); check the original theorem and whether there is a separate sharper bound. No practical RSA break follows.
3. Fixed-characteristic DLP: audit asymptotic uniformity, field input and nonmembership certificate; not a result for arbitrary prime fields or elliptic curves.
4. Nash: audit exact 1/5 threshold, encoding length and both unilateral regrets; not a conventional PTAS for arbitrary approximation accuracy.
5. VC compression: audit side-information and reconstruction cost; distinguish polynomial from linear conjecture.
6. Log-rank: inspect proof of KL stability obstruction; improvement in exponent is not the polylog conjecture. Constants and huge rank threshold matter.
7. Fictitious play: replicate exact published rational gadgets, compare concurrent independent arXiv:2610.08768 and tie conventions; do not count novelty twice.
8. Prophet inequalities: check upper/lower bounds under static anonymous pricing only; not all adaptive mechanisms.
9. Convex CE: inspect black-box lower bound and first-order oracle definition; not explicit-input hardness.
10. Cross-cutting Lean release intake: pin each forthcoming toolchain, commit, dependency lock and theorem export; audit assumptions/axioms, independently replay and compare each exact mathematical statement, record failed attempts. No review outcome until independent reviewer.

## Executable checks

Run from root:

    node scripts/cogentic_2026_intake.mjs
    python3 -m unittest discover -s tests -p test_cogentic_2026_intake.py -v

The exact JS function bodies that are committed in the script were executed against the fetched manifest in the author-side JavaScript runtime, yielding 10 papers, 8/8 rejected manifest mutants, first feasible density n=2001, and a nonisomorphic triangle-plus-isolate / three-edge star pair with equal edge decks and unequal vertex decks. The pair is explicitly outside the paper's claimed range. No graph at n<2001 can meet m>=1000n by the simple-graph edge bound. This is a finite scope control, not an in-range reproduction of the theorem. The Node CLI and unittest wrapper have not been run in a full checkout; CI is the first integration run. The controls detect structural and evidence-label errors, not maliciously replaced but well-formed blob IDs; independently re-fetch pinned upstream metadata for those.

## Integration limitation

GitHub local checkout failed DNS. Full regen, repository-wide tests, ledger closure and independent review are pending. Keep this draft open and claim #404 active until the normal AGENTS.md integration steps complete. No generated files hand-edited. No registry or acceptance state changed.
