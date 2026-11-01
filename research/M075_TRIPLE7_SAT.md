# M075 — seven-element triple-local optimization

**Status:** exact, audited SAT *encoding*; first resource-bounded search **inconclusive**. This is issue [#95](https://github.com/Svyable/100/issues/95), not an assertion about Frankl's original conjecture.

## Perceive

The independently checked 19-set example of van der Hout–Roos (2026; [source](https://doi.org/10.23952/jano.8.2026.1.02)) is union-closed on seven points, includes the empty set and the exact triple T={0,1,2}, and has triple frequencies (9,9,9) out of 19. This disproves a stronger **triple-local** assertion, *not* Frankl's original existential one. Other points appear in more than half the sets.

Our existing inclusion-minimality checker rules out a **proper subfamily of this specific example** with the same triple-local failure. It does not rule out a different family of size 18 or less.

## Decide — exact global finite predicate

Fix n=7 and T={0,1,2}. There are exactly **128 subsets** of the universe; Boolean variable x_S (DIMACS identifier S+1, for bitmask S) represents membership of S in a family. For each **separate exact size** k=2,3,...,18, require:

1. Include the empty set and the exact triple T.
2. For every A and B, (x_A AND x_B) implies x_(A union B).
3. Exactly k of the 128 Boolean membership variables are true.
4. For each t in T, at most floor((k-1)/2) selected sets contain t.

These conditions are exactly the seven-element counterexample search. There is no unjustified full-support constraint, no symmetry reduction, no change to the original Frankl conjecture.

A definitional prefix counter encodes at-least-j: g(i,j) iff g(i-1,j) OR (x_i AND g(i-1,j-1)), with g(0,0)=true and g(0,j>0)=false. Four standard Tseitin implications define each auxiliary variable. Every set-membership vector has a uniquely determined auxiliary extension. Independent tests exhaust all 256 set families on n=3 across five exact sizes, fuzz n=4, and verify the real 19-set n=7 control both directly and through the CNF.

## Act — reproduce the experiment

From the repository root:

~~~sh
python3 scripts/frankl_triple_sat.py --check-witness examples/FRANKL_VAN_DER_HOUT_ROOS_19.json
python3 scripts/frankl_triple_sat.py --size 18 --out /tmp/triple18.cnf
python3 scripts/frankl_triple_sat.py --size 17 --out /tmp/triple17.cnf
python3 scripts/frankl_triple_experiment.py --check-record data/experiments/frankl_triple7_pilot.json
python3 -m unittest discover -s tests -p 'test_frankl_triple_sat.py' -v
python3 -m unittest discover -s tests -p 'test_frankl_triple_experiment.py' -v
~~~

The optional solver pilot uses python-sat (with CaDiCaL195); it is *not* a mandatory CI dependency. Reproduce in an isolated environment:

~~~sh
python3 -m venv /tmp/frankl-sat-venv
/tmp/frankl-sat-venv/bin/pip install 'python-sat==1.9.dev17'
/tmp/frankl-sat-venv/bin/python scripts/frankl_triple_experiment.py --sizes 18,17 --conflicts 200000 --out /tmp/triple-pilot.json
~~~

An actual local pilot used Python 3.14.2, python-sat 1.9.dev17, CaDiCaL195, with a 200,000 conflict cap per size. The immutable observed JSON is at [data/experiments/frankl_triple7_pilot.json](../data/experiments/frankl_triple7_pilot.json).

| Exact size | CNF variables | CNF clauses | Observed conflicts | Result |
|---:|---:|---:|---:|---|
| 18 | 4,009 | 21,234 | 200,002 | **unknown** (budget exhausted) |
| 17 | 3,899 | 20,795 | 200,005 | **unknown** (budget exhausted) |

These are real, recorded resource-limited experiments with pinned CNF hashes, **not** proof of impossibility at either size. The checker rejects substituted source hashes, fake promoted statuses, malformed witness data, and inconsistent resource records.

## Evidence boundary and next decision

A model labelled SATISFIABLE with literal lines (prefixed v) can be checked via:

~~~sh
python3 scripts/frankl_triple_sat.py --size 18 --verify-model /tmp/solver-model.txt
~~~

The program checks the canonical auxiliary assignment against all generated clauses and then independently checks original set operations, closure, exact size, mandatory members, and strict triple frequencies. A valid model of size at most 18 **refutes** the proposed fixed-universe lower bound.

An UNSAT return alone establishes **nothing independently**. Proving a global 19-set minimum for the stated seven-element problem requires independent, correct, proof-checker-accepted UNSAT certificates for *all 17 sizes from 2 through 18*, the statement scope and clauses audited, and a genuine prior-art/specialist review. A source hash is not a proof trace. No result here modifies the solved, theorem-review, or 36-agent-trial ledgers.

**Next targeted research action:** design and separately prove safe permutation-symmetry breaking for S3 acting on T and S4 on the other points; benchmark against equal conflict budgets and obtain proof-producing SAT traces with an independently pinned DRAT/LRAT checker if possible. Do not count unknown runs as negative mathematics.
