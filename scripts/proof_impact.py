#!/usr/bin/env python3
"""Read-only, structural counterfactuals over the validated obligation DAG.

A hypothetical discharge is NOT a proof, a review, or a claim reservation.
No dependent is automatically discharged and external gates remain blocked.
"""
import argparse
import json


def analyze(entries):
    """Return deterministic impact rows for already validated obligations."""
    by_id = {item['id']: item for item in entries}
    done = {oid for oid, item in by_id.items() if item['status'] == 'discharged'}
    children = {oid: set() for oid in by_id}
    for oid, item in by_id.items():
        for dep in item['depends_on']:
            children[dep].add(oid)

    def missing(oid, closed):
        return set(by_id[oid]['depends_on']) - closed

    def state(oid, closed):
        if oid in closed:
            return 'discharged'
        if missing(oid, closed):
            return 'waiting_on_dependencies'
        if by_id[oid]['status'] == 'blocked':
            return 'externally_blocked'
        return 'runnable'

    def descendants(oid):
        seen, pending = set(), list(children[oid])
        while pending:
            child = pending.pop()
            if child not in seen:
                seen.add(child)
                pending.extend(children[child] - seen)
        return sorted(seen - done)

    def upstream(oid):
        seen, pending = set(), list(missing(oid, done))
        while pending:
            dep = pending.pop()
            if dep not in seen:
                seen.add(dep)
                pending.extend(missing(dep, done) - seen)
        return sorted(seen)

    rows = []
    for oid in sorted(by_id):
        current = state(oid, done)
        direct = sorted(children[oid] - done)
        last = [child for child in direct if missing(child, done) == {oid}]
        # Only a currently runnable item gets a single-discharge simulation.
        # No hypothetical change to the original input or its evidence.
        hypothetical = done | {oid} if current == 'runnable' else None
        changes = None if hypothetical is None else {
            'newly_runnable': [child for child in last if state(child, hypothetical) == 'runnable'],
            'newly_external_blocked': [child for child in last if state(child, hypothetical) == 'externally_blocked'],
        }
        rows.append({
            'id': oid, 'problem_id': by_id[oid]['problem_id'], 'category': current,
            'unmet': sorted(missing(oid, done)), 'unmet_ancestors': upstream(oid),
            'direct_dependents': direct, 'downstream_open': descendants(oid),
            'last_missing_for': last, 'if_discharged': changes,
        })
    return rows


def main():
    import proof_obligations

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--id', help='Show one obligation')
    parser.add_argument('--json', action='store_true', help='Emit machine-readable impact rows')
    args = parser.parse_args()
    rows = analyze(proof_obligations.load())
    if args.id:
        rows = [row for row in rows if row['id'] == args.id]
        if not rows:
            parser.error('Unknown obligation: ' + args.id)
    else:
        rows.sort(key=lambda row: (
            row['category'] != 'runnable',
            -len((row['if_discharged'] or {}).get('newly_runnable', [])),
            -len(row['downstream_open']), row['id']))
    if args.json:
        print(json.dumps({'boundary': 'Structural hypothetical only; not proof or claim availability.',
                          'obligations': rows}, indent=2))
    else:
        print('Structural hypothetical only; not proof or claim availability.')
        for row in rows:
            print(f"{row['id']} [{row['category']}] | downstream open: {len(row['downstream_open'])}")
            print('  unmet ancestors: ' + (', '.join(row['unmet_ancestors']) or 'none'))
            print('  last missing for: ' + (', '.join(row['last_missing_for']) or 'none'))
            impact = row['if_discharged']
            if impact is not None:
                print('  newly runnable: ' + (', '.join(impact['newly_runnable']) or 'none'))
                print('  still externally blocked: ' + (', '.join(impact['newly_external_blocked']) or 'none'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
