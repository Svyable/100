import json
import random
import sys
import types
import unittest
from fractions import Fraction
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import attest
from probes.core import ProbeFailure, digest, require


def toy(check):
    """A toy probe whose certificate lists the squares 0..n-1."""
    def search(params):
        squares = [i * i for i in range(params["n"])]
        return {"holds": True, "summary": {"n": params["n"], "total": sum(squares)},
                "certificate": {"squares": squares, "bound": Fraction(1, 2)}}
    module = types.SimpleNamespace(
        PROBE={"id": "toy", "problem_id": "M000", "levels": {"smoke": {"n": 6}}},
        search=search, check=check)
    return module


def strict(params, result):
    cert = result["certificate"]
    require(result["holds"] is True, "holds")
    require(cert.get("squares") == [i * i for i in range(params["n"])], "squares")
    require(cert.get("bound") == Fraction(1, 2), "bound")
    require(result["summary"] == {"n": params["n"], "total": sum(cert["squares"])}, "summary")


def lax(params, result):
    # Checks each square it is given, but not completeness, holds or the summary.
    for i, v in enumerate(result["certificate"].get("squares", [])):
        require(v == i * i, "square")


def run(module, pinned="match"):
    result = module.search(module.PROBE["levels"]["smoke"])
    pin = digest(result["certificate"]) if pinned == "match" else pinned
    with mock.patch.object(attest.probes, "load", return_value=module), \
         mock.patch.object(attest.probes, "command", return_value="toy"), \
         mock.patch.object(attest, "code_digest", return_value="0" * 64), \
         mock.patch.object(attest, "lab_digest", return_value=pin):
        return attest.attest("toy", "smoke", 16)


class AttestTests(unittest.TestCase):
    def test_strict_checker_is_clean(self):
        rec = run(toy(strict))
        self.assertEqual(rec["status"], "clean", rec)
        self.assertEqual(rec["replay"], "match")
        self.assertEqual(rec["tally"]["survived"], 0)
        self.assertEqual(rec["regions"]["control"], {"tried": 2, "rejected": 2})

    def test_lax_checker_flags_controls_summary_as_weak(self):
        rec = run(toy(lax))
        self.assertEqual(rec["status"], "weak")
        self.assertIn("control_survived:holds_flip", rec["flags"])
        self.assertIn("control_survived:certificate_empty", rec["flags"])
        self.assertIn("unbound_summary", rec["flags"])
        self.assertTrue(all(s["path"] for s in rec["survivors"]))

    def test_replay_drift_fails_even_with_strict_checker(self):
        rec = run(toy(strict), pinned="f" * 64)
        self.assertEqual(rec["replay"], "drift")
        self.assertEqual(rec["status"], "broken")

    def test_unpinned_probe_needs_triage_not_fail(self):
        rec = run(toy(strict), pinned=None)
        self.assertEqual((rec["replay"], rec["status"]), ("unpinned", "triage"))

    def test_deterministic(self):
        self.assertEqual(json.dumps(run(toy(lax)), sort_keys=True),
                         json.dumps(run(toy(lax)), sort_keys=True))

    def test_crash_counts_as_rejection_and_timeout_is_not_swallowed(self):
        crashy_calls = {"n": 0}

        def sometimes_crash(params, result):
            crashy_calls["n"] += 1
            if crashy_calls["n"] > 1:
                raise KeyError("untyped")
            strict(params, result)
        rec = run(toy(sometimes_crash))
        self.assertEqual(rec["tally"]["survived"], 0)
        self.assertGreater(rec["tally"]["crashed"], 0)

        def stubborn(params, result):
            try:
                while True:
                    pass
            except Exception:  # must not swallow the alarm
                return
        module = toy(stubborn)
        self.assertEqual(attest.verdict(module, {"n": 1}, {}, 0.05), "timeout")

    def test_put_rebuilds_tuples_without_mutating_original(self):
        obj = {"a": (1, [2, 3])}
        out = attest.put({"a": (1, [2, 3])}, ("a", 1, 0), 9)
        self.assertEqual(out, {"a": (1, [9, 3])})
        self.assertEqual(obj, {"a": (1, [2, 3])})
        self.assertIsInstance(out["a"], tuple)

    def test_mutate_changes_every_supported_type(self):
        rng = random.Random(0)
        for value in (True, 0, 5, 1.5, Fraction(2, 3), "4/9", "17", "C2", [1, 2], (1, 2)):
            change = attest.mutate(value, rng)
            if change is not None:
                self.assertNotEqual(change[1], value, value)
        self.assertIsNone(attest.mutate(None, rng))

    def test_committed_ledger_matches_registry(self):
        doc = attest.load_ledger()
        for key, rec in doc["probes"].items():
            self.assertEqual(key, f"{rec['probe']}@{rec['level']}")
            self.assertIn(rec["status"], ("clean", "triage", "weak", "broken"))
            self.assertRegex(rec["code_sha256"], "^[0-9a-f]{64}$")
            # A probe edited after attestation is stale, not wrong: the weekly
            # `scripts/attest.py --check` job reports it without blocking unrelated PRs.


if __name__ == "__main__":
    unittest.main()
