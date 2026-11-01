import Hundred.Basic

/-!
# M071 — Hadwiger's conjecture

**Registry statement.** Every loopless graph with no `K_t` minor is
`(t-1)`-colourable; equivalently `χ(G) ≥ t` forces a `K_t` minor.

**What is encoded.** A `K_t` minor is given by branch sets: `b v = i < t` puts `v`
in branch set `i` (values `≥ t` mean "deleted"). Each branch set is nonempty and
connected, and every two branch sets are joined by an edge. A set is connected
iff no 2-colouring `T` of it splits it without an edge across the split.

**Not encoded.** Fractional, list or odd-minor variants.
**Frontier:** proved for `t ≤ 6` (Robertson–Seymour–Thomas 1993). A 2026
counterexample claim is triaged on the site (`claims/#M071`); OpenAI's Lean
comparator for that claim encodes the chromatic form with `SimpleGraph`.
-/

namespace Hundred.Hadwiger
open Hundred

/-- `col` properly colours the graph with colours `< k`. -/
abbrev ProperColouring (n : Nat) (adj : Nat → Nat → Bool) (k : Nat) (col : Nat → Nat) : Prop :=
  (∀ v, v < n → col v < k) ∧
  (∀ u, u < n → ∀ v, v < n → adj u v = true → col u ≠ col v)

def Colourable (n : Nat) (adj : Nat → Nat → Bool) (k : Nat) : Prop :=
  ∃ col, ProperColouring n adj k col

/-- Branch set `i` of `b` is connected in the graph. -/
def BranchConnected (n : Nat) (adj : Nat → Nat → Bool) (b : Nat → Nat) (i : Nat) : Prop :=
  ∀ T : Nat → Bool,
    (∃ v, v < n ∧ b v = i ∧ T v = true) → (∃ v, v < n ∧ b v = i ∧ T v = false) →
    ∃ u, u < n ∧ ∃ v, v < n ∧ b u = i ∧ b v = i ∧ T u = true ∧ T v = false ∧ adj u v = true

/-- `b` is a model of a `K_t` minor. -/
def IsCliqueMinorModel (n : Nat) (adj : Nat → Nat → Bool) (t : Nat) (b : Nat → Nat) : Prop :=
  (∀ i, i < t → ∃ v, v < n ∧ b v = i) ∧
  (∀ i, i < t → BranchConnected n adj b i) ∧
  (∀ i, i < t → ∀ j, j < t → i ≠ j →
      ∃ u, u < n ∧ ∃ v, v < n ∧ b u = i ∧ b v = j ∧ adj u v = true)

def HasCliqueMinor (n : Nat) (adj : Nat → Nat → Bool) (t : Nat) : Prop :=
  ∃ b, IsCliqueMinorModel n adj t b

/-- The registry statement. -/
def Statement : Prop :=
  ∀ (t n : Nat) (adj : Nat → Nat → Bool), IsGraph n adj →
    HasCliqueMinor n adj t ∨ Colourable n adj (t - 1)

/-- The complete graph on vertices below `n`. -/
def complete (i j : Nat) : Bool := i != j

/-! Fidelity: `K_3` is a graph and is 3-colourable by the identity. -/
example : IsGraph 3 complete := by decide
example : ProperColouring 3 complete 3 (fun v => v) := by decide

end Hundred.Hadwiger
