#!/usr/bin/env python3
"""Lamport-style proof-obligation DAG: schema, scope and closure safety gates.

This is a structural gate, NOT a theorem prover. Passing it cannot establish
mathematical validity, independence of reviews, or originality.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "proof_obligations.json"
KINDS = {"scope", "reduction", "lemma", "witness"}
STATES = {"open", "blocked", "discharged"}
FIELDS = {
    "id", "problem_id", "kind", "statement", "prior_art_boundary",
    "falsifier", "next_action", "depends_on", "status", "evidence",
}
EVIDENCE_FIELDS = {
    "statement_sha256", "artifact", "checker", "scope_audit",
    "independent_review_urls",
}


def _inside(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("Evidence path must be nonempty and relative")
    path = Path(relative)
    if ".." in path.parts or not (root / path).is_file():
        raise ValueError("Evidence path missing or escapes repository: " + relative)
    return path


def validate(ledger, root=ROOT):
    """Return obligations after validating references, DAG and evidence closure."""
    if not isinstance(ledger, dict) or set(ledger) != {"version", "obligations"}:
        raise ValueError("Invalid obligation ledger shape")
    if type(ledger["version"]) is not int or ledger["version"] != 1:
        raise ValueError("Unsupported obligation ledger version")
    entries = ledger["obligations"]
    if not isinstance(entries, list):
        raise ValueError("Obligations must be a list")

    registry = json.loads((root / "data" / "problems.json").read_text(encoding="utf-8"))
    research = json.loads((root / "data" / "research_program.json").read_text(encoding="utf-8"))
    valid_ids = {record["id"] for record in registry}
    campaign_ids = {campaign["problem_id"] for campaign in research["campaigns"]}
    seen = {}
    for item in entries:
        if not isinstance(item, dict) or set(item) != FIELDS:
            raise ValueError("Obligation has missing or unknown fields")
        oid, pid = item["id"], item["problem_id"]
        if not isinstance(oid, str) or not isinstance(pid, str):
            raise ValueError("Obligation ID and problem ID must be strings")
        if not re.fullmatch(r"O-M\d{3}-\d{2}", oid) or not oid.startswith("O-" + pid + "-"):
            raise ValueError("Obligation ID must bind to its exact problem: " + oid)
        if oid in seen or pid not in valid_ids or pid not in campaign_ids:
            raise ValueError("Duplicate obligation or missing active campaign: " + oid)
        if item["kind"] not in KINDS or item["status"] not in STATES:
            raise ValueError("Invalid kind or status: " + oid)
        for field in ("statement", "prior_art_boundary", "falsifier", "next_action"):
            if not isinstance(item[field], str) or not item[field].strip():
                raise ValueError("Missing falsifiable statement/boundary/action: " + oid)
        deps = item["depends_on"]
        if (not isinstance(deps, list) or not all(isinstance(x, str) for x in deps)
                or len(set(deps)) != len(deps) or oid in deps):
            raise ValueError("Invalid dependency list: " + oid)

        evidence = item["evidence"]
        if item["status"] != "discharged":
            if evidence is not None:
                raise ValueError("Unclosed obligation cannot claim evidence: " + oid)
        else:
            if not isinstance(evidence, dict) or set(evidence) != EVIDENCE_FIELDS:
                raise ValueError("Discharge requires exact evidence fields: " + oid)
            digest = hashlib.sha256(item["statement"].encode("utf-8")).hexdigest()
            if evidence["statement_sha256"] != digest:
                raise ValueError("Proof evidence bound to different statement: " + oid)
            for field in ("artifact", "checker", "scope_audit"):
                _inside(root, evidence[field])
            reviews = evidence["independent_review_urls"]
            if not isinstance(reviews, list) or len(reviews) < 2:
                raise ValueError("Discharge needs two independent reviews: " + oid)
            hosts = []
            for link in reviews:
                if not isinstance(link, str):
                    raise ValueError("Invalid review URL: " + oid)
                uri = urlparse(link)
                if uri.scheme != "https" or not uri.hostname:
                    raise ValueError("Reviews must be HTTPS URLs: " + oid)
                hosts.append(uri.hostname.lower())
            if len(set(hosts)) < 2:
                raise ValueError("Reviews must come from distinct domains: " + oid)
        seen[oid] = item

    visiting, visited = set(), set()

    def walk(oid):
        if oid in visiting:
            raise ValueError("Cyclic proof dependency: " + oid)
        if oid in visited:
            return
        visiting.add(oid)
        item = seen[oid]
        for dep in item["depends_on"]:
            if dep not in seen:
                raise ValueError("Unknown proof dependency: " + dep)
            walk(dep)
            if item["status"] == "discharged" and seen[dep]["status"] != "discharged":
                raise ValueError("Discharge depends on an open proof obligation: " + oid)
        visiting.remove(oid)
        visited.add(oid)

    for oid in seen:
        walk(oid)

    # A novel restricted result may not be promoted without a scoped, discharged
    # lemma node. This reinforces, but does not replace, research.py's review gate.
    promoted = {
        mark["problem_id"] for mark in research["milestones"]
        if mark["classification"] == "restricted_verified"
    }
    for pid in promoted:
        if not any(item["problem_id"] == pid and item["kind"] == "lemma"
                   and item["status"] == "discharged" for item in entries):
            raise ValueError("Restricted result lacks discharged lemma: " + pid)

    return entries


def load(path=LEDGER, root=ROOT):
    return validate(json.loads(Path(path).read_text(encoding="utf-8")), root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate and exit")
    args = parser.parse_args()
    items = load()
    if not args.check:
        for item in items:
            print(item["id"] + " [" + item["status"] + "] " + item["statement"])
    print("Validated " + str(len(items)) + " exact proof obligations")


if __name__ == "__main__":
    main()
