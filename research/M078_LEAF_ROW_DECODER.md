# M078: executable six-leaf distance-row inversion and falsifier

- **Claim:** [#375](https://github.com/Svyable/100/issues/375), `X-M078-FOUR-HUB-LEAF-PROFILES-v1`
- **Status:** author-derived elementary restricted inverse lemma and **author-controlled exact software**; no historical novelty, independent review, complete four-hub reconstruction or graph reconstruction claimed.
- **Date:** 2026-11-17 UTC
- **Target:** six leaves in an unrooted subcubic tree with exactly four degree-three vertices (the remaining vertices, if any, are degree two). Their four-hub skeleton is a 3-edge star or a 3-edge path. The observed statistic is the multiset of the six **leaf-to-leaf** distance multisets, each of length five. This is *not* a leaf-to-all-vertices profile.

## Useful delivered capability

`python3 scripts/m078_leaf_rows.py --example star` or `--example path` prints a complete, machine-readable example analysis.

For a third-party proposed witness, save the six five-integer rows as JSON, then run:

```bash
python3 scripts/m078_leaf_rows.py --rows-json rows.json --max-nodes 1000000
python3 -m unittest discover -s tests -p 'test_m078_leaf_rows.py' -v
```

This searches every symmetric positive-integer six-point distance matrix compatible with the specified unlabeled row multisets, up to the reported recursion-state cap. It uses forced singleton-pair assignments and degree-one peeling before backtracking, plus partial triangle/quartet filters. For each possible four-hub tree metric it constructs a **separate weighted graph certificate** with explicit core-edge and pendant-edge lengths, attachments and a full reconstructed leaf-distance matrix. A standalone checker independently re-evaluates all 15 distances from the proposed weighted tree. Candidate cross-topology collisions require *both* certificates to have positive **integer** edge lengths (one subdivision per unit edge).

The JSON report contains `complete`. If this is `false`, the result is `INCONCLUSIVE` regardless of the candidates found. A `CROSS_TOPOLOGY_COLLISION` label is only a **machine-generated falsifier candidate** that needs independent replay and specialist scrutiny. A complete no-collision report covers *one finite input signature only*. It is not an unbounded theorem.

The script is standard-library Python, has no random seeds or hidden network dependencies in its exact search path, and returns exit code 2 for cap exhaustion.

## Two mathematical reductions, with proof

**Lemma 1 (singleton-edge inversion and peeling).** Consider any symmetric matrix with zero diagonal and an unlabeled multiset of its off-diagonal row multisets. A distance value occurring on exactly one unordered pair occurs in precisely two row instances and forces that pair's matrix entry. After these singleton entries are placed, any vertex of degree one in the remaining unknown-pair graph has exactly one unmatched row value; it forces its incident pair. Repeating is sound for every compatible symmetric matrix. If this process eliminates every unknown edge, the matrix is uniquely reconstructed up to relabeling. In particular, this holds if there is at most one repeated distance value, and more generally whenever the initial residual graph is a forest. **Proof:** singleton endpoints are the unique rows containing the value; a vertex with one remaining edge has exactly one remaining row occurrence. Induct. QED.

An alternative symmetric completion must therefore have (a) at least two distinct repeated distance values and (b) a nonempty 2-core of the remaining unknown-edge graph. This is an **all-orders necessary condition**, not a four-hub uniqueness proof. A red/blue switch on an alternating closed trail can preserve row color multiplicities; a simple even cycle is **not** necessary because a bowtie formed of two triangles admits a balanced switch.

**Lemma 2 (exact complete-matrix tree certificate).** For any positive weighted binary six-leaf tree with its labeled leaf-distance matrix \(D\), each pendant length is
\[
\lambda_i=\tfrac12\min_{j,k\ne i,\ j\ne k}(D_{ij}+D_{ik}-D_{jk}).
\]
Indeed, for an attachment hub \(h_i\), the expression equals \(\lambda_i\) plus the overlap length of the \(h_i\)-to-\(j\) and \(h_i\)-to-\(k\) branches; choosing \(j,k\) in the other two components incident to \(h_i\) gives zero overlap. Therefore \(H_{ij}=D_{ij}-\lambda_i-\lambda_j\) equals the distance between the attachment hubs for \(i\ne j\). For strictly positive hub separations, \(H_{ij}=0\) exactly when leaves \(i,j\) form a cherry.

For a four-hub star, three cherry pairs partition the six leaves. If the inter-cherry hub distances are \(u,v,w\), the three spokes are \((u+v-w)/2,(u+w-v)/2,(v+w-u)/2\). For a four-hub path, two cherry pairs are the endpoint hubs and the remaining two singleton leaves attach to its internal hubs. The unique path order and three positive core lengths are recovered from their hub distances. The candidate is **accepted only after reconstructing every entry of \(D\) from the resulting explicit tree**, so arbitrary non-additive or nonbinary inputs cannot pass. These formulas are standard tree-metric consequences of Buneman's four-point/additive tree theory, *not* presented as novel findings.

**Completeness boundary:** the row backtracker considers every common remaining positive value on each unassigned pair; peeling only fixes mandatory assignments; pruning rejects only an exposed triangle inequality or exposed quartet four-point violation. Thus every compatible positive binary six-leaf integer tree is represented, provided `complete=true`. This does not prove that row-multisets always determine the topology; it only makes a proposed finite counterexample independently replayable.

## Tests, negative controls and limitations

Run `python3 -m unittest discover -s tests -p 'test_m078_leaf_rows.py' -v`. The six-test module includes:

1. **Exhaustive bounded input box:** both topologies and all nine edge lengths in \(\{1,2\}\): 1,024 parameter tuples. Every generated signature was completely searched (no cap hit); none produced an opposite-topology tree metric. This is an overlapping, *known-bounded* type of check and not novelty or a new general theorem.
2. **Two independent tree interpretations:** the constructive pendant-limb/cherry reconstruction agrees with a separately written all-quartets and strict split-count classifier on every bounded test matrix.
3. **Tied-distance and leaf-relabeling controls:** uniform edge lengths, mixed lengths and 40 seeded row/column permutations.
4. **Adversarial false positives:** two nonisomorphic six-point **ordinary metrics** share exactly the same row multiset under a red/blue alternating 4-cycle switch; both are rejected as non-tree-metrics. Explicitly, assign 100,101,100,101 around the cycle 0–1–2–3–0 and unique values 102–112 to other pairs, then switch cycle colors. All distances lie between 100 and 112, guaranteeing triangle inequalities. This does not imply any star/path collision.
5. **Mutants:** change one pendant length, one attachment, or one core edge in a certificate; the independent certificate checker rejects every mutant. Invalid distance counts and a one-state cap are rejected or returned as **inconclusive**, never as a proof of impossibility.

A separate fixed-seed pilot of **10,000** 9-parameter random source trees (alternating star/path, lengths each uniform integer 1–13, seed 20261117) had zero cross-topology candidates and no cap hits; the largest backtracking tree had 41 visited states. This is **random, author-controlled evidence**, not exhaustive support for the universal claim.

**Failed avenue:** A prior decoder could select values with zero residual multiplicity, creating a fake collision. The corrected solver checks *positive counts at both endpoints* on every placement; the new verifier reconstructs an explicit weighted tree from every accepted matrix. Another false stronger statement—that all ambiguity requires an even **simple** cycle—fails on balanced alternating closed trails in a bowtie.

**Source context / priority:** [Buneman (1971)](https://www.research.ed.ac.uk/en/publications/the-recovery-of-trees-from-measures-of-dissimilarity/) is the classical labeled additive metric inverse theorem; [Boutin–Kemper (2004)](https://doi.org/10.1016/S0196-8858(03)00101-5) studies reconstruction from the weaker *global* multiset of all pairwise distances; [Huber–Steel (2014)](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v21i2p15) studies reconstructing labeled phylogenetic trees from sufficiently informative associated leaf distances. These sources do **not** settle priority for the exact row-instance peeling lemma, which looks elementary and likely has antecedents. A specialist prior-art and proof review remains necessary.

**Next major falsifier:** construct a **positive-integer** star/path pair with exactly equal six leaf-distance row multisets but different hub topology; provide both edge-length lists and expanded-graph shortest-path replay. The competing proof target is a symbolic obstruction to all color-balanced residual switches compatible with four-point additivity, not another unrestricted brute-force parameter expansion.

**Commercialization boundary:** no new general reconstruction algorithm, customer savings or defensible operational advantage has been independently validated. No math-to-market handoff, IP claim, or buyer outreach is justified. The scope is **not** the full graph reconstruction conjecture; do not touch `data/solved.json`, benchmark trial ledgers, evidence states, PR-landing automations or coverage counts. This bounded code-only artifact seeks reproducibility, not a theorem claim.
