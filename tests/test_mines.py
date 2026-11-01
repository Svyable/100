import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import mine
import mines
import research
from mines.poset_balance import height, width
from probes.core import ProbeFailure


class MineTests(unittest.TestCase):
    def test_ledger_matches_a_fresh_run(self):
        self.assertEqual(mine.main(["--check"]), 0)

    def test_tables_are_what_the_campaigns_say(self):
        ledger = json.loads(mine.RESULTS.read_text(encoding="utf-8"))
        tables = ledger["mines"]
        campaigns = {c["problem_id"]: c for c in research.load()[1]["campaigns"]}

        gold = tables["goldbach_growth"]["summary"]
        self.assertEqual(gold["record_count"], 12)
        self.assertEqual([gold["largest_least_prime"], gold["attained_at"]], [173, 7426])
        self.assertIn("goldbach_bound", campaigns["M006"]["next_experiment"])
        self.assertEqual(campaigns["M006"]["dossier"], "research/M006_BOUND.md")
        bound = tables["goldbach_bound"]["summary"]
        self.assertEqual(bound["bound_factor"], 3)
        self.assertEqual(bound["record_count"], 12)
        self.assertEqual(bound["worst_record_n"], 7426)
        self.assertEqual(bound["worst_record_prime"], 173)
        self.assertIn(
            "python3 scripts/mine.py --mine goldbach_bound",
            campaigns["M006"]["additional_verifiers"],
        )

        straus = tables["straus_patterns"]["summary"]
        self.assertEqual(straus["primes"], 117)
        self.assertEqual(straus["residues"], [3, 7, 11, 15, 19, 23])
        self.assertEqual(straus["by_residue"]["3"] + straus["by_residue"]["7"], 105)
        self.assertIn("straus_identities", campaigns["M019"]["next_experiment"])
        identities = tables["straus_identities"]["summary"]
        self.assertEqual(identities["covered_primes"], 106)
        self.assertEqual(identities["uncovered_primes"], 11)
        self.assertEqual(identities["uncovered_mod_120"], [1, 49])

        deck = tables["deck_invariants"]["summary"]
        self.assertEqual(deck["degree_separates_through"], 4)
        self.assertEqual(deck["degree_and_triangles_separate_through"], 5)
        self.assertEqual(deck["degree_and_triangles_excess"]["6"], 20)
        self.assertIn("20 excess", campaigns["M078"]["next_experiment"])

        poset = tables["poset_balance"]["summary"]
        self.assertEqual(poset["one_third_posets"], 11)
        self.assertEqual(poset["least_balance"], "1/3")
        self.assertTrue(all(key.startswith("2x") for key in poset["width_height"]))
        self.assertEqual(sum(poset["width_height"].values()), 11)
        self.assertIn("width 2", campaigns["M079"]["next_experiment"])

        frankl = tables["frankl_orbits"]["summary"]
        self.assertEqual(frankl["families"]["4"], 4958)
        self.assertEqual(frankl["orbits"]["4"], 366)
        self.assertEqual(frankl["minimum_abundance"], "1/2")
        self.assertIn("366", campaigns["M075"]["next_experiment"])

        for mine_id, record in tables.items():
            self.assertTrue(record["holds"])
            self.assertIn(mines.command(mine_id), research.RUNNABLE)

    def test_width_and_height_of_a_chain_and_an_antichain(self):
        chain = (0, 1, 3)          # 0 < 1 < 2
        antichain = (0, 0, 0)
        self.assertEqual((width(chain), height(chain)), (1, 3))
        self.assertEqual((width(antichain), height(antichain)), (3, 1))

    def test_checkers_reject_a_changed_table(self):
        gold = mines.load("goldbach_growth")
        params = gold.MINE["levels"]["smoke"]
        result = gold.search(params)
        gold.check(params, result)
        bad = copy.deepcopy(result)
        bad["summary"]["largest_least_prime"] = 1
        with self.assertRaises(ProbeFailure):
            gold.check(params, bad)

        deck = mines.load("deck_invariants")
        params = deck.MINE["levels"]["smoke"]
        result = deck.search(params)
        bad = copy.deepcopy(result)
        bad["summary"]["degree_and_triangles_excess"]["6"] = 0
        with self.assertRaises(ProbeFailure):
            deck.check(params, bad)

        straus = mines.load("straus_patterns")
        params = straus.MINE["levels"]["smoke"]
        result = straus.search(params)
        bad = copy.deepcopy(result)
        bad["certificate"]["rows"][0]["z"] += 1
        with self.assertRaises(ProbeFailure):
            straus.check(params, bad)


if __name__ == "__main__":
    unittest.main()
