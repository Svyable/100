# M073 — a seven-vertex rung improves the two-block stability certificate

**2026-11-01 · X-M073-RUNG-CORRELATION · [claim #167](https://github.com/Svyable/100/issues/167).**

**Status:** Author-derived restricted inequality, not independently reviewed or
established novel. This is a stronger *sufficient condition* on an equal-mass,
off-diagonal-dominant two-block graphon for the source-pinned 35-vertex,
66-edge incidence graph H. It neither resolves Sidorenko's conjecture nor
constructs the finite host alleged in the September 2026 preprint.
The Ising correlation monotonicity input is classical, not our theorem.

## The new local motif

Let F be a simple 3-uniform hypergraph with the following **local pair
multiplicity property**: whenever a pair {x,y} occurs in a triple, it occurs
in exactly two distinct triples. Let H(F) be its point–triple incidence graph.

**Rung lemma.** Every incidence edge i–f, with f={i,j,k}, lies in a
seven-vertex, nine-edge subgraph consisting of

- the edge i–f;
- the two internally disjoint three-edge paths
  i–g_ij–j–f and i–g_ik–k–f; and
- a two-edge rung j–g_jk–k.

Here g_xy is the unique triple other than f containing {x,y}.
The three auxiliary triples are pairwise distinct: if, for example,
g_ij=g_ik, that triple contains i,j,k and therefore equals f,
contradicting the definition of g_ij. The same argument applies to
the other pairs. All seven vertices are distinct and all nine edges
are present. This proves the lemma.

The source-pinned M073 table has 22 triples on 13 points, 33 occurring
point-pairs, and **every occurring pair occurs exactly twice**.
Consequently the lemma applies to **all 66** incidence edges.
The checker constructs and validates all 66 actual subgraphs; it does
not infer their existence merely from the number of four-cycles.

## Exact ferromagnetic endpoint correlation

For a finite graph G, give independent spins tau_v in {-1,+1} the
zero-field ferromagnetic weight

    product_{uv in E(G)} (1 + q*tau_u*tau_v),    0 <= q < 1.

The usual high-temperature expansion says that the denominator of the
two-point correlation at vertices i,f is the generating polynomial of
even-degree edge subsets, while the numerator is the polynomial of
edge subsets with odd-degree boundary {i,f}. For the rung motif,
enumerating its 2^9 edge subsets (or a short parity argument) gives

    D(q) = 1 + 3*q^4 + 4*q^6,
    N(q) = q + 2*q^3 + 3*q^5 + 2*q^7.

Therefore its **exact** endpoint correlation is

    K(q) = N(q)/D(q)
         = q*(1 + q^2 + 2*q^4)/(1 - q^2 + 4*q^4).       (1)

The prior two-bypass subgraph (without the rung) has correlation

    K0(q) = (q + 2*q^3 + q^7)/(1 + 2*q^4 + q^6).

Clearing denominators, the improvement is the polynomial identity

    N(q)*(1+2*q^4+q^6)
      - (q+2*q^3+q^7)*D(q)
      = 2*q^5*(1-q^2)^3*(1+q^2).                      (2)

All denominators are positive for 0<=q<1. Thus K(q)>K0(q)
for every 0<q<1, with equality at q=0 and in the q→1 limit.

For the *full* H(F), the classical Griffiths–Kelly–Sherman second
correlation inequality (GKS-II) implies that adding the remaining
nonnegative ferromagnetic couplings cannot decrease the correlation
of the fixed endpoints. Hence every incidence edge of the pinned H
has ferromagnetic correlation **at least K(q)**.

This is a structural improvement over the previously merged
[two-bypass estimate](M073_ANTIFERRO_STABILITY.md), not a new
ferromagnetic correlation principle.

## Stronger M073 inequality

Consider an equal-mass symmetric two-block graphon with matrix

    W = [[u+delta, b], [b, u-delta]],

where 0<u<=b<=1, 0<=delta<=min(u,1-u). Put

    p=(u+b)/2, q=(b-u)/(b+u), h=delta/u.

The previously established spin-flip pairing, AM–GM and Jensen argument
gives for every bipartite F with m edges

    t(F,W)/t(F,W0) >= (1-h^2)^[m*(1-C)/4],

provided C is a common lower bound on the ferromagnetic edge
correlations of F after flipping spins on one bipartition, and
W0=[[u,b],[b,u]]. This follows because the expected number of
monochromatic edges is at most m*(1-C)/2.

For the pinned 66-edge H, use C=K(q) from (1). The earlier
even-subgraph bound t(H,W0)>=p^66*(1+33*q^4+88*q^6)
then proves the **continuous-parameter inequality**

    t(H,W) >= p^66 * (1+33*q^4+88*q^6)
                    * (1-h^2)^[66*(1-K(q))/4].        (3)

For h=1 interpret the right side by continuity (it is zero).
The inequality holds for all real weights in the stated domain.
Its right side is a strict improvement over the previous two-bypass
bound when 0<q<1 and 0<h<1; it is not always at least p^66.
The domain is only a restricted two-block graphon family.

## An exact rational host the old certificate cannot certify

Choose

    (a,b,c) = (241/400, 1, 159/400).
    u=1/2, delta=41/400, p=3/4, q=1/3, h=41/200.

At q=1/3 the two-bypass bound has K0=223/561 and exponent
66*(1-K0)/4=169/17. The rung has K=23/57 and exponent
66*(1-K)/4=187/19. The common cycle factor is

    1+33*(1/3)^4+88*(1/3)^6 = 1114/729.

Write R=1-h^2=38319/40000. Exact rational comparisons give

    (1114/729)^17 * R^169 < 1,                     (4)
    (1114/729)^19 * R^187 > 1.                     (5)

Thus the **old** source-specific sufficient condition does not
certify Sidorenko for this host, but the **new** rung bound does.
The new certified ratio exceeds 1.0014828. The exact density ratio
is approximately 3.224523, independently computed by three
algorithms (point-label sum, histogram compression, and pairwise
factor elimination). The actual density is much larger than either
bound; the gain is in the rigorously certified region, not a claimed
near-counterexample.

## Reproduction and adversarial falsifiers

Run from the repository root:

    python3 scripts/m073_rung_correlation.py --check
    python3 -m unittest discover -s tests -p 'test_m073_rung_correlation.py' -v
    python3 scripts/regen.py --check

The source is loaded with the existing SHA-256 guard
653fd38252aa4034512303dd71d738a42cc3685666b982d41f21c76c336c4b02
on the canonical 22-triple array. The checker enumerates all 66
motifs, all 512 rung edge subsets, and 128 independent spin
assignments for each of five rational couplings. It independently
recomputes the two correlation polynomials and the exact threshold
comparisons; it also compares three independent source-density
algorithms on the rational example.

Adversarial controls: mutating a source triple destroys the required
pair multiplicity; deleting one of the two rung edges makes the
extra vertex a leaf and recovers exactly the **old** two-bypass
correlation; negative or out-of-range coupling values fail closed.
The 66-edge source audit, not a sampled graphon grid, is the
finite premise of the continuum proof. A code pass is not an
independent mathematical review.

**Failed avenue:** A third internally vertex-disjoint bypass from i
to f cannot exist in this motif: f has degree three, and its two
neighbors other than i are already used by the two length-three
bypasses. Adding the *rung* instead of a third bypass produces the
strict improvement (2).

## Literature, novelty boundary and next falsifier

- [OpenAI, *A counterexample to Sidorenko's conjecture* (2026)](https://github.com/openai/math/tree/main/preprints/A-counterexample-to-Sidorenkos-conjecture-September-23-2026), with pinned [incidence table](../data/reference/sidorenko_faces.json). The general finite-host claim is not verified here.
- [Griffiths, *Correlations in Ising Ferromagnets. I* (1967), DOI 10.1063/1.1705219](https://doi.org/10.1063/1.1705219), the classical positivity/monotonicity framework.
- [Kelly and Sherman, *General Griffiths' Inequalities on Correlations in Ising Ferromagnets* (1968), DOI 10.1063/1.1664600](https://doi.org/10.1063/1.1664600), the GKS-II input.
- [Prior M073 antiferromagnetic stability note](M073_ANTIFERRO_STABILITY.md), whose spin-flip/Jensen argument is reused unchanged.

The exact nine-edge motif polynomial and numerical application were
derived for this repository; **a comprehensive priority/novelty audit
against all published correlation bounds has not been completed**.
No specialist independent proof review exists. Do not mark M073 solved
or change its evidence state or the accepted-results ledger.

**Next falsifier:** Seek a stronger, still source-certified subgraph
around each incidence edge that increases the uniform correlation
bound beyond K(q), or find an exact rational two-block host outside
(3)'s sufficient tube with a *negative* ordinary Sidorenko gap.
Any proposed general result requires an independent proof and
literature audit.
