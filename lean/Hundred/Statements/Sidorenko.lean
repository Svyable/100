import Hundred.Statements.Basic

/-!
# M073 — Sidorenko conjecture

**Registry statement.** For every bipartite graph `H` with `e` edges and every
graph `G`, the homomorphism density satisfies
`t(H,G) ≥ t(K₂,G)^e`.

**What is encoded.** Homomorphism counts as the number of maps of vertex sets
preserving edges, and densities as the rational `hom(H,G) / |V(G)|^{|V(H)|}`
cleared to the integer inequality
`hom(H,G) · |V(G)|^e ≥ hom(K₂,G)^e · |V(G)|^{|V(H)|}` after multiplying through
by denominators. `H` is required to be bipartite (2-colourable).

**Not encoded.** Graphon formulations, continuous limits, or any specific open
bipartite pattern such as `K_{5,5}` minus a Hamilton cycle.
**Frontier:** known for trees, even cycles, complete bipartite graphs and many
families; small finite hosts are not expected to refute it.
-/

namespace Hundred.Statements.Sidorenko
open Hundred.Statements

/-- Number of graph homs from an `h`-vertex pattern into an `n`-vertex host.
A map is coded by its base-`n` digits. -/
def homCount (h n : Nat) (H G : Nat → Nat → Bool) : Nat :=
  countBelow (n ^ h) fun code =>
    (List.range h).all fun u =>
      (List.range h).all fun v =>
        !(H u v) || G (code / n ^ u % n) (code / n ^ v % n)

/-- Directed edge count (each undirected edge contributes 2). -/
def directedEdges (h : Nat) (H : Nat → Nat → Bool) : Nat :=
  (List.range h).foldl (fun s u => s + countBelow h fun v => H u v) 0

/-- `H` on `h` vertices is bipartite via colouring `col`. -/
def IsBipartite (h : Nat) (H : Nat → Nat → Bool) (col : Nat → Nat) : Prop :=
  (∀ v, v < h → col v < 2) ∧
  (∀ u, u < h → ∀ v, v < h → H u v = true → col u ≠ col v)

/-- Sidorenko inequality on a fixed bipartite pattern, cleared of denominators. -/
def HoldsFor (h e n : Nat) (H G : Nat → Nat → Bool) : Prop :=
  homCount h n H G * n ^ e ≥ (homCount 2 n (fun a b => decide (a ≠ b)) G) ^ e * n ^ h

/-- The registry statement. -/
def Statement : Prop :=
  ∀ (h e n : Nat) (H G : Nat → Nat → Bool) (col : Nat → Nat),
    IsGraph h H → IsGraph n G → IsBipartite h H col →
    directedEdges h H / 2 = e →
    HoldsFor h e n H G

/-- Single edge on 2 vertices. -/
def edge2 (i j : Nat) : Bool := decide (i ≠ j)

/-! Fidelity: `K₂` is a bipartite pattern; `hom` of the edge into itself is 2. -/
example : edge2 0 1 = true := by decide +kernel
example : edge2 0 0 = false := by decide +kernel
example : directedEdges 2 edge2 = 2 := by decide +kernel
example : homCount 2 2 edge2 edge2 = 2 := by decide +kernel

end Hundred.Statements.Sidorenko
