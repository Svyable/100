#!/usr/bin/env python3
"""Rebuild Lean, audit exported theorem dependencies, emit commit-bound evidence.
No report from this tool promotes a portfolio entry or establishes novelty.
"""
import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"propext", "Quot.sound", "Classical.choice"}
NAME = re.compile(r"Hundred(?:\.[A-Za-z_][A-Za-z_0-9]*)+")


EXPORT = re.compile(
    r"^\s*(?:@\[[^\]\n]*\]\s*)*"
    r"(?P<modifiers>(?:(?:private|protected|noncomputable)\s+)*)"
    r"(?:theorem|lemma)\s+(?P<name>[A-Za-z_][A-Za-z_0-9'.]*)"
)


def mask_comments(source):
    """Mask Lean line and nested block comments, retaining line numbers."""
    chars = list(source)
    i = 0
    depth = 0
    while i < len(source):
        if depth:
            if source.startswith('/-', i):
                depth += 1
                chars[i:i + 2] = '  '
                i += 2
            elif source.startswith('-/', i):
                depth -= 1
                chars[i:i + 2] = '  '
                i += 2
            else:
                if chars[i] != '\n':
                    chars[i] = ' '
                i += 1
        elif source.startswith('/-', i):
            depth = 1
            chars[i:i + 2] = '  '
            i += 2
        elif source.startswith('--', i):
            while i < len(source) and source[i] != '\n':
                chars[i] = ' '
                i += 1
        elif source[i] == '"':
            # Do not interpret declaration-like lines within strings as theorems.
            chars[i] = ' '
            i += 1
            while i < len(source):
                if source[i] == '\\' and i + 1 < len(source):
                    chars[i:i + 2] = '  '
                    i += 2
                elif source[i] == '"':
                    chars[i] = ' '
                    i += 1
                    break
                else:
                    if chars[i] != '\n':
                        chars[i] = ' '
                    i += 1
        else:
            i += 1
    if depth:
        raise ValueError('unterminated Lean block comment')
    return ''.join(chars)


def discover_theorems(root):
    """Find public theorem/lemma exports for registry-completeness preflight.

    The kernel and #print axioms remain authoritative. This source-level guard
    catches ordinary newly exported theorems omitted from the audit registry.
    """
    found = {}
    for path in sorted((root / 'lean/Hundred').rglob('*.lean')):
        namespace = []
        source = mask_comments(path.read_text(encoding='utf-8'))
        for lineno, line in enumerate(source.splitlines(), 1):
            opened = re.match(r'^\s*namespace\s+([A-Za-z_][A-Za-z_0-9.]*)\s*$', line)
            closed = re.match(r'^\s*end\s+([A-Za-z_][A-Za-z_0-9.]*)\s*$', line)
            if opened:
                name = opened.group(1)
                namespace.append(name if not namespace or name.startswith('Hundred.')
                                 else namespace[-1] + '.' + name)
            elif closed:
                if namespace and closed.group(1) in (namespace[-1], namespace[-1].rsplit('.', 1)[-1]):
                    namespace.pop()
            else:
                theorem = EXPORT.match(line)
                if not theorem or 'private' in theorem.group('modifiers').split():
                    continue
                if not namespace:
                    raise ValueError(f'{path.relative_to(root)}:{lineno}: theorem outside a namespace')
                name = namespace[-1] + '.' + theorem.group('name')
                if name in found:
                    raise ValueError(f'duplicate Lean theorem {name}')
                found[name] = f'{path.relative_to(root)}:{lineno}'
    return found

def validate_registry(root=ROOT):
    rows = json.loads((root / "data/lean_targets.json").read_text())
    ids, declarations = set(), []
    problems = {p['id'] for p in json.loads((root / 'data/problems.json').read_text())}
    for row in rows:
        if row['id'] in ids or row['problem_id'] not in problems:
            raise ValueError('duplicate target or unknown problem')
        ids.add(row['id'])
        for field in ('statement', 'scope_gap', 'next_step'):
            if not row.get(field, '').strip():
                raise ValueError(f'missing {field}')
        if row['stage'] not in ('implemented', 'planned'):
            raise ValueError('stage is not compilation or review evidence')
        if row['stage'] == 'implemented' and not row['declarations']:
            raise ValueError('implemented target needs declarations')
        if row['stage'] == 'planned' and row['declarations']:
            raise ValueError('planned target cannot export declarations')
        for name in row['declarations']:
            if not NAME.fullmatch(name) or name in declarations:
                raise ValueError('invalid or duplicate declaration')
            declarations.append(name)
    if not declarations:
        raise ValueError('empty audit')
    exported = discover_theorems(root)
    unregistered = sorted(set(exported) - set(declarations))
    if unregistered:
        raise ValueError(f'unregistered Lean theorems: {unregistered}')
    not_exported = sorted(set(declarations) - set(exported))
    if not_exported:
        raise ValueError(f'audit registrations without exported theorem: {not_exported}')
    return declarations


def parse_axioms(output, expected):
    found = {}
    pattern = r"'([^']+)' (?:does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])"
    for match in re.finditer(pattern, output):
        name, raw = match.groups()
        if name in found:
            raise ValueError('duplicate axiom report')
        axioms = [x.strip() for x in (raw or '').split(',') if x.strip()]
        if set(axioms) - ALLOWED:
            raise ValueError(f'{name}: unapproved axioms {axioms}')
        found[name] = axioms
    if set(found) != set(expected):
        raise ValueError('missing or unexpected axiom reports')
    return found


def run(args, cwd):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=300)
    if result.returncode:
        raise RuntimeError(f'{args}:\n{result.stdout}\n{result.stderr}')
    return result.stdout + result.stderr


def verify(root=ROOT):
    work = root / 'lean'
    report = work / 'verification.json'
    report.unlink(missing_ok=True)  # A failed run must never leave a stale success.
    names = validate_registry(root)
    pinned = (work / 'lean-toolchain').read_text().strip()
    version = run(['lake', 'env', 'lean', '--version'], work)
    if not re.search(r"version " + re.escape(pinned.rsplit(':v', 1)[1]) + r"(?:,|\s)", version):
        raise ValueError('toolchain mismatch')
    timings = {}
    started = time.monotonic()
    run(['lake', 'build'], work)
    timings['lake build'] = round(time.monotonic() - started, 2)
    for path in sorted(work.glob('Hundred/**/*.lean')) + [work / 'Negative.lean']:
        started = time.monotonic()
        run(['lake', 'env', 'lean', '-DwarningAsError=true', str(path)], work)
        timings[str(path.relative_to(root))] = round(time.monotonic() - started, 2)
    # Wall time to a clean kernel check is a tracked metric (LEAN.md); the slowest
    # modules are printed so a budget overrun is attributable before it becomes a timeout.
    for name, secs in sorted(timings.items(), key=lambda kv: -kv[1])[:5]:
        print(f'{secs:8.2f}s  {name}')
    audit = work / 'Audit.lean'
    audit.write_text('import Hundred\n' + '\n'.join('#print axioms ' + n for n in names) + '\n')
    output = run(['lake', 'env', 'lean', '-DwarningAsError=true', str(audit)], work)
    (work / 'axioms.log').write_text(output)
    axioms = parse_axioms(output, names)
    paths = sorted(work.glob('Hundred/**/*.lean')) + [work / 'Hundred.lean', work / 'Negative.lean', work / 'lean-toolchain', work / 'lakefile.toml', root / 'data/lean_targets.json', root / 'scripts/lean_verify.py']
    hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    commit = run(['git', 'rev-parse', 'HEAD'], root).strip()
    dirty = bool(run(['git', 'status', '--porcelain', '--untracked-files=normal'], root).strip())
    report.write_text(json.dumps({'schema_version': 1, 'commit': commit, 'dirty': dirty,
        'toolchain': pinned, 'source_sha256': hashes, 'axioms': axioms,
        'result': 'kernel_checked', 'scope_review': 'pending', 'timings_seconds': timings,
        'portfolio_promotion': False}, indent=2) + '\n')
    print(f'Checked {len(names)} declarations; evidence: {report}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    if args.validate_only:
        print(f'Validated {len(validate_registry())} audit declarations (no Lean execution).')
    else:
        verify()
