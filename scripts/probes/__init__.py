"""Exact probe lab: reusable engines and per-problem probes.

Probes are allowlisted *in code* here; nothing in data/ can make the lab
execute a new module. Each probe reproduces or extends a finite, exactly
checkable statement and has an independent checker. A passing probe is
evidence about a finite range only and never resolves a universal conjecture.
"""
from importlib import import_module

ENGINES = {
    "primes": {
        "name": "Prime sieve + deterministic Miller-Rabin",
        "modules": ["scripts/probes/primes.py"],
        "use": "Verified-range certificates for additive and unit-fraction problems.",
    },
    "finite_fields": {
        "name": "GF(q) arithmetic for every prime power, with quadratic characters",
        "modules": ["scripts/probes/fields.py"],
        "use": "Paley constructions, projective geometries, arcs/MDS codes, Ramsey colourings, matroids.",
    },
    "graph_census": {
        "name": "Isomorphism-free graph census with Burnside completeness certificate",
        "modules": ["scripts/probes/graphs.py"],
        "use": "Exhaustive checks of graph conjectures on all graphs up to 7 vertices.",
    },
    "poset_census": {
        "name": "Poset census with orbit-counting certificate and linear-extension DP",
        "modules": ["scripts/probes/posets.py"],
        "use": "Exhaustive order-theoretic checks on all posets up to 7 elements.",
    },
    "cyclotomic": {
        "name": "Exact arithmetic in cyclotomic rings Z[zeta_m]",
        "modules": ["scripts/probes/cyclotomic.py"],
        "use": "Floating-point-free verification of complex configurations (SICs, MUBs, codes).",
    },
    "tensor_certificates": {
        "name": "Sparse exact tensor-decomposition checker",
        "modules": ["scripts/probes/tensor.py"],
        "use": "Replay any bilinear algorithm or rank decomposition as an exact certificate.",
    },
    "symmetry_reduction": {
        "name": "Group-transitivity reductions (frames in PG(2,q), bases under GL(n,p))",
        "modules": ["scripts/probes/arcs.py", "scripts/probes/rota.py"],
        "use": "Shrinks exhaustive searches by fixing a canonical starting configuration.",
    },
    "exact_lp": {
        "name": "Exact rational simplex with LP-duality optimality certificates",
        "modules": ["scripts/probes/exact_lp.py"],
        "use": "Certified LP relaxations (Held-Karp, fractional covers, LP bounds) with no floating point.",
    },
    "graph_homomorphisms": {
        "name": "Exact homomorphism counting for bipartite patterns, recountable from either side",
        "modules": ["scripts/probes/homomorphisms.py"],
        "use": "Homomorphism-density inequalities (Sidorenko, forcing, common graphs) on certified host sets.",
    },
    "polynomial_algebra": {
        "name": "Exact bivariate polynomial algebra with lattice kernels and inverse construction",
        "modules": ["scripts/probes/polynomials.py"],
        "use": "Jacobians, compositions and certified inverses of polynomial maps; exhaustive integer classes.",
    },
    "interval_arithmetic": {
        "name": "Rigorous fixed-point interval arithmetic with certified exp, log, sin, cos, atan and pi",
        "modules": ["scripts/probes/intervals.py"],
        "use": "Floating-point-free enclosures for analytic computations; every series carries a remainder bound.",
    },
    "l_functions": {
        "name": "Certified zeta and Dirichlet L-function evaluation with argument-principle zero counts",
        "modules": ["scripts/probes/lfunctions.py"],
        "use": "Euler-Maclaurin and Stirling with explicit remainders, Hardy Z sign changes, exact N(T).",
    },
    "group_characters": {
        "name": "Permutation groups, quotients and character degrees by Dixon's modular method",
        "modules": ["scripts/probes/groups.py"],
        "use": "Conjugacy classes, Sylow and radical subgroups, irreducible degrees for groups up to ~10^4.",
    },
    "clique_search": {
        "name": "Branch-and-bound clique search with exhaustive subset re-check",
        "modules": ["scripts/probes/ramsey_witness.py"],
        "use": "Ramsey and coding lower-bound witnesses.",
    },
}

# probe id -> module name (ordered by problem id)
PROBES = {
    "zeta_zeros": "zeta_zeros",
    "dirichlet_zeros": "dirichlet_zeros",
    "goldbach": "goldbach",
    "erdos_straus": "erdos_straus",
    "jacobian": "jacobian",
    "alperin_weights": "alperin",
    "hadwiger": "hadwiger",
    "sidorenko": "sidorenko",
    "reconstruction": "reconstruction",
    "one_third": "posets",
    "rota": "rota",
    "strassen": "tensor",
    "sic": "sic",
    "mds_arcs": "arcs",
    "hadamard": "hadamard",
    "ramsey_witnesses": "ramsey_witness",
    "projective_planes": "planes",
    "held_karp": "held_karp",
}


def load(probe_id):
    module = import_module(f"{__name__}.{PROBES[probe_id]}")
    if module.PROBE["id"] != probe_id:
        raise ValueError(f"probe registry mismatch for {probe_id}")
    return module


def artifact(probe_id):
    return f"scripts/probes/{PROBES[probe_id]}.py"


def command(probe_id):
    return f"python3 scripts/lab.py --probe {probe_id}"


def all_probes():
    return [load(pid) for pid in PROBES]
