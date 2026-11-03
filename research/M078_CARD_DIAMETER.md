# M078 — subcubic tree-card motif collisions survive a diameter coordinate

**2026-11-02 US Central / 2026-11-03 UTC.** Claim [#277](https://github.com/Svyable/100/issues/277), work ID X-M078-CARD-DIAMETER, scope SHA-256 edf53c8c535ae8e7edd61d61e6ff8301ae56a385530216aa49bc8f0bbc4c624e.

**Classification:** Author-derived all-orders restricted negative theorem *candidate*, with an elementary proof and two differently implemented exact finite checkers. Historical priority and independent specialist mathematical acceptance are **not established**. It is **not** a counterexample to graph reconstruction: these trees have different full vertex-deleted decks.

## Exact statistic and theorem

For a finite graph H, let i_F(H) count vertex subsets inducing the unlabeled graph F. Define the paired card statistic D_k(G) as the multiset, over v in V(G), of the triple:

1. the vector (i_F(G-v)) over **all** unlabeled motifs F of orders 1 through k, including disconnected motifs;
2. the sorted degree sequence of G-v;
3. dmax(G-v), the **maximum diameter of a connected component** of G-v (isolated vertices have diameter zero).

All coordinates remain paired *within each card*, not just compared as marginal multisets.

**Restricted theorem candidate:** For every integer k >= 3 and every integer n >= 16k, there exist explicit **nonisomorphic connected subcubic trees** G and H on n vertices with D_k(G)=D_k(H). Both original trees have diameter 2A, and their card-diameter coordinates are A-1 for exactly one card and 2A for every other card. Thus this nonlocal diameter statistic does not repair the bounded-motif compressed deck.

This does not prove or refute the full reconstruction conjecture. The sufficient threshold 16k is not claimed optimal.

## Explicit construction for every n

Let L=2k-3, h=L+4=2k+1, q=floor((n-16k)/3), t=(n-16k) mod 3, and A=2h-1+q. Start with a central vertex o and three internally disjoint paths of length A from o to three leaves. At distance h from o along the first two paths, attach one extra pendant path, of respective lengths b,c.

| t | G: (b,c) | H: (b,c) |
|---|---|---|
| 0 | (L,L+2) | (L+1,L+1) |
| 1 | (L,L+3) | (L+1,L+2) |
| 2 | (L+1,L+3) | (L+2,L+2) |

Each pair has sum 2L+2+t, giving 1+3A+b+c=n. Every spur length lies in [L,h-1]. Both trees have exactly three degree-three vertices (the center and two attachment points), five leaves and n-8 degree-two vertices.

**Nonisomorphism:** Suppressing degree-two vertices, the three branch vertices form a three-vertex path; its middle vertex is the uniquely identifiable center. Each outer branch vertex has two leaf-directed segments of lengths {b,A-h} or {c,A-h}. Since b,c <= h-1 <= A-h, the smaller length recovers b or c. The unordered pair {b,c} is therefore an isomorphism invariant and differs between G and H for all three residue classes.

## Separated-landmark rooted-ball lemma

Let T be a tree, r>=2, and X={v:deg_T(v) != 2}. Suppose distinct vertices of X are separated by at least 2r-1 edges. Then the multiset of rooted induced radius-r balls depends only on |V(T)| and the number of exceptional vertices of each degree.

Indeed, no root can lie within distance r-1 of two exceptional vertices, since that would place them at distance at most 2r-2. A root at distance j<r from one exceptional vertex of degree d has a rooted ball determined solely by (d,j); other exceptional vertices can only occur at the radius boundary, where their additional incident edges are invisible. A root at distance at least r from every exceptional vertex has the ordinary rooted path ball of radius r. Each exceptional vertex of degree d contributes one root at distance zero and d roots at each distance 1,...,r-1. These root classes are disjoint, proving the lemma.

For the construction, take r=k-1, so L=2r-1. All pairs of leaves and branch vertices are separated by at least L: attachment-to-spur leaf >=L; attachment-to-main leaf A-h>=h-1>=L; center-to-attachment h>=L; all remaining exceptional-pair paths are longer. Consequently G and H have identical rooted radius-r ball multisets. Their ball-type multiplicities are exactly 3 for branch roots, 9 for each distance 1,...,r-1 from a branch, 5 for each distance 0,...,r-1 from a leaf, and n-(14r-6) ordinary path roots.

**Paired induced motifs:** For a connected induced motif F on s<=k vertices, every copy containing root v lies in its radius-(s-1) ball. Thus a_F(G,v), the number of copies containing v, depends only on the rooted ball. The identity s*i_F(G)=sum_v a_F(G,v) gives equal global counts, and i_F(G-v)=i_F(G)-a_F(G,v) gives equal *paired* connected-motif counts. To recover disconnected motifs F=C_1+...+C_j, expand the product of induced component counts, product_i i_{C_i}(H). The vertex-disjoint, cross-edge-free tuples contribute a positive fixed multiple of i_F(H). All other tuples induce a graph of smaller order or fewer connected components, so induction on order and component count determines every disconnected induced count. This reduction is already present in [the prior M078 local-motif note](M078_TREE_LOCAL_MOTIFS.md); it is not claimed new here.

For k>=3, the radius-r ball also determines the root's degree and all its neighbors' degrees. The global degree multiset is the same in both trees. Deleting v removes its degree and decrements all neighbor degrees, so the card degree sequence is determined by this local information. Hence motif and degree coordinates match **jointly** by rooted-ball type.

## New nonlocal step: card diameters

Each spur leaf lies at distance h+b <= 2h-1 <= A from o. Its distance to the main leaf in its own arm is b+(A-h) <= A-1. The three original main-arm leaves are pairwise distance 2A apart, and no other pair is farther. Thus the original diameter is exactly 2A.

Deleting any v != o leaves **two entire length-A main arms** attached to o, providing a path of length 2A in one card component. Deleting vertices cannot increase component diameters, so dmax(T-v)=2A.

Deleting o leaves three components, each containing a main-arm path of length A-1. For a component with a spur of length b, the other potentially longest paths have lengths b+(A-h)<=A-1 and b+(h-1)<=2h-2<=A-1, since b<=h-1 and A>=2h-1. Therefore dmax(T-o)=A-1.

The diameter coordinate is independent of the spur redistribution. Pair center with center (they have the same rooted-ball type and degree-card profile), and all other roots by their rooted-ball type. Their diameter is always 2A. This establishes equality of the **full paired** D_k statistic for all k,n in scope.

## Exact reproduction and adversarial tests

Run from repository root:

- python3 scripts/m078_card_diameter.py --check --json
- python3 -m unittest discover -s tests -p 'test_m078_card_diameter.py' -v
- c++ -std=c++17 -O3 scripts/m078_card_diameter_direct.cpp -o /tmp/m078_cd && /tmp/m078_cd

The Python implementation builds literal adjacency sets, verifies tree order and degree histogram, canonicalizes rooted radius-r balls, computes component diameters by two BFS sweeps, and counts every induced unlabeled motif through order four by enumerating subsets of the **original** graph. It obtains card counts via global-minus-incident identities. The separate C++17 implementation constructs the graphs independently and **enumerates motifs separately in each deleted card**, using a different adjacency representation and all permutations of each small motif. Both compare a joint vector containing motifs, degree sequence and card diameter.

| k | n | Python joint motif check | C++ literal-card check | dmax histogram |
|---|---|---|---|---|
| 3 | 48 | equal | equal | 12:1, 26:47 |
| 3 | 49 | equal | equal | 12:1, 26:48 |
| 3 | 50 | equal | equal | 12:1, 26:49 |
| 3 | 51 | equal | equal | 13:1, 28:50 |
| 4 | 64 | equal | equal | 16:1, 34:63 |
| 5 | 80 | rooted-ball and diameter only | not enumerated | 20:1, 42:79 |

Ten dedicated tests check all residue classes, paired motifs, every card diameter, malformed inputs, a false added edge, and a moved spur leaf. The latter shortens one spur below L and produces **unequal** rooted balls and unequal literal paired-card motifs. Optional same-author NetworkX graph-isomorphism checks reject isomorphism at (3,48),(3,49),(3,50),(4,64),(5,80). These algorithmic paths were controlled by the same author: **not independent specialist review**. The all-orders assertion rests on the proof, not the finite enumeration.

## Failed avenue and literature boundary

**Failed stronger extrapolation:** The earlier three-legged spider pair S(3,3,5) and S(3,4,4) is locally indistinguishable for k=3 in the repository's prior work, but their card dmax histograms are **{4:1,6:4,7:1,8:6}** and **{3:1,7:8,8:3}**, respectively. So merely adding card diameter to that earlier construction is false. The new construction introduces three fixed, diameter-dominating arms and redistributes two remote spurs.

Primary and adjacent sources: Kelly, *A congruence theorem for trees* (1957), [DOI](https://doi.org/10.2140/pjm.1957.7.961), reconstructs trees from **full** decks. Spinoza–West, *Reconstruction from the deck of ℓ-vertex induced subgraphs* (2018 online / 2019 print), [DOI](https://doi.org/10.1002/jgt.22409), and Groenland–Johnston–Scott–Tan, *Reconstruction from smaller cards* ([arXiv:2103.13359](https://arxiv.org/abs/2103.13359)), study larger-card decks. Hartman–Pokorná–Trlifaj, *Reconstructing graphs and their connectivity using graphlets* ([arXiv:2508.19189](https://arxiv.org/abs/2508.19189), 2025), studies graphlet-degree reconstruction. The prior [M078 local-motif result](M078_TREE_LOCAL_MOTIFS.md), claim #267 / PR #268, supplies the local connected/disconnected reduction but **does not preserve card diameter**. A targeted literature search did not locate this exact joint-card statement, but this is **not evidence of historical novelty**; long-path local indistinguishability is a familiar technique.

**Boundaries:** The diameter statistic is the **maximum component diameter**, not the multiset of *all* component diameters (which can expose spur lengths). The theorem is restricted to simple undirected subcubic trees, k>=3, n>=16k, and motifs of order at most k. It neither improves global reconstruction bounds nor addresses complete decks, and no minimality of 16k is claimed. No solved status, coverage allocation, benchmark, or independently accepted outcome is changed.

**Next falsifiers:** (1) Independent mathematical audit of the distance boundary 2r-1, disconnected-motif induction, and center-card diameter inequalities; (2) independently authored full k=5 motif enumerator or formalized rooted-ball lemma; (3) test richer component-size-plus-diameter card statistics, expected to distinguish this construction; (4) systematic historical priority search in tree reconstruction and graphlet literature; (5) seek a smaller-order subcubic witness. No change to the separate Project 100 PR Landing task or cadence.
