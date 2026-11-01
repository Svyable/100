# M074 — an elementary obstruction to the four-zero CH(27,9) root

**2026-11-01. Research candidate, not an independently accepted result.**
The argument below excludes a **specific rooted subcase** of a hypothetical
27-vertex directed-triangle-free, nine-outregular oriented graph: a vertex
of indegree ten for which exactly four of its ten inneighbors receive no
arcs from the root's seven nonneighbors. It depends on the already recorded
nine-vertex arc and degree lemmas and the B-induced small-subset tests.
It does **not** exclude indegree-ten roots with zero, one, two, or three
such inneighbors, prove the complete finite (27,9) case, or resolve the
unrestricted Caccetta–Häggkvist conjecture. Earlier external computational
certificates address (27,9); this derivation has **no audited priority or
novelty claim**. Independent mathematical and prior-art review is pending.

## Statement and exact notation

Let `D` be an oriented (no loops, no opposite arcs), directed-C3-free
27-vertex graph with **every outdegree exactly nine**. Previous local
lemmas show every indegree is at most ten. Suppose `v` has indegree ten.
Write

- `A = N+(v)` (nine vertices), `B = N-(v)` (ten), and `C` the seven
  vertices not adjacent to `v`;
- `alpha(a) = d+_{D[A]}(a)`, with `2 <= alpha(a) <= 8` and
  `m = sum_A alpha <= 29` by the nine-vertex theorem;
- `k(b) = d-_{C}(b)`, with `0 <= k(b) <= 7`, and exactly **four** zeroes
  in the ten `k` values (the `z=4` hypothesis).

There is no arc from `A` to `B`: `v -> a -> b -> v` would be a directed
triangle. There is also no arc from `A` to `v`, so for every `a in A`,

    d+_C(a) = 9 - alpha(a).                              (1)

In particular, `alpha(a)=2` means `a` sends an arc to **every** vertex
of `C`. The earlier root cuts require

    sum_B k >= 92 - 2m,                                (2)

and every `b -> a` edge with `b in B, a in A` requires
`alpha(a) >= k(b)+2`. The earlier B-internal girth lemma supplies the
necessary checks reproduced by `scripts/ch27_b_internal.py`.

**Proposition.** Under these hypotheses, `z=4` is impossible.

## Lemma 1 — at least two arcs from C into A

Put `E=e(C,A)` and `K=sum_B k=e(C,B)`. The four zeroes in `k` imply
`K <= 6*7 = 42`. Equality is already impossible. If `K=42`, then six
`b` vertices have `k(b)=7`. Each receives all seven arcs from `C`, so
sends none to `C`, none to `A` (the `alpha >= k+2=9` requirement is
impossible), and sends one to `v`. Thus each sends eight arcs inside
`B`. Six such vertices would account for at least 48 arcs of `D[B]`,
more than its maximum 45 unoriented pairs. Therefore **`K<=41`**.

Counting the 63 outgoing arcs of `C` gives

    63 = E + K + e(C,C),    e(C,C) <= 21,
    E >= 42 - K.                                      (3)

In fact **`E >= 2`**. If `E<=1`, then `K<=41` forces `e(C,C)>=21`.
So `e(C,C)=21`, meaning `D[C]` is a tournament. A tournament with no
oriented triangle is transitive, hence has a sink `c` with no outgoing
arc inside `C`. That sink cannot point to any of the four zero-`k`
vertices in `B`, so it has at most six outgoing arcs to `B` and at
most **one** into all of `A` (because `E<=1`). Thus its total
outdegree is at most seven, contradicting outdegree nine. QED.

## Lemma 2 — C-to-A eligibility

Let `L={a in A:alpha(a)=2}`, `s=|L|`, and `H=A\L`, `h=9-s`.
Every `x in L` points to every `c in C`, so `c -> x` is forbidden by
orientation. If another `y in H` points to even one `x in L`, then
`c -> y` is also impossible: it would close `y -> x -> c -> y`.
Consequently a vertex of `H` can **receive** from `C` only if all its
`alpha(y)` outgoing arcs in `A` end inside `H`. This requires
`alpha(y) <= h-1`.

If an `alpha=8` vertex exists and `s>=1`, it points to every other
member of `A` and hence into `L`, so it cannot receive from `C`.
No other `y in H` can point to that vertex (no digons), reducing its
eligible internal-high outneighbors to at most `h-2`.

Finally, (1) and orientation give

    d-_C(y) <= 7 - d+_C(y) = alpha(y)-2.          (4)

Thus a safe upper bound on `E` is the sum of `alpha(y)-2` over those
`y` allowed by the preceding necessary conditions. This deliberately
ignores further triangle-free constraints among the high vertices:
**it can overestimate `E` but never underestimate it.**

The enumerator independently generates 166 sorted `alpha` profiles
with `sum alpha <= 29`, and 924 sorted `k` profiles with four zeroes
and six values in `[1,7]`. Previously derived (2), B-subset arc
capacities, and B-small-subset girth tests leave exactly **295** pairs.
A separately proved, later-added [z=4 sink lemma](M074_27_Z4_SINK.md)
already excludes **four** of those pairs, leaving **291** for this
classifier. Applying (3)–(4) excludes **284** further pairs. All four
sink-excluded pairs *also* violate the C-to-A bound, so the original
C-to-A-only exclusion count **288 = 284 + 4** remains mathematically
true, but must not be double counted as a sequential work stage. The
other seven pairs have exactly three distinct `alpha` vectors,
treated next. The enumeration counts
**integer profiles only**, not graph isomorphism classes.

## Lemma 3 — the last seven profiles are also impossible

All vectors in this section are sorted. Parenthesized exponents denote
multiplicity (for example `3^5` means five copies of 3). Every `k`
profile in each row has four zeroes. There are **1 + 3 + 3 = 7** pairs:

| `alpha` | `K=sum k` | count | Necessary `E>=42-K` |
|---|---:|---:|---:|
| `(2^3,3^5,8)` | 37 | 1 | 5 |
| `(2^2,3^5,4,6)` | 34 | 3 | 8 |
| `(2,3^7,6)` | 34 | 3 | 8 |

**Case I: `(2^3,3^5,8)`.** The eight-outdegree vertex points to
all eight other `A` vertices, including the three low ones. It
cannot receive from `C`, and neither can the low vertices. Each
three-outdegree vertex can receive at most one arc from `C`, so to
supply `E>=5`, all **five** must receive one and avoid sending to any
low vertex. But the eight-outdegree vertex points to all five,
so those five must each send their three `A`-arcs to *other vertices
among themselves*. That requires 15 arcs within a five-vertex oriented
graph, which has at most ten. Contradiction.

**Case II: `(2^2,3^5,4,6)`.** There are seven vertices `H`, of
combined internal-`A` outdegree 25. Each can send at most two arcs
into `L`, so its outdegree **inside `H`** is at least one. If
`D[H]` had 21 arcs it would be a directed-C3-free tournament, hence
transitive with an outdegree-zero sink. Thus `e(H,H)<=20`, and

    e(H,L) = 25-e(H,H) >=5.

At least three distinct `H` vertices must point into the two-vertex
`L`. They cannot receive from `C`. The combined incoming capacity
(4) over all high vertices is

    5*(3-2)+(4-2)+(6-2) = 11.

Losing at least three high vertices, each of capacity at least one,
leaves **`E<=8`**. But (3) requires `E>=8`, so equality holds.
In particular the three disqualified high vertices must be exactly
three of the five `alpha=3` vertices. The `alpha=6`, `alpha=4`,
and other two `alpha=3` vertices all avoid `L` and receive their
maximum possible `C` indegree. Consequently all **four** of these
high vertices are adjacent to **every** vertex of `C` (their
outdegrees toward `C` and indegrees from `C` sum to seven).

Equality `E=8`, `K=34` forces `e(C,C)=63-8-34=21`.
Thus `D[C]` is a transitive tournament with a sink `c` receiving
all six arcs from the other `C` vertices. Each of the two low `A`
vertices points to `c`. Each of the four protected high vertices
also must point to `c`: it has at least one outgoing neighbor
among the other six `C` vertices by (1), is adjacent to `c`, and
`c -> a -> c' -> c` would be a directed triangle because all other
`c' in C` point into the sink. Therefore `c` has indegree at least
`6+2+4=12`, contradicting the global maximum indegree ten.

**Case III: `(2,3^7,6)`.** There is only one low vertex `L`.
The eight high vertices have total internal-`A` outdegree 27,
and each sends at most one arc into `L`. Therefore every vertex of
`D[H]` has outdegree at least two. Here is a short independent
rooted inequality for any eight-vertex oriented C3-free digraph
of minimum outdegree two: if a vertex has outdegree `a`, indegree
`b`, its outneighborhood must supply at least `2a` arcs into the
outneighborhood or nonneighbors (arcs to its inneighbors are
forbidden), whence

    2a <= binom(a,2) + a*(7-a-b),
    a+2b <= 9.

Summing yields `3e(H,H)<=8*9=72`, so `e(H,H)<=24`.
To provide `E>=8`, the `alpha=6` high vertex **must** avoid `L`
and receive from `C`: without it the other seven highs each have
capacity at most one. Its outdegree inside `H` is then six.
If `e(H,H)=24`, equality `a+2b=9` holds at every vertex of `H`,
which is impossible at this even-outdegree-six vertex (six plus
twice an integer cannot equal nine). Thus `e(H,H)<=23`, implying

    e(H,L) = 27-e(H,H) >=4.

At least four distinct high vertices point to the single low one,
so they cannot receive from `C`. As the six-outdegree vertex is
protected, these are at least four `alpha=3` vertices, leaving
at most three other threes that can receive from `C`. Equation (4)
then bounds `E<=4+3=7`, contradicting `E>=8`. QED.

All 295 profiles (4 sink + 284 further C-to-A + 7 terminal) have now been excluded, so **no digraph satisfying
the exact proposition can have `z=4`**. This is a conditional
root-local theorem using the established nine-vertex prerequisites;
it is not a solution of the remaining `z=0,1,2,3` cases.

## Reproducibility, falsifiers, and independence

```sh
python3 scripts/ch27_b_internal.py
python3 scripts/ch27_c_to_a.py --check
python3 -m unittest discover -s tests -p 'test_ch27_c_to_a.py' -v
python3 scripts/regen.py --check --fast
```

The new script evaluates *all* 153,384 coarse necessary integer pairs
and preserves the updated *sequential* 4/284/1/3/3
partition (the original C-to-A-only count 288 includes the four sink cuts). The tests use a
different histogram enumeration and recompute the upper/lower bounds
independently. Weakening the root cut or allowing an `alpha=8` vertex
to be targeted by other A vertices deliberately leaves nonzero
unresolved pairs. These checks validate arithmetic and guards, **not**
the truth of every handwritten lemma. A mathematical reviewer should
specifically challenge (1), the `C`-tournament sink step, the seven
profile exhaustiveness, and the equality conditions in Cases II–III.

Any 27-vertex directed-C3-free nine-outregular graph with a ten-indegree
root and four zero-`k` vertices would be a direct falsifier of the
proposition; it must be checked as an actual adjacency list. No
independent review, accepted-outcome record, new-restricted-result flag,
or solved-ledger change is warranted by this author-derived note alone.

**Prior-art anchors:** [the existing nine-vertex proof](M074_NINE_VERTEX.md),
[the B-small-subset lemma](M074_B_INTERNAL_GIRTH.md),
[the rooted regular/irregular reduction](M074_27_REGULAR.md),
[EGRES open statement](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture),
and [earlier independently checked finite certificates through order 36](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md).
