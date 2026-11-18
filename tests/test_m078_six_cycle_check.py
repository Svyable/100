"""Adversarial controls for #385 six-cycle proof packet (stdlib only)."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from m078_six_cycle_check import (verify_object, enumerate_paths, enumerate_cycles,
                                   incidence_rows, STAR_EDGES, check_coloring)


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads((ROOT / 'scripts' / 'certificates' /
                                 'm078_six_cycle_trade.json').read_text())

    def test_full_exact_certificate(self):
        v = verify_object(self.packet)
        self.assertEqual((v['exact_certs'], v['systems_proved']), (142, 5400))

    def test_topologies_and_cycle_data(self):
        self.assertEqual((len(enumerate_paths()), len(enumerate_cycles())), (90, 60))
        star = incidence_rows(STAR_EDGES)
        self.assertEqual(star[0], (1,1,0,0,0,0,0,0,0))
        self.assertEqual(star[2], (1,0,0,1,0,0,1,1,0))
        self.assertTrue(all(len(r) == 9 for r in star))

    def test_coefficient_mutation_rejected(self):
        x = copy.deepcopy(self.packet)
        x['representatives'][0]['terms'][0][1] += 1
        with self.assertRaisesRegex(ValueError, 'rational identity'):
            verify_object(x)

    def test_deleted_orbit_rejected(self):
        x = copy.deepcopy(self.packet)
        x['representatives'].pop()
        with self.assertRaisesRegex(ValueError, 'representative count'):
            verify_object(x)

    def test_duplicate_orbit_rejected(self):
        x = copy.deepcopy(self.packet)
        x['representatives'][1] = copy.deepcopy(x['representatives'][0])
        with self.assertRaisesRegex(ValueError, 'redundant orbit'):
            verify_object(x)

    def test_invalid_coloring_rejected(self):
        x = copy.deepcopy(self.packet)
        x['representatives'][0]['red'][0] = x['representatives'][0]['red'][1]
        with self.assertRaises(ValueError):
            verify_object(x)

    def test_target_tamper_rejected(self):
        x = copy.deepcopy(self.packet)
        x['target_coordinate'] = 15
        with self.assertRaisesRegex(ValueError, 'target coordinate'):
            verify_object(x)


if __name__ == '__main__':
    unittest.main()
