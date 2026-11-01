import Hundred.Basic

/-!
# M095 — The Ramsey number R(5,5)

**Registry statement.** Determine `R(5,5)`; the conjectured value is 43.

**What is encoded.** A red/blue colouring of the complete graph on `0, …, n-1` is
any `c : Nat → Nat → Bool` read on pairs `i < j` (`true` = red). A monochromatic
`K_s` is a bitmask `S < 2^n` with `s` vertices whose pairs all have one colour.
`Arrows n s t` is the Ramsey property `n → (s, t)`.

**Known.** `¬ Arrows 42 5 5` (Exoo 1989, an explicit colouring) and
`Arrows 46 5 5` (Angeltveit–McKay 2024), so `43 ≤ R(5,5) ≤ 46`. The conjecture is
therefore exactly `Arrows 43 5 5`. Neither known bound is re-proved here.
-/

namespace Hundred.Ramsey
open Hundred

/-- `c` has a clique of size `s` on vertices below `n` in colour `col`. -/
abbrev HasMonoClique (c : Nat → Nat → Bool) (n s : Nat) (col : Bool) : Prop :=
  ∃ S, S < 2 ^ n ∧ popcountBelow n S = s ∧
    ∀ i, i < n → ∀ j, j < n → i < j → S.testBit i = true → S.testBit j = true → c i j = col

/-- The Ramsey property `n → (s, t)`. -/
def Arrows (n s t : Nat) : Prop :=
  ∀ c : Nat → Nat → Bool, HasMonoClique c n s true ∨ HasMonoClique c n t false

/-- The registry conjecture `R(5,5) = 43`, given the known lower bound. -/
def Conjecture : Prop := Arrows 43 5 5

/-- The pentagon colouring: red on the 5-cycle, blue on its complement. -/
def pentagon (i j : Nat) : Bool := (j + 5 - i) % 5 == 1 || (i + 5 - j) % 5 == 1

/-- **Kernel-checked:** `R(3,3) > 5` via the pentagon. -/
theorem not_arrows_5_3_3 : ¬ Arrows 5 3 3 := by
  intro h
  have hr : ¬ HasMonoClique pentagon 5 3 true := by decide +kernel
  have hb : ¬ HasMonoClique pentagon 5 3 false := by decide +kernel
  cases h pentagon with
  | inl x => exact hr x
  | inr x => exact hb x

/-! Fidelity: a 3-clique exists in the all-red colouring of `K_3`. -/
example : HasMonoClique (fun _ _ => true) 3 3 true := by decide

end Hundred.Ramsey
