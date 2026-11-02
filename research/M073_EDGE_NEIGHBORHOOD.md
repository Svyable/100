# M073 — two-square edge neighborhoods sharpen the source-pinned Ising bound

**November 2, 2026 · work ID `X-M073-EDGE-NEIGHBORHOOD` · [claim #272](https://github.com/Svyable/100/issues/272).**  
**Evidence level:** author-derived restricted continuum inequality and finite exact
source certificate; **no independent specialist proof review and no historical
novelty determination**. This is not a construction of the external finite
Sidorenko host and does not resolve, affirm or refute the universal conjecture.

## Precisely bounded result

Let `H` be the 35-vertex, 66-edge point–face incidence graph of the 22
triples in [the pinned source table](../data/reference/sidorenko_faces.json).
For an equal-mass symmetric two-block graphon with matrix

```text
           [ u + delta       b ]
       W = [                   ],
           [     b       u - delta ]
```

assume `0 < u <= b <= 1`, `0 <= delta <= u`, and
`u + delta <= 1`. Put

```text
p=(u+b)/2, q=(b-u)/(b+u), h=delta/u, R=1-h^2.
```

Define three polynomials (variable `q`):

```text
D  = 1 + 5q^4 + 6q^6 + 11q^8 + 6q^10 + 3q^12,
NA = q + 2q^3 + 7q^5 + 6q^7 + 11q^9 + 4q^11 + q^13,
NB = q + 2q^3 + 6q^5 + 9q^7 +  8q^9 + 5q^11 + q^13.
KA=NA/D, KB=NB/D.
```

Let `Z_H(q)=sum_{k=0}^{22} c_k q^(2k)` be the complete even-subgraph
polynomial already proved by two finite recurrences in
[M073_INFORMATION_ALIGNMENT.md](M073_INFORMATION_ALIGNMENT.md). The
coefficients `c_k` are the 23 entries in
[data/experiments/m073_information_alignment.json](../data/experiments/m073_information_alignment.json);
in particular `c_0=1, c_2=33, c_3=88`, and all are nonnegative.

**Restricted theorem candidate (with a source-table finite premise).**
For all real parameters in the domain above,

```text
t(H,W) >= p^66 * Z_H(q) * R^E(q),
E(q) = (66 - 54 KA(q) - 12 KB(q))/4.                       (1)
```

At `h=1` the right side is interpreted as zero. For `0<q<1`,
`0<h<1`, this is a **strict improvement** over the previous
seven-vertex rung/Jensen/GKS certificate even after that older
certificate is strengthened by the **full** even-subgraph factor
`Z_H(q)`, rather than only its 4- and 6-cycle truncation. The old
exponent is `66(1-K0(q))/4` where

```text
K0(q) = (q + 2q^3 + 3q^5 + 2q^7)/(1+3q^4+4q^6).
```

This theorem is confined to the stated two-block family and the
source-pinned `H`; the exact host claimed in the September 2026
manuscript is not checked here.

## Local graph construction and finite source premise

Fix a point–face incidence edge `i-f`, with `f={i,j,k}` and
`j<k`. Each occurring point pair lies in exactly two source triples.
Write `g_ij,g_ik,g_jk` for the other faces containing the respective
pairs. These four faces and the three points `i,j,k` form the
seven-vertex, nine-edge rung graph of
[M073_RUNG_CORRELATION.md](M073_RUNG_CORRELATION.md).

Let `x_ij,x_ik,x_jk` be the third points of the three alternate
faces (outside `f`). The three points are distinct for the pinned
table. Let `h_ij` be the other face containing `{i,x_ij}`,
`h_ik` the other face containing `{i,x_ik}`, and `h_jk`
the other face containing `{j,x_jk}`.

A **square graft** along `i-g_ij` adds the three-edge path
`i-h_ij-x_ij-g_ij`, making a four-cycle. Graft a second square
along `i-g_ik` if `h_ij != h_ik`; otherwise graft along
`j-g_jk`. The source table has the following **complete finite
classification**:

| Type | Condition | Rooted incidences | Grafted rung edges |
|---|---|---:|---|
| A | `h_ij != h_ik` | 54 | `i-g_ij`, `i-g_ik` |
| B | `h_ij = h_ik` | 12 | `i-g_ij`, `j-g_jk` |

For all 66 roots, `h_ij != h_jk`. Thus the two selected new
points and two new faces are distinct, and the construction contains
**11 vertices and 15 specified edges**. Four source neighborhoods
have one *additional* incidence edge: the argument deliberately uses
only the specified 15-edge subgraph, not an unjustified claim that
every induced neighborhood has 15 edges.

This finite premise is checked in two ways: an explicit pair-to-faces
map and a separate incidence-neighbor search. Both enumerate all 66
roots and confirm the 54/12 split; both reject an adversarially
mutated source triple. The SHA-256 guard on the 22-triple table is
inherited from `m073_assortative2.load_faces`. The 54/12 split is
**not asserted** for arbitrary pair-twice triple systems.

## Exact local correlations and strict gain

For a finite graph `G`, assign uniform spins `tau_v in {-1,+1}`
and weight each edge by `1+q*tau_v*tau_w`. The high-temperature
expansion gives

```text
E_G[tau_i tau_f] =
  (sum_{S subset E(G), boundary(S)={i,f}} q^|S|)
  / (sum_{S subset E(G), boundary(S)=empty} q^|S|).
```

Direct enumeration of all `2^15=32768` edge subsets of each abstract
two-square graph yields the common denominator `D` and the
numerators `NA` and `NB` above. A *separate* direct sum over all
`2^11=2048` spin assignments agrees exactly for rational values
`q=0,1/3,3/4` (and additional test values). This is algorithmic
cross-verification, not outside mathematical review.

The strict polynomial identities are

```text
KA-KB = q^5 (1-q^2)^3 / D,                              (2)

KB-K0 = q^5 (1-q^2)^3 (1+q^2)
        * (1+3q^2+2q^4+2q^6) / (D * D0),               (3)

D0 = 1+3q^4+4q^6.
```

Every denominator is positive on `[0,1)`, and every numerator in
(2)–(3) is strictly positive for `0<q<1`. Consequently the
two-square correlations are uniformly better than the rung bound,
and the 54 A-type roots have a further strict gain.

To pass from local to full `H`, give each graph edge ferromagnetic
coupling `atanh(q)>=0`. The classical Griffiths–Kelly–Sherman
second inequality implies that adding all remaining edges of `H`
cannot decrease `E[tau_i tau_f]`. Thus each full-graph incidence
correlation is at least `KA` on the 54 A roots and `KB` on the
12 B roots.

For completeness, the earlier [AM–GM/Jensen spin-flip proof](M073_ANTIFERRO_STABILITY.md)
pairs each spin assignment with its global reversal, obtaining

```text
t(H,W)/t(H,W0) >= R^( E_mu0[M] / 2 ),
W0=[[u,b],[b,u]],
```

where `M` is the number of edges monochromatic in the original
spin labels. Flipping one bipartition turns the baseline into a
ferromagnet; for each edge `e`,
`Pr(e monochromatic)=(1-E[tau_i tau_f])/2`. The edgewise bounds give

```text
E_mu0[M] <= (66 - 54 KA - 12 KB)/2.
```

Because `0<R<=1`, the Jensen inequality yields
`t(H,W)/t(H,W0) >= R^E(q)`. Finally the exact high-temperature
identity `t(H,W0)=p^66 Z_H(q)` proves (1). The case `h=1`
follows by continuity.

## Exact rational boundary witness

Choose

```text
(a,b,c)=(12443/20000, 1, 7557/20000),
u=1/2, p=3/4, q=1/3, h=2443/10000,
R=94031751/100000000.
```

At `q=1/3` the exact source spectrum and local correlations give

```text
Z_H(1/3) = 598495823780642816000 / 328256967394537077627,
KA(1/3) = 21899/53397,
KB(1/3) = 21755/53397,
E_new = 10199/1047,
E_uniform_B = 174031/17799,
E_rung = 187/19.
```

The checker proves all three strict inequalities **by rational integer
powers**, without floating-point tolerance:

```text
Z_H(1/3)^19    * R^187    < 1,     (rung + full spectrum)
Z_H(1/3)^17799 * R^174031 < 1,     (uniform B + full spectrum)
Z_H(1/3)^1047  * R^10199  > 1.     (54/12 weighted bound) (4)
```

The corresponding rung/uniform-B/weighted lower ratios are approximately
`0.994975110`, `0.998934253` and `1.001174748`. This witness is
certified by (1) but **not even by the uniform two-square B inequality
with the complete 23-coefficient spectrum**. The 54/12 source-specific
weighting is necessary for this particular certificate. The exact actual density ratio,
computed by direct 8192-point-label summation and independently
by the source-profile histogram, is approximately `4.061229761`.
The result is a stronger *sufficient certificate*, not a near-violation
or a counterexample to Sidorenko.

## Reproduction, adversaria and failure log

From repository root:

```sh
python3 scripts/m073_edge_neighborhood.py --check
python3 -m unittest discover -s tests -p 'test_m073_edge_neighborhood.py' -v
python3 scripts/regen.py --check --fast
python3 scripts/regen.py --check
python3 -m unittest discover -s tests
```

The checker rederives the 54/12 source classification by two
independently written searches, enumerates parity polynomials from
edge subsets, checks them against direct spin sums, verifies the
strict factorization identities and uses **both** the source spin
and parity recurrences for `Z_H`. The rational witness uses exact
large-integer inequalities. Tests corrupt a source triple, introduce
a repeated point, break a square edge, test the `q` domain and
challenge both strict-gain identities.

**Failed or corrected avenues:**

- Adding only the three third points of the alternate faces makes
  dangling leaves and **does not** improve endpoint correlation.
- A uniform choice of the two squares attached at `i` fails at
  12 roots because their completion faces coincide. The B-type
  alternative restores a distinct two-square motif.
- Assuming every resulting **induced** 11-vertex neighborhood has
  exactly 15 edges is false at four roots; the proof uses a
  15-edge *subgraph*, with monotonicity handling extras.
- The first rational separation used only `1+33q^4+88q^6`,
  already dominated by the repository's full even-subgraph
  polynomial. The final witness (4) challenges the stronger
  **full-spectrum** rung certificate instead.
- A three-square 13-vertex uniform extension is obstructed by
  repeated completion faces at 12 roots; no three-square bound is
  asserted. Nothing here certifies all off-diagonal-dominant
  two-block parameters.

**Next falsifiers:** independent external proof audit of the 54/12
source classification and the Jensen/GKS transfer; independently
reimplement the two-square spin polynomials without this code; seek
a larger uniformly embeddable motif or an actual two-block negative
Sidorenko gap outside (1)'s sufficient tube. The full conjecture,
the 2026 claimed finite host, and historical novelty remain
separate questions.

## Literature and priority boundary

- [OpenAI, *A counterexample to Sidorenko's conjecture*,
  September 23, 2026](https://github.com/openai/math/tree/main/preprints/A-counterexample-to-Sidorenkos-conjecture-September-23-2026):
  source of the pinned incidence graph and the claimed external
  finite host; this work does not independently validate that claim.
- [Griffiths, *Correlations in Ising Ferromagnets. I* (1967)](https://doi.org/10.1063/1.1705219)
  and [Kelly–Sherman, *General Griffiths' Inequalities* (1968)](https://doi.org/10.1063/1.1664600):
  classical ferromagnetic correlation monotonicity.
- [Friedli–Velenik, *The Ising Model*, §3.5](https://www.unige.ch/math/folks/velenik/smbook/Ising_Model.pdf):
  high-temperature parity expansion.
- [Lovász, *Subgraph Densities in Signed Graphons and the Local
  Simonovits–Sidorenko Conjecture* (2011)](https://doi.org/10.37236/614):
  relevant local graphon inequality context.
- Existing [rung proof](M073_RUNG_CORRELATION.md) and
  [complete spectrum](M073_INFORMATION_ALIGNMENT.md), both
  author-derived and not independently accepted.

The 11-vertex motif polynomials and weighted 54/12 edgewise
certificate are **new to this repository**. They are **not claimed
historically new**: no exhaustive literature-priority search or
independent specialist review has been completed. No problem
status, solved entry, coverage allocation or separate PR-landing
workflow changes.
