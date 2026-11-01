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
fidelity test of the encoding, not progress; it is kept small because trial division
in the kernel is quadratic, and the lab covers far larger ranges in Python.
-/

namespace Hundred.Statements.Goldbach
open Hundred.Statements

/-- The registry statement. -/
def Statement : Prop :=
  ∀ n : Nat, 4 ≤ n → n % 2 = 0 → ∃ p, p ≤ n ∧ IsPrime p ∧ IsPrime (n - p)

/-- Least Goldbach prime for every even `n ≤ 100` (0 elsewhere), produced by the
lab probe `goldbach`; the kernel re-checks every entry below. -/
def leastPrime : List Nat := [
    0, 0, 0, 0, 2, 0, 3, 0, 3, 0, 3, 0, 5, 0, 3, 0, 3, 0, 5, 0,
    3, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 3, 0, 3, 0, 5, 0, 7, 0,
    3, 0, 5, 0, 3, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0,
    7, 0, 3, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 3, 0, 3, 0, 5, 0,
    7, 0, 3, 0, 5, 0, 3, 0, 5, 0, 7, 0, 3, 0, 5, 0, 7, 0, 19, 0,
    3]

/-- The witness for `n`. -/
def witness (n : Nat) : Nat := leastPrime.getD n 0

/-- Bounded, kernel-decidable certificate: every listed witness is valid. -/
abbrev Certified (N : Nat) : Prop :=
  ∀ n, n < N + 1 → 4 ≤ n → n % 2 = 0 →
    witness n ≤ n ∧ IsPrime (witness n) ∧ IsPrime (n - witness n)

theorem certified_100 : Certified 100 := by decide +kernel

/-- **Kernel-checked:** the statement holds for every even `4 ≤ n ≤ 100`. -/
theorem holds_upTo_100 :
    ∀ n, n ≤ 100 → 4 ≤ n → n % 2 = 0 → ∃ p, p ≤ n ∧ IsPrime p ∧ IsPrime (n - p) :=
  fun n hn h4 he => ⟨witness n, certified_100 n (Nat.lt_succ_of_le hn) h4 he⟩

/-! Fidelity: the encoding agrees with hand-checked cases. -/
example : IsPrime 3 ∧ IsPrime (10 - 3) := by decide +kernel
example : witness 100 = 3 := by decide +kernel

end Hundred.Statements.Goldbach
