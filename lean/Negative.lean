import Hundred
open Hundred.Ramsey

-- Mutation tests: kernel reduction must reject both false certificates.
example : ¬ TriangleFree (fun (_ _ : Fin 3) => true) := by decide
example : ¬ IndependentTripleFree (fun (_ _ : Fin 3) => false) := by decide
example : ¬ ValidColoring (fun (_ _ : Fin 1) => true) := by decide
example : ¬ ValidColoring (fun (a b : Fin 2) => decide (a.val < b.val)) := by decide
