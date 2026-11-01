# M073 — exact two-block graphon sanity check, not a Sidorenko witness

**Research checkpoint, 2026-10-31.** Target: the 35-vertex,
66-edge bipartite incidence pattern from the September 2026
[Sidorenko counterexample manuscript](https://github.com/openai/math/tree/main/preprints/A-counterexample-to-Sidorenkos-conjecture-September-23-2026).
The paper claims the existence of a finite simple host with
\(t(H,G)<t(K_2,G)^{66}\). The repository
[previously reconstructed the 22 triples on 13 points](M071_M073_WITNESSES.md)
from [pinned OpenAI math source commit
`4eaee875`](https://github.com/openai/math/blob/4eaee87548250b2682affda7d05d947c05554bae/lean/ComparatorChallenges/SidorenkoCounterexample.lean).
No explicit host graph or numerical order is available in that frozen source.
This note **does not** claim a finite counterexample, revalidate the
upstream proof, resolve Sidorenko's conjecture, or establish originality.

## Exact predeclared experiment

Fix two measurable vertex classes of **equal mass** \(1/2\) each.
Let the symmetric two-step graphon have weights

\[
W=\frac{1}{2}
\begin{pmatrix}a&b\\b&c\end{pmatrix},
\qquad a,b,c\in\{0,1,2\}.
\]

These are **27** parameter cells, with within-block weights allowed.
They are not 27 two-vertex simple host graphs: within-block diagonal
weights are legal for a graphon and represent a *large* block of vertices.

Writing \(P=\{0,\ldots,12\}\) for pattern points and \(F\) for its
22 listed triples, independently choose a block label for each of the
35 pattern vertices. With \(M=\bigl(\begin{smallmatrix}
a&b\\b&c\end{smallmatrix}\bigr)\), the integer homomorphism numerator is

\[
T=\sum_{x\in\{0,1\}^{13}}
 \prod_{f=\{i,j,k\}\in F}
 \left(\sum_{y\in\{0,1\}}M_{x_i y}M_{x_j y}M_{x_k y}\right).
\]

Thus \(t(H,W)=T/(2^{35}2^{66})\), while
\(t(K_2,W)=(a+2b+c)/8\). The Sidorenko inequality is **exactly**

\[
\boxed{\;2^{97}T\ \ge\ (a+2b+c)^{66}.\;}
\]

There is no floating-point rounding or finite-sampling error.

Two independent algorithms evaluate the left numerator:

1. **Face elimination:** enumerate all \(2^{13}\) assignments to the point
   classes and sum each face class analytically.
2. **Pairwise-factor elimination:** construct all 66 separate incidence-edge
   factors, then eliminate the 35 binary variables by exact dynamic
   programming. This implementation does not use the face-product
   formula as a calculation step.

For tiny bipartite patterns, both agree with brute-force enumeration
of **every** binary assignment to **every** vertex.

## Recorded result and failure boundary

| Exact coarse test | Count |
|---|---:|
| Equal-mass two-block graphons with weights in \(\{0,1/2,1\}\) | 27 |
| Strict violations of the 66-edge inequality | **0** |
| Strictly positive gaps | **24** |
| Equality | **3** |

The equality cells are exactly \((a,b,c)=(0,0,0),(1,1,1),(2,2,2)\):
constant graphons. All the other 24 tested cells have a positive exact
gap. This **only** excludes those 27 proposed graphons as counterexamples
to the paper's *fixed pattern*, not a continuous two-block family,
unequal block masses, three or more blocks, or the paper's random-host
construction. It is a measured *negative result*, not a new restricted
universal theorem.

A deliberately **nonbipartite** K3 control with cross-only weights
\(M=\bigl(\begin{smallmatrix}0&2\\2&0\end{smallmatrix}\bigr)\)
has \(t(K_3,W)=0<(1/2)^3\); the general pairwise-factor evaluator
detects this strict violation. It tests the inequality comparator without
pretending to refute Sidorenko for bipartite graphs. Further tests reject
looped/duplicate edges, a malformed pinned face table, invalid weights,
and an unregistered expansion of the 27-cell trial.

## Reproduce

Run from the repository root:

```sh
python3 scripts/sidorenko_twoblock.py --check
python3 scripts/sidorenko_twoblock.py --json
python3 -m unittest discover -s tests -p 'test_sidorenko_twoblock.py' -v
```

The input is committed `data/reference/sidorenko_faces.json`, which
already records the source revision and its hash. The global verifier
`python3 scripts/verify_claim_witnesses.py --check` independently
checks this frozen table. These density computations do **not** upgrade
`O-M073-01`, which still requires the full finite host \(G\)
with a second independent density recount and independent review.

**Next falsifier:** extract an actual finite host from upstream
`RandomHost.lean` (order, edges, input hash), or find a rational
higher-block/unequal-mass step graphon with an exact strict inequality.
Any such candidate must be independently recounted and compared to the
*precisely same* 35-vertex, 66-edge incidence pattern. Expanding only the
coarse two-class grid would not prove the unrestricted claim.

**Claim scope:** [#99](https://github.com/Svyable/100/issues/99);
related witness obligation [#13](https://github.com/Svyable/100/issues/13).
No change to `data/solved.json`, evidence status, or independent review.
