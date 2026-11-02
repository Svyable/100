"""Exact relaxed integer-profile falsifier for CH(27,9) z=0 five-low obstruction.

No SAT/MILP inference is used. This audits necessary degree tuples, not graphs.
Proof: research/M074_Z0_FIVE_LOW.md.
"""
import argparse
import json
from collections import Counter
from itertools import combinations_with_replacement

SCOPE = ('X-M074-Z0-ROOT-v1: For a hypothetical oriented directed-triangle-free '
         '27-vertex nine-outregular graph at an indegree-ten root with A=N+(v), '
         'B=N-(v), C nonneighbors and every b in B receiving an arc from C (z=0), '
         'derive a new exact necessary obstruction or explicit counterexample to a '
         'proposed strengthening, using root incidence, global indegree deficits, '
         'independent integer enumeration and literal graph controls; compare with '
         'existing CH27 lemmas and primary literature, without claiming the full '
         'finite case.')
SCOPE_SHA256 = '1885916a20816601272789f54ca2cc3e538a45c04ccccd7b3e5a579fe4fe3ed6'


def alpha_profiles():
    """Sorted nine-tuples with exactly five 2s, four entries >=3, sum <=29."""
    for tail in combinations_with_replacement(range(3, 9), 4):
        a = (2,) * 5 + tail
        if sum(a) <= 29:
            yield a


def k_profiles():
    """Sorted positive C->B indegree ten-tuples (z=0)."""
    yield from combinations_with_replacement(range(1, 8), 10)


def reject_reason(a, k):
    """Necessary gates. None is a proof gap, NOT a constructed counterexample."""
    assert len(a) == 9 and a.count(2) == 5 and sum(a) <= 29
    assert len(k) == 10 and min(k) >= 1 and max(k) <= 7
    m, K = sum(a), sum(k)
    # Missing A-C pairs: M>=m-19, K>=92-2m+M>=73-m.
    if K < 73 - m:
        return 'missing_pair_lower_cut'
    # Five alpha=2 vertices have indegree<=5, forcing >=20 high vertices,
    # including >=8 of B. A high B vertex needs >=2 eligible A targets.
    s = a[-2]
    assert s <= 6
    b_high_needed = 8
    if s == 6:
        assert 3 in a
        # K>=44 implies <=4 k=1; each alpha=3 has ambient indegree<=9.
        assert K >= 44 and k.count(1) <= 4
        b_high_needed = 9
    if sum(x <= s - 2 for x in k) < b_high_needed:
        return 'high_B_eligibility'
    return None


def audit():
    counts = Counter()
    alphas = list(alpha_profiles())
    ks = list(k_profiles())
    for a in alphas:
        for k in ks:
            counts[reject_reason(a, k) or 'unresolved'] += 1
    return {
        'alpha_profiles': len(alphas),
        'positive_k_profiles': len(ks),
        'total_relaxed_pairs': len(alphas) * len(ks),
        'sequential_rejections': dict(sorted(counts.items())),
        'unresolved': counts['unresolved'],
        'boundary': 'Only z=0, t=5 degree tuples; not a 27-vertex graph census',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    result = audit()
    if args.check:
        import hashlib
        assert hashlib.sha256(SCOPE.encode()).hexdigest() == SCOPE_SHA256
        assert result['alpha_profiles'] == 35
        assert result['positive_k_profiles'] == 8008
        assert result['total_relaxed_pairs'] == 280280
        assert result['sequential_rejections'] == {
            'high_B_eligibility': 79791,
            'missing_pair_lower_cut': 200489,
        }
        assert result['unresolved'] == 0
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)


if __name__ == '__main__':
    main()
