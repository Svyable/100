# M075 — Frankl's union-closed sets conjecture

**Docket date: 2026-10-30.** Status: the unrestricted 1/2 assertion is not established by the cited progress papers. Some unrelated announcements claim full proofs; these need independent specialist examination before any status change.

## Exact statement

For every **finite** nonempty family F of **distinct** finite sets closed under taking the union of any two members, if at least one member is nonempty, does there exist an element appearing in at least |F|/2 members?

Be careful with the quantifiers: verifying all families on a fixed ground-set size is a finite theorem, not a proof for all ground sets.

## Mathematical frontier

- [Alweiss–Huang–Sellke, Electronic Journal of Combinatorics 2024](https://doi.org/10.37236/12232) proved the universal lower bound (3 - sqrt(5))/2 ≈ 0.381966.
- [Costa–Sadhu, arXiv:2610.02295, October 2026](https://arxiv.org/abs/2610.02295) report an improved bound of 0.3828852549667978 via entropy inequalities. This remains a preprint, and 0.382885... is **below** 1/2.
- Further complete-proof announcements require proof-by-proof review; numerical bounds and limited-height results do not establish the conjecture.

## Exact certificate and finite benchmark

```sh
python3 scripts/union_closed.py check examples/FRANKL_SMALL.json
python3 scripts/union_closed.py exhaustive --n 4
python3 -m unittest discover -s tests -v
```

A certificate declares a universe {0,...,n-1} and enumerates every distinct set as a list of element indices. The checker verifies union-closure by evaluating all ordered pairs, then counts exact element frequencies. It rejects duplicate sets, invalid elements and trivial families.

The exhaustive command considers **all 2^(2^n) possible families** for n≤4 and filters the nontrivial union-closed ones. Any hypothetical counterexample would terminate the run with an explicit family. Passing the test proves only the **restricted** n≤4 statement; no new result is claimed.

## Closure-pruned canonical orbit generator (2026-10-31)

[Exact construction and mathematical proof](M075_CANONICAL.md) and
[standalone checker](../scripts/frankl_canonical.py) make the previously
informal S5 symmetry step executable.

- Proves algebraically that the lexicographically least relabeling is constant on and separates every S_n orbit; unlike a finite-only test, the group-action argument works for any finite n.
- Gives a closure-preserving, descending-size include/exclude generator. It enumerates full-support union-closed families **without examining every possible set system**, and a canonical filter emits precisely one representative per orbit.
- Reproduces 4,542 labeled full-support families and 330 orbits at n=4, reconciling with 4,958 labeled families and 366 orbits over all possible supports.
- Reproduces **2,747,402 labeled full-support families at n=5**, agreeing with the pre-existing entry in [OEIS A326906](https://oeis.org/A326906). The n=5 orbit total is deliberately **not** claimed checked.
- The 2006 published small-ground-set results already cover n=5. This is infrastructure, not a new restricted theorem or proof of Frankl's conjecture.

```sh
python3 scripts/frankl_canonical.py --check
python3 scripts/frankl_canonical.py --n 5 --limit 30
```

The next frontier is a **canonical augmentation** that prunes relabeling-equivalent *partial states* before exploring them. Obtain independent mathematical scope review of the two lemmas; a full n=5 orbit audit and an n≥10 structural target would be separate work.

## Possible next proof steps

1. Analyze minimal counterexamples under reductions in the contemporary literature; precisely distinguish 'ground-set size' from 'family height'.
2. Implement exact extremal enumeration modulo permutations of the ground set, with an isomorphism checker, before attempting n=5 or larger.
3. Test entropy inequalities with rational/interval bounds, recording which proof protocols cannot reach 1/2. A barrier for a restricted proof method is **not** a counterexample to Frankl.
4. Formulate and independently source-check a small lemma on a restricted family class before running automated proof search.

## Integrity requirements

A successful finite test is not evidence for the unrestricted conjecture beyond its tested scope. An unreviewed internet proof claim is not a verified resolution. Store original papers, assumptions, executable inputs and exact claims before changing status.
