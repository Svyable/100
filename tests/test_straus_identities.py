import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import mine
import mines
import research
import straus_identities
from probes.core import ProbeFailure


class StrausIdentityTests(unittest.TestCase):
    def test_polynomial_proofs_and_primary_samples(self):
        straus_identities.prove_all()
        n, x, y, z = straus_identities.FAMILIES[0].triple(0)
        self.assertEqual((n, x, y, z), (97, 25, 970, 4850))
        n, x, y, z = straus_identities.FAMILIES[1].triple(0)
        self.assertEqual((n, x, y, z), (73, 20, 292, 730))

    def test_coverage_report_matches_the_mine_ledger(self):
        report = straus_identities.coverage_report(8000)
        self.assertEqual(report["primes_1_mod_24"], 117)
        self.assertEqual(report["covered"], 106)
        self.assertEqual(len(report["uncovered"]), 11)
        self.assertEqual(report["uncovered_mod_120"], [1, 49])
        self.assertEqual(report["by_family"]["R3-97"], 30)
        self.assertEqual(report["by_family"]["R7-73"], 35)

    def test_mine_is_registered_and_reproducible(self):
        self.assertIn("straus_identities", mines.MINES)
        self.assertEqual(mine.main(["--mine", "straus_identities"]), 0)
        ledger = json.loads(mine.RESULTS.read_text(encoding="utf-8"))
        record = ledger["mines"]["straus_identities"]
        self.assertTrue(record["holds"])
        self.assertEqual(record["summary"]["covered_primes"], 106)
        self.assertEqual(record["summary"]["uncovered_primes"], 11)

    def test_campaign_points_at_the_identity_dossier(self):
        _, program, _ = research.load()
        campaign = next(c for c in program["campaigns"] if c["problem_id"] == "M019")
        self.assertEqual(campaign["dossier"], "research/M019_IDENTITIES.md")
        self.assertIn("straus_identities", campaign["next_experiment"])
        self.assertIn(
            "python3 scripts/mine.py --mine straus_identities",
            campaign["additional_verifiers"],
        )
        milestone = next(m for m in program["milestones"] if m["id"] == "B-MINE-019-ID")
        self.assertEqual(milestone["verifier"], "python3 scripts/mine.py --mine straus_identities")

    def test_checker_rejects_a_tampered_coverage_count(self):
        module = mines.load("straus_identities")
        params = module.MINE["levels"]["smoke"]
        result = module.search(params)
        module.check(params, result)
        bad = json.loads(json.dumps(result))
        bad["summary"]["covered_primes"] = 0
        with self.assertRaises(ProbeFailure):
            module.check(params, bad)


if __name__ == "__main__":
    unittest.main()
