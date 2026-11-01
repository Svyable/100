import Hundred.Statements.Basic

/-!
# M078 — Graph reconstruction conjecture (Kelly–Ulam)

**Registry statement.** Two finite simple graphs on `n ≥ 3` vertices with the same
multiset of vertex-deleted subgraphs (deck) are isomorphic.

**What is encoded.** `delete adj v` is `G - v` relabelled onto `0, …, n-2`.
"Same deck" (hypomorphic) means a bijection `σ` with `G - v ≅ H - σ v` for every
`v`. Bijections on `{0, …, n-1}` are maps into the range that are injective.

**Not encoded.** Edge reconstruction or digraph variants.
**Frontier:** verified for all graphs on at most 11 vertices (McKay 1997); proved
for trees, regular and disconnected graphs (Kelly 1957).
-/

namespace Hundred.Statements.Reconstruction
open Hundred.Statements

/-- `f` is a bijection of `{0, …, n-1}`. -/
abbrev IsPerm (n : Nat) (f : Nat → Nat) : Prop :=
  (∀ i, i < n → f i < n) ∧ (∀ i, i < n → ∀ j, j < n → f i = f j → i = j)

/-- The graphs `G` and `H` on `n` vertices are isomorphic. -/
def Iso (n : Nat) (G H : Nat → Nat → Bool) : Prop :=
  ∃ f, IsPerm n f ∧ ∀ i, i < n → ∀ j, j < n → G i j = H (f i) (f j)

/-- Skip vertex `v` when relabelling. -/
def skip (v i : Nat) : Nat := if i < v then i else i + 1

/-- `G - v`, relabelled onto `0, …, n-2`. -/
def delete (G : Nat → Nat → Bool) (v : Nat) : Nat → Nat → Bool :=
  fun i j => G (skip v i) (skip v j)

/-- `G` and `H` have the same deck. -/
def Hypomorphic (n : Nat) (G H : Nat → Nat → Bool) : Prop :=
  ∃ σ, IsPerm n σ ∧ ∀ v, v < n → Iso (n - 1) (delete G v) (delete H (σ v))

/-- The registry statement. -/
def Statement : Prop :=
  ∀ (n : Nat) (G H : Nat → Nat → Bool), 3 ≤ n → IsGraph n G → IsGraph n H →
    Hypomorphic n G H → Iso n G H

/-! Fidelity: deleting vertex 1 from the path `0 - 1 - 2` leaves two isolated vertices. -/
def path3 (i j : Nat) : Bool := (i + 1 == j) || (j + 1 == i)

example : delete path3 1 0 1 = false := by decide
example : delete path3 0 0 1 = true := by decide

end Hundred.Statements.Reconstruction
