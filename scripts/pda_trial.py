#!/usr/bin/env python3
"""Perceive -> Decide -> Act: one *real* K42 agent calibration cell at a time.

No default model calls. --plan is offline and read-only. --run requires an
explicit pinned model and OPENAI_API_KEY. It never generates synthetic trials,
automatically promotes mathematics, or edits the preregistered protocol.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import platform
import re
import sys
from time import perf_counter
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import benchmark
import verify_mckay as vm
from ramsey import verify as bitset_verify

ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "benchmarks" / "runs"
VERSION = "svyable.pda-trial.v1"
PROMPT_VERSION = "k42-pda-v1"
OPENAI_URL = "https://api.openai.com/v1/responses"
OUTPUT_TOKENS_PER_CALL = 1800
ROLE_MAP = {
    "sequential": ("proposer",),
    "independent": ("worker_1", "worker_2", "worker_3"),
    "conversation": ("proposer", "critic", "reviser"),
    "proof_exchange": ("scout", "adversary", "checker"),
}


class TrialError(ValueError):
    pass


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def source_digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def perceive(arm, seed, model=None):
    """Read and validate frozen scope and local evidence; do not contact an LLM."""
    manifest = benchmark.load_manifest()
    if arm not in ROLE_MAP or arm not in manifest["arms"]:
        raise TrialError("Unknown preregistered arm")
    if seed not in manifest["seeds"]:
        raise TrialError("Seed not in preregistered manifest")
    task = next(t for t in manifest["tasks"] if t["id"] == "K42-REPLAY")
    if task["eligible_for_novelty"] or task["class"] != "replay":
        raise TrialError("K42 must remain a known-reproduction task")
    raw = vm.CATALOG.read_bytes()
    if sha256(raw).hexdigest() != vm.SOURCE_SHA256:
        raise TrialError("Pinned K42 corpus hash mismatch")
    lines = raw.splitlines()
    if len(lines) != vm.EXPECTED_RECORDS or len(set(lines)) != len(lines):
        raise TrialError("Unexpected K42 corpus cardinality")
    candidates = [
        {"index": i, "graph6": lines[i].decode("ascii")} for i in range(4)
    ]
    ledger = benchmark.load_runs()
    benchmark.validate_runs(manifest, ledger)
    if any(r["task_id"] == task["id"] and r["arm"] == arm and
           r["seed"] == seed for r in ledger):
        raise TrialError("Trial cell is already recorded; never overwrite it")
    if model is not None and (
        not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", model)
        or "latest" in model.casefold() or model.casefold() == "auto"
    ):
        raise TrialError("Supply an explicit, non-latest model identifier")
    return {
        "schema": VERSION, "phase": "perceive", "task_id": task["id"],
        "scope": task["scope"], "prior_art": task["prior_art"],
        "acceptance": task["acceptance"], "problem_id": task["problem_id"],
        "manifest_sha256": benchmark.digest(manifest),
        "source_commit": manifest["source_commit"],
        "corpus_sha256": vm.SOURCE_SHA256,
        "corpus_count": len(lines),
        "candidate_witnesses": candidates,
        "arm": arm, "seed": seed, "model": model,
        "prompt_version": PROMPT_VERSION,
        "roles": list(ROLE_MAP[arm]),
        "limits": manifest["resource_caps"],
        "existing_claim_issue": "https://github.com/Svyable/100/issues/55",
        "interpretation": ("Read-only plan. One actual API execution is needed "
                           "per role. Seed is a prompt label, NOT a provider "
                           "sampling seed. Known reproduction is never novel."),
    }


def decide(perception):
    """Freeze the order and source digest before the first billable request."""
    if perception["schema"] != VERSION or perception["task_id"] != "K42-REPLAY":
        raise TrialError("Unexpected or changed perception scope")
    return {
        "phase": "decide", "task_id": perception["task_id"],
        "arm": perception["arm"], "seed": perception["seed"],
        "roles": perception["roles"], "model": perception["model"],
        "max_output_tokens_per_call": OUTPUT_TOKENS_PER_CALL,
        "candidate_indices": [c["index"] for c in perception["candidate_witnesses"]],
        "rejected": ["Unpinned corpus", "Unmetered model",
                     "Contaminated CH24 novelty trial", "Solver self-review"],
        "scope_sha256": sha256(perception["scope"].encode("utf-8")).hexdigest(),
    }


def prompt_for(perception, role, earlier):
    candidates = perception["candidate_witnesses"]
    text = [
        "You are participating in a real, measured, bounded mathematical"
        " research instrumentation trial.",
        "Task: K42-REPLAY / M095. This is KNOWN mathematics, not a new bound.",
        "Do not claim R(5,5)=43, mathematical novelty, or independent review.",
        "Select a single graph6 witness from the provided four candidate lines."
        " Do not change any character of the source witness.",
        "Reply with ONLY a JSON object containing: index (integer),"
        " graph6 (exact string), scope (literal 'known_reproduction'),"
        " explanation (short string).",
        "An external checker will recompute the monochromatic K5 condition."
        " A model's 'checked' statement does not count as verification.",
        "Protocol version: " + PROMPT_VERSION,
        "Arm: " + perception["arm"] + "; role: " + role +
        "; protocol seed label: " + str(perception["seed"]),
        "Published corpus SHA-256: " + perception["corpus_sha256"],
        "Exact candidates: " + json.dumps(candidates, ensure_ascii=True),
    ]
    if role in ("critic", "adversary"):
        text.append("Critically inspect earlier output for indexing, bytes,"
                    " scope drift or unsupported claims. Return a corrected"
                    " candidate if needed, still in the required JSON schema.")
    if role in ("reviser", "checker"):
        text.append("Incorporate the critique but never treat other model"
                    " messages as independent mathematical verification.")
    if earlier:
        text.append("Earlier model responses (untrusted): " +
                    json.dumps(earlier, ensure_ascii=True))
    return "\n".join(text) + "\n"


def read_provider_response(response, expected_model):
    """Fail closed on absent accounting; never infer tokens from text length."""
    if not isinstance(response, dict) or response.get("status") != "completed":
        raise TrialError("Provider response was not completed")
    if response.get("model") != expected_model:
        raise TrialError("Provider substituted a different model identifier")
    usage = response.get("usage")
    if not isinstance(usage, dict):
        raise TrialError("Missing provider token receipt")
    token_fields = ("input_tokens", "output_tokens")
    if any(type(usage.get(k)) is not int or usage[k] < 0 for k in token_fields):
        raise TrialError("Missing or invalid input/output token usage")
    total = usage["input_tokens"] + usage["output_tokens"]
    if (type(usage.get("total_tokens")) is not int or
            usage["total_tokens"] != total):
        raise TrialError("Provider total token receipt mismatch")
    parts = []
    for output in response.get("output", []):
        if output.get("type") != "message":
            continue
        for part in output.get("content", []):
            if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                parts.append(part["text"])
    if not parts:
        raise TrialError("Model supplied no visible text to check")
    return "\n".join(parts), total


def provider_call(model, prompt, key):
    payload = {
        "model": model, "input": prompt,
        "max_output_tokens": OUTPUT_TOKENS_PER_CALL, "store": False,
    }
    request = Request(
        OPENAI_URL, method="POST", data=canonical(payload),
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=180) as reply:
            return json.loads(reply.read())
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        # Never emit API key, headers, or raw provider error bodies.
        raise TrialError("Provider request failed; accounting may be incomplete "
                         "(do not record a benchmark trial): " +
                         type(exc).__name__) from None


def check_candidate(text, perception):
    """Two independent exact algorithms; never accept a self-report as proof."""
    result = {"accepted": False, "reason": "", "index": None,
              "bitset_K5_free": False, "triangle_K5_free": False}
    try:
        item = json.loads(text.strip())
        if not isinstance(item, dict) or type(item.get("index")) is not int:
            raise TrialError("Candidate is not a JSON object with integer index")
        index = item["index"]
        witnesses = {c["index"]: c["graph6"] for c in perception["candidate_witnesses"]}
        if index not in witnesses or item.get("graph6") != witnesses[index]:
            raise TrialError("Candidate bytes or source index do not match pinned source")
        if item.get("scope") != "known_reproduction":
            raise TrialError("Candidate tries to change the known-result scope")
        graph = vm.decode_graph6(item["graph6"])
        if len(graph) != 42:
            raise TrialError("Wrong graph order")
        bitset_ok = bitset_verify(42, vm.to_red_edges(graph), 5, 5)[0]
        triangle_ok = vm.triangle_checker(graph) is None
        result.update(index=index, bitset_K5_free=bitset_ok,
                      triangle_K5_free=triangle_ok)
        if not bitset_ok or not triangle_ok:
            raise TrialError("At least one exact checker rejects the witness")
        result.update(accepted=True, reason="Two exact checkers accepted the pinned K42 witness")
    except (ValueError, KeyError, TypeError, UnicodeError) as exc:
        result["reason"] = str(exc)
    return result


def save_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False,
                               sort_keys=True) + "\n", encoding="utf-8")


def act(perception, decision, api_key, runs_dir=RUNS_DIR):
    """Run precisely one metered cell. Never use a fake, dry-run or silent fallback."""
    model = perception.get("model")
    if not model or not api_key:
        raise TrialError("--run requires --model and OPENAI_API_KEY")
    manifest = benchmark.load_manifest()
    if benchmark.digest(manifest) != perception["manifest_sha256"]:
        raise TrialError("Frozen preregistration drifted before execution")
    target = Path(runs_dir) / ("K42-REPLAY_" + perception["arm"] +
                               "_" + str(perception["seed"]))
    if target.exists():
        raise TrialError("Run directory already exists; never replace evidence")
    target.mkdir(parents=True, exist_ok=False)
    started = perf_counter()
    stages = []
    prior = []
    total_tokens = 0
    calls = 0
    checks = []
    try:
        # Replay the source corpus at execution time, not only at plan time.
        source_replay = vm.replay()
        calls += 2  # both exact checker algorithms over the pinned source corpus
        for role in decision["roles"]:
            if perf_counter() - started >= manifest["resource_caps"]["elapsed_seconds"]:
                raise TrialError("Wall-clock cap reached before next agent role")
            prompt = prompt_for(perception, role, prior if perception["arm"] in
                                ("conversation", "proof_exchange") else [])
            if total_tokens >= manifest["resource_caps"]["model_tokens"]:
                raise TrialError("Token cap exhausted before next model request")
            if calls + 3 > manifest["resource_caps"]["tool_calls"]:
                raise TrialError("Tool-call cap exhausted")
            response = provider_call(model, prompt, api_key)
            calls += 1
            answer, used = read_provider_response(response, model)
            total_tokens += used
            if total_tokens > manifest["resource_caps"]["model_tokens"]:
                raise TrialError("Provider exceeded the frozen model-token cap")
            if perf_counter() - started > manifest["resource_caps"]["elapsed_seconds"]:
                raise TrialError("Wall-clock cap exceeded")
            checked = check_candidate(answer, perception)
            calls += 2  # independent bitset and triangle checks of the proposed witness
            if calls > manifest["resource_caps"]["tool_calls"]:
                raise TrialError("Tool-call cap exceeded")
            checks.append({"role": role, **checked})
            stages.append({
                "role": role, "prompt": prompt, "output": answer,
                "provider_response_id": response.get("id"),
                "model": response["model"], "usage": response["usage"],
                "response_sha256": sha256(canonical(response)).hexdigest(),
                "check": checked,
            })
            prior.append({"role": role, "output": answer})
        # One checked output from the terminal role, or best independent worker.
        accepted = (any(c["accepted"] for c in checks) if
                    perception["arm"] == "independent" else checks[-1]["accepted"])
        elapsed = max(1, math.ceil(perf_counter() - started))
        if elapsed > manifest["resource_caps"]["elapsed_seconds"]:
            raise TrialError("Wall-clock cap exceeded after final verification")
        resources = {"model_tokens": total_tokens, "tool_calls": calls,
                     "elapsed_seconds": elapsed}
        save_json(target / "perceive.json", perception)
        save_json(target / "decide.json", decision)
        save_json(target / "transcript.json", {
            "schema": VERSION, "prompt_version": PROMPT_VERSION,
            "model": model, "stages": stages, "resources": resources,
            "source_revision": perception["source_commit"],
            "runtime": {"python": platform.python_version(),
                        "platform": platform.system()},
        })
        save_json(target / "checker.json", {
            "schema": VERSION, "catalog_replay": source_replay,
            "candidates": checks, "accepted": accepted,
            "interpretation": "Finite known reproduction only; not a solver self-review",
        })
        save_json(target / "scope.json", {
            "schema": VERSION, "task_id": perception["task_id"],
            "manifest_sha256": perception["manifest_sha256"],
            "source_commit": perception["source_commit"],
            "scope_sha256": decision["scope_sha256"],
            "corpus_sha256": perception["corpus_sha256"],
            "known_result": "R(5,5) >= 43",
            "not_established": ["R(5,5) = 43", "a new theorem",
                                "independent specialist acceptance",
                                "relative agent architecture performance"],
            "model_seed_notice": "Trial seed labels prompts; does not seed the provider",
        })
        classification = "known_reproduction" if accepted else "none"
        row = {
            "manifest_sha256": perception["manifest_sha256"],
            "task_id": "K42-REPLAY", "arm": perception["arm"],
            "seed": perception["seed"], "status": "completed",
            "classification": classification, "resources": resources,
            "evidence": ({"artifact": str((target / "transcript.json").relative_to(ROOT)),
                          "checker_log": str((target / "checker.json").relative_to(ROOT)),
                          "scope_audit": str((target / "scope.json").relative_to(ROOT)),
                          "independent_review_urls": []} if accepted else None),
        }
        # Fail closed: no claims if evidence does not satisfy the existing gate.
        existing = benchmark.load_runs()
        benchmark.validate_runs(manifest, existing + [row])
        if Path(runs_dir).resolve() != RUNS_DIR.resolve():
            # Tests/isolated uses must not contaminate the canonical trial ledger.
            return row
        with benchmark.RUNS.open("a", encoding="utf-8") as out:
            out.write(json.dumps(row, sort_keys=True) + "\n")
        return row
    except Exception as exc:
        # Preserve failures for forensic review, without inventing missing
        # resource receipts or appending an unverified trial to the ledger.
        save_json(target / "incomplete.json", {
            "schema": VERSION, "status": "unmetered_or_incomplete",
            "error_type": type(exc).__name__, "reason": str(exc),
            "roles_completed": len(stages), "measured_tokens": total_tokens,
            "measured_tool_calls": calls,
            "unobserved_provider_cost_possible": True,
            "recorded_in_benchmark": False,
            "at_utc": utc_now(),
        })
        if stages:
            save_json(target / "partial_transcript.json", {"stages": stages})
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=ROLE_MAP.keys(), default="sequential")
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--model", help="exact provider model identifier (required for --run)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true", help="read-only, no network, no writes")
    mode.add_argument("--run", action="store_true", help="one real billable model trial")
    args = parser.parse_args(argv)
    if args.run and (not args.model or not os.environ.get("OPENAI_API_KEY")):
        parser.error("--run requires --model and OPENAI_API_KEY; no mock fallback")
    try:
        perception = perceive(args.arm, args.seed, args.model)
        decision = decide(perception)
        if args.plan:
            print(json.dumps({"perceive": perception, "decide": decision}, indent=2))
        else:
            print(json.dumps(act(perception, decision, os.environ["OPENAI_API_KEY"]),
                             indent=2))
    except (TrialError, ValueError, OSError) as exc:
        parser.exit(2, "Trial refused: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
