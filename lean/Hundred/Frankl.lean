import Hundred.Ramsey

/-! M075: exhaustive two-element ground-set case, not unrestricted Frankl.
A set is a two-bit mask (Fin 4); a family is a four-bit mask (Fin 16).
There is one membership bit per set, so duplicates cannot inflate frequencies.
-/
namespace Hundred.Frankl

/-- Constructive finite existential search, with a witness or a refutation. -/
instance finiteExists : (n : Nat) → (p : Fin n → Prop) →
    [DecidablePred p] → Decidable (∃ i, p i)
  | 0, _, _ => isFalse (fun ⟨i, _⟩ => Fin.elim0 i)
  | n + 1, p, dp =>
    match dp 0 with
    | isTrue h0 => isTrue ⟨0, h0⟩
    | isFalse h0 =>
      match @finiteExists n (fun i => p i.succ) (fun i => dp i.succ) with
      | isTrue hs => isTrue (by rcases hs with ⟨i, hi⟩; exact ⟨i.succ, hi⟩)
      | isFalse hs => isFalse (fun ⟨i, hi⟩ =>
          Fin.cases (fun h => h0 h) (fun j h => hs ⟨j, h⟩) i hi)

abbrev Set2 := Fin 4
abbrev Family2 := Fin 16

def member (f : Family2) (s : Set2) : Bool :=
  decide (f.val / 2 ^ s.val % 2 = 1)

def contains (s : Set2) (x : Fin 2) : Bool :=
  decide (s.val / 2 ^ x.val % 2 = 1)

def union (s t : Set2) : Set2 :=
  ⟨(s.val ||| t.val) % 4, Nat.mod_lt _ (by decide)⟩

abbrev UnionClosed (f : Family2) : Prop :=
  ∀ s t : Set2, member f s = true → member f t = true → member f (union s t) = true

abbrev Nontrivial (f : Family2) : Prop :=
  ∃ s : Set2, member f s = true ∧ s.val ≠ 0

def size (f : Family2) : Nat :=
  ((List.finRange 4).filter (member f)).length

def frequency (f : Family2) (x : Fin 2) : Nat :=
  ((List.finRange 4).filter (fun s => member f s && contains s x)).length

abbrev HasAbundantElement (f : Family2) : Prop :=
  ∃ x : Fin 2, size f ≤ 2 * frequency f x

/-- Bitwise union agrees with elementwise union on the full encoded domain. -/
theorem union_membership : ∀ s t : Set2, ∀ x : Fin 2,
    contains (union s t) x = (contains s x || contains t x) := by decide

/-- Exhaustive restricted theorem: all 16 families, without a search oracle. -/
theorem frankl_two : ∀ f : Family2,
    Nontrivial f → UnionClosed f → HasAbundantElement f := by decide

/-- Replay of FRANKL_SMALL.json: the family {empty set, {0}} has mask 3. -/
def small : Family2 := 3

theorem small_nontrivial : Nontrivial small := by decide
theorem small_closed : UnionClosed small := by decide
theorem small_half : size small = 2 ∧ frequency small 0 = 1 := by decide

/-- Downstream application of the universal finite result. -/
theorem small_abundant : HasAbundantElement small :=
  frankl_two small small_nontrivial small_closed

end Hundred.Frankl
