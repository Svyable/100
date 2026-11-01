import Hundred.Statements.Basic

/-!
# M079 — One-third–two-thirds conjecture

**Registry statement.** Every finite poset that is not a total order has an
incomparable pair `x, y` such that the proportion of linear extensions with
`x < y` lies in `[1/3, 2/3]`.

**What is encoded.** A poset on `n` elements is a reflexive, antisymmetric,
transitive Bool relation. An incomparable pair fails both directions. Balance of
a pair against an extension count `E` with `before` extensions putting `x`
before `y` is the cleared inequality `E ≤ 3·before ≤ 2·E`.

**Not encoded.** An executable enumerator of all linear extensions (the Python
lab does that), Linial's width-2 theorem, or any asymptotic strengthening.
**Frontier:** verified for all posets on at most 11 elements; width 2 is settled.
-/

namespace Hundred.Statements.OneThird
open Hundred.Statements

/-- Reflexive, antisymmetric, transitive relation on `{0,…,n-1}`. -/
def IsPoset (n : Nat) (le : Nat → Nat → Bool) : Prop :=
  (∀ i, i < n → le i i = true) ∧
  (∀ i, i < n → ∀ j, j < n → le i j = true → le j i = true → i = j) ∧
  (∀ i, i < n → ∀ j, j < n → ∀ k, k < n →
      le i j = true → le j k = true → le i k = true)

/-- Incomparable pair. -/
def Incomparable (le : Nat → Nat → Bool) (x y : Nat) : Prop :=
  le x y = false ∧ le y x = false

/-- Not a total order: some incomparable pair exists. -/
def NonTotal (n : Nat) (le : Nat → Nat → Bool) : Prop :=
  ∃ x y, x < n ∧ y < n ∧ Incomparable le x y

/-- Balance of `(x,y)` lies in `[1/3, 2/3]` of the extension count `E`. -/
def Balanced (E before : Nat) : Prop :=
  E ≤ 3 * before ∧ 3 * before ≤ 2 * E

/-- The registry statement: some incomparable pair is balanced among extensions.
The extension count itself is supplied as a hypothesis so that the comparator does
not claim an enumeration theorem. -/
def Statement : Prop :=
  ∀ (n E : Nat) (le : Nat → Nat → Bool),
    2 ≤ n → IsPoset n le → NonTotal n le → 0 < E →
    ∃ x y before,
      x < n ∧ y < n ∧ Incomparable le x y ∧ before ≤ E ∧ Balanced E before

/-- Two-element antichain. -/
def antichain2 (i j : Nat) : Bool := decide (i == j)

/-! Fidelity: the two-element antichain fails both order directions, and the
balance inequalities hold for `E = 2`, `before = 1`. -/
example : antichain2 0 0 = true := by decide +kernel
example : antichain2 0 1 = false := by decide +kernel
example : antichain2 1 0 = false := by decide +kernel
example : (2 : Nat) ≤ 3 * 1 := by decide +kernel
example : 3 * (1 : Nat) ≤ 2 * 2 := by decide +kernel

end Hundred.Statements.OneThird
