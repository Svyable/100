# Frankl triple-local counterexamples: two inclusion-minimal certificates

**Result scope:** exact finite exhaustive statements about two **fixed,
published families**. These are not counterexamples to Frankl's conjecture,
not globally smallest triple-local counterexamples, and not independently
accepted novel mathematical theorems. Recorded 2026-10-31.

## The precise bounded theorem

Fix a union-closed family F and a designated exact three-element member
T={a,b,c}. Call F a *triple-local falsifier* if each of a,b,c appears in
strictly fewer than |F|/2 members of F.

A falsifier F is **inclusion-minimal relative to itself** if no proper
subfamily G ⊊ F is simultaneously union-closed, contains the same exact T,
and remains a triple-local falsifier.

An exact DPLL search verifies this inclusion-minimality separately for:

- **van der Hout–Roos (2026)**: 19 sets on seven elements, including ∅.
  Frequencies of the selected triple are (9,9,9), and the other four are
  (14,14,14,17). Source: [DOI 10.23952/jano.8.2026.1.02](https://doi.org/10.23952/jano.8.2026.1.02),
  Figure 1. The 19×7 incidence matrix was transcribed and independently
  checked for union closure.
- **Sarvate–Renaud (1990)**: 27 sets on nine elements, *without* ∅;
  selected triple frequencies are (13,13,13).
  Source: [published family transcription](https://mathoverflow.net/questions/138567/renaud-sarvate-limitation-on-frankls-conjecture).

The fact that both happen to be inclusion-minimal **does not** mean 27
is the smallest possible example. The 2026 paper exhibits a distinct
19-set family. The claims are restricted to the inclusion order on
subfamilies of each fixed example and should undergo literature review
before being described as original.

## An exact, independently reproducible exhaustive proof procedure

For each original set S_i, introduce a binary member variable x_i.
A subfamily is union-closed iff for every i,j and k such that
S_k=S_i∪S_j the implication x_i=x_j=1 ⇒ x_k=1 holds.

For each selected triple element t, its frequency is strictly less than
half the subfamily size iff

    Σ_i (2·[t∈S_i] − 1) x_i ≤ −1.

We force the index of T to be present and, in separate branches,
force **each other original set** to be absent. Every *proper*
subfamily has at least one such absent original set, so this is a
complete cover of the possibility space.

For each branch the DPLL algorithm applies only valid logical inferences:
(a) union-closure forward and backwards implications; (b) a lower bound
on each signed-frequency expression by minimizing every still-free
coefficient; and (c) when the bound exactly saturates −1, forcing all
free variables to their minimizing values. The remaining choices are
exhaustively branched both ways. Any survivor is independently tested
for closure, the triple, and all three frequency inequalities.

The 19-set case explores **1,516 nodes** across 18 forced exclusions,
with 82 nontrivial closure implications, and finds no survivor.
The 27-set case explores **17,944 nodes** across 26 forced exclusions,
with 211 nontrivial closure implications, and finds no survivor.

These counts are regression fingerprints of the exact deterministic
search, not formal proof certificates in another proof assistant.

## Positive control: an augmented family really is reducible

Adding ∅ to the published 27-set family preserves union closure and the
triple-local failure. The algorithm finds a **19-member proper subfamily**
still falsifying the same triple-local assertion. This demonstrates that
the checker can detect nonminimality and is not a tautological test.
That 19-member subfamily is not asserted equal or isomorphic to the
independently published 2026 seven-element example.

## Reproduce

\`\`\`sh
python3 scripts/frankl_subfamily_minimal.py examples/FRANKL_VAN_DER_HOUT_ROOS_19.json --assert-minimal
python3 scripts/frankl_subfamily_minimal.py examples/FRANKL_SARVATE_RENAUD.json --assert-minimal
python3 -m unittest discover -s tests -p "test_frankl_subfamily_minimal.py" -v
\`\`\`

This is a useful reusable finite **lemma-falsification and witness-
simplification instrument**. The project should not increase the parent
M075 rank or Solved count on this basis. Research next: locate a genuine
structural lemma allowing search beyond one fixed family's subfamilies.
