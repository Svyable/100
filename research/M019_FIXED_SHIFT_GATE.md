# M019 — exact failure of the universal fixed shifts 3 and 7

**2026-11-01 · Work item `O-M019-01` · [claim #121](https://github.com/Svyable/100/issues/121)**

**Result type:** a rigorous, bounded *negative* result about two proposed first
denominators. This is **not a novel theorem**, an Erdős–Straus counterexample,
a proof of the conjecture, or an independently reviewed result.

## Exact statement and proof

Fix positive integers `n,c` with `4 | n+c`, and insist on the first
denominator `x=(n+c)/4`. Set `m=nx`. Then positive integers `y,z`
satisfy

```text
4/n = 1/x + 1/y + 1/z
```

if and only if a positive divisor `d | m²` exists with

```text
d ≡ -m (mod c),      m²/d ≡ -m (mod c).
```

Indeed, subtracting `1/x` gives `1/y+1/z=c/m`, hence
`(cy-m)(cz-m)=m²`. Both factors are positive: if `cy≤m`, then
`1/y≥c/m` contradicts the positive remaining summand. Conversely,
given the two congruences, `y=(m+d)/c` and `z=(m+m²/d)/c` are
positive integers and satisfy the original identity. If `gcd(m,c)=1`,
the second congruence follows from the first, but the checker tests
**both** directly.

For `n=1129`, trial division through `floor(sqrt(1129))=33` proves
primality, and `1129≡1 (mod 24)`.

* **Shift 3:** `x=283` (prime), `m=1129·283`. Both prime factors are
  `1 (mod 3)`, so every positive divisor of `m²` is `1 (mod 3)`.
  But the required divisor must be `-m≡2 (mod 3)`. Impossible.
* **Shift 7:** `x=284=2²·71`, `m=1129·284`. The prime-factor
  residues modulo 7 are `1129≡2`, `2≡2`, `71≡1`. Every divisor
  of `m²` therefore lies in the multiplicative subgroup
  `{1,2,4}` modulo 7. Yet `m≡1 (mod 7)`, so the required divisor
  residue is `6`, outside that subgroup. Impossible.

Thus **neither** `4x-n=3` **nor** `4x-n=7` can work at the prime
`n=1129`. In particular, a universally valid positive-integer
identity for *all* primes `n≡1 (mod 24)` under either fixed shift
cannot exist. This directly falsifies the universal wording of
`O-M019-01`, not the underlying Erdős–Straus conjecture.

The independent divisor-enumeration path checks every divisor of `m²`
for each shift, with no numerical tolerance or bounded-denominator
search. A separate prime-factor subgroup proof gives the obstruction
without enumerating divisors. The checker also exhausts primes
`n≡1 (mod 24)` below 1129, finding at least one of these two
shifts for each; **1129 is the first joint failure in that bounded
scan**, not a new global number-theoretic bound.

## Essential positive control

The same prime **does** have an Egyptian-fraction representation using
shift `11`:

```text
4/1129 = 1/285 + 1/29260 + 1/99103620.
```

The checker verifies this as an exact `fractions.Fraction` identity.
It also accepts shift 3 at `n=97` and shift 7 at `n=73`, guarding
against a vacuous all-negative test.

## Reproduce and falsify

```sh
python3 scripts/straus_shift_gate.py --check
python3 -m unittest discover -s tests -p 'test_straus_shift_gate.py' -v
```

Eight adversarial tests cover prime-factor certificates, the two
independent modular obstructions, a positive witness for `1129`,
two other positive controls, brute divisor comparison for small
instances, first-joint-failure enumeration, and invalid inputs.
Mutation targets include a spurious divisor residue, a missing prime
factor, and a false assertion that no decomposition exists.

**Boundary:** Only the two forced first denominators are excluded.
Other values of `x` remain available; no conjecture-wide result follows.
This does not meet the original obligation's constructive acceptance
criterion and does not discharge it. The appropriate next step is to
re-scope the obligation away from universal fixed shifts and toward
a genuinely new restricted family or a new analytic mechanism.

## Prior art and novelty caution

* L. J. Mordell, **“A Congruence Problem of E. G. Straus”**,
  *Journal of the London Mathematical Society* 38 (1963), 108–110,
  https://doi.org/10.1112/jlms/s1-38.1.108 .
* Benjamin Dahan, **“Sieve dimension and search depth for the
  Erdős–Straus conjecture, n ≡ 1 (mod 24)”**, arXiv:2608.24035
  (posted 2026-08-25), https://arxiv.org/abs/2608.24035 .
  The abstract explicitly studies fixed-shift `c=7` obstructions
  and subgroup-based approaches, substantially preempting novelty
  claims for this elementary divisor obstruction.
* Existing project identities and finite mine:
  [M019_IDENTITIES.md](M019_IDENTITIES.md), which already warns that
  polynomial coverings cannot settle the entire hard class.

**Novelty classification:** `known_or_reproduction`. This work adds a
transparent, self-contained, exact **scope falsifier** for the current
repository obligation, not an independently validated discovery.
