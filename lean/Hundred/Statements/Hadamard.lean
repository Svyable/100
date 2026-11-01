import Hundred.Statements.Basic

/-!
# M094 — Hadamard matrix conjecture

**Registry statement.** A Hadamard matrix of order `4k` exists for every `k ≥ 1`.

**What is encoded.** An `n × n` matrix over `Int` with entries `±1` whose rows
are pairwise orthogonal (`H Hᵀ = n I`; the diagonal is automatic for `±1` entries).

**Not encoded.** Orders 1 and 2 (trivial), constructions (Sylvester, Paley,
Williamson). **Frontier:** the smallest open order is 668.
-/

namespace Hundred.Statements.Hadamard
open Hundred.Statements

/-- `H` restricted to `0 ≤ i, j < n` is a Hadamard matrix. -/
abbrev IsHadamard (n : Nat) (H : Nat → Nat → Int) : Prop :=
  (∀ i, i < n → ∀ j, j < n → H i j = 1 ∨ H i j = -1) ∧
  (∀ i, i < n → ∀ j, j < n → i ≠ j → sumBelow n (fun k => H i k * H j k) = 0)

/-- The registry statement. -/
def Statement : Prop :=
  ∀ k : Nat, 1 ≤ k → ∃ H : Nat → Nat → Int, IsHadamard (4 * k) H

/-- Parity of the lowest `k` bits of `m`. -/
def parity : Nat → Nat → Bool
  | 0, _ => false
  | k + 1, m => (m % 2 == 1) != parity k (m / 2)

/-- Sylvester's matrix of order `2^k`: entry `(-1)^popcount(i AND j)`. -/
def sylvester (k : Nat) (i j : Nat) : Int :=
  if parity k (i &&& j) then -1 else 1

/-- Paley I matrix of order 12 (from quadratic residues mod 11). -/
def paley12Rows : List (List Int) := [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [-1, 1, 1, -1, 1, 1, 1, -1, -1, -1, 1, -1],
    [-1, -1, 1, 1, -1, 1, 1, 1, -1, -1, -1, 1],
    [-1, 1, -1, 1, 1, -1, 1, 1, 1, -1, -1, -1],
    [-1, -1, 1, -1, 1, 1, -1, 1, 1, 1, -1, -1],
    [-1, -1, -1, 1, -1, 1, 1, -1, 1, 1, 1, -1],
    [-1, -1, -1, -1, 1, -1, 1, 1, -1, 1, 1, 1],
    [-1, 1, -1, -1, -1, 1, -1, 1, 1, -1, 1, 1],
    [-1, 1, 1, -1, -1, -1, 1, -1, 1, 1, -1, 1],
    [-1, 1, 1, 1, -1, -1, -1, 1, -1, 1, 1, -1],
    [-1, -1, 1, 1, 1, -1, -1, -1, 1, -1, 1, 1],
    [-1, 1, -1, 1, 1, 1, -1, -1, -1, 1, -1, 1]]

def paley12 (i j : Nat) : Int := (paley12Rows.getD i []).getD j 0

/-- **Kernel-checked** small cases `k = 1, 2, 3` (orders 4, 8, 12). -/
theorem order_4 : ∃ H, IsHadamard 4 H := ⟨sylvester 2, by decide +kernel⟩
theorem order_8 : ∃ H, IsHadamard 8 H := ⟨sylvester 3, by decide +kernel⟩
theorem order_12 : ∃ H, IsHadamard 12 H := ⟨paley12, by decide +kernel⟩

/-! Fidelity: a matrix with two equal rows is rejected. -/
example : ¬ IsHadamard 2 (fun _ _ => 1) := by decide +kernel

end Hundred.Statements.Hadamard
