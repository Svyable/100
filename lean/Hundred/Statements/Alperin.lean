import Hundred.Statements.Basic

/-!
# M048 — Alperin weight conjecture

**Registry statement.** For every finite group `G` and every prime `p` dividing
`|G|`, the number of conjugacy classes of Alperin `p`-weights equals the number
of `p`-regular conjugacy classes of `G`.

**What is encoded.** A finite group is represented by its order together with two
functions of `p` (Alperin-weight count and `p`-regular class count). The
conjecture is the pointwise equality of those counts for every prime dividing the
order. Concrete character-theoretic constructions are *not* formalized here; the
Python lab checks named groups through A5 by an independent path.

**Not encoded.** Defect groups, Brauer characters, block induction, or any
infinite family beyond the abstract equality.
**Frontier:** published computational verification for every group of order at
most 100; the lab reproduces classical named groups only.
-/

namespace Hundred.Statements.Alperin
open Hundred.Statements

/-- Order plus the two counting functions the conjecture equates. -/
structure FiniteGroupData where
  order : Nat
  alperinWeights : Nat → Nat
  pRegularClasses : Nat → Nat

/-- `G` satisfies Alperin's equality at every prime dividing `|G|`. -/
def SatisfiesAlperin (G : FiniteGroupData) : Prop :=
  ∀ p, 2 ≤ p → G.order % p = 0 → G.alperinWeights p = G.pRegularClasses p

/-- The registry statement. -/
def Statement : Prop := ∀ G : FiniteGroupData, SatisfiesAlperin G

/-- Cyclic group of order 2: one 2-regular class and one Alperin 2-weight. -/
def C2 : FiniteGroupData where
  order := 2
  alperinWeights := fun _ => 1
  pRegularClasses := fun _ => 1

/-! Fidelity: the classical C2 / p = 2 counts match as Nat equalities. -/
example : C2.order = 2 := by decide +kernel
example : C2.alperinWeights 2 = C2.pRegularClasses 2 := by decide +kernel
example : C2.order % 2 = 0 := by decide +kernel

end Hundred.Statements.Alperin
