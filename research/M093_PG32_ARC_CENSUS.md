# M093: exact binary projective 4-arc baseline

**Scope:** PG(3,2) only. Known finite mathematics, not a new MDS bound, a proof of the MDS conjecture, or a discharge of O-M093-01. Claim: [#325](https://github.com/Svyable/100/issues/325). Scope digest: `6043c0a3c92b19171160bad828d8ba28c105f70f76066c8c69d08a84a15ade43`.

## Statement and exact representation

The 15 points of PG(3,2) have unique nonzero 4-bit representatives. A 4-arc here is a set of points for which **every four** representatives are linearly independent over GF(2); this is the projective generator-matrix condition for a binary linear [n,4] MDS code. This is *not* the cap condition (no three collinear). For 4-, 5- and 6-point subsets the exact census is respectively **840, 168, 0**.

The checker enumerates all `C(15,4)=1365`, `C(15,5)=3003`, and `C(15,6)=5005` subsets, and all four-subsets of each candidate. It compares two independent exact paths for every candidate: XOR Gaussian rank and the 24-term determinant modulo two. A standard-basis 4-arc and the five-point parity-extension arc are positive controls; a four-vector linear dependency is a negative control.

## Analytic upper bound and sanity checks

If six points formed a 4-arc, choose any four as a basis. A fifth point must have every basis coordinate nonzero: otherwise it lies in the span of three basis vectors. Over GF(2), that forces the fifth point to be the sum of all four basis vectors. The sixth point must satisfy the same condition, so it coincides with the fifth, contradiction. The five-point example `{1,2,4,8,15}` meets the condition. Thus the maximum size in PG(3,2) is five. The enumeration independently supplies exact counts, not the upper-bound proof.

## Reproduction

```sh
python3 scripts/pg32_arc_census.py
# PG(3,2) 4-arc census: {4: 840, 5: 168, 6: 0}
# Two exact checkers agree on every subset; controls passed.
```

Executed with local Python on 2026-11-11; the output above was observed. No random seeds, floating-point arithmetic, external packages or downloaded inputs. Repository-wide regeneration, unit tests and CI were **not** executed locally because direct GitHub DNS access was unavailable; CI must establish integration correctness.

**Falsifiers:** any disagreement between rank and determinant on one candidate, a six-point 4-arc, or a failure of the positive/negative controls. This tests only a small finite sanity case and cannot verify the q≤9 PG(3,q) obligation or primary-source fiducials/constructions. For broader MDS context see the repository's M093 obligation in `SCALE.md` and Ball's 2012 prime-field MDS theorem as identified in that obligation; no novelty or independent review is asserted.
