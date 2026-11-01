"""Tests for the exact probe lab: engines, tamper detection, ledger and report integrity."""
import copy
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import lab
import probes
import rank
import research
from probes import (core, cyclotomic, exact_lp, fields, graphs, groups, homomorphisms, intervals,
                    lfunctions, polynomials, primes)
from probes.core import ProbeFailure


def I_exact(value, p):
    return intervals.RI.exact(value, p)


def run(probe_id, params):
    module = probes.load(probe_id)
    result = module.search(params)
    module.check(params, result)  # untampered result must pass
    return module, result


class EngineTests(unittest.TestCase):
    def test_finite_fields_axioms(self):
        for q in (2, 3, 4, 5, 7, 8, 9, 16, 25, 27):
            F = fields.GF(q)
            self.assertEqual(sum(1 for x in F.chi if x == 1), (q - 1) // 2 if q % 2 else q - 1)
            for a in range(1, q):
                self.assertEqual(F.mul(a, F.inv(a)), 1)
                self.assertEqual(F.add(a, F.neg(a)), 0)
            for a, b, c in ((1, q - 1, q // 2), (q - 1, q - 2, 1), (2 % q, 3 % q, q - 1)):
                self.assertEqual(F.mul(a, F.add(b, c)), F.add(F.mul(a, b), F.mul(a, c)))
        with self.assertRaises(ValueError):
            fields.GF(6)

    def test_primality_oracles_agree(self):
        flags = primes.sieve(20000)
        odd = primes.odd_sieve(20000)
        for n in range(20001):
            self.assertEqual(bool(flags[n]), primes.is_prime(n), n)
            self.assertEqual(bool(flags[n]), odd(n), n)

    def test_cyclotomic_ring(self):
        R = cyclotomic.Cyclotomic(12)
        self.assertEqual(cyclotomic.phi(12), (1, 0, -1, 0, 1))
        z = R.zeta(1)
        power = R.const(1)
        for _ in range(12):
            power = R.mul(power, z)
        self.assertTrue(R.equal(power, R.const(1)))
        self.assertEqual(R.as_integer(R.mul(z, R.conj(z))), 1)
        self.assertIsNone(R.as_integer(z))

    def test_two_canonical_forms_agree_on_isomorphism(self):
        for n in range(1, 6):
            codes = graphs.census(n)
            self.assertEqual(len(codes), graphs.burnside_count(n))
            brute = {graphs.brute_canonical(n, graphs.edge_set(n, c)) for c in codes}
            degree = {graphs.degree_canonical(n, graphs.edge_set(n, c)) for c in codes}
            self.assertEqual(len(brute), len(codes))
            self.assertEqual(len(degree), len(codes))

    def test_exact_lp_random_programs_are_certified(self):
        import random
        rng = random.Random(20261031)
        for _ in range(80):
            n, m = rng.randint(2, 4), rng.randint(2, 5)
            x0 = [rng.randint(0, 3) for _ in range(n)]  # a known feasible point
            c = [rng.randint(0, 6) for _ in range(n)]   # c >= 0 keeps the program bounded
            A_ge = [[rng.randint(-2, 4) for _ in range(n)] for _ in range(m)]
            b_ge = [sum(a * v for a, v in zip(row, x0)) - rng.randint(0, 3) for row in A_ge]
            if rng.random() < 0.5:
                A_eq = [[rng.randint(0, 3) for _ in range(n)]]
                b_eq = [sum(a * v for a, v in zip(A_eq[0], x0))]
            else:
                A_eq, b_eq = [], []
            value, x, y, z = exact_lp.solve(c, A_eq, b_eq, A_ge, b_ge)
            self.assertEqual(exact_lp.certify(c, A_eq, b_eq, A_ge, b_ge, x, y, z), value)
            self.assertLessEqual(value, sum(a * v for a, v in zip(c, x0)))
        with self.assertRaises(exact_lp.Infeasible):
            exact_lp.solve([1, 1], [[1, 1]], [1], [[1, 1]], [3])
        with self.assertRaises(ValueError):  # a non-optimal primal point fails certification
            exact_lp.certify([1, 1], [], [], [[1, 2], [3, 1]], [4, 6], [4, 0], [], [0, 0])

    def test_homomorphism_counts_match_brute_force(self):
        sid = probes.load("sidorenko")
        for name, H in sid.patterns().items():
            if H["A"] + H["B"] > 6:
                continue
            for n in range(1, 4):
                for code in graphs.census(n):
                    adj = graphs.to_adjacency(n, code)
                    brute = homomorphisms.brute_count(H, n, adj)
                    self.assertEqual(homomorphisms.count_from_side(H, n, adj, "A"), brute, name)
                    self.assertEqual(homomorphisms.count_from_side(H, n, adj, "B"), brute, name)
        k4 = graphs.to_adjacency(4, (1 << 6) - 1)
        c4 = sid.patterns()["C4"]
        self.assertEqual(homomorphisms.count_from_side(c4, 4, k4), 4 * 3 * 7)  # n(n-1)(n^2-3n+3)

    def test_polynomial_algebra(self):
        P = polynomials
        f, g = {(1, 0): 1, (0, 2): 1}, {(0, 1): 1}                     # (x + y^2, y)
        self.assertEqual(P.jacobian(f, g), {(0, 0): 1})
        jac = probes.load("jacobian")
        p, q = jac.inverse(f, g, 2)
        self.assertEqual((p, q), ({(1, 0): 1, (0, 2): -1}, {(0, 1): 1}))  # (x - y^2, y)
        self.assertEqual(P.compose(p, f, g), {(1, 0): 1})
        self.assertIsNone(jac.inverse({(1, 0): 1}, {(1, 0): 1}, 1))     # (x, x) is not invertible
        kernel = P.lattice_kernel([[1, 1, 0], [0, 1, 1]], [-1, 0, 1])
        self.assertEqual(sorted(map(tuple, kernel)), [(-1, 1, -1), (0, 0, 0), (1, -1, 1)])

    def test_interval_functions_enclose_exact_values(self):
        I = intervals
        p = 90
        x = I.RI.exact(Fraction(7, 3), p)
        self.assertTrue((x * 3).contains(7) and (x / 7).contains(Fraction(1, 3)))
        self.assertTrue(I.RI.exact(2, p).sqrt().sqr().contains(2))
        self.assertTrue(I.exp(I.log(x)).contains(Fraction(7, 3)))
        s, c = I.sincos(x)
        self.assertTrue((s.sqr() + c.sqr()).contains(1))
        self.assertTrue((I.atan(I.RI.exact(1, p)) * 4 - I.pi(p)).contains_zero())
        self.assertTrue((I.atan(I.RI.exact(-3, p)) - I.atan(I.RI.exact(Fraction(1, 3), p))
                         + I.pi(p).shift(-1)).contains_zero())  # atan 3 + atan 1/3 = pi/2
        self.assertTrue((I.log(I.RI.exact(8, p)) - I.log2(p) * 3).contains_zero())
        # pi = 3.14159265358979323846264338327950288419716939937510...
        digits = Fraction(314159265358979323846264338327950288419716939937510, 10 ** 50)
        self.assertTrue(abs(I.pi(p).lower() - digits) < Fraction(1, 10 ** 26))
        self.assertTrue(I.pi(p).lower() <= digits + Fraction(1, 10 ** 50) and I.pi(p).upper() >= digits)
        with self.assertRaises(ZeroDivisionError):
            I.RI(-1, 1, p).recip()
        # arguments in each half-plane window, including the Im < 0 window centred at -pi/2
        z = I.CI.exact(1, -1, p)
        self.assertEqual(I.half_plane(z), 0)
        self.assertTrue((I.arg_in_window(z, 3) + I.pi(p) * Fraction(1, 4)).contains_zero())
        self.assertTrue((I.arg_in_window(I.CI.exact(-1, 0, p), 2) - I.pi(p)).contains_zero())

    def test_l_function_values_and_zero_counts(self):
        LF = lfunctions
        p = 100
        zeta = LF.LSeries(1, [1], p)
        z2 = zeta.value(I_exact(2, p), I_exact(0, p))
        self.assertTrue((z2.re - intervals.pi(p).sqr() / 6).contains_zero())
        self.assertLess(z2.re.width(), Fraction(1, 10 ** 20))
        # the first zero 14.134725141734693790... lies between two certified sign changes
        lo, hi = (LF.hardy_z(zeta, I_exact(t, p), 0)[0].sign() for t in ("14.1347", "14.1348"))
        self.assertEqual((lo, hi), (-1, 1))
        # L(1, chi_-4) = pi/4 through the removable singularity of the integral term
        chi4 = LF.LSeries(4, [0, 1, 0, -1], p)
        self.assertTrue((chi4.value(I_exact(1, p), I_exact(0, p)).re - intervals.pi(p) / 4).contains_zero())
        self.assertEqual(LF.lifted_direction([0, 0, 3, 3]), -1)
        self.assertEqual(LF.lifted_direction([0, 1, 2, 3, 0]), 4)
        self.assertIsNone(LF.lifted_direction([0, 2]))
        # N(50) = 10 for zeta; N(40, chi_-4) = 14 needs the Im < 0 window at the end of the segment
        cfg = (Fraction(1, 2), 8, None)
        pieces = LF.find_pieces(zeta, Fraction(50), *cfg)
        self.assertEqual(LF.argument_count(zeta, Fraction(50), 0, pieces, *cfg, 24, 24, pole=True)[0], 10)
        chi4 = LF.LSeries(4, [0, 1, 0, -1], 80)
        cfg = (Fraction(2, 5), 4, 16)
        pieces = LF.find_pieces(chi4, Fraction(40), *cfg)
        self.assertEqual(pieces[-1][2], 3)
        self.assertEqual(LF.argument_count(chi4, Fraction(40), 1, pieces, *cfg, 20, 16, pole=False)[0], 14)

    def test_character_degrees_two_primes(self):
        expected = {"S4": [1, 1, 2, 3, 3], "A5": [1, 3, 3, 4, 5], "PSL(2,7)": [1, 3, 3, 6, 7, 8],
                    "GL(2,3)": [1, 1, 2, 2, 2, 3, 3, 4]}
        alp = probes.load("alperin_weights")
        for name, degrees in expected.items():
            G = groups.FiniteGroup.from_permutations(alp.GROUPS[name][0])
            d1, r1 = groups.character_degrees(G)
            d2, r2 = groups.character_degrees(G, skip=1, reverse=True)
            self.assertEqual(d1, degrees)
            self.assertEqual(d2, degrees)
            self.assertNotEqual(r1, r2)
        # a quotient: S4 / V4 is S3
        S4 = groups.FiniteGroup.from_permutations(alp.GROUPS["S4"][0])
        V4 = frozenset(groups.closure([groups.cycle(4, (0, 1), (2, 3)), groups.cycle(4, (0, 2), (1, 3))],
                                      S4.identity))
        quotient = groups.FiniteGroup.quotient(S4.elements, V4, S4.gens)
        self.assertEqual(quotient.order, 6)
        self.assertEqual(groups.character_degrees(quotient)[0], [1, 1, 2])

    def test_canonical_json_is_order_independent(self):
        self.assertEqual(core.digest({"b": 1, "a": [Fraction(1, 3)]}),
                         core.digest({"a": ["1/3"], "b": 1}))


class TamperTests(unittest.TestCase):
    """Every checker must reject a corrupted certificate."""

    def assertRejects(self, module, params, result):
        with self.assertRaises(ProbeFailure):
            module.check(params, result)

    def test_goldbach(self):
        params = {"limit": 2000}
        m, r = run("goldbach", params)
        bad = copy.deepcopy(r)
        bad["certificate"]["least_prime"][40] = 9  # 9 is not prime
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["least_prime"].pop()
        self.assertRejects(m, params, bad)

    def test_erdos_straus(self):
        params = {"limit": 600}
        m, r = run("erdos_straus", params)
        bad = copy.deepcopy(r)
        bad["certificate"]["triples"][100][2] += 1
        self.assertRejects(m, params, bad)

    def test_hadwiger(self):
        params = {"max_n": 5}
        m, r = run("hadwiger", params)
        bad = copy.deepcopy(r)
        target = next(x for x in bad["certificate"]["5"] if len(x["branch_sets"]) >= 3)
        target["branch_sets"].pop()
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        target = next(x for x in bad["certificate"]["5"] if len(set(x["colouring"])) >= 3)
        target["colouring"] = [0] * 5
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["5"].pop()
        self.assertRejects(m, params, bad)

    def test_reconstruction(self):
        params = {"max_n": 5}
        m, r = run("reconstruction", params)
        bad = copy.deepcopy(r)
        codes = bad["certificate"]["5"]["graphs"]
        codes[1] = codes[0]
        self.assertRejects(m, params, bad)

    def test_one_third(self):
        params = {"max_n": 5}
        m, r = run("one_third", params)
        self.assertEqual(r["summary"]["least_best_balance"], "1/3")
        bad = copy.deepcopy(r)
        row = next(x for x in bad["certificate"]["5"] if "pair" in x)
        row["x_before_y"] += 1
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        rows = bad["certificate"]["5"]
        rows[-1] = copy.deepcopy(rows[0])
        self.assertRejects(m, params, bad)

    def test_rota(self):
        params = {"cases": [[2, 2], [3, 2], [2, 3]]}
        m, r = run("rota", params)
        bad = copy.deepcopy(r)
        case = bad["certificate"]["2^3"]
        case["orders"] = "ff" + case["orders"][2:]
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["3^2"]["bases"][1] = bad["certificate"]["3^2"]["bases"][0]
        self.assertRejects(m, params, bad)

    def test_strassen(self):
        params = {"powers": [1, 2]}
        m, r = run("strassen", params)
        bad = copy.deepcopy(r)
        bad["certificate"]["decompositions"]["2"][3][2][0][1] *= -1
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["decompositions"]["4"].pop()
        self.assertRejects(m, params, bad)

    def test_sic(self):
        params = {"coefficient_bound": 0}
        m, r = run("sic", params)
        bad = copy.deepcopy(r)
        bad["certificate"]["d3_fiducials"][0][0] = [1, 1, 0]
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["d2_bloch_times_sqrt3"][0] = [1, 1, -1]
        self.assertRejects(m, params, bad)

    def test_mds_arcs(self):
        params = {"qs": [2, 3, 4, 5]}
        m, r = run("mds_arcs", params)
        self.assertEqual({q: v["max_arc_size"] for q, v in r["summary"].items()},
                         {"2": 4, "3": 4, "4": 6, "5": 6})
        bad = copy.deepcopy(r)
        bad["certificate"]["5"]["witness"][-1] = [1, 0, 1]  # collinear with (1,0,0),(0,0,1)
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["4"]["modulus"] = [1, 0, 1]  # x^2 + 1 is reducible over GF(2)
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["5"]["maximum_arcs_through_frame"] = 4
        self.assertRejects(m, params, bad)

    def test_hadamard(self):
        params = {"limit": 48}
        m, r = run("hadamard", params)
        bad = copy.deepcopy(r)
        bad["certificate"]["matrices"]["12"][5] ^= 1 << 7
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        del bad["certificate"]["matrices"]["20"]
        self.assertRejects(m, params, bad)

    def test_williamson_quadruples(self):
        had = probes.load("hadamard")
        for n in (3, 5, 7, 9):
            rows = had.williamson(n)
            self.assertIsNotNone(rows, n)
            size = 4 * n
            self.assertTrue(all(bin(rows[i] ^ rows[j]).count("1") == size // 2
                                for i in range(size) for j in range(i + 1, size)), n)
        A, B, C, D = had.williamson_quadruple(7)
        for t in range(1, 7):
            self.assertEqual(sum(sum(X[i] * X[(i + t) % 7] for i in range(7)) for X in (A, B, C, D)), 0)

    def test_ramsey_witnesses(self):
        params = {"witnesses": ["paley5", "circ8_1_4", "paley17"]}
        m, r = run("ramsey_witnesses", params)
        bad = copy.deepcopy(r)
        bad["certificate"]["paley5"]["edges"].append([0, 2])  # creates a triangle in C5
        self.assertRejects(m, params, bad)

    def test_projective_planes(self):
        params = {"max_q": 5, "table_limit": 30}
        m, r = run("projective_planes", params)
        bad = copy.deepcopy(r)
        line = bad["certificate"]["planes"]["3"][0]
        line[0] = next(x for x in range(13) if x not in line)
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["table"]["6"] = "open"
        self.assertRejects(m, params, bad)


    def test_held_karp(self):
        params = {"max_n": 5}
        m, r = run("held_karp", params)
        bad = copy.deepcopy(r)
        bad["certificate"][-1]["x"][0] = "0"
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"][-1]["hk"] = "1/1"
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"][-1]["opt"] += 1
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"].pop()
        self.assertRejects(m, params, bad)


    def test_sidorenko(self):
        params = {"max_host": 4}
        m, r = run("sidorenko", params)
        bad = copy.deepcopy(r)
        bad["certificate"]["K55_minus_C10"]["hosts"][-1][2] += 1
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["C4"]["hosts"].pop()
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["K33"]["min_ratio"] = "1/1"
        self.assertRejects(m, params, bad)


    def test_jacobian(self):
        params = {"degree": 2, "coefficients": [-1, 0, 1]}
        m, r = run("jacobian", params)
        self.assertEqual(r["summary"]["constant_jacobian_maps"], 240)
        bad = copy.deepcopy(r)
        row = next(x for x in bad["certificate"]["rows"] if len(x["p"]) > 1)
        row["p"][0][1] = str(Fraction(row["p"][0][1]) + 1)
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["rows"].pop()
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["rows"][0]["p"].append([[2, 1], "1"])  # exceeds the degree bound
        self.assertRejects(m, params, bad)


    def test_zeta_zeros(self):
        params = {"height": 30}
        m, r = run("zeta_zeros", params)
        self.assertEqual(r["summary"]["zeros"], 3)  # 14.13, 21.02, 25.01
        bad = copy.deepcopy(r)
        bad["certificate"]["zero_count"] += 1
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["signs"][-1] *= -1
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        i = next(k for k, x in enumerate(bad["certificate"]["signs"][1:], 1) if x != bad["certificate"]["signs"][k - 1])
        del bad["certificate"]["points"][i], bad["certificate"]["signs"][i]  # drop a sign change
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["pieces"][0][2] = 2  # claim Re < 0 at sigma = 2
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["pieces"].pop()  # no longer reaches sigma = 1/2
        self.assertRejects(m, params, bad)

    def test_dirichlet_zeros(self):
        params = {"discriminants": [-4, 5], "height": 12}
        m, r = run("dirichlet_zeros", params)
        self.assertEqual(r["summary"]["per_character"], {"-4": 2, "5": 3})  # 6.02, 10.24 | 6.65, 9.83, 11.96
        bad = copy.deepcopy(r)
        bad["certificate"]["characters"][0]["chi"][1] = -1
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["characters"][1]["zero_count"] -= 1
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["characters"][0]["real_axis"][0][1] = "1"  # radius too large to certify
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"]["characters"][0]["parity"] = 0
        self.assertRejects(m, params, bad)
        with self.assertRaises(ProbeFailure):
            m._check_character(-4 * 4, 16, [m.kronecker(-16, n) for n in range(16)], 1)  # not fundamental

    def test_alperin_weights(self):
        params = {"groups": ["S4", "A5"]}
        m, r = run("alperin_weights", params)
        self.assertEqual(r["summary"]["table"], {"S4 p=2": [2, 2], "S4 p=3": [4, 4], "A5 p=2": [4, 4],
                                                 "A5 p=3": [4, 4], "A5 p=5": [3, 3]})
        bad = copy.deepcopy(r)
        bad["certificate"][0]["radicals"].pop()
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"][2]["regular_classes"].pop()
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        bad["certificate"][2]["radicals"][0]["quotient_degrees"] = [1, 1, 1, 3, 3, 3]
        self.assertRejects(m, params, bad)
        bad = copy.deepcopy(r)
        rad = bad["certificate"][2]["radicals"]
        rad.append(copy.deepcopy(rad[-1]))  # duplicate (conjugate) radical subgroup
        self.assertRejects(m, params, bad)


class LedgerTests(unittest.TestCase):
    def test_registry_engines_and_levels(self):
        ids = set()
        for m in probes.all_probes():
            p = m.PROBE
            self.assertNotIn(p["id"], ids)
            ids.add(p["id"])
            self.assertTrue(set(p["engines"]) <= set(probes.ENGINES), p["id"])
            self.assertEqual(set(p["levels"]), set(lab.LEVELS))
            self.assertTrue(p["frontier"].strip())
            self.assertTrue((ROOT / probes.artifact(p["id"])).is_file())
            self.assertIn(probes.command(p["id"]), research.RUNNABLE)

    def test_committed_ledger_covers_every_probe_and_report_is_fresh(self):
        ledger = lab.load_ledger()
        for level in lab.LEVELS:
            self.assertEqual(set(ledger["levels"][level]), set(probes.PROBES))
            for pid, rec in ledger["levels"][level].items():
                self.assertTrue(rec["holds"], f"{pid} {level}")
                self.assertEqual(rec["params"], probes.load(pid).PROBE["levels"][level])
                self.assertEqual(len(rec["certificate_sha256"]), 64)
        self.assertEqual(lab.REPORT.read_text(encoding="utf-8"), lab.render_report(ledger))

    def test_check_mode_reproduces_ledger(self):
        self.assertEqual(lab.main(["--check", "--probe", "strassen", "--probe", "sic"]), 0)

    def test_failed_check_is_exit_code_two(self):
        module = probes.load("strassen")
        original = module.check
        try:
            def broken(params, result):
                raise ProbeFailure("simulated")
            module.check = broken
            with self.assertRaises(lab.LabError) as ctx:
                lab.run_probe(module, "smoke")
            self.assertEqual(ctx.exception.code, 2)
        finally:
            module.check = original

    def test_confirmed_violation_is_flagged_not_promoted(self):
        module = probes.load("strassen")
        original = module.search
        try:
            module.search = lambda params: dict(original(params), holds=False)
            record, _, _ = lab.run_probe(module, "smoke")
            self.assertFalse(record["holds"])
        finally:
            module.search = original
        self.assertEqual(json.loads(research.SOLVED.read_text(encoding="utf-8")), [])

    def test_every_computable_problem_is_covered_or_roadmapped(self):
        items, program, _ = research.load()
        covered = lab.coverage(items, program)
        roadmap = {e["problem_id"] for e in lab.load_roadmap(items, covered)["entries"]}
        for p in items:
            if p["modality"] in rank.COMPUTABLE:
                self.assertTrue(p["id"] in covered or p["id"] in roadmap, p["id"])
        self.assertFalse(covered & roadmap)

    def test_modality_is_required(self):
        items = json.loads(rank.REGISTRY.read_text(encoding="utf-8"))
        broken = copy.deepcopy(items)
        del broken[0]["modality"]
        with self.assertRaises(ValueError):
            rank.validate(broken)
        broken = copy.deepcopy(items)
        broken[0]["modality"] = "solved_by_vibes"
        with self.assertRaises(ValueError):
            rank.validate(broken)


if __name__ == "__main__":
    unittest.main()
