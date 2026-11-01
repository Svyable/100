#!/usr/bin/env python3
"""Fail-closed CH SAT artifact gate. A solver verdict alone is never a proof."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "regular": ("ch_regularity.py", "16448ff34866b74e7b98ea38e599841363503de88590eca564ae29e2b9891d35"),
    "pivot": ("ch_pivot.py", "18f4a672b3294b59202f4656641d361e8e2ca6b9fc63af7a823ee85108825fff"),
}

def check(target, proof, checker):
    script, expected = TARGETS[target]
    if not proof.is_file() or not checker.is_file():
        raise ValueError("proof and checker must be existing files")
    with tempfile.TemporaryDirectory() as tmp:
        cnf = Path(tmp) / "instance.cnf"
        subprocess.run([sys.executable, str(ROOT / "scripts" / script),
                        "--output", str(cnf)], check=True, capture_output=True)
        actual = hashlib.sha256(cnf.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("CNF hash mismatch; refusing certificate")
        # The trusted checker must accept: CHECKER CNF PROOF and return 0
        # only after validating an UNSAT proof. Never parse solver stdout
        # or accept a bare UNSAT label as evidence.
        result = subprocess.run([str(checker.resolve()), str(cnf), str(proof.resolve())],
                                capture_output=True, text=True)
        if result.returncode:
            raise ValueError("independent proof checker rejected certificate")
        return {"target": target, "cnf_sha256": actual,
                "proof_sha256": hashlib.sha256(proof.read_bytes()).hexdigest(),
                "checker": str(checker.resolve()), "checker_exit_code": 0,
                "note": "Checker exit status only; checker trust and proof format require audit"}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target", choices=TARGETS, required=True)
    p.add_argument("--proof", type=Path, required=True)
    p.add_argument("--checker", type=Path, required=True)
    a = p.parse_args()
    try:
        print(json.dumps(check(a.target, a.proof, a.checker), indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as e:
        p.exit(1, f"NOT CERTIFIED: {e}\n")

if __name__ == "__main__":
    main()
