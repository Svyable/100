# Superagent router — Project 100 control plane

**Status: operational admission/reservation prototype, not a running worker fleet.**
This adapts the ideas of [DeepSeek's dsh-superagent prototype](https://github.com/deepseek-ai/dsh-superagent-prototype): one router, one ticket per accepted task, bounded worker slots, follow-ups sent to the owning ticket, and explicit human hand-off. It does **not** reuse DeepSeek's source code or claim to implement its harness.

The portfolio already has the work queue (scripts/work.py), proof dependencies (data/proof_obligations.json), scout/adversary/checker guidance (scripts/scale.py), and experiment accounting (scripts/fleet.py). The missing boundary was **admission**: whether a real claim currently owns a live, unchanged task and whether there is worker capacity. This tool models that boundary without weakening the math standards.

## Lifecycle

1. **Sources / Triggers:** a complete, fresh GitHub *open-issues* snapshot; optional GitHub issue-comment event IDs. This is input from the operator, not polled by the script. Open PRs are not claims.
2. **Gate / Eval:** use **only** the canonical derived work item. Require status=runnable, a single open issue titled [Claim] <work-id>, exactly one full 64-character scope digest in the issue body, and a matching current work.py digest. Duplicate claims, missing metadata, changed scopes, and blocked/dependency-waiting work are refused.
3. **Ticket / Mandate:** one persistent ticket for each valid claim. Its work contract comes from work.py, **not** the untrusted issue body's prose. The script emits prepare_worker with the exact deliverable, acceptance, boundary and falsifier; no worker is actually executed.
4. **Slots:** default 3 concurrent reserved/running workers (configurable to 1–100); no automatic oversubscription. Separate agents should use isolated worktrees and the same ticket ID on artifacts. A needs_human report releases the slot without releasing ownership; a later explicit resume must fit capacity.
5. **Stop / Retry:** a vanished claim, duplicate, scope change or newly blocked work quarantines the ticket and retains its slot. An operator must stop the actual executor and supply an explicit ended report; quarantine never silently frees capacity. Ended claims cannot auto-relaunch.
6. **Replies:** issue-comment identifiers route to their existing ticket; unknown/unowned comments go to operator_review_followup rather than spawning a second worker. Delivered comment IDs persist in router state to prevent replay (10,000 ID safety cap).

The result is a **reservation and mandate document**, not a GitHub lease, lock service, accepted research result, or worker runtime. Worker starts/stops/replies and independent review are external responsibilities.

## Try it with live GitHub issues

Use an authenticated gh CLI and one trusted operator process. The GitHub list must be complete; if any page fails or is missing, **do not set complete=true**.

~~~sh
# Work contracts always come from the checked-out main/target commit.
python3 scripts/work.py --json > /tmp/100-work.json

# GitHub's Issues API includes PRs; the router explicitly ignores them.
# --slurp produces one outer array containing all paginated results.
gh api --paginate --slurp 'repos/Svyable/100/issues?state=open&per_page=100' \
  | python3 -c 'import sys,json,datetime; pages=json.load(sys.stdin); print(json.dumps({"repository":"Svyable/100","complete":True,"fetched_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"issues":[i for page in pages for i in page]}))' \
  > /tmp/100-open-claims.json

# Initialize durable state ONCE. Never erase a state file to free busy slots.
printf '{"protocol":"svyable.router.v1","tickets":[]}\n' > /tmp/100-router-state.json

# Preview actions with no writes or agent execution.
python3 scripts/router.py --claims /tmp/100-open-claims.json \
  --state /tmp/100-router-state.json --max-workers 3

# Persist new reservations, locally/atomically, while holding an advisory file lock.
python3 scripts/router.py --claims /tmp/100-open-claims.json \
  --state /tmp/100-router-state.json --max-workers 3 --commit \
  > /tmp/100-router-actions.json
~~~

Use the returned prepare_worker actions to provision **one isolated worktree/session per ticket**, restricted to that exact mandate. Before starting a real worker, recheck the open issue and current digest against GitHub; this local snapshot is NOT an atomic GitHub claim lease. The adapter must report that a reserved ticket actually became running; never infer a worker start from a prepared action.

For a worker report, write a JSON array such as:

~~~json
[
  {"ticket_id": "F-M071:123:0123456789ab", "status": "running"}
]
~~~

Then pass --reports /path/to/reports.json with a freshly fetched issue snapshot and --commit. Valid transitions are reserved→running/needs_human/ended; running→needs_human/ended; needs_human→running/ended (only if capacity exists); quarantined→ended. No implicit retry after failure; the operator decides whether to continue a claim.

For human replies, pass --events /path/to/events.json with entries such as {"type":"issue_comment","issue_number":123,"comment_id":456}. Events supply pointers only; the worker adapter obtains the actual message from GitHub with its own authorization. A report or a follow-up is never proof acceptance.

## Deployment and safety boundary

- **Exactly one router writer per repository/state path.** The local fcntl lock and atomic rename serialize CLI invocations on the same filesystem; they are not distributed locks. Multiple machines require a shared transactional store and live compare-and-set for ticket ownership.
- **No launch permissions are granted.** There is deliberately no unattended GitHub Action or model invocation here: the repo does not yet have a connected long-running executor, health-checker or atomic issue lease. Do not label prepared packets as actual fleet capacity or benchmark trials.
- **Human attention only for exceptions.** Route ordinary results to the ticket/claim PR; surface stuck workers, quarantine, incorrect digests and deliberate needs_human reports. No spin-polling, unattended branch writes or model-authorized "Solved" promotions.
- **Resource measurements must be real.** This state tracks reservations, not tokens, tool calls, elapsed compute or agent-hours. Keep actual runs in data/experiments/runs.jsonl and audited outcomes in data/outcomes.json under their existing policies.
- **Proof standards do not change.** Follow AGENTS.md, scripts/regen.py, CI and independent-scope-review rules. Scout/adversary/checker roles are methods of attacking a task, not three independent truth votes.

Recommended next integration: an authenticated, single-writer GitHub listener with durable tickets, claim leases and an executor adapter (Cursor, Codex or another worker host). Implement health checks, timeouts and backoff in that adapter—not as claims about behavior this script does not provide.

## Verify

~~~sh
python3 -m unittest discover -s tests -p 'test_router.py' -v
python3 -m unittest discover -s tests -v
python3 scripts/regen.py --check
~~~
