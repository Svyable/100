# M079 — sharp 2/5 balance candidate for width-five chain-plus-five antichain posets

**Claim:** [#254](https://github.com/Svyable/100/issues/254), work ID X-M079-CHAIN5-SHARP. **Scope SHA-256:** c060c40e6fc3e7a1dd32415a4fa29b8a30664fe94d8fcc400db8447808d271de, of the literal UTF-8 string: X-M079-CHAIN5-SHARP|For every finite poset consisting of a chain and five pairwise incomparable outsiders, width exactly five, each outsider incomparable with at least one chain vertex, delta(P)>=2/5.

**Evidence:** author-derived all-orders **restricted theorem candidate**, not independently reviewed or historically established as novel. The existing [chain-plus-five result](M079_CHAIN_PLUS_FIVE.md) gives only 3/8 and a 2/5 witness; the **2/5 lower bound** is new to this project. This does not settle the unrestricted one-third–two-thirds conjecture or arbitrary width-five posets.

## Precise statement and sharpness

Let P consist of a designated finite chain c1<...<cm and five additional pairwise incomparable elements x0,...,x4. Assume width(P)=5 and every outsider is incomparable with at least one chain vertex. For a uniform random linear extension L, define delta(P) as the maximum over distinct u,v of min(Pr_L(u before v),Pr_L(v before u)).

**Candidate theorem:** delta(P) >= 2/5, sharp. The previously known normalized gap intervals [-4,0],[-1,0],[-1,1],[0,1],[0,4] give 1,405 linear extensions and best smaller-side pair count 562, so delta=562/1405=2/5.

## Structural reduction

Each outsider x has an interval I_x=[a_x,b_x] of allowed insertion gaps in the chain, length L_x>=2. Disjoint intervals force a comparison between outsiders via the chain, contradicting their incomparability. Integer interval Helly gives a common gap. If two consecutive gaps were common, the intervening chain vertex would be incomparable with all five outsiders, contradicting width exactly five. Translate the unique common gap to 0: max a_i=min b_i=0, a_i<=0<=b_i, L_i>=2. Conversely these constraints construct precisely the class up to deterministic chain padding. Sorting the five intervals removes only outsider relabeling. Two identical intervals yield an automorphism exchanging outsiders, hence an exactly 1/2-balanced pair.

## New all-orders profile-sensitive atom lemma

For a chain plus k>=2 pairwise incomparable outsiders, all with allowed interval length >=2, fix outsider x with L=|I_x|. Put S_x=sum over y!=x of (k-1)/(L_y+k-2). For every allowed gap g of x,

    Pr_P(x in gap g) <= (1+S_x)/(L+S_x).

**Proof.** Let B be the number of extensions Q of P-x. Write p_y(g)=Pr_Q(y in gap g) and q_y=Pr_Q(y in I_x). Reinserting x into a fixed Q at gap g gives 1+t_g(Q) positions, where t_g is the number of other outsiders occupying g. Consequently the exact insertion identities are

    E(P)/B = L + sum_y q_y,
    Pr_P(x in g) = (1+sum_y p_y(g))/(L+sum_y q_y).

Because g is in I_x, q_y>=p_y(g). The earlier elementary gap-atom bound, applied to P-x with k-1 outsiders, gives p_y(g)<=(k-1)/(L_y+k-2). With s=sum p_y(g)<=S_x and L>=2, monotonicity of (1+s)/(L+s) proves the claim. The argument does **not** assume the induced Q distribution after deleting x is uniform; the insertion identities correctly sum over Q.

For k=5, S_x=sum_y 4/(L_y+3). If L>=5+4S_x, every x-gap atom is <=1/5. The first cumulative gap mass reaching 2/5 is <=3/5, and occurs before the last gap (whose mass is <=1/5). Thus x and an actual chain vertex are 2/5-balanced. This is a profile-sensitive strengthening of the previous coarse 5/(L+4) bound.

## Reduction to 3,652,287 exact finite cases

- **Length >=18:** S_x<=4*(4/5)=16/5, and 5+4S_x<=17.8, so the analytic criterion applies.
- **Length 17:** if at least three other intervals have length two, two coincide (only [-1,0] and [0,1] are possible), giving a 1/2 automorphism pair. Otherwise at most two have length two and two have length >=3, so S_x<=2*(4/5)+2*(2/3)=44/15<3=(17-5)/4. Again the analytic criterion applies.
- **Length 16:** after excluding duplicates, at most two other intervals have length two. The analytic threshold is S_x<=11/4. If another interval has length >=6, S_x<=4/5+4/5+2/3+4/9<11/4. Among remaining length profiles, monotonicity of 4/(L_y+3) leaves exactly (2,2,3,3), (2,2,3,4), (2,2,3,5), (2,3,3,3). Their distinct normalized interval counts are respectively 48, 192, 240, 32: 16 placements of the length-16 interval, and 2/3/4/5 possible placements of each short length, with the unique-common-gap condition automatically satisfied. Total **512**. The C++ sequential and factorial-block DPs agree on all 512; independently implemented Python factorial-block and literal-poset ideal DPs also agree on all 512. Minimum balance is **227/500 >2/5**, attained at [-10,5],[-1,0],[-1,1],[-1,2],[0,1] (E=3500, best=1589).
- **All lengths <=15:** 119 interval types contain zero. The number of sorted five-multisets with at least one interval starting at zero and one ending at zero is, independently by inclusion-exclusion, C(123,5)-2*C(109,5)+C(95,5)=**40,355,371**. The duplicate-interval or analytic profile criterion discharges **36,703,596**. Two independently formulated exact integer recurrences (sequential chain-prefix/outsider-mask and factorial gap-block) check **3,651,775** residuals. No case has 5*best<2*E; the minimum residual balance is **562/1405=2/5**.

Thus the new exact finite core is **3,651,775+512=3,652,287**, not a claim to 40 million independent theorems or coverage slots. The older [M079_CHAIN_PLUS_FIVE.md](M079_CHAIN_PLUS_FIVE.md) already independently implements a full 40,355,371-case two-recurrence census for the length-15 base, obtaining minimum 2/5. Its checker is additional author-side corroboration, not independent human review.

## Reproduction, controls and provenance

Run from the repository root (Python 3.12+, C++17):

    python3 scripts/m079_chain5_sharp.py --check --json
    python3 scripts/m079_chain5_sharp.py --smoke --json
    python3 -m unittest discover -s tests -p 'test_m079_chain5_sharp.py' -v
    python3 scripts/m079_chain5_kernel.py --check --json  # older full base census

**Author-side local outputs, 2026-11-02 UTC:** 40,355,371 base multisets, 36,703,596 symbolically discharged, 3,651,775 exact base residuals, 512 length-16 boundary residuals, zero falsifiers, base minimum 562/1405, boundary minimum 1589/3500. The local sequential-only implementation produced deterministic FNV-64 transcript 4638243d10a8ccff; the committed checker also compares the full per-pair and per-gap vectors from its two DPs. The transcript is a drift detector, not a cryptographic mathematical proof. Seven adversarial tests passed locally against equivalent code, including a 226,135-case smoke, all 512 boundary tuples checked by two Python representations, seeded three-way comparisons, relabeling, order duality, translation, invalid width/interval controls and a wrong-count negative control. Full repository regeneration, repository-wide tests and exact-head CI remain outstanding; do not merge without those gates.

The integer maximum is safe: with at most 28 chain vertices in the length-15 residual and five outsiders, E(P)<(m+5)!/m!<2^63. All comparisons use integer cross-products; the symbolic cutoff uses exact products of small denominators. The checker counts all outsider–outsider and outsider–chain pairs, not just a chosen pair. The FNV digest is not independent acceptance. **No external specialist has reviewed the mathematical proof or established historical novelty.**

## Literature and boundary

- [Brightwell–Wright (1992), 5-thin posets](https://doi.org/10.1137/0405037) proves a 1/3 result under bounded incomparability degree; this class has outsiders incomparable with arbitrarily many chain vertices.
- [Olson–Sagan (2018)](https://arxiv.org/abs/1706.04985) proves 1/3 for certain families, including some dimension-two subcases, but the inspected source did not identify the present exact 2/5 fixed-width class.
- [Aires–Chan–Pak–Panova (September 25, revised October 30, 2026)](https://arxiv.org/abs/2609.30888) gives a microscopic universal improvement over the Brightwell–Felsner–Trotter bound, not this quantitative fixed-width statement.
- The prior [3/8 chain-plus-five candidate](M079_CHAIN_PLUS_FIVE.md) has the sharp 2/5 example but does not prove the 2/5 lower bound.

**Historical novelty is not established by a targeted source search.** Older near-chain, interval-order, fixed-width and linear-extension balance literature requires specialist audit. No global 1/3–2/3 proof or solved-status change is claimed.

## Failed avenues, assumptions and next falsifiers

The old 5/(L+4) atom estimate would require L>=21 for 2/5, leaving **427,920,736** finite multisets. The new profile inequality plus duplicate symmetry cuts that to a small exact core. A seeded million-case local search around the known witness found no value below 2/5, but is not used as proof. The naive product of interval lengths gives 300 instead of the witness's 1405 extensions because it ignores factorial same-gap outsider orderings.

Assumptions: exactly five outsiders, pairwise incomparable, width exactly five, every outsider incomparable with at least one chain vertex, finite P, and uniform linear-extension distribution. The statement does not apply to arbitrary width-five posets, outsider comparabilities or six outsiders.

Next falsifiers: an omitted interval type or length-16 profile, a mistake in the insertion reweighting, an exact base/boundary counterexample, an algorithm disagreement, integer overflow, or a primary source with an earlier stronger theorem. Obtain independent specialist mathematical and historical-novelty review before recording acceptance. No evidence-state, solved, coverage, benchmark or Project 100 PR Landing automation/cadence change was made.

## Additional independent-path computational audit (2026-11-02 UTC)

After the profile-pruned proof candidate was prepared, an **entirely unpruned** separate C++ enumeration of all interval multisets of lengths 2 through 17 completed. It checked **112,875,904** normalized tuples (independent inclusion-exclusion count), with **zero** cases below 2/5, a **single** equality tuple [-4,0],[-1,0],[-1,1],[0,1],[0,4], and minimum 562/1405. Runtime was 889.44 seconds, deterministic unpruned FNV-64 digest `64d89d8cb51a72da`. This audit does **not** use the symbolic profile cutoff or the 512-case profile classification, so it directly challenges completeness of those reductions; it does reuse a sequential-gap DP formulation and is not a new human proof review.

A separately implemented **factorial-block C++ DP** also agreed with the sequential DP on every one of the **3,651,775** exact base residuals and **512** length-16 cases in a local dual run (73.89 seconds; same pruned FNV-64 `4638243d10a8ccff`). Two independent Python representations agreed on the 512 boundary cases. These are independent **algorithmic representations** under the same author, not independent specialist acceptance. The committed exact-head checkout, full repository tests, regeneration and CI remain outstanding.
