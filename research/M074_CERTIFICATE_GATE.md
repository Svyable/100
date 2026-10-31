# M074 certificate acceptance gate

The local solver's reported UNSAT result is **not** a certified theorem.
No independently replayed proof trace is currently in this repository.

Run only with a real proof and an independently audited proof checker:

```sh
python3 scripts/ch_certificate_gate.py --target pivot \
  --proof /path/to/complete-proof.trace \
  --checker /path/to/trusted-checker
```

The gate regenerates the frozen pivot (or regular) CNF, checks its exact
SHA-256, invokes the checker as `checker CNF PROOF`, rejects any nonzero
exit, and records the proof hash. The checker must accept the actual proof
format (DRAT/LRAT/FRAT as appropriate), check the complete derivation, and
return zero **only** for a verified contradiction. A solver exit code, an
UNSAT string, a fabricated checker, or a hash match alone proves nothing.

**Trust boundary:** This is a *replay harness*, not a built-in trusted
proof checker. Before accepting its report, independently review the checker
binary/source and version, command-line contract, proof format, negative
controls, CNF-to-graph equivalence, root and pivot relabeling, and every
external cube-coverage assumption. Capture the executable checksum and
machine-independent evidence. The harness intentionally cannot certify
a theorem merely because a user-supplied executable exits successfully.

External prior art and the unresolved mathematical scope are documented in
[M074_PRIOR_ART.md](M074_PRIOR_ART.md) and [M074_REGULARITY.md](M074_REGULARITY.md).
Do not promote the Solved ledger until all gates pass.
