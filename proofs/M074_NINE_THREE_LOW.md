# M074 — sharp three-low-vertex theorem for nine-point triangle-free orientations

**Research candidate, 2026-11-02 UTC.** Claim [#234](https://github.com/Svyable/100/issues/234), work ID `X-M074-9LOCAL-THREE`, scope SHA-256 `2779707ac1be135eef987dbd81547a294b6528332b42d0f70da671a16bde4d71`. This is an author-derived, **exactly certificate-checked restricted theorem candidate**. The proof has been independently *mechanically replayed* with the separate `drat-trim` / `lrat-check` tools, but has **not** undergone independent specialist review of the mathematical encoding or historical novelty. It does not prove the Caccetta–Häggkvist conjecture or the (27,9) case.

## Exact theorem and sharpness

**Theorem (nine-vertex three-low candidate).** Let `H` be a loopless **oriented** graph on exactly nine vertices (no antiparallel arc pairs), containing no directed cycle of length three. If every vertex has outdegree at least two, then **at least three distinct vertices have outdegree exactly two**. The number three is best possible.

The following adjacency list (outneighbors, vertices 0 through 8) has 24 arcs, no digons or directed triangles, minimum outdegree two, and exactly three outdegree-two vertices. It is also the sharpness witness in the earlier [two-low note](M074_NINE_TWO_LOW.md):

```text
0: 6 7
1: 0 3
2: 1 8
3: 0 6 7
4: 1 5 8
5: 1 2 8
6: 2 4 5
7: 2 4 5
8: 0 1 3
```

The novelty *within this repository* is excluding **exactly two** low vertices, which the previous hand proof explicitly left unresolved. Zero and one low were already excluded by that earlier elementary result; we additionally certify them directly to make this finite proof independent of that earlier proof candidate. No claim of historical first discovery is made.

## Exhaustive symmetry reduction (seven cases)

Write `a(i,j)` for the directed arc `i→j`, with 72 Boolean variables, one for each ordered pair of distinct vertices. Suppose the theorem fails, so the number `t` of outdegree-two vertices is 0, 1 or 2.

- `t=0`: every outdegree is at least three. Delete excess outgoing arcs from one vertex, if necessary, to make its outdegree **exactly three**; deletion cannot create a directed triangle or digon and leaves all other outdegrees unchanged. Relabel this vertex `0` and its outneighbors `1,2,3`. The resulting `zero_low` case is exhaustive.
- `t=1`: relabel the unique outdegree-two vertex `0`, and its two outneighbors `1,2`. Every other vertex has outdegree at least three. This is the `one_low` case.
- `t=2`: relabel the two outdegree-two vertices `0,1` so that `1→0` is absent (possible because a digon is forbidden). If `0→1`, relabel the remaining seven vertices so `N⁺(0)={1,2}`. The two outneighbors of `1` either **include** `2` or **exclude** `2`: representatives `N⁺(1)={2,3}` and `{3,4}`. If `0` and `1` are nonadjacent, relabel so `N⁺(0)={2,3}`. The two outneighbors of `1` overlap `{2,3}` in 2, 1 or 0 vertices: representatives `{2,3}`, `{2,4}`, `{4,5}`. These are **all five** possible cases, not heuristic orbit samples.

The direct CNF has no auxiliary variables. For every `i<j`, the clause `¬a(i,j)∨¬a(j,i)` forbids digons (36 clauses). For every unordered triple `{i,j,k}`, the two cyclic orientations are forbidden by two three-literal clauses (168 clauses). For each vertex with required outdegree at least `d`, every subset of `9−d` of its eight outgoing arc variables has a positive disjunction; these clauses are equivalent to outdegree at least `d`. For each designated outdegree-two vertex, every triple of its eight outgoing arc variables has a negative disjunction, equivalent to outdegree at most two. Finally, unit clauses fix the normalized rows. Thus every model of the CNF is **exactly** a graph of the stated type in that case; conversely every normalized counterexample would yield a CNF model. No unknown SAT-model-to-graph reconstruction is required.

| Case | Fixed outgoing rows | CNF clauses | LRAT added clauses | Result |
|---|---|---:|---:|---|
| `zero_low` | `0:{1,2,3}` | 464 | 4,817 | UNSAT |
| `one_low` | `0:{1,2}` | 500 | 8,755 | UNSAT |
| `edge_overlap` | `0:{1,2}`, `1:{2,3}` | 544 | 713 | UNSAT |
| `edge_disjoint` | `0:{1,2}`, `1:{3,4}` | 544 | 977 | UNSAT |
| `nonedge_overlap2` | `0:{2,3}`, `1:{2,3}` | 544 | 569 | UNSAT |
| `nonedge_overlap1` | `0:{2,3}`, `1:{2,4}` | 544 | 639 | UNSAT |
| `nonedge_overlap0` | `0:{2,3}`, `1:{4,5}` | 544 | 1,124 | UNSAT |

Each UNSAT result has a committed compressed **LRAT proof**, whose clauses are checked against the exactly regenerated DIMACS input by `scripts/ch9_three_low.py`. The checker maintains the live clause database, assumes the negation of each learned clause, replays its ordered unit-propagation hints and requires a contradiction; the final learned clause is empty. All seven trimmed traces use RUP hints (no RAT additions). This is a proof certificate, not merely a solver exit status. Since all seven cases are impossible, every admissible graph has at least three low vertices. The explicit witness shows sharpness. □

## Reproducibility, adversarial controls, and independent replay

**Dependency-free proof replay:**

```sh
python3 -m scripts.ch9_three_low --check --json
python3 -m unittest discover -s tests -p 'test_ch9_three_low.py' -v
python3 -m scripts.ch9_three_low --emit-dimacs edge_overlap > /tmp/ch9_edge_overlap.cnf
```

The seven `.lrat.gz` files are in `data/certificates/m074_nine_three/`, with SHA-256 digests pinned in the checker. The 72-variable direct encoding is also tested against an independently written adjacency-matrix evaluator and exhaustive 256-row degree truth tables. Seven dedicated tests include corrupted LRAT-hint and tautologized-input rejection, literal sharpness replay, and an example with two low vertices that **does contain a directed triangle**. These tests cannot replace human proof review.

**Independent external certificate path:** On a separate machine, compile [Marijn Heule's `drat-trim`](https://github.com/marijnheule/drat-trim) (commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` was used here). Generate the exact CNF via `--emit-dimacs`, decompress the corresponding LRAT file, and run `lrat-check INPUT.cnf PROOF.lrat`. All seven files were checked with this external C checker and accepted. The LRATs were generated with `python-sat 1.9.dev17` / CaDiCaL195, converted from DRAT by `drat-trim -L`, then compressed with gzip level 9, `mtime=0`. The optional generator reproduces all seven compressed certificates **byte-for-byte** (all seven SHA-256 digests match):

```sh
python3 -m scripts.ch9_three_low_generate \
  --output-dir /tmp/ch9_repro --drat-trim /path/to/drat-trim
```

The generator requires optional `python-sat` and the external `drat-trim` executable; the committed proof checker and normal repository tests require neither. The external checker and our Python checker are distinct implementations, but both audit author-selected cases; **they are not independent mathematical or historical-priority review**.

## A conditional new CH(27,9) root consequence

Assume hypothetically an oriented, directed-triangle-free 27-vertex digraph `D` with **all** outdegrees nine, and a vertex `v` of indegree ten. As in the existing [rank-and-girth root argument](M074_ZERO_K_TWO.md), put `A=N⁺(v)` (9 vertices), `B=N⁻(v)` (10 vertices), `C` the seven nonneighbors, and `z=#{b∈B : d⁻_C(b)=0}`. The prior restricted proof candidate gives `z≤2`, while the nine-vertex neighborhood lemma gives minimum outdegree two in `D[A]`. The present theorem supplies **three distinct** `a∈A` with `d⁺_A(a)=2` (previously only two were certified). Each such `a` sends its other seven outgoing arcs to all of `C`, so receives none from `C`; it has at most four incoming arcs from `A`, and at most `z≤2` from `B` (otherwise a directed triangle `a→c→b→a` forms). Including `v→a`,

`d⁻_D(a) ≤ 1+4+0+2 = 7`.

**Conditional consequence:** every indegree-ten root has **at least three distinct outneighbors of ambient indegree at most seven**, assuming the earlier rooted lemmas. Let `h` count indegree-ten vertices, `k` count vertices of indegree at most seven, and `r` count indegree-eight vertices. Degree-sum balance gives `h≥2k+r`, while counting arcs from indegree-ten vertices to the `k` low vertices gives `3h≤7k`. Therefore `3r≤k`. These inequalities are compatible and **do not exclude** the (27,9) case, let alone the unrestricted conjecture.

## Prior art, failed avenues, limitations and next falsifiers

- **Primary historical source:** L. Caccetta and R. Häggkvist, *On minimal digraphs with given girth*, *Congressus Numerantium* **21** (1978), 181–187 (bibliographic confirmation in [Razborov's reference list](https://doi.org/10.1002/jgt.21707)).
- **Published specialist context:** J. Hladký, D. Kráľ and S. Norin, *Counting flags in triangle-free digraphs*, *Combinatorica* **37** (2017), 49–76, [DOI](https://doi.org/10.1007/s00493-015-2662-5); A. Grzesik, *On the Caccetta–Häggkvist Conjecture with a Forbidden Transitive Tournament*, *EJC* **24** (2017), [DOI](https://doi.org/10.37236/5954). Neither cited source was found to state this exact nine-vertex low-degree multiplicity lemma. Absence of a hit is **not** evidence of historical novelty.
- **Repository baseline:** [nine-vertex two-low proof](M074_NINE_TWO_LOW.md) and [eight-vertex rigidity](M074_EIGHT_VERTEX_RIGIDITY.md), both still awaiting external mathematical review; the former explicitly left exactly-two-low existence unresolved. The present direct certificate does **not** rely on either proof to establish the nine-vertex result.
- **Failed elementary route:** Deleting one degree-two vertex and using the existing eight-vertex arc/indegree inequalities reduces the exactly-two-low case to residual `(m,b,m_J)` possibilities `(25,3,20)`, `(25,4,19)`, `(26,4,20)` and `(27,4,21)` (plus the stronger eight-vertex equality rigidity that eliminates the last). These inequalities alone do **not** eliminate the other three; an unproved extrapolation from the earlier two-low argument would be invalid. The seven exact LRAT certificates replace that gap, not an asserted hand proof.
- **Scope and next falsifier:** A nine-vertex oriented directed-triangle-free min-outdegree-two adjacency list with only two degree-two vertices would falsify the theorem; a missing symmetry case, incorrect degree encoding, or rejected LRAT trace would invalidate the certificate. Next priorities are an independently written statement-to-CNF fidelity audit, a shorter elementary proof of the three residual cases, and a specialist prior-art review. No result for 10 or more vertices is implied. No solved/evidence status, coverage allocation, or independent-acceptance record should change.
