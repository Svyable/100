# M074 — the 24-vertex, degree-eight regular case is impossible

**Dated:** 2026-10-31. **Status:** self-contained structural proof with independently repeatable finite integer check; independent specialist proof review pending. This is a **restricted** case of the directed-triangle Caccetta–Häggkvist question, **not** a proof at (24,8) under only a minimum **outdegree** condition, and not the unrestricted conjecture. External [wustep/maths](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md) already reports computational exclusion of the *full* (24,8) finite case. We assert no novelty or external acceptance.

## The exact theorem

**Theorem.** There is no directed-triangle-free oriented graph on 24 vertices in which *every* vertex has indegree **and** outdegree exactly eight.

A directed graph with digons already has a directed 2-cycle, so the oriented hypothesis is the relevant counterexample class.

### Lemma 1 — the eight-vertex local budget

Let H be a directed-triangle-free oriented graph on eight vertices with minimum outdegree at least two.

1. Every vertex of H has indegree at most three.
2. The total number of arcs of H is at most **23**.
3. No such graph has minimum outdegree at least three.

**Proof.** Fix a vertex, with outdegree a and indegree b; set A=N+(v) and C=V(H)\\(A∪N-(v)∪{v}). For k=2 or 3, if every vertex has outdegree at least k, then each vertex of A sends at least k arcs to A∪C. Because H has neither digons nor directed triangles,

    k a <= e(A,A) + e(A,C)
        <= a(a-1)/2 + a(7-a-b),

which gives **a + 2b <= 13 - 2k**.

For k=3 this forces b<=2 (since a>=3), contrary to average indegree at least three; so (3) holds. For k=2, a>=2 gives b<=3, proving (1). Thus e(H)<=24. If e(H)=24, then every indegree equals three. The k=2 inequality a+2b<=9 now yields a<=3 for every vertex, while average outdegree is three; all outdegrees equal three, contradicting (3). Therefore e(H)<=23, proving (2). QED.

### Lemma 2 — cross-cut edge demand in any regular 3r-vertex candidate

Suppose D is an oriented, directed-triangle-free graph on 3r vertices with every indegree and outdegree equal to r. Fix a root v. Put A=N+(v), B=N-(v), C=V\\(A∪B∪{v}), so |A|=|B|=r and |C|=r-1. Set

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

Let α_1,…,α_8 and β_1,…,β_8 be integers between two and seven with Σα_i<=23 and Σβ_j<=23. At most **15** of the 64 pairs (i,j) have α_i+β_j>=9.

**Proof.** Write x_i=α_i−2, y_j=β_j−2. These numbers are nonnegative, at most five, with Σx<=7 and Σy<=7. We must count pairs x_i+y_j>=5.

If both arrays have an entry equal to five, all remaining entries in each array sum to at most two. Every eligible pair lies in the exceptional row or column, giving at most 8+8−1=15. If only one array has a five, its exceptional row contributes at most eight and all other entries on that side sum to at most two. Those remaining entries can give at most two further pairs (a single 2 requires y>=3, of which at most two exist; or two 1s each require y>=4, of which at most one exists). Thus at most ten.

If both arrays have maximum four, each has at most one four. The exceptional row and column contribute at most 7+7−1=13 eligible pairs (a four needs the opposite entry to be positive). The other entries on each side sum to at most three, so there can be at most one additional pair with both entries at least two; total at most 14. If only one array has a four and neither has a five, its exceptional row contributes at most seven and its other entries (total <=3) contribute at most three more pairs, for at most ten. Finally, if both maxima are at most three, eligible pairs require both entries >=2; each array has at most three such entries, giving at most nine pairs. QED.

### Proof of the theorem

Apply Lemma 2 with r=8. Both induced 8-vertex graphs D[A] and the arc-reversal of D[B] have minimum outdegree at least two. Lemma 1 gives m_A<=23 and m_B<=23. Thus Lemma 2 forces **t=e(B,A)>=64−46=18**.

On the other hand, Lemma 2 permits an arc b→a only when α(a)+β(b)>=9. Lemma 3 says there are at most **15** such ordered pairs. Hence **18<=t<=15**, a contradiction. QED.

## What remains for the *full finite* (24,8) statement

**Proposition (necessary irregularity and an exact nine-indegree pivot).** In a hypothetical 24-vertex directed-triangle-free oriented graph with minimum outdegree eight, delete excess outgoing arcs to make all outdegrees exactly eight. No vertex can have indegree >=10: if a root has indegree b>=10, its eight outneighbors have at least b−7>=3 outgoing neighbors within their own eight-vertex induced graph, contrary to Lemma 1(3). Thus all indegrees are at most nine. If no vertex had indegree nine, their average eight would make the graph 8-in/8-out-regular, excluded above. Therefore a remaining hypothetical counterexample **must** have an indegree-nine vertex and some vertex of indegree at most seven.

At an indegree-nine root v, the eight outneighbors A have total internal arcs m_A<=23, hence their 64 outgoing arcs include at least 41 arcs A→C, where C is now the six-element nonneighbor set. Because all α>=2 and Σα<=23, **some a∈A has α(a)=2** and therefore points to *all six* vertices of C. For any b∈B receiving an arc c→b from C, the arc b→a is impossible. These are necessary conditions, not a proof that indegree nine cannot occur.

This isolates the **next mathematical task**: exclude the indegree-nine branch without assuming exact in/out regularity; alternatively produce a genuinely independent and reviewable finite certificate. Do not import the 8-inregular assumption into the missing branch.

## Verifying the arithmetic without a SAT solver

From the repository root:

    python3 scripts/ch24_crosscut.py
    python3 -m unittest discover -s tests -p 'test_ch24_crosscut.py' -v

The stand-alone checker enumerates all **42** sorted eight-tuples with entries in [2,7] and sum at most 23, then checks all 42² profile pairs. It independently recomputes the case-bound and shows the maximum *eligible pairs* is 15 while the minimum required cross arcs is 18. This integer check is **not** an exhaustive enumeration of 24-vertex digraphs. The mathematical proof is the preceding lemmas.

**Related source checks:** [EGRES open status](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture), [Hladký–Král'–Norine published triangle bound](https://doi.org/10.1007/s00493-015-2662-5), and [wustep's prior finite computations](https://github.com/wustep/maths/blob/main/problems/caccetta-haggkvist-k3/ATTACK.md). The general conjecture remains open. Leave the M074 registry evidence state and `data/solved.json` unchanged.
