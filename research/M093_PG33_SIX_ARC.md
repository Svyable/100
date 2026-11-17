# M093: six-point 4-arcs in PG(3,3) (known finite obstruction)

**Scope.** In projective 3-space over GF(3), a 4-arc is a set of points for which every four representatives are linearly independent. No six-point 4-arc exists, while a five-point 4-arc does. This is elementary, known finite MDS mathematics, **not** a new bound or the full MDS conjecture. Claim: [#379](https://github.com/Svyable/100/issues/379). It does not discharge O-M093-01 (all q through 9), or overlap the PG(3,2) orbit census.

## All-orders-in-this-field proof

Suppose six projective points form a 4-arc. Any four are independent, so apply an invertible change of coordinates to make the first four the standard basis e1,e2,e3,e4. Every coordinate of either remaining representative u or v must be nonzero: replacing any basis vector with that representative must preserve independence. In GF(3), the nonzero values are {1,2}. For every pair of basis vectors replaced by u,v, independence requires the corresponding 2-by-2 minor u_i v_j - u_j v_i to be nonzero. Equivalently the four ratios u_i/v_i must be pairwise distinct. There are only two possible nonzero ratios in GF(3), a contradiction. Conversely the four standard basis points together with (1,1,1,1) form a five-point 4-arc: each of the five possible 4-by-4 determinants is nonzero.

## Exact executable control

`python3 research/m093_pg33_six_arc.py` implements Gaussian-elimination determinants modulo 3 and checks every four-subset. It verifies the five-point witness, enumerates all 8 normalized choices for a fifth point, checks all 28 unordered distinct pairs as potential fifth/sixth points, and finds zero six-arcs. Controls reject a point with a zero coordinate and duplicate points. An independent ratio-count argument cross-checks the 28 rejected pairs. The finite enumeration is redundant to the symbolic proof, not independent external review.

## Boundary and falsifier

A six-point set with all 15 four-by-four minors nonzero would falsify the claim; a disagreement between determinant and ratio checks would falsify the implementation. The argument is specific to GF(3) and 4-arcs; it neither establishes maximum sizes over GF(4) through GF(9) nor resolves O-M093-01. Historical novelty is **not claimed**. Primary baseline: Simeon Ball, *On sets of vectors of a finite vector space in which every subset of basis size is a basis*, JEMS 14 (2012), https://doi.org/10.4171/JEMS/342 (the general prime-field MDS literature); the short proof above is elementary and self-contained.
