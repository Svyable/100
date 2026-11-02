# M074 — rank-forced missing pairs and girth eliminate CH(27,9) z=3

**Research proof candidate (2026-11-01).** A restricted, computer-audited *necessary-condition* exclusion in the directed-triangle Caccetta–Häggkvist problem. Its mathematical argument consists of finite structural lemmas plus an exhaustive integer-profile certificate; the certificate does **not** enumerate 27-vertex graphs. Independently accepted proof review and historical novelty assessment are absent. The full (27,9) minimum-outdegree-only case and the unrestricted conjecture remain open in this research record.

## Statement

Let D be an oriented directed-triangle-free digraph on 27 vertices with all outdegrees exactly nine. Fix a vertex v with indegree ten and let A=N⁺(v), B=N⁻(v), C the nonneighbors of v, of orders 9, 10, 7 respectively. Let k(b)=d⁻_C(b) and z=#{b∈B:k(b)=0}.

**Restricted theorem (candidate):** z≠3. With the earlier [z≤3 theorem](M074_ZERO_K_THREE.md), this gives **z≤2**. No claim concerning possible z=0,1,2 configurations follows.

## 1. The existing root constraints

Write α(a)=d⁺_A(a) and m=Σ_A α(a). Because A sends no arcs to v or B and each vertex has outdegree nine, d⁺_C(a)=9−α(a). The [sharp nine-vertex lemma](M074_NINE_VERTEX.md) gives 2≤α≤8, m≤29, and at least one α=2. Each ambient indegree is ≤10 by the same lemma. Let M count unoriented (missing) A–C vertex pairs and K=e(C,B)=Σ_B k(b). Counting incoming arcs at C and all arcs out of C gives

    e(A,C)=81−m,        e(C,A)=m−18−M,
    e(B,C)+e(C,C)≤m−11,
    K≥92−2m+M.                                             (1)

As in [the regular-branch dossier](M074_27_REGULAR.md), an edge b→a, b∈B, a∈A, requires α(a)≥k(b)+2: otherwise a→c→b→a occurs for some c∈C. Put q(j)=#{a∈A:α(a)≥j+2}; then the internal B-outdegree of b satisfies

    d⁺_B(b) ≥ f(b):=max(0,1+k(b)−q(k(b))).                  (2)

Let f_1≥...≥f_10 be the ten sorted floors. The standard oriented subset capacity says

    Σ_{i=1}^s f_i ≤ s(19−s)/2,   1≤s≤10.                  (3)

The previously established [B-small-subset lemma](M074_B_INTERNAL_GIRTH.md) additionally requires f_3≤7, f_5≤6 and f_6≤5.

## 2. Rank-forced missing A–C pairs

**Lemma A (rank deficit).** For any nine-entry α degree tuple, define for each a∈A with d=α(a) the number t_a equal to the **d-th largest** α-value among the other eight A vertices. Then

    M ≥ R(α):=Σ_{a∈A} max(0,α(a)−t_a).                     (4)

**Proof.** Vertex a has d distinct internal A-outneighbors. At least one has α(a′)≤t_a. The C-outneighbor sets P_x=N⁺_C(x) have sizes |P_x|=9−α(x). For a→a′, every c∈P_{a′}\P_a must be **nonadjacent** to a: a→c is absent and c→a would complete a→a′→c→a. So at least max(0,α(a)−α(a′))≥max(0,α(a)−t_a) missing pairs are incident with a. Missing pairs corresponding to distinct sources a have different first coordinates and may be summed. □

This refines the single-source missing-pair estimate. It uses only the sorted degrees and triangle exclusion, not a supposed realization of every degree tuple.

## 3. Two-edge girth deficit inside B

**Lemma B (induced-girth capacity).** For each integer 4≤s≤10 such that f_s≥11−s,

    Σ_{i=1}^s f_i ≤ s(19−s)/2−2.                           (5)

**Proof.** Let S consist of the s vertices having the largest lower bounds f_i. Every b∈S has at most 10−s B-outneighbors outside S, so its internal S-outdegree is at least f_s−(10−s)≥1. Hence D[S] has a directed cycle. Since D is directed-triangle-free, a *shortest* cycle has length at least four. That cycle is chordless: either directed orientation of a chord would give a shorter directed cycle. In particular at least two unordered vertex pairs of S are nonadjacent (choose two diagonals if the shortest cycle has four vertices; a longer chordless cycle has at least two absent chords as well). Thus e(S,S)≤binom(s,2)−2. At most s(10−s) arcs leave S for B\S. Summing the B-outdegree floors proves (5). □

This is an elementary instance of a directed-girth edge deficit. Related general girth-deficit work exists in [PR #134](https://github.com/Svyable/100/pull/134); this note does not assert novelty for the general lemma or rely on that unmerged PR.

## 4. Exhaustive *integer* reduction, not a graph enumeration

For z=3, the ten sorted k-values have three zeros and seven entries chosen with repetition from {1,...,7}: exactly C(13,6)=1,716 tuples. The nine α-values lie in {2,...,8}, sum≤29, giving exactly 166 sorted tuples. The complete necessary-condition space has **284,856** pairs. Applying the mathematically proved constraints in this exact order:

| Filter | Newly excluded | Remaining |
|---|---:|---:|
| Root cut K≥92−2m | 253,556 | 31,300 |
| Ordinary B-subset capacity (3) | 22,498 | 8,802 |
| Previous small-subset girth | 2,255 | 6,547 |
| Rank-forced missing pairs (1), (4) | 6,448 | 99 |
| New girth deficit (5) | 97 | **2** |

Two independent implementations, one using sorted combinations and the other histogram compositions, replay the classification and agree on the two remaining relaxed integer pairs, which are **not graphs**:

    I:  α=(2,2,2,3,3,3,3,3,8),  k=(0,0,0,5,5,6,6,6,6,6).
    II: α=(2,2,2,3,4,4,4,4,4),  k=(0,0,0,2,3,4,5,6,7,7).

The exact finite enumeration is a premise only for the claim that these are the *last two necessary integer profiles*. To falsify the reduction, exhibit a third tuple satisfying all five explicitly stated inequalities. The two remaining structural contradictions are proved without enumeration.

## 5. Both endpoints are impossible

**Case I (dominated five).** Here m=29, K=40. The rank-deficit (4) gives M≥6, and e(C,A)=m−18−M≤5. Meanwhile e(B,C)+e(C,C)≤m−11=18, so e(C,C)≤18. As 63=K+e(C,A)+e(C,C), necessarily e(C,A)≥63−40−18=5. Thus e(C,A)=5 exactly.

Each of the three α=2 vertices points to **every** vertex of C and cannot receive from C. The unique α=8 vertex points to all other vertices of A (including α=2 vertices), so it also cannot receive from C: c→a would close a→low→c→a. Every α=3 vertex can receive at most α−2=1 arcs from C, by orientation and its six arcs to C. Since five C→A arcs are needed, all five α=3 vertices receive one. None can point to any α=2 vertex (y→low→c→y would be a triangle), or to the α=8 vertex (it points into all five). All three outgoing A-arcs of each of the five α=3 vertices must therefore lie within the same five-vertex set. This would give **15** arcs among five vertices, exceeding binom(5,2)=10 for an oriented graph. Contradiction.

**Case II (three descending sources).** Here m=29 and K=34. Let H consist of the five A vertices of internal outdegree four. Collectively they send 20 internal A arcs, at most binom(5,2)=10 among H, so at least ten arcs point from H to its four lower-degree complements. Since a single H vertex has total A-outdegree four, these ten arcs originate at **at least three distinct** H vertices. For each such source a, some edge a→a′ has α(a′)≤3, so the triangle-propagation rule gives at least one missing A–C pair incident with a. The three sources give M≥3. Equation (1) now forces K≥92−58+3=37, contrary to K=34.

Both last profiles are impossible. Thus **z≠3**, and when combined with the earlier z≤3 theorem, **z≤2**, under the stated hypotheses. □

## 6. Consequence and boundary

At an indegree-ten root v, at least one a∈A has α(a)=2 (otherwise A would have internal minimum outdegree three, forbidden by the nine-vertex lemma). For this a, all seven C vertices are its outneighbors; it has no incoming arc from C. The nine-vertex rooted inequality gives d⁻_A(a)≤4, and only vertices b with k(b)=0 may send b→a, so d⁻_B(a)≤z≤2. With v→a:

    d⁻_D(a)≤1+4+2=7.

**Every indegree-ten root therefore has an outneighbor with indegree at most seven.** This is not the eight-low-neighbor condition required by the global degree-defect transfer proof, and the z=0,1,2 branches remain unexcluded. Full CH(27,9) and the unrestricted Caccetta–Häggkvist conjecture are not claimed solved.

## Verification, falsifiers and review status

Run:

    python3 scripts/ch27_z3_girth.py --check
    python3 -m unittest discover -s tests -p 'test_ch27_z3_girth.py' -v

The main checker enumerates 166×1,716 sorted profiles and the independent test generates them via degree histograms, recomputes the rank deficit using a distinct threshold count, and independently evaluates all inequalities. Exhaustive small-graph controls consider every oriented partial graph on four and five vertices; mutation deleting the two-edge girth deficit restores 99 relaxed candidates; omitting the two endpoint arguments restores exactly two. These are **integer and small-graph controls**, not an actual 27-vertex graph UNSAT certificate or proof-assistant formalization.

Before mathematical publication or status promotion, obtain independent specialist review of the root cut, rank-deficit summation, shortest-cycle chord argument, endpoint equality conditions and completeness of the finite profile enumerator; perform a prior-art assessment. Do not change data/solved.json or the general problem evidence state. The external [EGRES entry](https://lemon.cs.elte.hu/egres/open/Caccetta-H%C3%A4ggkvist_conjecture) continues to treat the unrestricted conjecture as open.
