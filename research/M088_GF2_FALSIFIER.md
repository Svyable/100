# M088 — exact GF(2) falsifier and a scope obstruction

**Work packet:** O-M088-01, scope SHA-256
5204bcc35834d93882867d02268da6bfe4c98a2398ff94770255bf1f624a3ae5.
**Claim:** [#108](https://github.com/Svyable/100/issues/108).
**Classification:** a bounded, self-checked negative/scope result using elementary
known finite-field algebra. **No independent mathematical review.**
**Status:** the obligation remains open; neither a hitting-set lemma nor general
PIT is proved.

## Formal polynomial versus Boolean function

The [locked class](M088_LOCK.md) permits binary XOR and multiplication gates,
at most 20 gates, syntactic degree at most 3, and queries only points of
GF(2)^n, with 0 <= n <= 8. It says that the oracle "judges" a circuit
nonzero by returning a nonzero value, but does not explicitly decide whether
"nonzero" in the hitting-set theorem means a **nonzero formal polynomial**
in GF(2)[x_0,...,x_(n-1)] or a **nonzero Boolean function** on the cube.
These are different predicates.

If **formal polynomial identity testing** is intended, no hitting set made
of GF(2)-valued input assignments can hit all nonzero circuits in this lock,
not even the full cube. A two-gate circuit computes

    g0 = x0*x0
    g1 = g0 + x0 = x0^2 + x0

Its formal monomials are distinct, so the polynomial is nonzero. Its
syntactic degree is 2, and it has 2 gates. Yet a^2+a=0 for both a=0 and
a=1. Thus it vanishes at **every** oracle point. The same circuit ignores
additional variables for any 1 <= n <= 8. This is an exact, universal
obstruction to formal-polynomial hitting sets over this evaluation domain,
not a new theorem. The oracle cannot distinguish this polynomial from zero.

If instead **nonzero Boolean function** is intended, the above circuit is
zero as a function and is **not** a counterexample. The entire cube GF(2)^n
is trivially a hitting set for nonzero functions, of size 2^n <= 256 under
the fixed n <= 8 lock. This does not prove a nontrivial polynomial-size
hitting set as n grows, nor a restricted PIT lemma. The lock must choose the
predicate before a claimed hitting-set theorem can be evaluated.

## Unambiguous candidate-set falsifier

For n=2, the proposed set S={(0,0),(1,0),(0,1)} **misses** the nonzero
function f(x0,x1)=x0*x1, represented by one multiplication gate. It vanishes
on all three points of S, but f(1,1)=1. This falsifies **that candidate set
only**, under both nonzero interpretations. It is not an obstruction to all
hitting sets of Boolean functions.

## Exact replay and adversarial controls

Run:

    python3 scripts/pit_gf2_falsifier.py --check --json
    python3 -m unittest discover -s tests -p 'test_pit_gf2_falsifier.py' -v

The falsifier accepts a JSON file with exactly circuit and hitting_set
using --input PATH. A circuit has n and gates; each gate has op (xor or mul),
a and b references to an input x0, prior gate g0, or constant 0/1.
Gates are topologically ordered, and the last gate is the output. The
checker rejects invalid operands, forward references, non-binary points,
duplicate points, out-of-range n, more than 20 gates, and syntactic degree
over 3. Constants are permitted. No input is executed as code.

One algorithm expands formal monomials with GF(2) coefficient cancellation.
A separate direct gate interpreter computes all 2^n Boolean evaluations
without consulting the expansion. Tests evaluate the resulting monomials
through a third direct product/parity loop; this is a cross-check of
implementation paths, **not** an external review. A positive control adds
(1,1) to the three-point set and rejects the claimed functional falsifier.
Invalid-input controls fail closed.

**Observed fixed-fixture results (2026-11-01):** the two-gate formal
obstruction is nonzero as a formal polynomial and zero on both points of
GF(2); the one-gate function is nonzero at (1,1) and zero at the three
candidate points. No exhaustive enumeration of all 20-gate circuits,
new hitting set, solver run, or independent reviewer is claimed.

## Prior art and exact boundary

The algebraic distinction is elementary over small finite fields.
Kaufman and Ron, *Testing Polynomials over General Fields*, SIAM Journal
on Computing (2006), DOI
[10.1137/S0097539704445615](https://doi.org/10.1137/S0097539704445615),
and Alon–Kaufman–Krivelevich–Litsyn–Ron,
*Testing Low-Degree Polynomials over GF(2)* (2003),
[DOI 10.1007/978-3-540-45198-3_17](https://doi.org/10.1007/978-3-540-45198-3_17),
provide context on low-degree testing over finite fields. Their
property-testing questions are **not** the same as this hitting-set
obligation. A recent restricted PIT result by Shpilka and Tal
([arXiv:2602.20832](https://arxiv.org/abs/2602.20832), February 2026)
uses characteristic zero or sufficiently large characteristic; it cannot
be silently imported into this GF(2) lock.

**Next falsifier/proof obligation:** settle formal polynomial vs Boolean
function semantics in the lock; if formal, expand the evaluation domain
(e.g. extension fields) or restrict to multilinear formal polynomials
and re-specify the work item. If functional, propose a nontrivial
candidate set and challenge it with this checker, then seek external
statement-fidelity review. Do not mark O-M088-01 discharged or modify
data/solved.json on this evidence.
