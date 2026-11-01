import Hundred
open Hundred.Ramsey

-- Mutation tests: kernel reduction must reject both false certificates.
example : ¬ TriangleFree (fun (_ _ : Fin 3) => true) := by decide
example : ¬ IndependentTripleFree (fun (_ _ : Fin 3) => false) := by decide
example : ¬ ValidColoring (fun (_ _ : Fin 1) => true) := by decide
example : ¬ ValidColoring (fun (a b : Fin 2) => decide (a.val < b.val)) := by decide

-- The generic checker is executable at concrete finite sizes.
example : check cycle5 = true := by decide
example : check (fun (_ _ : Fin 3) => true) = false := by decide

open Hundred.Frankl
-- Empty family and {empty set} must fail the nontriviality precondition.
example : ¬ Nontrivial (0 : Family2) := by decide
example : ¬ Nontrivial (1 : Family2) := by decide
-- {{0},{1}} omits its union {0,1}.
example : ¬ UnionClosed (6 : Family2) := by decide
-- The unused ground element in the tiny family is not abundant.
example : ¬ (size small ≤ 2 * frequency small 1) := by decide

-- L006: a false bit ordering and a missing union are rejected by both encodings.
example : ¬ (Hundred.FranklBridge.pack (fun s => decide (s.val = 0))).val = 2 := by decide
example : ¬ Hundred.Statements.Frankl.UnionClosed 2 6 := by decide +kernel

-- L005 negative controls: polynomial cancellation without positive denominators is invalid.
example : ¬ Hundred.Statements.ErdosStraus.Solves 3 0 0 0 := by decide
-- The n ≡ 3 mod 4 recipe must not be used at n = 5.
example : ¬ Hundred.Statements.ErdosStraus.Solves 5 2 20 20 := by decide
