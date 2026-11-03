# M075 — Canonical parents can fail; safe augmentation survives

**Status (2026-11-01):** Explicit all-n counterexample to one naive canonical-parent rule, plus a complete parent-orbit augmentation lemma. This is **not a proof of Frankl's conjecture**, and no independent novelty or scope review is yet recorded.

## Definitions

For n ≥ 1 set U = {0,...,n−1}. A union-closed family F of subsets of U has full support when its union is U; every such nonempty family includes U.

For a subset S, m(S) = Σ_{i in S} 2^i. Encode a family by e(F) = Σ_{S in F} 2^{m(S)}. The canonical integer C_n(F) is the minimum e(πF) over every relabeling π in the symmetric group S_n. A family is canonical when e(F) = C_n(F).

For a family with at least two members, define d(F) by removing a member S ≠ U with minimum cardinality, breaking ties by the smaller subset mask m(S). The tempting shortcut “canonical child implies canonical deletion-parent” is **false**.

## Proposition 1 — A counterexample for every n ≥ 3

For n ≥ 3 let F_n = { {0}, {1}, {0,1}, U }. Then F_n is union-closed, full-support and canonical, but d(F_n) is not canonical.

**Proof.** The union of the two singleton members is the doubleton already present; union with U remains U. Every relabeling selects two singleton indices a,b and retains their doubleton and U. The largest variable bit position in e(πF_n) is m({a,b}) = 2^a+2^b, which is minimized uniquely when {a,b}={0,1}. Hence F_n is canonical. Our deletion rule removes {0}. The remaining family is {{1},{0,1},U}; swapping 0 and 1 yields {{0},{0,1},U}, with a strictly smaller encoding. QED.

At n=3, the exact bitmask witness is:

| Object | Subset masks | Encoded family |
|---|---|---:|
| Canonical child | 1,2,3,7 | 142 |
| Chosen deletion-parent | 2,3,7 | 140 |
| Canonical relabeling of parent | 1,3,7 | 138 |

The **all-n** claim has the preceding proof; checking n=3,4,5 is only a finite diagnostic.

## Proposition 1b — Even choosing among all minimum deletions can fail

The previous witness has a *different* minimum-member deletion that
happens to be canonical. A stronger obstruction removes that escape.

For **every n ≥ 4**, define

F*_n = { {1,2}, {0,3}, {0,1,2,3}, U }.

At n=4 the last two members coincide, so this is a three-member family;
at n>4 it is a four-member family. It is union-closed because the
two disjoint doubletons unite to the displayed four-set, which then
unites with U to give U; all other unions are already present.

**Canonicality for every n ≥ 4.** Any relabeling preserves the pair
of disjoint doubletons and their four-element union Q.
The largest non-top subset mask is m(Q), minimized uniquely
as an integer when Q={0,1,2,3} (mask 15). With Q fixed,
the two disjoint doubletons partition Q. Their mask pairs are
{3,12}, {5,10}, and {6,9}; lexicographic comparison of the
high bit positions makes {6,9} the canonical choice.
Thus F*_n is canonical under our exact integer encoding.

**No canonical minimum parent.** The two minimum-cardinality members
have masks 6 and 9. Removing either leaves its partner plus Q and U;
a relabeling inside Q sends the remaining doubleton to {0,1}
(mask 3), which strictly decreases the encoding while fixing Q and U.
Therefore **neither** minimum-member deletion gives a canonical
labeled parent. This proves the all-n assertion. The code
checks the instances n=4 and n=5 independently of this argument.

For n=4, the fully certified example is

F*_4 = { {1,2}, {0,3}, {0,1,2,3} },

with family bitmask 33344 (subset masks 6,9,15).
Removing {1,2} leaves subset masks {9,15}; removing {0,3}
leaves {6,15}. Both parents are noncanonical: a relabeling
makes their surviving doubleton {0,1}, of mask 3.
The canonical parent bitmask is 32776 in either case.

**Proof of n=4 canonicality.** Any relabeling gives two
disjoint doubletons A,B and the full set U. Two disjoint
doubletons require four distinct ground elements. Their subset masks
cannot both be below 9, because doubletons with masks below 9
are the three pairs among {0,1,2}, which intersect. The
least possible larger mask is 9, with complementary
smaller mask 6. Since encoding orders integer bit positions,
{6,9} uniquely minimizes the family encoding. QED.

The exhaustive n=4 orbit test finds **five** canonical
full-support family representatives for which *no*
minimum-cardinality member can be removed leaving a
canonical labeled parent. This is a finite property
of our exact encoding, not a theorem about all possible
orbit-generation conventions.

## Lemma 2 — Minimum-member deletion preserves closure

Let F be full-support and union-closed with at least two members. Choose any minimum-cardinality member S ≠ U. Then F minus {S} remains union-closed and retains U.

**Proof.** If A and B are remaining members whose union equals S, then A,B are subsets of S. Since S had minimum cardinality, both would have to equal S, contradiction. Thus no required union is lost. The top set U remains. QED.

## Theorem 3 — Safe augmentation from parent orbits

Let L_k(n) contain exactly one canonical representative of each S_n-orbit of full-support union-closed families with k members. Begin with L_1(n) = {{U}}.

For each canonical parent P in L_k(n), try all absent subsets S proper in U such that |S| ≤ min{|A| : A in P}. If P union {S} is union-closed, canonicalize it and deduplicate the resulting canonical integers to form L_{k+1}(n).

**Claim.** The process generates exactly one representative of each such orbit at every size, for all finite n.

**Proof.** Soundness follows from the closure test, preservation of U, and canonicalization. For completeness, take any family F with k+1 members, remove a minimum-cardinality member S by Lemma 2, and call the parent P. By induction a canonical representative C_n(P) of the parent orbit was already generated. Choose a ground-set permutation π with π(P)=C_n(P). Then π(F)=C_n(P) union {π(S)} is a valid augmentation; |π(S)| ≤ the size of every remaining parent member because S was minimum in F. Our procedure therefore tries this very subset and canonicalizes the child to C_n(F). Since canonical integers separate orbits, deduplication retains exactly one representative per orbit. Induct on k. QED.

**The key correction:** Do not require the chosen deletion-parent of the *canonicalized child* to be literally canonical. Proposition 1 refutes precisely that extra restriction. This is a standard orbitwise construction strategy, not a claimed new general algorithm.

## Exact finite checks

The implementation is [scripts/frankl_augmentation.py](../scripts/frankl_augmentation.py).

| Ground set n | All full-support orbits | Orbits reached by the specifically flawed strict-parent rule |
|---:|---:|---:|
| 1 | 2 | not tested |
| 2 | 6 | not tested |
| 3 | **28** | **10** |
| 4 | **330** | **32** |

For n=4, the distribution by number of members from 1 to 16 is:

(1, 4, 10, 20, 34, 45, 49, 49, 42, 30, 21, 13, 6, 3, 2, 1).

These counts are known finite mathematics, not new Frankl progress. The second column under naive strict-parent pruning describes **only** the deliberately flawed choice d(C_n(child))=current canonical parent; no claim is made about other canonical-construction-path algorithms.

Reproduce with:

~~~sh
python3 scripts/frankl_augmentation.py --check
python3 -m unittest discover -s tests -p 'test_frankl_augmentation.py' -v
~~~

Independent checks use the existing descending-family generator through n=4, plus an unpruned raw Boolean-family truth table through n=3. Every one of the 4,542 labeled full-support n=4 families is checked for deletion closure. The all-n counterexample is instantiated at n=3,4,5. The orbit generator intentionally caps at n=4 and claims no measured n=5 efficiency.

## Prior art and genuine research boundary

Brendan McKay's [1998 isomorph-free exhaustive generation paper](https://doi.org/10.1006/jagm.1997.0898) already develops canonical construction paths. The [2020 formalization of Faradžev–Read exhaustive generation](https://pmc.ncbi.nlm.nih.gov/articles/PMC7324030/) explicitly treats union-closed families and symmetry-aware generation. We therefore claim **no publication-level novelty** for this generic method or these finite counts.

What remains genuinely open *for our research pipeline* is a new, provably sound, cheaper canonical-parent certificate or structural invariant that prunes large-n search without losing orbits. Any purported speedup needs a fixed-budget benchmark. Any mathematical novelty needs specialist prior-art and independent scope review.

This work does not establish an n=6 census, a minimal-counterexample obstruction, a new abundance bound, or Frankl's universal one-half statement.
