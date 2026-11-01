/-!
# Shared finite vocabulary

Core Lean 4 only (no Mathlib), so every statement in this library can be read
end to end and checked by the kernel with no external dependencies.

Conventions used throughout:

* A finite object on `n` points uses the vertices `0, 1, …, n-1`; quantifiers are
  written `∀ i, i < n → …` so that bounded instances are decidable.
* Graphs and digraphs are adjacency functions `Nat → Nat → Bool`; the hypotheses
  that make them simple (symmetry, no loops) are stated explicitly.
* Every helper is structurally recursive, so `decide` can evaluate it.
-/

namespace Hundred

/-- Number of `i < n` with `p i = true`. -/
def countBelow : Nat → (Nat → Bool) → Nat
  | 0, _ => 0
  | n + 1, p => countBelow n p + (if p n then 1 else 0)

/-- Integer sum of `f i` over `i < n`. -/
def sumBelow : Nat → (Nat → Int) → Int
  | 0, _ => 0
  | n + 1, f => sumBelow n f + f n

/-- `p` is prime: at least 2 and no divisor strictly between 1 and `p`. -/
def IsPrime (p : Nat) : Prop :=
  2 ≤ p ∧ ∀ d, d < p → 2 ≤ d → p % d ≠ 0

instance (p : Nat) : Decidable (IsPrime p) := by
  unfold IsPrime
  exact inferInstance

/-- A simple graph on vertices `0, …, n-1`: symmetric and loopless. -/
def IsGraph (n : Nat) (adj : Nat → Nat → Bool) : Prop :=
  (∀ i, i < n → ∀ j, j < n → adj i j = adj j i) ∧ (∀ i, i < n → adj i i = false)

/-- The vertices of `S` (a bitmask) below `n`, counted. -/
def popcountBelow (n S : Nat) : Nat :=
  countBelow n (fun i => S.testBit i)

/-! ## Fidelity checks for the vocabulary itself -/

example : IsPrime 2 := by decide
example : IsPrime 97 := by decide
example : ¬ IsPrime 1 := by decide
example : ¬ IsPrime 91 := by decide
example : countBelow 10 (fun i => i % 3 == 0) = 4 := by decide
example : popcountBelow 5 0b10110 = 3 := by decide

end Hundred
