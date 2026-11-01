import Hundred.Statements.Basic

/-!
# M019 — Erdős–Straus conjecture

**Registry statement.** For every integer `n ≥ 2`, `4/n = 1/x + 1/y + 1/z` has a
solution in positive integers.

**What is encoded.** Clearing denominators, `4/n = 1/x + 1/y + 1/z` with
`x, y, z > 0` is equivalent to `4xyz = n(xy + yz + zx)`; no rationals are needed.

**Not encoded.** Distinctness of `x, y, z` (not required by the conjecture) and
residue classes other than the classical `n ≡ 3 mod 4` family below. **Frontier:** verified computationally far beyond `10^14`.
-/

namespace Hundred.Statements.ErdosStraus

/-- One solution of `4/n = 1/x + 1/y + 1/z` in positive integers. -/
abbrev Solves (n x y z : Nat) : Prop :=
  0 < x ∧ 0 < y ∧ 0 < z ∧ 4 * x * y * z = n * (x * y + y * z + z * x)

/-- The registry statement. -/
def Statement : Prop :=
  ∀ n : Nat, 2 ≤ n → ∃ x y z, Solves n x y z

/-- Explicit `(x, y, z)` for `n = 2, …, 100`, from the lab's divisor solver. -/
def table : List (Nat × Nat × Nat) := [
    (1, 2, 2),
    (1, 4, 12),
    (2, 3, 6),
    (2, 4, 20),
    (2, 7, 42),
    (2, 15, 210),
    (3, 7, 42),
    (3, 10, 90),
    (3, 16, 240),
    (3, 34, 1122),
    (4, 13, 156),
    (4, 18, 468),
    (4, 29, 812),
    (4, 61, 3660),
    (5, 21, 420),
    (5, 30, 510),
    (5, 46, 2070),
    (5, 96, 9120),
    (6, 31, 930),
    (6, 43, 1806),
    (6, 67, 4422),
    (6, 139, 19182),
    (7, 43, 1806),
    (7, 60, 2100),
    (7, 92, 8372),
    (7, 190, 35910),
    (8, 57, 3192),
    (8, 78, 9048),
    (8, 121, 14520),
    (8, 249, 61752),
    (9, 73, 5256),
    (9, 100, 9900),
    (9, 154, 23562),
    (9, 316, 99540),
    (10, 91, 8190),
    (10, 124, 22940),
    (10, 191, 36290),
    (10, 391, 152490),
    (11, 111, 12210),
    (11, 154, 6314),
    (11, 232, 53592),
    (11, 474, 224202),
    (12, 133, 17556),
    (12, 181, 32580),
    (12, 277, 76452),
    (12, 565, 318660),
    (13, 157, 24492),
    (14, 99, 9702),
    (13, 326, 105950),
    (13, 664, 440232),
    (14, 183, 33306),
    (14, 248, 92008),
    (14, 379, 143262),
    (14, 771, 593670),
    (15, 211, 44310),
    (15, 286, 81510),
    (15, 436, 189660),
    (15, 886, 784110),
    (16, 241, 57840),
    (16, 326, 159088),
    (16, 497, 246512),
    (16, 1009, 1017072),
    (17, 273, 74256),
    (17, 370, 81770),
    (17, 562, 315282),
    (17, 1140, 1298460),
    (18, 307, 93942),
    (18, 415, 171810),
    (18, 631, 397530),
    (18, 1279, 1634562),
    (19, 343, 117306),
    (20, 210, 30660),
    (19, 704, 494912),
    (19, 1426, 2032050),
    (20, 381, 144780),
    (20, 514, 395780),
    (20, 781, 609180),
    (20, 1581, 2497980),
    (21, 421, 176820),
    (21, 568, 322056),
    (21, 862, 742182),
    (21, 1744, 3039792),
    (22, 463, 213906),
    (22, 624, 583440),
    (22, 947, 895862),
    (22, 1915, 3665310),
    (23, 507, 256542),
    (23, 690, 61410),
    (23, 1036, 1072260),
    (23, 2094, 4382742),
    (24, 553, 305256),
    (24, 745, 554280),
    (24, 1129, 1273512),
    (24, 2281, 5200680),
    (25, 601, 360600),
    (25, 810, 392850),
    (25, 1226, 1501850),
    (25, 2476, 6128100),
    (26, 651, 423150)]

/-- The tabulated triple for `n`. -/
def triple (n : Nat) : Nat × Nat × Nat := table.getD (n - 2) (1, 1, 1)

abbrev Certified (N : Nat) : Prop :=
  ∀ n, n < N + 1 → 2 ≤ n → Solves n (triple n).1 (triple n).2.1 (triple n).2.2

theorem certified_100 : Certified 100 := by decide +kernel

/-- **Kernel-checked:** the statement holds for every `2 ≤ n ≤ 100`. -/
theorem holds_upTo_100 : ∀ n, n ≤ 100 → 2 ≤ n → ∃ x y z, Solves n x y z :=
  fun n hn h2 => ⟨_, _, _, certified_100 n (Nat.lt_succ_of_le hn) h2⟩


/-- Classical infinite family. Repeated denominators are permitted by Solves. -/
theorem residue_three (k : Nat) :
    Solves (4 * k + 3) (k + 1)
      (2 * (4 * k + 3) * (k + 1)) (2 * (4 * k + 3) * (k + 1)) := by
  refine ⟨by omega, Nat.mul_pos (by omega) (by omega),
    Nat.mul_pos (by omega) (by omega), ?_⟩
  simp [Nat.mul_add, Nat.add_mul, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]
    <;> simp only [← Nat.mul_assoc]
    <;> omega

/-- The residue-class statement, quantified over every natural n, with no upper bound. -/
theorem holds_mod_four_three (n : Nat) (hn : n % 4 = 3) :
    ∃ x y z, Solves n x y z := by
  have heq : n = 4 * (n / 4) + 3 := by omega
  rw [heq]
  exact ⟨_, _, _, residue_three (n / 4)⟩

/-! Fidelity: `4/5 = 1/2 + 1/4 + 1/20`. -/
example : Solves 5 2 4 20 := by decide +kernel

end Hundred.Statements.ErdosStraus
