#!/usr/bin/env python3
"""Fail-closed, single-writer admission and slot planner for Project 100.

This is the control plane, not an executor: no model, shell, issue or PR is
launched by this script. Admission uses a recently fetched *complete* GitHub
open-issues snapshot and the repository's current derived work contracts.
"""
import argparse
import fcntl
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROTOCOL = "svyable.router.v1"
REPOSITORY = "Svyable/100"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
CLAIM = re.compile(r"^\[Claim\] ([A-Za-z0-9_-]+)(?:\s|$)")
SCOPE = re.compile(r"(?im)^\s*(?:scope(?:_sha256)?(?:\s+digest)?|digest)\s*:\s*\x60?([0-9a-f]{64})\b")
OCCUPY = {"reserved", "running", "quarantined"}
STAGES = OCCUPY | {"needs_human", "ended"}
TRANSITIONS = {
    "reserved": {"running", "needs_human", "ended"},
    "running": {"needs_human", "ended"},
    "needs_human": {"running", "ended"},
    "quarantined": {"ended"},
    "ended": set(),
}


def _date(value):
    if not isinstance(value, str):
        raise ValueError("Snapshot missing fetched_at")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("Invalid fetched_at") from None
    if result.utcoffset() is None:
        raise ValueError("Snapshot timestamp must include UTC offset")
    return result.astimezone(timezone.utc)


def checked_snapshot(snapshot, now):
    if (not isinstance(snapshot, dict) or snapshot.get("repository") != REPOSITORY
            or snapshot.get("complete") is not True or not isinstance(snapshot.get("issues"), list)):
        raise ValueError("Require a complete, repository-scoped open-issues snapshot")
    age = (now - _date(snapshot.get("fetched_at"))).total_seconds()
    if not -30 <= age <= 600:
        raise ValueError("Missing, future or stale GitHub claims snapshot")
    numbers = set()
    for issue in snapshot["issues"]:
        if not isinstance(issue, dict) or type(issue.get("number")) is not int or issue["number"] <= 0:
            raise ValueError("Malformed GitHub issue in snapshot")
        if issue["number"] in numbers:
            raise ValueError("Duplicate issue number in claims snapshot")
        numbers.add(issue["number"])
        if issue.get("state") != "open":
            raise ValueError("Snapshot must contain only open issues")
    return snapshot["issues"]


def checked_state(state):
    if not isinstance(state, dict) or state.get("protocol") != PROTOCOL or not isinstance(state.get("tickets"), list):
        raise ValueError("Invalid router state; explicit initialized state required")
    seen_ids, seen_claims, seen_work = set(), set(), set()
    for t in state["tickets"]:
        if (not isinstance(t, dict) or not isinstance(t.get("ticket_id"), str)
                or not isinstance(t.get("work_id"), str)
                or type(t.get("claim_number")) is not int or t["claim_number"] <= 0
                or not isinstance(t.get("scope_sha256"), str)
                or not HEX64.fullmatch(t["scope_sha256"])
                or t.get("status") not in STAGES):
            raise ValueError("Invalid ticket record")
        if t["ticket_id"] in seen_ids or t["claim_number"] in seen_claims:
            raise ValueError("Duplicate active ticket identity")
        seen_ids.add(t["ticket_id"])
        seen_claims.add(t["claim_number"])
        if t["status"] != "ended":
            if t["work_id"] in seen_work:
                raise ValueError("Two live tickets for the same work item")
            seen_work.add(t["work_id"])
    return [dict(t) for t in state["tickets"]]


def claim_scope(issue):
    if "pull_request" in issue or not isinstance(issue.get("title"), str):
        return None
    m = CLAIM.match(issue["title"])
    if not m:
        return None
    body = issue.get("body")
    found = SCOPE.findall(body if isinstance(body, str) else "")
    # Distinct multiple digests must not be silently resolved by choosing one.
    digest = found[0] if len(found) == 1 else None
    return m.group(1), digest


def plan(work_items, claims_snapshot, state, reports=(), events=(), max_workers=3, now=None):
    """Return reservable ticket mandates; only a separate executor runs workers.

    No claim is created here. A slot is never freed on a stale or missing issue;
    it stays quarantined until an explicit terminal report is recorded.
    """
    now = now or datetime.now(timezone.utc)
    if type(max_workers) is not int or not 1 <= max_workers <= 100:
        raise ValueError("max_workers must be an integer from 1 to 100")
    issues = checked_snapshot(claims_snapshot, now)
    tickets = checked_state(state)
    work = {}
    for item in work_items:
        if (not isinstance(item, dict) or not isinstance(item.get("id"), str)
                or item["id"] in work or not isinstance(item.get("scope_sha256"), str)
                or not HEX64.fullmatch(item["scope_sha256"])):
            raise ValueError("Duplicate or malformed derived work contract")
        work[item["id"]] = item
    by_ticket = {t["ticket_id"]: t for t in tickets}
    for report in reports:
        if not isinstance(report, dict) or set(report) != {"ticket_id", "status"}:
            raise ValueError("Report requires ticket_id and status only")
        t = by_ticket.get(report["ticket_id"])
        if t is None or report["status"] not in TRANSITIONS[t["status"]]:
            raise ValueError("Unknown ticket or forbidden status transition")
        t["status"] = report["status"]
    claim_groups = {}
    issue_by_number = {i["number"]: i for i in issues}
    for issue in issues:
        spec = claim_scope(issue)
        if spec:
            wid, digest = spec
            claim_groups.setdefault(wid, []).append((issue, digest))
    decisions, actions = [], []
    for t in tickets:
        issue = issue_by_number.get(t["claim_number"])
        group = claim_groups.get(t["work_id"], [])
        valid = (issue is not None and len(group) == 1 and group[0][0]["number"] == t["claim_number"]
                 and group[0][1] == t["scope_sha256"]
                 and t["work_id"] in work and work[t["work_id"]]["status"] == "runnable"
                 and work[t["work_id"]]["scope_sha256"] == t["scope_sha256"])
        if not valid and t["status"] in ("reserved", "running", "needs_human"):
            t["status"] = "quarantined"
            actions.append({"action": "operator_stop_required", "ticket_id": t["ticket_id"],
                            "reason": "claim closed, duplicated, changed scope or work no longer runnable"})
    used = sum(t["status"] in OCCUPY for t in tickets)
    by_work = {t["work_id"]: t for t in tickets if t["status"] != "ended"}
    for wid, item in work.items():
        group = claim_groups.get(wid, [])
        if not group:
            continue  # unclaimed work never becomes an assignment
        if len(group) > 1:
            decisions.append({"work_id": wid, "decision": "refuse", "reason": "duplicate_open_claims"})
            continue
        issue, digest = group[0]
        if digest != item["scope_sha256"]:
            decisions.append({"work_id": wid, "decision": "refuse", "reason": "missing_or_stale_scope_digest"})
            continue
        if item.get("status") != "runnable":
            decisions.append({"work_id": wid, "decision": "refuse", "reason": "work_not_runnable"})
            continue
        if wid in by_work:
            decisions.append({"work_id": wid, "decision": "owned", "reason": by_work[wid]["status"]})
            continue
        # An ended claim cannot be relaunched by merely re-running the router.
        if any(t["claim_number"] == issue["number"] for t in tickets):
            decisions.append({"work_id": wid, "decision": "refuse", "reason": "claim_already_ended"})
            continue
        if used >= max_workers:
            decisions.append({"work_id": wid, "decision": "queued", "reason": "worker_slots_full"})
            continue
        ticket_id = f"{wid}:{issue['number']}:{digest[:12]}"
        ticket = {"ticket_id": ticket_id, "work_id": wid, "claim_number": issue["number"],
                  "scope_sha256": digest, "status": "reserved"}
        tickets.append(ticket)
        by_work[wid] = ticket
        used += 1
        decisions.append({"work_id": wid, "decision": "reserved", "reason": "verified_single_claim"})
        actions.append({"action": "prepare_worker", "ticket_id": ticket_id,
                        "claim_number": issue["number"], "mandate": {
                            "work_id": wid, "scope_sha256": digest,
                            "deliverable": item["deliverable"], "acceptance": item["acceptance"],
                            "boundary": item["boundary"], "falsifier": item.get("falsifier", ""),
                            "instructions": "Work only within this contract. Follow AGENTS.md, regenerate, run checks; never self-accept mathematical claims."}})
    # Human comments stay with the Ticket owning the claim, not a new task.
    seen_events = set()
    for event in events:
        if (not isinstance(event, dict) or set(event) != {"type", "issue_number", "comment_id"}
                or event["type"] != "issue_comment" or type(event["issue_number"]) is not int
                or type(event["comment_id"]) is not int or event["comment_id"] <= 0):
            raise ValueError("Malformed follow-up event")
        if event["comment_id"] in seen_events:
            continue
        seen_events.add(event["comment_id"])
        owned = next((t for t in tickets if t["claim_number"] == event["issue_number"]
                      and t["status"] in ("reserved", "running", "needs_human")), None)
        if owned:
            actions.append({"action": "relay_followup", "ticket_id": owned["ticket_id"],
                            "comment_id": event["comment_id"]})
        else:
            actions.append({"action": "operator_review_followup", "issue_number": event["issue_number"],
                            "comment_id": event["comment_id"]})
    return {"protocol": PROTOCOL, "mode": "reservation_only", "slots_total": max_workers,
            "slots_occupied": used, "decisions": decisions, "actions": actions,
            "state": {"protocol": PROTOCOL, "tickets": tickets}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--claims", required=True, type=Path, help="fresh complete open-issues snapshot")
    p.add_argument("--state", required=True, type=Path, help="existing router state JSON")
    p.add_argument("--work", type=Path, help="optional saved work.snapshot JSON for tests")
    p.add_argument("--reports", type=Path, help="optional explicit worker status reports JSON list")
    p.add_argument("--events", type=Path, help="optional issue-comment followup events JSON list")
    p.add_argument("--max-workers", type=int, default=3)
    p.add_argument("--commit", action="store_true", help="atomically persist reservations with an exclusive local lock")
    args = p.parse_args()
    if args.work:
        items = json.loads(args.work.read_text(encoding="utf-8"))["items"]
    else:
        import work
        items = work.snapshot()["items"]
    snapshot = json.loads(args.claims.read_text(encoding="utf-8"))
    reports = json.loads(args.reports.read_text(encoding="utf-8")) if args.reports else []
    events = json.loads(args.events.read_text(encoding="utf-8")) if args.events else []
    # This lock is local to one state path / filesystem. It is NOT a distributed
    # claim lease and does not authorize launches against an unrefreshed GitHub API.
    with open(str(args.state) + ".lock", "a+", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = json.loads(args.state.read_text(encoding="utf-8"))
        result = plan(items, snapshot, state, reports=reports, events=events, max_workers=args.max_workers)
        if args.commit:
            fd, tmp = tempfile.mkstemp(prefix=".router-", dir=str(args.state.parent))
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as out:
                    json.dump(result["state"], out, indent=2, ensure_ascii=False)
                    out.write("\n")
                    out.flush()
                    os.fsync(out.fileno())
                os.replace(tmp, args.state)
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
