# M075: Burnside-certified full-support orbit counts through n=5

**Exact finite result reproduced; no new Frankl theorem.** This is an
independent way to compute the previously published five-element orbit
count, complementing the canonical-minimum construction in
[M075_CANONICAL.md](M075_CANONICAL.md).

## Statement

Let \(\mathcal U_n\) be the finite set of all nonempty union-closed
families \(F\subseteq 2^{[n]}\) whose union is exactly \([n]\).
The symmetric group \(S_n\) acts on these families by relabeling ground
elements. Compute the number of orbits \(|\mathcal U_5/S_5|\), without
canonicalizing each of the millions of labeled families individually.

The exact known answer is **28,960**, listed in
[OEIS A326907](https://oeis.org/A326907). We obtain this by an independently
implemented group fixed-point calculation.

## Lemma A: a fixed family is a union of subset-orbits

For \(\pi\in S_n\), let \(\langle\pi\rangle\) act on \(2^{[n]}\).
A family satisfies \(\pi(F)=F\) if and only if its membership is constant
on every cycle (orbit) of the induced action on subsets. Proof: the
forward implication follows by repeatedly applying \(\pi\) and
\(\pi^{-1}\); the converse follows by applying \(\pi\) to the union of
whole cycles. Thus we can decide **one orbit of subsets at a time**,
not one subset at a time.

Each subset orbit has a single cardinality because permutations
preserve the size of a set. Begin with the one-point subset orbit
\(\{[n]\}\), mandatory for full-support union-closed families.
Process all other subset orbits in decreasing cardinality, with a
deterministic numeric tie-break.

When an orbit \(B\) is added, require that every union \(A\cup S\)
with \(S\in B\) and \(A\) in the augmented family belongs to that
augmented family. Exclusion does not alter the current family.

**Soundness:** after each accepted inclusion the family remains
union-closed; invariance and full support are automatic because
complete orbits are added and \([n]\) remains present.

**Completeness:** take any \(\pi\)-invariant full-support union-closed
family \(F\) and follow the decisions for its subset orbits. If an
orbit \(B\subset F\) is to be included, all required unions lie in \(F\).
A required union outside \(B\) has strictly greater size than its
contributing \(S\in B\), unless it equals \(S\); hence its orbit was
processed earlier and included. The same applies to unions of two
members of \(B\). No required inclusion is pruned, so every fixed
family is reached. A unique orbit decision vector generates each
family exactly once. QED.

## Lemma B: only cycle types need to be counted

Conjugate permutations \(\pi'=\sigma\pi\sigma^{-1}\) fix equally many
families: relabeling \(F\mapsto\sigma(F)\) is a bijection from
\(\operatorname{Fix}(\pi)\) onto \(\operatorname{Fix}(\pi')\), preserving
union closure and full support. Elements of \(S_n\) are conjugate
precisely when they have the same cycle-type partition of \(n\).
Hence only seven representative cycle types exist in \(S_5\).

Burnside's lemma now gives

\[
|\mathcal U_n/S_n|
 =\frac{1}{n!}\sum_{\pi\in S_n}|\operatorname{Fix}(\pi)|.
\]

The identity's fixed count is the independent labeled full-support
enumeration in [frankl_canonical.py](../scripts/frankl_canonical.py).
For each other cycle type we enumerate the complete-orbit choices
using Lemma A.

## Exact n=5 certificate

| Cycle type | Class size | Fixed full-support families |
|---|---:|---:|
| 1+1+1+1+1 | 1 | 2,747,402 |
| 2+1+1+1 | 10 | 58,122 |
| 2+2+1 | 15 | 7,506 |
| 3+1+1 | 20 | 1,256 |
| 3+2 | 20 | 168 |
| 4+1 | 30 | 166 |
| 5 | 24 | 22 |
| **Total** | **120** | **3,475,200 weighted** |

Therefore

\[
|\mathcal U_5/S_5|
=\frac{3{,}475{,}200}{120}=\boxed{28{,}960}.
\]

This equals [OEIS A326907](https://oeis.org/A326907). The labeled
identity count agrees with [OEIS A326906](https://oeis.org/A326906).
The \(n=4\) implementation independently reproduces orbit count 330,
also computed by taking the minimum among all relabelings in our
existing Frankl structure mine.

## Reproduce

```sh
python3 scripts/frankl_burnside.py --check
python3 scripts/frankl_canonical.py --check
python3 -m unittest discover -s tests -p 'test_frankl_burnside.py' -v
```

- [Implementation](../scripts/frankl_burnside.py) reconstructs the subset
  orbits and all seven \(S_5\) conjugacy classes.
- [Frozen integer certificate](../data/frankl_burnside_n5.json) pins
  every class weight and fixed-family count; CI rejects drift.
- [Adversarial tests](../tests/test_frankl_burnside.py) compare
  fixed-point enumeration with brute-force \(n=3\), compare \(n=4\)
  Burnside output with direct canonicalization, and reject
  non-permutations and missing within-orbit unions.

This is a more efficient counting method than testing a full
canonical minimum for every labeled family. **It does not establish
a particular measured 10x speedup**, and the known n=5 result is
already far inside the published cases of Frankl's conjecture.
The unresolved next step remains a genuine structural lemma beyond
known special cases, with independent mathematical review and exact
quantifier scope before any claim is promoted.
