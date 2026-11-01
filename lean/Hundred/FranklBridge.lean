import Hundred.Frankl
import Hundred.Statements.Frankl

/-!
M075 / L006. Fidelity bridge between two independent encodings on a two-element
ground set. Theorems here quantify over all sixteen families, not just fixtures.
The generic bitmask comparator's k=3 case remains separate: this file makes no
claim to a representation theorem for arbitrary k or arbitrary extensional sets.
-/

namespace Hundred.FranklBridge

open Hundred.Frankl

/-- Both encodings assign exactly the same membership bit to every subset. -/
theorem member_iff : ∀ f : Family2, ∀ s : Set2,
    member f s = Hundred.Statements.Frankl.Mem f.val s.val := by decide +kernel

/-- The two encodings count the same family members. -/
theorem size_eq : ∀ f : Family2,
    size f = Hundred.Statements.Frankl.size 2 f.val := by decide +kernel

/-- Element frequencies are identical in the two encodings. -/
theorem frequency_eq : ∀ f : Family2, ∀ x : Fin 2,
    frequency f x = Hundred.Statements.Frankl.degree 2 f.val x.val := by decide +kernel

/-- A family contains a nonempty member in one encoding iff it does in the other. -/
theorem nontrivial_iff : ∀ f : Family2,
    Nontrivial f ↔ Hundred.Statements.Frankl.HasNonemptyMember 2 f.val := by decide +kernel

/-- All sixteen families agree on the (non-vacuous) union-closure requirement. -/
theorem unionClosed_iff : ∀ f : Family2,
    UnionClosed f ↔ Hundred.Statements.Frankl.UnionClosed 2 f.val := by decide +kernel

/-- Both models assign the same half-frequency threshold to every family. -/
theorem abundant_iff : ∀ f : Family2,
    HasAbundantElement f ↔ Hundred.Statements.Frankl.Abundant 2 f.val := by decide +kernel

/-- Transport the Fin-based restricted Frankl theorem to the generic comparator. -/
theorem from_fin2 : Hundred.Statements.Frankl.OnGroundSet 2 := by
  intro F hbound hclosed hnonempty
  have h16 : F < 16 := by simpa using hbound
  let f : Family2 := ⟨F, h16⟩
  have hc : UnionClosed f := (unionClosed_iff f).mpr hclosed
  have hn : Nontrivial f := (nontrivial_iff f).mpr hnonempty
  exact (abundant_iff f).mp (frankl_two f hn hc)

/-- Encode an arbitrary extensional family predicate on the four subset masks. -/
def pack (p : Set2 → Bool) : Family2 :=
  ⟨(if p 0 then 1 else 0) + (if p 1 then 2 else 0) +
      (if p 2 then 4 else 0) + (if p 3 then 8 else 0), by
    cases h0 : p 0 <;> cases h1 : p 1 <;>
      cases h2 : p 2 <;> cases h3 : p 3 <;>
      simp [h0, h1, h2, h3] <;> decide⟩

/-- Packing preserves membership for every extensional predicate and subset. -/
theorem pack_member (p : Set2 → Bool) :
    ∀ s : Set2, member (pack p) s = p s := by
  intro s
  have hcases : s = 0 ∨ s = 1 ∨ s = 2 ∨ s = 3 := by
    have hall : ∀ t : Set2, t = 0 ∨ t = 1 ∨ t = 2 ∨ t = 3 := by decide
    exact hall s
  rcases hcases with hs | hs | hs | hs <;> rw [hs] <;>
    cases h0 : p 0 <;> cases h1 : p 1 <;>
    cases h2 : p 2 <;> cases h3 : p 3 <;>
    simp [pack, member, h0, h1, h2, h3] <;> decide

/-- Completeness: every extensional family of subsets has a sixteen-mask code. -/
theorem extensional_complete (p : Set2 → Bool) :
    ∃ f : Family2, ∀ s : Set2, member f s = p s :=
  ⟨pack p, pack_member p⟩

/-- Consolidate the independently checked k=1 and k=3 cases with the
transported k=2 theorem. This does NOT transport k=2 to k=3. -/
theorem bounded_ground_sets : ∀ k : Nat, 1 ≤ k → k ≤ 3 →
    Hundred.Statements.Frankl.OnGroundSet k := by
  intro k hlow hhigh
  have h : k = 1 ∨ k = 2 ∨ k = 3 := by omega
  rcases h with h | h | h
  · subst k
    exact Hundred.Statements.Frankl.ground_1
  · subst k
    exact from_fin2
  · subst k
    exact Hundred.Statements.Frankl.ground_3

end Hundred.FranklBridge
