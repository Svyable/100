# M080 — exact GF(2)^4 orbit gate and repeated-basis grid certificate

**Research checkpoint, 2026-11-01.** Work item O-M080-01, bounded [claim #170](https://github.com/Svyable/100/issues/170). **Result:** a complete, replayable finite certificate for all four-row instances with at least two equal underlying bases, plus an exact orbit count for the still-unchecked all-distinct search. This **does not discharge O-M080-01**, solve Rota's basis conjecture, establish a new rank-four case, or demonstrate historical novelty. Outside mathematical review is pending.

## Exact theorem and boundary

Let B1,B2,B3,B4 be bases of F_2^4, where each row is an **unordered set** of four distinct vectors, and equal vectors in different rows are separate **labeled occurrences**.

**Finite restricted theorem (exhaustive certificate).** If at least two of the Bi are equal as sets, there exist permutations of the four vectors within each row such that all four columns are bases of F_2^4.

**Orbit count (exact Burnside calculation).** Fix B1=E, the standard basis, and regard the remaining three rows as an unordered multiset. Under the residual coordinate-permutation action of S4, the 99,137,080 normalized input multisets form exactly **4,141,145 orbits**:

| Multiplicity among B2,B3,B4 | Orbits | Certified here |
|---|---:|---|
| All three equal | 51 | Yes |
| Exactly two equal | 29,956 | Yes |
| All three distinct | **4,111,138** | **No** |
| Total | **4,141,145** | 30,007 orbits |

These counts concern equivalence classes of input instances, not inequivalent solutions or new mathematical theorems. No representative/certificate is supplied for the all-distinct class.

## Proof of the orbit count

There are (16−1)(16−2)(16−4)(16−8)/4! = 840 unordered bases of F_2^4. The action of GL(4,2) sends any ordered first basis to E; its setwise stabilizer is precisely the 24 coordinate-permutation matrices. Permuting rows 2,3,4 changes no existence question, so normalized instances are 3-multisets of the 840 bases, totaling C(842,3)=99,137,080.

For an element g in S4, let c_j(g) count its j-cycles on the 840 bases. A 3-multiset fixed by g is a union of complete orbits with multiplicities constant around each orbit. The coefficient of t^3 in the generating function product_j (1−t^j)^(−c_j) is

    F(g) = C(c1+2,3) + c1*c2 + c3.

Exact action on the 840 rank-four vector sets yields:

| Coordinate cycle type | Number of permutations | c1,c2,c3,c4 on bases | F(g) |
|---|---:|---|---:|
| 1^4 | 1 | 840,0,0,0 | 99,137,080 |
| 2 1^2 | 6 | 48,396,0,0 | 38,608 |
| 2^2 | 3 | 12,414,0,0 | 5,332 |
| 3 1 | 8 | 6,0,278,0 | 334 |
| 4 | 6 | 2,5,0,207 | 14 |

Burnside's lemma gives

    [99,137,080 + 6(38,608) + 3(5,332) + 8(334) + 6(14)] / 24
    = 4,141,145.

For all-equal multisets the fixed count is c1; for exactly-two-equal it is c1(c1−1); for three-distinct it is C(c1,3)+c1*c2+c3. Averaging yields respectively 51, 29,956, and 4,111,138. The independent test derives c2,c3 from fixed points of g^2,g^3, instead of the generator's orbit walks.

## Proof of the repeated-basis finite theorem

Any original four-row instance with a repeated basis can be reordered so that **two of the last three rows are equal**: choose a nonrepeated first row if one exists, and otherwise choose a first row from the other repeated pair. Normalize the first row by an invertible linear map to E. Use the residual S4 to transform the repeated basis to one of its **51** orbit representatives; the fourth row is then some arbitrary one of the **840** bases. Thus the exhaustive search space is exactly 51*840=42,840 representative pairs (B,C), each representing the row collection E,B,B,C.

For each such pair, the generator loops over the 24^2 ordered assignments of the two repeated B-rows. It rejects a pair if any of the four partial columns (e_i,b_i,b'_i) is dependent. For each surviving pair, it computes which of the four C-vectors completes each partial column to a basis and tries all 24 perfect matchings. It found a complete assignment for **every one** of the 42,840 pairs, and records the three row-permutation indices as a **128,520-byte binary certificate**.

A **separate checker** reads the archive, reconstructs all 840 bases and all 51 orbit representatives, and checks **all 171,360 columns** by a Leibniz determinant expansion modulo two. It does **not** use the generator's XOR elimination to accept a witness. The 840-base list is also independently checked against the exact group-order formula. Negative controls include dependent columns, a nonbasis, invalid permutation codes, a truncated archive, and wrong action cycle counts.

**Archive SHA-256:** 6cee3dfcf6e5f9359b69d0e1e9244a37c9dd4cdacfa4d2d7c61e30552e5eb24b

Reproduce from the repository root:

    python3 scripts/m080_repeated.py --check
    python3 -m unittest discover -s tests -p 'test_m080_repeated.py' -v
    # Only to regenerate the committed archive, then compare the digest:
    python3 scripts/m080_repeated.py --write
    python3 scripts/regen.py --check

The certificate is a finite exhaustive proof, conditional on the auditability of the enumerator, orbit coverage and independent checker. It is **not** a Lean kernel proof, DRAT certificate, or specialist-reviewed mathematical proof. In particular, a passed test does not constitute independent acceptance.

## Prior art and failed/remaining avenues

The broad rank-four Rota case has a **2012 unpublished computational proof by M. Cheung** ([primary manuscript](https://educ.jmu.edu/~duceyje/undergrad/2012/mike.pdf)), cited in Alexey Pokrovskiy's 2025 [AMS paper](https://doi.org/10.1090/proc/16581). The DOI belongs to **Pokrovskiy's paper**, not to Cheung's unpublished manuscript. Therefore even a full finite rank-four certificate would not automatically be a new rank-four theorem. The current contribution is a narrower, independently replayable reduction and certificate, not an originality claim. The general problem remains open; see [Montgomery–Sauermann (2025)](https://arxiv.org/abs/2508.05601) and [Chow's three-basis reduction](https://arxiv.org/abs/math/0504367).

**Failed avenue:** Raw enumeration of the 99,137,080 normalized three-multisets repeats equivalent inputs roughly 24-fold. Burnside compression reduces the true search to 4,141,145 orbits, but **does not** by itself supply one canonical representative or a grid for each. The repeated-basis theorem removes only 30,007 of those orbits; **4,111,138 all-distinct orbits remain**. A 42,840-pair finite certificate cannot be extrapolated to those.

**Next falsifier:** Build a canonical representative enumerator for the 4,111,138 all-distinct orbits, with a second orbit-count/uniqueness checker. Then produce a grid for each representative, or an exhaustive nonexistence certificate for a specific one. Verify every column by an independent determinant engine, and compare the full finite claim against Cheung's 2012 corpus before any novelty or O-M080-01 discharge.
