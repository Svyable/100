# M093: binary projective 4-arc orbit–stabilizer replay

Claim [#328](https://github.com/Svyable/100/issues/328). Scope: exact projective 4-arcs in PG(3,2) only, using the GL(4,2) action rather than the prior rank/determinant-only census of [#326](https://github.com/Svyable/100/pull/326). Known finite mathematics, no new MDS result or independent mathematical review.

The 15 nonzero vectors of GF(2)^4 are unique representatives of the projective points. The number of ordered bases, hence |GL(4,2)|, is (16−1)(16−2)(16−4)(16−8)=20160. Every invertible transformation preserves independence of every four columns. For the ordered standard basis, the setwise stabilizer is precisely its 24 coordinate permutations. Its orbit therefore has 20160/24=840 four-arcs. Every five-arc consists of a basis and the sum of its four vectors, so the five-set stabilizer permutes the five points and has order 5!=120: any four of the five form a basis, and their fifth is forced as the sum. Hence its orbit has 20160/120=168 five-arcs. All four-arcs are bases, and all five-arcs are images of the standard parity extension, proving transitivity without relying on the exhaustive counts.

`python3 scripts/pg32_orbits.py --check` enumerates all 20160 invertible matrices via ordered independent columns, computes both setwise stabilizers and image orbits, and **separately** enumerates all 4- and 5-subsets satisfying the independence predicate to verify completeness. Exact observed output on 2026-11-11:

```
n=4 orbit=840 stabilizer=24
n=5 orbit=168 stabilizer=120
GL4 order=20160; controls passed
```

Negative controls reject a dependent four-set and verify a singular linear transformation maps an independent basis to a rank-three image. All calculations are integer XOR, no external dependencies or random seeds. This is a distinct group-action cross-check of the already known census, not independent human review. The exhaustive candidate sweep shares a rank predicate with the group-action construction; the orbit-stabilizer proof supplies the separate algebraic justification. The original six-point impossibility argument remains in `research/M093_PG32_ARC_CENSUS.md`; this work does not test q>2 or discharge O-M093-01. Falsifiers: any invertible matrix producing a dependent image, orbit-stabilizer disagreement, or an arc outside the computed orbit.

Primary mathematical basis: classical orbit–stabilizer theorem and elementary linear algebra over GF(2); for MDS scope, see the Ball (2012) prime-field theorem cited in `research/M093_PG3_ARCS.md`. No claim of historical priority.
