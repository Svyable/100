# M092 — exact dimension-four SIC projector replay (known construction)

**Run date:** 2026-11-01. **Work packet:** `O-M092-01` (scope digest
`eaba3c39e8db2ecb`); [claim #112](https://github.com/Svyable/100/issues/112).
**Status:** a bounded **known-result reproduction**, not a discharge of the
dimension-4-through-8 witness obligation, an independently reviewed proof, a
uniform construction, or a new theorem.

## Primary source and scope

Ingemar Bengtsson, [*The Number Behind the Simplest SIC–POVM*,
*Foundations of Physics* **47**, 1031–1041 (2017)](https://doi.org/10.1007/s10701-017-0078-3),
published 8 March 2017, equations (3), (5), (7), (8).
The paper gives a phase table for the **d=4 Weyl–Heisenberg covariant** SIC.
We reproduce its 16 **rank-one projectors** exactly rather than a specific
choice of the normalized fiducial vector. This tests the published
phase/projector construction and the number-field representation. It does not
import fiducials for d=5,6,7,8.

Use `X|j>=|j+1 mod 4>`, `Z|j>=i^j|j>`,
`tau=-(1+i)/sqrt(2)`, `D_ab=tau^(ab) X^a Z^b`.
The paper's phase unit is

`u=(sqrt(5)-1)/(2 sqrt(2)) + i sqrt(sqrt(5)+1)/2`.

Its published 4-by-4 phase table (row a, column b, top-left identity
excluded) is:

```text
       u       -1       1/u
u      1/u     -1/u     1/u
-1     -u      -1       1/u
1/u    u        u        u
```

We reconstruct the projector from the paper's operator-basis identity

`P = (1/4) sum_{a,b} c_ab D_ab^dagger`,
where `c_00=1` and `c_ab=phase_ab/sqrt(5)` otherwise.

## Exact arithmetic and independent control

`python3 scripts/sic_d4_projector.py` uses only the Python standard library,
`fractions.Fraction`, and 16-coordinate exact algebra with generators
`a=sqrt(2)`, `b=sqrt(5)`, `t=i sqrt(1+sqrt(5))`, `i=sqrt(-1)`.
The reduction relations are `a²=2`, `b²=5`, `t²=-(1+b)`,
`i²=-1`; conjugation fixes a,b and negates t,i.
No numerical tolerance, approximate roots, or CAS is involved.
The embedding selects the positive real square roots in the source formula.

**Verified on the frozen published input:**

- The reconstructed 4-by-4 matrix is Hermitian, idempotent, and has trace 1.
- All 16 Weyl–Heisenberg translates are Hermitian, idempotent, trace-1 matrices.
- The 16-by-16 projector Gram matrix has diagonal trace overlap 1 and all
  **120 unordered off-diagonal pairs equal exactly 1/5**.
- A separate displacement-character computation, using only the Weyl
  coefficient norms and fourth-root character sums (no orbit projector
  matrices), independently recovers overlaps 1 and 1/5. This second path is
  not independent *human* mathematical review and is weaker than idempotence.
- Five adversarial tests include altered **unit-modulus** phase data, altered
  nonunit phase data, field identities, conjugation, and displacement unitarity.
  The unit-modulus mutation demonstrates why the character check alone is
  insufficient: it passes the phase-modulus premise but fails projector
  reconstruction.

**Reproduce:**

```sh
python3 scripts/sic_d4_projector.py
python3 -m unittest discover -s tests -p 'test_sic_d4_projector.py' -v
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

Deterministic certificate metadata SHA-256:
`75f2a9bb55798cd0350eaff0e7fbed6e2e22edad1700a7a79d8546af104b4c2d`.
This digest covers the script's fixed output metadata, **not** a source
manuscript PDF or independently audited proof certificate.

## Failure modes and next falsifier

The field arithmetic assumes the exact algebraic embedding selected by the
published radicals; it does not prove an independently extracted fiducial
vector matches a separately distributed source file. The two code paths
share the source phase table, so a common transcription error remains a
possible failure. An outside specialist must check that the phase table and
operator conventions match the primary source. The exact replay does not
establish a uniform SIC family, and does not discharge `O-M092-01`.

**Next falsifier:** import a *separately published, source-hashed* d=5
(or d=6–8) exact fiducial with its full field tower, verify all 25 (or d²)
projectors and every off-diagonal overlap using an independent algorithm,
and include a deliberate one-coordinate perturbation that the checker rejects.
Do not mark the obligation discharged without external mathematical review.
