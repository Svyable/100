# M019 — parametric identities from the residue mine

**Dated:** 2026-10-31. **Scope:** explicit infinite families of solutions of
$4/n = 1/x + 1/y + 1/z$ on arithmetic progressions inside $n \equiv 1\pmod{24}$.
**Not claimed:** a proof of the Erdős–Straus conjecture, novelty over classical
Mordell-type coverings, or coverage of every integer $n \equiv 1\pmod{24}$.

The certified mine [`straus_patterns`](../scripts/mines/straus_patterns.py) only
*clusters* solutions for primes $n \le 8000$ with $n \equiv 1\pmod{24}$ by the
residue $4x-n$. This note turns the two dominant clusters (residues 3 and 7) into
polynomial identities, then adds a short list of fixed-divisor companions. The
independent checker is [`scripts/straus_identities.py`](../scripts/straus_identities.py);
the coverage table is the mine [`straus_identities`](../scripts/mines/straus_identities.py).

## Why this is the overlooked step

Classical unit-fraction identities already settle every $n\not\equiv 1\pmod{24}$.
Inside the hard class, a computer search keeps rediscovering the same progressions.
Writing the closed form, and proving it as a polynomial identity, is the part the
table does not do. Extending the verified range is refused by the dispatcher: that
range already sits inside published computations.

## Two primary identities

### Residue 3 on $n = 120t+97$

For every integer $t \ge 0$ set

$$
n = 120t+97,\qquad
x = 30t+25,\qquad
y = (12t+10)\,n,\qquad
z = (60t+50)\,n = 5y.
$$

Then $4x-n = 3$ and

$$
\frac{4}{n} - \frac{1}{x} = \frac{3}{nx} = \frac{1}{y} + \frac{1}{5y} = \frac{6}{5y}.
$$

The middle equality is $5y = 2nx$, which holds because $y = (2x/5)\,n$ and
$x = 30t+25$ is divisible by 5. Clearing denominators gives the polynomial identity
checked in code.

### Residue 7 on $n = 120t+73$

For every integer $t \ge 0$ set

$$
n = 120t+73,\qquad
x = 30t+20,\qquad
y = (6t+4)\,n,\qquad
z = (15t+10)\,n.
$$

Then $4x-n = 7$ and $1/y + 1/z = 7/(nx)$. Equivalently $y = (x/5)\,n$ and
$z = (x/2)\,n$, which are integral because $x = 30t+20$.

Together these two progressions already match **65 of the 117** primes
$n \le 8000$ with $n \equiv 1\pmod{24}$ in the residue mine.

## Fixed-divisor companions

Write $x = (n+r)/4$ with residue $r \in \{3,7,11\}$ and choose a positive divisor
$d$ of $x^2$. Set

$$
a = \frac{x+d}{r},\qquad
b = \frac{x^2/d + x}{r},\qquad
y = an,\qquad
z = bn.
$$

The relation $(ra-x)(rb-x) = x^2$ forces $rab = x(a+b)$, which is exactly
$4/n = 1/x + 1/y + 1/z$. On any arithmetic progression where $a$ and $b$ are
integer polynomials in the parameter, this is again a polynomial identity.

The repository records seven such companions (moduli 168 and 264), including the
composite-only progression $n = 168t+49 = 7(24t+7)$, which never contributes an
odd prime but still covers an infinite hard-class progression.

## Coverage certificate

On the smoke range $N = 8000$:

- 117 primes are $\equiv 1\pmod{24}$;
- the nine identities cover **106** of them by closed form;
- the **11** uncovered primes all lie in $\{1,49\}\pmod{120}$.

Run:

```sh
python3 scripts/straus_identities.py --check
python3 scripts/mine.py --mine straus_identities
python3 -m unittest discover -s tests -p 'test_straus_identities.py' -v
```

## Evidence boundary

- The identities are **reproduced constructive coverings**, in the same spirit as
  classical Mordell / Sierpiński parametric solutions. Do not describe them as a
  new resolution of Erdős–Straus, and do not promote M019 toward Solved.
- A finite list of polynomial identities cannot cover every $n \equiv 1\pmod{24}$;
  that obstruction is already the campaign blocker.
- The next attack is therefore **not** a longer search. It is either a genuinely
  new restricted family outside these Mordell-type progressions, or a different
  idea for the remaining classes $n \equiv 1,49\pmod{120}$.
