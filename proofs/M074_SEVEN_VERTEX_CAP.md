# M074 — a seven-vertex dense-cut obstruction

**2026-10-31, finite auxiliary theorem.** This is an elementary bound used to audit a *relaxed* irregular (27,9) Caccetta–Häggkvist profile. It is not a proof of the full (27,9) instance or of the unrestricted conjecture. Independent mathematical review and a prior-art check remain outstanding.

## Theorem

A loopless oriented digraph on **seven** vertices with **no directed triangle** and maximum indegree at most **three** has **at most 17 arcs**.

### Proof

Assume there are at least 18 arcs. The underlying undirected graph has at most three missing edges. It cannot contain a five-vertex clique: every triangle-free orientation of a complete graph is a transitive tournament, and a transitive tournament on five vertices has a vertex with **four incoming arcs**, contradicting the indegree ceiling.

If at most two edges were missing, remove at most two vertices covering those missing edges; the remaining five vertices form a clique. Likewise, with exactly three missing edges, if two share an endpoint then those two and the remaining missing edge can be covered by two vertices, again leaving a clique on five vertices. Thus **exactly three nonedges occur, and they form a matching**. Label the nonadjacent pairs \(\{p,p'\},\{q,q'\},\{r,r'\}\) and the unpaired vertex \(s\). Every other pair is connected by exactly one arc.

Let \(B=N^-(s)\) and \(A=N^+(s)\). Since \(s\) is adjacent to all six other vertices and has indegree at most three, \(b=|B|\in\{0,1,2,3\}\) and \(|A|=6-b\). Every edge between \(A\) and \(B\) points **from B into A**: an edge \(a\to b'\) would create \(s\to a\to b'\to s\).

* **b=3.** Each \(a\in A\) receives an arc from \(s\) and from every vertex of \(B\) except possibly its nonadjacent mate. If its mate were not in \(B\), its indegree would be at least four. Therefore \(A\) consists of one member of each nonadjacent pair, and \(B\) of their three mates. Each \(a\in A\) receives exactly three arcs from \(s\cup B\), but the three vertices of \(A\) are pairwise adjacent. At least one receives an additional arc, contradiction.
* **b=2.** If the two vertices of \(B\) are mates, then the four vertices of \(A\) receive three arcs each from \(s\cup B\), yet there are edges within \(A\). If \(B\) instead contains one vertex from each of two pairs, the two vertices \(u,u'\) of the untouched third pair lie in \(A\), each with three incoming arcs from \(s\cup B\). Consequently both must point to each of the remaining two \(A\)-vertices. Either remaining vertex then receives two arcs from \(u,u'\), one from \(s\) and one from the \(B\)-vertex that is not its mate: at least four, contradiction.
* **b=1.** Let \(p\in B\), let its mate \(p'\in A\), and let \(Q=\{q,q'\}\) and \(R=\{r,r'\}\) be the other two nonadjacent pairs inside \(A\). Each vertex of \(Q\cup R\) already receives two arcs (from \(s\) and \(p\)), so can receive at most one more. The four edges of the complete bipartite graph between \(Q\) and \(R\) therefore supply **exactly one** incoming arc to each of its four vertices. None can additionally receive an arc from \(p'\). All four must point to \(p'\), which also receives an arc from \(s\), giving indegree at least five.
* **b=0.** Every vertex other than \(s\) receives an arc from \(s\), so its indegree in the remaining six-vertex graph is at most two. This graph has all twelve edges of \(K_{2,2,2}\), hence its total indegree is twelve and **every** internal indegree is exactly two. Reversing all arcs gives a triangle-free oriented graph on six vertices with minimum outdegree two. This is impossible by the independent [six-vertex lemma](../research/M074_ELEMENTARY_18.md).

Every possible value of \(b\) is contradictory. Hence the assumed 18 arcs are impossible and the bound is proved. □

## Sharpening: the sharp cap is 16 (finite exhaustive certificate)

The preceding hand argument excludes 18 or more arcs. An additional **fully bounded finite check** excludes 17 arcs, leaving the sharp bound **16**. This stronger step is an exhaustively checked finite theorem, not an additional enumeration-free hand proof.

A hypothetical 17-arc example has exactly **four missing unordered pairs** among the 21 pairs of seven vertices. Let \(M\) be that four-edge *undirected* missing-pair graph. Since the oriented graph contains no triangle, it cannot contain an underlying \(K_5\): a triangle-free tournament on five vertices is transitive, with a sink of indegree four. Thus \(M\) has no two-vertex edge cover.

There are **exactly three** relevant graph types for \(M\), up to relabeling:

1. If \(M\) contains a triangle, its fourth edge must be disjoint from that triangle; otherwise two vertices cover all four edges. Hence \(M\cong K_3\sqcup K_2\) plus two isolated vertices.
2. If \(M\) contains no triangle, it is bipartite (a graph with only four edges cannot contain another odd cycle). By the bipartite matching/vertex-cover theorem, absence of a two-vertex cover forces a matching of size at least three. The fourth edge either connects one matched endpoint to the seventh, previously unmatched vertex, yielding \(P_3\sqcup K_2\sqcup K_2\), or joins two disjoint matching pairs, yielding \(P_4\sqcup K_2\) plus one isolated vertex.

For each type, fix the explicit missing pairs in [ch27_seventeen.py](../scripts/ch27_seventeen.py). Every other one of the 17 unordered pairs has **exactly two** orientations. Enumerate the \(2^{17}=131{,}072\) bit assignments, calculate all seven indegrees and scan all ordered triples for directed triangles, and keep exactly those with maximum indegree at most three and no triangle. This finite proof has the following exhaustive table (a second adjacency-matrix implementation repeats all checks):

| Missing graph | Orientations | Indegree-cap survivors | Triangle-free survivors |
|---|---:|---:|---:|
| Triangle + disjoint edge | 131,072 | 17,192 | **0** |
| Four-vertex path + disjoint edge | 131,072 | 18,460 | **0** |
| Three-vertex path + two disjoint edges | 131,072 | 20,004 | **0** |

Thus 17 arcs are impossible. If a graph had more than 17 arcs, deleting arcs down to exactly 17 preserves orientation, absence of directed triangles, and the maximum-indegree bound, so that is impossible too. The 16-arc positive example in [ch27_seven.py](../scripts/ch27_seven.py) has maximum indegree three and no directed triangle. Consequently **16 is the sharp maximum**.

This bounded orientation enumeration is not a proof-assistant kernel certificate, and it needs independent expert inspection of both the graph classification and the code. It is not evidence of a 27-vertex global exclusion.

## Consequence for the (27,9) irregular root

With the notation of [the (27,9) proof](M074_27_REGULAR.md), the seven-vertex set \(C\) has maximum **internal** indegree at most three whenever seven distinct members of \(A\) send an arc to every member of \(C\). The ambient indegree ceiling is ten, so those seven incoming arcs leave room for at most three internal predecessors.

For the previously noted *relaxed* \(z=4\) profile

    alpha=(2,2,2,2,2,2,2,7,8),  m=29
    k=(0,0,0,0,5,5,5,5,7,7),  e(C,B)=34,

the seven alpha-two vertices cover all of \(C\). Thus \(e(C,C)\le16\) by the sharp finite bound above (the hand-only bound 17 also suffices for this particular profile). But seven C vertices send 63 outgoing arcs, while \(e(C,A)\le m-18=11\). Therefore

    e(C,C) = 63-e(C,B)-e(C,A) >= 63-34-11 = 18,

a contradiction. **This particular integer profile is excluded.** Moreover, the profile \(\alpha=(2^7,6,8)\), \(k=(0^4,4,5,6,7,7,7)\) from the earlier note is likewise excluded: it requires at least 17 internal C arcs. The sharp bound 16 still leaves other relaxed \(z=4\) profiles, and does not prove the finite (27,9) theorem.

## Independent computational cross-check

[scripts/ch27_seven.py](../scripts/ch27_seven.py) enumerates all \(2^{18}=262,144\) orientations of the unique 18-edge undirected graph surviving the five-clique reduction. Exactly **19,592** have maximum indegree at most three; **zero** among them avoid a directed triangle. The checker tests a separate 16-edge triangle-free positive control; enumeration corroborates the hand proof but is not its premise.

Reproduce:

    python3 scripts/ch27_seventeen.py --check
    python3 -m unittest discover -s tests -p 'test_ch27_seventeen.py' -v
    python3 scripts/ch27_seven.py --check
    python3 -m unittest discover -s tests -p 'test_ch27_seven.py' -v

**Evidence limit:** The full general Caccetta–Häggkvist conjecture, the 27-vertex irregular case, and independent specialist acceptance all remain open.
