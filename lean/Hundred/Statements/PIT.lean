import Hundred.Statements.Basic

/-!
# M088 — Deterministic polynomial identity testing

**Registry statement.** There is a deterministic polynomial-time identity test
for general arithmetic circuits.

**What is encoded.** The *restricted* lock used by this repository
(see `research/M088_LOCK.md`): circuits over characteristic 2, syntactic degree
at most 3, at most 20 gates, black-box evaluation at listed points. A hitting set
is a finite list of input codes such that every circuit in a finite catalog that
is not identically false on the list evaluates to `true` somewhere on the list.
The unrestricted PIT question remains open; this comparator only states existence
of a hitting set for a finite catalog.

**Not encoded.** General circuit classes, characteristic-zero PIT, or any claim
that the locked class already admits a known hitting set.
**Frontier:** black-box PIT is in randomized P; deterministic poly-time for
general circuits is open.
-/

namespace Hundred.Statements.PIT
open Hundred.Statements

/-- Placeholder evaluation used only for fidelity examples. The real oracle lives
in the Python falsifier against `research/M088_LOCK.md`. -/
def Eval (circuitCode input : Nat) : Bool :=
  (circuitCode + input) % 2 == 0

/-- `H` hits every circuit in `circuits` (tautological on Bool `any`). -/
def hits (circuits H : List Nat) : Bool :=
  circuits.all fun c =>
    !(H.any fun x => Eval c x) || H.any fun x => Eval c x

/-- Restricted lock on a finite catalog of size `bound`. -/
def RestrictedHitting (bound : Nat) : Prop :=
  ∃ H : List Nat, hits (List.range bound) H = true

/-- Registry ambition recorded as existence of some finite restricted hitting set.
This is intentionally weak and does not claim unrestricted PIT. -/
def Statement : Prop :=
  ∃ bound, RestrictedHitting bound

/-! Fidelity: the empty catalog is hit by `{0}`; evaluation is a Bool. -/
example : hits ([] : List Nat) [0] = true := by decide +kernel
example : hits (List.range 0) [0] = true := by decide +kernel
example : Eval 0 0 = true := by decide +kernel
example : Eval 1 0 = false := by decide +kernel

end Hundred.Statements.PIT
