import Std

/-! Known finite benchmark for M095. This does not establish R(5,5).
The relation represents RED edges; its complement on distinct vertices is BLUE.
All three distinctness conditions are required to exclude repeated vertices.
-/
namespace Hundred.Ramsey

abbrev TriangleFree {n : Nat} (edge : Fin n → Fin n → Bool) : Prop :=
  ∀ a b c, a ≠ b → b ≠ c → a ≠ c →
    ¬ (edge a b = true ∧ edge b c = true ∧ edge a c = true)

abbrev IndependentTripleFree {n : Nat} (edge : Fin n → Fin n → Bool) : Prop :=
  ∀ a b c, a ≠ b → b ≠ c → a ≠ c →
    ¬ (edge a b = false ∧ edge b c = false ∧ edge a c = false)

abbrev ValidColoring {n : Nat} (edge : Fin n → Fin n → Bool) : Prop :=
  (∀ a, edge a a = false) ∧ (∀ a b, edge a b = edge b a)

abbrev AvoidsMonochromaticTriangle {n : Nat} (edge : Fin n → Fin n → Bool) : Prop :=
  ValidColoring edge ∧ TriangleFree edge ∧ IndependentTripleFree edge

/-- Constructive finite universal quantification, including symbolic bounds. -/
instance finiteForall : (n : Nat) → (p : Fin n → Prop) →
    [DecidablePred p] → Decidable (∀ i, p i)
  | 0, _, _ => isTrue (fun i => Fin.elim0 i)
  | n + 1, p, dp =>
    match dp 0 with
    | isFalse h0 => isFalse (fun h => h0 (h 0))
    | isTrue h0 =>
      match @finiteForall n (fun i => p i.succ) (fun i => dp i.succ) with
      | isTrue hs => isTrue (fun i => Fin.cases h0 hs i)
      | isFalse hs => isFalse (fun h => hs (fun i => h i.succ))

instance {n : Nat} (edge : Fin n → Fin n → Bool) :
    Decidable (AvoidsMonochromaticTriangle edge) := by
  unfold AvoidsMonochromaticTriangle ValidColoring TriangleFree IndependentTripleFree
  infer_instance

/-- Executable checker for any finite red/blue adjacency function. -/
def check {n : Nat} (edge : Fin n → Fin n → Bool)
    [Decidable (AvoidsMonochromaticTriangle edge)] : Bool :=
  decide (AvoidsMonochromaticTriangle edge)

/-- A true checker result entails the full graph certificate, for arbitrary n. -/
theorem check_sound {n : Nat} {edge : Fin n → Fin n → Bool}
    [Decidable (AvoidsMonochromaticTriangle edge)]
    (h : check edge = true) : AvoidsMonochromaticTriangle edge :=
  of_decide_eq_true h

/-- Modular adjacency of the five-cycle, independently encoded from the JSON witness. -/
def cycle5 (a b : Fin 5) : Bool :=
  decide ((a.val + 1) % 5 = b.val ∨ (b.val + 1) % 5 = a.val)

theorem cycle5_valid : ValidColoring cycle5 := by decide

theorem cycle5_triangleFree : TriangleFree cycle5 := by decide

theorem cycle5_independentTripleFree : IndependentTripleFree cycle5 := by decide

theorem cycle5_certificate : AvoidsMonochromaticTriangle cycle5 :=
  ⟨cycle5_valid, cycle5_triangleFree, cycle5_independentTripleFree⟩

/-- The exact finite existence claim: a red/blue coloring on five vertices.
This is the usual lower-bound witness for R(3,3), not its upper bound. -/
theorem five_vertex_witness :
    ∃ edge : Fin 5 → Fin 5 → Bool, AvoidsMonochromaticTriangle edge :=
  ⟨cycle5, cycle5_certificate⟩

/-- Reusable restriction lemma: injective vertex maps preserve this certificate. -/
theorem restrict {m n : Nat} {edge : Fin n → Fin n → Bool}
    (h : AvoidsMonochromaticTriangle edge) (f : Fin m → Fin n)
    (hf : ∀ a b, f a = f b → a = b) :
    AvoidsMonochromaticTriangle (fun a b => edge (f a) (f b)) := by
  rcases h with ⟨⟨loops, symm⟩, red, blue⟩
  refine ⟨⟨fun a => loops (f a), fun a b => symm (f a) (f b)⟩, ?_, ?_⟩
  · intro a b c hab hbc hac
    exact red (f a) (f b) (f c)
      (fun e => hab (hf a b e)) (fun e => hbc (hf b c e)) (fun e => hac (hf a c e))
  · intro a b c hab hbc hac
    exact blue (f a) (f b) (f c)
      (fun e => hab (hf a b e)) (fun e => hbc (hf b c e)) (fun e => hac (hf a c e))
end Hundred.Ramsey
