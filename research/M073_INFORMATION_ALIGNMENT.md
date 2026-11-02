# M073: aligning binary labels, parity constraints and graphon densities

November 1, 2026. Work item **O-M073-02**, [claim #195](https://github.com/Svyable/100/issues/195).

**Result:** the complete even-subgraph polynomial of the pinned 35-vertex,
66-edge incidence graph is now computed by two different exact algorithms.
The newly recorded coefficients strengthen the previous quantitative bound.
This is a source-specific calculation using classical mathematics, with
independent mathematical and historical-novelty review still outstanding.
It does not resolve Sidorenko or produce a counterexample host.

## Align meanings before manipulating symbols

Let H be the incidence graph of the [pinned 22 triples on 13 points](../data/reference/sidorenko_faces.json).
The two graphon classes have mass 1/2 and block matrix W=((a,b),(b,a)),
with a,b in [0,1]. Put p=(a+b)/2, r=(a-b)/(a+b) when p>0.

| Representation | Object | Exactly preserved quantity |
| --- | --- | --- |
| Graphon | Product of 66 edge weights averaged over vertex labels | t(H,W)/p^66 |
| Spin system | Independent uniform signs at all 35 vertices | E product over uv of (1+r sigma_u sigma_v) |
| Binary linear code | Kernel of the incidence matrix over F_2 | Sum of r^weight over all codewords |
| Hypergraph coloring | Binary labels on the 13 points; A monochromatic triples | E[(1+3r^2)^A (1-r^2)^(22-A)] |

These are equalities with explicit normalization, not analogies between similar
notation. The spin and parity identities are classical high-temperature/Fourier
expansions; see [Friedli–Velenik, Section 3.5](https://www.unige.ch/math/folks/velenik/smbook/Ising_Model.pdf).
The wider code/partition-function connection is classical too:
[Forney, *Codes on graphs: Duality and MacWilliams identities*](https://arxiv.org/abs/0911.5508).
The source-specific complete spectrum below is the new-to-project output;
these citations are not evidence of its historical novelty.

## Exact representation theorem

The following identity applies to the incidence graph of **any finite family
of triples**, including repeated triples as distinct face vertices. Let n be
the number of points and f the number of faces. For a point-sign assignment s,
let A(s) be the number of faces with three identical signs. Then

\[
 Z_H(r):=\sum_{S\subseteq E(H):\,\partial S=0}r^{|S|}
 =2^{-n}\sum_{s\in\{-1,1\}^n}
 (1+3r^2)^{A(s)}(1-r^2)^{f-A(s)}. \tag{1}
\]

Here partial S is the vector of vertex degrees modulo two; every edge subset
has coefficient one before collecting by cardinality. Equation (1) is a
polynomial identity for all real r, independent of graphon restrictions.

**Proof.** Expand the spin product over all edges. Independence and
E[sigma^k]=0 for odd k, 1 for even k, annihilate exactly the subsets with
nonzero degree parity. This gives the left side. Alternatively integrate the
sign tau at a face {u,v,w} first:

\[
\tfrac12\sum_{\tau=\pm1}
 (1+r\tau s_u)(1+r\tau s_v)(1+r\tau s_w)
 =1+r^2(s_us_v+s_us_w+s_vs_w).
\]

The parenthesized sum is 3 when the three signs agree and -1 otherwise.
Face signs are independent conditional on point signs. Multiplying these
f factors and then averaging over all point signs proves (1).
Finally W(s,t)=p(1+rst), so t(H,W)=p^(3f) Z_H(r) for the stated graphons.

There is a complementary direct recurrence. At each degree-three face, an
even edge subset chooses either no edges or one of its three edge pairs.
Track the XOR of the selected point endpoints and the number k of chosen
pairs. Starting from state (0,0) with count one, each face adds the four
possible transitions. At the end the counts in parity state zero are
exactly the coefficients of r^(2k). Every selection has a unique sequence
of local choices, so this recurrence neither omits nor duplicates a subset.
It uses no spin transform or cancellation and checks every coefficient.

## Complete pinned spectrum and consequences

Writing x=r^2, Z_H(r)=sum from k=0 to 22 of c_k x^k, the coefficient vector is

```text
[1, 0, 33, 88, 823, 4232, 24831, 127584,
 603274, 2540960, 9417578, 30237520, 83066126,
 192776048, 373654910, 599077600, 785645157,
 830015520, 690493733, 436109080, 196772043,
 56595016, 7805139]
```

The [machine-readable certificate](../data/experiments/m073_information_alignment.json)
also records the full histogram of A and the source digest. This recovers the
weight distribution of all **2^32 = 4,294,967,296** even subgraphs from
**2^13 = 8,192** point-label assignments. These are state counts, not a claim
of a measured 524,288-fold runtime speedup. No individual enumeration of
billions of subgraphs is performed. The previous face-elimination engine
already exploited the 13-point structure for numeric evaluation; this work
extracts the entire polynomial and adds a combinatorial coefficient check.

Because every c_k is nonnegative, for all graphons in the stated family,

\[
 t(H,W)\ge p^{66}\bigl(1+33r^4+88r^6+
 823r^8+4232r^{10}+24831r^{12}\bigr). \tag{2}
\]

For p>0 and a unequal to b, (2) is strict since c_7=127584>0.
The displayed bound strictly improves the earlier 1+33r^4+88r^6 bound
whenever a differs from b. At a=b it equals p^66. When a=b=0, treat the
case separately: the density and bound are both zero, and r is undefined.

Three additional concrete deductions illustrate what the alignment reveals:

1. **823 is not the eight-cycle count.** It splits as 361 simple eight-cycles
   plus 462 distinct unions of two edge-disjoint four-cycles. Such unions
   may share a point vertex. A separate cycle DFS and edge-set census verify
   this split; confusing cycle counts with even-subgraph counts would miss it.
2. The leading coefficient **7,805,139** counts the even subgraphs containing
   two edges at every face (44 edges total). Larger even subgraphs cannot
   exist, because each of the 22 degree-three face vertices has selected
   degree zero or two.
3. There are **96 labeled two-colorings of the 13 points with no
   monochromatic face** (48 up to global color reversal), from histogram
   entry A=0. This is a coloring fact about the pinned hypergraph, not a
   Sidorenko counterexample.

## Checks, limits and next useful transfer

Run:

```sh
python3 scripts/m073_information_alignment.py --check
python3 -m unittest discover -s tests -p 'test_m073_information_alignment.py' -v
python3 scripts/regen.py --check
```

Validation compares all coefficients from the spin-histogram transform and
the parity-state recurrence, and separately evaluates six exact weight pairs
using the existing pairwise-edge factor eliminator. Tests exhaust all 16
triple systems on four points by direct edge-subset enumeration, include
isolated points and repeated triples, and reject changed coefficients,
changed histograms and invalid domains. Relabeling and the 823 decomposition
provide further controls. The coefficient sum 2^32 matches the connected
graph's cycle-space dimension 66-35+1=32; it is a checksum, not a standalone
proof of each coefficient. These are separate algorithms written/run by the
same author, **not independent human review or Lean verification**.

The scalar histogram A is sufficient because the point signs are uniform
and the two diagonal weights agree. Unequal class masses need at least
joint information about A and label population; unequal diagonal entries
need richer local face-type counts. The polynomial must not be transferred
to those domains without a new identity. O-M073-01 remains open, and
O-M073-02 remains open pending independent proof/scope review.

The reusable research method is: specify one invariant, give exact maps
between representations, carry normalization and assumptions through every
map, derive a consequence that was not recorded, and check it through a
different representation. Symbol alignment exposes previously uncomputed
consequences of the input; it does not supply new empirical information or
establish priority by itself.
