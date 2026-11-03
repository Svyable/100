import Std.Tactic

/-!
# M080 — one-exceptional-row Rota construction: general cyclic Latin completion

Only the combinatorial assertion that an INJECTIVE matching of exceptional
columns to omitted basis symbols yields cyclic Latin rows is proved here,
for every n >= 1. The exchange graph and its matching are inputs.
NOT encoded: vector/matroid independence, Hall's theorem, determinant
nonzero-term existence, the exact permanent counting identity, or full RBC.
Those steps have separate paper proof and exact finite adversarial tests.
No unproved assumptions are introduced as Lean axioms.
-/

namespace Hundred.Research.M080

private theorem mod_shift_inj (N a b s : Nat) (_hN : 0 < N)
    (ha : a < N) (hb : b < N) (hs : s < N)
    (h : (a + s) % N = (b + s) % N) : a = b := by
  by_cases ha1 : a + s < N
  · rw [Nat.mod_eq_of_lt ha1] at h
    by_cases hb1 : b + s < N
    · rw [Nat.mod_eq_of_lt hb1] at h
      omega
    · have hb2 : b + s - N < N := by omega
      rw [Nat.mod_eq_sub_mod (by omega : b+s ≥ N), Nat.mod_eq_of_lt hb2] at h
      omega
  · have ha2 : a + s - N < N := by omega
    rw [Nat.mod_eq_sub_mod (by omega : a+s ≥ N), Nat.mod_eq_of_lt ha2] at h
    by_cases hb1 : b + s < N
    · rw [Nat.mod_eq_of_lt hb1] at h
      omega
    · have hb2 : b + s - N < N := by omega
      rw [Nat.mod_eq_sub_mod (by omega : b+s ≥ N), Nat.mod_eq_of_lt hb2] at h
      omega

/-- For a permutation missing of n+1 columns, the n repeated rows
are cyclic translates of missing by shifts 1,...,n. -/
def cyclicRows (n : Nat) (missing : Fin (n+1) → Fin (n+1))
    (r : Fin n) (c : Fin (n+1)) : Fin (n+1) :=
  ⟨((missing c).val + (r.val+1)) % (n+1), Nat.mod_lt _ (Nat.succ_pos n)⟩

theorem cyclic_rows_permutations (n : Nat)
    (missing : Fin (n+1) → Fin (n+1))
    (h_missing : ∀ c d, missing c = missing d → c = d)
    : (∀ r c d, cyclicRows n missing r c = cyclicRows n missing r d → c = d)
      ∧ (∀ c r s, cyclicRows n missing r c = cyclicRows n missing s c → r = s)
      ∧ (∀ c r, cyclicRows n missing r c ≠ missing c) := by
  constructor
  · intro r c d h
    have hv : ((missing c).val + (r.val+1)) % (n+1)
            = ((missing d).val + (r.val+1)) % (n+1) := congrArg Fin.val h
    have heq : (missing c).val = (missing d).val :=
      mod_shift_inj (n+1) _ _ _ (Nat.succ_pos n)
        (missing c).isLt (missing d).isLt (by omega : r.val+1<n+1) hv
    exact h_missing c d (Fin.ext heq)
  constructor
  · intro c r s h
    have hv : ((missing c).val + (r.val+1)) % (n+1)
            = ((missing c).val + (s.val+1)) % (n+1) := congrArg Fin.val h
    have hv' : ((r.val+1) + (missing c).val) % (n+1)
            = ((s.val+1) + (missing c).val) % (n+1) := by
       simpa [Nat.add_comm] using hv
    have heq := mod_shift_inj (n+1) (r.val+1) (s.val+1) (missing c).val
      (Nat.succ_pos n)
      (by omega : r.val+1<n+1) (by omega : s.val+1<n+1)
      (missing c).isLt hv'
    exact Fin.ext (by omega : r.val=s.val)
  · intro c r heq
    have hv : ((missing c).val + (r.val+1)) % (n+1)
            = (missing c).val := congrArg Fin.val heq
    have hzero : ((missing c).val + 0) % (n+1) = (missing c).val := by
      simpa using Nat.mod_eq_of_lt (missing c).isLt
    have hv' : ((r.val+1)+(missing c).val) % (n+1)
             = (0+(missing c).val) % (n+1) := by
      simpa [Nat.add_comm] using hv.trans hzero.symm
    have hbad := mod_shift_inj (n+1) (r.val+1) 0 (missing c).val
      (Nat.succ_pos n)
      (by omega : r.val+1<n+1) (by omega : 0<n+1)
      (missing c).isLt hv'
    omega

/-- Combinatorial matching-to-grid step. exchange i c is any relation
(e.g. replacing b_i by exceptional c gives a basis). The matching and
cyclic Latin completion imply every column has a legal replacement and
all repeated rows are permutations. This does not formalize Hall's theorem,
basis exchange or the full Rota conjecture. -/
theorem matching_gives_cyclic_grid (n : Nat)
    (exchange : Fin (n+1) → Fin (n+1) → Prop)
    (missing : Fin (n+1) → Fin (n+1))
    (h_matching : ∀ c d, missing c = missing d → c = d)
    (h_exchange : ∀ c, exchange (missing c) c) :
    ∃ fill : Fin n → Fin (n+1) → Fin (n+1),
        (∀ r c d, fill r c = fill r d → c = d)
      ∧ (∀ c r s, fill r c = fill s c → r = s)
      ∧ (∀ c r, fill r c ≠ missing c)
      ∧ (∀ c, exchange (missing c) c) := by
  refine ⟨cyclicRows n missing, ?_, ?_, ?_, h_exchange⟩
  exact (cyclic_rows_permutations n missing h_matching).1
  exact (cyclic_rows_permutations n missing h_matching).2.1
  exact (cyclic_rows_permutations n missing h_matching).2.2

end Hundred.Research.M080
