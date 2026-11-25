"""Exercise the pinned Cogentic intake with the repository's Node runtime."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CogenticIntakeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node is required for intake controls")
    def test_manifest_and_controls(self):
        run = subprocess.run(
            ["node", str(ROOT / "scripts/cogentic_2026_intake.mjs")],
            cwd=ROOT, check=True, capture_output=True, text=True, timeout=30,
        )
        result = json.loads(run.stdout)
        self.assertEqual(result["papers"], 10)
        self.assertEqual(result["mutants_rejected"], 8)
        self.assertEqual(result["edge_control"], {
            "first_feasible_n": 2001,
            "edge_collision": True,
            "vertex_collision": False,
            "in_scope": False,
        })
