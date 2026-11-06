#!/usr/bin/env python3
"""Optional reproduction of seven CaDiCaL/DRAT-to-LRAT proof artifacts.

Requires python-sat (CaDiCaL195) and a compiled drat-trim executable.
Outputs into a user-chosen directory; never overwrites committed artifacts.
The standard-library checker is scripts/ch9_three_low.py.
"""

import argparse
import gzip
import hashlib
import subprocess
from pathlib import Path

from scripts.ch9_three_low import CERT_SHA256, dimacs, formula


def regenerate(output_dir, drat_trim):
    from pysat.solvers import Solver  # optional, not required for CI

    output_dir.mkdir(parents=True, exist_ok=True)
    for case in CERT_SHA256:
        clauses = formula(case)
        prefix = output_dir / case
        cnf = prefix.with_suffix('.cnf')
        drat = prefix.with_suffix('.drat')
        lrat = prefix.with_suffix('.lrat')
        cnf.write_text(dimacs(clauses), encoding='ascii')
        with Solver(name='cadical195', bootstrap_with=clauses,
                    with_proof=True) as solver:
            if solver.solve():
                raise ValueError(f'Unexpected SAT instance: {case}')
            drat.write_text('\n'.join(solver.get_proof()) + '\n',
                            encoding='ascii')
        subprocess.run([str(drat_trim), str(cnf), str(drat), '-L', str(lrat)],
                       check=True, capture_output=True, text=True)
        compressed = gzip.compress(lrat.read_bytes(), compresslevel=9, mtime=0)
        digest = hashlib.sha256(compressed).hexdigest()
        prefix.with_suffix('.lrat.gz').write_bytes(compressed)
        print(case, 'sha256', digest,
              'MATCH' if digest == CERT_SHA256[case] else 'DIFF')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--drat-trim', required=True, type=Path)
    args = parser.parse_args()
    regenerate(args.output_dir, args.drat_trim.resolve())


if __name__ == '__main__':
    main()
