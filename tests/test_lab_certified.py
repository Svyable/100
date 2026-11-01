"""Independent interval, analytic and group certificates preserved alongside original probes."""
import copy
import unittest
from fractions import Fraction
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from probes import core, intervals_cert as intervals, groups_cert as groups, lfunctions
from probes.core import ProbeFailure
import probes
from test_lab import run

def I_exact(value, p):
    return intervals.RI.exact(value, p)

class IndependentEngineTests(unittest.TestCase):
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

class IndependentTamperTests(unittest.TestCase):
    def assertRejects(self, module, params, result):
            with self.assertRaises(ProbeFailure):
                module.check(params, result)

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
                m._check_character(-4 * 4, 16, [m.kronecker(-16, n) for n in range(16)], 1)

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
