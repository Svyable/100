# M006 — an explicit least-Goldbach-prime bound on the growth mine

**Dated:** 2026-11-01. **Scope:** every even integer $4 \le n \le 20000$.
**Not claimed:** an asymptotic theorem, a bound through $4\cdot10^{18}$, or any
progress toward the strong Goldbach conjecture beyond this finite window.

## The overlooked step

The certified mine [`goldbach_growth`](../scripts/mines/goldbach_growth.py) lists
the twelve record-setting least Goldbach primes through $20000$, the largest
being $173$ at $n=7426$. The campaign asked to test an explicit upper bound
against those records, not to push the verified range toward the published
$4\cdot10^{18}$ check.

## Finite theorem

For every even integer $n$ with $4 \le n \le 20000$, if $p$ is the least prime
such that $n-p$ is prime, then

$$
p \le \lfloor 3(\ln n)^2\rfloor.
$$

The independent checker rebuilds each least prime with an odd-only sieve and
recomputes the same inequality. Because the right-hand side is increasing for
$n\ge3$, it is enough that the bound dominate the twelve running-maximum
records; the mine nevertheless verifies every even $n$ in range.

The sharpest ratio on the records is $173/(\ln 7426)^2 \approx 2.178$, so the
constant $3$ has slack. Tightening the constant is cosmetic inside this window;
exporting the inequality past $20000$ is refused by the dispatcher.

## Evidence boundary

- Oliveira e Silva, Herzog and Pardi (Math. Comp. 2014) already verify Goldbach
  through $4\cdot10^{18}$. This note only shapes the tiny initial segment into
  an explicit inequality.
- Do not promote M006 toward Solved.
- Run:

```sh
python3 scripts/mine.py --mine goldbach_bound
python3 -m unittest discover -s tests -p 'test_mines.py' -v
```
