# M074 — an exact profile certificate and a full finite (24,8) exclusion

> **Alternate proof route (2026-10-31, unreviewed):** [Weighted indegree deficits and B-subset capacities](../research/drafts/M074_WEIGHTED_DEFICIT.md) give a hand case split that does not rely on the 19 × 5005 profile classification below. A separate histogram audit and weakened-cut negative control test the new inequalities. Neither route has independent specialist review or establishes a new unrestricted CH result.

**Research record, 2026-10-31.** The argument below closes the previously open **indegree-nine branch** by combining an auditable 19 × 5005 integer-profile lemma with a global degree-counting contradiction. **Independent specialist proof review remains pending.** It does not settle the unrestricted Caccetta–Häggkvist conjecture. **No novelty is claimed:** [wustep/maths](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md) has already reported computational exclusion of the full finite (24,8) case.

## Exact finite theorem

**Theorem.** Every loopless digraph on 24 vertices with minimum outdegree at least eight contains a directed cycle of length at most three.

Suppose otherwise. A graph without a directed 2-cycle or 3-cycle is oriented. Delete surplus outgoing arcs independently until **all outdegrees are exactly eight**; deletion cannot create a cycle. We must exclude an oriented, directed-triangle-free graph \(D\) on 24 vertices with all outdegrees exactly eight.

We use two previously established local results from [../research/M074_ELEMENTARY_24_REGULAR.md](../research/M074_ELEMENTARY_24_REGULAR.md): (i) a directed-triangle-free oriented graph on eight vertices with minimum outdegree two has at most **21 arcs**, all indegrees at most **three**, and any indegree-three vertex has outdegree exactly **two**; it cannot have minimum outdegree three; (ii) the 24-vertex case with every indegree and outdegree eight is impossible. The latter uses the 22-versus-15 cross-cut inequality and **does not** imply the present theorem on its own.

### 1. An indegree-nine vertex must exist

Fix any vertex \(v\), let \(b=d^-(v)\), \(A=N^+(v)\) (eight vertices), \(B=N^-(v)\), and \(C\) the remaining \(15-b\) vertices. No arc can go from \(A\) to \(B\) (directed triangle), or from \(A\) to \(v\) (digon). Each \(a\in A\) has internal outdegree at least \(8-(15-b)=b-7\). If \(b\ge10\), the induced eight-vertex graph on \(A\) would have minimum outdegree at least three, impossible. Thus every indegree is at most nine. If no indegree were nine, average indegree eight would force 8-in/8-out regularity, already excluded. **Fix \(v\) with indegree nine.**

### 2. Five necessary constraints for the indegree-nine root

Write \(A=N^+(v)\), \(B=N^-(v)\), \(C=V\setminus(A\cup B\cup\{v\})\), so \((|A|,|B|,|C|)=(8,9,6)\). Let

- \(\alpha_a=d_A^+(a)\ge2\), \(m=\sum_{a\in A}\alpha_a=e(A,A)\le21\);
- \(k_b=d_C^-(b)\in\{0,\ldots,6\}\) for \(b\in B\);
- \(q_b=|\{a\in A:\alpha_a\ge k_b+2\}|\).

The \(A\)-vertices have 64 outgoing arcs, none into \(B\) or \(v\), so \(e(A,C)=64-m\). Orientation on the 8×6 cut gives \(e(C,A)\le48-(64-m)=m-16\). All six \(C\)-vertices have indegree at most nine, so \(e(B,C)+e(C,C)\le54-(64-m)=m-10\). Counting 48 arcs leaving \(C\) yields

\[
\boxed{\sum_{b\in B}k_b=e(C,B)\ge74-2m.}\tag{1}
\]

The \(B\)-vertices send 72 arcs in total, including nine arcs into \(v\). At most \(\binom{9}{2}=36\) lie inside \(B\), and at most \(m-10\) enter \(C\). Therefore

\[
\boxed{e(B,A)\ge37-m.}\tag{2}
\]

For \(b\to a\), any path \(a\to c\to b\) would close a directed triangle. The \(8-\alpha_a\) outgoing \(C\)-neighbors of \(a\) and the \(k_b\) incoming \(C\)-neighbors of \(b\) must be disjoint subsets of six vertices. Thus \(8-\alpha_a+k_b\le6\), i.e. **\(\alpha_a\ge k_b+2\)**. The \(B\)-vertex \(b\) can therefore send at most \(q_b\) arcs to \(A\). Combined with (2),

\[
\boxed{\sum_{b\in B}q_b\ge37-m.}\tag{3}
\]

It can send at most \(6-k_b\) arcs to \(C\), since every \(C\to b\) arc precludes the opposite arc. Because \(b\) sends one arc to \(v\) and has total outdegree eight,

\[
\boxed{d_B^+(b)\ge f_b:=\max(0,1+k_b-q_b).}\tag{4}
\]

For any \(S\subseteq B\) of size \(s\), at most \(\binom{s}{2}\) arcs go between vertices inside \(S\), and at most \(s(9-s)\) go from \(S\) to \(B\setminus S\). Sort the nine \(f_b\)'s in descending order and take \(S\) to be the vertices with the largest \(s\) lower bounds:

\[
\boxed{\sum_{i=1}^s f_{(i)}\le s(17-s)/2\quad (s=1,\ldots,9).}\tag{5}
\]

Each inequality follows from the original graph assumptions without assuming regular indegrees, a solver verdict, or the existence of any of the integer profiles.

### 3. Exhaustive small integer-profile lemma

Sort the eight \(\alpha_a\)'s and nine \(k_b\)'s. This is lossless because (1)–(5) are symmetric under relabeling in \(A\) and \(B\). The \(\alpha\)'s are between two and seven, with sum at most 21: precisely **19** multisets. The \(k\)'s range from zero to six: precisely \(\binom{15}{9}=\mathbf{5005}\) multisets.

The exact finite filter is:

| Required constraints | Pairs remaining |
|---|---:|
| (1), \(\sum k\ge74-2m\) | 20,500 |
| (1) and (3), cross-cut eligibility | 1,116 |
| (1), (3) and all nine subset-capacity inequalities (5) | **83** |

The 83 survivors consist of only two internal \(A\) outdegree multisets:

| \(\alpha\) sorted | Compatible relaxed \(k\) multisets |
|---|---:|
| \((2,2,2,2,2,2,2,7)\) | 77 |
| \((2,2,2,2,2,2,3,6)\) | 6 |

Both have **\(m=21\)**. This is a necessary-condition result; surviving integer profiles are **not** claimed to correspond to realizable 24-vertex digraphs.

Reproduce with [the finite checker](../scripts/ch24_irregular_profiles.py), which enumerates the 19 × 5005 multisets directly. The [independent regression](../tests/test_ch24_irregular_profiles.py) rebuilds both multiset families using **different algorithms** (weak surplus partitions and combinadic indices) and recomputes the same counts and survivor identities. It also provides a genuine triangle-free eight-vertex control for the first profile.

### 4. Eliminate the six-outdegree local profile

Suppose the \(A\)-subgraph has internal outdegrees \((2^6,3,6)\) and \(m=21\). Let \(x\) have outdegree six and \(z\) have outdegree three. Orientation implies \(d_A^-(x)\le1\); the eight-vertex local lemma (indegree three implies outdegree two) gives \(d_A^-(z)\le2\); each other vertex has indegree at most three. These upper bounds sum to \(1+2+6(3)=21\), so every bound is attained.

In particular \(d_A^-(x)=1\), while **every other vertex has indegree at least two**. The six-outdegree vertex \(x\) points to six of the other seven vertices. Let \(y\) be the sole vertex it does not point to. The unique incoming arc of \(x\) must be \(y\to x\). Because \(y\) has indegree at least two, some \(t\) among the six outneighbors of \(x\) points to \(y\). Hence \(y\to x\to t\to y\) is a directed triangle, contradiction.

Therefore **only the first profile \((2^7,7)\) remains** for any indegree-nine root.

### 5. Seven low outneighbors at every indegree-nine vertex

Let \(u\in A\) have internal outdegree seven. It points to each of the other seven \(A\)-vertices \(X=A\setminus\{u\}\). Every vertex \(a\in X\) has internal outdegree two, both into **other vertices of \(X\)**, since \(u\to a\) forbids \(a\to u\). Also each \(a\in X\) sends six arcs to \(C\), and therefore receives none from \(C\).

From (1) and \(m=21\), \(e(C,B)=\sum k_b\ge32\); as each of nine \(B\)-vertices receives at most six arcs from \(C\), at least **six** vertices of \(B\) have a predecessor in \(C\). None of those six can point to any \(a\in X\), or \(a\to c\to b\to a\) would be a triangle. At most three \(B\)-vertices can point into \(X\). Each \(a\in X\) thus has indegree at most

\[
1\ \text{(from \(v\))}+3\ \text{(inside \(A\))}+3\ \text{(from \(B\))}+0\ \text{(from \(C\))}=7.
\]

**Every indegree-nine vertex points to seven distinct vertices of indegree at most seven.** Those seven vertices also send two arcs each *to other members of that very seven-vertex low-indegree set*.

### 6. Global contradiction

Let \(H\) be the vertices of indegree nine, \(L\) the vertices of indegree at most seven, and put \(h=|H|\), \(\ell=|L|\). All other indegrees are eight. Since all outdegrees equal eight and total indegree equals total outdegree,

\[
h=\sum_{a\in L}(8-d^-(a))\ge\ell.
\]

Each high vertex has seven low outneighbors, so \(e(H,L)\ge7h\). Every low vertex has indegree at most seven, so \(e(H,L)\le7\ell\). Consequently

\[
7h\le e(H,L)\le7\ell\le7h.
\]

Equality holds throughout. Every low vertex must have indegree **exactly seven** and all of its incoming arcs originate in \(H\). Therefore **\(e(L,L)=0\)**.

But \(H\) is nonempty by section 1. Choose \(v\in H\) and its seven low outneighbors \(X\subseteq L\) from section 5. Every \(a\in X\) sends two arcs to other vertices of \(X\). Thus **\(e(L,L)\ge14\)**, contradiction. This proves the stated finite theorem. □

## Verification, provenance, and review gates

Run from the repository root:

```sh
python3 scripts/ch24_irregular_profiles.py
python3 -m unittest discover -s tests -p 'test_ch24_irregular_profiles.py' -v
python3 -m unittest discover -s tests -p 'test_ch24_crosscut.py' -v
```

The core 83-profile certificate is a finite integer computation, **not** exhaustive graph search, and its mathematical use depends on the soundness of the explicitly proved cut inequalities. Even if CI passes, seek independent specialist review of the eight-vertex local lemma, the 19 × 5005 reduction, the triangle elimination and the global quantifiers.

The result is **a review-ready candidate proof of the complete finite (24,8) case**, already computationally excluded elsewhere. We have not independently replayed that earlier external DRAT corpus; no accepted publication, originality, arbitrary-\((n,r)\) extension, or Solved archive entry is implied. Subsequent work should seek an independent referee and test whether the high/low mechanism generalizes beyond \((24,8)\).