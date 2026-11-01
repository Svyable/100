# Adversarial lemma gates — refute false extensions before proof search

**Research instrument, 2026-10-31.** This is not a newly proved open conjecture.
The fixture registry is deliberately outside generated website pages; CI
replays it directly.

## Why this is a priority

Mathematical agents often take a legitimate local theorem and try to
strengthen it by deleting one hypothesis or tightening one inequality.
That is a reasonable discovery strategy, but an **existing finite
counterexample can instantly invalidate a whole branch of proposed proofs**.

The negative-control registry
[lemma_adversaries.json](../data/lemma_adversaries.json) freezes four
cross-domain checks (three *false auxiliary* claims and one positive
known-theorem example). Each record states its EXACT proposition, source,
classification and machine-verifiable numeric fingerprint.

\`\`\`sh
python3 scripts/lemma_adversary.py --check
python3 -m unittest discover -s tests -p "test_lemma_adversary.py" -v
\`\`\`

| ID | Precisely tested claim | Outcome | Boundary |
|---|---|---|---|
| A-M075-TRIPLE | If a union-closed family contains a given triple, one of the triple's three elements is abundant | **False**: published 27-set counterexample, each selected element appears 13/27 times | Does **not** refute Frankl |
| A-M075-DOUBLET | A union-closed family containing an exact doubleton has an abundant element inside it | **True, known**: injection argument; the checker reproduces a sharp 2-set instance | It does **not** certify the universal argument merely by running examples |
| A-M074-DEFECT | Outregular and maximum indegree <=r+1, without further saturation, forces no low-to-low arcs | **False**: explicit 6-vertex, 2-outregular graph with two low-to-low arcs | Does **not** refute the properly conditioned degree-defect theorem |
| A-M074-NINE-28 | Nine-vertex oriented directed-triangle-free graphs of minimum outdegree two have at most 28 arcs | **False**: nine-vertex 29-arc sharp construction | Does **not** refute the valid upper bound 29 or CH |

The direct checkers are backed by *separate* elementary oracles: set-of-sets
union closure and exact membership counts; adjacency-matrix degree counts;
directed-triangle and digon detection. Tests mutate statuses, fixture
paths, frequencies, witness arcs, and problem assignments to ensure failures
are not silently misclassified as mathematical successes.

## Stop rule for generated lemmas

Before promoting any new lemma, a contributor must:

1. State exact quantifiers, including all conditions that were weakened
   from the originating theorem;
2. Check every **applicable** adversarial-control witness, not just the
   conjecture-level counterexample search;
3. Exhibit a nonvacuous model of the antecedent when testing a proposed
   theorem derived from a conjecture's counterexample assumptions, or
   explicitly mark nonvacuity as unknown;
4. Record whether a failure is an auxiliary-hypothesis falsification,
   a known theorem reproduction, a new restricted theorem, or a verified
   counterexample to the **exact full** conjecture;
5. Demand independent mathematical scope review before giving a new
   result any rank or Solved credit.

The registry uses allowlisted evaluators, not arbitrary user-supplied
Python or theorem-string evaluation. It proves no arbitrary theorem false
or true. Additional evaluators must come with exact statement-level
tests, independent witness checking, and prior-art citations.

**Next valuable step:** integrate these applicability checks into the
proof-exchange review workflow so that parallel agents cannot quietly
reintroduce the same false auxiliary lemmas. This will be a separate,
CI-gated change; the present executable registry is the frozen baseline.

Primary examples:
- [Sarvate–Renaud triple-local boundary](notes/M075_PAIR_BOUNDARY.md).
- [Degree-defect saturation theorem](../proofs/DEGREE_DEFECT_TRANSFER.md).
- [Sharp nine-vertex CH local lemma](../proofs/M074_NINE_VERTEX.md).

No active rank or \`data/solved.json\` entry is changed by these controls.
