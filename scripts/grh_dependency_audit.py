#!/usr/bin/env python3
"""Validate the *scope* of the external RH/Dirichlet GRH consequence audit.

This is a dependency classification check, NOT a proof verifier. It cannot
certify the external Lean library, its mathematical statements or corollaries.
"""
import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "grh_dependency_audit.json"
PROBLEMS = ROOT / "data" / "problems.json"
VERIFIED = {"riemann", "dirichlet"}
UNCOVERED = {"dedekind", "hecke", "artin", "automorphic"}
FAMILIES = VERIFIED | UNCOVERED | {"unresolved"}
TRIAGE = {"eligible_audit", "needs_theorem_matching", "blocked_stronger_family"}
TARGETS = {"M001": ("riemann", "riemannHypothesis"),
           "M002": ("dirichlet", "LFunction_eq_zero_re")}


class ScopeError(ValueError):
    """An audit record claims more than its supporting evidence allows."""


def _https(url):
    return isinstance(url, str) and urlparse(url).scheme == "https" and bool(urlparse(url).hostname)


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate(audit, problems=None):
    if not isinstance(audit, dict) or audit.get("schema_version") != 1:
        raise ScopeError("expected schema_version 1")
    try:
        date.fromisoformat(audit["as_of"])
    except (KeyError, TypeError, ValueError):
        raise ScopeError("as_of must be an ISO date") from None
    for source in ("source_lean", "source_mit"):
        if not _https(audit.get(source)):
            raise ScopeError(f"{source} must be a primary HTTPS URL")
    if set(audit.get("verified_families", [])) != VERIFIED:
        raise ScopeError("certification covers exactly RH and Dirichlet GRH in this snapshot")
    if set(audit.get("other_families_not_covered", [])) != UNCOVERED:
        raise ScopeError("must explicitly exclude broader L-function families")
    if audit.get("project_replayed") is not False or audit.get("project_independently_reviewed") is not False:
        raise ScopeError("do not self-attest proof replay or independent acceptance")
    targets = audit.get("active_targets")
    if not isinstance(targets, list) or len(targets) != len(TARGETS):
        raise ScopeError("must inventory M001 and M002 exactly once")
    seen = set()
    for item in targets:
        if not isinstance(item, dict):
            raise ScopeError("target must be an object")
        target_id = item.get("id")
        if target_id not in TARGETS or target_id in seen:
            raise ScopeError("unexpected or duplicate active target")
        seen.add(target_id)
        if (item.get("requires_family"), item.get("external_theorem")) != TARGETS[target_id]:
            raise ScopeError("target theorem or L-function family mismatch")
        if item.get("scope_relation") != "matches_as_reported" or item.get("project_status") != "pending_scope_audit":
            raise ScopeError("this external match is not independent Project 100 acceptance")
    if seen != set(TARGETS):
        raise ScopeError("M001/M002 missing")
    if problems is not None:
        by_id = {entry["id"]: entry for entry in problems}
        if ("Riemann zeta" not in by_id["M001"]["question"] or
                "Dirichlet L-function" not in by_id["M002"]["question"]):
            raise ScopeError("active registry no longer has the audited theorem scope")
    claims = audit.get("consequences")
    if not isinstance(claims, list) or not claims:
        raise ScopeError("consequences must be a nonempty list")
    seen_claims = set()
    for claim in claims:
        if not isinstance(claim, dict):
            raise ScopeError("consequence must be an object")
        claim_id = claim.get("id")
        if not _nonempty(claim_id) or claim_id in seen_claims:
            raise ScopeError("missing or duplicate consequence ID")
        seen_claims.add(claim_id)
        if not _nonempty(claim.get("topic")) or not _nonempty(claim.get("next_test")):
            raise ScopeError(f"{claim_id}: topic and bounded next test required")
        family, triage = claim.get("requires_family"), claim.get("triage")
        if family not in FAMILIES or triage not in TRIAGE:
            raise ScopeError(f"{claim_id}: invalid family or triage")
        if family in UNCOVERED and triage != "blocked_stronger_family":
            raise ScopeError(f"{claim_id}: stronger L-function family is not certified")
        if family == "unresolved" and triage != "needs_theorem_matching":
            raise ScopeError(f"{claim_id}: exact theorem dependency unknown")
        if triage == "eligible_audit" and family not in VERIFIED:
            raise ScopeError(f"{claim_id}: cannot audit as eligible under this proof")
        if triage == "blocked_stronger_family" and family not in UNCOVERED:
            raise ScopeError(f"{claim_id}: blocked flag requires a named stronger family")
    return Counter(claim["triage"] for claim in claims)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable triage counts")
    args = parser.parse_args()
    try:
        audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        problems = json.loads(PROBLEMS.read_text(encoding="utf-8"))
        counts = validate(audit, problems)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    result = {"count": sum(counts.values()),
              "eligible_audit": counts["eligible_audit"],
              "needs_theorem_matching": counts["needs_theorem_matching"],
              "blocked_stronger_family": counts["blocked_stronger_family"],
              "project_proof_verified": False}
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print("GRH scope classification valid (not a proof check):", result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
