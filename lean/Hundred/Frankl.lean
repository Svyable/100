import Hundred.Basic

/-!
# M075 — Frankl's union-closed sets conjecture

**Registry statement.** Every finite union-closed family of finite sets containing
at least one nonempty set has an element lying in at least half of its members.

**What is encoded.** Every finite family of finite sets is isomorphic to one on a
ground set `{0, …, k-1}`. A set is a bitmask `s < 2^k`; a family is a bitmask
`F < 2^(2^k)` whose bit `s` says whether `s` is a member. "At least half" is
`2 · #{S ∈ F : x ∈ S} ≥ |F|`, so no rationals are needed.

**Not encoded.** The best constant (currently about `0.38`, Gilmer 2022 and
successors). **Frontier:** verified for ground sets of size ≤ 12 and families
of size ≤ 57 (literature).
-/

namespace Hundred.Frankl
open Hundred

/-- `s` is a member of the family `F`. -/
abbrev Mem (F s : Nat) : Bool := F.testBit s

/-- Number of members of `F` (over ground set size `k`). -/
def size (k F : Nat) : Nat := countBelow (2 ^ k) (fun s => Mem F s)

/-- Number of members of `F` containing the element `x`. -/
def degree (k F x : Nat) : Nat := countBelow (2 ^ k) (fun s => Mem F s && s.testBit x)

abbrev UnionClosed (k F : Nat) : Prop :=
  ∀ s, s < 2 ^ k → ∀ t, t < 2 ^ k → Mem F s = true → Mem F t = true → Mem F (s ||| t) = true

abbrev HasNonemptyMember (k F : Nat) : Prop :=
  ∃ s, s < 2 ^ k ∧ Mem F s = true ∧ s ≠ 0

abbrev Abundant (k F : Nat) : Prop :=
  ∃ x, x < k ∧ size k F ≤ 2 * degree k F x

/-- The registry statement, for every ground-set size `k`. -/
def Statement : Prop :=
  ∀ k F, F < 2 ^ (2 ^ k) → UnionClosed k F → HasNonemptyMember k F → Abundant k F

/-- The statement restricted to ground sets of size exactly `k`. -/
abbrev OnGroundSet (k : Nat) : Prop :=
  ∀ F, F < 2 ^ (2 ^ k) → UnionClosed k F → HasNonemptyMember k F → Abundant k F

/-- **Kernel-checked exhaustively:** all 2, 16 and 256 families on ground sets of size 1, 2, 3. -/
theorem ground_1 : OnGroundSet 1 := by decide +kernel
theorem ground_2 : OnGroundSet 2 := by decide +kernel
theorem ground_3 : OnGroundSet 3 := by decide +kernel

/-! Fidelity: `{∅, {0}, {1}, {0,1}}` is union-closed and abundant; `{{0}, {1}}` is not union-closed. -/
example : UnionClosed 2 0b1111 ∧ Abundant 2 0b1111 := by decide
example : ¬ UnionClosed 2 0b0110 := by decide

end Hundred.Frankl
