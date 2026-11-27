# 100 — a compendium of consequential mathematics

**Editorial edition: 2026-11-27.** A durable map of the mathematics that matters: foundational theorems, landmark resolutions and refutations, quantitative frontiers, and open questions. A solved conjecture remains intellectually valuable and retains its permanent ID, history, proof sources and descendants.

## How to read the compendium

- [The 100 research dossiers and their execution ranking](RANKED.md): the existing stable IDs, covering ten fields. The ranking rewards attackability and is not a universal importance ranking.
- [ProofAtlas 500](https://www.proofatlas.ai/open-problems/): an external importance-ranked discovery index, not an authority on truth or a substitute for specialist sources. Its dates and precise statements matter; later papers may supersede its snapshot.
- [The 2026 frontier below](#2026-frontier): significant changes to our existing targets and additional landmark mathematics.
- [Candidate proof and research record](README.md#current-status--strongest-results): what our own contributors have attempted; [YIELD](YIELD.md) reports independent acceptance, not the world's theorem count.
- [Research protocol](docs/RESEARCH_PROTOCOL.md), [portfolio selection](docs/PORTFOLIO_SELECTION.md) and [agent protocol](AGENTS.md): canonical validation, scope, and review rules.

The owner directs this edition to treat the recent external results as true **for editorial and research-planning purposes**. Accordingly the compendium describes their mathematical consequences under that assumption, including resolutions, counterexamples and bounds. The assumption is not a claim that Project 100 independently checked the proofs. The canonical research registry, Solved archive, proof evidence, current top-20 restriction, and PR-landing workflow are unchanged until their existing gates are met.

## Subject index — all 100 permanent research dossiers

This subject index is a dated navigation snapshot of the 100 stable research IDs, not a new ranking or evidence audit. The [generated ranking](RANKED.md) remains authoritative for execution. Within each field the entries retain their relative research rank.

### Algebra

M041 Plane Jacobian conjecture · M042 Dixmier conjecture A1 · M043 Kaplansky idempotent conjecture · M044 Kaplansky direct-finiteness conjecture · M045 Finitistic dimension conjecture · M046 Auslander–Reiten conjecture · M047 Broué abelian defect conjecture · M048 Alperin weight conjecture · M049 Soficity conjecture · M050 Cherlin–Zilber algebraicity conjecture

### Algebraic geometry

M021 Hodge conjecture · M022 Generalized Hodge conjecture · M023 Tate conjecture · M024 Lefschetz standard conjecture · M025 Grothendieck section conjecture · M026 Bombieri–Lang conjecture · M027 Vojta main conjecture · M028 Zilber–Pink conjecture · M029 Mumford–Tate conjecture · M030 Abundance conjecture

### Analysis

M051 3D Euler regularity · M052 Inviscid SQG regularity · M053 Weak cosmic censorship · M054 Nonlinear Kerr stability · M055 Higher-dimensional Kakeya conjecture · M056 Fourier restriction conjecture · M057 Bochner–Riesz conjecture · M058 Kannan–Lovász–Simonovits conjecture · M059 Hilbert invariant subspace problem · M060 Morrey 2x2 conjecture

### Arithmetic

M019 Erdős–Straus conjecture · M011 Schanuel's conjecture · M012 Artin primitive-root conjecture · M013 Leopoldt's conjecture · M014 Hilbert's tenth problem over Q · M015 Inverse Galois problem · M016 Fontaine–Mazur conjecture · M017 Global Langlands functoriality · M018 Infinitely many primes n²+1 · M020 Lehmer's Mahler-measure conjecture

### Combinatorics

M074 Caccetta–Häggkvist conjecture · M075 Frankl union-closed sets conjecture · M076 Erdős–Rado sunflower conjecture · M078 Graph reconstruction conjecture · M079 One-third–two-thirds conjecture · M071 Hadwiger conjecture · M072 Erdős–Hajnal conjecture · M073 Sidorenko conjecture · M077 Komlós discrepancy conjecture · M080 Rota basis conjecture

### Complexity

M088 Deterministic polynomial identity testing · M082 NP versus coNP · M083 Valiant VP versus VNP · M084 Matrix multiplication exponent omega=2 · M085 Unique Games conjecture · M086 Quantum PCP conjecture · M087 P versus BPP · M089 Strongly polynomial linear programming · M090 Graph isomorphism in polynomial time · M081 P versus NP

### Dynamics

M061 2D self-avoiding walk exponents · M062 Critical percolation no-infinite-cluster conjecture · M063 Planar first-passage KPZ exponent · M064 FPP limit-shape strict convexity · M065 Mandelbrot local-connectivity conjecture · M066 Birkhoff billiard conjecture · M067 Sarnak Möbius disjointness conjecture · M068 Furstenberg times-two times-three conjecture · M069 Standard map positive metric entropy · M070 3D Ising conformal scaling conjecture

### Mathematical physics / finite structures

M092 Zauner SIC conjecture · M093 Linear MDS code main conjecture · M094 Hadamard matrix conjecture · M096 Projective plane order 12 · M097 Metric TSP four-thirds conjecture · M095 Exact Ramsey number R(5,5) · M091 Yang–Mills existence and mass gap · M098 Vaught conjecture · M099 Decidability of real exponential field · M100 Falconer distance-set conjecture

### Number theory

M002 Generalized Riemann Hypothesis · M003 Birch–Swinnerton-Dyer conjecture · M004 abc conjecture · M005 Twin prime conjecture · M006 Strong Goldbach conjecture · M007 Bateman–Horn conjecture · M008 Elliott–Halberstam conjecture · M009 Montgomery pair-correlation conjecture · M010 Generalized Ramanujan conjecture · M001 Riemann Hypothesis

### Topology

M031 Smooth 4D Poincaré conjecture · M032 Smooth 4D Schoenflies conjecture · M033 11/8 conjecture · M034 Borel rigidity conjecture · M035 Novikov conjecture · M036 Singer conjecture · M037 Hilbert–Smith conjecture · M038 Complex structure on S6 · M039 Hopf sign conjecture · M040 Higher-dimensional Weinstein conjecture

## Foundations: the mathematics behind the frontier

A curated starting shelf, not an assertion that any one ranking of mathematics is objective. Each entry gives a substantive theorem and a route into its proof or source literature; these are established landmarks, not new Project 100 results.

| Theme | Landmark theorem or principle | Why it matters / source |
|---|---|---|
| Arithmetic | Infinitely many primes; unique factorization in the integers; prime number theorem, π(x) ~ x/log x | The basic structure and asymptotic distribution of primes; [DLMF number theory](https://dlmf.nist.gov/27). |
| Arithmetic geometry | Fermat's Last Theorem: no positive integer solutions to xⁿ+yⁿ=zⁿ for n>2 | Modularity and elliptic curves connect arithmetic to analysis; [Wiles, Annals of Mathematics](https://doi.org/10.2307/2118559). |
| Logic | Gödel incompleteness: consistent, effectively axiomatized theories containing enough arithmetic cannot decide all arithmetic sentences | Separates mathematical truth, derivability and formal verification; [Stanford Encyclopedia, Gödel](https://plato.stanford.edu/entries/goedel-incompleteness/). |
| Computability | Turing undecidability of the halting problem | General limits of algorithmic decision procedures; [Turing 1936](https://doi.org/10.1112/plms/s2-42.1.230). |
| Topology | Poincaré theorem: every closed simply connected 3-manifold is homeomorphic to S³ | Ricci flow and geometrization; [Perelman, entropy formula](https://arxiv.org/abs/math/0211159), [Clay Poincaré](https://www.claymath.org/millennium/poincare-conjecture/). |
| Algebra | Galois theory identifies solvability by radicals with solvable Galois groups in characteristic zero | Symmetry controls equations; [Stacks Project, fields](https://stacks.math.columbia.edu/tag/09FI). |
| Geometry | Gauss–Bonnet relates total curvature of a closed oriented surface to 2π times its Euler characteristic | Local geometry determines global topology; [Encyclopedia of Mathematics](https://encyclopediaofmath.org/wiki/Gauss-Bonnet_theorem). |
| Analysis | Fourier–Plancherel: Fourier transform extends to a unitary map on L² with unitary normalization | Bridge between physical and frequency domains; [Encyclopedia of Mathematics](https://encyclopediaofmath.org/wiki/Plancherel_theorem). |
| Probability | Central limit theorem for i.i.d. variables of finite nonzero variance | Normalized sums converge in distribution to a Gaussian; [Encyclopedia of Mathematics](https://encyclopediaofmath.org/wiki/Central_limit_theorem). |
| Information | Shannon's noisy-channel coding theorem: reliable rates below capacity, converse above capacity, under its channel assumptions | Quantifies the limits of reliable communication; [Shannon 1948](https://doi.org/10.1002/j.1538-7305.1948.tb01338.x). |
| Combinatorics | Szemerédi: positive upper-density subsets of positive integers contain arithmetic progressions of every finite length | Structural patterns forced by density; [Szemerédi 1975](https://doi.org/10.4064/aa-27-1-199-245). |
| Graph theory | Four-color theorem: every planar graph is 4-colorable | Landmark computer-assisted proof; [Appel and Haken](https://doi.org/10.1215/ijm/1256049011). |
| Optimization | Linear programming strong duality for feasible finite optima | Primal/dual certificates and optimization algorithms; [NEOS guide](https://neos-guide.org/guide/types/lp/). |
| Complexity | Cook–Levin: Boolean satisfiability is NP-complete | Enables reductions that classify computational difficulty; [Cook 1971](https://doi.org/10.1145/800157.805047). |
| Quantum information | Bell inequalities constrain local hidden-variable correlations; quantum predictions violate them | Operational distinction between classical and quantum correlations; [Bell 1964](https://doi.org/10.1103/PhysicsPhysiqueFizika.1.195). |

## 2026 frontier

**Reading convention:** every result below is an assumed-true external result for this edition unless called a baseline or a conditional implication. Sources are dated release records or specialist leads; links do not certify proofs. No local full-proof replay or new independent review is represented. For claims whose primary proof has not been inspected, retain the source-audit task and do not expand the stated scope.

| Stable ID | Mathematical change | Consequence / next question | Source |
|---|---|---|---|
| M001 | RH: all nontrivial zeros of ζ have real part 1/2. | Understand and simplify the formal argument; extract arithmetic consequences. | [GRH Polymath, Nov 24](https://terrytao.wordpress.com/2026/11/24/g-r-h-polymath/); [existing audit #395](https://github.com/Svyable/100/issues/395). |
| M002 | GRH for Dirichlet L-functions, specifically. | Do not infer GRH for arbitrary automorphic or other L-functions. Compare canonical scope. | [GRH Polymath](https://terrytao.wordpress.com/2026/11/24/g-r-h-polymath/), [#395](https://github.com/Svyable/100/issues/395). |
| M041 | Jacobian conjecture counterexamples in dimensions ≥3, as reported in the prior frontier review. | Plane case remains a distinct target; isolate obstruction to dimension reduction. Exact construction and scope still require primary-source audit. | [Gao, arXiv:2608.00222](https://arxiv.org/abs/2608.00222). |
| M055 | Kakeya maximal and dimension conjectures follow from the claimed local-smoothing proof. | Study endpoint and quantitative consequences rather than repeat the dimension proof. | [Oct 26 release](https://github.com/openai/math/blob/main/history.md). |
| M056 | Stein spherical restriction estimates throughout the interior of the conjectured range. | Endpoints and exact dimension/exponent scope must remain separate. | [Oct 26 release](https://github.com/openai/math/blob/main/history.md). |
| M071 | Hadwiger refuted: χ_f(G)>h(G) even for arbitrarily large graphs of independence number at most two; a universal linear list-coloring bound also reported. | Determine sharp χ/h and list-coloring ratios and explicit finite witnesses. | [Hadwiger counterexample](https://github.com/openai/math/tree/main/preprints/A-counterexample-to-Hadwigers-conjecture-September-23-2026); [release index](https://github.com/openai/math/blob/main/overview.tex). |
| M072 | Erdős–Hajnal for all induced paths, as reported in the prior review. | Transfer to other forbidden induced graphs; general conjecture not thereby settled. | [The Erdős–Hajnal property for paths, arXiv:2611.01963](https://arxiv.org/abs/2611.01963); full proof audit outstanding. |
| M073 | Sidorenko refuted by a connected bipartite pattern on 35 vertices and 66 edges. | Recover exact graph and host graphon, certify density inequality; characterize positive graph families. | [Sidorenko manuscript](https://github.com/openai/math/tree/main/preprints/A-counterexample-to-Sidorenkos-conjecture-September-23-2026). |
| M075 | Frankl: reported lower bound 0.3828852549667978 on maximum element frequency; conjecture asks ≥1/2. | Gap ≈0.117114745; attack entropy-method barriers and structural equality cases. | [Costa–Sadhu, arXiv:2610.02295v1](https://arxiv.org/abs/2610.02295v1); exact certificate audit pending. |
| M076 | Fixed-petal sunflower exponential bound: for each r≥3 there is C_r such that sufficiently large k-uniform families (>C_r^k) contain an r-sunflower. | Optimize the base, dependence on r, constructive extraction, and uniformity. | [Nov 24 manuscript](https://github.com/openai/math/tree/main/preprints/An-exponential-bound-for-sunflowers-November-24-2026). |
| M077 | Komlós vector discrepancy bounded by a universal constant; elementary proof gives K≤36. | Optimize K and obtain efficient constructive signings; do not confuse fixed-order stronger variants. | [Karingula–Lovett, Sep 17](https://eccc.weizmann.ac.il/report/2026/188/). |
| M078 | Cogentic dense edge-reconstruction result, reported for linear edge density. | Edge-deleted and vertex-deleted decks are distinct. Full vertex reconstruction remains a target. | [Pinned Cogentic papers](https://github.com/google-research/google-research/tree/4a7bc8ab0bc7/cogentic_research_papers), [#404](https://github.com/Svyable/100/issues/404). |
| M083 | VP≠VNP; reported stronger hierarchy VF⊊VBP⊊VP⊊VNP. | Quantitative arithmetic circuit lower bounds and reductions; not P≠NP. | [Nov 23 manuscript](https://github.com/openai/math/tree/main/preprints/VP-and-VNP-are-different-November-23-2026), [Nov 24 release](https://github.com/openai/math/blob/main/history.md). |
| M084 | Matrix multiplication exponent ω=9/4 in the reported theorem's setting; disproves ω=2 in that setting. | Field dependence, finite-size algorithms, constants, memory and numerical stability. | [Nov 24 manuscript](https://github.com/openai/math/tree/main/preprints/The-matrix-multiplication-exponent-is-nine-fourths-November-24-2026), [#403](https://github.com/Svyable/100/issues/403). |
| M088 | Circuit lower bounds and tensor geometry may transfer to deterministic polynomial identity testing. | An implication is not yet proved here; specify circuit class, field and hitting-set complexity. | [Nov 24 release](https://github.com/openai/math/blob/main/history.md). |
| M089 | Deterministic strongly polynomial linear programming, as reported. | Explicit operations, encoding bounds, complexity constants and practical implementation. | [Nov 24 release](https://github.com/openai/math/blob/main/history.md). |
| M092 | All-dimension SIC existence via reported Stark-unit reciprocity. | Separate general SIC existence, Weyl–Heisenberg covariance and Zauner symmetry; exact paper audit remains necessary. Do not rely on a separate withdrawn 2026 proof claim. | [ProofAtlas](https://www.proofatlas.ai/open-problems/) and [Open Quantum Problems](https://openquantumproblems.com/p/N1) identify Radchenko–Wheeler's October 4 manuscript; primary proof intake outstanding. |
| M097 | Baseline metric TSP subtour gap 4/3 ≤ sup OPT/LP ≤ 3/2; existing restricted subdivision candidates do not close it. | Prove universal 4/3 or construct a counterexample; optimize rounding and certificates. | [Project research dossier](research/M097_SUBDIVISION_CORE.md), [ProofAtlas](https://www.proofatlas.ai/open-problems/). |

### Beyond the original 100: additional landmarks to retain

The recent release also reports polynomial Hirsch conjecture counterexamples for bounded simple rational polytopes, a strict arithmetic complexity hierarchy, Fourier-transform and integer-multiplication exponent results, and falsification of the Exponential Time Hypothesis. These merit separate permanent compendium entries with exact statements and proof-scope audits, not silent reuse of M-IDs. [Primary release history](https://github.com/openai/math/blob/main/history.md).

## A living atlas, not a graveyard of conjectures

Each future compendium entry should retain: permanent ID; precise statement and domain; established/assumed/open distinction; latest proof, refutation or bound with date and source version; theorem dependencies; independently verified scope; remaining sharp constants, structural classifications and algorithms; implications and non-implications; and a revision history. Record upper and lower bounds separately with exact normalization. Keep the established mathematical landscape even when an active research target is retired or replaced.

For new discovery, use the live [ranked portfolio](RANKED.md) and existing claims. For external intake, use ProofAtlas and primary manuscripts to identify changed frontiers; coordinate with [#404](https://github.com/Svyable/100/issues/404), [#409](https://github.com/Svyable/100/issues/409), [#403](https://github.com/Svyable/100/issues/403) and [#395](https://github.com/Svyable/100/issues/395) rather than opening duplicate audit projects. Never claim independent mathematical or commercial validation from an assumed result.
