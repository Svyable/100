# Top 100 portfolio selection and admission

**First screening: October 31, 2026. The active 100, scores and proof statuses remain unchanged.**

The [screening ledger](../data/portfolio_triage.json) flags 15 entries and
names five alternatives. Flags are editorial hypotheses, **not conclusions**:
unflagged does not mean verified, and a candidate source link does not mean an
independent current open-status audit is complete. Check the ledger with
`python3 scripts/portfolio_triage.py --check`.

## Keep three decisions separate

1. **Membership** asks if a well-defined open problem is sufficiently
   consequential and distinctive to deserve one of 100 scarce slots.
   Prestige is relevant, but breadth of mathematical impact, distinctness,
   and method transfer matter. Do not automatically exclude hard problems.
2. **Execution** asks which targets can support reproducible useful work now.
   The existing [execution queue](../ATTACK_QUEUE.md) correctly rewards
   working campaigns and independent exact checkers.
3. **Evidence** asks whether the precise statement remains open. Compare
   the newest primary specialist literature against claimed resolutions.
   Preprint postings, formal-statement compilers and independent mathematical
   acceptance are different levels of evidence.

The current [weighted ranking](../RANKED.md) devotes 30% to attackability.
It is an editorial *work-priority* heuristic, not an authoritative ordering
of the 100 greatest unsolved theorems. Do not silently rewrite scores.

## Review outcomes and gates

| Screening action | Meaning | Evidence required |
|---|---|---|
| respecify | Current statement is too broad or ambiguous | Specialist theorem, quantifiers, hypotheses, exact open remainder |
| consolidation_review | Target overlaps another entry | Exact implication map, distinct attacks, value of keeping a focused subcase |
| compare_candidates | Another target might create greater portfolio value | Side-by-side mathematical impact, methods, costs and status audit |
| audit_claim | An external manuscript may resolve the target | Exact theorem-scope match, independent proof/dependency and specialist reviews |

A candidate is *not* admission-ready until it has: (1) an exact falsifiable
statement; (2) a dated contemporary **primary specialist** source establishing
the still-open remainder, plus a search for later claims; (3) a distinctness
and implication map against the active 100; (4) a realistic first lemma or
certificate with explicit verification cost; and (5) a dated, source-backed
replacement comparison in a PR.

Never replace a problem solely because it is difficult or because an
unreviewed paper claims a proof. A **full accepted resolution** requires
the stronger [Solved archive rules](RESEARCH_ENGINE.md). A duplicate,
underspecified target or deprioritized target is not a solved problem.
Stable IDs and prior campaign history must be preserved.

## Next audit passes, in order

1. **Statement fidelity:** M017, M053, M056, M063, M070.
2. **Claim resolution watch:** M038, M058, M062, M066, M069;
   reconcile with the [existing 2026 claim reviews](../research/CLAIM_REVIEWS_2026.md).
3. **Overlap and inclusion tradeoffs:** M018 with M007, M041 with M042,
   and M019/M096 against the intake candidates.
4. **Outside admissions:** Independently audit the five source leads in
   the screening ledger; none is currently certified admission-ready.
5. **One-for-one decisions:** Only after the evidence packets exist,
   propose actual promotions/retirements, update scripts and preserve IDs.

CI can validate schema, source leads and review discipline. It **cannot**
judge theorem truth, specialist independence, or the complete 2026 literature.
