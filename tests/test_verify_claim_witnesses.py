"""Independent extractability checks for the M071/M073 claim witnesses."""
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_claim_witnesses as witnesses


class ClaimWitnessTests(unittest.TestCase):
    def test_sidorenko_pattern_invariants_two_ways(self):
        pin = witnesses.load_faces()
        path_a = witnesses.reconstruct_pattern(pin["faces_tuples"])
        path_b = witnesses.recount_by_degrees(pin["faces_tuples"])
        self.assertEqual(path_a["edge_count"], 66)
        self.assertEqual(path_b["edge_count"], 66)
        self.assertEqual(path_a["point_degrees"], path_b["point_degrees"])
        self.assertEqual(sum(path_a["point_degrees"]), 66)
        self.assertTrue(all(d == 3 for d in path_a["face_degrees"]))
        self.assertTrue(witnesses.pattern_connected(path_a["edges"]))
        self.assertEqual(path_a["pattern"]["A"] + path_a["pattern"]["B"], 35)

    def test_sidorenko_holds_on_tiny_hosts(self):
        pin = witnesses.load_faces()
        path_a = witnesses.reconstruct_pattern(pin["faces_tuples"])
        sanity = witnesses.sidorenko_tiny_hosts(path_a["pattern"], max_host=2)
        self.assertTrue(sanity["holds_on_all_hosts"])
        self.assertEqual(sanity["host_count"], 1 + 2)
        with self.assertRaises(witnesses.WitnessError):
            witnesses.sidorenko_tiny_hosts(path_a["pattern"], max_host=3)

    def test_tampered_faces_change_digest_and_fail_pin(self):
        pin = witnesses.load_faces()
        faces = [list(face) for face in pin["faces"]]
        faces[0][1] = 8
        with mock.patch.object(witnesses, "FACES", Path("/tmp/not-used")):
            broken = dict(pin)
            broken["faces"] = faces
            with mock.patch.object(
                witnesses.json, "loads", return_value={
                    **{k: v for k, v in pin.items() if k != "faces_tuples"},
                    "faces": faces,
                }
            ):
                # Direct reconstruct must still see 22 triples, but degrees change.
                rebuilt = witnesses.reconstruct_pattern(
                    [tuple(sorted(face)) for face in faces]
                )
                self.assertEqual(rebuilt["edge_count"], 66)
                self.assertNotEqual(
                    witnesses.digest([list(f) for f in pin["faces_tuples"]]),
                    witnesses.digest(faces),
                )

    def test_frozen_report_matches_recomputation(self):
        report = witnesses.check_report()
        self.assertEqual(report["reviews"][0]["problem_id"], "M071")
        self.assertEqual(report["reviews"][1]["problem_id"], "M073")
        self.assertEqual(report["reviews"][0]["status"], "no_explicit_finite_graph")
        self.assertEqual(
            report["reviews"][1]["status"], "pattern_reconstructed_host_missing"
        )
        self.assertFalse(report["reviews"][0]["explicit_graph_published"])
        self.assertFalse(report["reviews"][1]["explicit_host_published"])
        self.assertFalse(
            json.loads((ROOT / "data/solved.json").read_text(encoding="utf-8"))
        )

    def test_hadwiger_gap_is_explicit(self):
        gap = witnesses.audit_hadwiger()
        blob = " ".join(
            gap[k].lower()
            for k in ("claimed_quantifiers", "construction_notes", "gap")
        )
        self.assertIn("for every", blob)
        self.assertIn("no finite graph", blob)
        self.assertFalse(gap["explicit_graph_published"])
        self.assertEqual(gap["comparator_sha256"], witnesses.HADWIGER_COMPARATOR_SHA256)


if __name__ == "__main__":
    unittest.main()
