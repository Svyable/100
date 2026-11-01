# M073 — a bipartite antiferromagnetic two-block stability inequality

**2026-11-01 · work ID `X-M073-ANTIFERRO-STABILITY` · [claim #165](https://github.com/Svyable/100/issues/165).**

**Evidence:** A self-contained author-derived *restricted continuum inequality*, with exact rational and adversarial checks. The proof combines elementary spin-flip pairing, AM–GM, Jensen, and the classical positive-coupling Ising high-temperature expansion. **Neither novelty over prior literature nor independent mathematical acceptance has been established.** This does not establish Sidorenko for arbitrary graphons, recover the claimed finite host, or change the portfolio's evidence state.

## General bipartite stability lemma

Let `F` be **any finite simple bipartite graph** with `m >= 1` edges. Give two graphon blocks equal measure 1/2 and write

```text
       [ u + delta     b ]
  W =  [                 ],      W0 = [ u  b ; b  u ].
       [     b     u - delta ]
```

Assume `0 < u <= b <= 1`, `0 <= delta <= u`, and `u+delta <= 1`. Define

```text
q = (b-u)/(b+u),             h = delta/u.
```

**Theorem.** For every such `F`,

```text
t(F,W) >= t(F,W0) * (1-h^2)^(m*(1-q)/4).                 (1)
```

This is a *relative* lower bound, not an unconditional Sidorenko theorem for every host. It is useful when a quantitative bound for `W0` is already known. At `h=1`, interpret (1) by continuity (the right side is zero). All inequalities below are exact over the stated real domain.

### Proof: pair opposite spin assignments

Assign independent uniform spins `sigma_v in {-1,+1}` to vertices of `F`. In an assignment let `M_+` be the number of edges whose endpoints both carry `+1`, `M_-` the number whose endpoints both carry `-1`, and `M=M_++M_-` the total monochromatic-edge count. Write `P0(sigma)` for the product of edge weights under `W0`. For `0 <= h < 1`,

```text
P_W(sigma)  = P0(sigma) (1+h)^M+ (1-h)^M-,
P_W(-sigma) = P0(sigma) (1+h)^M- (1-h)^M+.
```

The global spin flip preserves `P0`. Applying arithmetic–geometric mean to the two displayed products gives

```text
[P_W(sigma)+P_W(-sigma)]/2
  >= P0(sigma) (1-h^2)^(M/2).
```

Let `mu0` be the probability measure on spin assignments proportional to `P0`. Summing the paired inequality and applying Jensen to the convex function `x -> (1-h^2)^(x/2)` yields

```text
t(F,W)/t(F,W0)
  >= E_mu0 [(1-h^2)^(M/2)]
  >= (1-h^2)^(E_mu0[M]/2).                              (2)
```

### Proof: the antiferromagnetic edge correlation bound

Fix a bipartition `L,R` of `F`. Flip the spin of every vertex in `R` and call the resulting spins `tau`. For every edge `vw`, the `W0` weight becomes

```text
p (1+q tau_v tau_w),    p=(u+b)/2,    0<=q<1.
```

This is a **zero-field ferromagnetic Ising** measure. Its two-point correlations are nonnegative: expand `product_e(1+q tau_v tau_w)`; the denominator is the sum of `q^|S|` over even-degree edge subsets `S`, while the numerator for `E[tau_v tau_w]` sums over subsets with odd-degree boundary `{v,w}`. Every summand is nonnegative.

For an **edge** `e=vw`, remove `e` temporarily, and let `C >= 0` be the resulting two-point correlation. Restoring its factor `1+q tau_v tau_w` gives

```text
E[tau_v tau_w] = (C+q)/(1+q*C) >= q,
```

because `0<=C<=1`. Undoing the bipartite spin flip,

```text
E_mu0[sigma_v sigma_w] <= -q
Pr_mu0(sigma_v=sigma_w) <= (1-q)/2.
```

Sum this over all `m` edges: `E_mu0[M] <= m(1-q)/2`. Since `0 < 1-h^2 <= 1`, (2) implies (1). The case `h=1` follows by continuity. **Bipartiteness is essential to the gauge argument**; it has not been removed. □

## Application to the pinned M073 incidence graph

The source-pinned graph `H` has **35 vertices and 66 edges**, defined by 22 triples on 13 points in [the pinned source table](../data/reference/sidorenko_faces.json). Its independently counted simple cycles number `c4=33`, `c6=88`. The [previous balanced two-block theorem](M073_REGULAR2_CYCLE_MARGIN.md) gives

```text
t(H,W0) >= p^66 (1+33q^4+88q^6).
```

Therefore (1) gives the following **newly documented sufficient condition** on the off-diagonal-dominant two-block region:

```text
t(H,W) >= p^66 (1+33q^4+88q^6)
                   * (1-(delta/u)^2)^(33*(1-q)/2).     (3)
```

Whenever the multiplicative factor on the right is at least one, the usual Sidorenko inequality holds for that `W`. The result covers `b > max(a,c)` with `a != c`, a region not covered by the prior equal-diagonal, ordered, or assortative-cone arguments.

**Explicit rational interior certificate.** Set

```text
a=19/32, b=1, c=13/32;
u=1/2, delta=3/32, p=3/4, q=1/3, delta/u=3/16.
```

Then the multiplier in (3) is exactly

```text
(1114/729) * (247/256)^11 > 1,                       (4)
```

with an exact integer cross-multiplication in the checker. Thus `t(H,W)>p^66` for this nonconstant, unequal-diagonal, strictly disassortative graphon. The certified lower ratio is approximately **1.0308240203**, while the independently computed exact homomorphism ratio is approximately **2.9438492414**. The latter is a regression, not the continuum proof.

## Reproducibility, falsifiers and limits

From the repository root:

```sh
python3 scripts/m073_antiferro_stability.py --check
python3 -m unittest discover -s tests -p 'test_m073_antiferro_stability.py' -v
python3 scripts/regen.py --check
```

The checker verifies the pinned triple table and cycle counts, recomputes the rational sample through two **distinct** 8192-point-label paths (a compressed profile histogram and direct face elimination), checks the exact rational lower factor, and checks (1) on small bipartite graphs with two rational parameter sets. It also checks the edge-correlation premise directly.

**Adversarial nonbipartite control:** on a triangle with `u=1/2, b=1`, the original edge-spin correlation is `-3/13 > -1/3=-q`. Thus the key edge-correlation step **fails** if one silently drops bipartiteness. This does not assert that the final density inequality fails for every triangle. The result is also not established for `b<u`, unequal block masses, three or more blocks, or arbitrary graphons. The proof's lower factor may fall below one, so it cannot certify the entire off-diagonal-dominant region.

**Next falsifier:** Seek an explicit two-block host in the off-diagonal-dominant region *outside* (4)'s sufficient tube where the ordinary density gap is negative; otherwise attempt a sharper edge-correlated or nontermwise bound that certifies the entire two-block region. The externally claimed finite host for the full M073 pattern remains a separate proof obligation.

## Prior art / provenance

- [OpenAI, *A counterexample to Sidorenko's conjecture*, September 23, 2026](https://github.com/openai/math/tree/main/preprints/A-counterexample-to-Sidorenkos-conjecture-September-23-2026) — source of the 35-vertex/66-edge pattern and claimed finite host; this note neither reproduces nor independently validates the claimed host.
- [Friedli and Velenik, *The Ising Model*, §3.5](https://www.unige.ch/math/folks/velenik/smbook/Ising_Model.pdf) — classical high-temperature expansion and positive ferromagnetic correlations.
- [Lovász, *Subgraph Densities in Signed Graphons and the Local Simonovits–Sidorenko Conjecture* (2011)](https://doi.org/10.37236/614) — local graphon inequalities.
- [Sah, Sawhney, Stoner and Zhao, *A reverse Sidorenko inequality* (2020)](https://doi.org/10.1007/s00222-020-00956-9) — related extremal two-spin machinery, not claimed to imply this exact numerical bound.

The spin and correlation tools are **classical**. The combined explicit stability estimate is author-derived, but a complete priority/novelty audit and an outside proof review are still required. No independent acceptance, new solution of Sidorenko, or update to `data/solved.json` is claimed.
