# M074 — the 24-vertex, degree-eight regular case is impossible

**Dated:** 2026-10-31. **Status:** self-contained structural proof with independently repeatable finite integer check; independent specialist proof review pending. This is a **restricted** case of the directed-triangle Caccetta–Häggkvist question, **not** a proof at (24,8) under only a minimum **outdegree** condition, and not the unrestricted conjecture. External [wustep/maths](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md) already reports computational exclusion of the *full* (24,8) finite case. We assert no novelty or external acceptance.

## The exact theorem

**Theorem.** There is no directed-triangle-free oriented graph on 24 vertices in which *every* vertex has indegree **and** outdegree exactly eight.

A directed graph with digons already has a directed 2-cycle, so the oriented hypothesis is the relevant counterexample class.

### Lemma 1 — the eight-vertex local budget

Let H be a directed-triangle-free oriented graph on eight vertices with minimum outdegree at least two.

1. Every vertex of H has indegree at most three.
2. The total number of arcs of H is at most **21**; this is sharp.
3. No such graph has minimum outdegree at least three.

**Proof.** Fix a vertex, with outdegree a and indegree b; set A=N+(v) and C the vertices outside A, N-(v), and v. For k=2 or 3, if every vertex has outdegree at least k, then each vertex of A sends at least k arcs to A∪C. Because H has neither digons nor directed triangles,

    k a <= e(A,A) + e(A,C)
        <= a(a-1)/2 + a(7-a-b),

which gives **a + 2b <= 13 - 2k**.

For k=3 this forces b<=2 (as a>=3), contrary to average indegree at least three; (3) follows. For k=2, a>=2 gives b<=3, proving (1).

We sharpen the arc count. A vertex of indegree three must have outdegree exactly **two**: the k=2 inequality gives a<=3; if a=3, the outneighbor set A has size three and C has size one. Every vertex of A must then send at least one arc inside A, forcing a directed 3-cycle on those three vertices. Similarly, a vertex of indegree two has outdegree at most **four**: a=5 would give C empty and force minimum outdegree two inside its five-vertex outneighborhood, impossible by the same counting inequality on five vertices. A vertex of indegree one has outdegree at most **five**: a=6 would give C empty and force minimum outdegree two inside six vertices, impossible by the [six-vertex obstruction](M074_ELEMENTARY_18.md).

Suppose e(H)>=22. Since all indegrees are at most three, at least six vertices have indegree three (otherwise total indegree is at most 5*3+3*2=21). No vertex has indegree zero: its presence would make the total indegree at most 7*3=21. If exactly six vertices have indegree three, the other two must each have indegree two, so total outdegree is at most 6*2+2*4=20. If seven vertices have indegree three, the final vertex has indegree one or two, and total outdegree is at most 7*2+5=19. With eight indegrees equal to three, the total outdegree is at most 8*2=16. All contradict e(H)>=22. Therefore **e(H)<=21**.

Sharpness: take the seven-vertex oriented circulant with steps {1,2}, which is 2-in/2-out-regular and triangle-free, and add a new vertex sending an arc to all seven old vertices but receiving none. The resulting eight-vertex graph has minimum outdegree two and exactly 14+7=21 arcs. QED.

### Lemma 2 — cross-cut edge demand in any regular 3r-vertex candidate

Suppose D is an oriented, directed-triangle-free graph on 3r vertices with every indegree and outdegree equal to r. Fix a root v. Put A=N+(v), B=N-(v), C the remaining vertices, so |A|=|B|=r and |C|=r-1. Set

- α(a)=outdegree of a *inside A*, for a∈A;
- β(b)=indegree of b *inside B*, for b∈B;
- m_A=e(A,A), m_B=e(B,B), and t=e(B,A).

By the prior [saturated-pivot lemma](M074_ELEMENTARY_18.md), α(a)>=2 and β(b)>=2. There are no A→B arcs: each would close v→A→B→v.

Every a∈A has r−α(a) outgoing neighbors in C, so at most α(a)−1 incoming neighbors in C. Its r incoming arcs must therefore include at least r−α(a)−d^-_A(a) arcs from B. Summing over a gives

    t >= r² - 2m_A.

Dually each b∈B has r−β(b) incoming neighbors from C, so can send at most β(b)−1 arcs into C. Its r outgoing arcs, including its arc to v, force at least r−β(b)−d^+_B(b) arcs into A. Summing gives

    t >= r² - 2m_B.

Finally, if b→a for b∈B and a∈A, there cannot be c∈C with a→c→b, since that would form a directed triangle. Their two respective subsets of C have sizes r−α(a) and r−β(b), so disjointness forces

    (r−α(a)) + (r−β(b)) <= r−1,
    or equivalently α(a)+β(b) >= r+1.

**This is a general theorem about any hypothetical regular counterexample**, not an assertion that such a graph exists. QED.

### Lemma 3 — an exact 8×8 integer crossing bound

Let α_1,…,α_8 and β_1,…,β_8 be integers between two and seven with Σα_i<=21 and Σβ_j<=21. At most **15** of the 64 pairs (i,j) have α_i+β_j>=9.

**Proof.** Put x_i=α_i−2 and y_j=β_j−2. All entries lie between zero and five, and Σx<=5, Σy<=5. Eligible pairs satisfy x_i+y_j>=5.

If both arrays have an entry five, every eligible pair lies in that one row or that one column, giving at most 8+8−1=15. If just one array has a five, all other entries on that side are zero, so its exceptional row/column accounts for at most eight eligible pairs. Otherwise each maximum is at most four. If both maxima equal four, each array has at most one further unit of positive surplus: all eligible pairs lie in the exceptional row/column, contributing at most 5+5−1=9. If just one side has a four, its exceptional row/column contributes at most five; the remaining surplus there is at most one and the other side has no four, so there are no further eligible pairs. If both maxima are at most three, an eligible pair requires both entries at least two. Each side has at most two such entries, so there are at most four eligible pairs. In all cases the total is at most **15**. QED.

### Proof of the theorem

Apply Lemma 2 with r=8. Both induced 8-vertex graphs D[A] and the arc-reversal of D[B] have minimum outdegree at least two. Lemma 1 gives m_A<=21 and m_B<=21. Thus Lemma 2 forces **t=e(B,A)>=64−42=22**.

On the other hand, Lemma 2 permits an arc b→a only when α(a)+β(b)>=9. Lemma 3 says there are at most **15** such ordered pairs. Hence **22<=t<=15**, a contradiction. QED.

## What remains for the *full finite* (24,8) statement

**Proposition (necessary irregularity and an exact nine-indegree pivot).** In a hypothetical 24-vertex directed-triangle-free oriented graph with minimum outdegree eight, delete excess outgoing arcs to make all outdegrees exactly eight. No vertex can have indegree >=10: if a root has indegree b>=10, its eight outneighbors have at least b−7>=3 outgoing neighbors within their own eight-vertex induced graph, contrary to Lemma 1(3). Thus all indegrees are at most nine. If no vertex had indegree nine, their average eight would make the graph 8-in/8-out-regular, excluded above. Therefore a remaining hypothetical counterexample **must** have an indegree-nine vertex and some vertex of indegree at most seven.

At an indegree-nine root v, the eight outneighbors A have m_A<=21 internal arcs, so they send at least **43** arcs into the six-element nonneighbor set C. Because each α>=2 and Σα<=21, some a∈A has α(a)=2 and therefore points to **all six vertices of C**. Every b∈B receiving even one arc from C cannot point to a (it would form a→c→b→a).

There are at most 48−e(A,C)<=5 arcs C→A, because digons are forbidden. The six vertices in C have 48 outgoing arcs in total, so e(C,B)+e(C,C)>=43. Since all indegrees are at most nine, and at least 43 incoming C-arcs arrive from A, we have e(B,C)+e(C,C)<=6*9−43=11, hence e(C,C)<=11. It follows that **e(C,B)>=32**. Each of the nine B-vertices receives at most six arcs from C, so at least six B-vertices have a predecessor in C; at most three do not. The saturated pivot a therefore receives at most three arcs from B, none from C, at most three from A (Lemma 1), and one from v. Thus **d⁻(a)<=7**.

This gives a tighter necessary structure: *every indegree-nine root has an outneighbor of indegree at most seven*. This is an irregular-branch obligation, not a contradiction and not a resolution of the full finite case.

This isolates the **next mathematical task**: exclude the indegree-nine branch without assuming exact in/out regularity; alternatively produce a genuinely independent and reviewable finite certificate. Do not import the 8-inregular assumption into the missing branch.

## Verifying the arithmetic without a SAT solver

From the repository root:

    python3 scripts/ch24_crosscut.py
    python3 -m unittest discover -s tests -p 'test_ch24_crosscut.py' -v

The stand-alone checker enumerates all **19** sorted eight-tuples with entries in [2,7] and sum at most 21, then checks all 19² profile pairs. It independently recomputes the case-bound and shows the maximum *eligible pairs* is 15 while the minimum required cross arcs is 22. This integer check is **not** an exhaustive enumeration of 24-vertex digraphs. The mathematical proof is the preceding lemmas.

**Related source checks:** [EGRES open status](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture), [Hladký–Král'–Norin published triangle bound](https://doi.org/10.1007/s00493-015-2662-5), and [wustep's prior finite computations](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md). The general conjecture remains open. Leave the M074 registry evidence state and `data/solved.json` unchanged.
