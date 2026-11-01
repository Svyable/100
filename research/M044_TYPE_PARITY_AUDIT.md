# M044: exact type-parity replay and missing-witness boundary

**Work packet:** \`O-M044-01\` (claim #110; scope digest
\`4f9c55ca7a8b68eb1673e4d122d950255a0def42d2c07e63126f90c698ad17fd\`).
**Outcome:** \`gap_reported\`, not discharged. Checked 2026-11-01.

## Pinned primary source

OpenAI, *A Torsion-Free Group Algebra That Is Not Directly Finite*,
October 4, 2026, [pinned manuscript](https://github.com/openai/math/blob/4eaee87548250b2682affda7d05d947c05554bae/preprints/A-Torsion-Free-Group-Algebra-That-Is-Not-Directly-Finite-October-4-2026/direct-finiteness.pdf)
and its [LaTeX source](https://github.com/openai/math/tree/4eaee87548250b2682affda7d05d947c05554bae/preprints/A-Torsion-Free-Group-Algebra-That-Is-Not-Directly-Finite-October-4-2026/build/sections).
SHA-256 of the raw pinned source files:

| File in \`build/sections/\` | SHA-256 |
|---|---|
| \`algebra.tex\` | \`71fe26eab4e6a01564a687c522bbceb8923182c0201af9685eac84d9f86a141f\` |
| \`random.tex\` | \`bb172b92ba622e262c2bf124e70c3cd55922200083c09db658615759b81323c4\` |
| \`assembly.tex\` | \`3987e23ea7c5c8d217ca539d5a307d59f8eac5b8381a0afe411125e57f0bee4a\` |

The **assembly** section expressly selects an outcome of a conditioned random
matching model instead of enumerating the matching edges. The paper gives a
construction by existence, not a particular edge-labeled pair of graphs.
Consequently it supplies neither a concrete list of cone relators nor concrete
root-to-vertex words for the proposed \`a,b,c\` in \`F_2[G]\`. The abstract
definitions in Proposition "Parity criterion" are **not** a replayable input
file. We cannot truthfully report either exact published-support group-ring
multiplication or an independent witness. This is an *extractability gap*, not
a counterexample to the manuscript's theorem or a proof that no finite
witness exists.

## What was checked exactly

\`python3 scripts/m044_type_audit.py --check\` implements finite field
arithmetic in \`F_2[x]/(x^7+x+1)\` (checking all 127 nonzero elements have
multiplicative inverses), enumerates all \`q^2+q+1 = 16,513\` normalized
projective points and lines for \`q=128\`, and enumerates the
\`16,513 × 129 = 2,130,177\` incidences. Each line has 129 distinct
points and each point lies on 129 lines. For two distinct lines the unique
projective intersection follows from rank two of independent linear forms;
the checker also cross-product-checks deterministic pairs. These are
finite computations and elementary projective geometry, not a review of
the random matching estimates.

The seven complements of the Fano-plane lines have size four, meet
pairwise in two elements, and each of the seven extra letters belongs to
four complements. The ordinary part of two prescribed label sets intersects
in 129 points for the same line, and one for different lines. The extra
part contributes an even intersection except for the distinguished
root with itself, where it contributes seven. Thus the exact parity
hypotheses of Proposition "Parity criterion" hold at the **type** level.

As a small, explicit type-only allocation, take \`m=5\`, put 161 vertices
of each of the seven extra types in distinct line classes in \`A\`, 129
of each in distinct line classes in \`B\`, and place the unique root in
an unused \`A\` line class. There are enough line classes
(\`7×161+1=1,128 < 16,513\` and \`7×129=903 < 16,513\`).
The seven extra letters each occur \`4×161+1=645\` times in \`A\` and
\`4×129=516\` times in \`B\`, exactly matching each ordinary letter's
\`129m=645\` and \`129(m−1)=516\` occurrences. The type allocation has
82,565 \`A\` vertices and 66,052 \`B\` vertices. **No edges were
matched**: \`m=5\` is not asserted to meet the manuscript's asymptotic
girth, spherical-arrangement, root-protection, or torsion-freeness conditions.

The tests reject a modified Fano complement, a duplicated complement,
an invalid residue class for \`m\`, and a reducible polynomial
\`x^7+1\`. The projective census is a different arithmetic path from
the Fano combinatorics; neither is a second group-ring multiplication.

## Precise unverified dependencies

1. An explicit pair of labeled matching graphs with exact roots and a
   verified no-arrangements / root-protection certificate is **absent**.
2. Without that graph, the finite group presentation and the exact
   supports of \`a,b,c\` cannot be extracted for independent word reduction.
3. The manuscript's probabilistic and topological arguments, including
   torsion-freeness and nontriviality of the proposed \`c\`, were **not**
   independently checked here.
4. Therefore \`ab=1\`, \`ac=0\`, \`c≠0\`, \`ba≠1\`, and the M049 nonsoficity
   consequence remain **unverified claims** in this audit. Do not
   change \`data/solved.json\`, claim-review status, or obligation status.

## Next decisive falsifier / replay contract

Obtain a pinned concrete pair \`Γ_A, Γ_B\` with every vertex's signed
outgoing labels, matched endpoint, two roots, and the finite presentation
derived from the cones. Preserve input hashes. Independently check
immersion, all type parities, girth, no forbidden arrangements and
root protection; extract exact path words for the group-ring supports.
Then use **two genuinely distinct** group-ring multiplication/reduction
implementations to test \`ab=1\` and \`ac=0\`, and independently certify
\`c≠0\`. A trace with \`ab≠1\`, \`ba=1\`, a support mismatch, or a
failed root-protection check would be decisive against that particular
candidate. A failed search or a type-only success is **not** a
refutation or verification of the claimed existence theorem.

**Status:** \`O-M044-01\` remains open as a mathematical obligation; the
claim issue for this *bounded attempt* can close with a gap report. No
independent reviewer, theorem, accepted work item, or executed model
benchmark is recorded.
