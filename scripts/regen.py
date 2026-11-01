#!/usr/bin/env python3
"""Regenerate every derived artifact from its sources, in dependency order.

    python3 scripts/regen.py           # rewrite all generated files (~3 s)
    python3 scripts/regen.py --check   # fail if any generated file is stale or any ledger invalid
    python3 scripts/regen.py --check --fast   # skip checks that recompute certificates (lab probes)
    python3 scripts/regen.py --list    # print the generated paths

Generated files conflict on almost every concurrent PR. They never need a manual
merge: take either side (`git checkout --theirs -- <paths>`), run this script,
then commit. Certificate ledgers (lab, mines, McKay, Frankl orbit counts) are
recomputed only by their own tools; this script re-renders and re-checks them.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SLOW_CHECKS = {"lab.py"}  # reruns every probe (~1 min); CI always runs it

# (write command, check command, outputs). Order matters: the site reads the rest.
STEPS = (
    (["rank.py"], ["rank.py", "--check"], ["RANKED.md"]),
    (["research.py"], ["research.py", "--check"], ["ATTACK_QUEUE.md"]),
    (["lab.py", "--render"], ["lab.py", "--check"], ["LAB.md"]),
    (["mine.py"], ["mine.py", "--check"], ["MINES.md", "data/mine_results.json"]),
    (["approach.py"], ["approach.py", "--check"], ["APPROACH.md"]),
    (["roadmap.py"], ["roadmap.py", "--check"], ["ROADMAP.md"]),
    (["next.py"], ["next.py", "--check"], ["docs/data/next.json"]),
    (None, ["portfolio_triage.py", "--check"], []),
    (None, ["proof_obligations.py", "--check"], []),
    (None, ["formal.py", "--check"], []),
    (None, ["lean_verify.py", "--validate-only"], []),
    (None, ["work.py", "--check"], []),
    (["scale.py", "--write"], ["scale.py", "--check"], ["SCALE.md"]),
    (["build_site.py"], ["build_site.py", "--check"],
     ["docs/ (everything except docs/assets, docs/next, docs/*.md, docs/.nojekyll)"]),
)


def run(args):
    started = time.monotonic()
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / args[0]), *args[1:]],
                            cwd=ROOT, text=True, capture_output=True)
    return result, time.monotonic() - started


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--fast", action="store_true", help="with --check, skip certificate recomputation")
    opts = parser.parse_args()
    if opts.list:
        for _, _, outputs in STEPS:
            for path in outputs:
                print(path)
        return 0
    failed = []
    for write, check, _ in STEPS:
        args = check if opts.check else write
        if args is None or (opts.check and opts.fast and args[0] in SLOW_CHECKS):
            continue
        result, secs = run(args)
        line = (result.stdout.strip() or result.stderr.strip()).splitlines()
        status = "ok " if result.returncode == 0 else "FAIL"
        print(f"{status} {secs:5.2f}s  {' '.join(args):38s} {line[-1][:90] if line else ''}")
        if result.returncode:
            failed.append((args, result))
    for args, result in failed:
        print(f"\n--- {' '.join(args)} ---\n{result.stdout}{result.stderr}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
