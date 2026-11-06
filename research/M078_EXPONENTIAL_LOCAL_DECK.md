# M078: exponential fibers of the joint bounded-card fingerprint

**Claim:** https://github.com/Svyable/100/issues/284
**Work item:** X-M078-EXPONENTIAL-LOCAL-DECK
**Scope SHA-256:** e96604c33b3876d604f8de1a92089f91573b857fb7a6dfebe987e84ac9f4a7ab
**Date:** 2026-11-02 (America/Chicago)

**Evidence classification:** Author-derived unconditional restricted proof candidate. No open conjecture, numerical extrapolation, or computational-completeness assumption is used. Independent mathematical review and historical novelty remain unestablished. This strengthens the earlier paired motif/card obstruction in M078_TREE_LOCAL_MOTIFS.md quantitatively, and strengthens the statistic by pairing degree and motif data on each individual card. It does **not** refute reconstruction from the complete cards.

## Exact theorem

For a finite graph X, i_F(X) is the number of vertex subsets inducing an unlabeled graph F (including disconnected F). Let deg(X) denote its sorted degree sequence. Define the **joint** fingerprint

\[
\Phi_k(T)=\operatorname{multi}_{v\in V(T)}
  \left((i_F(T-v))_{1\le |V(F)|\le k},\,\deg(T-v)\right).
\]

The tuple stays paired per deleted vertex before forming the multiset.

**Theorem.** Fix any integers k ≥ 3, m ≥ 4, s ≥ 0. Set L=2k−3 and n=m+(m+2)L+s. There exist at least

\[
\boxed{\frac18\binom{s+m+1}{m+1}}
\]

pairwise nonisomorphic n-vertex trees with maximum degree three, all with exactly the same joint fingerprint \(\Phi_k\). The fractional lower bound can of course be rounded upward.

**Every-order corollary.** For all k ≥ 3 and n ≥ 12k−10, put

\[
m=\left\lfloor\frac{n-2(2k-3)}{2k-1}\right\rfloor.
\]

At least \(4^m/(8(m+1))\) pairwise nonisomorphic subcubic n-vertex trees have the same joint fingerprint. Thus, for each fixed k, one fingerprint has exponentially many nonisomorphic preimages at **every sufficiently large order**, not merely along a subsequence. For varying k with n/k growing, the lower bound has the form exp(Ω(n/k)).

## Proof

### 1. Explicit construction and number of nonisomorphic trees

Take a fixed path of m vertices b_1,...,b_m. At each endpoint attach two pendant paths; at each internal path vertex attach one. All b_i now have degree three. There are m+2 pendant paths. Give their edge lengths L+x_1,...,L+x_(m+2), where the x_j are nonnegative integers with sum s. The pendant paths have no additional common vertices. The resulting graph is a tree of maximum degree three, with m+(m+2)L+s vertices.

The number of ordered choices of extras x is the stars-and-bars number C(s+m+1,m+1). The vertices of degree three induce precisely the original m-vertex path. Any graph isomorphism must therefore restrict to either the identity or a reversal of this branch path. Once its action is fixed, the length at every internal branch vertex is recovered uniquely from the graph; at either endpoint the two pendant paths may only be swapped. Consequently at most 2·2·2=8 ordered choices produce one isomorphism class. At least C(s+m+1,m+1)/8 nonisomorphic trees occur.

### 2. Rooted-ball histogram is independent of the choices

Write r=k−1≥2 and note L=2r−1. We examine the rooted radius-r induced ball at every vertex. Each branch vertex has a fixed radius-r rooted ball, because all pendant leaves are at distance at least 2r−1≥r, and a leaf appearing precisely at the radius boundary reveals nothing beyond that boundary.

For each pendant path of length a≥2r−1, index its non-branch vertices by distance d=1,...,a from the attachment branch; write e=a−d for their distance from the terminal leaf. There are exactly r−1 vertices with d≤r−1: their balls see the attachment branch, but no terminal leaf at distance less than r; each ball depends only on the branch position and d. There are exactly r vertices with e≤r−1: their balls see the terminal leaf, but not the attachment branch at distance less than r; each depends only on e. These two sets are disjoint. At the remaining a−(2r−1) positions both d and e are at least r. Each such ball is the same rooted path of 2r edges with the root in its center. A branch or leaf lying exactly at distance r looks identical to the end of an untruncated path within the induced ball.

The fixed branch-root balls and the fixed near-branch and near-leaf ball counts are independent of x. The number of middle-path balls across all pendant paths is

\[
\sum_j ((L+x_j)-(2r-1))=\sum_j x_j=s.
\]

Hence the entire multiset of rooted radius-r balls depends only on k,m,s, and not on their distribution among the paths.

### 3. Local balls determine the paired card statistics

For every connected induced motif F with t≤k vertices, let a_F(T,v) count its copies containing v. A copy containing v lies entirely within its rooted radius-(t−1) ball. Therefore a_F(T,v) is determined by the rooted radius-r ball, as r=k−1. The identities

\[
t\,i_F(T)=\sum_{v\in V(T)}a_F(T,v),
\qquad i_F(T-v)=i_F(T)-a_F(T,v)
\]

show that the connected induced motif counts **in the card** T−v are functions of the rooted-ball type and the common global ball histogram.

Disconnected motifs require no further global information. If F=C_1 ⊔ ... ⊔ C_h is a disjoint union of connected graphs, expand the product of induced counts \( \prod_j i_{C_j}(X) \). A selection of pairwise disjoint induced copies with no cross-edge contributes to i_F(X), with positive coefficient given by factorials of repeated component multiplicities. Every other selection has overlapping copies or a cross-edge, and hence its union induces a graph on at most |F| vertices with fewer than h connected components. Induction on h recovers i_F(X) from the connected induced motif counts of orders at most |F|. Apply this separately to every card X=T−v. Thus **every** motif count through order k, including disconnected ones, is a function of the rooted ball at v and the common ball histogram.

Because r≥2, the rooted radius-r ball also determines the degree of its root and the original degrees of its immediate neighbors. The common ball histogram determines the global degree multiset of T. Removing v deletes its degree and subtracts one from the degree of each neighbor; all other degrees remain fixed. Hence deg(T−v) is a function of the **same rooted ball**. The motif vector and card degree sequence therefore remain paired under a single map from rooted-ball types to joint card data. The rooted-ball histograms agree across the family, so the joint fingerprints \(\Phi_k\) agree. This completes the unconditional proof.

### 4. Lower bound at every large order

Fix k and n≥6L+8=12k−10. Put \(m=\lfloor(n-2L)/(L+2)\rfloor\), so m≥4, and \(s=n-2L-(L+1)m\). By the floor inequality s≥m. The stars-and-bars count is increasing in s, so the theorem guarantees at least C(2m+1,m+1)/8 nonisomorphic trees. The central coefficient in row 2m+1 is at least the average of its 2m+2 coefficients:

\[
\binom{2m+1}{m+1}\ge \frac{2^{2m+1}}{2m+2}=\frac{4^m}{m+1}.
\]

This proves the corollary without any asymptotic assumption.

## Reproducibility, falsifiers, and review limits

Run these author-side exact checks:

    python3 scripts/m078_exponential_fibers.py --check
    python3 scripts/m078_exponential_fibers.py --check --deep
    python3 -m unittest discover -s tests -p 'test_m078_exponential_fibers.py' -v

The code separately constructs literal adjacency sets, hashes rooted balls by recursively canonicalizing a BFS-limited tree, and obtains an isomorphism-class invariant by recovering the degree-three spine and pendant lengths. The independent card-check path *literally enumerates* every induced subset of each vertex-deleted card and retains the pair (all motif counts, degree sequence). For sizes ≤4, an exhaustive comparison of all 64 labeled four-vertex graphs checks that sorted degree sequence distinguishes all 11 unlabeled types, including disconnected ones.

Checked examples: k=3,m=6,s=2 (6 binary placements, 4 isomorphism classes, direct joint card census on 32 vertices); k=4,m=5,s=1 (3 binary placements, 2 isomorphism classes, direct joint census through four-vertex motifs on 41 vertices); k=3,m=4,s=4 (126 weak compositions on 26 vertices, 31 distinct graph types by spine recovery, also independently compared by NetworkX graph-isomorphism; all rooted-ball histograms match); and endpoint-padding variants with direct card tests. Ten targeted adversarial tests pass. The 126-instance case does *not* assert a direct motif census for every assignment.

Potential falsifiers include accidentally observing a branch and a leaf simultaneously when shortening the minimum legs below 2k−3; failing to keep motif and degree data paired **per card**; using a rooted radius below k−1; or mistaking full vertex-deleted cards for the bounded summaries here. The construction uses no computational step to justify its all-orders theorem. These tests are author-controlled checks, **not independent peer review or machine-kernel certification**.

Relevant existing work: Kelly's 1957 tree reconstruction theorem (https://doi.org/10.2140/pjm.1957.7.961), Groenland–Johnston–Scott–Tan, *Reconstruction from smaller cards* (https://doi.org/10.1007/s11856-025-2858-3), and Spinoza–West, *Reconstruction from k-decks for graphs with maximum degree 2* (https://arxiv.org/abs/1609.00284). Their deck statistics are distinct from the joint fingerprint studied here. The central locality idea was already developed in this repository in M078_TREE_LOCAL_MOTIFS.md. Historical novelty of this quantitative extension has not been established. No general reconstruction result, solved status, independent acceptance, or coverage promotion follows from this work.
