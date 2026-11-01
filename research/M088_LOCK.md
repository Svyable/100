# M088 — locked restricted circuit class

**Status:** class lock only. No hitting set is claimed. No readiness change.
This paragraph discharges the *specification* half of `O-M088-01` /
`J-algebraic_complexity-lock_restriction`. The lemma half (a deterministic
hitting set for the locked class) and an independent falsifier remain open.

## Lock (one paragraph)

Work over the field **GF(2)** (characteristic 2). Circuits are straight-line
programs whose gates are binary **addition** (`XOR`) or **multiplication**
(`AND`) on bits, with at most **20 gates**, syntactic **degree at most 3**
(each multiplication multiplies the sum of the degrees of its inputs; inputs
have degree 1), and a single output gate. The evaluation model is a
**black-box oracle**: a proposed hitting set is a finite list of input
assignments in `GF(2)^n` with `n ≤ 8`, and a circuit is judged nonzero if the
oracle returns a nonzero value at any listed point. Constant circuits and
circuits that ignore some inputs are allowed. No extension field, no division
gates, no characteristic-zero coefficients, and no circuits outside this size
or degree bound are in scope.

## Falsifier (not yet implemented)

A nonzero circuit in this class that vanishes at every point of a proposed
hitting set. The checker must rebuild the circuit from an explicit gate list
and re-evaluate on an independent code path.

## Prior-art boundary

Black-box PIT is in randomized polynomial time. Deterministic poly-time PIT for
*general* arithmetic circuits remains open and is not claimed by locking this
toy class. A hitting set for the lock would be a restricted lemma, not a
resolution of M088.
