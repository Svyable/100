import Hundred.Basic

/-!
# M074 — Caccetta–Häggkvist conjecture

**Registry statement.** Every loopless digraph on `n` vertices with minimum
out-degree at least `r ≥ 1` has a directed cycle of length at most `⌈n / r⌉`.

**What is encoded.** A digraph is `adj : Nat → Nat → Bool` on `0, …, n-1` with no
loops (`adj v v = false`); there is at most one arc per ordered pair, as in the
conjecture. A directed cycle of length `ℓ` is an injective sequence
`c 0, …, c (ℓ-1)` with an arc from each `c i` to `c ((i+1) mod ℓ)`.
`⌈n / r⌉` is `(n + r - 1) / r`.

**Not encoded.** The `r = n/3` (triangle) case separately. **Frontier:** proved
for `r ≤ 5` (Hoáng–Reed 1987) and for many restricted families; the lab and the
external fixed-`r = 6` corpus are tracked in the campaign.
-/

namespace Hundred.CaccettaHaggkvist
open Hundred

/-- Out-degree of `v` among vertices below `n` (loops are excluded separately). -/
def outdeg (n : Nat) (adj : Nat → Nat → Bool) (v : Nat) : Nat :=
  countBelow n (fun w => adj v w)

/-- `c` is a directed cycle of length `ℓ ≥ 1` on vertices below `n`. -/
abbrev IsCycle (n : Nat) (adj : Nat → Nat → Bool) (ℓ : Nat) (c : Nat → Nat) : Prop :=
  1 ≤ ℓ ∧ (∀ i, i < ℓ → c i < n) ∧
  (∀ i, i < ℓ → ∀ j, j < ℓ → c i = c j → i = j) ∧
  (∀ i, i < ℓ → adj (c i) (c ((i + 1) % ℓ)) = true)

/-- The registry statement. -/
def Statement : Prop :=
  ∀ (n r : Nat) (adj : Nat → Nat → Bool), 1 ≤ r →
    (∀ v, v < n → adj v v = false) →
    (∀ v, v < n → r ≤ outdeg n adj v) →
    ∃ ℓ c, ℓ ≤ (n + r - 1) / r ∧ IsCycle n adj ℓ c

/-- Fixed out-degree slice (the campaign works one `r` at a time). -/
def StatementFor (r : Nat) : Prop :=
  ∀ (n : Nat) (adj : Nat → Nat → Bool),
    (∀ v, v < n → adj v v = false) →
    (∀ v, v < n → r ≤ outdeg n adj v) →
    ∃ ℓ c, ℓ ≤ (n + r - 1) / r ∧ IsCycle n adj ℓ c

/-- The circulant digraph `v → v+1, v+2 (mod 7)`, out-degree 2. -/
def circ7 (v w : Nat) : Bool := (w + 7 - v) % 7 == 1 || (w + 7 - v) % 7 == 2

/-! Fidelity: `circ7` meets the hypotheses for `r = 2` and has a 4-cycle
`0 → 2 → 4 → 6 → 0`, matching the bound `⌈7/2⌉ = 4`. -/
example : (∀ v, v < 7 → circ7 v v = false) ∧ (∀ v, v < 7 → 2 ≤ outdeg 7 circ7 v) := by decide

def cyc4 (i : Nat) : Nat := 2 * i

example : IsCycle 7 circ7 4 cyc4 := by decide

end Hundred.CaccettaHaggkvist
