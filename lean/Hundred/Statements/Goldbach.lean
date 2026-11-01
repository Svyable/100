import Hundred.Statements.Basic

/-!
# M006 — Strong (binary) Goldbach conjecture

**Registry statement.** Every even integer `n ≥ 4` is a sum of two primes.

**What is encoded.** `Statement` quantifies over all natural numbers; primes are
`Hundred.IsPrime` (trial division, checked against known values in `Basic`).
Writing `n = p + (n - p)` with `p ≤ n` is equivalent to `n = p + q`, because
`n - p` is truncated subtraction only when `p > n`, which is excluded.

**Not encoded.** Weak (ternary) Goldbach, Chen-type statements, any bound on the
least partition. **Frontier:** verified for every even `n ≤ 4·10^18`
(Oliveira e Silva, Herzog & Pardi, 2014). The kernel-checked range below is a
fidelity test of the encoding, not progress.
-/

namespace Hundred.Statements.Goldbach
open Hundred.Statements

/-- The registry statement. -/
def Statement : Prop :=
  ∀ n : Nat, 4 ≤ n → n % 2 = 0 → ∃ p, p ≤ n ∧ IsPrime p ∧ IsPrime (n - p)

/-- Least Goldbach prime for every even `n ≤ 1000` (0 elsewhere), produced by the
lab probe `goldbach`; the kernel re-checks every entry below. -/
def leastPrime : List Nat := [
    0, 0, 0, 0, 2, 0, 3, 0, 3, 0, 3, 0, 5, 0, 3, 0, 3, 0, 5, 0,
    3, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 3, 0, 3, 0, 5, 0, 7, 0,
    3, 0, 5, 0, 3, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0,
    7, 0, 3, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 3, 0, 3, 0, 5, 0,
    7, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 7, 0, 19, 0,
    3, 0, 5, 0, 3, 0, 3, 0, 5, 0, 3, 0, 3, 0, 5, 0, 3, 0, 5, 0,
    7, 0, 13, 0, 11, 0, 13, 0, 19, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0,
    3, 0, 3, 0, 5, 0, 7, 0, 11, 0, 11, 0, 3, 0, 3, 0, 5, 0, 7, 0,
    3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0,
    7, 0, 3, 0, 3, 0, 5, 0, 7, 0, 11, 0, 11, 0, 3, 0, 3, 0, 5, 0,
    3, 0, 3, 0, 5, 0, 7, 0, 11, 0, 11, 0, 13, 0, 3, 0, 5, 0, 7, 0,
    23, 0, 11, 0, 13, 0, 3, 0, 5, 0, 3, 0, 3, 0, 5, 0, 3, 0, 5, 0,
    7, 0, 3, 0, 3, 0, 5, 0, 7, 0, 11, 0, 11, 0, 3, 0, 5, 0, 7, 0,
    3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 7, 0, 3, 0, 3, 0, 5, 0, 7, 0,
    3, 0, 5, 0, 3, 0, 3, 0, 5, 0, 7, 0, 11, 0, 11, 0, 3, 0, 5, 0,
    7, 0, 19, 0, 11, 0, 13, 0, 31, 0, 3, 0, 5, 0, 3, 0, 3, 0, 5, 0,
    3, 0, 5, 0, 7, 0, 13, 0, 11, 0, 13, 0, 19, 0, 3, 0, 5, 0, 7, 0,
    3, 0, 5, 0, 7, 0, 29, 0, 11, 0, 3, 0, 3, 0, 5, 0, 3, 0, 5, 0,
    7, 0, 3, 0, 5, 0, 7, 0, 19, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0,
    7, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 7, 0, 19, 0,
    3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 13, 0, 3, 0, 5, 0, 7, 0, 17, 0,
    11, 0, 3, 0, 3, 0, 5, 0, 7, 0, 11, 0, 11, 0, 3, 0, 3, 0, 5, 0,
    7, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 7, 0, 19, 0,
    3, 0, 5, 0, 3, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 13, 0, 11, 0,
    13, 0, 3, 0, 5, 0, 7, 0, 31, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0,
    13, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 7, 0, 19, 0,
    11, 0, 13, 0, 3, 0, 3, 0, 5, 0, 7, 0, 11, 0, 11, 0, 13, 0, 17, 0,
    17, 0, 19, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 7, 0, 47, 0, 11, 0,
    3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 7, 0, 3, 0, 3, 0, 5, 0, 7, 0,
    3, 0, 5, 0, 7, 0, 17, 0, 11, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0,
    7, 0, 3, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0,
    3, 0, 3, 0, 5, 0, 7, 0, 11, 0, 11, 0, 13, 0, 3, 0, 5, 0, 7, 0,
    23, 0, 11, 0, 3, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0,
    7, 0, 3, 0, 3, 0, 5, 0, 7, 0, 11, 0, 11, 0, 13, 0, 3, 0, 5, 0,
    3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 7, 0, 19, 0, 3, 0, 5, 0, 7, 0,
    17, 0, 11, 0, 3, 0, 5, 0, 7, 0, 19, 0, 3, 0, 5, 0, 7, 0, 17, 0,
    11, 0, 3, 0, 5, 0, 7, 0, 19, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0,
    7, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 13, 0, 3, 0, 5, 0, 7, 0,
    3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 13, 0, 3, 0, 5, 0, 3, 0, 5, 0,
    7, 0, 13, 0, 11, 0, 13, 0, 19, 0, 3, 0, 5, 0, 7, 0, 23, 0, 11, 0,
    3, 0, 5, 0, 7, 0, 19, 0, 11, 0, 13, 0, 3, 0, 3, 0, 5, 0, 7, 0,
    11, 0, 11, 0, 3, 0, 3, 0, 5, 0, 3, 0, 3, 0, 5, 0, 7, 0, 11, 0,
    11, 0, 3, 0, 5, 0, 7, 0, 19, 0, 11, 0, 13, 0, 31, 0, 3, 0, 5, 0,
    3, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 13, 0, 11, 0, 13, 0, 19, 0,
    3, 0, 5, 0, 3, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 13, 0, 11, 0,
    13, 0, 19, 0, 17, 0, 19, 0, 31, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0,
    13, 0, 3, 0, 5, 0, 7, 0, 17, 0, 11, 0, 3, 0, 5, 0, 7, 0, 19, 0,
    3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0,
    7, 0, 43, 0, 11, 0, 13, 0, 31, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0,
    3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 7, 0, 73, 0, 3, 0, 5, 0, 7, 0,
    3]

/-- The witness for `n`. -/
def witness (n : Nat) : Nat := leastPrime.getD n 0

/-- Bounded, kernel-decidable certificate: every listed witness is valid. -/
abbrev Certified (N : Nat) : Prop :=
  ∀ n, n < N + 1 → 4 ≤ n → n % 2 = 0 →
    witness n ≤ n ∧ IsPrime (witness n) ∧ IsPrime (n - witness n)

theorem certified_1000 : Certified 1000 := by decide +kernel

/-- **Kernel-checked:** the statement holds for every even `4 ≤ n ≤ 1000`. -/
theorem holds_upTo_1000 :
    ∀ n, n ≤ 1000 → 4 ≤ n → n % 2 = 0 → ∃ p, p ≤ n ∧ IsPrime p ∧ IsPrime (n - p) :=
  fun n hn h4 he => ⟨witness n, certified_1000 n (Nat.lt_succ_of_le hn) h4 he⟩

/-! Fidelity: the encoding agrees with hand-checked cases. -/
example : IsPrime 3 ∧ IsPrime (10 - 3) := by decide
example : witness 100 = 3 := by decide

end Hundred.Statements.Goldbach
