# M098 — first-order Vaught conjecture

**Checked:** 2026-10-31. **Registry state:** `verified_open`. **Not a resolution of the infinitary theorem, and not a claim that every later manuscript has been read.**

The active target stays the first-order statement. The October 2026 infinitary counterexample is recorded in the [claim ledger](../data/claim_reviews_2026.json) so it cannot be reused as a closing citation.

## Exact first-order statement

Let `T` be a complete first-order theory in a countable language, with infinite models. Write `I(aleph_0, T)` for the number of models of `T` of size aleph_0, up to isomorphism. Vaught's conjecture, in the form surveyed by Pillay and Tanović, says that `I(aleph_0, T)` is countable or equal to the continuum.

The registered question is that statement. It is not the absolute infinitary form, and it is not a claim about an arbitrary sentence of `L_{omega_1, omega}`.

Under the continuum hypothesis the numerical form is immediate, because the only infinite cardinal at most the continuum is aleph_1. The absolute formulation, which does not follow from the continuum hypothesis, asks that uncountably many countable models yield a perfect set of pairwise non-isomorphic countable models. That absolute form is also first-order when the theory is first-order. This note does not treat the two formulations as the same theorem, and it does not mark either one solved.

**Open-status source:** Anand Pillay and Predrag Tanović, *The number of countable models of first-order theories*, [arXiv:2508.06854](https://arxiv.org/abs/2508.06854), submitted 2025-08-09. The text read on 2026-10-31 still says the first-order conjecture is widely open. It does not discuss arXiv:2610.15217. Morley's theorem is cited there as still the strongest general restriction for an arbitrary first-order theory: the only infinite possibilities are aleph_0, aleph_1, and the continuum.

Special cases already proved, as listed in that survey and in the introduction of the infinitary manuscript, include theories of Boolean algebras, modules over a serial ring, omega-stable theories, superstable theories of finite rank, and o-minimal theories. Those are restricted positive results. They are not a proof of the unrestricted conjecture, and this repository has not replayed them.

## Why arXiv:2610.15217 does not settle M098

Ackerman, Freer, and Knight, *A counterexample to Vaught's Conjecture for L_{omega_1, omega}*, [arXiv:2610.15217](https://arxiv.org/abs/2610.15217), 2026-10-10, claim a sentence of infinitary logic with exactly aleph_1 countable models and no perfect set of non-isomorphic models. Their Theorem 2.27 is stated for a Knight sentence in `L_{omega_1, omega}`. The abstract says this disproves Vaught's conjecture for infinitary logic.

An infinitary sentence is not a complete first-order theory. A correct proof of that theorem would refute the infinitary extension. It would not produce a complete first-order theory with exactly aleph_1 countable models. This repository has not certified the infinitary proof.

Section 1.2 of the same manuscript records that Knight's 2002 announcement of a *first-order* counterexample was not accepted. That older announcement is also not a resolution of M098.

## Formalization limits, pinned

Author repository [cameronfreer/vaught-conjecture-counterexample](https://github.com/cameronfreer/vaught-conjecture-counterexample) at commit [`e9f465e1a6b328788d9bf4691f7887a5f535b41d`](https://github.com/cameronfreer/vaught-conjecture-counterexample/commit/e9f465e1a6b328788d9bf4691f7887a5f535b41d) (2026-10-30). The README at that commit says the development is a counterexample to Vaught's conjecture for `L_{omega_1, omega}`, **not** to the first-order Vaught conjecture. It also says:

- The proved statement is `HasThinAlephOneSpectrum` for `baseLanguage.densitySentence`, an infinitary sentence in a countable relational language.
- The formalization does not cover every claim of the manuscript.
- It does not identify the models of that sentence with the manuscript's class of strongly coded templates.
- The first-order Vaught conjecture is listed as not covered.

The Palomar registration note likewise says the registered formalization is not a first-order counterexample. A Lean check of an infinitary sentence is not acceptance of M098.

## Regression

`tests/test_claim_reviews.py` refuses to treat M098 as resolved while its claim record points at the infinitary manuscript, and it refuses to use that manuscript, or the two author repositories, as the registry `source_url`. The open-status citation has to be the Pillay–Tanović survey.

## Still open

Independent specialist acceptance of the infinitary argument, a first-order proof or counterexample, and any restricted lemma proved in this repository. None of those is claimed here.
