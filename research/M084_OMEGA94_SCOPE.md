# M084 — November 24, 2026 matrix exponent intake

Claim [#403](https://github.com/Svyable/100/issues/403), X-M084-OMEGA94-SCOPE; scope SHA-256 5241b81c21d6bd7ea9ae9c62864eb9587b54b6be37f01cb7a254e7fc1e3a7e99. Author-side audit, 2026-11-25. No registry change.

## Primary records

[Release commit](https://github.com/openai/math/commit/92b516ef8e2abf66c3db7aa31438d3010bc7956f); [inspected revision](https://github.com/openai/math/commit/3344da59991ed94f9ba711217b29c1d760badfa6).
- [Introduction](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/preprints/The-matrix-multiplication-exponent-is-nine-fourths-November-24-2026/build/intro.tex), blob 82b36d928a495e72a27fd6bb666443e802d8fd5b.
- [Obstruction](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/preprints/The-matrix-multiplication-exponent-is-nine-fourths-November-24-2026/build/obstruction.tex), blob e817b4580eb69a590234ddd2dc50982d366e6939.
- [Tensor geometry companion](https://github.com/openai/math/tree/3344da59991ed94f9ba711217b29c1d760badfa6/preprints/Euclidean-geometry-in-the-asymptotic-spectrum-of-tensors-November-24-2026).
- [Lean scope](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/lean/docs/107.md), blob 0007f291d081b9c9011cef37a0585778a44e2952.
- [Proof module](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/lean/OAI/LinearAlgebra/SpectralBooks/ExactExponent.lean), blob c0a1bc6519c86e87e9672b3cdf7b8e766acd3a37.
- [Comparator](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/lean/ComparatorChallenges/MatrixExponent.lean).

## Scope

M084 asks whether omega=2 without specifying the field or formal versus pointwise model. The paper claims omega_F=9/4 for formal rational-function arithmetic circuits over every field, including a finite nonscalar multiplication/division gate lower bound ceil(n^(9/4)/2). The author-described Lean theorem uses division-free polynomial identities, and the comparator contains sorry stubs; the distinct proof module composes formalOmega_square_eq_omega with MatrixExponent.omega_eq. A dependency and axiom audit, kernel replay and bridge from division-free to rational circuits remain necessary. If accepted and scope-equivalent, the answer to M084 is negative. No conclusion about Boolean algorithms, finite-field pointwise-only correctness or wall-clock performance.

The lower-bound argument uses batched distinctness tensor-network volume, conditional compression, iteration maintaining size and batch hypotheses, then bilinearization and finite-field specialization. Audit each interface including uniformity, field assumptions, and companion geometry. Earlier upper-bound sources not independently audited. The paper introduction bounds dual exponent between 1/2 and 2/3; the broader Lean scope claims exactly 1/2 and an exact rectangular formula; do not conflate.

## Executed bounded controls

Python 3.13.5, isolated directory, exact committed blob identities script e0324d4e4a317e7a13ddc7dfc08a820f8369f895 and test 0518bb6cad5e14058e8889b90e08a95c859e2438. Commands:

    python3 scripts/m084_omega94_audit.py
    python3 -m unittest discover -s tests -v

Observed: 216 ordered positive triples, 16 dual samples, four of four mutants rejected (square coefficient, plateau, permutation, homogeneity); three tests passed in 0.045 s. Exact rational formula consistency only; no proof replay, speed benchmark or independent acceptance. Positive weights only.

## Follow-up (unexecuted)

Independent Lean dependency and axiom audit; exact paper scope audit including finite-field specialization and uniform batch lower bound; O-M084-01 and V-P-M084 published tensor decomposition replay and checker review (verify distinct authorship); separately scoped practical benchmarking with hardware, field, timings and logs; S-M084 and F-M084 formal comparator and registry status review under existing claim protocol.

Full checkout failed DNS; full regen, full suite, outcome closure and review pending. Keep draft; no generated file hand-edited.
