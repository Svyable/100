import Hundred.Statements.Basic

/-!
# M097 — Metric TSP four-thirds conjecture

**Registry statement.** For every metric on finitely many points, the optimum
TSP tour cost is at most `(4/3)` times the Held–Karp / subtour LP optimum.

**What is encoded.** A metric is a symmetric Nat distance with zero diagonal and
the triangle inequality. A tour is a cyclic permutation. Held–Karp is abstracted
as a lower bound `hk` already certified elsewhere (the Python exact-LP engine);
the conjecture is the cleared inequality `3 · OPT ≤ 4 · hk`.

**Not encoded.** The LP itself, fractional subtour separation, or graphic-metric
specialization.
**Frontier:** integrality gap is known to be at least `4/3` and at most `3/2`;
small-`n` maxima are published.
-/

namespace Hundred.Statements.MetricTSP
open Hundred.Statements

/-- Symmetric zero-diagonal triangle inequality on `{0,…,n-1}`. -/
def IsMetric (n : Nat) (d : Nat → Nat → Nat) : Prop :=
  (∀ i, i < n → d i i = 0) ∧
  (∀ i, i < n → ∀ j, j < n → d i j = d j i) ∧
  (∀ i, i < n → ∀ j, j < n → ∀ k, k < n → d i k ≤ d i j + d j k)

/-- `p` is a cyclic ordering of `{0,…,n-1}` (a tour). -/
def IsTour (n : Nat) (p : Nat → Nat) : Prop :=
  (∀ i, i < n → p i < n) ∧
  (∀ i, i < n → ∀ j, j < n → p i = p j → i = j)

/-- Tour length. -/
def tourLen (n : Nat) (d : Nat → Nat → Nat) (p : Nat → Nat) : Nat :=
  (List.range n).foldl (fun s i => s + d (p i) (p ((i + 1) % n))) 0

/-- Cleared four-thirds inequality against a Held–Karp lower bound. -/
def FourThirds (opt hk : Nat) : Prop :=
  3 * opt ≤ 4 * hk

/-- The registry statement. -/
def Statement : Prop :=
  ∀ (n opt hk : Nat) (d : Nat → Nat → Nat),
    3 ≤ n → IsMetric n d →
    (∃ p, IsTour n p ∧ tourLen n d p = opt) →
    hk ≤ opt →
    FourThirds opt hk

/-- Path metric on 3 vertices: distances 1 along the path, 2 at the ends. -/
def path3 (i j : Nat) : Nat :=
  if i == j then 0 else if (i + j == 1) || (i + j == 3) then 1 else 2

/-- Identity tour on 3 vertices. -/
def id3 (i : Nat) : Nat := i

/-! Fidelity: path distances and the cleared `4/3` inequality on equal opt/hk. -/
example : path3 0 0 = 0 := by decide +kernel
example : path3 0 1 = 1 := by decide +kernel
example : path3 0 2 = 2 := by decide +kernel
example : path3 0 1 = path3 1 0 := by decide +kernel
example : tourLen 3 path3 id3 = 4 := by decide +kernel
example : 3 * (4 : Nat) ≤ 4 * 4 := by decide +kernel

end Hundred.Statements.MetricTSP
