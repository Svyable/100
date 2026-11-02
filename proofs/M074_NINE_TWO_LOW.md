# M074 — two degree-two vertices in every nine-vertex triangle-free oriented neighborhood

**Research candidate, 2026-11-01.** Elementary local strengthening, independently checkable integer case split, no new unrestricted Caccetta–Häggkvist theorem. This is a **different result** from the already merged [regular (27,9) exclusion](M074_27_REGULAR.md); no duplicate crossing theorem is claimed. External mathematical review and novelty audit are pending.

## Exact local theorem

**Theorem.** Every **oriented**, loopless directed graph \(H\) on nine vertices, with **no directed 3-cycle** and minimum outdegree at least **two**, has **at least two distinct vertices of outdegree exactly two**.

Previously, the [nine-vertex local theorem](M074_NINE_VERTEX.md) established that at least **one** such vertex exists (minimum outdegree three is impossible), that all indegrees are at most **four**, and that \(m=e(H)\le29\). We use its indegree-four bound, and the following established [eight-vertex local lemma](../research/M074_ELEMENTARY_24_REGULAR.md):

For an oriented directed-triangle-free eight-vertex graph \(J\) of minimum outdegree two, \(m_J\le21\), every indegree is at most three, and every indegree-three vertex has outdegree two.

If \(s\) counts the internal outdegree-two vertices in \(J\), then

\[
m_J\ge 2s+3(8-s)=24-s \quad\Longrightarrow\quad s\ge24-m_J.
\]

Only \(s\) vertices can have indegree three; the rest have indegree at most two. Therefore

\[
m_J\le3s+2(8-s)=16+s \quad\Longrightarrow\quad s\ge m_J-16.
\]

Thus

\[
\boxed{s\ge\max(24-m_J,m_J-16).}\tag{1}
\]

This is a graph-theoretic consequence of the proved eight-vertex lemma, not a fit to experimental counts.

## Proof of the nine-vertex strengthening

Assume for contradiction that \(H\) has exactly **one** outdegree-two vertex \(x\). Every other vertex has outdegree at least three, so with \(m=e(H)\),

\[
\boxed{26=2+8\cdot3\le m\le29.}\tag{2}
\]

Write \(b=d_H^-(x)\le4\). Delete \(x\) to obtain the eight-vertex graph \(J=H-x\). Deleting \(x\) removes at most one outgoing arc from each other vertex. Since every other vertex originally has outdegree at least three, **\(J\) has minimum outdegree at least two**. Its arc count is

\[
m_J=m-2-b\le21.
\]

Hence \(m\le23+b\le27\), and \(b\ge m-23\ge3\). There are only three remaining possibilities:

| \(m\) | \(b\) | \(m_J=m-2-b\) |
|---:|---:|---:|
| 26 | 3 | 21 |
| 26 | 4 | 20 |
| 27 | 4 | 21 |

If \(m_J=21\), equation (1) gives **at least five** degree-two vertices in \(J\). Since \(x\) is the **only** vertex of global outdegree two in \(H\), each of these five vertices must have gained its additional outgoing arc by pointing to \(x\). Consequently \(b\ge5\), contradicting \(b\le4\). This eliminates both 21-arc possibilities.

It remains that \(m=26,b=4,m_J=20\). Equation (1) gives at least four degree-two vertices in \(J\), and every such vertex points to \(x\). As \(b=4\), there are **exactly four**, forming a set \(S\subseteq V(J)\); all four arcs entering \(x\) originate in \(S\). The other four vertices \(T=V(J)\setminus S\) have internal outdegree at least three. Because \(J\) has exactly 20 arcs, they have internal outdegree **exactly three** each:

\[
20=4\cdot2+4\cdot3.
\]

Orientation forbids \(x\to s\) for \(s\in S\), since \(s\to x\) already holds. Therefore \(x\)'s two outgoing neighbors are **distinct vertices \(p,q\in T\)**.

Neither \(p\) nor \(q\) can send an arc to any \(s\in S\): for example, \(x\to p\to s\to x\) would be a directed triangle. But \(p\) and \(q\) each have **three outgoing neighbors in \(J\)**, and the only available destinations are the **other three** vertices of \(T\). Thus \(p\to q\) and \(q\to p\), a forbidden digon.

All cases contradict orientation or triangle-freeness. Hence at least **two** vertices of \(H\) have outdegree exactly two. □

## A genuine three-degree-two witness, and the gap it leaves

The following nine-vertex oriented graph has **24 arcs**, minimum outdegree two, no digons, no directed triangles, and **exactly three** outdegree-two vertices. Its outneighbor lists, indexed \(0,\ldots,8\), are:

```text
0: 6 7
1: 0 3
2: 1 8
3: 0 6 7
4: 1 5 8
5: 1 2 8
6: 2 4 5
7: 2 4 5
8: 0 1 3
```

The degree sequence is \((2,2,2,3,3,3,3,3,3)\); direct adjacency replay verifies the graph. Thus any stronger universal claim demanding **four or more** outdegree-two vertices is false. **The present theorem proves at least two; it does not establish whether exactly two is realizable.** A separate exploratory solver search found no two-degree-two witness, but an unverified solver result is **not** a mathematical exclusion, a published certificate or a premise of this theorem.

A separate adversarial control is the oriented circulant on \(\mathbb Z/9\mathbb Z\) with steps \(1,2,3\), deleting the step-three outgoing arc from each of vertices 0 and 1. It has minimum outdegree two and exactly two degree-two vertices but **contains a directed triangle**. Therefore its existence does not contradict the theorem and directly demonstrates that triangle-freeness cannot be omitted.

## Conditional improvement in the finite (27,9) campaign

Suppose, *only hypothetically*, that \(D\) is an oriented, directed-triangle-free graph on 27 vertices with all outdegrees nine. Earlier work shows every global indegree is at most ten and eliminates the indegree-nine-regular branch. Fix **any** vertex \(v\) of indegree ten and use the root sets \(A=N^+(v)\) (nine), \(B=N^-(v)\) (ten), \(C\) (seven).

The proven [\(z\le3\) root theorem](M074_ZERO_K_THREE.md) says at most three \(b\in B\) have \(k(b)=d_C^-(b)=0\). Every \(a\in A\) sends at least two outgoing arcs inside \(A\), so the present nine-vertex theorem gives **two distinct \(a_1,a_2\in A\) with \(d_A^+(a_i)=2\)**. Each sends all seven remaining outgoing arcs to every \(c\in C\). Such an \(a_i\):

- receives one arc from \(v\);
- receives at most four arcs from within \(A\) (nine-vertex local indegree cap);
- receives **no** arc from \(C\) (orientation);
- receives at most three arcs from \(B\), since \(a_i\to c\to b\to a_i\) forbids every \(b\) with \(k(b)>0\).

Therefore

\[
\boxed{d_D^-(a_i)\le1+4+3=8 \quad (i=1,2).}
\]

**Every indegree-ten vertex has at least two distinct outneighbors of ambient indegree at most eight.** This improves the previously recorded one-low-outneighbor condition, but does not prove the finite \((27,9)\) case.

For a global necessary inequality, let \(H_{10}=\{v:d_D^-(v)=10\}\) with size \(h\), and \(L_8=\{v:d_D^-(v)\le8\}\) with size \(\ell\). Degree-sum balance gives \(h=\sum_{u\in L_8}(9-d_D^-(u))\ge\ell\). Every high vertex has two low outneighbors, so

\[
2h\le e(H_{10},L_8)\le\sum_{u\in L_8}d_D^-(u)=9\ell-h,
\qquad\boxed{h\le3\ell.}
\]

The inequalities \( \ell\le h\le3\ell \) remain consistent; **there is no global contradiction**. The next task is to strengthen the local statement further using the *actual* rooted \(A/B/C\) incidence and the \(z=0,1,2,3\) cases, not assume the degree-defect saturation hypothesis of eight low outneighbors.

## Reproduction and scope audit

- [`scripts/ch9_two_low.py`](../scripts/ch9_two_low.py) checks all 20 \((m,b)\) integer cases for a hypothetical unique degree-two vertex and validates the exact three-low witness and triangle-negative control.
- [`tests/test_ch9_two_low.py`](../tests/test_ch9_two_low.py) independently derives the remaining arithmetic case by another enumeration, checks the forced digon mechanism for every choice of \(p,q\in T\), uses a separate matrix-based directed-triangle validator for the witness, and verifies malformed inputs and a triangle-bearing countercontrol.

```sh
python3 scripts/ch9_two_low.py --check
python3 -m unittest discover -s tests -p 'test_ch9_two_low.py' -v
```

This is a **hand proof with arithmetic and adjacency regression tests**, not a full nine-vertex graph census, a SAT UNSAT certificate, or a Lean formalization. Independent mathematical and prior-art review remain outstanding. Earlier [wustep/maths finite computations](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md) already report the full finite (27,9) exclusion by a different route. Neither the main conjecture's evidence status nor `data/solved.json` should change.
