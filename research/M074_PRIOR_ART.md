# M074 — external fixed-outdegree-six proof claim: verification docket

**Intake:** 2026-10-31. **Disposition:** substantial external proof claim, **not
independently accepted here**. Do not market the fixed-`r=6` case as a fresh,
unclaimed result without examining this work.

## Exact claim

The project [Josh P., *Fixed outdegree six in the Caccetta–Häggkvist
conjecture*](https://github.com/joshp123/solve-a-maths-problem-dont-care-which-make-no-mistakes)
claims that **every finite loopless simple digraph** with minimum outdegree
at least 6 has a directed cycle of length at most `ceil(n/6)`. It does
**not** claim the unrestricted conjecture for all `r`.

The repository calls itself an **unpublished computer-assisted proof that
has not been peer reviewed**. Version 0.2.0 and the cited archived DOI
`10.5281/zenodo.21495432` identify the package. A separate 2026 computer
search [wustep/maths Caccetta–Häggkvist record](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md)
reports further finite SAT exclusions. Neither independent repo should
be treated as a journal acceptance.

## Claimed proof corpus identity — NOT YET REPLAYED IN THIS REPOSITORY

| Property | Value, as published by the claim's authors |
|---|---|
| Source version | `0.2.0` |
| Archive | `proof-corpus-v0.1.0.tar.zst` |
| Compressed size | 438,808,162 bytes |
| Published SHA-256 | `3d00174851a213fdf81085bd38bbb7e573f36f8b1e691e5eded8ac43d8937285` |
| Quick replay | `./verify.sh --quick` |
| Full replay | `./verify.sh --full` |
| Reported resource requirements | ≈ 8 GiB RAM, 16 GiB free disk; C99 compiler, Python, zstd, and CaDiCaL for full replay |

Source: [upstream README](https://github.com/joshp123/solve-a-maths-problem-dont-care-which-make-no-mistakes/blob/main/README.md)
and [reproduction guide](https://github.com/joshp123/solve-a-maths-problem-dont-care-which-make-no-mistakes/blob/main/REPRODUCING.md).

**No claim that we downloaded, hashed, ran, or independently certified the
438 MB corpus is made.** The published checksum is a *target for future
verification*, not a checksum already established by Svyable.

## Two independent kinds of verification

1. **Computational replay**: fetch the pinned source, reproduce the archive
   SHA-256 and all frozen CNF/proof hashes, and run the upstream quick/full
   verification. Capture replay outputs, exit status, tool versions, and
   hardware requirements.
2. **Mathematical audit**: independently read the original theorems P1–P4,
   test graph-to-CNF implication, justify every branch reduction, inspect
   the `n=18` regularity and symmetry arguments, and check the `n=54`
   contradiction. A proof checker cannot establish the correctness of a
   hand-written mathematical reduction that produced its formula.

An independent audit should test deliberately corrupted proof data as a
negative control. A successful archive hash alone does not establish the
mathematical theorem. A successful proof replay does not automatically imply
that the manuscript has been peer reviewed.

## Local complement: two genuinely independent CNF formulations

The [direct minimum-outdegree encoder](../scripts/ch_sat.py) and
[compact exact-outdegree encoder](../scripts/ch_compact.py) encode different
arc-assignment spaces but search for the same existence of a counterexample.

Every minimum-outdegree-`r` counterexample contains an exact-outdegree-`r`
spanning subgraph: delete surplus outgoing arcs. Deleting arcs **cannot
create** a directed 2-cycle, 3-cycle or any shorter cycle. Therefore
satisfiability is equivalent, although a satisfying assignment in one
encoding is not literally the same SAT variable assignment as in the other.

For `n=18,r=6`:

| Feature | Direct min-degree | Compact exact-degree |
|---|---:|---:|
| Arc variables | 306 | 306 |
| Auxiliary variables | 0 | 1,764 |
| Clauses | 113,169 | **8,445** |
| Encoded CNF bytes | 5,125,375 | **127,597** |
| Proof result | Not solved | Not solved |

The compact representation has **13.4× fewer clauses**, but may or may not
solve faster. It includes new auxiliary prefix-threshold variables. A smaller
CNF is not a proof and is not a guaranteed runtime improvement.

The compact gate recurrence is
`z[i,j] <=> z[i-1,j] OR (x[i] AND z[i-1,j-1])`.
Its four CNF implications are truth-table tested. The final constraints
`z[m,r]` and `NOT z[m,r+1]` require **exactly** `r` outgoing arcs.
Every arc assignment in the bounded test cases is independently checked
against the expected graph semantics. The prefix completion is unique
because each gate is a logical equivalence, so projecting away auxiliary
variables leaves exactly the intended arc assignments.

Commands:

```sh
python3 scripts/ch_sat.py cnf --n 18 --r 6 --output /tmp/ch18_direct.cnf
python3 scripts/ch_compact.py --n 18 --r 6 --output /tmp/ch18_compact.cnf
sha256sum /tmp/ch18_direct.cnf /tmp/ch18_compact.cnf
python3 -m unittest discover -s tests -p 'test_ch_compact.py' -v
```

Expected compact SHA-256:
`8a2eebf9618bbc9b5dcf2c1fcc5f35736acf852d6466869cb569641fafc00fca`.

## Review decision tree

- **Full independent proof established for fixed `r=6`:** record the
  restricted result and supporting independent reviews; continue targeting
  the unrestricted CH conjecture and non-overlapping methods. The Solved
  archive remains empty for M074.
- **Unresolved hand-reduction gap:** document its exact location, construct
  the smallest failing example or missing lemma, and retain the claim as
  unverified.
- **Insufficient replay resources:** log the missing proof asset/checker
  explicitly. No proof promotion.
- **Independent finite result:** record its exact `n,r` scope and certificate
  identity; do not infer an all-`n` or all-`r` theorem.

**Priority:** independent review of the external claim outranks a fresh,
unverified duplicate search at `(18,6)`.
