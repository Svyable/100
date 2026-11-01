import Hundred.Statements.Basic

/-!
# M096 — Is there a projective plane of order 12?

**Registry statement.** No projective plane of order 12 exists (conjectured: the
order of every finite projective plane is a prime power).

**What is encoded.** A projective plane of order `q` has `N = q² + q + 1` points
and `N` lines; `I p l` says point `p` lies on line `l`. We require: every line has
`q + 1` points, every two distinct points lie on exactly one common line, and
every two distinct lines meet in exactly one point. For `q ≥ 2` these axioms are
equivalent to the usual definition (they force the non-degeneracy axiom).

**Not encoded.** The prime-power conjecture in general. **Frontier:** order 10
was excluded by Lam, Thiel & Swiercz (1989); order 12 is the smallest open case.
-/

namespace Hundred.Statements.ProjectivePlane
open Hundred.Statements

abbrev IsPlane (q : Nat) (I : Nat → Nat → Bool) : Prop :=
  (∀ l, l < q * q + q + 1 → countBelow (q * q + q + 1) (fun p => I p l) = q + 1) ∧
  (∀ p, p < q * q + q + 1 → ∀ r, r < q * q + q + 1 → p ≠ r →
      countBelow (q * q + q + 1) (fun l => I p l && I r l) = 1) ∧
  (∀ l, l < q * q + q + 1 → ∀ m, m < q * q + q + 1 → l ≠ m →
      countBelow (q * q + q + 1) (fun p => I p l && I p m) = 1)

/-- The registry statement. -/
def Statement : Prop := ¬ ∃ I : Nat → Nat → Bool, IsPlane 12 I

/-- The Fano plane: line `l` is `{l, l+1, l+3} mod 7` (a perfect difference set). -/
def fano (p l : Nat) : Bool :=
  (p + 7 - l) % 7 == 0 || (p + 7 - l) % 7 == 1 || (p + 7 - l) % 7 == 3

/-- The order-3 plane from the difference set `{0, 1, 3, 9} mod 13`. -/
def order3 (p l : Nat) : Bool :=
  (p + 13 - l) % 13 == 0 || (p + 13 - l) % 13 == 1 || (p + 13 - l) % 13 == 3 ||
    (p + 13 - l) % 13 == 9

/-- **Kernel-checked:** planes of orders 2 and 3 exist, so the axioms are satisfiable. -/
theorem exists_order_2 : ∃ I, IsPlane 2 I := ⟨fano, by decide +kernel⟩
theorem exists_order_3 : ∃ I, IsPlane 3 I := ⟨order3, by decide +kernel⟩

/-! Fidelity: the empty incidence relation is not a plane. -/
example : ¬ IsPlane 2 (fun _ _ => false) := by decide +kernel

end Hundred.Statements.ProjectivePlane
